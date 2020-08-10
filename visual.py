import vtk
import PyQt5
from PyQt5.QtWidgets import QApplication
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

def get_program_parameters():
    import argparse
    description = 'Read a .stl file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='42400-IDGH.stl')
    args = parser.parse_args()
    return args.filename

def visualizeVTK(poly_data):
    colors = vtk.vtkNamedColors()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a rendering window and renderer

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
    ren.AddActor(actor)
    ren.AddActor(axes)
    ren.SetBackground(colors.GetColor3d("green")) # Set renderer's background color to green
    widget.GetRenderWindow().AddRenderer(ren)
    widget.show()
    # start event processing
    app.exec_()
def visualize(filename):
    colors = vtk.vtkNamedColors()

    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    poly_data = reader.GetOutput()

    visualizeVTK(poly_data)


if __name__ == '__main__':
    filename = get_program_parameters()
    visualize(filename)
