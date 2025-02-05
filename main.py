import json
from pathlib import Path
from typing import Tuple, Dict, List
import numpy as np
from loguru import logger

from src.config.settings import EnvSettings
from src.utils.local import list_matched_files, reset_directory
from src.utils.manip import process_image
from src.utils.geometry import GeometryProcessor
from src.utils.graph import GraphAnnotator


def process_file_pair(
        raw_img_path: Path,
        raw_annot_path: Path,
        output_folder: Path,
        new_resolution: Tuple[int, int],
        category_id: int,
        annot_id: int,
        annot_npy_dir: Path
):
    """
    Process a single image-annotation file pair.

    Returns:
        image_json: Dict containing image metadata.
        annot_id: Updated annotation ID after processing.
    """
    # Process image and get scaling/padding factors
    new_img_path, scale_x, scale_y, left_padding, top_padding = process_image(
        str(raw_img_path), str(output_folder), new_resolution
    )
    image_id = Path(new_img_path).stem  # Unique image ID based on filename without extension
    image_info = {
        "height": new_resolution[1],
        "width": new_resolution[0],
        "id": image_id,
        "file_name": Path(new_img_path).name,
    }

    # Process annotation
    geom_processor = GeometryProcessor(raw_annot_path=str(raw_annot_path), logger=logger)
    segments = geom_processor.split_edges_into_segments()
    segments = geom_processor.scale_segments(
        segments=segments,
        scale_x=scale_x,
        scale_y=scale_y,
        left_padding=left_padding,
        top_padding=top_padding
    )

    annotator = GraphAnnotator(
        segments=segments,
        image_id=image_id,
        category_id=category_id,
        logger=logger
    )
    coordinate_graph, _ = annotator.build_graphs()
    annotations, annot_id = annotator.create_annotations(annot_id=annot_id)

    # Save coordinate graph as numpy file
    npy_path = annot_npy_dir / f"{image_id}.npy"
    np.save(str(npy_path), coordinate_graph)

    return image_info, annotations, annot_id


def process_split_set(
        split_set: str,
        image_paths: List[Path],
        annot_paths: List[Path],
        env: EnvSettings,
        new_resolution: Tuple[int, int],
        category_id: int,
        annot_json_folder: Path,
        annot_npy_dir: Path
) -> None:
    """
    Process one split set (e.g., 'train', 'val', etc.) by iterating through
    matched image and annotation files.
    """
    output_folder = Path(env.data_path) / split_set
    reset_directory(output_folder)
    output_json_file = annot_json_folder / f"instances_{split_set}.json"

    # Initialize output JSON structure
    output_json: Dict = {
        "categories": [
            {
                "supercategory": "Corner",
                "id": category_id,
                "name": "Corner"
            }
        ],
        "images": [],
        "annotations": []  # corrected key name
    }
    annot_id = 0

    # Process each image-annotation pair
    for raw_img_path, raw_annot_path in zip(image_paths, annot_paths):
        image_info, annotations, annot_id = process_file_pair(
            raw_img_path,
            raw_annot_path,
            output_folder,
            new_resolution,
            category_id,
            annot_id,
            annot_npy_dir
        )
        output_json["images"].append(image_info)
        output_json["annotations"].extend(annotations)

    # Save combined JSON file for this split set
    with open(str(output_json_file), 'w') as f:
        json.dump(output_json, f, indent=4)
    logger.info(f"Saved JSON for split '{split_set}' to {output_json_file}")


def main() -> None:
    """
    Main function to process raw images and annotation files.

    Steps:
        1. Load configuration settings.
        2. Retrieve matched raw image and annotation files.
        3. Reset output directories.
        4. For each split, process image-annotation pairs.
        5. Save combined JSON metadata.
    """
    env = EnvSettings()
    # Use pathlib for better path handling
    raw_data_path = Path(env.raw_data_path)
    reset_directory(env.data_annot_json)
    reset_directory(env.data_annot_npy)
    reset_directory(env.data_original_vector_boundary)

    # File matching based on extensions
    matched_files = list_matched_files(
        folder_path=raw_data_path,
        image_extensions=['.png', '.jpg'],
        annot_extensions=['.txt']
    )
    new_resolution: Tuple[int, int] = (512, 512)
    category_id: int = 1

    # Process each split (e.g., 'train', 'val', etc.)
    for split_set, file_groups in matched_files.items():
        image_paths, annot_paths = file_groups  # assume first list are images, second are annotations
        process_split_set(
            split_set,
            image_paths,
            annot_paths,
            env,
            new_resolution,
            category_id,
            env.data_annot_json,
            env.data_annot_npy
        )


if __name__ == "__main__":
    main()
