import os
import shutil
import random
from pathlib import Path
from typing import List, Tuple, Dict


def reset_directory(directory_path: Path):
    """
    Checks if a directory exists. If it does, deletes it and creates an empty one.
    
    Args:
        directory_path (str): The path of the directory to reset.
    """
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)  # Delete the existing directory and its contents
    os.makedirs(directory_path)  # Create a new empty directory

def list_matched_files(folder_path: Path, image_extensions: List[str], annot_extensions: List[str]) -> Dict[str, Tuple[List[str], List[str]]]:
    """
    Lists files in a specified folder, ensuring that image files with various extensions and annot files
    with various extensions are aligned based on their base names.

    Args:
        folder_path (str): Path to the target folder.
        image_extensions (List[str]): List of image file extensions to filter (e.g., ['.png', '.jpg']).
        annot_extensions (List[str]): List of annot file extensions to filter (e.g., ['.txt', '.csv']).

    Returns:
        Dict[str, Tuple[List[str], List[str]]]: A dictionary containing train, validation, and test sets where corresponding files have the same base name but different extensions.
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Invalid folder path: {folder_path}")

    # Initialize dictionaries to store files by base name
    image_files_dict = {}
    annot_files_dict = {}

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            for img_ext in image_extensions:
                if file.lower().endswith(img_ext.lower()):
                    base_name = file[:-len(img_ext)]
                    image_files_dict[base_name] = file_path
                    break
            for txt_ext in annot_extensions:
                if file.lower().endswith(txt_ext.lower()):
                    base_name = file[:-len(txt_ext)]
                    annot_files_dict[base_name] = file_path
                    break

    # Find common base names that exist for both image and annot files
    common_base_names = list(set(image_files_dict.keys()).intersection(annot_files_dict.keys()))
    random.shuffle(common_base_names)

    # Split into train, validation, and test sets
    total_files = len(common_base_names)
    train_end = int(0.7 * total_files)
    valid_end = train_end + int(0.2 * total_files)

    train_names = common_base_names[:train_end]
    valid_names = common_base_names[train_end:valid_end]
    test_names = common_base_names[valid_end:]

    def get_file_pairs(names: List[str]) -> Tuple[List[str], List[str]]:
        return [image_files_dict[name] for name in names], [annot_files_dict[name] for name in names]

    train_images, train_annots = get_file_pairs(train_names)
    valid_images, valid_annots = get_file_pairs(valid_names)
    test_images, test_annots = get_file_pairs(test_names)

    return {
        'train': (train_images, train_annots),
        'valid': (valid_images, valid_annots),
        'test': (test_images, test_annots)
    }