import librosa
import soundfile as sf
import numpy as np
from pathlib import Path


def to_mono(audio):
    # audio shape: (samples,) or (samples, channels)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)   # average L and R channels
    return audio


def resample_convertmono_normalise_audio(input_path, output_path, target_sr=16000):
    audio, sr = librosa.load(input_path, sr=target_sr, mono=True)  # librosa resamples and converts to mono automatically
    normalised_audio = audio / np.iinfo(np.int16).max  # normalise to [-1.0, 1.0]. Note: other types of normalisation could be used, e.g. peak normalisation or RMS normalisation
    sf.write(output_path, normalised_audio, target_sr)

# Example
# resample_convertmono_normalise_audio("raw/drone/drone_001_dji.wav", "processed/drone/drone_001_dji.wav")
# print(librosa.get_samplerate("raw/drone/drone_001_dji.wav")) # should print original sample rate (e.g. 44100)
# print(librosa.get_samplerate("processed/drone/drone_001_dji.wav"))  # should print 16000


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


def process_directory(
    input_dir,
    output_dir,
    target_sr=16000,
    do_split=False,
    clip_duration=3.0,
    hop_duration=1.5,
):
    """
    Iterates over all .wav files in input_dir (recursively), applies
    resample_convertmono_normalise_audio to each, and optionally splits
    each processed file into overlapping clips.
    """
    input_dir  = Path(input_dir)
    output_dir = Path(output_dir)
 
    wav_files = sorted(input_dir.rglob("*.wav"))
    if not wav_files:
        print(f"No .wav files found in '{input_dir}'.")
        return
 
    print(f"Found {len(wav_files)} .wav file(s) in '{input_dir}'.\n")
 
    for wav_path in wav_files:
        # Mirror the sub-directory structure inside output_dir
        relative   = wav_path.relative_to(input_dir)
        out_path   = output_dir / relative
        out_path.parent.mkdir(parents=True, exist_ok=True)
 
        print(f"  Processing: {wav_path}")
 
        # --- Resample / mono / normalise ---
        resample_convertmono_normalise_audio(str(wav_path), str(out_path), target_sr)
        print(f"  → Saved processed file: {out_path}")
 
        # --- Optional clip splitting ---
        if do_split:
            audio, _ = librosa.load(str(out_path), sr=target_sr, mono=True)
            clips = split_into_clips(audio, target_sr, clip_duration, hop_duration)
 
            if not clips:
                print(f"  → File too short to produce any clips — skipped splitting.")
            else:
                clip_dir  = out_path.parent / out_path.stem  # subfolder per source file
                clip_dir.mkdir(parents=True, exist_ok=True)
                for i, clip in enumerate(clips):
                    clip_path = clip_dir / f"{out_path.stem}_clip{i:03d}.wav"
                    sf.write(str(clip_path), clip, target_sr)
                print(f"  → Split into {len(clips)} clip(s) → {clip_dir}/")
 
        print()
 
    print("Done.")

# Example usage (CWD: audio-ml):
process_directory(
    input_dir="dataset/raw",
    output_dir="dataset/processed",
    target_sr=16000,
    do_split=True,
    clip_duration=3.0,
    hop_duration=1.5,
)