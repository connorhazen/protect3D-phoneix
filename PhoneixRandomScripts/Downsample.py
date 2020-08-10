"""
Uses two different methods of smoothing dataset
Uses decimation method to downsample number of points in mesh w/ given specifications
Displays original mesh, both smoothed meshes, and downsampled mesh using VTK
"""

#%%
import vtk 

#%%
def ReadPolyData(file_name):
    import os
    path, extension = os.path.splitext(file_name)
    extension = extension.lower()
    reader = vtk.vtkSTLReader()
    reader.SetFileName(file_name)
    reader.Update()
    poly_data = reader.GetOutput()
    return poly_data

def decimation(poly, fraction=0.1, N=None, method='quadric', boundaries=False):
        """
        Downsample the number of vertices in a mesh to `fraction`.

        :param float fraction: the desired target of reduction.
        :param int N: the desired number of final points
            (**fraction** is recalculated based on it).
        :param str method: can be either 'quadric' or 'pro'. 
            In the first case triagulation will look like more regular, 
            irrespective of the mesh origianl curvature.
            In the second case triangles are more irregular but mesh is more precise on more
            curved regions.
        :param bool boundaries: (True), in `pro` mode decide whether
            to leave boundaries untouched or not.

        .. note:: Setting ``fraction=0.1`` leaves 10% of the original nr of vertices.
        """

        if N:  
            num = poly.GetNumberOfPoints()
            fraction = float(N) / num
            if fraction >= 1:
                return originalSourcePolyData
        if 'quad' in method:
            decimate = vtk.vtkQuadricDecimation()
            decimate.SetAttributeErrorMetric(True)
            decimate.SetVolumePreservation(True)
        else:
            decimate = vtk.vtkDecimatePro()
            decimate.PreserveTopologyOn()
            if boundaries:
                decimate.BoundaryVertexDeletionOff()
            else:
                decimate.BoundaryVertexDeletionOn()
                
        decimate.SetInputData(poly)
        decimate.SetTargetReduction(1 - fraction)
        decimate.Update()
        return vtk.vtkPolyData(), decimate

#%%
#file = '/Users/Sophia/protect3d-restor3d-Phoenix/meshes/l_ankle_scan_1.stl'
file = 'AdamsS_XC1P28 Reposititioned Anatomy.stl'

sourcePolyData = ReadPolyData(file)
originalSourcePolyData = vtk.vtkPolyData()
originalSourcePolyData.DeepCopy(sourcePolyData)

print("Before decimation\n"
          "-----------------\n"
          "There are " + str(sourcePolyData.GetNumberOfPoints()) + " points.\n"
          "There are " + str(sourcePolyData.GetNumberOfPolys()) + " polygons.\n")

# Clean the polydata so that the edges are shared 
cleanPolyData = vtk.vtkCleanPolyData()
cleanPolyData.SetInputData(originalSourcePolyData)

# Smooth data using different methods
smooth_loop = vtk.vtkLoopSubdivisionFilter()
smooth_loop.SetNumberOfSubdivisions(3)
smooth_loop.SetInputConnection(cleanPolyData.GetOutputPort())

smooth_butterfly = vtk.vtkButterflySubdivisionFilter()
smooth_butterfly.SetNumberOfSubdivisions(3)
smooth_butterfly.SetInputConnection(cleanPolyData.GetOutputPort())

smoothedData = vtk.vtkPolyData()
smoothedData.DeepCopy(smoothedData)

# decrease number of points in mesh through decimation
downsampleMesh, decimate = decimation(originalSourcePolyData, N=1000) # reduce to 1000 pts

#%%
colors = vtk.vtkNamedColors()
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)
 
# Create a mapper and actor for initial dataset
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(originalSourcePolyData)
mapper.ScalarVisibilityOff()
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetPointSize(20)
actor.GetProperty().SetDiffuseColor(
        colors.GetColor3d('White'))
renderer.AddActor(actor)

# Create a mapper and actor for smoothed dataset (vtkLoopSubdivisionFilter)
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(smooth_loop.GetOutputPort())
actor_loop = vtk.vtkActor()
actor_loop.SetMapper(mapper)
actor_loop.SetPosition(400, 0, 0)
actor_loop.GetProperty().SetDiffuseColor(
        colors.GetColor3d('Tomato'))
renderer.AddActor(actor_loop)

# Create a mapper and actor for smoothed dataset (vtkButterflySubdivisionFilter)
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(smooth_butterfly.GetOutputPort())
actor_butterfly = vtk.vtkActor()
actor_butterfly.SetMapper(mapper)
actor_butterfly.SetPosition(0, 400, 0)
actor_butterfly.GetProperty().SetDiffuseColor(
        colors.GetColor3d('Blue'))
renderer.AddActor(actor_butterfly)


# Create a mapper and actor for downsampled dataset
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(decimate.GetOutputPort())
actor_downsample = vtk.vtkActor()
actor_downsample.SetMapper(mapper)
actor_downsample.SetPosition(400, 400, 0)
actor_downsample.GetProperty().SetDiffuseColor(
        colors.GetColor3d('Green'))
renderer.AddActor(actor_downsample)


# Visualize
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Add actors and render
renderer.AddActor(actor)
renderer.AddActor(actor_loop)
renderer.AddActor(actor_butterfly)
renderer.AddActor(actor_downsample)

renderer.SetBackground(1, 1, 1) # Background color white
renderWindow.SetSize(800, 800)
renderWindow.Render()
renderWindowInteractor.Start()
