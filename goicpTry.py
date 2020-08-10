import numpy as np;
from py_goicp import GoICP, POINT3D, ROTNODE, TRANSNODE;
import argparse
import random
from stl import mesh
import time
np.random.seed(0)
random.seed(0)



# Run GoIcp on src and tgt, returns transform Matrix for source with mse less than threshold
def goicpTransform1(src, tgt, mseUnscaled = .04, pruneAmount = 200, trimFraction = .15, dtSize = 150):

    start_time = time.time()

    srcNp, tgtNp, scaleValue, src_means, tgt_means = centerAndScale(mesh.Mesh.from_file(src), mesh.Mesh.from_file(tgt))
    srcNp = np.reshape(srcNp.points, (len(srcNp)*3, 3))
    tgtNp = np.reshape(tgtNp.points, (len(tgtNp)*3, 3))



    tgtNp_suffled = np.copy(tgtNp)
    np.random.shuffle(tgtNp_suffled)
    tgtNp_suffled = tgtNp_suffled[:pruneAmount]



    mse = mseUnscaled/scaleValue
    print("EPSILON: " + str(mse * pruneAmount * (1-trimFraction)))


    Nm, model = loadPointCloud(srcNp)
    Nd, data = loadPointCloud(tgtNp_suffled)
    # Nd, data = loadPointCloud(vtk_to_numpy(tgtVtk.GetPoints().GetData()))
    initNodeTrans = TRANSNODE()
    initNodeTrans.x = -.5
    initNodeTrans.y = -.5
    initNodeTrans.z = -.5
    initNodeTrans.w = 1
    goicp = GoICP()
    goicp.loadModelAndData(Nm, model, Nd, data)
    goicp.setDTSizeAndFactor(dtSize, 2.0)
    goicp.trimFraction = trimFraction
    goicp.MSEThresh = mse
    goicp.setInitNodeTrans( initNodeTrans)
    goicp.BuildDT()
    goicp.Register()
    # print(goicp.optimalRotation()) # A python list of 3x3 is returned with the optimal rotation
    # print(goicp.optimalTranslation())# A python list of 1x3 is returned with the optimal translation



    transformMatrix = np.vstack((goicp.optimalRotation(),np.zeros((1,3), float)))
    transformMatrix = np.hstack((transformMatrix, np.reshape(np.append(goicp.optimalTranslation(), [1]), (4,1))))


    print(transformMatrix)
    transformMatrix = np.linalg.inv(transformMatrix)
    print(transformMatrix)

    shift1 = makeTranslationMatrix(src_means*-1)
    scale1 = makeScaleMatrix(1/scaleValue)
    shift2 = makeTranslationMatrix(tgt_means)
    scale2 = makeScaleMatrix(scaleValue)

    total = np.dot(shift2, scale2)
    total = np.dot(total, transformMatrix)
    total = np.dot(total, scale1)
    total = np.dot(total, shift1)
    print(total)


    return transformMatrix, total


def makeTranslationMatrix(vector = [0.0,0.0,0.0]):
    botRow = np.zeros((1,3), float)
    middleDiag = np.zeros((3,3), float)
    np.fill_diagonal(middleDiag, 1)

    trans = np.append(vector, [1])
    trans = np.reshape(trans, (4,1))
    trans4 = np.vstack((middleDiag, botRow))
    trans4 = np.hstack((trans4, trans))
    return trans4

def makeScaleMatrix(value = 0.0):
    botRow = np.zeros((1,3), float)
    sideCol = np.reshape([0,0,0,1.0], (4,1))
    middleDiag = np.zeros((3,3), float)
    np.fill_diagonal(middleDiag, 1)

    scale = middleDiag * value
    scale = np.vstack((scale, botRow))
    scale = np.hstack((scale, sideCol))
    return scale


def centerAndScale(src, tgt):

    srcNp = np.reshape(src.points, (len(src)*3, 3))
    tgtNp = np.reshape(tgt.points, (len(tgt)*3, 3))
    src_means = np.mean(srcNp, axis = 0)
    tgt_means = np.mean(tgtNp, axis = 0)


    tgt.translate(tgt_means*-1)


    src.translate(src_means * -1)


    srcNp = np.reshape(src.points, (len(src)*3, 3))
    tgtNp = np.reshape(tgt.points, (len(tgt)*3, 3))
    mins_src = np.absolute(np.min(srcNp))
    maxs_src = np.max(srcNp)
    mins_tgt = np.absolute(np.min(tgtNp))
    maxs_tgt = np.max(tgtNp)
    max = np.max((mins_src, maxs_src, mins_tgt, maxs_tgt)) * 2


    scale = 1/max
    src.points *= scale

    tgt.points *=scale

    return src, tgt, max, src_means, tgt_means

def loadPointCloud(array):
    p3dlist = [];
    for p in range(len(array)):
        x,y,z = array[p]
        pt = POINT3D(float(x), float(y), float(z));
        p3dlist.append(pt);
    return len(array), p3dlist;

def get_program_parameters():
    description = 'How to align two vtkPolyData\'s.'
    epilogue = '''

    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('src_fn', help='The polydata source file name,e.g. Grey_Nurse_Shark.stl.')
    parser.add_argument('tgt_fn', help='The polydata target file name, e.g. shark.ply.')

    args = parser.parse_args()

    return args.src_fn, args.tgt_fn


def ReadPolyData(file_name):
    import os
    path, extension = os.path.splitext(file_name)
    extension = extension.lower()
    if extension == ".ply":
        reader = vtk.vtkPLYReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".vtp":
        reader = vtk.vtkXMLpoly_dataReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".obj":
        reader = vtk.vtkOBJReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".stl":
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".vtk":
        reader = vtk.vtkpoly_dataReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".g":
        reader = vtk.vtkBYUReader()
        reader.SetGeometryFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    else:
        # Return a None if the extension is unknown.
        poly_data = None
    return poly_data

if __name__ == '__main__':
    src, tgt = get_program_parameters()
    goicpTransform(src, tgt)
