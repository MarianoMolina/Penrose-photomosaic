import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ..modules.create_tiles import create_tiles_and_scale

def test_create_tiles():
    canvas_size = (1080, 1080)
    divisions = 6
    tiles = create_tiles_and_scale(divisions, canvas_size)

    fig, ax = plt.subplots()
    ax.set_xlim(0, canvas_size[0])
    ax.set_ylim(0, canvas_size[1])

    # Draw each tile
    for tile in tiles:
        polygon = patches.Polygon([(tile[i], tile[i + 1]) for i in range(0, len(tile), 2)], closed=True, edgecolor='black', fill=False)
        ax.add_patch(polygon)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

test_create_tiles()
