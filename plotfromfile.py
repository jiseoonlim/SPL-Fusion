import matplotlib.pyplot as plt
import pandas as pd

fig = plt.figure()
ax = plt.axes(projection = '3d')

data = pd.read_csv('C:/Users/IBSLAB/Desktop/SPL/1218_3.txt', sep=",", header=None)
data.columns = ['x','y','z']

ax.scatter(data.x, data.y, data.z, s=2, marker='.', cmap='plasma', c =data.z)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

plt.show()