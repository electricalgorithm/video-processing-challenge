from utils import extract_audio, extract_video, extract_stereo_channels, combine_to_5_1_audio
from utils import generate_wave, text_to_binary, save_audio_files, get_wav_duration, adjust_volume
from utils import extract_frames_from_video, insert_images_into_frames, create_video_from_frames
from utils import prepare_environment, combine_video_with_audio

# Flag text for the challenge.
FLAG_TEXT = text_to_binary("FLAG-AMPMOD_ON_LFE")

# Challenge Settings
sample_rate = 48000                                         # Sample rate (Hz)
bit_duration = 1                                            # Duration of each bit (seconds)
db_high = 20                                                # Amplitude for '1' bits (in dB)
db_low = -20                                                # Amplitude for '0' bits (in dB)
start_time = 14                                             # Trimming start in seconds.
input_file = "docs/bbb_sunflower_1080p_30fps_normal.mp4"    # The video to encode flag into.
hint_image = "docs/hint_image.png"                          # The hint image to place onto frames.
output_file = "challenge_video.mp4"                         # The output file.

# Internal files.
_flag_audio_file = "tmp/flag_audio.wav"
_flag_audio_file_high_volume = "tmp/flag_audio_high_vol.wav"
_output_sound_file = "tmp/video_sound.wav"
_output_sound_high_volume_file = "tmp/video_sound_high_vol.wav"
_left_output_file = "tmp/video_sound_left_channel.wav"
_right_output_file = "tmp/video_sound_right_channel.wav"
_output_file_5_1 = "tmp/5_1_audio_with_flag.wav"
_output_video_file = "tmp/video_file.mp4"
_output_file_with_watermark = "tmp/video_file_with_hint.mp4"
_extracted_frames = "tmp/extracted_frames"


# Prepare environment.
prepare_environment("docs", "tmp", "extracted_frames")

# Generate the wave
print("> Creating flag bass audio.")
wave = generate_wave(FLAG_TEXT, db_high, db_low, sample_rate, bit_duration)
save_audio_files(_flag_audio_file_high_volume, wave, sample_rate)
print("> Decreasing flag bass audio volume level.")
adjust_volume(_flag_audio_file_high_volume, _flag_audio_file, 0.2)

print("#######################################################")
print("############ FLAG BASS AUDIO IS CREATED ###############")
print("#######################################################")

# Get the duration of the generated wave.
_duration = get_wav_duration(_flag_audio_file)
print(f"> Duration has found: {_duration}.")

# Construct the 5.1 audio.
print("> Extracting the audio from the container.")
extract_audio(input_file, _output_sound_file, start_time, _duration)
print("> Increasing audio volume level.")
adjust_volume(_output_sound_file, _output_sound_high_volume_file, 1.5)
print("> Extracting left and right audio from sound file.")
extract_stereo_channels(_output_sound_high_volume_file, _left_output_file, _right_output_file)
print("> Combining the channels with bass flag into 5.1 channels.")
combine_to_5_1_audio(_left_output_file, _left_output_file, _right_output_file, _flag_audio_file, _left_output_file, _right_output_file, _output_file_5_1)

print("#######################################################")
print("##### ORIGINAL VIDEO HAS COMBINED WITH FLAG BASS ######")
print("#######################################################")

# Construct the new video.
print("> Extracting video from the container.")
extract_video(input_file, _output_video_file, start_time, _duration)
print("> Extracting the frames from the video.")
extract_frames_from_video(_output_video_file, _extracted_frames)
print("> Placing hint image onto frames randomely.")
insert_images_into_frames(_extracted_frames, hint_image, "4x4", 30, 1800)
print("> Creating video from the new frames.")
create_video_from_frames(_extracted_frames, _output_file_with_watermark)

print("#######################################################")
print("######### VIDEO WITH HINT IMAGES IS CREATED ###########")
print("#######################################################")

# Combine the video and audio.
print("> Combining the hinted video and audio with bass flag.")
combine_video_with_audio(_output_file_with_watermark, _output_file_5_1, output_file)

print("#######################################################")
print("########### SOUND AND VIDEO HAS COMBINED ##############")
print("#######################################################")

print(f"> Challenge is created. File -> {output_file}")
