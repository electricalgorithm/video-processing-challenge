"""
Module to handle FFmpeg commands
"""

import logging
import subprocess

class FFmpegOperations:
    """This class implements the functionalty of FFmpeg commands."""
    ENABLE_DEBUG = False

    # Internal attributes
    __info_channel = subprocess.STDOUT if ENABLE_DEBUG else subprocess.DEVNULL

    @staticmethod
    def get_ffmpeg_command(*args) -> list[str]:
        """Returns the ffmpeg command within given
        list of arguments.
        :param args: arguments to run ffmpeg
        :return: list of strings 
        """
        return ["ffmpeg", "-hide_banner", "-y", args]
    
    @staticmethod
    def extract_audio(input_file: str, output_file: str, start_time: int, duration: int) -> None:
        """This function extracts the audio file from a video container
        using ffmpeg. Note that, the audio checked out with 1st stream.

        :param input_file: a string containing the video container location.
        :param output_file: location of the extracted audio, please end with encoding format.
        :param start_time: the start time to trim the audio.
        :param duration: duration to trim the audio.
        """
        command = FFmpegOperations.get_ffmpeg_command(
            "-ss", str(start_time),
            "-t", str(duration),
            "-i", input_file,
            "-map", "0:1",
            output_file
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug("Audio extraction complete.")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("Audio extraction failed.")
    
    @staticmethod
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

        command = FFmpegOperations.get_ffmpeg_command(
            "-ss", start_time,  # Start time
            "-t", duration,     # Duration
            "-i", input_file,   # Input file
            output_file         # Output file
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug("Video extraction complete.")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("Video extraction failed.")
    
    @staticmethod
    def extract_stereo_channels(input_file: str, left_output_file: str, right_output_file: str) -> None:
        """Extract stereo audio files from a stereo container.
        :param input_file: a stereo container
        :param left_output_file: file to save left channel
        :param right_output_file: file to save right channel
        """
        command = FFmpegOperations.get_ffmpeg_command(
            "-i", input_file,
            "-filter_complex",
            "[0:a]channelsplit=channel_layout=stereo[left][right]",
            "-map", "[left]",
            left_output_file,
            "-map", "[right]",
            right_output_file
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug("Stereo channel extraction complete.")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("Stereo channel extraction failed.")
    
    @staticmethod
    def adjust_volume(input_file: str, output_file: str, volume_level: float) -> None:
        """Adjust the volume within a ratio of old magnitudes.
        :param input_file: a mono audio location to read
        :param output_file: a mono audio location to save
        :param volume_level: a ratio comparing to old volume such as 1.02
        """
        command = FFmpegOperations.get_ffmpeg_command(
            "-i", input_file,
            "-filter_complex",
            f"volume={volume_level}",
            output_file
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug(f"Volume adjustment complete. Output file: {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("Volume adjustment failed.")
    
    @staticmethod
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
        command = FFmpegOperations.get_ffmpeg_command(
            "-i", left_file,
            "-i", center_file,
            "-i", right_file,
            "-i", lfe_file,
            "-i", rear_left_file,
            "-i", rear_right_file,
            "-filter_complex",
            "[0:a][1:a][2:a][3:a][4:a][5:a]amerge=inputs=6[a]",
            "-map", "[a]",
            output_file
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug("5.1 channel combination complete.")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("5.1 channel combination failed.")

    @staticmethod
    def extract_frames_from_video(input_video: str, output_directory: str, frame_rate: int = 30):
        """Extract frames from a video using ffmpeg.
        :param input_video: path to the input video
        :param output_directory: path to the output directory
        :param frame_rate: frame rate of the output frames
        """
        command = FFmpegOperations.get_ffmpeg_command(
            "-i", input_video,
            "-vf", f"fps={frame_rate}",
            f"{output_directory}/output_frames_%04d.png"
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug(f"Frames extracted from {input_video} and saved to {output_directory}")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("Frame extraction failed.")
    
    @staticmethod
    def create_video_from_frames(input_frames_dir: str, output_video: str, frame_rate: int = 30):
        """Create a video from frames using ffmpeg.
        :param input_frames_dir: path to the directory containing the frames
        :param output_video: path to the output video
        :param frame_rate: frame rate of the output video
        """
        command = FFmpegOperations.get_ffmpeg_command(
            "-framerate", f"{frame_rate}",
            "-i", f"{input_frames_dir}/output_frames_%04d.png",
            "-crf", "20",
            "-preset", "medium",
            output_video
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug(f"Video created from frames in {input_frames_dir} and saved as {output_video}")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("Video creation from frames failed.")
    
    @staticmethod
    def combine_video_with_audio(video: str, sound: str, output: str) -> None:
        """Combine a video with given sound.
        :param video: path to the video
        :param sound: path to the sound
        :param output: save path
        """
        command = FFmpegOperations.get_ffmpeg_command(
            "-i", video,
            "-i", sound,
            output
        )

        try:
            subprocess.run(command, check=True, stderr=FFmpegOperations.__info_channel)
            logging.debug(f"Video combined with the sound given.")
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)
            logging.error("Video combination with sound has encountered a problem.")