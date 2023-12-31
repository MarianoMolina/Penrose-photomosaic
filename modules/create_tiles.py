import math, cmath, os, time
from typing import List, Tuple
import matplotlib.pyplot as plt
from .utils import *

def create_tiles_and_scale(divisions: int, canvas_size: Tuple[int, int]) -> List[Rhombi]:
    """
    Create the tiles for the mosaic.
    
    Parameters:
    divisions (int): The number of divisions to make.
    canvas_size (Tuple[int, int]): The size of the original image.
    
    Returns:
    List[Rhombi]: The tiles for the mosaic.
    """
    rhombi = create_tiles(divisions)
    scaled_tiles = normalize_and_scale_tiles(rhombi, canvas_size)
    return scaled_tiles

def create_tiles(divisions: int, save_partial: bool = True) -> List[Rhombi]:
    if divisions < 15:
        base = 5
        phi = (5 ** 0.5 + 1) / 2
        triangles = create_initial_triangles(base)
        divided_triangles = divide_triangles(triangles, divisions, phi)
        if save_partial: draw_triangles(divided_triangles, "Divided Triangles")
        rhombi = pair_triangles_and_form_rhombi(divided_triangles)
        if save_partial: draw_rhombi(rhombi, "Formed Rhombi")
        return rhombi
    else:
        return False # AVOID CREATING RHOMBI VECTORS FOR DIVISIONS > 15

def create_initial_triangles(base: int) -> List[Triangle]:
    """
    Create the initial triangles for the mosaic.
    
    Parameters:
    base (int): The number of triangles to make.
    
    Returns:
    List[Triangle]: The initial triangles for the mosaic.
    """
    triangles = []
    for i in range(base * 2):
        v2 = cmath.rect(1, (2 * i - 1) * math.pi / (base * 2))
        v3 = cmath.rect(1, (2 * i + 1) * math.pi / (base * 2))
        if i % 2 == 0:
            v2, v3 = v3, v2
        triangles.append(("thin", 0, v2, v3))
    return triangles

def divide_triangles(triangles: List[Triangle], divisions: int, phi: float) -> List[Triangle]:
    """
    Divide the triangles for the mosaic.
    
    Parameters:
    triangles (List[Triangle]): The initial triangles for the mosaic.
    divisions (int): The number of divisions to make.
    phi (float): The golden ratio.
    
    Returns:
    List[Triangle]: The divided triangles for the mosaic.
    """
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
    """
    Pair the triangles and form rhombi.
    
    Parameters:
    triangles (List[Triangle]): The divided triangles for the mosaic.
    
    Returns:
    List[Rhombi]: The rhombi for the mosaic.
    """
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
    """
    Sort the vertices of a polygon based on their angle with respect to the centroid.
    
    Parameters:
    vertices (List[complex]): The vertices of the polygon.
    
    Returns:
    List[complex]: The sorted vertices.
    """
    # Calculate the centroid of the polygon
    centroid = sum(vertices) / len(vertices)

    # Sort vertices based on their angle with respect to the centroid
    def angle(vertex):
        rel_vector = vertex - centroid
        return cmath.phase(rel_vector)

    sorted_vertices = sorted(vertices, key=angle)
    return sorted_vertices

def normalize_and_scale_tiles(rhombi: List[Rhombi], canvas_size: Tuple[int, int]) -> List[Rhombi]:
    """
    Normalize and scale the rhombi.
    
    Parameters:
    rhombi (List[Rhombi]): The rhombi for the mosaic.
    canvas_size (Tuple[int, int]): The size of the original image.
    
    Returns:
    List[Rhombi]: The normalized and scaled rhombi.
    """
    scaled_tiles = []
    # Finding the maximum dimension to scale rhombi
    max_dimension = max(max(abs(v.real), abs(v.imag)) for rhombus in rhombi for v in rhombus) * 2
    scale = min(canvas_size) / max_dimension

    for rhombus in rhombi:
        scaled_rhombus = tuple(complex(v.real * scale + canvas_size[0] / 2, v.imag * scale + canvas_size[1] / 2) for v in rhombus)
        scaled_tiles.append(scaled_rhombus)

    return scaled_tiles

def draw_triangles(triangles: List[Triangle], title: str) -> None:
    """
    Draw the triangles.
    
    Parameters:
    triangles (List[Triangle]): The triangles for the mosaic.
    title (str): The title of the plot.
    """
    fig, ax = plt.subplots()
    for shape, v1, v2, v3 in triangles:
        x = [v1.real, v2.real, v3.real, v1.real]
        y = [v1.imag, v2.imag, v3.imag, v1.imag]
        ax.plot(x, y)

    ax.set_title(title)
    ax.set_aspect('equal')
    plt.savefig('photomosaic/output/triangles.png')
    
def draw_rhombi(rhombi: List[Rhombi], title: str) -> None:
    """
    Draw the rhombi.
    
    Parameters:
    rhombi (List[Rhombi]): The rhombi for the mosaic.
    title (str): The title of the plot.
    """
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
    
def find_join_side(v1: complex, v2: complex, v3: complex, shape: str) -> Tuple[complex, complex]:
    """
    Find the side to join the triangles.
    
    Parameters:
    v1 (complex): The first vertex of the triangle.
    v2 (complex): The second vertex of the triangle.
    v3 (complex): The third vertex of the triangle.
    shape (str): The shape of the triangle.
    
    Returns:
    Tuple[complex, complex]: The vertices of the side to join the triangles.
    """
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

def hash_edge(v1: complex, v2: complex) -> int:
    """
    Hash an edge.
    
    Parameters:
    v1 (complex): The first vertex of the edge.
    v2 (complex): The second vertex of the edge.
    
    Returns:
    int: The hash of the edge.
    """
    v1_tuple = complex_to_tuple(v1)
    v2_tuple = complex_to_tuple(v2)
    edge = tuple(sorted([v1_tuple, v2_tuple]))
    edge_hash = hash(edge)
    return edge_hash

def get_rhombi_by_division_and_scale(image_size: Tuple[int, int], config: dict, color: Tuple[int, int, int]=(255, 0, 0)) -> List[Rhombi]:
    """
    Get the tiles for the mosaic by division and scale them.
    
    Parameters:
    image (Image.Image): The original image.
    config (dict): The configuration settings.
    
    Returns:
    List[Rhombi]: The tiles for the mosaic.
    """
    config['timing']['getting_tiles'] = time.time()
    log_message(f'4- Creating tiles for {config["divisions"]} divisions in a {image_size} canvas', config)
    if config['divisions'] in config['available_vectors']:
        base_tiles = load_vector(f'rhombi_{config["divisions"]}')
        source = 'Loaded'
    else:
        base_tiles = create_tiles(config['divisions'], config['save_partial'])
        source = 'Created'
    if base_tiles and source:
        tiles = normalize_and_scale_tiles(base_tiles, image_size)
        canvas = create_canvas(image_size)
        draw_borders(canvas, tiles, color)
        canvas.save(os.path.join(config['output_path'], config['tile_canvas_name']), optimize=True)
        elapsed_time = round(time.time() - config["timing"]["getting_tiles"], 3)
        log_message(f'5- {source} {len(tiles)} Rhombi. Took {elapsed_time}s', config)
        return tiles
    else:
        raise Exception(f'Error: Cannot retrieve or create for {config["divisions"]} divisions.')

def create_and_save_rhombi_vectors_from_division(config: dict):
    division = config['divisions']
    print(f'Creating rhombi vectors for {division} divisions.')
    rhombi = create_tiles(division, False)
    print(f'Created {len(rhombi)} rhombi.')
    if save_vector(rhombi, f'rhombi_{division}', config):
        print(f'Saved rhombi_{division}.json')
    else:
        print(f'Failed to save rhombi_{division}.json')