from goicp import goicpAlign
import argparse
import vtk
import numpy as np
from applyMatrix import align

from PyQt5.QtWidgets import QApplication
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

colors = vtk.vtkNamedColors()

def main():
    atlas = "AnkleAtlasL.stl"
    src = get_program_parameters()
    print(atlas, src)
    matrix = goicpAlign(src, atlas)

    srcVtk = ReadPolyData(src)
    tgtVtk = ReadPolyData(atlas)

    print( np.linalg.det(matrix))
    # goicpTransform = vtk.vtkTransform()
    # goicpTransform.SetMatrix(matrix.flatten())
    # transformFilter = vtk.vtkTransformPolyDataFilter()
    # transformFilter.SetInputData(srcVtk)
    # transformFilter.SetTransform(goicpTransform)
    # transformFilter.Update()


    srcName  = src.split(".")
    saveName = srcName[0] + "_reoriented.stl"
    align(src, saveName, matrix)


    

def makeActor(vtkData, color):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(vtkData)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d(color))
    actor.GetProperty().SetOpacity(1)
    return actor

def get_program_parameters():
    import argparse
    description = 'Read a .stl file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='42400-IDGH.stl')
    args = parser.parse_args()
    return args.filename

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

    main()
