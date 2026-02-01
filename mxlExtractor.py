import csv
import os
from pathlib import Path
from music21 import converter, note, chord

# 1. Setup Filepaths
file_path = 'Songs\\the-avengers-theme-song-check-my-new-version.mxl'
base_output = "output"
sub_folder = Path(file_path).stem + "_data"
output_dir = os.path.join(base_output, sub_folder)
os.makedirs(output_dir, exist_ok=True)

# 2. Load the Score
print(f"Loading {file_path}...")
score = converter.parse(file_path)

# 3. Iterate through Parts
for part in score.parts:
    # Get instrument name and sanitize it for a filename
    raw_name = part.partName if part.partName else "Unknown_Instrument"
    clean_name = "".join([c for c in raw_name if c.isalnum() or c in (' ', '_')]).rstrip()
    filename = os.path.join(output_dir, f"{clean_name.replace(' ', '_')}.csv")
    
    print(f"Generating: {filename}")
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Measure', 'Beat', 'Type', 'Pitch/Content', 'Duration_QuarterNotes'])
        
        # .notesAndRests captures Notes, Chords, and Rests
        for element in part.recurse().notesAndRests:
            m_num = element.measureNumber
            beat = element.beat
            duration = element.duration.quarterLength
            
            if isinstance(element, note.Note):
                content = element.pitch.nameWithOctave
                item_type = 'Note'
            elif isinstance(element, chord.Chord):
                content = ";".join([str(p.nameWithOctave) for p in element.pitches])
                item_type = 'Chord'
            elif isinstance(element, note.Rest):
                content = 'REST'
                item_type = 'Rest'
            else:
                continue
                
            writer.writerow([m_num, beat, item_type, content, duration])

print(f"\nSuccess! All files are saved in the directory: '{output_dir}'")