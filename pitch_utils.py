"""
pitch_utils.py
Pitch detection using librosa's YIN algorithm.
Returns: frequency (Hz), note name, cents deviation, error string.
"""

import numpy as np
import librosa

from instruments import INSTRUMENT_RANGES

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]


def freq_to_note_cents(frequency: float):
    """
    Convert a frequency in Hz to (note_name_with_octave, cents_deviation).
    cents > 0 → sharp, cents < 0 → flat.
    """
    if frequency <= 0:
        return None, 0.0

    # A4 = 440 Hz = MIDI 69
    midi_float = 69 + 12 * np.log2(frequency / 440.0)
    midi_round = round(midi_float)
    cents = (midi_float - midi_round) * 100.0

    octave   = (midi_round // 12) - 1
    note_idx = midi_round % 12
    note_name = NOTE_NAMES[note_idx] + str(octave)

    return note_name, cents


def detect_pitch_and_note(audio_path: str, instrument: str):
    """
    Load audio, run YIN pitch detection, return summary statistics.

    Returns
    -------
    frequency   : float  – median dominant frequency (Hz)
    note        : str    – e.g. "A4"
    cents       : float  – deviation from perfect pitch
    accuracy    : float  – % of voiced frames within ±20 cents
    consistency : float  – 0-100, inverse of pitch std-dev
    all_notes   : list   – [(note_str, count), ...] sorted by freq
    error       : str|None
    """
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
    except Exception as e:
        return None, None, None, None, None, None, f"Could not load audio: {e}"

    # Normalise
    if np.max(np.abs(y)) > 0:
        y = librosa.util.normalize(y)

    # YIN pitch detection — returns pitch per frame
    lo, hi = INSTRUMENT_RANGES.get(instrument, (60, 2000))
    try:
        f0 = librosa.yin(y, fmin=max(50, lo * 0.8), fmax=min(4500, hi * 1.2), sr=sr)
    except Exception as e:
        return None, None, None, None, None, None, f"Pitch detection failed: {e}"

    # Keep only voiced (non-zero) pitches
    voiced = f0[f0 > 20]

    if len(voiced) == 0:
        return None, None, None, None, None, None, \
            "No clear pitch detected. Try playing a single sustained note."

    # Filter to instrument range with 20% tolerance
    in_range = voiced[(voiced >= lo * 0.8) & (voiced <= hi * 1.2)]
    if len(in_range) == 0:
        median_f = float(np.median(voiced))
        return median_f, None, None, None, None, None, \
            f"Pitch ({median_f:.1f} Hz) is outside the expected range for {instrument}."

    # --- Dominant frequency via histogram of notes ---
    note_counts: dict = {}
    cents_by_note: dict = {}

    for f in in_range:
        n, c = freq_to_note_cents(float(f))
        if n is None:
            continue
        note_counts[n]  = note_counts.get(n, 0) + 1
        cents_by_note.setdefault(n, []).append(c)

    if not note_counts:
        return None, None, None, None, None, None, "No mappable pitches found."

    # Dominant note = most frequent
    dominant_note = max(note_counts, key=note_counts.__getitem__)
    dominant_cents_list = cents_by_note[dominant_note]
    dominant_cents = float(np.median(dominant_cents_list))

    # Dominant frequency (median of all pitches mapping to dominant note)
    dom_freqs = [f for f in in_range
                 if freq_to_note_cents(float(f))[0] == dominant_note]
    dominant_freq = float(np.median(dom_freqs)) if dom_freqs else float(np.median(in_range))

    # --- Accuracy: % of frames within ±20 cents of their nearest semitone ---
    all_cents = [freq_to_note_cents(float(f))[1] for f in in_range]
    in_tune_count = sum(1 for c in all_cents if abs(c) <= 20)
    accuracy = round(in_tune_count / len(all_cents) * 100, 1)

    # --- Consistency: inverse of std-dev of cents (capped at 100) ---
    std_dev = float(np.std(all_cents)) if len(all_cents) > 1 else 0.0
    consistency = max(0.0, round(100.0 - std_dev * 1.4, 1))

    # --- All detected notes ranked ---
    all_notes = sorted(note_counts.items(), key=lambda x: x[1], reverse=True)

    return (
        round(dominant_freq, 2),
        dominant_note,
        round(dominant_cents, 2),
        accuracy,
        consistency,
        all_notes[:8],
        None,   # no error
    )
