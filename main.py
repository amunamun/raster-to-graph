import gdown
from typing import List
from clearml import Task
from loguru import logger, Logger
from src.config.settings import EnvSettings
from src.utils.google_drive import download_files_from_drive


if __name__ == "__main__":
    env: EnvSettings = EnvSettings()
    log: Logger = logger
    clearml_task = Task.init(project_name=env.clearml_project_name)
    files_locally = download_files_from_drive(url=env.gdrive_folder_link, output_folder=env.gdrive_folder_download_path)
    breakpoint()

