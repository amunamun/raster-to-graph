import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from typing_extensions import Annotated

load_dotenv()


class EnvSettings(BaseSettings):

    # Variable for data
    raw_data_path: Annotated[
        str, Field(default=os.getenv("RAW_DATA_PATH", "tmp"))
    ]
    data_path: Annotated[
        str, Field(default=os.getenv("RAW_DATA_PATH", "data"))
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
        str, Field(default=os.environ["CLEARML_API_ACCESS_KEY"])
    ]
    clearml_secret_key: Annotated[
        str, Field(default=os.environ["CLEARML_API_SECRET_KEY"])
    ]
    clearml_project_name: Annotated[
        str, Field(default=os.getenv("CLEARML_PROJECT_NAME", "RASTER_TO_GRAPH"))
    ]
