from utils_dir.flag_generator import FlagSoundGenerator
from utils_dir.ffmpeg_operations import FFmpegOperations
from utils_dir.audio_toolbox import AudioToolbox
from utils_dir.video_toolbox import VideoToolbox

# Run attributes
FLAG = "FLAG-DENEME_TEST_TEST"

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

if __name__ == "__main__":
    # Generate the flag encoded bass sound.
    FlagSoundGenerator.generate(FLAG, _flag_audio_file_high_volume, db_high, db_low, sample_rate, bit_duration)
    FFmpegOperations.adjust_volume(_flag_audio_file_high_volume, _flag_audio_file, 0.2)
    duration = AudioToolbox.get_wav_duration(_flag_audio_file)
    
    # Construct the elements.
    AudioToolbox.construct_5_1_audio(input_file, start_time, duration, _flag_audio_file, _output_file_5_1)
    VideoToolbox.construct_video_within_hint_on_top(input_file, start_time, duration, hint_image, _output_file_with_watermark)

    # Combine the elements into one container.
    FFmpegOperations.combine_video_with_audio(_output_file_with_watermark, _output_file_5_1, output_file)