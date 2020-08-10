import vtk
import numpy as np;
from sklearn.neighbors import NearestNeighbors
from vtk.util.numpy_support import vtk_to_numpy
import time


radius = 40

def crop(toCrop, templateVtk):
    start_time = time.time()
    toCropVtk= vtk.vtkPolyData()
    toCropVtk.DeepCopy(toCrop)

    toCropNp = vtk_to_numpy(toCropVtk.GetPoints().GetData())
    templateNp = vtk_to_numpy(templateVtk.GetPoints().GetData())
    neigh = NearestNeighbors(n_neighbors=1)
    neigh.fit(templateNp)


    cell_array = vtk.vtkCellArray()
    points = vtk.vtkPoints()
    point_id = 0
    for i in range(toCropVtk.GetNumberOfCells()):
        pointsInCell = vtk_to_numpy(toCropVtk.GetCell(i).GetPoints().GetData())
        arr = neigh.kneighbors(pointsInCell)
        max = np.max(arr[0])
        if(max <= radius):
            polygon = vtk.vtkPolygon()
            polygon.GetPointIds().SetNumberOfIds(3)
            for n in range(3):
                points.InsertNextPoint(pointsInCell[n])
                polygon.GetPointIds().SetId(n, point_id)
                point_id += 1
            cell_array.InsertNextCell(polygon)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(cell_array)

    print("CropTime (sec): " + str(time.time() - start_time))
    return polydata



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

    crop(ReadPolyData("meshes/AnkleMesh_1_L_Output.stl"), ReadPolyData("meshes/AnkleAtlasL.stl"))
