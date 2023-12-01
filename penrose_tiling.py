import math, cmath, os, json, random
from PIL import Image, ImageDraw
from typing import List, Tuple, Union
import matplotlib.pyplot as plt

Triangle = Tuple[str, complex, complex, complex] # shape, v1, v2, v3
Rhombi = Tuple[complex, complex, complex, complex] # 4 vertices
Img_slice = Tuple[Image.Image, Tuple[float, float], List[Tuple[float, float]]] # Image, top-left position, relative vertices

# UTILS
def get_image_size(image_path: str) -> Tuple[int, int]:
    with Image.open(image_path) as img:
        return img.size  # Returns a tuple (width, height)

def draw_triangles(triangles: List[Triangle], title: str) -> None:
    fig, ax = plt.subplots()
    for shape, v1, v2, v3 in triangles:
        x = [v1.real, v2.real, v3.real, v1.real]
        y = [v1.imag, v2.imag, v3.imag, v1.imag]
        ax.plot(x, y)

    ax.set_title(title)
    ax.set_aspect('equal')
    plt.savefig('photomosaic/output/triangles.png')
    
def draw_rhombi(rhombi: List[Rhombi], title: str) -> None:
    fig, ax = plt.subplots()
    for rhombus in rhombi:
        if not len(rhombus) == 4:
            print(f'Drawing Error: Incorrect vertices count for a rhombus: {len(rhombus)}')
            # print("Rhombus: ", rhombus)
        else:
            v1, v2, v3, v4  = rhombus
            x = [v1.real, v2.real, v3.real, v4.real, v1.real]
            y = [v1.imag, v2.imag, v3.imag, v4.imag, v1.imag]
            ax.plot(x, y)

    ax.set_title(title)
    ax.set_aspect('equal')
    plt.savefig('photomosaic/output/rhombi.png')
    
# CREATE TILES
def create_tiles(divisions: int, canvas_size: Tuple[int, int]) -> List[Rhombi]:
    base = 5
    phi = (5 ** 0.5 + 1) / 2
    triangles = create_initial_triangles(base)
    divided_triangles = divide_triangles(triangles, divisions, phi)
    draw_triangles(divided_triangles, "Divided Triangles")
    rhombi = pair_triangles_and_form_rhombi(divided_triangles)
    draw_rhombi(rhombi, "Formed Rhombi")
    scaled_tiles = normalize_and_scale_tiles(rhombi, canvas_size)
    return scaled_tiles

def create_initial_triangles(base: int) -> List[Triangle]:
    triangles = []
    for i in range(base * 2):
        v2 = cmath.rect(1, (2 * i - 1) * math.pi / (base * 2))
        v3 = cmath.rect(1, (2 * i + 1) * math.pi / (base * 2))
        if i % 2 == 0:
            v2, v3 = v3, v2
        triangles.append(("thin", 0, v2, v3))
    return triangles

def divide_triangles(triangles: List[Triangle], divisions: int, phi: float) -> List[Triangle]:
    for _ in range(divisions):
        new_triangles = []
        for shape, v1, v2, v3 in triangles:
            if shape == "thin":
                p1 = v1 + (v2 - v1) / phi
                new_triangles += [("thin", v3, p1, v2), ("thick", p1, v3, v1)]
            else:
                p2 = v2 + (v1 - v2) / phi
                p3 = v2 + (v3 - v2) / phi
                new_triangles += [("thick", p3, v3, v1), ("thick", p2, p3, v2), ("thin", p3, p2, v1)]
        triangles = new_triangles
    return triangles

def pair_triangles_and_form_rhombi(triangles: List[Triangle]) -> List[Rhombi]:
    triangle_halves = {}
    rhombi = []
    for shape, v1, v2, v3 in triangles:
        v1_rounded, v2_rounded, v3_rounded = round_complex(v1, 6), round_complex(v2, 6), round_complex(v3, 6)
        long_side = find_join_side(v1_rounded, v2_rounded, v3_rounded, shape)
        hashed_edge = hash_edge(*long_side)

        if hashed_edge in triangle_halves:
            matching_triangle = [round_complex(v, 6) for v in triangle_halves[hashed_edge]]
            shared_vertices = set(long_side)
            unique_vertices = set([v1_rounded, v2_rounded, v3_rounded]) - shared_vertices

            matching_unique = set(matching_triangle) - shared_vertices
            rhombus_vertices = list(unique_vertices) + list(matching_unique) + list(shared_vertices)
            if len(shared_vertices) > 2:
                print(f'Error: Matching edge has more than 2 vertices: {shared_vertices}')
            if len(matching_triangle) > 3:
                print(f'Error: Matching triangle has more than 3 vertices: {matching_triangle}')
            if len(rhombus_vertices) == 4:
                sorted_rhombus = sort_vertices(rhombus_vertices)
                rhombi.append(tuple(sorted_rhombus))
            else:
                print(f"Error: Incorrect vertices count for a rhombus:, {len(rhombus_vertices)}")
            del triangle_halves[hashed_edge]
        else:
            triangle_halves[hashed_edge] = [v1, v2, v3]
    return rhombi

def sort_vertices(vertices: List[complex]) -> List[complex]:
    # Calculate the centroid of the polygon
    centroid = sum(vertices) / len(vertices)

    # Sort vertices based on their angle with respect to the centroid
    def angle(vertex):
        rel_vector = vertex - centroid
        return cmath.phase(rel_vector)

    sorted_vertices = sorted(vertices, key=angle)
    return sorted_vertices

def normalize_and_scale_tiles(rhombi: List[Rhombi], canvas_size: Tuple[int, int]) -> List[Rhombi]:
    scaled_tiles = []
    # Finding the maximum dimension to scale rhombi
    max_dimension = max(max(abs(v.real), abs(v.imag)) for rhombus in rhombi for v in rhombus) * 2
    scale = min(canvas_size) / max_dimension

    for rhombus in rhombi:
        scaled_rhombus = tuple(complex(v.real * scale + canvas_size[0] / 2, v.imag * scale + canvas_size[1] / 2) for v in rhombus)
        scaled_tiles.append(scaled_rhombus)

    return scaled_tiles

# CREATE TILES UITLS
def find_join_side(v1: complex, v2: complex, v3: complex, shape: str) -> Tuple[complex, complex]:
    distances = {
        (v1, v2): distance_complex(v1, v2),
        (v2, v3): distance_complex(v2, v3),
        (v1, v3): distance_complex(v1, v3)
    }
    # For 'thin' triangles, find the shortest side, for 'thick' triangles, find the longest side
    if shape == "thin":
        join_side = min(distances, key=distances.get)
    else:  # 'thick'
        join_side = max(distances, key=distances.get)
    
    return join_side

def distance_complex(v1: complex, v2: complex) -> float:
    return abs(v2 - v1)

def hash_edge(v1: complex, v2: complex) -> int:
    v1_tuple = complex_to_tuple(v1)
    v2_tuple = complex_to_tuple(v2)
    edge = tuple(sorted([v1_tuple, v2_tuple]))
    edge_hash = hash(edge)
    return edge_hash

def complex_to_tuple(z: complex, precision: int = 5) -> Tuple[float, float]:
    return (round(z.real, precision), round(z.imag, precision))

def round_complex(z: complex, precision: int = 5) -> complex:
    return complex(round(z.real, precision), round(z.imag, precision))

## SLICE IMAGE
def slice_image(image_path: str, tiles: List[Rhombi]) -> List[Img_slice]:
    image = Image.open(image_path)
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

def get_masked_slice(image: Image.Image, vertices: List[Tuple[float, float]]) -> Image.Image:
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

def create_canvas(size: Tuple[int, int]) -> Image.Image:
    """ Create a blank canvas. """
    return Image.new('RGBA', size, (255, 255, 255, 0))

def place_slices_on_canvas(canvas: Image.Image, slices: List[Img_slice]) -> None:
    """ Place each slice on the canvas at its original position. """
    print(f'Placing {len(slices)} slices on canvas')
    for slice_img, pos, inner_vert in slices:
        x, y = pos
        canvas.paste(slice_img, (int(x), int(y)), slice_img if slice_img.mode == 'RGBA' else None)
            
def draw_borders(canvas: Image.Image, tiles: List[Rhombi], color:Tuple[int,int,int]=(0, 255, 0), thickness: int = 1) -> None:
    """ Draw borders between tiles. """
    draw = ImageDraw.Draw(canvas)
    for tile in tiles:
        vertices = [(tile[i].real, tile[i].imag) for i in range(0, len(tile))]
        draw.polygon(vertices, outline=color, width=thickness)
        
def calculate_average_color(image_slice: Image.Image) -> Tuple[int, int, int]:
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

    return int(avg_r), int(avg_g), int(avg_b)

def update_image_database(database_path: str, image_folder: str) -> None:
    # Load existing database if it exists
    if os.path.exists(database_path):
        with open(database_path, 'r') as file:
            image_database = json.load(file)
    else:
        image_database = {}

    # Get a set of current image filenames in the folder
    current_images = set(os.listdir(image_folder))

    # Remove entries from the database if the corresponding image is no longer present
    for img_name in list(image_database.keys()):
        if img_name not in current_images:
            del image_database[img_name]

    # Update the database with new images
    for img_name in current_images:
        if img_name not in image_database:
            image_path = os.path.join(image_folder, img_name)
            try:
                with Image.open(image_path) as img:
                    avg_color = calculate_average_color(img)
                    image_database[img_name] = avg_color
            except IOError:
                print(f"Error opening {img_name}. Skipping.")

    # Save the updated database
    with open(database_path, 'w') as file:
        json.dump(image_database, file)

    print("Image database updated.")
        
def replace_slices(slices: List[Img_slice], database_path: str, scale_factor: float) -> List[Img_slice]:
    """ Replace each slice with a random image from the database. """
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
        closest_color = min(image_database.values(), key=lambda color: color_distance(color, avg_color))
        
        # Get image with similar color
        closest_images = [image_path for image_path, color in image_database.items() if color == closest_color]
        image_path = random.choice(closest_images)
        replacement_image = Image.open(str('photomosaic/image_database/' + image_path))
        
        # Define the bounding box for the replacement image and the scaling factor
        img_width, img_height = replacement_image.size
        tile_width, tile_height = calculate_bounding_box_dimensions(scaled_inner_vert)
        scale_w = tile_width / img_width
        scale_h = tile_height / img_height
        scale = max(scale_w, scale_h)

        # Resize, mask and append the image
        new_size = (int(img_width * scale), int(img_height * scale))
        replacement_image = replacement_image.resize(new_size)
        cropped_replacement = get_masked_slice(replacement_image, scaled_inner_vert)
        mosaic.append((cropped_replacement, scaled_pos, scaled_inner_vert))
    return mosaic
     
def calculate_bounding_box_dimensions(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
    """ Calculate the width and height of the bounding box for given vertices. """
    min_x = min(x for x, _ in vertices)
    max_x = max(x for x, _ in vertices)
    min_y = min(y for _, y in vertices)
    max_y = max(y for _, y in vertices)
    return max_x - min_x, max_y - min_y

def color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """ Calculate the distance between two colors. """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5