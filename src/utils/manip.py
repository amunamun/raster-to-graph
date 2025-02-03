import os
import random
import pandas as pd
from PIL import Image
import networkx as nx
from typing import List, Tuple, Dict


def add_wall_to_graph(graph: nx.Graph, vertices: List[Tuple[float, float]]) -> None:
    """
    Adds a closed-loop (wall) to the graph by connecting each vertex to the next and closing the loop.

    This function leverages NetworkX's behavior where add_edge automatically adds nodes if missing.

    Args:
        graph (nx.Graph): The graph where the wall will be added.
        vertices (List[Tuple[float, float]]): A list of (x, y) coordinates representing the wall's vertices.
    """
    n = len(vertices)
    for i in range(n):
        # Connect the current vertex to the next; the modulo ensures the last vertex connects back to the first.
        graph.add_edge(vertices[i], vertices[(i + 1) % n])


def find_edge_code(raw_annot_path: str) -> pd.DataFrame:
    """
    Processes an annotation file to build a graph of walls and computes the edge code (node degree)
    for each vertex.

    The function performs the following steps:
      1. Reads a whitespace-delimited annotation file.
      2. Removes the extraneous (last) column.
      3. Dynamically assigns column names for coordinate pairs.
      4. Constructs a graph by connecting vertices into a closed loop for each row.
      5. Returns a DataFrame with nodes and their corresponding degree (edge code).

    Args:
        raw_annot_path (str): The file path to the raw annotation file.

    Returns:
        pd.DataFrame: A DataFrame with columns 'node' and 'edge_code' representing each vertex
                      and its degree in the constructed graph.
    """
    # Read the raw annotation file using whitespace as the delimiter.
    df = pd.read_csv(raw_annot_path, sep=r'\s+', header=None)

    # Remove the last two column (adjust if more columns need to be removed).
    df = df.iloc[:, :-2]

    # Determine the number of coordinate pairs and assign dynamic column names.
    num_points = df.shape[1] // 2
    columns = [f"x{i // 2 + 1}" if i % 2 == 0 else f"y{i // 2 + 1}" for i in range(df.shape[1])]
    df.columns = columns

    graph = nx.Graph()

    # Iterate over each row
    for row in df.itertuples(index=False):
        vertices = [(getattr(row, f"x{i + 1}"), getattr(row, f"y{i + 1}")) for i in range(num_points)]
        add_wall_to_graph(graph, vertices)

    # Create a DataFrame that maps each node to its degree (edge code).
    result_df = pd.DataFrame({
        'point': list(graph.nodes()),
        'edge_code': [graph.degree[node] for node in graph.nodes()],
    })

    return result_df


def process_image(raw_img_path: str,
                  output_folder: str,
                  new_resolution: Tuple[int, int]) -> Tuple[
    str, float, float, int, int]:
    """
    Processes an image by resizing it, centering it on a canvas of target resolution,
    and saving the processed image.

    Args:
        raw_img_path (str): Path to the raw input image.
        output_folder (str): Folder where the processed image will be saved.
        new_resolution (Tuple[int, int]): Target (width, height) for the processed image.

    Returns:
        Tuple[str, float, float, int, int]:
            - new_img_path (str): Path to the saved image.
            - scale_x (float): Scaling factor in the x-direction.
            - scale_y (float): Scaling factor in the y-direction.
            - left_padding (int): Horizontal padding applied.
            - top_padding (int): Vertical padding applied.
    """
    new_width, new_height = new_resolution
    new_img_path = os.path.join(output_folder, os.path.basename(raw_img_path))

    with Image.open(raw_img_path) as img:
        original_width, original_height = img.size
        scale_x = new_width / original_width
        scale_y = new_height / original_height

        # Resize image while maintaining aspect ratio
        img.thumbnail(new_resolution)

        # Create a blank white canvas and calculate padding to center the image
        canvas = Image.new("RGB", new_resolution, (255, 255, 255))
        left_padding = (new_width - img.width) // 2
        top_padding = (new_height - img.height) // 2
        canvas.paste(img, (left_padding, top_padding))

        # Save the processed image
        canvas.save(new_img_path)

    return new_img_path, scale_x, scale_y, left_padding, top_padding


def process_annotations(raw_annot_path: str,
                        scale_x: float,
                        scale_y: float,
                        left_padding: int,
                        top_padding: int,
                        image_id: str,
                        category_id: int,
                        start_annot_id: int) -> Tuple[List[Dict], int]:
    """
    Processes the annotation file to scale coordinates and assign semantic labels.

    The function:
      - Reads the annotation file to build a graph of wall points.
      - Scales the coordinates based on provided scale factors and padding.
      - Assigns a random semantic label to each annotation.

    Args:
        raw_annot_path (str): Path to the raw annotation file.
        scale_x (float): Scaling factor in the x-direction.
        scale_y (float): Scaling factor in the y-direction.
        left_padding (int): Horizontal padding applied to the image.
        top_padding (int): Vertical padding applied to the image.
        image_id (str): Unique identifier for the processed image.
        category_id (int): Category ID to be assigned to each annotation.
        start_annot_id (int): Starting annotation ID counter.

    Returns:
        Tuple[List[Dict], int]:
            - List of annotation dictionaries.
            - Updated annotation ID counter.
    """
    annotations = []
    annot_id = start_annot_id
    # Expecting annotation_data_df to have columns "node" and "edge_code"
    annotation_data_df = find_edge_code(raw_annot_path)

    # Iterate over each annotation (node) in the DataFrame.
    for _, row in annotation_data_df.iterrows():
        # Use "node" column which is expected to be a tuple (x, y)
        x, y = row["point"]
        new_x = int(x * scale_x) + left_padding
        new_y = int(y * scale_y) + top_padding
        semantics = random.choices(
            ['outside', 'kitchen', 'bathroom', 'bedroom', 'closet', 'corridor', 'restroom', 'balcony'],
            k=4
        )
        annot_id += 1
        annotations.append({
            "image_id": image_id,
            "category_id": category_id,
            "id": annot_id,
            "point": [new_x, new_y],
            "edge_code": row["edge_code"],
            "semantic": semantics
        })

    return annotations, annot_id