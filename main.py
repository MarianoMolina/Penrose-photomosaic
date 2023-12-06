# Local Imports
from modules.utils import load_image, save_mosaic
from modules.update_database import update_database_and_config
from modules.create_tiles import (
    get_rhombi_by_division_and_scale,
)
from modules.replace_slices import slice_and_place_images, create_mosaic
from modules.database_visualize import visualize_database_and_target_image_colors
from modules.gradio_ui import mosaic_interface

def start():
    """
    Main function to generate a Penrose tiles photomosaic.
    This function orchestrates the entire process of creating a photomosaic using Penrose tiling. 
    It starts by loading the configuration settings from a JSON file. 
    Then it updates the image database based on the images present in the source folder. 
    After loading the target image for the mosaic, it proceeds to create and draw tiles 
    based on the number of divisions specified in the configuration.
    Next, it slices the original image into Penrose tile shapes and places these slices onto a canvas. 
    These slices are then replaced with corresponding images from the database that best match in color. 
    Finally, the completed mosaic is saved to the specified output path.

    Parameters:
    config (dict): Configuration settings loaded from 'config.json'.

    Output:
    - The original image, Penrose tiles visualization, and the final photomosaic are saved in the 
    specified output directory.
    - If verbose mode is enabled in the configuration, progress logs are printed to the console.
    """
    # Load config and database
    config = update_database_and_config("photomosaic/config.json")
    # Visualize database and target image colors
    if config["show_color_analysis"]:
        visualize_database_and_target_image_colors(config)
    # Load image
    original_image = load_image(config)
    # Get tile vectors
    tiles = get_rhombi_by_division_and_scale(original_image.size, config)
    # Slice image
    slices = slice_and_place_images(original_image, tiles, config)
    # Replace slices with target
    mosaic, color_mosaic = create_mosaic(slices, original_image.size, config)
    # Save result
    if save_mosaic(mosaic, color_mosaic, config):
        print(f'Finished. Mosaics saved to {config["output_path"]}.')

if __name__ == "__main__":
    # start()
    mosaic_interface.launch()
