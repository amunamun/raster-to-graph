from setuptools import setup

setup(
    name="raster-to-graph",
    version="0.0.1",
    description="Training Raster to Graph",
    install_requires=[
        "opencv-python~=4.8.0.74",
        "python-dotenv==0.21.0",
        "gdown==5.2.0",
        "clearml==1.17.1",
        "pydantic_settings==2.7.1",
        "loguru==0.7.3",
        "pandas==2.2.3",
        "cython==0.29.30"
    ],
    python_requires=">=3.10",
)
