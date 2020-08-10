# Iterative Closest Point Method to find a best fit rigid transformation 
# btwn two point sets

import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy

def getData(file_name):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(file_name)
    reader.Update()
    polydata = reader.GetOutput()
    
    points = polydata.GetPoints()
    array = points.GetData()
    numpy_nodes = vtk_to_numpy(array)
    return numpy_nodes

def find_rigid_alignment(A, B):
	"""
	2-D or 3-D registration with known correspondences.
	Registration occurs in the zero centered coordinate system, and then
	must be transported back.

		Args:
		-	A: Numpy array of shape (N,D) -- Reference Point Cloud (target)
		-	B: Numpy array of shape (N,D) -- Point Cloud to Align (source)

		Returns:
		-	R: optimal rotation
		-	t: optimal translation
	"""
	num_pts = A.shape[0]
	dim = A.shape[1]

	a_mean = np.mean(A, axis=0)
	b_mean = np.mean(B, axis=0)

	# Zero-center the point clouds
	A -= a_mean
	B -= b_mean

	N = np.zeros((dim, dim))
	for i in range(num_pts):
		N += A[i].reshape(dim,1).dot( B[i].reshape(1,dim) )
	N = A.T.dot(B)

	U, D, V_T = np.linalg.svd(N)
	S = np.eye(dim)
	det = np.linalg.det(U) * np.linalg.det(V_T.T)
	
	# Check for reflection case
	if not np.isclose(det,1.):
		S[dim-1,dim-1] = -1

	R = U.dot(S).dot(V_T)
	t = R.dot( b_mean.reshape(dim,1) ) - a_mean.reshape(dim,1)
	return R, -t.squeeze()

#A = getData("AdamsS_XC1P28 Preoperative Anatomy.stl")
#B = getData("AdamsS_XC1P28 Reposititioned Anatomy.stl")

A = getData("AnkleMesh_1_L_Output.stl")    
B = getData("l_ankle_scan_1.stl")
print(find_rigid_alignment(A,B))