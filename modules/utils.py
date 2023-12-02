import numpy as np
from PIL import Image, ImageDraw
from typing import List, Tuple
import math, json, os, time

# Object structures
Triangle = Tuple[str, complex, complex, complex] # shape, v1, v2, v3
Rhombi = Tuple[complex, complex, complex, complex] # 4 vertices
Img_slice = Tuple[Image.Image, Tuple[float, float], List[Tuple[float, float]]] # Image, top-left position, relative vertices
Img_database_object = Tuple[int, int, int, float] # r, g, b, color_variance

def create_canvas(size: Tuple[int, int]) -> Image.Image:
    """
    Create a blank canvas.
    
    Parameters:
    size (Tuple[int, int]): The size of the canvas.
    
    Returns:
    Image.Image: A blank canvas.
    """
    return Image.new('RGBA', size, (255, 255, 255, 0))

def distance_complex(v1: complex, v2: complex) -> float:
    """
    Calculate the distance between two complex numbers.
    
    Parameters:
    v1 (complex): The first complex number.
    v2 (complex): The second complex number.
    
    Returns:
    float: The distance between the two complex numbers.
    """
    return abs(v2 - v1)

def complex_to_tuple(z: complex, precision: int = 5) -> Tuple[float, float]:
    """
    Convert a complex number to a tuple of floats.
    
    Parameters:
    z (complex): The complex number.
    precision (int): The number of decimal places to round to.
    
    Returns:
    Tuple[float, float]: The tuple of floats.
    """
    return (round(z.real, precision), round(z.imag, precision))

def round_complex(z: complex, precision: int = 5) -> complex:
    """
    Round a complex number.
    
    Parameters:
    z (complex): The complex number.
    precision (int): The number of decimal places to round to.
    
    Returns:
    complex: The rounded complex number.
    """
    return complex(round(z.real, precision), round(z.imag, precision))

def color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """
    Calculate the distance between two colors.
    
    Parameters:
    color1 (Tuple[int, int, int]): The first color.
    color2 (Tuple[int, int, int]): The second color.
    
    Returns:
    float: The distance between the two colors.
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

def calculate_color_variance(image: Image.Image) -> float:
    """
    Calculate the variance of the colors in an image.

    Parameters:
    image (Image.Image): The image.

    Returns:
    float: The variance of the colors in the image.
    """
    np_image = np.array(image)
    
    # Check if the image is grayscale or color
    if len(np_image.shape) == 2:  # Grayscale image
        variance = np.var(np_image)  # Variance of the grayscale values
    else:  # Color image
        variances = np.var(np_image[:, :, :3], axis=(0, 1))  # Variance for each color channel
        variance = np.mean(variances)  # Overall variance
    return variance

def calculate_average_color(image_slice: Image.Image) -> Tuple[int, int, int]:
    """
    Calculate the average color of an image.
    
    Parameters:
    image_slice (Image.Image): The image.
    
    Returns:
    Tuple[int, int, int]: The average color of the image.
    """
    if isinstance(image_slice, Image.Image):
        if image_slice.mode == 'P':
            # Convert paletted images to RGB
            image_slice = image_slice.convert('RGB')

        pixels = list(image_slice.getdata())
        total_pixels = len(pixels)

        if image_slice.mode == 'RGBA':
            # Image with alpha channel
            avg_r = sum(r for r, g, b, a in pixels) / total_pixels
            avg_g = sum(g for r, g, b, a in pixels) / total_pixels
            avg_b = sum(b for r, g, b, a in pixels) / total_pixels
        else:
            # Image without alpha channel
            avg_r = sum(r for r, g, b in pixels) / total_pixels
            avg_g = sum(g for r, g, b in pixels) / total_pixels
            avg_b = sum(b for r, g, b in pixels) / total_pixels
    elif isinstance(image_slice, np.ndarray):
        # Process as NumPy array
        avg_r = np.mean(image_slice[:, :, 0])
        avg_g = np.mean(image_slice[:, :, 1])
        avg_b = np.mean(image_slice[:, :, 2])
    else:
        raise TypeError("Unsupported image type")
    return int(avg_r), int(avg_g), int(avg_b)

def draw_borders(canvas: Image.Image, tiles: List[Rhombi], color:Tuple[int,int,int]=(0, 255, 0), thickness: int = 1) -> None:
    """
    Draw borders between tiles.
    
    Parameters:
    canvas (Image.Image): The canvas.
    tiles (List[Rhombi]): The tiles.
    color (Tuple[int, int, int]): The color of the borders.
    thickness (int): The thickness of the borders.
    """
    draw = ImageDraw.Draw(canvas)
    for tile in tiles:
        vertices = [(tile[i].real, tile[i].imag) for i in range(0, len(tile))]
        draw.polygon(vertices, outline=color, width=thickness)

def calculate_bounding_box_dimensions(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the width and height of the bounding box for given vertices.
    
    Parameters:
    vertices (List[Tuple[float, float]]): The vertices.
    
    Returns:
    Tuple[float, float]: The width and height of the bounding box."""
    min_x = min(x for x, _ in vertices)
    max_x = max(x for x, _ in vertices)
    min_y = min(y for _, y in vertices)
    max_y = max(y for _, y in vertices)
    return max_x - min_x, max_y - min_y

def log_message(message: str, config: dict) -> None:
    """
    Log a message to the console if verbose mode is enabled.

    Parameters:
    message (str): The message to be logged.
    config (dict): Configuration settings which includes the verbose flag.
    """
    if config.get('verbose', False):
        print(message)
        
def divide_image_into_chunks_and_get_color(image, chunk_size=(10, 10)):
    """ Divide an image into chunks and calculate average color of each chunk. """
    img_array = np.array(image)
    chunk_colors = []
    for x in range(0, img_array.shape[0], chunk_size[0]):
        for y in range(0, img_array.shape[1], chunk_size[1]):
            chunk = img_array[x:x + chunk_size[0], y:y + chunk_size[1]]
            avg_color = calculate_average_color(chunk)
            chunk_colors.append(avg_color)
            
    return chunk_colors

def calculate_scale_factor(config):
    divisions = config['divisions']
    scale = 4 * (2.618 ** divisions) / (math.log(divisions) * (divisions ** 2))
    scale = min(50, scale)
    return scale

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
    log_message(f'0- Loaded configuration from {config_file}', config)
    config['scale_factor'] = calculate_scale_factor(config)
    return config

def load_image(config: dict) -> Image.Image:
    """
    Load the image to be used for the mosaic.
    
    Parameters:
    config (dict): The configuration settings.
    
    Returns:
    Image.Image: The original image.
    """
    log_message(f'3- Loading image from {config["image_path"]}', config)
    original_image = Image.open(config["image_path"])
    original_image.save(os.path.join(config['output_path'], config['original_image_name']))
    return original_image

def save_mosaic(mosaic, color_mosaic, config):
        log_message(f'10- Saving mosaics', config)
        config['timing']['save_mosaic'] = time.time()
        mosaic.save(os.path.join(config['output_path'], config['mosaic_name']), optimize=True)
        color_mosaic.save(os.path.join(config['output_path'], config['color_mosaic_name']), optimize=True)
        log_message(f'11- Saved mosaics. Took {time.time() - config["timing"]["save_mosaic"]}', config)
        return True