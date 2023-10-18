from utils_dir.flag_generator import FlagSoundGenerator
from utils_dir.ffmpeg_operations import FFmpegOperations
from utils_dir.audio_toolbox import AudioToolbox
from utils_dir.video_toolbox import VideoToolbox

class ChallengeGenerator:
    INTERFILES = {
        "flag_audio_file_high_volume": "tmp/flag_audio_high_vol.wav",
        "flag_audio_file": "tmp/flag_audio.wav",
        "output_file_5_1": "tmp/5_1_audio_with_flag.wav",
        "output_file_with_watermark": "tmp/video_file_with_hint.mp4",
    }

    def __init__(self, flag: str, input_multimedia: str):
        self._flag = flag
        self._input_multimedia_container = input_multimedia
        self._settings = {
            "multimedia_start_after_s": 14,
            "sample_rate_hz": 48000,
            "bit_duration_s": 1,
            "amp_high_bass_db": 20,
            "amp_low_bass_db": -20,
            "scale_bass_volume_ratio": 0.2,
        }
    
    def set_settings(self,
                     multimedia_start_after_s: int | None = None,
                     sample_rate_hz: int | None = None,
                     bit_duration_s: int | None = None,
                     amp_high_bass_db: int | None = None,
                     amp_low_bass_db: int | None = None) -> None:
        if multimedia_start_after_s is not None:
            self._settings["multimedia_start_after_s"] = multimedia_start_after_s
        if sample_rate_hz is not None:
            self._settings["sample_rate_hz"] = sample_rate_hz
        if bit_duration_s is not None:
            self._settings["bit_duration_s"] = bit_duration_s
        if amp_high_bass_db is not None:
            self._settings["amp_high_bass_db"] = amp_high_bass_db
        if amp_low_bass_db is not None:
            self._settings["amp_low_bass_db"] = amp_low_bass_db

    def prepare_multimedia(self, hint_image: str, output_multimedia_loc: str, start_time: int) -> None:
        # Generate the flag encoded bass sound.
        FlagSoundGenerator.generate(
            self._flag,
            self.INTERFILES["flag_audio_file_high_volume"],
            self._settings["amp_high_bass_db"],
            self._settings["amp_low_bass_db"],
            self._settings["sample_rate_hz"],
            self._settings["bit_duration_s"]
        )
        FFmpegOperations.adjust_volume(
            self.INTERFILES["flag_audio_file_high_volume"],
            self.INTERFILES["flag_audio_file"],
            self._settings["scale_bass_volume_ratio"]
        )
        duration = AudioToolbox.get_wav_duration(self.INTERFILES["flag_audio_file"])
        
        # Construct the elements.
        AudioToolbox.construct_5_1_audio(
            self._input_multimedia_container,
            start_time,
            duration,
            self.INTERFILES["flag_audio_file"],
            self.INTERFILES["output_file_5_1"]
        )
        VideoToolbox.construct_video_within_hint_on_top(
            self._input_multimedia_container,
            start_time,
            duration,
            hint_image,
            self.INTERFILES["output_file_with_watermark"]
        )

        # Combine the elements into one container.
        FFmpegOperations.combine_video_with_audio(self.INTERFILES["output_file_with_watermark"], self.INTERFILES["output_file_5_1"], output_multimedia_loc)