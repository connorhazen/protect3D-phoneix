import numpy as np;
from py_goicp import GoICP, POINT3D, ROTNODE, TRANSNODE;
import vtk
import argparse
from vtk.util.numpy_support import vtk_to_numpy
from vtk.util import numpy_support
import random
from restoredICP import ICP
from subprocess import call
from configMaker import saveConfigFile
import time
import PyQt5
srcFile = "src.txt"
tgtFile = "tgt.txt"
cScript = "./Go-ICP-master/GoICP"
configFile = "config.txt"
outputFile = "output.txt"
colors = vtk.vtkNamedColors()
# np.random.seed(0)
# random.seed(0)
from PyQt5.QtWidgets import QApplication
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


# Run GoIcp on src and tgt, returns transform Matrix that has the lowest MSE,
# Also displays transformed source with given matix
def goicpTransform(src, tgt, mseUnscaled = .04, pruneAmount = 200, trimFraction = .15, dtSize = 150):

    start_time = time.time()
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

    saveConfigFile(configFile, mseThresh = mse, trimFrac = trimFraction, distTransSize = dtSize)


    #
    # call([cScript, srcFile, tgtFile, str(pruneAmount) , configFile, outputFile])
    # rotation, translation = readFileForMatrix(outputFile)


    # # Here is the python version
    # # For some it does not give the smae results.

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



    # transformMatrix = np.vstack((rotation,np.zeros((1,3), float)))
    # transformMatrix = np.hstack((transformMatrix, np.reshape(np.append(translation, [1]), (4,1))))

    print(transformMatrix)
    transformMatrix = np.linalg.inv(transformMatrix)
    print(transformMatrix)


    goicpTransform = vtk.vtkTransform()
    goicpTransform.SetMatrix(transformMatrix.flatten())

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(srcVtk)
    transformFilter.SetTransform(goicpTransform)
    transformFilter.Update()

    goicpVtk = transformFilter.GetOutput()

    print("Go Icp Time (sec): " + str(time.time() - start_time))

    goicpVtk = scaleBack(goicpVtk, scaleValue)
    srcVtk = scaleBack(srcVtk, scaleValue)
    tgtVtk = scaleBack(tgtVtk, scaleValue)
    goicpVtk = shiftBack(goicpVtk, tgt_means)
    srcVtk = shiftBack(srcVtk, tgt_means)
    tgtVtk = shiftBack(tgtVtk, tgt_means)

    #
    # T, distances, i = ICP(tgtNp, srcNp, max_iterations=1000, convergence = .00001)
    # print("my icp \n", T)
    #
    #
    #
    #
    # myicpTransform = vtk.vtkTransform()
    # myicpTransform.SetMatrix(T.flatten())
    #
    # transformFilter = vtk.vtkTransformPolyDataFilter()
    # transformFilter.SetInputData(tgtVtk)
    # transformFilter.SetTransform(myicpTransform)
    # transformFilter.Update()
    #
    # myicpVtk = transformFilter.GetOutput()
    #

    #
    # tgtNpNew = vtk_to_numpy(goicpVtk.GetPoints().GetData())
    # T2, distances2, i = ICP(tgtNpNew, srcNp, max_iterations=1000, convergence = .00001)
    #
    # myicpTransform2 = vtk.vtkTransform()
    # myicpTransform2.SetMatrix(T2.flatten())
    #
    # transformFilter2 = vtk.vtkTransformPolyDataFilter()
    # transformFilter2.SetInputData(goicpVtk)
    # transformFilter2.SetTransform(myicpTransform2)
    # transformFilter2.Update()
    #
    # myicpVtk2 = transformFilter2.GetOutput()




    srcActor = makeActor(srcVtk, "blue")
    tgtActor = makeActor(tgtVtk, "yellow")
    transActor = makeActor(goicpVtk, "red")
    # transActor2 = makeActor(myicpVtk, "orange")
    # transActor3 = makeActor(myicpVtk2, "white")

    axes = vtk.vtkAxesActor()
    # axes.SetAxisLabels(False)
    axes.SetShaftTypeToCylinder()
    axes.SetCylinderRadius(.001)
    axes.SetTotalLength(500,500,500)



    app = QApplication(['QVTKRenderWindowInteractor'])
    # create the widget
    widget = QVTKRenderWindowInteractor()
    widget.Initialize()
    widget.Start()
    # if you don't want the 'q' key to exit comment this.
    # widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
    ren = vtk.vtkRenderer()
    ren.AddActor(transActor)
    # ren.AddActor(transActor2)
    #ren.AddActor(transActor3)
    ren.AddActor(tgtActor)
    ren.AddActor(srcActor)
    ren.AddActor(axes)
    ren.SetBackground(colors.GetColor3d("green")) # Set renderer's background color to green
    widget.GetRenderWindow().AddRenderer(ren)
    widget.show()
    # start event processing
    app.exec_()





    return transformMatrix, goicpVtk

def close_window(iren):
    render_window = iren.GetRenderWindow()
    render_window.Finalize()
    iren.TerminateApp()


def readFileForMatrix(fileName):
    f = open(fileName)
    lines = f.readlines()
    newlines = []
    for line in lines:
        line = line.split()
        line = [i.strip() for i in line]
        line = [float(i) for i in line]
        newlines.append(line)

    time = newlines[0]
    rotation = np.vstack(newlines[1:4])
    translation = np.vstack(newlines[4:7])
    return rotation, translation

def scaleBack(data, scaleValue):
    scale = makeScaleMatrix(scaleValue)
    scaleTransform = vtk.vtkTransform()
    scaleTransform.SetMatrix(scale.flatten())
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(data)
    transformFilter.SetTransform(scaleTransform)
    transformFilter.Update()
    return transformFilter.GetOutput()

def shiftBack(data, means):
    center = makeTranslationMatrix(means)
    centerTransform = vtk.vtkTransform()
    centerTransform.SetMatrix(center.flatten())
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(data)
    transformFilter.SetTransform(centerTransform)
    transformFilter.Update()
    return transformFilter.GetOutput()

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

def makeActor(vtkData, color):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(vtkData)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d(color))
    actor.GetProperty().SetOpacity(1)
    return actor

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

def translateArray(array, translation = [0.0,0.0,0.0]):
    array = np.hstack((array, np.full((len(array), 1), 1.0)))

    translate = makeTranslationMatrix(translation)

    newArr = np.transpose(array)
    newArr = translate.dot(newArr)
    newArr = np.transpose(newArr)
    return(np.delete(newArr, -1, axis=1))

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
