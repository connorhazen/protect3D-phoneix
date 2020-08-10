import vtk
def get_program_parameters():
    import argparse
    description = 'Read a .stl file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='42400-IDGH.stl')
    args = parser.parse_args()
    return args.filename

def main():
    colors = vtk.vtkNamedColors()

    filename = get_program_parameters()

    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)

    originalMapper = vtk.vtkPolyDataMapper()
    originalMapper.SetInputConnection(reader.GetOutputPort())

    # # Create the polydata geometry
    # reader = vtk.vtkSphereSource()
    # reader.Update()
    #
    # # Set up the actor to display the untransformed polydata
    # originalMapper = vtk.vtkPolyDataMapper()
    # originalMapper.SetInputConnection(reader.GetOutputPort())

    originalActor = vtk.vtkActor()
    originalActor.SetMapper(originalMapper)
    originalActor.GetProperty().SetColor(colors.GetColor3d("blue"))

    # Set up the transform filter
    translation = vtk.vtkTransform()
    # translation.Translate(1000.0, 100.0, 500.0)
    translation.RotateX(10.0)
    # translation.RotateY(120.0)
    # translation.RotateZ(85.0)


    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(reader.GetOutputPort())
    transformFilter.SetTransform(translation)
    transformFilter.Update()
    # transformFilter.RotateX(90)



    # Set up the actor to display the transformed polydata
    transformedMapper = vtk.vtkPolyDataMapper()
    transformedMapper.SetInputConnection(transformFilter.GetOutputPort())

    transformedActor = vtk.vtkActor()
    transformedActor.SetMapper(transformedMapper)
    transformedActor.GetProperty().SetColor(colors.GetColor3d("red"))
    # transformedActor.RotateX(90)

    # Set up the rest of the visualization pipeline
    renderer = vtk.vtkRenderer()
    renderer.AddActor(originalActor)
    renderer.AddActor(transformedActor)
    renderer.SetBackground(colors.GetColor3d("green")) # Set renderer's background color to green

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.Start()

    stlWriter = vtk.vtkSTLWriter()
    stlWriter.SetFileName("meshes/trial1.stl")
    stlWriter.SetInputConnection(transformFilter.GetOutputPort())
    stlWriter.Write()

if __name__ == '__main__':
    main()
