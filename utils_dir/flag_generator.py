"""
Module to save functionality of flag generation.
"""

import numpy as np
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

class FlagSoundGenerator:
    """
    This class generates the sound file from flag string.
    """

    @staticmethod
    def generate(data_to_encode: str, save_to_file: str, db_high: float, db_low: float, sample_rate: int = 44100, bit_duration: float = 1) -> None:
        """This method generates and saves the audio file.
        :param data: string of 1s and 0s.
        :param sample_rate: sample rate of the wave signal.
        :param bit_duration: the duration of each bit in seconds.
        :param db_high: decibel for signal with 1s.
        :param db_low: decibel for signal with 0s.
        """
        data_encoded = FlagSoundGenerator._text_to_binary(data_to_encode) 
        bass_sound = FlagSoundGenerator._generate_wave(data_encoded, db_high, db_low, sample_rate, bit_duration)
        FlagSoundGenerator._save_audio_files(save_to_file, bass_sound, sample_rate)

    @staticmethod
    def _text_to_binary(input_text: str) -> str:
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

    @staticmethod
    def _generate_wave(data: str, db_high: float, db_low: float, sample_rate: int = 44100, bit_duration: float = 1) -> np.ndarray:
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

    @staticmethod
    def _save_audio_files(name_of_files: str, wave: np.ndarray, sample_rate: int = 44100) -> None:
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
