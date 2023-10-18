"""
This module handles video related tasks.
"""

import os
import logging
from random import randint
from PIL import Image
from utils_dir.ffmpeg_operations import FFmpegOperations

class VideoToolbox:
    _extracted_video_file = "tmp/video_file.mp4"
    _extracted_frames_dir = "tmp/extracted_frames"

    @staticmethod
    def construct_video_within_hint_on_top(input_file: str, start_time: int, duration: int, hint_image: str, output_video_file: str):
        logging.info("Extracting video from the container.")
        FFmpegOperations.extract_video(input_file, VideoToolbox._extracted_video_file, start_time, duration)

        logging.info("> Extracting the frames from the video.")
        FFmpegOperations.extract_frames_from_video(VideoToolbox._extracted_video_file, VideoToolbox._extracted_frames_dir)

        logging.info("> Placing hint image onto frames randomely.")
        VideoToolbox.insert_images_into_frames(VideoToolbox._extracted_frames_dir, hint_image, "4x4", 30, 1800)

        logging.info("> Creating video from the new frames.")
        FFmpegOperations.create_video_from_frames(VideoToolbox._extracted_frames_dir, output_video_file)

    @staticmethod
    def divide_image_to_tabular(image_location: str, tabular_dims: str) -> list[list[dict[str, object]]]:
        """It divides a PIL Image into tabular sub-images with given
        dimensions.
        :param image: Image's path
        :param tabular_dims: A string contains dimensions such as 3x4 (3 rows, 4 cols).
        """
        # Copy the image object.
        image = Image.open(image_location)

        # Parse tabular_dims.
        rows = int(tabular_dims.split("x")[0])
        cols = int(tabular_dims.split("x")[1])

        # Calculate the size of sub-images.
        width, height = image.size
        sub_width = width // cols
        sub_height = height // rows

        sub_images_matrix: list[list[dict[str, object]]] = []
        for row_index in range(rows):
            row_images: list[dict[str, object]] = []

            for col_index in range(cols):
                # Calculate the coordinates of currect sub image.
                left_coord = col_index * sub_width
                righ_coord = left_coord + sub_width
                upper_coord = row_index * sub_height
                lower_coord = upper_coord + sub_height
                # Extract the sub image and store it.
                sub_image = image.crop((left_coord, upper_coord, righ_coord, lower_coord))
                image_data = {
                    "image": sub_image,
                    "left_start": left_coord,
                    "upper_start": upper_coord,
                }
                row_images.append(image_data)
            sub_images_matrix.append(row_images)

        # Close the first image.
        image.close()

        return sub_images_matrix


    @staticmethod
    def insert_images_into_frames(input_dir: str, image_to_overlay: str, tabular_dims: str = "6x6", frame_interval=30, start_frame=0):
        # Get all files in the input directory.
        files = sorted(os.listdir(input_dir))
        frame_number = 0

        sub_images = VideoToolbox.divide_image_to_tabular(image_to_overlay, tabular_dims)
        possible_sub_images = [
            (row_index, col_index)
            for row_index in range(len(sub_images))
            for col_index in range(len(sub_images[0]))
        ]

        # Iterate over the files in the input directory.
        for i, filename in enumerate(files):
            if filename.endswith(".png"):

                if len(possible_sub_images) == 0:
                    break

                # If the frame number is a multiple of the frame interval, watermark the current frame.
                if frame_number >= start_frame and frame_number % frame_interval == 0:
                    # Open the image.
                    frame = Image.open(os.path.join(input_dir, filename))

                    # Add a sub-image to main frame.
                    random_index = randint(0, len(possible_sub_images)-1)
                    sub_image_index = possible_sub_images[random_index]
                    sub_image_to_place = sub_images[sub_image_index[0]][sub_image_index[1]]
                    
                    # Get image data
                    sub_image = sub_image_to_place["image"]
                    sub_image_left_start = sub_image_to_place["left_start"]
                    sub_image_upper_start = sub_image_to_place["upper_start"]
                    
                    # Paste onto main frame.
                    frame.paste(sub_image, (sub_image_left_start, sub_image_upper_start))
                    print(f"Sub image {possible_sub_images[random_index]} placed onto frame {frame_number+1}.")
                    
                    # Delete from old list.
                    del possible_sub_images[random_index]

                    # Save the frame.
                    frame.save(os.path.join(input_dir, filename))
                
                # Increment the frame number.
                frame_number = i + 1
