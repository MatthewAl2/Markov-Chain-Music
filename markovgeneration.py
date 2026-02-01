import csv
import os
import random
from pathlib import Path
from collections import defaultdict

# 1. Setup Directories
input_base = "output"
output_base = "melodies"

# 2. Markov Logic Functions
def build_chain(csv_path, order=2):
    chain = defaultdict(list)
    sequence = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sequence.append(row['Pitch/Content'])
            
    if len(sequence) <= order:
        return None, []

    for i in range(len(sequence) - order):
        state = tuple(sequence[i : i + order])
        next_note = sequence[i + order]
        chain[state].append(next_note)
        
    return chain, sequence

def generate_sequence(chain, all_notes, order=2, length=50):
    if not chain:
        return ["Insufficient Data"]
        
    # Start with a random sequence from the original to ensure variety
    start_idx = random.randint(0, len(all_notes) - order - 1)
    current_state = tuple(all_notes[start_idx : start_idx + order])
    result = list(current_state)

    for _ in range(length):
        options = chain.get(current_state)
        
        if not options:
            # Dead end? Pick a new random state to keep going
            new_start = random.choice(list(chain.keys()))
            current_state = new_start
            options = chain[current_state]
            
        next_note = random.choice(options)
        result.append(next_note)
        current_state = tuple(result[-order:])
        
    return result

# 3. Process all subfolders in "output"
if not os.path.exists(input_base):
    print(f"Error: Base directory '{input_base}' not found.")
else:
    for song_folder in os.listdir(input_base):
        input_path = os.path.join(input_base, song_folder)
        print(f"Processing folder: {input_path}")
        
        if os.path.isdir(input_path):
            # Create corresponding folder in 'melodies'
            target_dir = os.path.join(output_base, song_folder.replace("_data", "_generated"))
            os.makedirs(target_dir, exist_ok=True)
            print(f"Saving generated melodies to: {target_dir}")
            
            # Process each instrument CSV
            for csv_file in os.listdir(input_path):
                if csv_file.endswith(".csv"):
                    file_path = os.path.join(input_path, csv_file)
                    
                    # Build and Generate
                    order_val = 2
                    chain, full_seq = build_chain(file_path, order=order_val)
                    new_melody = generate_sequence(chain, full_seq, order=order_val, length=100)
                    
                    # Save the new melody
                    output_file = os.path.join(target_dir, f"gen_{csv_file}")
                    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Sequence_Step', 'Pitch_Content'])
                        for idx, note in enumerate(new_melody):
                            writer.writerow([idx, note])
                            
            print(f"Finished generating melodies for: {song_folder}")

print(f"\nAll generated melodies saved in: {output_base}")