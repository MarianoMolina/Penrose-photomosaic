import gradio as gr
from modules.utils import *
from modules.database_visualize import *
import matplotlib.pyplot as plt
from modules.replace_slices import place_slices_on_canvas, replace_slices, slice_image
from modules.create_tiles import normalize_and_scale_tiles, de_serialize_vector_complex

def plot_pattern(pattern_type):
    pattern = load_vector_file(pattern_type)
    ## Return a matplotlib figure
    fig = plt.figure()
    scale_factor = 100
    for vector in pattern:
        vector = vector
        x, y = zip(*vector)
        # scale
        x = tuple(i * scale_factor for i in x)
        y = tuple(i * scale_factor for i in y)
        # Closing the shape by appending the first point at the end
        x += (x[0],)
        y += (y[0],)

        # Plotting the shape
        plt.plot(x, y)

    # Setting plot limits
    lim = (scale_factor * 1)+0.1
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # Adding grid, title and labels
    plt.grid(True)
    plt.title(f'Pattern {pattern_type}')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    return fig
    
def get_pattern_plot(pattern: str) -> gr.Plot:
    return gr.Plot(plot_pattern(pattern), label="Pattern selected", show_label=True)
    
def update_color_analysis(photo_database_colors: gr.State, target_image_colors: gr.State) -> gr.Plot:
    if isinstance(photo_database_colors, gr.State):
        photo_database_colors = photo_database_colors.value
    if isinstance(target_image_colors, gr.State):
        target_image_colors = target_image_colors.value
    if photo_database_colors and target_image_colors:
        fig = get_visualization_graph(target_image_colors, photo_database_colors)
        return gr.Plot(fig, label="Color analysis", show_label=True)
    gr.Info('Please make sure you have uploaded an image and a photo database. If you just updated the photo database, please click again.')
    return gr.Plot(label="Color analysis", show_label=True)

def update_photo_database(photo_database_upload: gr.File, photo_database_json: dict) -> gr.State:
    if isinstance(photo_database_json, gr.State):
        photo_database_json = photo_database_json.value
    if isinstance(photo_database_upload, gr.File):
        photo_database_upload = photo_database_upload.value
    image_folder = "photomosaic/images_temp"
    current_photo_set_filenames = [os.path.basename(img_file_path) for img_file_path in photo_database_upload] if photo_database_upload else []
    images_already_in_database = set(os.listdir(image_folder))
    photo_database = photo_database_json if photo_database_json else {}
    
    # Image not in the current set but in the database so it is removed
    for image in images_already_in_database - set(current_photo_set_filenames):
        os.remove(os.path.join(image_folder, image))
    
    # Image in the photo dict but not in the current set so it is removed
    for image in set(photo_database.keys()) - set(current_photo_set_filenames):
        del photo_database[image]
        
    ## TODO: Check if file type is wrong and remove it / tell the user
    for img_file_path in photo_database_upload:
        filename = os.path.basename(img_file_path)
        if filename not in photo_database.keys() and filename not in images_already_in_database:
            database_image_path = os.path.join(image_folder, filename)
            with Image.open(img_file_path) as img:
                img.thumbnail((1024,1024), Image.Resampling.LANCZOS)
                photo_database[filename] = get_color_profile_of_image(img)
                img.save(database_image_path, optimize=True)
    
    return gr.State(photo_database)

def update_target_photo_map(target_image_upload: Image.Image) -> gr.Dropdown:
    rgb_image = target_image_upload.convert('RGB')
    target_image_colors = divide_image_into_chunks_and_get_color(rgb_image)
    return gr.State(target_image_colors)

def get_color_profile_of_image(image: Image.Image) -> Tuple:
    r, b, g = calculate_average_color(image)
    color_var = calculate_color_variance(image)
    return (r, b, g, color_var)

def call_create_mosaic(target_image: Image.Image, pattern_dropdown: gr.Dropdown, photo_database: gr.State, scale_chosen: int):
    print('Creating mosaic')
    if isinstance(pattern_dropdown, gr.Dropdown):
        pattern_dropdown = pattern_dropdown.value
    if isinstance(photo_database, gr.State):
        photo_database = photo_database.value
    image_folder = "photomosaic/images_temp"
    tiles = de_serialize_vector_complex(load_vector_file(pattern_dropdown))
    tiles = normalize_and_scale_tiles(tiles, target_image.size)
    slices = slice_image(target_image, tiles)
    mosaic_tiles, color_mosaic_tiles = replace_slices(slices, photo_database, scale_chosen, image_folder)
    
    print('Placing slices on canvas')
    new_canvas = create_canvas((target_image.size[0]*scale_chosen, target_image.size[1]*scale_chosen))
    place_slices_on_canvas(new_canvas, color_mosaic_tiles)
    color_image = gr.Image(new_canvas, label="Color Mosaic", show_label=True, show_download_button=True)
    
    photo_canvas = create_canvas((target_image.size[0]*scale_chosen, target_image.size[1]*scale_chosen))
    place_slices_on_canvas(photo_canvas, mosaic_tiles)  
    photo_image = gr.Image(photo_canvas, label="Photo Mosaic", show_label=True, show_download_button=True)
    print('Mosaic created')
    return photo_image, color_image

pm_theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="emerald",
)
list_vectors = list_files_in_folder("photomosaic/vectors")

with gr.Blocks(theme=pm_theme, title="Photomosaic generator") as mosaic_interface:
    photo_database_json = gr.State({})
    target_image_colors = gr.State([])
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
                        ## 1- Upload your image
                        This image will be converted into a mosaic
                        """)
        with gr.Column(scale=3):
            target_image_upload = gr.Image(label="Image to convert", type="pil", show_label=True, interactive=True)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
                        ## 2- Number of divisions
                        Select the number of divisions to use in your pattern. The pattern is created by creating a set of 'initial triangles', which can be divided into smaller triangles any number of times. 
                        For reference: 9 divisions creates 20800 tiles. 10 creates 54560. 
                        """)
        with gr.Column(scale=3):
            with gr.Group():
                pattern_dropdown = gr.Dropdown(label="Select pattern", value=list_vectors[0], choices=list_vectors)
                pattern_selected = get_pattern_plot(pattern_dropdown.value)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
                        ## 3- Upload images 
                        - These images, if provided, will be used to create the photomosaic.
                        - If no images are uploaded, only the color mosaic will be generated.
                        - Accepted formats are JPEG, JPG and PNG. 
                        """)
        with gr.Column(scale=3):
            photo_database_upload = gr.File(label="Photo Database", file_count='multiple', container=True, visible=True, file_types=["png", "jpg", "jpeg"], show_label=True, interactive=True)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
                        ## 4- Color field
                        Click to analyse the color field of your target and database images
                        """)
        with gr.Column(scale=3):
            with gr.Group():
                show_color_analysis = gr.Button(value="Analyze color field", variant="primary")
                color_analysis = gr.Plot(label="Color analysis", show_label=True)
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("""
                        ## 5- Color blend
                        Select color blending strength and opacity
                        (This is currently not being used since it slows down the process)
                        """)
        with gr.Column(scale=3):
            color_matching_slider = gr.Slider(label="Color Matching Strength", minimum=0, maximum=1, step=0.1, value=0.5, interactive=True)
        with gr.Column(scale=3):
            overlay_blend_slider = gr.Slider(label="Overlay Blend Opacity", minimum=0, maximum=1, step=0.1, value=0.5, interactive=True)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
                        ## 6- Scaling
                        Select how much to scale your initial image
                        """)
        with gr.Column(scale=3):
            scale_chosen = gr.Slider(label="Scale", minimum=1, maximum=40, step=1, value=20, interactive=True)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
                        ## 7- Generate
                        Click to generate your mosaic
                        """)
        with gr.Column(scale=3):
            create = gr.Button(value="Create Mosaic", variant="primary")
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("""
                        ## 8- Results
                        """)
        with gr.Column(scale=3):
            output_photo = gr.Image(label="Generated Mosaic", show_label=True)
        with gr.Column(scale=3):
            output_color = gr.Image(label="Generated Mosaic", show_label=True)
    target_image_upload.change(update_target_photo_map, target_image_upload, target_image_colors)
    pattern_dropdown.change(get_pattern_plot, pattern_dropdown, pattern_selected)
    photo_database_upload.change(update_photo_database, [photo_database_upload, photo_database_json], photo_database_json)
    show_color_analysis.click(update_color_analysis, [photo_database_json, target_image_colors], color_analysis)
    create.click(call_create_mosaic, [target_image_upload, pattern_dropdown, photo_database_json, scale_chosen], [output_photo, output_color])