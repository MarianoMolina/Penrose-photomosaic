import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the color data from the database
with open('photomosaic/image_database.json') as file:
    data = json.load(file)

# Extract RGB values
r, g, b = zip(*[color for _, color in data.items()])

# Create a 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(r, g, b)

ax.set_xlabel('Red Channel')
ax.set_ylabel('Green Channel')
ax.set_zlabel('Blue Channel')

plt.show()
