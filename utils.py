import os
import subprocess
from random import randint
import numpy as np
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from pydub import AudioSegment
from PIL import Image, ImageFont, ImageDraw

ENABLE_DEBUG = False
INFO_CHANNEL = subprocess.STDOUT if ENABLE_DEBUG else subprocess.DEVNULL

def generate_wave(data: str, db_high: float, db_low: float, sample_rate: int = 44100, bit_duration: float = 1) -> np.ndarray:
    """It generates and encodes the wave with amplitude modulation.
    :param data: string of 1s and 0s.
    :param sample_rate: sample rate of the wave signal.
    :param bit_duration: the duration of each bit in seconds.
    :param db_high: decibel for signal with 1s.
    :param db_low: decibel for signal with 0s.
    :returns np.ndarray: the encoded signal
    """
    high_amplitude = 10 ** (db_high / 20)
    low_amplitude = 10 ** (db_low / 20)
    
    signal = np.array([])
    for bit in data:
        if bit == '1':
            signal = np.append(signal, high_amplitude * np.sin(2 * np.pi * 10 * np.arange(0, bit_duration, 1 / sample_rate)))
        elif bit == '0':
            signal = np.append(signal, low_amplitude * np.sin(2 * np.pi * 10 * np.arange(0, bit_duration, 1 / sample_rate)))
    
    return signal


def save_audio_files(name_of_files: str, wave: np.ndarray, sample_rate: int = 44100) -> None:
    """This function stores the wav file and graph file in file-system.
    :param wave: The wave file to be investigeted.
    :param sample_rate: The sample rate of the sound.
    """
    write(name_of_files, sample_rate, wave.astype(np.float32))
    plt.plot(wave)
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.title("Encoded Waveform")
    file_name = name_of_files.split(".")[0]
    plt.savefig(f"{file_name}.png")



def text_to_binary(input_text: str) -> str:
    """Takes a string and encodes it to 1s and 0s with using ASCII
    representations.
    :param input_text: the string wanted to convert into 1s and 0s.
    :returns str: a string encoded.
    """
    binary_string = ""
    for char in input_text:
        # Get the ASCII code for the character and convert it to binary
        binary_char = format(ord(char), '08b')  # '08b' formats the number as an 8-digit binary string
        binary_string += binary_char
    return binary_string


def extract_audio(input_file: str, output_file: str, start_time: int, duration: int) -> None:
    """This function extracts the audio file from a video container
    using ffmpeg. Note that, the audio checked out with 1st stream.

    :param input_file: a string containing the video container location.
    :param output_file: location of the extracted audio, please end with encoding format.
    :param start_time: the start time to trim the audio.
    :param duration: duration to trim the audio.
    """
    start_time = str(start_time)
    duration = str(duration)

    cmd = [
        "ffmpeg",
        "-hide_banner",     # Hide FFmpeg banner
        "-y",               # Overwrite output file if it exists
        "-ss", start_time,  # Start time
        "-t", duration,     # Duration
        "-i", input_file,   # Input file
        "-map", "0:1",      # Map audio stream
        output_file         # Output file
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print("Audio extraction complete.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Audio extraction failed.")


def extract_video(input_file: str, output_file: str, start_time: int, duration: int):
    """This function extracts the video file from a video container
    using ffmpeg.

    :param input_file: a string containing the video container location.
    :param output_file: location of the extracted video, please end with encoding format.
    :param start_time: the start time to trim the video.
    :param duration: duration to trim the video.
    """
    start_time = str(start_time)
    duration = str(duration)

    cmd = [
        "ffmpeg",
        "-hide_banner",     # Hide FFmpeg banner
        "-y",               # Overwrite output file if it exists
        "-ss", start_time,  # Start time
        "-t", duration,     # Duration
        "-i", input_file,   # Input file
        output_file         # Output file
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print("Video extraction complete.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Video extraction failed.")

def extract_stereo_channels(input_file: str, left_output_file: str, right_output_file: str) -> None:
    """Extract stereo audio files from a stereo container.
    :param input_file: a stereo container
    :param left_output_file: file to save left channel
    :param right_output_file: file to save right channel
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",                        # Hide FFmpeg banner
        "-y",                                  # Overwrite output file if it exists
        "-i", input_file,                      # Input file
        "-filter_complex",
        "[0:a]channelsplit=channel_layout=stereo[left][right]",
        "-map", "[left]",                     # Map the left channel to left_output_file
        left_output_file,
        "-map", "[right]",                    # Map the right channel to right_output_file
        right_output_file
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print("Stereo channel extraction complete.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Stereo channel extraction failed.")


def adjust_volume(input_file: str, output_file: str, volume_level: float) -> None:
    """Adjust the volume within a ratio of old magnitudes.
    :param input_file: a mono audio location to read
    :param output_file: a mono audio location to save
    :param volume_level: a ratio comparing to old volume such as 1.02
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",                       # Overwrite output file if it exists
        "-i", input_file,            # Input file
        "-filter_complex",
        f"volume={volume_level}",   # Volume adjustment (e.g., 0.2 for 20% volume)
        output_file
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print(f"Volume adjustment complete. Output file: {output_file}")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Volume adjustment failed.")


def combine_to_5_1_audio(left_file, center_file, right_file, lfe_file, rear_left_file, rear_right_file, output_file) -> None:
    """Combine 6 mono audio files into a 5.1 channel audio file.
    :param left_file: left channel file
    :param center_file: center channel file
    :param right_file: right channel file
    :param lfe_file: LFE channel file
    :param rear_left_file: rear left channel file
    :param rear_right_file: rear right channel file
    :param output_file: output file
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",                    # Hide FFmpeg banner
        "-y",                              # Overwrite output file if it exists
        "-i", left_file,                   # Left channel file
        "-i", center_file,                 # Center channel file
        "-i", right_file,                  # Right channel file
        "-i", lfe_file,                    # LFE channel file
        "-i", rear_left_file,              # Rear left channel file
        "-i", rear_right_file,             # Rear right channel file
        "-filter_complex",
        "[0:a][1:a][2:a][3:a][4:a][5:a]amerge=inputs=6[a]",
        "-map", "[a]",                     # Map the merged audio to the output file
        output_file
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print("5.1 channel combination complete.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("5.1 channel combination failed.")

def get_wav_duration(file_path) -> None:
    """Get the duration of a wav file in seconds.
    :param file_path: path to the wav file
    """
    audio = AudioSegment.from_wav(file_path)
    duration_ms = len(audio)
    duration_s = duration_ms / 1000

    return int(duration_s)

def extract_frames_from_video(input_video: str, output_directory: str, frame_rate: int = 30):
    """Extract frames from a video using ffmpeg.
    :param input_video: path to the input video
    :param output_directory: path to the output directory
    :param frame_rate: frame rate of the output frames
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",  # Hide FFmpeg banner
        "-y",            # Overwrite output files if they exist
        "-i", input_video,
        "-vf", f"fps={frame_rate}",
        f"{output_directory}/output_frames_%04d.png"
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print(f"Frames extracted from {input_video} and saved to {output_directory}")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Frame extraction failed.")

def create_video_from_frames(input_frames_dir: str, output_video: str, frame_rate: int = 30):
    """Create a video from frames using ffmpeg.
    :param input_frames_dir: path to the directory containing the frames
    :param output_video: path to the output video
    :param frame_rate: frame rate of the output video
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",  # Hide FFmpeg banner
        "-y",            # Overwrite output file if it exists
        "-framerate", f"{frame_rate}",
        "-i", f"{input_frames_dir}/output_frames_%04d.png",
        "-crf", "20",
        "-preset", "medium",
        output_video
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print(f"Video created from frames in {input_frames_dir} and saved as {output_video}")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Video creation from frames failed.")

def prepare_environment(docs_directory: str = "docs", temp_directory: str = ".temp", frame_extract_directory: str = "secret_frames"):
    # Define the paths for the directories
    secret_frames_directory = os.path.join(temp_directory, frame_extract_directory)

    # Create the "temp" folder under "docs"
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)

    # Create the "secret_frames" folder under "temp"
    if not os.path.exists(secret_frames_directory):
        os.makedirs(secret_frames_directory)

    print("Folders created successfully.")

def combine_video_with_audio(video: str, sound: str, output: str) -> None:
    """Combine a video with given sound.
    :param video: path to the video
    :param sound: path to the sound
    :param output: save path
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",  # Hide FFmpeg banner
        "-y",            # Overwrite output file if it exists
        "-i", video,
        "-i", sound,
        output
    ]

    try:
        subprocess.run(cmd, check=True, stderr=INFO_CHANNEL)
        print(f"Video combined with the sound given.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Video combination with sound has encountered a problem.")

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

def insert_images_into_frames(input_dir: str, image_to_overlay: str, tabular_dims: str = "6x6", frame_interval=30, start_frame=0):
    # Get all files in the input directory.
    files = sorted(os.listdir(input_dir))
    frame_number = 0

    sub_images = divide_image_to_tabular(image_to_overlay, tabular_dims)
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
