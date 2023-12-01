from penrose_tiling import (
    create_tiles, slice_image, replace_slices, create_canvas, place_slices_on_canvas, draw_borders, update_image_database
)
from PIL import Image
import json

def main():
    print('Updating image database...')
    database_path = 'photomosaic/image_database.json'
    image_folder = 'photomosaic/image_database'
    update_image_database(database_path, image_folder)
    image_path = 'photomosaic/picture.jpg'
    divisions = 9
    scale_factor = 2 * (2.65 ** (divisions - 1))/(divisions*16)
    
    print(f'Loading image from {image_path}')
    original_image = Image.open(image_path)
    original_image.save('photomosaic/output/original_image.png')
    canvas_size = original_image.size
    print(f'Loaded image with size: {canvas_size}')

    # Step 2: Create tiles, draw them on an empty canvas, and display the canvas
    print(f'Creating tiles for {divisions} divisions in a {canvas_size} canvas')
    tiles = create_tiles(divisions, canvas_size)
    tile_canvas = create_canvas(canvas_size)
    draw_borders(tile_canvas, tiles, color=(255, 0, 0), thickness=1)
    print(f'Created {len(tiles)} Rhombi')
    tile_canvas.save('photomosaic/output/tile_canvas.png')

    # Step 3: Slice the image and place the slices on a canvas
    print(f'Slicing image {image_path} into {len(tiles)} slices')
    slices = slice_image(image_path, tiles)
    canvas = create_canvas(canvas_size)
    print(f'Created {len(slices)} slices. Placing on canvas...')
    place_slices_on_canvas(canvas, slices)
    draw_borders(canvas, tiles)
    canvas.save('photomosaic/output/image_with_borders.png')
    print(f'Replacing slices with images from database...')
    mosaic = replace_slices(slices, database_path, scale_factor)
    scaled_canvas_size = (int(canvas_size[0] * scale_factor), int(canvas_size[1] * scale_factor))
    new_canvas = create_canvas(scaled_canvas_size)
    place_slices_on_canvas(new_canvas, mosaic)
    new_canvas.save('photomosaic/output/mosaic.png', optimize=True)
    print(f'Done')
    
# def main():
#     config = load_config()
#     update_image_database(config)
#     original_image = load_image(config['image_path'])
#     tiles = create_and_draw_tiles(original_image, config)
#     slices = slice_and_place_images(original_image, tiles, config)
#     mosaic = create_mosaic(slices, config)
#     save_mosaic(mosaic, config)

# def load_config(config_file='config.json'):
#     with open(config_file, 'r') as file:
#         config = json.load(file)
#     return config

# def load_image(image_path):
#     return Image.open(image_path)

# def create_and_draw_tiles(image, config):
#     # Implement the logic to create and draw tiles
#     tiles = create_tiles(config['divisions'], image.size)
#     canvas = create_canvas(image.size)
#     draw_borders(canvas, tiles, color=(255, 0, 0), thickness=1)
#     return tiles, canvas

# def slice_and_place_images(image, tiles, config):
#     slices = slice_image(image, tiles)
#     canvas = create_canvas(image.size)
#     place_slices_on_canvas(canvas, slices)
#     return canvas

# def create_mosaic(slices, config):
#     mosaic = replace_slices(slices, config['database_path'], config['scale_factor'])
#     scaled_canvas_size = (int(config['canvas_size'][0] * config['scale_factor']),
#                           int(config['canvas_size'][1] * config['scale_factor']))
#     new_canvas = create_canvas(scaled_canvas_size)
#     place_slices_on_canvas(new_canvas, mosaic)
#     return new_canvas

# def save_mosaic(mosaic, config):
#     mosaic.save(config['output_path'])
    
if __name__ == '__main__':
    main()