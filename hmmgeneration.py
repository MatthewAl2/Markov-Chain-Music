import os
import csv
import argparse
import numpy as np
from collections import defaultdict
from hmmlearn.hmm import CategoricalHMM
import random

# --- CLI SETUP ---
parser = argparse.ArgumentParser(description="Joint multi-instrument HMM CSV generator (CategoricalHMM)")
parser.add_argument('--states', type=int, default=8, help='Number of hidden states in HMM')
parser.add_argument('--measures', type=int, default=50, help='Number of measures to generate')
parser.add_argument('--beats_per_measure', type=float, default=4.0, help='Beats per measure')
parser.add_argument('--input', type=str, default='output', help='Base directory for input CSVs')
parser.add_argument('--output', type=str, default='melodies', help='Base directory for generated CSVs')
args = parser.parse_args()


# ------------------- HELPERS -------------------

def read_instrument_csv(csv_path):
    events = []
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            event = (
                row.get("Type", "Note"),
                row.get("Pitch/Content", "REST"),
                float(row.get("Duration_QuarterNotes", 1.0)),
                float(row.get("Measure", 1)),
                float(row.get("Beat", 1))
            )
            events.append(event)
    return events


def build_joint_sequence(instrument_csvs):
    instrument_names = list(instrument_csvs.keys())
    instrument_events = {name: read_instrument_csv(path) for name, path in instrument_csvs.items()}
    max_len = max(len(events) for events in instrument_events.values())

    joint_sequence = []
    for i in range(max_len):
        joint_state = []
        for name in instrument_names:
            events = instrument_events[name]
            if i < len(events):
                joint_state.append(events[i])
            else:
                # pad missing instruments with rests
                joint_state.append(("Rest", "REST", 1.0, 1, 1))
        joint_sequence.append(tuple(joint_state))
    return joint_sequence, instrument_names


# ------------------- ENCODING -------------------

def encode_joint_sequence(joint_sequence):
    """Map each unique joint event to a discrete integer"""
    unique_events = {}
    reverse_map = {}
    encoded_seq = []

    idx = 0
    for joint_state in joint_sequence:
        if joint_state not in unique_events:
            unique_events[joint_state] = idx
            reverse_map[idx] = joint_state
            idx += 1
        encoded_seq.append(unique_events[joint_state])

    return np.array(encoded_seq).reshape(-1, 1), unique_events, reverse_map


# ------------------- HMM TRAINING -------------------

def train_hmm(encoded_seq, n_states, n_features):
    """Train a categorical HMM on the encoded sequence"""
    model = CategoricalHMM(n_components=n_states, n_iter=500, tol=1e-4, verbose=True)
    model.n_features = n_features
    model.fit(encoded_seq)
    return model


# ------------------- GENERATION -------------------

def generate_sequence(model, reverse_map, num_measures, beats_per_measure):
    sequence = []
    total_time = 0
    max_time = num_measures * beats_per_measure

    while total_time < max_time:
        X, Z = model.sample(1)
        event_idx = int(X[0][0])
        joint_state = reverse_map[event_idx]
        sequence.append(joint_state)
        # Increment total time by the longest note in joint state
        state_duration = max(event[2] for event in joint_state)
        total_time += state_duration

    return sequence


# ------------------- CSV OUTPUT -------------------

def save_joint_csvs(result_sequence, instrument_names, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    files = {}
    writers = {}

    for name in instrument_names:
        csv_path = os.path.join(output_dir, f"gen_{name}.csv")
        f = open(csv_path, mode='w', newline='', encoding='utf-8')
        writer = csv.writer(f)
        writer.writerow(['Sequence_Step', 'Type', 'Pitch/Content', 'Duration_QuarterNotes', 'Measure', 'Beat'])
        files[name] = f
        writers[name] = writer

    for idx, joint_state in enumerate(result_sequence):
        for inst_idx, name in enumerate(instrument_names):
            event = joint_state[inst_idx]
            event_type, pitch, duration, measure, beat = event
            writers[name].writerow([idx, event_type, pitch, duration, measure, beat])

    for f in files.values():
        f.close()


# ------------------- MAIN -------------------

input_base = args.input
output_base = args.output

if not os.path.exists(input_base):
    print(f"Input directory '{input_base}' not found.")
    exit(1)

for song_folder in os.listdir(input_base):
    folder_path = os.path.join(input_base, song_folder)
    if not os.path.isdir(folder_path):
        continue

    print(f"\nProcessing folder: {song_folder}")

    # Map instrument name -> CSV path
    instrument_csvs = {}
    for csv_file in os.listdir(folder_path):
        if csv_file.endswith(".csv"):
            inst_name = os.path.splitext(csv_file)[0]
            instrument_csvs[inst_name] = os.path.join(folder_path, csv_file)

    joint_sequence, instrument_names = build_joint_sequence(instrument_csvs)
    encoded_seq, event_map, reverse_map = encode_joint_sequence(joint_sequence)

    # Train HMM
    model = train_hmm(encoded_seq, args.states, n_features=len(event_map))
    print(f"HMM trained with {args.states} hidden states and {len(event_map)} unique joint events.")

    # Generate new sequence
    new_sequence = generate_sequence(model, reverse_map, args.measures, args.beats_per_measure)

    # Save per-instrument CSVs
    target_dir = os.path.join(output_base, song_folder + "_generated_hmm")
    save_joint_csvs(new_sequence, instrument_names, target_dir)
    print(f"CSV files saved in: {target_dir}")

print("\nAll sequences processed using HMM.")
