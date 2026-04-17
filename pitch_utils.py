"""
pitch_utils.py
Pitch detection using librosa's YIN algorithm.
"""

import numpy as np
import librosa

from instruments import INSTRUMENT_RANGES

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]


def freq_to_note_cents(frequency: float):
    if frequency <= 0:
        return None, 0.0

    midi_float = 69 + 12 * np.log2(frequency / 440.0)
    midi_round = round(midi_float)
    cents = (midi_float - midi_round) * 100.0

    octave = (midi_round // 12) - 1
    note_idx = midi_round % 12
    note_name = NOTE_NAMES[note_idx] + str(octave)

    return note_name, cents


def detect_pitch_and_note(audio_path: str, instrument: str):

    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
    except Exception as e:
        return None, None, None, None, None, None, f"Could not load audio: {e}"

    if np.max(np.abs(y)) > 0:
        y = librosa.util.normalize(y)

    lo, hi = INSTRUMENT_RANGES.get(instrument, (60, 2000))

    # adjust range slightly for real-world input (especially voice)
    fmin = max(50, lo * 0.75)
    fmax = min(4500, hi * 1.25)

    try:
        f0 = librosa.yin(y, fmin=fmin, fmax=fmax, sr=sr)
    except Exception as e:
        return None, None, None, None, None, None, f"Pitch detection failed: {e}"

    voiced = f0[f0 > 30]

    if len(voiced) == 0:
        return None, None, None, None, None, None, \
            "No clear pitch detected. Try a steady note."

    in_range = voiced[(voiced >= lo * 0.75) & (voiced <= hi * 1.25)]

    if len(in_range) == 0:
        median_f = float(np.median(voiced))
        return median_f, None, None, None, None, None, \
            f"Pitch ({median_f:.1f} Hz) is outside expected range for {instrument}."

    note_counts = {}
    cents_by_note = {}

    for f in in_range:
        n, c = freq_to_note_cents(float(f))
        if n is None:
            continue

        note_counts[n] = note_counts.get(n, 0) + 1
        cents_by_note.setdefault(n, []).append(c)

    if not note_counts:
        return None, None, None, None, None, None, "No valid notes detected."

    dominant_note = max(note_counts, key=note_counts.get)
    dominant_cents = float(np.median(cents_by_note[dominant_note]))

    dom_freqs = [
        f for f in in_range
        if freq_to_note_cents(float(f))[0] == dominant_note
    ]
    dominant_freq = float(np.median(dom_freqs)) if dom_freqs else float(np.median(in_range))

    all_cents = [freq_to_note_cents(float(f))[1] for f in in_range]
    in_tune_count = sum(1 for c in all_cents if abs(c) <= 20)
    accuracy = round(in_tune_count / len(all_cents) * 100, 1)

    std_dev = float(np.std(all_cents)) if len(all_cents) > 1 else 0.0
    consistency = max(0.0, round(100.0 - std_dev * 1.4, 1))

    all_notes = sorted(note_counts.items(), key=lambda x: x[1], reverse=True)

    return (
        round(dominant_freq, 2),
        dominant_note,
        round(dominant_cents, 2),
        accuracy,
        consistency,
        all_notes[:8],
        None,
    )
