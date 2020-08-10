from goicp import goicpAlign
import argparse
import numpy as np
from applyMatrix import align


def protect3DRunner(src, atlas):

    print(atlas, src)
    matrix = goicpAlign(src, atlas)

    # This is what the new file will be called.
    # Ex. ankle.stl -> ankle__reoriented.stl
    srcName  = src.split(".")
    saveName = srcName[0] + "_reoriented.stl"
    print("File saved to " + srcName[0] + "_reoriented.stl")
    align(src, saveName, matrix)


def get_program_parameters():
    description = 'Alignment of external scan with provided atlas.'
    epilogue = '''

    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('src_fn', help='The polydata source file name,e.g. Grey_Nurse_Shark.stl.')
    parser.add_argument('tgt_fn', help='The polydata atlas file name, e.g. AnkleAtlasL.stl.')
    args = parser.parse_args()

    return args.src_fn, args.tgt_fn


if __name__ == '__main__':

    src, atlas = get_program_parameters()
    protect3DRunner(src, atlas)
