import os
from PIL import Image
from typing import Tuple


def process_image(raw_img_path: str,
                  output_folder: str,
                  new_resolution: Tuple[int, int]) -> Tuple[
    str, float, float, int, int]:
    """
    Processes an image by resizing it, centering it on a canvas of target resolution,
    and saving the processed image.

    Args:
        raw_img_path (str): Path to the raw input image.
        output_folder (str): Folder where the processed image will be saved.
        new_resolution (Tuple[int, int]): Target (width, height) for the processed image.

    Returns:
        Tuple[str, float, float, int, int]:
            - new_img_path (str): Path to the saved image.
            - scale_x (float): Scaling factor in the x-direction.
            - scale_y (float): Scaling factor in the y-direction.
            - left_padding (int): Horizontal padding applied.
            - top_padding (int): Vertical padding applied.
    """
    new_width, new_height = new_resolution
    new_img_path = os.path.join(output_folder, os.path.basename(raw_img_path))

    with Image.open(raw_img_path) as img:
        original_width, original_height = img.size
        scale_x = new_width / original_width
        scale_y = new_height / original_height

        # Resize image while maintaining aspect ratio
        img.thumbnail(new_resolution)

        # Create a blank white canvas and calculate padding to center the image
        canvas = Image.new("RGB", new_resolution, (255, 255, 255))
        left_padding = (new_width - img.width) // 2
        top_padding = (new_height - img.height) // 2
        canvas.paste(img, (left_padding, top_padding))

        # Save the processed image
        canvas.save(new_img_path)

    return new_img_path, scale_x, scale_y, left_padding, top_padding