from goicpTry import goicpTransform1
import argparse
import vtk

from PyQt5.QtWidgets import QApplication
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

colors = vtk.vtkNamedColors()

def main():
    atlas = "AnkleAtlasL.stl"
    src = get_program_parameters()
    print(atlas, src)
    t, total = goicpTransform1(src, atlas)

    srcVtk = ReadPolyData(src)
    tgtVtk = ReadPolyData(atlas)


    goicpTransform = vtk.vtkTransform()
    goicpTransform.SetMatrix(total.flatten())
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(srcVtk)
    transformFilter.SetTransform(goicpTransform)
    transformFilter.Update()




    srcActor = makeActor(srcVtk, "blue")
    tgtActor = makeActor(tgtVtk, "yellow")
    transActor = makeActor(transformFilter.GetOutput(), "red")
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
