"""
This module handles audio related tasks.
"""
import logging
from pydub import AudioSegment
from ffmpeg_operations import FFmpegOperations

class AudioToolbox:
    _extracted_sound_file = "tmp/video_sound.wav"
    _extracted_high_vol_sound_file = "tmp/video_sound_high_vol.wav"
    _extracted_left_sound_file = "tmp/video_sound_left_channel.wav"
    _extracted_right_sound_file = "tmp/video_sound_right_channel.wav"


    @staticmethod
    def get_wav_duration(file_path) -> None:
        """Get the duration of a wav file in seconds.
        :param file_path: path to the wav file
        """
        audio = AudioSegment.from_wav(file_path)
        duration_ms = len(audio)
        duration_s = duration_ms / 1000

        return int(duration_s)

    @staticmethod
    def construct_5_1_audio(input_file: str, start_time: int, duration: int, flag_sound: str, output_sound_file: str) -> None:
        logging.info("Extracting the audio from the container.")
        FFmpegOperations.extract_audio(input_file, AudioToolbox._extracted_sound_file, start_time, duration)

        logging.info("Increasing audio volume level.")
        FFmpegOperations.adjust_volume(AudioToolbox._extracted_sound_file, AudioToolbox._extracted_high_vol_sound_file, 1.5)

        logging.info("Extracting left and right audio from sound file.")
        FFmpegOperations.extract_stereo_channels(AudioToolbox._extracted_high_vol_sound_file, AudioToolbox._extracted_left_sound_file, AudioToolbox._extracted_right_sound_file)

        logging.info("Combining the channels with bass flag into 5.1 channels.")
        FFmpegOperations.combine_to_5_1_audio(AudioToolbox._extracted_left_sound_file, AudioToolbox._extracted_left_sound_file, AudioToolbox._extracted_right_sound_file, flag_sound, AudioToolbox._extracted_left_sound_file, AudioToolbox._extracted_right_sound_file, output_sound_file)
