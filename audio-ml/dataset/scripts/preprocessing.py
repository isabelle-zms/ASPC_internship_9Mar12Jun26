import librosa
import soundfile as sf
import numpy as np
import wavfile
import tensorflow as tf

def to_mono(audio):
    # audio shape: (samples,) or (samples, channels)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)   # average L and R channels
    return audio

def resample_convertmono_normalise_audio(input_path, output_path, target_sr=16000):
    audio, sr = librosa.load(input_path, sr=target_sr, mono=True)  # librosa resamples and converts to mono automatically
    normalised_audio = audio / tf.int16.max  # normalise to [-1.0, 1.0]. Note: other types of normalisation could be used, e.g. peak normalisation or RMS normalisation
    sf.write(output_path, normalised_audio, target_sr)

# Example
resample_convertmono_normalise_audio("raw/drone/drone_001_dji.wav", "processed/drone/drone_001_dji.wav")
print(librosa.get_samplerate("raw/drone/drone_001_dji.wav")) # should print original sample rate (e.g. 44100)
print(librosa.get_samplerate("processed/drone/drone_001_dji.wav"))  # should print 16000




def split_into_clips(audio, sr, clip_duration=3.0, hop_duration=1.5):
    """
    clip_duration : length of each clip in seconds
    hop_duration  : step between clips (overlap = clip - hop)
    """
    clip_len  = int(clip_duration * sr)   # 3.0s × 16000 = 48000 samples
    hop_len   = int(hop_duration  * sr)   # 1.5s × 16000 = 24000 samples
    clips = []

    for start in range(0, len(audio) - clip_len + 1, hop_len):
        clip = audio[start : start + clip_len]
        clips.append(clip)

    return clips

# Example
# clips = split_into_clips(audio, sr=16000, clip_duration=3.0, hop_duration=1.5)
# print(f"Generated {len(clips)} clips")   # e.g. "Generated 8 clips"

# # Save each clip
# for i, clip in enumerate(clips):
#     sf.write(f"processed/drone/drone_001_clip{i:02d}.wav", clip, 16000)