import gdown
from typing import List

def download_files_from_drive(url: str, output_folder: str) -> List[str]:
    """
    Downloads all files from a Google Drive folder.

    Parameters:
        url (str): The URL of the Google Drive folder to download.
        output_folder (str): The local directory where the downloaded files will be saved.

    Returns:
        List[str]: A list of file paths for the downloaded files.
    """
    return gdown.download_folder(url=url, output=output_folder, quiet=True, use_cookies=True)
