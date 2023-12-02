from .utils import *
import json, os

def update_image_database(config: dict, max_size: Tuple[int, int]=(1024, 1024)) -> bool:
    """
    Update the image database if the source folder has been modified since the last update.
    
    Parameters:
    source_folder (str): The path to the source folder.
    database_path (str): The path to the database.
    image_folder (str): The path to the image folder.
    max_size (Tuple[int, int]): The maximum size of the images in the image folder.
    
    Returns:
    bool: True if the database was updated, False otherwise."""
    log_message('1- Updating image database...', config)
    config['timing']['update_image_database'] = time.time()
    source_folder = config['source_folder']
    database_path = config['database_path']
    image_folder = config['image_folder']
    if os.path.exists(database_path):
        with open(database_path, 'r') as file:
            image_database = json.load(file)
    else:
        image_database = {}
    source_images = set(os.listdir(source_folder))
    database_images = set(os.listdir(image_folder))

    # Remove entries from the json database if the corresponding image is no longer present
    for img_name in set(image_database.keys()) - source_images:
        del image_database[img_name]
            
    # Remove deleted images from the image database
    for image in database_images - source_images:
        os.remove(os.path.join(image_folder, image))
        
    # Add new images to the database
    for image in source_images - database_images:
        source_path = os.path.join(source_folder, image)
        database_image_path = os.path.join(image_folder, image)
        if image not in image_database:
            try:
                with Image.open(source_path) as img:
                    r, b, g = calculate_average_color(img)
                    color_var = calculate_color_variance(img)
                    image_database[image] = (r, b, g, color_var)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(database_image_path, optimize=True)
            except IOError:
                print(f"Error opening {image}. Skipping.")
        else:
            try:
                with Image.open(source_path) as img:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(database_image_path, optimize=True)
            except IOError:
                print(f"Error opening {image} already in json database. Skipping.")
    # Images that are in the source images but we haven't added to the json yet because they 
    # were already in the database -> this can happen if you modify the database json at some 
    # point or something went wrong during this process before
    for image in source_images - set(image_database.keys()):
        source_path = os.path.join(source_folder, image)
        try:
            with Image.open(source_path) as img:
                r, b, g = calculate_average_color(img)
                color_var = calculate_color_variance(img)
                image_database[image] = (r, b, g, color_var)
        except IOError:
            print(f"Error opening {image} already in image folder database. Skipping.")
    # Save the updated database
    with open(database_path, 'w') as file:
        json.dump(image_database, file)
    log_message(f'2- Image database updated. Took {time.time() - config["timing"]["update_image_database"]}', config)
    return True
