from setuptools import setup

setup(
    name="raster-to-graph",
    version="0.0.1",
    description="Training Raster to Graph",
    install_rewuires=[
        "cython==0.29.30",
        "imageio==2.22.0",
        "matplotlib==3.5.2",
        "networkx==2.6.3",
        "numpy==1.21.6",
        "opencv-python==4.5.3.56",
        "pillow==8.3.2",
        "scikit-image==0.19.2",
        "scipy==1.7.3",
        "shapely==2.0.1",
        "torch @ https://download.pytorch.org/whl/cu111/torch-1.9.1%2Bcu111-cp38-cp38-manylinux1_x86_64.whl",
        "torchvision @ https://download.pytorch.org/whl/cu111/torchvision-0.10.1%2Bcu111-cp38-cp38-manylinux1_x86_64.whl",
        "tqdm==4.64.0",
        "gdown==4.7.3",
        "clearml==1.17.1",
        "loguru==0.7.3",
        "pydantic_settings==2.0.3"
    ],
    python_requires="==3.7.16",
)
