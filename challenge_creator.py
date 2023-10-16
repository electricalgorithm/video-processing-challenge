from utils import extract_audio, extract_video, extract_stereo_channels, combine_to_5_1_audio
from utils import generate_wave, text_to_binary, save_audio_files, get_wav_duration, adjust_volume
from utils import extract_frames_from_video, watermark_frames, create_video_from_frames
from utils import prepare_environment, combine_video_with_audio

# Flag text for the challenge.
FLAG_TEXT = text_to_binary("FLAG-AMPMOD_ON_LFE")

# Challenge Settings
sample_rate = 48000                                         # Sample rate (Hz)
bit_duration = 1                                            # Duration of each bit (seconds)
db_high = 20                                                # Amplitude for '1' bits (in dB)
db_low = -20                                                # Amplitude for '0' bits (in dB)
start_time = 10                                             # Trimming start in seconds.
input_file = "docs/bbb_sunflower_1080p_30fps_normal.mp4"    # The video to encode flag into.
output_file = "docs/flagged_video.mp4"                      # The output file.

# Internal files.
_flag_audio_file_high_volume = "docs/temp/flag_audio_high_vol.wav"
_flag_audio_file = "docs/temp/flag_audio.wav"
_output_sound_file = "docs/temp/sound_for_flag.wav"
_output_video_file = "docs/temp/video_for_flag.mp4"
_left_output_file = "docs/temp/left_channel_for_flag.wav"
_right_output_file = "docs/temp/right_channel_for_flag.wav"
_output_file_5_1 = "docs/temp/5_1_audio_for_flag.wav"
_output_file_with_watermark = "docs/temp/flagged_video_with_watermark.mp4"
_extracted_frames = "docs/temp/secret_frames"


# Prepare environment.
prepare_environment("docs", "temp", "secret_frames")

# Generate the wave
wave = generate_wave(FLAG_TEXT, db_high, db_low, sample_rate, bit_duration)
save_audio_files(_flag_audio_file_high_volume, wave, sample_rate)
print("> Flag bass audio is created.")
adjust_volume(_flag_audio_file_high_volume, _flag_audio_file, 0.2)
print("> Flag bass audio volume level adjusted.")

# Get the duration of the generated wave.
_duration = get_wav_duration(_flag_audio_file)
print(f"> Duration has found: {_duration}.")

# Construct the 5.1 audio.
extract_audio(input_file, _output_sound_file, start_time, _duration)
print("> Audio is extracted from the container.")
extract_stereo_channels(_output_sound_file, _left_output_file, _right_output_file)
print("> Left and right audio is extracted from sound file.")
combine_to_5_1_audio(_left_output_file, _left_output_file, _right_output_file, _flag_audio_file, _left_output_file, _right_output_file, _output_file_5_1)
print("> The sound combined into 5.1 channels.")

# Construct the new video.
extract_video(input_file, _output_video_file, start_time, _duration)
print("> Video is extracted from the container.")
extract_frames_from_video(_output_video_file, _extracted_frames)
print("> Video frames are extracted from the video.")
watermark_frames(_extracted_frames,
                 "Have you checked the sound information? I bet the flag is there. I would look for the meaning of 5.1. :)",
                 30,
                 1800
                )
print("> Video frames are marked.")
create_video_from_frames(_extracted_frames, _output_file_with_watermark)
print("> Video is created from frames.")

# Combine the video and audio.
combine_video_with_audio(_output_file_with_watermark, _output_file_5_1, output_file)
print("> Video and audio are combined.")
print("> Challenge is created.")
