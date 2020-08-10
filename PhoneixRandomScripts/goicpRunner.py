from goicp import goicpTransform
import argparse
import vtk
from croping import crop
from visual import visualizeVTK



def main():
    atlas = "meshes/AnkleAtlasL.stl"
    src = get_program_parameters()
    print(atlas, src)
    t, newVtk = goicpTransform(src, atlas)
    i = input("Was the transformation correct? (y/n) : ")
    if(i == "n" ):
        t, newVtk = goicpTransform(src, atlas,  mseUnscaled = .035, pruneAmount = 200, trimFraction = 0, dtSize = 200)
        i = input("Was the transformation correct? (y/n) : ")
        if(i == "n" ):
            t, newVtk = goicpTransform(src, atlas,  mseUnscaled = .025, pruneAmount = 200, trimFraction = .1, dtSize = 300)


    #
    # #cropAtlas = "meshes/AnkleMesh_5_L_Output.stl"
    # print("Starting croping-----")
    # croped = crop(newVtk, ReadPolyData(atlas))
    # visualizeVTK(croped)
    #
    # i = input("Do you want to save the output? (y/n) : ")
    # if(i=="y"):
    #     srcName  = src.split(".")
    #     print("file saved to " + srcName[0] + "_reoriented.stl")
    #     stlWriter = vtk.vtkSTLWriter()
    #     stlWriter.SetFileName(srcName[0] + "_reoriented.stl")
    #     stlWriter.SetInputData(newVtk)
    #     stlWriter.Write()

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
