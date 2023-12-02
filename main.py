# Standard Library Imports
import os

# Local Imports
from modules.utils import load_config, load_image, save_mosaic
from modules.update_database import update_image_database
from modules.create_tiles import create_and_draw_tiles
from modules.replace_slices import slice_and_place_images, create_mosaic
from modules.database_visualize import visualize_database_and_target_image_colors

def start():
    """
    Main function to generate a Penrose tiles photomosaic.
    This function orchestrates the entire process of creating a photomosaic using Penrose tiling. It starts by loading the configuration settings from a JSON file. Then it updates the image database based on the images present in the source folder. After loading the target image for the mosaic, it proceeds to create and draw tiles based on the number of divisions specified in the configuration.
    Next, it slices the original image into Penrose tile shapes and places these slices onto a canvas. These slices are then replaced with corresponding images from the database that best match in color. Finally, the completed mosaic is saved to the specified output path.

    Parameters:
    config (dict): Configuration settings loaded from 'config.json'.
    
    Output:
    - The original image, Penrose tiles visualization, and the final photomosaic are saved in the specified output directory.
    - If verbose mode is enabled in the configuration, progress logs are printed to the console.
    """
    config = load_config('photomosaic/config.json')
    if update_image_database(config):
        if config['show_color_analysis']: visualize_database_and_target_image_colors(config)
        original_image = load_image(config)
        tiles = create_and_draw_tiles(original_image, config)
        slices = slice_and_place_images(original_image, tiles, config)
        mosaic, color_mosaic = create_mosaic(slices, original_image.size, config)
        if save_mosaic(mosaic, color_mosaic, config):
            print(f'Finished. Mosaics saved to {config["output_path"]}.')
        
if __name__ == '__main__':
    start()