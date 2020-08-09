import vtk
import argparse
from vtk.util.numpy_support import vtk_to_numpy


def decimateStl(stl, pruneAmount, saveFile):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(stl)
    reader.Update()
    polyData = reader.GetOutput()
    stlDec = decimateVtk(polyData, int(pruneAmount))
    print(stlDec.GetPoints().GetNumberOfPoints())
    tgtNp = vtk_to_numpy(stlDec.GetPoints().GetData())
    print(len(tgtNp))

    stlWriter = vtk.vtkSTLWriter()
    stlWriter.SetFileName(saveFile)
    stlWriter.SetInputData(stlDec)
    stlWriter.Write()

def decimateVtk(vtkData, size):
    numPointsDesired = size
    numPoints = vtkData.GetPoints().GetNumberOfPoints()

    decimate = vtk.vtkDecimatePro()
    decimate.SetInputData(vtkData)
    decimate.SetTargetReduction(1 - (numPointsDesired/numPoints))
    decimate.PreserveTopologyOn()
    decimate.Update()

    return decimate.GetOutput()

def get_program_parameters():
    description = 'Decimate stl file while maintaining topology.'
    epilogue = '''

    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('stl', help='The polydata source file name,e.g. Grey_Nurse_Shark.stl.')
    parser.add_argument('pruneAmount', help='Ideal new stl size')
    parser.add_argument('saveFile', help='Stl output save name')



    args = parser.parse_args()

    return args.stl, args.pruneAmount, args.saveFile
if __name__ == '__main__':
    stl, pruneAmount, saveFile = get_program_parameters()
    decimateStl(stl, pruneAmount, saveFile)
