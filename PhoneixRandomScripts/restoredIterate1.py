from ICP import realign
from visualFolder import display
import glob
import vtk
import re
import argparse

def get_program_parameters():

    description = 'Restored Align'
    epilogue = '''

    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('folder', help='The polydata source folder,e.g. meshes/.')


    args = parser.parse_args()

    return args.folder

def restore(folder = ""):
    if folder[-1] != "/":
        folder = folder + "/"
    original = {}
    repositioned = {}

    for file in glob.glob(folder + "*.stl"):
        name = file.split("/")
        name = re.split("_|\.", name[-1])

        if "ICP" in name:
            continue
        elif "repositioned" in name:
            repositioned[name[0]] = file
        else:
            original[name[0]] = file



    for k in original.keys():
        if k in repositioned.keys():
            transformed = realign(original[k], repositioned[k])
            stlWriter = vtk.vtkSTLWriter()
            stlWriter.SetFileName(folder + k + "_ICP"+".stl")
            stlWriter.SetInputData(transformed)
            stlWriter.Write()

    display(folder)


if __name__ == '__main__':
    restore(get_program_parameters())
