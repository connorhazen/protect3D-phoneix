import vtk
import glob




def get_program_parameters():
    import argparse
    description = 'Read a .stl folder.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('folder', help='meshes/')
    args = parser.parse_args()
    return args.folder


def display(folder = ""):
    if folder[-1] != "/":
        folder = folder + "/"

    colors = vtk.vtkNamedColors()


    print(glob.glob(folder + "*.stl"))

    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    ren.SetBackground(colors.GetColor3d("cobalt_green"))

    # Create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)


    for file in glob.glob(folder + "*.stl"):

        reader = vtk.vtkSTLReader()
        reader.SetFileName(file)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(1)

        if "repositioned" in file:
            actor.GetProperty().SetDiffuseColor(
                colors.GetColor3d('Red'))
            actor.GetProperty().SetOpacity(.6)
        if "ICP" in file:
            actor.GetProperty().SetOpacity(0)
            actor.GetProperty().SetDiffuseColor(
                colors.GetColor3d('Blue'))


        # Assign actor to the renderer
        ren.AddActor(actor)


    # Enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()


if __name__ == '__main__':
    display(get_program_parameters())
