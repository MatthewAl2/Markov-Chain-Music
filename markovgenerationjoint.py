import csv
import os
import random
import argparse
from collections import defaultdict

# --- CLI SETUP ---
parser = argparse.ArgumentParser(description="Joint multi-instrument Markov CSV generator")
parser.add_argument('--order', type=int, default=2, help='Memory length (order) of the Markov Chain')
parser.add_argument('--length', type=int, default=100, help='Number of events to generate (ignored if --measures is set)')
parser.add_argument('--measures', type=int, default=None, help='Number of measures to generate (overrides --length if set)')
parser.add_argument('--beats_per_measure', type=int, default=4, help='Number of beats per measure (default=4)')
parser.add_argument('--input', type=str, default='output', help='Base directory for input CSVs')
parser.add_argument('--output', type=str, default='melodies', help='Base directory for generated CSVs')
args = parser.parse_args()


# ------------------- MARKOV HELPERS -------------------

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


def build_joint_chain(joint_sequence, order):
    chain = defaultdict(list)
    if len(joint_sequence) <= order:
        return None
    for i in range(len(joint_sequence) - order):
        state = tuple(joint_sequence[i:i+order])
        next_state = joint_sequence[i + order]
        chain[state].append(next_state)
    return dict(chain)


# ------------------- GENERATION -------------------

def generate_joint_sequence(chain, order, length):
    """Generate sequence by fixed number of events"""
    if not chain:
        return ["Insufficient Data"]
    current_state = random.choice(list(chain.keys()))
    result_sequence = list(current_state)
    while len(result_sequence) < length:
        options = chain.get(current_state)
        if not options:
            current_state = random.choice(list(chain.keys()))
            options = chain[current_state]
        next_state = random.choice(options)
        result_sequence.append(next_state)
        current_state = tuple(result_sequence[-order:])
    return result_sequence[:length]


def generate_joint_sequence_by_measures(chain, order, num_measures, beats_per_measure):
    """Generate sequence up to a certain number of measures"""
    if not chain:
        return ["Insufficient Data"]

    current_state = random.choice(list(chain.keys()))
    result_sequence = list(current_state)

    # Track total absolute time in quarter notes
    total_time = sum(max(event[2] for event in state) for state in current_state)  # sum longest note per joint state
    max_time = num_measures * beats_per_measure

    while total_time < max_time:
        options = chain.get(current_state)
        if not options:
            current_state = random.choice(list(chain.keys()))
            options = chain[current_state]
        next_state = random.choice(options)
        result_sequence.append(next_state)
        state_duration = max(event[2] for event in next_state)
        total_time += state_duration
        current_state = tuple(result_sequence[-order:])

    return result_sequence


# ------------------- CSV OUTPUT -------------------

def save_joint_csvs(result_sequence, instrument_names, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    files = {}
    writers = {}

    # Initialize CSVs for each instrument
    for name in instrument_names:
        csv_path = os.path.join(output_dir, f"gen_{name}.csv")
        f = open(csv_path, mode='w', newline='', encoding='utf-8')
        writer = csv.writer(f)
        writer.writerow(['Sequence_Step', 'Type', 'Pitch/Content', 'Duration_QuarterNotes', 'Measure', 'Beat'])
        files[name] = f
        writers[name] = writer

    # Write events per instrument
    for idx, joint_state in enumerate(result_sequence):
        for inst_idx, name in enumerate(instrument_names):
            event = joint_state[inst_idx]
            event_type, pitch, duration, measure, beat = event
            writers[name].writerow([idx, event_type, pitch, duration, measure, beat])

    # Close all files
    for f in files.values():
        f.close()


# ------------------- MAIN EXECUTION -------------------

input_base = args.input
output_base = args.output

if not os.path.exists(input_base):
    print(f"Error: Input directory '{input_base}' not found.")
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
    chain = build_joint_chain(joint_sequence, args.order)
    print(f"Joint chain states learned: {len(chain)}")

    # Generate either by measures or by length
    if args.measures:
        new_sequence = generate_joint_sequence_by_measures(chain, args.order,
                                                           args.measures,
                                                           args.beats_per_measure)
    else:
        new_sequence = generate_joint_sequence(chain, args.order, args.length)

    # Output CSVs per instrument
    target_dir = os.path.join(output_base, song_folder + "_generated_joint")
    save_joint_csvs(new_sequence, instrument_names, target_dir)
    print(f"CSV files saved in: {target_dir}")

print("\nAll joint melodies processed and saved as CSVs.")
