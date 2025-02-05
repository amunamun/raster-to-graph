# Raster-to-Graph

Raster-to-Graph is a repository for converting raster data into graph representations. The repository includes tools to transform data from the DOTA format to a custom format and to train a model using the processed data.

## Prerequisites

- **Python:** 3.10.16 (recommended – tested in a Conda virtual environment)
- **CUDA:** Version 11.1 (if using GPU acceleration)
- **Compiler:** g++-10 (for building native extensions)

## Setup Instructions

### 1. Clone the Repository

Clone the repo to your local machine:

```bash
git clone <repository_url>
cd raster-to-graph
```

### 2. Create and Activate a Virtual Environment
Using Conda:

```bash
conda create -n raster_to_graph python=3.10.16
conda activate raster_to_graph
```

### 3. Install the Package
Install the Python package with pip:
```bash
pip install .
```

### 4. Build Native Operations
Run the build script to compile necessary operations:

```bash
sh src/training_utils/models/ops/make.sh
```

### 5. Resolve CUDA Compatibility (if needed)
If you encounter CUDA mismatches, ensure you have CUDA 11.1 installed. Then, install the required compiler and set environment variables:

```bash
sudo apt install cuda-toolkit-11-1
sudo apt-get install g++-10
export CC=gcc-10
export CXX=g++-10
```
## Data Preparation

### Step 1: Download Data
Use gdown to download the data from Google Drive:

```bash
gdown --folder https://drive.google.com/drive/folders/1_deeQN2TNOg4setau1G2_IrjnPAqOBSq?usp=sharing -O tmp
```


### Step 2: Set Environment Variables
Configure the necessary environment variables. You can either export these variables in your shell or create a .env file:

```env
# CLEARML Configuration
export RAW_DATA_PATH='tmp'
export DATA_PATH='data'
export OUTPUT_PATH='output'

# CLEARML Configuration
export CLEARML_WEB_HOST='https://app.clear.ml/'
export CLEARML_API_HOST='https://api.clear.ml'
export CLEARML_FILES_HOST='https://files.clear.ml'
export CLEARML_API_ACCESS_KEY=<your_clearml_api_access_key>
export CLEARML_API_SECRET_KEY=<your_clearml_api_secret_key>
export CLEARML_PROJECT_NAME='RASTER_TO_GRAPH'

# Image Settings
export IMAGE_RESOLUTION='512,512'
```
Replace <your_clearml_api_access_key> and <your_clearml_api_secret_key> with your actual ClearML credentials.


### Step 3: Transform the Data
Convert the downloaded DOTA-formatted data into the required format by running:

```bsah
python get_data.py
```

## Training the Model
Once the data is prepared, pass on the required argument either in the terminal of edit the args.py file.

You can start the training process with:

```bash
python train.py
```
## Troubleshooting

1. CUDA Issues: Verify that CUDA 11.1 is installed and the environment variables for the compiler are correctly set.
2. Dependency Issues: Ensure that you are using Python 3.10.16 as specified, since the repository has been tested with this version.
3. ClearML Configuration: Double-check your ClearML keys and endpoints if you run into issues related to experiment tracking.