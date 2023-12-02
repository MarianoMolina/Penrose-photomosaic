# Standard Library Imports
import json
import os
from typing import List, Tuple

# Related Third-party Imports
from PIL import Image

# Local Application/Library Specific Imports
from modules.utils import Rhombi, Img_slice, create_canvas, draw_borders
from modules.update_database import update_image_database
from modules.create_tiles import create_tiles
from modules.replace_slices import slice_image, replace_slices, place_slices_on_canvas

def main():
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
    if update_database(config):
        original_image = load_image(config)
        tiles = create_and_draw_tiles(original_image, config)
        slices = slice_and_place_images(original_image, tiles, config)
        mosaic = create_mosaic(slices, original_image.size, config)
        save_mosaic(mosaic, config)
        log_message(f'Done', config)

def update_database(config: dict) -> bool:
    """
    Update the image database if the source folder has been modified since the last update.
    
    Returns:
    bool: True if the database was updated, False otherwise.
    """
    log_message('Updating image database...', config)
    return update_image_database(config['source_folder'], config['database_path'], config['image_folder'])

def load_config(config_file: str) -> dict:
    """
    Load the configuration settings from a JSON file.

    Parameters:
    config_file (str): The path to the configuration JSON file.

    Returns:
    dict: Configuration settings loaded from the file.
    """
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def load_image(config: dict) -> Image.Image:
    """
    Load the image to be used for the mosaic.
    
    Parameters:
    config (dict): The configuration settings.
    
    Returns:
    Image.Image: The original image.
    """
    log_message(f'Loading image from {config["image_path"]}', config)
    original_image = Image.open(config["image_path"])
    original_image.save(os.path.join(config['output_path'], config['original_image_name']))
    log_message(f'Loaded image with size: {original_image.size}', config)
    return original_image

def create_and_draw_tiles(image: Image.Image, config: dict) -> List[Rhombi]:
    """
    Create the tiles for the mosaic and draw them on a canvas.
    
    Parameters:
    image (Image.Image): The original image.
    config (dict): The configuration settings.
    
    Returns:
    List[Rhombi]: The tiles for the mosaic.
    """
    log_message(f'Creating tiles for {config["divisions"]} divisions in a {image.size} canvas', config)
    tiles = create_tiles(config['divisions'], image.size)
    # Save a copy of the tiles with borders
    canvas = create_canvas(image.size)
    draw_borders(canvas, tiles, color=(255, 0, 0))
    canvas.save(os.path.join(config['output_path'], config['tile_canvas_name']), optimize=True)
    log_message(f'Created {len(tiles)} Rhombi', config)
    return tiles

def slice_and_place_images(image: Image.Image, tiles: List[Rhombi], config: dict) -> List[Img_slice]:
    """
    Slice the original image into tiles and place them on a canvas.
    
    Parameters:
    image (Image.Image): The original image.
    tiles (List[Rhombi]): The tiles for the mosaic.
    config (dict): The configuration settings.
    
    Returns:
    List[Img_slice]: The slices of the original image.
    """
    log_message(f'Slicing image {config["image_path"]} into {len(tiles)} slices', config)
    slices = slice_image(image, tiles)
    log_message(f'Created {len(slices)} slices. Placing on canvas...', config)
    # Save a copy of the slices with borders
    canvas = create_canvas(image.size)
    place_slices_on_canvas(canvas, slices)
    draw_borders(canvas, tiles)
    canvas.save(os.path.join(config['output_path'], config['image_with_borders_name']), optimize=True)
    return slices

def create_mosaic(slices: List[Img_slice], size: Tuple[int, int], config: dict) -> Image.Image:
    """
    Create the mosaic by replacing the slices with images from the database.
    
    Parameters:
    slices (List[Img_slice]): The slices of the original image.
    size (Tuple[int, int]): The size of the original image.
    config (dict): The configuration settings.
    
    Returns:
    Image.Image: The mosaic.
    """
    log_message(f'Replacing slices with images from database...', config)
    scale_factor = 2 * (2.65 ** (config['divisions'] - 1))/(config['divisions']*2)
    mosaic = replace_slices(slices, config['database_path'], scale_factor, config['image_folder'])
    scaled_canvas_size = (int(size[0] * scale_factor),
                          int(size[1] * scale_factor))
    new_canvas = create_canvas(scaled_canvas_size)
    place_slices_on_canvas(new_canvas, mosaic)
    return new_canvas

def save_mosaic(mosaic: Image.Image, config: dict) -> None:
    """
    Save the mosaic to the output folder.
    """
    mosaic.save(os.path.join(config['output_path'], config['mosaic_name']), optimize=True)

def log_message(message: str, config: dict) -> None:
    """
    Log a message to the console if verbose mode is enabled.

    Parameters:
    message (str): The message to be logged.
    config (dict): Configuration settings which includes the verbose flag.
    """
    if config.get('verbose', False):
        print(message)

if __name__ == '__main__':
    main()