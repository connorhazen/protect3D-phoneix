import numpy as np;
from py_goicp import GoICP, POINT3D, ROTNODE, TRANSNODE;
import vtk
import argparse
from vtk.util.numpy_support import vtk_to_numpy
from vtk.util import numpy_support
import random

srcFile = "src1.txt"
tgtFile = "tgt1.txt"

mseUnscaled = .04
pruneAmount = 200
trimFraction = .15
dtSize = 150
np.random.seed(0)
random.seed(0)

def trial(src, tgt):
    srcVtk, tgtVtk, scaleValue, tgt_means = getCenteredAndScaled(src, tgt)

    tgtDec = decimateVtk(tgtVtk, pruneAmount)
    tgtDecNp = vtk_to_numpy(tgtDec.GetPoints().GetData())
    # saveToFile(tgtFile, tgtDecNp)
    # pruneAmount = str(len(tgtDecNp))

    tgtNp = vtk_to_numpy(tgtVtk.GetPoints().GetData())
    # saveToFile(tgtFile, tgtNp)
    # pruneAmount = str(len(tgtNp))


    srcNp = vtk_to_numpy(srcVtk.GetPoints().GetData())
    saveToFile(srcFile, srcNp)

    tgtNp_suffled = np.copy(tgtDecNp)
    np.random.shuffle(tgtNp_suffled)
    tgtNp_suffled = tgtNp_suffled[:pruneAmount]
    saveToFile(tgtFile, tgtNp_suffled)
    mse = mseUnscaled/scaleValue
    print("EPSILON: " + str(mse * pruneAmount * (1-trimFraction)))
    goIcptrial(mse)

def goIcptrial(mse):

    goicp = GoICP();
    Nm, a_points = loadPointCloud(srcFile);
    Nd, b_points = loadPointCloud(tgtFile);
    goicp.loadModelAndData(Nm, a_points, Nd, b_points);
    goicp.setDTSizeAndFactor(dtSize, 2.0);
    goicp.trimFraction = trimFraction
    goicp.MSEThresh = mse

    goicp.BuildDT();
    print("done dt")
    goicp.Register();
    # print(goicp.optimalRotation()); # A python list of 3x3 is returned with the optimal rotation
    # print(goicp.optimalTranslation());# A python list of 1x3 is returned with the optimal translation
    transformMatrix = np.vstack((goicp.optimalRotation(),np.zeros((1,3), float)))
    transformMatrix = np.hstack((transformMatrix, np.reshape(np.append(goicp.optimalTranslation(), [1]), (4,1))))

    print(transformMatrix)
    transformMatrix = np.linalg.inv(transformMatrix)
    print(transformMatrix)

def loadPointCloud(filename):
    pcloud = np.loadtxt(filename, skiprows=1);
    plist = pcloud.tolist();
    p3dlist = [];
    for x,y,z in plist:
        pt = POINT3D(x,y,z);
        p3dlist.append(pt);
    return pcloud.shape[0], p3dlist;



def getCenteredAndScaled(src, tgt):
    tgtVtk = ReadPolyData(tgt)
    srcVtk = ReadPolyData(src)

    src_np = vtk_to_numpy(srcVtk.GetPoints().GetData())
    tgt_np = vtk_to_numpy(tgtVtk.GetPoints().GetData())
    src_means = np.mean(src_np, axis = 0)
    tgt_means = np.mean(tgt_np, axis = 0)


    center = makeTranslationMatrix(tgt_means * -1)
    centerTransform = vtk.vtkTransform()
    centerTransform.SetMatrix(center.flatten())
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(tgtVtk)
    transformFilter.SetTransform(centerTransform)
    transformFilter.Update()
    tgtVtk = transformFilter.GetOutput()

    center = makeTranslationMatrix(src_means * -1)
    centerTransform = vtk.vtkTransform()
    centerTransform.SetMatrix(center.flatten())
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(srcVtk)
    transformFilter.SetTransform(centerTransform)
    transformFilter.Update()
    srcVtk = transformFilter.GetOutput()

    src_np = vtk_to_numpy(srcVtk.GetPoints().GetData())
    tgt_np = vtk_to_numpy(tgtVtk.GetPoints().GetData())

    mins_src = np.absolute(np.min(src_np))
    maxs_src = np.max(src_np)
    mins_tgt = np.absolute(np.min(tgt_np))
    maxs_tgt = np.max(tgt_np)
    max = np.max((mins_src, maxs_src, mins_tgt, maxs_tgt)) * 2


    scale = makeScaleMatrix(1/max)
    scaleTransform = vtk.vtkTransform()
    scaleTransform.SetMatrix(scale.flatten())
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(tgtVtk)
    transformFilter.SetTransform(scaleTransform)
    transformFilter.Update()
    tgtVtk = transformFilter.GetOutput()



    scale = makeScaleMatrix(1/max)
    scaleTransform = vtk.vtkTransform()
    scaleTransform.SetMatrix(scale.flatten())
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(srcVtk)
    transformFilter.SetTransform(scaleTransform)
    transformFilter.Update()
    srcVtk = transformFilter.GetOutput()

    return srcVtk, tgtVtk, max, tgt_means

def saveToFile(name, vtk):
    f = open(name, 'w')
    f.write(str(len(vtk))+ '\n')
    f.close()
    f=open(name,'ab')
    np.savetxt(f, vtk, delimiter=' ')
    f.close()

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

def makeRotationMatrix(array):
    botRow = np.zeros((1,3), float)
    sideCol = np.reshape([0,0,0,1.0], (4,1))

    ret = np.vstack((array, botRow))
    ret = np.hstack((ret, sideCol))

    return ret

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

def decimateVtk(vtkData, size):
    numPointsDesired = size
    npData =  vtk_to_numpy(vtkData.GetPoints().GetData())
    numPoints = len(npData)

    decimate = vtk.vtkDecimatePro()
    decimate.SetInputData(vtkData)
    decimate.SetTargetReduction(1 - (numPointsDesired/numPoints))
    decimate.PreserveTopologyOn()
    decimate.Update()

    return decimate.GetOutput()

if __name__ == '__main__':
    src, tgt = get_program_parameters()
    trial(src, tgt)
