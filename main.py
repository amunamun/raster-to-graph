import gdown
from typing import List
from clearml import Task
from loguru import logger
from src.config.settings import EnvSettings
from src.utils.local import list_files_by_extension


if __name__ == "__main__":
    env: EnvSettings = EnvSettings()
    clearml_task = Task.init(project_name=env.clearml_project_name)
    raw_files = list_files_by_extension(folder_path=env.raw_data_path, extensions=['.png', '.txt'])
    
    breakpoint()


