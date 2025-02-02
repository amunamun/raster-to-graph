import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from typing_extensions import Annotated

load_dotenv()


class EnvSettings(BaseSettings):
    # Google Drive configuration – if still needed
    gdrive_folder_link: Annotated[
        str, Field(default=os.environ["GDRIVE_FOLDER_LINK"])
    ]

    gdrive_folder_download_path: Annotated[
        str, Field(default=os.getenv("GDRIVE_FOLDER_DOWNLOAD_PATH", "tmp"))
    ]

    # ClearML configuration
    clearml_web_server: Annotated[
        str, Field(default=os.getenv("CLEARML_WEB_SERVER", "https://app.clear.ml/"))
    ]
    clearml_api_server: Annotated[
        str, Field(default=os.getenv("CLEARML_API_SERVER", "https://api.clear.ml"))
    ]
    clearml_file_server: Annotated[
        str, Field(default=os.getenv("CLEARML_FILE_SERVER", "https://files.clear.ml"))
    ]
    clearml_access_key: Annotated[
        str, Field(default=os.environ["CLEARML_ACCESS_KEY"])
    ]
    clearml_secret_key: Annotated[
        str, Field(default=os.environ["CLEARML_SECRET_KEY"])
    ]
    clearml_project_name: Annotated[
        str, Field(default=os.getenv("CLEARML_PROJECT_NAME", "RASTER_TO_GRAPH"))
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"