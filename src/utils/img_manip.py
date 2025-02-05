import os
import random

import numpy as np
import pandas as pd
from PIL import Image
import networkx as nx
from collections import defaultdict
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


def read_coordinates(file_path):
    """
    Reads a text file line by line, extracting coordinate pairs from each line.

    Each line in the file should contain a sequence of integers followed by two words (e.g., "wall 1").
    The function ignores the last two words and converts the preceding integers into (x, y) coordinate pairs.

    Args:
        file_path (str): The path to the text file containing the coordinate data.

    Returns:
        list[list[tuple[int, int]]]: A list of coordinate lists, where each list represents a line in the file.
    """
    coordinates_list = []

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()[:-2]  # Remove the last two words
            coordinates = [(int(parts[i]), int(parts[i + 1])) for i in range(0, len(parts), 2)]
            coordinates_list.append(coordinates)

    return coordinates_list


def build_graph(polygon):
    """
    Create a graph where nodes are junctions and edges represent wall segments.
    For each polygon, consecutive vertices (and the last with the first) are connected.
    """
    graph = nx.Graph()
    for pt in polygon:
        graph.add_node(pt)
    # Connect consecutive points and close the polygon.
    num_points = len(polygon)
    for i in range(num_points):
        graph.add_edge(polygon[i], polygon[(i + 1) % num_points])
    return graph


def compute_cardinal_neighbors(graph):
    """
    For every node in the graph, compute its four cardinal neighbors (top, left, bottom, right)
    based on the positions of all nodes in G. If no neighbor exists in a direction, (-1, -1) is used.
    """
    neighbors_dict = {}
    nodes = list(graph.nodes)
    for pt in nodes:
        x, y = pt
        top = (-1, -1)
        left = (-1, -1)
        bottom = (-1, -1)
        right = (-1, -1)

        # Top: same x, with y less than current; choose the one closest (largest y)
        candidates_top = [other for other in nodes if other[0] == x and other[1] < y]
        if candidates_top:
            top = max(candidates_top, key=lambda p: p[1])

        # Bottom: same x, with y greater than current; choose the one closest (smallest y)
        candidates_bottom = [other for other in nodes if other[0] == x and other[1] > y]
        if candidates_bottom:
            bottom = min(candidates_bottom, key=lambda p: p[1])

        # Left: same y, with x less than current; choose the one closest (largest x)
        candidates_left = [other for other in nodes if other[1] == y and other[0] < x]
        if candidates_left:
            left = max(candidates_left, key=lambda p: p[0])

        # Right: same y, with x greater than current; choose the one closest (smallest x)
        candidates_right = [other for other in nodes if other[1] == y and other[0] > x]
        if candidates_right:
            right = min(candidates_right, key=lambda p: p[0])

        neighbors_dict[pt] = [top, left, bottom, right]
    return neighbors_dict

def build_quatree_from_graph(graph, root):
    """
    Starting from 'root', use BFS (via single_source_shortest_path_length) to group nodes by level.
    Returns a dictionary mapping level -> list of nodes.
    """
    lengths = nx.single_source_shortest_path_length(graph, root)
    quatree = defaultdict(list)
    for node, level in lengths.items():
        quatree[level].append(node)
    return dict(quatree)

def find_edge_code(raw_annot_path: str, immg_path: str) -> pd.DataFrame:
    coordinate_list = read_coordinates(file_path=raw_annot_path)
    for coord in coordinate_list:
        graph = build_graph(polygon=coord)
        neighbor_dict = compute_cardinal_neighbors(graph=graph)
        root = min(graph.nodes)
        neighbor_dict['quadtree'] = [build_quatree_from_graph(graph=graph, root=root)]
        data_array = np.array(neighbor_dict)
        file_path = os.path.join(immg_path)
        np.save(file_path, data_array)
        breakpoint()


    # neighbors_dict = compute_cardinal_neighbors(graph=graph)
    # root = min(graph.nodes)
    # quadtree = build_quatree_from_graph(graph=graph, root=root)
    breakpoint()






    # Mapping dictionaries.
    edges = {
        0: '0000', 1: '0001', 2: '0010', 3: '0011', 4: '0100', 5: '0110', 6: '0111',
        7: '1000', 8: '1001', 9: '1011', 10: '1100', 11: '1101', 12: '1110', 13: '1111',
        14: '0101', 15: '1010'
    }
    edges_rev = {v: k for k, v in edges.items()}

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
        n = len(vertices)
        for i in range(n):
            graph.add_edge(vertices[i], vertices[(i + 1) % n])

    def find_directional_neighbor(point, neighbors, direction):
        """
        Given a point and its neighbors, return the closest neighbor
        in the specified cardinal direction or (-1, -1) if none exists.
        Direction is one of: 'up', 'left', 'down', 'right'.
        """
        x, y = point
        candidate = None

        if direction == 'up':
            # Neighbors directly above: same x, greater y.
            valid = [n for n in neighbors if n[0] == x and n[1] > y]
            if valid:
                candidate = min(valid, key=lambda n: n[1] - y)
        elif direction == 'down':
            # Neighbors directly below: same x, smaller y.
            valid = [n for n in neighbors if n[0] == x and n[1] < y]
            if valid:
                candidate = max(valid, key=lambda n: n[1])  # closest from below
        elif direction == 'left':
            # Neighbors to the left: same y, smaller x.
            valid = [n for n in neighbors if n[1] == y and n[0] < x]
            if valid:
                candidate = max(valid, key=lambda n: n[0])  # closest from left
        elif direction == 'right':
            # Neighbors to the right: same y, greater x.
            valid = [n for n in neighbors if n[1] == y and n[0] > x]
            if valid:
                candidate = min(valid, key=lambda n: n[0] - x)

        return candidate if candidate is not None else (-1, -1)

    data = []
    for node in graph.nodes():
        neighbors = list(graph.neighbors(node))
        # For each cardinal direction, pick the closest neighbor (or (-1,-1) if none).
        up = find_directional_neighbor(node, neighbors, 'up')
        left = find_directional_neighbor(node, neighbors, 'left')
        down = find_directional_neighbor(node, neighbors, 'down')
        right = find_directional_neighbor(node, neighbors, 'right')

        # Build the binary edge_class based on whether a neighbor exists in each direction.
        # Order: up, left, down, right.
        edge_class = ('1' if up != (-1, -1) else '0') + \
                    ('1' if left != (-1, -1) else '0') + \
                    ('1' if down != (-1, -1) else '0') + \
                    ('1' if right != (-1, -1) else '0')

        # Lookup the corresponding numeric edge_code.
        edge_code = edges_rev.get(edge_class, None)

        data.append({
            'point': node,
            'edge_class': edge_class,
            'edge_code': edge_code,
            'adjacent_nodes': [up, left, down, right]
        })
    breakpoint()

    # Create a dictionary to store the adjacency list in the desired format
    adjacency_dict = {}

    for node in graph.nodes():
        neighbors = list(graph.neighbors(node))
        adjacency_dict[node] = neighbors

    # Process the adjacency list into the desired format
    processed_adj_dict = {}
    for node, neighbors in adjacency_dict.items():
        processed_adj_dict[node] = [(n, n) if n == (-1, -1) else n for n in neighbors]  # Adjust -1, -1 if needed

    breakpoint()

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