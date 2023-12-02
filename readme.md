# Penrose Tiles Photomosaic Builder

This project creates a unique photomosaic using Penrose tiling. It takes a target image, an image database, and a specified number of divisions, then assembles a mosaic where each tile is a slice of an image from the database. The matching is based on color proximity, offering a visually appealing and non-repeating pattern of Penrose tiles.

## Features

- **Penrose Tiling**: Generates an aesthetically pleasing, non-repeating pattern.
- **Color Matching**: Uses color proximity to select the best matching image from the database for each tile.
- **Customizable**: Number of divisions and scaling factors can be adjusted.
- **Verbose Mode**: Provides detailed process logs.

## Requirements

- Python 3.x
- Pillow (PIL Fork)
- Matplotlib

## Setup

1. **Install Dependencies**:
    
    ```
    pip install pillow matplotlib 
    ```
    
2. **Configuration**: Set up your configuration file `config.json` with the following structure:
    
    ```
   { 
    "source_folder": "path/to/image_source/", "database_path": "path/to/image_database.json", "image_folder": "path/to/image_database/", "image_path": "path/to/target_image.jpg", "divisions": 3, "verbose": true, "output_path": "path/to/output/", "mosaic_name": "mosaic_output_name.png", "tile_canvas_name": "tile_canvas_output_name.png", "original_image_name": "original_image_output_name.png", "image_with_borders_name": "image_with_borders_output_name.png"
   }
    ```
    - `source_folder`: Directory where source images for the database are stored.
    - `database_path`: Path to the JSON file where the image database information is saved.
    - `image_folder`: Directory where processed images for the database are stored.
    - `image_path`: Path to the target image for the photomosaic.
    - `divisions`: Number of divisions for Penrose tiling.
    - `verbose`: Enable detailed logging.
    - `output_path`: Directory where output images are saved.
    - `mosaic_name`, `tile_canvas_name`, `original_image_name`, `image_with_borders_name`: Names for various output files.
1. **Image Database**: Populate the `source_folder` with images to be used in the mosaic.

## Usage

To run the photomosaic builder, execute:

```
python main.py
```

This script will process the images in your database, create Penrose tiles from your target image, and assemble them into a photomosaic.

## Outputs

The program generates the following outputs in the specified `output_path`:

- Original target image.
- Tiles visualization.
- Image with Penrose tiling borders.
- Final photomosaic.