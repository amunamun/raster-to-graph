import os
from typing import List, Dict

def list_files_by_extension(folder_path: str, extensions: List[str]) -> Dict[str, List[str]]:
    """
    Lists files in a specified folder based on the provided extensions.

    Args:
        folder_path (str): Path to the target folder.
        extensions (List[str]): List of file extensions to filter (e.g., ['.png', '.txt']).

    Returns:
        Dict[str, List[str]]: A dictionary where keys are extensions and values are lists of matching file names.
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Invalid folder path: {folder_path}")

    files_by_extension = {ext: [] for ext in extensions}  # Initialize dictionary

    # Iterate through the folder and categorize files
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):  # Ensure it's a file, not a directory
            for ext in extensions:
                if file.lower().endswith(ext.lower()):
                    files_by_extension[ext].append(file)
                    break  # Avoid checking other extensions once matched

    return files_by_extension