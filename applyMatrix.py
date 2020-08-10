import numpy as np
from stl import mesh


def align(filename, saveName, matrix):
    stl = mesh.Mesh.from_file(filename)
    stl.transform(matrix)
    stl.save(saveName)
