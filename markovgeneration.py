import csv
import os
import random
import argparse
from collections import defaultdict

# --- CLI SETUP ---
parser = argparse.ArgumentParser(description="Generate melodies using a Markov Chain with full musical events.")
parser.add_argument('--order', type=int, default=2, help='Memory length (order) of the Markov Chain.')
parser.add_argument('--length', type=int, default=100, help='Number of events to generate per file.')
parser.add_argument('--input', type=str, default='output', help='Base directory for input CSVs.')
parser.add_argument('--output', type=str, default='melodies', help='Base directory for generated files.')
args = parser.parse_args()


# --- MARKOV CHAIN BUILDER USING FULL MUSICAL EVENTS ---

def build_chain(csv_path, order):
    chain = defaultdict(list)
    sequence = []

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        required_cols = [
            "Type",
            "Pitch/Content",
            "Duration_QuarterNotes",
            "Beat"
        ]

        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column '{col}' in {csv_path}")

        # Convert each row into a musical event token
        for row in reader:
            event = (
                row["Type"],                           # Note or Rest
                row["Pitch/Content"],                  # Pitch name or REST
                float(row["Duration_QuarterNotes"]),   # Duration
                float(row["Beat"])                     # Beat position
            )
            sequence.append(event)

    if len(sequence) <= order:
        return None, []

    # Build transitions
    for i in range(len(sequence) - order):
        state = tuple(sequence[i:i + order])
        next_event = sequence[i + order]
        chain[state].append(next_event)

    return dict(chain), sequence


# --- SEQUENCE GENERATOR ---

def generate_sequence(chain, all_events, order, length):
    if not chain:
        return ["Insufficient Data"]

    # Start from learned state
    current_state = random.choice(list(chain.keys()))
    result = list(current_state)

    while len(result) < length:
        options = chain.get(current_state)

        # Dead-end fallback
        if not options:
            current_state = random.choice(list(chain.keys()))
            options = chain[current_state]

        next_event = random.choice(options)
        result.append(next_event)

        # Slide Markov window
        current_state = tuple(result[-order:])

    return result[:length]


# --- MAIN EXECUTION PIPELINE ---

input_base = args.input
output_base = args.output

print(f"Running Markov generation with order={args.order}, length={args.length}")

if not os.path.exists(input_base):
    print(f"Error: Input directory '{input_base}' not found.")
else:
    os.makedirs(output_base, exist_ok=True)

    for song_folder in os.listdir(input_base):
        input_path = os.path.join(input_base, song_folder)

        if os.path.isdir(input_path):
            target_dir = os.path.join(output_base, song_folder.replace("_data", "_generated"))
            os.makedirs(target_dir, exist_ok=True)

            print(f"\nProcessing folder: {song_folder}")

            for csv_file in os.listdir(input_path):
                if csv_file.endswith(".csv"):
                    file_path = os.path.join(input_path, csv_file)

                    chain, full_seq = build_chain(file_path, args.order)

                    if chain:
                        print(f"{csv_file} → states learned: {len(chain)}")
                    else:
                        print(f"{csv_file} → insufficient data")

                    new_melody = generate_sequence(chain, full_seq, args.order, args.length)

                    # Write generated output
                    output_file = os.path.join(target_dir, f"gen_{csv_file}")
                    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            'Sequence_Step',
                            'Type',
                            'Pitch/Content',
                            'Duration_QuarterNotes',
                            'Beat'
                        ])

                        for idx, event in enumerate(new_melody):
                            if event == "Insufficient Data":
                                writer.writerow([idx, "", "", "", ""])
                                continue

                            event_type, pitch, duration, beat = event
                            writer.writerow([idx, event_type, pitch, duration, beat])

    print(f"\nAll generated melodies saved in: {output_base}")
