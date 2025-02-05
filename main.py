import os
from typing import Tuple, Dict
from loguru import logger
from collections import deque
import numpy as np
from src.config.settings import EnvSettings
from src.utils.local import list_matched_files, reset_directory
from src.utils.manip import process_image
from src.utils.geometry import GeometryProcessor

def init_neighbors():
    return [(-1, -1), (-1, -1), (-1, -1), (-1, -1)]

# Function to get direction
def get_direction(origin, point):
    dx = point[0] - origin[0]
    dy = origin[1] - point[1]  # Invert Y-axis if working with image coordinates

    angle = np.degrees(np.arctan2(dy, dx))

    if -45 <= angle <= 45:
        return "Right"
    elif 45 < angle <= 135:
        return "Up"
    elif angle > 135 or angle < -135:
        return "Left"
    elif -135 <= angle < -45:
        return "Down"

def main() -> None:
    """
    Main function to process raw image and annotation files.

    The script:
      1. Reads configuration from EnvSettings.
      2. Finds matched raw image and annotation files.
      3. Resets output directories.
      4. Processes each image: resizes and centers it on a canvas.
      5. Processes annotations: scales coordinates and assigns semantic labels.
      6. Saves a combined JSON with image and annotation metadata.
    """
    env: EnvSettings = EnvSettings()

    # Retrieve matched image and annotation files based on file extensions.
    splitted_raw_files: dict = list_matched_files(
        folder_path=env.raw_data_path,
        image_extensions=['.png', '.jpg'],
        annot_extensions=['.txt']
    )

    # Prepare and reset output directories.
    annot_json_folder = os.path.join(env.data_path, 'annot_json')
    reset_directory(annot_json_folder)

    # Set constants for image processing and annotation.
    new_resolution: Tuple[int, int] = (512, 512)
    category_id: int = 1

    for splitted_set, file_groups in splitted_raw_files.items():
        # Each key corresponds to a split set; file_groups[0]: images, file_groups[1]: annotations.
        output_folder = os.path.join(env.data_path, splitted_set)
        reset_directory(output_folder)
        output_json_file = os.path.join(annot_json_folder, f'instances_{splitted_set}.json')

        # Initialize JSON structure with a single category and empty lists for images and annotations.
        output_json: Dict = {
            "categories": [
                {
                    "supercategory": "Corner",
                    "id": category_id,
                    "name": "Corner"
                }
            ],
            "images": [],
            "annotation": []
        }
        annot_id = 0  # Counter for unique annotation IDs

        # Process paired image and annotation files.
        for raw_img_path, raw_annot_path in zip(file_groups[0], file_groups[1]):
            # Process image and retrieve scaling/padding factors.
            new_img_path, scale_x, scale_y, left_padding, top_padding = process_image(
                raw_img_path, output_folder, new_resolution
            )

            # Generate a unique image ID (without extension)
            image_id = os.path.splitext(os.path.basename(new_img_path))[0]
            output_json["images"].append({
                "height": new_resolution[1],
                "width": new_resolution[0],
                "id": image_id,
                "file_name": os.path.basename(new_img_path)
            })


            # Process the annotations
            processor = GeometryProcessor(raw_annot_path=raw_annot_path, logger=logger)
            segments = processor.split_edges_into_segments()
            processor.save_segments(segments)



            def init_neighbors_as_coordinates():
                return [(-1, -1), (-1, -1), (-1, -1), (-1, -1)]  # [Up, Left, Down, Right]

            def init_neighbors_as_code():
                return "0000"  # [Up, Left, Down, Right]

            # Function to get direction index
            def get_direction_index(origin, point):
                dx = point[0] - origin[0]
                dy = origin[1] - point[1]  # Invert Y-axis for image coordinates

                angle = np.degrees(np.arctan2(dy, dx))

                if -45 <= angle <= 45:
                    return 3  # Right
                elif 45 < angle <= 135:
                    return 0  # Up
                elif angle > 135 or angle < -135:
                    return 1  # Left
                elif -135 <= angle < -45:
                    return 2  # Down

            # Building the graph
            coordinate_graph = {}
            code_graph = {}
            for pt1, pt2 in segments:
                if pt1 not in coordinate_graph:
                    coordinate_graph[pt1] = init_neighbors_as_coordinates()
                if pt2 not in coordinate_graph:
                    coordinate_graph[pt2] = init_neighbors_as_coordinates()

                if pt1 not in code_graph:
                    code_graph[pt1] = init_neighbors_as_code()
                if pt2 not in code_graph:
                    code_graph[pt2] = init_neighbors_as_code()

                # Determine direction from pt1 to pt2 and vice versa
                dir_idx_pt1_to_pt2 = get_direction_index(pt1, pt2)
                dir_idx_pt2_to_pt1 = get_direction_index(pt2, pt1)

                # Update the neighbors in the coordinate graph
                coordinate_graph[pt1][dir_idx_pt1_to_pt2] = pt2
                coordinate_graph[pt2][dir_idx_pt2_to_pt1] = pt1

                # Update the neighbors in the code graph
                text_list = list(code_graph[pt1])
                text_list[dir_idx_pt1_to_pt2] = "1"
                code_graph[pt1] = ''.join(text_list)

                text_list = list(code_graph[pt2])
                text_list[dir_idx_pt2_to_pt1] = "1"
                code_graph[pt2] = ''.join(text_list)

            # Step 1: Find the starting point closest to (0, 0)
            origin = min(coordinate_graph.keys(), key=lambda p: np.hypot(p[0], p[1]))

            # Step 2: BFS to build quadtree levels
            visited = set()
            queue = deque([(origin, 0)])  # (point, level)
            quatree = {}

            while queue:
                point, level = queue.popleft()
                if point in visited:
                    continue
                visited.add(point)

                # Add point to the corresponding level in the quadtree
                if level not in quatree:
                    quatree[level] = []
                quatree[level].append(point)

                # Enqueue neighbors for the next level
                neighbors = coordinate_graph[point]
                for neighbor in neighbors:
                    if neighbor != (-1, -1) and neighbor not in visited:
                        queue.append((neighbor, level + 1))

            coordinate_graph['quadtree'] = quatree



            breakpoint()


















        #     # Process and scale the annotation data.
        #     annotations, annot_id = process_annotations(
        #         raw_annot_path, scale_x, scale_y, left_padding, top_padding,
        #         image_id, category_id, annot_id
        #     )
        #     output_json["annotation"].extend(annotations)
        #
        # # Save the output JSON file for this split set.
        # with open(output_json_file, 'w') as f:
        #     json.dump(output_json, f, indent=4)


if __name__ == "__main__":
    main()