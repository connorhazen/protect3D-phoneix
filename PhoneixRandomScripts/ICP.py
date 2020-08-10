import vtk
import random
import numpy as np
from sklearn.neighbors import NearestNeighbors
import argparse
from vtk.util.numpy_support import vtk_to_numpy
from math import ceil, cos, radians

def get_program_parameters():

    description = 'How to align two vtkPolyData\'s.'
    epilogue = '''

    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('src_fn', help='The polydata source file name,e.g. Grey_Nurse_Shark.stl.')
    parser.add_argument('tgt_fn', help='The polydata target file name, e.g. shark.ply.')

    args = parser.parse_args()

    return args.src_fn, args.tgt_fn


def realign(src_fn = "", tgt_fn = ""):
    colors = vtk.vtkNamedColors()

    print('Loading source:', src_fn)
    sourcePolyData = ReadPolyData(src_fn)
    # Save the source polydata in case the align does not improve
    # segmentation
    originalSourcePolyData = vtk.vtkPolyData()
    originalSourcePolyData.DeepCopy(sourcePolyData)

    print('Loading target:', tgt_fn)
    tpd = ReadPolyData(tgt_fn)

    # renderer = vtk.vtkRenderer()
    # renderWindow = vtk.vtkRenderWindow()
    # renderWindow.AddRenderer(renderer)
    # interactor = vtk.vtkRenderWindowInteractor()
    # interactor.SetRenderWindow(renderWindow)



    #Using loops to account for local minima

    points = tpd.GetPoints()
    array = points.GetData()
    numpyNodesTarget = vtk_to_numpy(array)




    # Set up the transform filter
    tempData = vtk.vtkPolyData()
    tempData.DeepCopy(sourcePolyData)
    translation = vtk.vtkTransform()

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(tempData)
    transformFilter.SetTransform(translation)
    transformFilter.Update()

    points = transformFilter.GetOutput().GetPoints()
    array = points.GetData()
    numpyNodesSource = vtk_to_numpy(array)

    T, distances, i = ICP(numpyNodesSource, numpyNodesTarget, max_iterations=1000, convergence = .001)

    myTrans = vtk.vtkTransform()
    myTrans.SetMatrix(T.flatten())

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(tempData)
    transformFilter.SetTransform(myTrans)
    transformFilter.Update()



    bestDistance = np.mean(distances)
    bestTransform = transformFilter.GetOutput()










    #Old Method, no loops to "shake up" source poly.
    # # Refine the alignment using IterativeClosestPoint
    # icp = vtk.vtkIterativeClosestPointTransform()
    # icp.SetSource(sourcePolyData)
    # icp.SetTarget(tpd.GetOutput())
    # icp.GetLandmarkTransform().SetModeToRigidBody()
    # icp.SetMaximumNumberOfLandmarks(100)
    # icp.SetMaximumMeanDistance(.00001)
    # icp.SetMaximumNumberOfIterations(10000)
    # icp.CheckMeanDistanceOn()
    # icp.StartByMatchingCentroidsOn()
    # icp.Update()
    #
    # #  print(icp)
    #
    #
    # lmTransform = icp.GetLandmarkTransform()
    # transform = vtk.vtkTransformPolyDataFilter()
    #
    #
    # transform.SetInputData(sourcePolyData)
    # transform.SetTransform(lmTransform)
    # transform.SetTransform(icp)
    # transform.Update()
    # distance.SetInputData(0, tpd.GetOutput())
    # distance.SetInputData(1, transform.GetOutput())
    # distance.Update()
    #
    # distanceAfterICP = distance.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)
    #
    # if distanceAfterICP < bestDistance:
    #     bestDistance = distanceAfterICP
    #
    # bestTransform = transform.GetOutput()
    #
    #

    # print('min: {:0.5f}'.format(bestDistance))
    #
    # sourceMapper = vtk.vtkDataSetMapper()
    # sourceMapper.SetInputData(bestTransform)
    #
    # sourceMapper.ScalarVisibilityOff()
    #
    # sourceActor = vtk.vtkActor()
    # sourceActor.SetMapper(sourceMapper)
    # sourceActor.GetProperty().SetOpacity(.6)
    # sourceActor.GetProperty().SetDiffuseColor(
    #     colors.GetColor3d('White'))
    # renderer.AddActor(sourceActor)
    #
    # targetMapper = vtk.vtkDataSetMapper()
    # targetMapper.SetInputData(tpd.GetOutput())
    # targetMapper.ScalarVisibilityOff()
    #
    # targetActor = vtk.vtkActor()
    # targetActor.SetMapper(targetMapper)
    # targetActor.GetProperty().SetDiffuseColor(
    #     colors.GetColor3d('Tomato'))
    # renderer.AddActor(targetActor)
    #
    #
    # originalMapper = vtk.vtkPolyDataMapper()
    # originalMapper.SetInputData(originalSourcePolyData)
    # originalActor = vtk.vtkActor()
    # originalActor.GetProperty().SetDiffuseColor(
    #     colors.GetColor3d('Blue'))
    # originalActor.SetMapper(originalMapper)
    #
    # # uncomment if want to see orginal source
    # renderer.AddActor(originalActor)
    #
    # renderWindow.AddRenderer(renderer)
    # renderer.SetBackground(colors.GetColor3d("sea_green_light"))
    # renderer.UseHiddenLineRemovalOn()
    #
    # renderWindow.SetSize(640, 480)
    # renderWindow.Render()
    # renderWindow.SetWindowName('AlignTwoPolyDatas')
    # renderWindow.Render()
    # interactor.Start()

    return bestTransform


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

def best_fit_transform(A, B):
    '''
    Calculates the least-squares best-fit transform that maps corresponding points A to B in m spatial dimensions
    Input:
      A: Nxm numpy array of corresponding points
      B: Nxm numpy array of corresponding points
    Returns:
      T: (m+1)x(m+1) homogeneous transformation matrix that maps A on to B
      R: mxm rotation matrix
      t: mx1 translation vector
    '''

    assert A.shape == B.shape

    # get number of dimensions
    m = A.shape[1]

    # translate points to their centroids
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # special reflection case
    if np.linalg.det(R) < 0:
       Vt[m-1,:] *= -1
       R = np.dot(Vt.T, U.T)

    # translation
    t = centroid_B.T - np.dot(R,centroid_A.T)

    # homogeneous transformation
    T = np.identity(m+1)
    T[:m, :m] = R
    T[:m, m] = t

    return T, R, t


def nearest_neighbor(src, dst):
    '''Find the nearest (Euclidean) neighbor in dst for each point in src

    Parameters
    ----------
        src: Pxm array of points
        dst: Qxm array of points
    Returns
    -------
        distances: P-elements array of Euclidean distances of the nearest neighbor
        indices: P-elements array of dst indices of the nearest neighbor
    '''
    # Asserting src and dst have the same dimension. They can have different point count.
    assert src.shape[1] == dst.shape[1]

    neigh = NearestNeighbors(n_neighbors=1)
    neigh.fit(dst)
    distances, indices = neigh.kneighbors(src, return_distance=True)
    return distances.ravel(), indices.ravel()


def ICP(A, B, standard_deviation_range = 0.0, init_pose=None, max_iterations=100, convergence=0.001, quickconverge=1):
    '''
    The Iterative Closest Point method: finds best-fit transform that maps points A on to points B
    Input:
        A: Pxm numpy array of source m-Dimensioned points
        B: Qxm numpy array of destination m-Dimensioned point
        standard_deviation_range: If this value is not zero, the outliers (defined by the given standard Deviation) will be ignored.
        init_pose: (m+1)x(m+1) homogeneous transformation
        max_iterations: exit algorithm after max_iterations
        convergence: convergence criteria
        quickconverge: streategy to overapply transformation at each iteration. Value of 2 means two transforamtions are made.
        filename: fileName to save the In-Progress data for preview
    Output:
        T: final homogeneous transformation that maps A on to B
        distances: Euclidean distances (errors) of the nearest neighbor
        i: number of iterations to converge
    '''

    # Asserting A and B have the same dimension. They can have different point count.
    assert A.shape[1] == B.shape[1]

    # get number of dimensions
    m = A.shape[1]

    # make points homogeneous, copy them to maintain the originals
    src = np.ones((m+1,A.shape[0]))
    dst = np.ones((m+1,B.shape[0]))
    src[:m,:] = np.copy(A.T)
    dst[:m,:] = np.copy(B.T)

    # apply the initial pose estimation
    if init_pose is not None:
        src = np.dot(init_pose, src)

    prev_error = 0
    delta_error = 0



    for i in range(max_iterations):

        # find the nearest neighbors between the current source and destination points
        distances, indices = nearest_neighbor(src[:m,:].T, dst[:m,:].T)

        #Compute Mean Error and Standard Deviation
        mean_error = np.mean(distances)
        stde_error = np.std(distances)

        #Ignore distances that are outlers
        if standard_deviation_range > 0.0:
            trimmed_dst_indices = []
            trimmed_src_indices = []
            for j in range(len(indices)):
                if distances[j] > (mean_error + standard_deviation_range * stde_error):
                    continue
                if distances[j] < (mean_error - standard_deviation_range * stde_error):
                    continue
                trimmed_dst_indices.append(indices[j])
                trimmed_src_indices.append(j)
            # compute the transformation between the selected values in source and nearest destination points
            T,_,_ = best_fit_transform(src[:m,trimmed_src_indices].T, dst[:m,trimmed_dst_indices].T)
            #Recomputing Mean Error based on selected distances
            mean_error = np.mean(distances[trimmed_src_indices])
        else:
            # compute the transformation between the source and nearest destination points
            T,_,_ = best_fit_transform(src[:m,:].T, dst[:m,indices].T)

        #Transform the current source
        if quickconverge > 1.0:
            if i > 2:
                if delta_error > 0.0:
                    quickconverge = quickconverge - 0.4

        for p in range(int(ceil(quickconverge))):
            src = np.dot(T, src)

        #Log the current transformation matrix
        currentT,_,_ = best_fit_transform(A, src[:m,:].T)

        # logging.debug(np.array2string(T.flatten(),separator=","))

        # check error to see if convergence cretia is met
        delta_error = (mean_error - prev_error)

        if np.abs(delta_error) < convergence:
            break
        prev_error = mean_error


    # calculate final transformation
    T,_,_ = best_fit_transform(A, src[:m,:].T)

    return T, distances, i


if __name__ == '__main__':
    src_fn, tgt_fn = get_program_parameters()
    realign(src_fn, tgt_fn)
