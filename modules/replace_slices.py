from PIL import Image, ImageDraw
from typing import List, Tuple
from .utils import *
import json, random

def slice_image(image: str, tiles: List[Rhombi]) -> List[Img_slice]:
    """
    Slice the original image into tiles and place them on a canvas.
    
    Parameters:
    image (Image.Image): The original image.
    tiles (List[Rhombi]): The tiles for the mosaic.
    
    Returns:
    List[Img_slice]: The image slices.
    """
    slices = []

    for tile in tiles:
        # Convert complex vertices to a list of (x, y) tuples
        absolute_vertices = [(vertex.real, vertex.imag) for vertex in tile]
        # Find the top-left position of the tile
        top_left_x = min(x for x, _ in absolute_vertices)
        top_left_y = min(y for _, y in absolute_vertices)
        top_left_position = (top_left_x, top_left_y)
        # Convert vertices to integer and calculate relative positions
        relative_vertices = [(x - top_left_x, y - top_left_y) for x, y in absolute_vertices]
        slice_img = get_masked_slice(image, absolute_vertices)
        # Append the image slice, its top-left position, and its relative vertices
        slices.append((slice_img, top_left_position, relative_vertices))
    return slices

# Adjust blending based on variance and color distance
def adjust_blend_strength(variance: float, color_distance: int, max_opacity=1.0) -> float:
    """
    Adjust the blending strength based on the variance and color distance.
    
    Parameters:
    variance (float): The variance of the image.
    color_distance (int): The distance between the average color of the slice and the replacement image.
    max_opacity (float): The maximum opacity of the replacement image.
    
    Returns:
    float: The adjusted opacity.
    """
    strength = min(max_opacity, (variance / 10000) + (color_distance / 100))
    return strength

def place_slices_on_canvas(canvas: Image.Image, slices: List[Img_slice]) -> None:
    """
    Place each slice on the canvas at its original position. 
    
    Parameters:
    canvas (Image.Image): The canvas.
    slices (List[Img_slice]): The image slices.
    """
    print(f'Placing {len(slices)} slices on canvas')
    for slice_img, pos, inner_vert in slices:
        x, y = pos
        canvas.paste(slice_img, (int(x), int(y)), slice_img if slice_img.mode == 'RGBA' else None)
        
def replace_slices(slices: List[Img_slice], database_path: str, scale_factor: float, image_database_path: str) -> List[Img_slice]:
    """
    Replace each slice with a random image from the database.
    
    Parameters:
    slices (List[Img_slice]): The image slices.
    database_path (str): The path to the database.
    scale_factor (float): The scale factor.
    image_database_path (str): The path to the image database.
    
    Returns:
    List[Img_slice]: The image slices with replacements.
    """
    with open(database_path, 'r') as file:
        image_database = json.load(file)
    mosaic = []
    for slice_img, pos, inner_vert in slices:
        # Scale up the slice position
        scaled_pos = (pos[0] * scale_factor, pos[1] * scale_factor)

        # Scale up inner vertices
        scaled_inner_vert = [(x * scale_factor, y * scale_factor) for x, y in inner_vert]

        # Get average color of the slice
        avg_color = calculate_average_color(slice_img)
        closest_color = min(image_database.values(), key=lambda color: color_distance(color[:3], avg_color))  
              
        # Get image with similar color
        closest_images = [image_path for image_path, color in image_database.items() if color == closest_color]
        image_path = random.choice(closest_images)
        replacement_image = Image.open(str(image_database_path + image_path))
        
        # Define the bounding box for the replacement image and the scaling factor
        img_width, img_height = replacement_image.size
        tile_width, tile_height = calculate_bounding_box_dimensions(scaled_inner_vert)
        scale_w = tile_width / img_width
        scale_h = tile_height / img_height
        scale = max(scale_w, scale_h)

        # Resize, mask and append the image
        color_variance = image_database[image_path][3]
        color_dist = color_distance(image_database[image_path][:3], avg_color)
        blend_strength = adjust_blend_strength(color_variance, color_dist)
        
        new_size = (int(img_width * scale), int(img_height * scale))
        replacement_image = replacement_image.resize(new_size)
        replacement_image = overlay_blend(replacement_image, avg_color, blend_strength)
        cropped_replacement = get_masked_slice(replacement_image, scaled_inner_vert)
        mosaic.append((cropped_replacement, scaled_pos, scaled_inner_vert))
    return mosaic

def overlay_blend(image: Image.Image, target_color: Tuple[int, int, int], opacity: float =0.5) -> Image.Image:
    """
    Blend the image with the target color.
    
    Parameters:
    image (Image.Image): The image to blend.
    target_color (Tuple[int, int, int]): The target color.
    opacity (float): The opacity of the image.
    
    Returns:
    Image.Image: The blended image.
    """
    # Ensure opacity is within the correct range
    opacity = max(0, min(opacity, 1))

    # Create a solid color image
    color_image = Image.new("RGB", image.size, color=target_color)

    # Prepare for pixel-wise operation
    blended_image = Image.new("RGB", image.size)
    base_pixels = image.load()
    blend_pixels = color_image.load()
    result_pixels = blended_image.load()

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            base = base_pixels[x, y]
            blend = blend_pixels[x, y]

            new_pixel = []
            for i in range(3):  # For R, G, B channels
                if base[i] < 128:  # Darker than 50% gray
                    # Multiply mode
                    new_color = (2 * base[i] * blend[i]) / 255
                else:
                    # Screen mode
                    new_color = 255 - 2 * (255 - base[i]) * (255 - blend[i]) / 255
                
                # Apply opacity
                new_color = int(new_color * opacity + base[i] * (1 - opacity))
                new_pixel.append(new_color)

            result_pixels[x, y] = tuple(new_pixel)

    return blended_image

def get_masked_slice(image: Image.Image, vertices: List[Tuple[float, float]]) -> Image.Image:
    """
    Get the masked slice of the image.
    
    Parameters:
    image (Image.Image): The image to slice.
    vertices (List[Tuple[float, float]]): The vertices of the slice.
    
    Returns:
    Image.Image: The masked slice.
    """
    # Create a mask for the rhomboid shape
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    # Draw the polygon with white fill
    draw.polygon(vertices, outline=1, fill=255)
    # Crop the mask to the bounding box
    bounding_box = (min(int(v[0]) for v in vertices), min(int(v[1]) for v in vertices),
                    max(int(v[0]) for v in vertices), max(int(v[1]) for v in vertices))
    mask = mask.crop(bounding_box)
    # Crop the image slice to the bounding box
    slice_img = image.crop(bounding_box)
    # Apply the mask to the slice
    slice_img.putalpha(mask)
    return slice_img
