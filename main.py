import os
import json
from typing import Tuple, Dict

from src.config.settings import EnvSettings
from src.utils.local import list_matched_files, reset_directory
from src.utils.manip import process_image, process_annotations

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

            # Process and scale the annotation data.
            annotations, annot_id = process_annotations(
                raw_annot_path, scale_x, scale_y, left_padding, top_padding,
                image_id, category_id, annot_id
            )
            output_json["annotation"].extend(annotations)

        # Save the output JSON file for this split set.
        with open(output_json_file, 'w') as f:
            json.dump(output_json, f, indent=4)


if __name__ == "__main__":
    main()