import numpy as np
from stl import mesh
your_mesh = mesh.Mesh.from_file('Dec.stl')
print(len(your_mesh))
print(np.reshape(your_mesh.points, (len(your_mesh)*3, 3)))

your_mesh.points *= 10

print(np.reshape(your_mesh.points, (len(your_mesh)*3, 3)))


from mpl_toolkits import mplot3d
from matplotlib import pyplot
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(tgtNp1.vectors))
scale = tgtNp1.points.flatten("f")
axes.auto_scale_xyz(scale, scale, scale)
pyplot.show()
