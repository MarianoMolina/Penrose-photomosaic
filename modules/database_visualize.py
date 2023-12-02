import json
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image
from .utils import divide_image_into_chunks_and_get_color, color_distance, log_message

def visualize_database_and_target_image_colors(config: dict):
    # Load the color data from the database
    if config.get('verbose', False): log_message(f'(opt) - Visualizing database data and target image colors', config)
    with open(config['database_path']) as file:
        data = json.load(file)
        
    image = Image.open(config['image_path'])
    rgb_image = image.convert('RGB')
    colors = divide_image_into_chunks_and_get_color(rgb_image)
    r_img, g_img, b_img = zip(*colors)

    # Extract RGB values
    r_db, g_db, b_db, _ = zip(*[color for color in data.values()])
    distances = [min([color_distance(tc, dbc) for dbc in zip(r_db, g_db, b_db)]) for tc in colors]
    norm = Normalize(vmin=min(distances), vmax=max(distances))
    normalized_distances = [norm(d) for d in distances]
    point_color = plt.cm.viridis(normalized_distances) 
    
    def sync_rotation(event):
        # Synchronize the rotation of both plots
        if event.inaxes == ax1:
            ax2.view_init(elev=ax1.elev, azim=ax1.azim)
        elif event.inaxes == ax2:
            ax1.view_init(elev=ax2.elev, azim=ax2.azim)
        fig.canvas.draw_idle()
    
    # Create a figure with two 3D subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'projection': '3d'})

    # Plot the database colors in the first subplot
    ax1.scatter(r_db, g_db, b_db)
    ax1.set_title("Database Colors")

    # Plot the image colors in the second subplot
    ax2.scatter(r_img, g_img, b_img, color=point_color)
    ax2.set_title("Image Colors")
    
    for axis in [ax1, ax2]:
        axis.set_xlabel('Red Channel')
        axis.set_ylabel('Green Channel')
        axis.set_zlabel('Blue Channel')
        
    # Connect the rotation event
    fig.canvas.mpl_connect('motion_notify_event', sync_rotation)

    # Show the figure
    plt.show()