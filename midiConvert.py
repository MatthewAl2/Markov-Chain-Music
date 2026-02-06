import pandas as pd
from music21 import stream, note, instrument


def combine_instruments(csv_files, midi_output):
    score = stream.Score()

    for instrument_name, csv_path in csv_files:
        df = pd.read_csv(csv_path)

        part = stream.Part()
        part.insert(0, instrument.fromString(instrument_name))

        current_offset = 0.0

        for _, row in df.iterrows():
            event_type = row.get("Type", "Note")
            pitch = row.get("Pitch/Content", "REST")
            duration = float(row.get("Duration_QuarterNotes", 1.0))

            # Create note or rest
            if event_type.lower() == "rest" or pitch == "REST":
                n = note.Rest(quarterLength=duration)
            else:
                n = note.Note(pitch, quarterLength=duration)

            # Place event in time
            part.insert(current_offset, n)

            # Move timeline forward
            current_offset += duration

        score.append(part)

    score.write("midi", midi_output)


# --- GENERATED MARKOV MUSIC ---
csv_files = [
    ("Clarinet", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_B_Clarinet_1.csv"),
    ("Trumpet", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_B_Trumpet_1.csv"),
    ("Trumpet", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_B_Trumpet_2.csv"),
    ("Bass", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Bass.csv"),
    ("Bassoon", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Bassoon_1.csv"),
    ("Cello", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Cello_1.csv"),
    ("Cello", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Cello_2.csv"),
    ("Glockenspiel", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Clockenspiel.csv"),
    ("Contrabass", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Contrabass_1.csv"),
    ("Contrabass", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Contrabass_2.csv"),
    ("French Horn", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_F_Horn_1.csv"),
    ("French Horn", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_F_Horn_2.csv"),
    ("Flute", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Flute_1.csv"),
    ("Percussion", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_HiHat.csv"),
    ("Oboe", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Oboe_1.csv"),
    ("Timpani", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Quads.csv"),
    ("Snare Drum", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Snare_drum.csv"),
    ("Suspended Cymbal", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Suspended_cymbal.csv"),
    ("Gong", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Tamtam.csv"),
    ("Timpani", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Timpani.csv"),
    ("Trombone", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Trombone_1.csv"),
    ("Trombone", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Trombone_2.csv"),
    ("Tuba", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Tuba.csv"),
    ("Viola", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Viola.csv"),
    ("Violin", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Violin_1.csv"),
    ("Violin", "melodies\\the-avengers-theme-song-check-my-new-version_data_generated_joint\\gen_Violin_2.csv"),
]

combine_instruments(csv_files, "full_orchestra.mid")


# --- ORIGINAL TRUE SCORE (for comparison) ---
csv_files = [
    ("Clarinet", "output\\the-avengers-theme-song-check-my-new-version_data\\B_Clarinet_1.csv"),
    ("Trumpet", "output\\the-avengers-theme-song-check-my-new-version_data\\B_Trumpet_1.csv"),
    ("Trumpet", "output\\the-avengers-theme-song-check-my-new-version_data\\B_Trumpet_2.csv"),
    ("Bass", "output\\the-avengers-theme-song-check-my-new-version_data\\Bass.csv"),
    ("Bassoon", "output\\the-avengers-theme-song-check-my-new-version_data\\Bassoon_1.csv"),
    ("Cello", "output\\the-avengers-theme-song-check-my-new-version_data\\Cello_1.csv"),
    ("Cello", "output\\the-avengers-theme-song-check-my-new-version_data\\Cello_2.csv"),
    ("Glockenspiel", "output\\the-avengers-theme-song-check-my-new-version_data\\Clockenspiel.csv"),
    ("Contrabass", "output\\the-avengers-theme-song-check-my-new-version_data\\Contrabass_1.csv"),
    ("Contrabass", "output\\the-avengers-theme-song-check-my-new-version_data\\Contrabass_2.csv"),
    ("French Horn", "output\\the-avengers-theme-song-check-my-new-version_data\\F_Horn_1.csv"),
    ("French Horn", "output\\the-avengers-theme-song-check-my-new-version_data\\F_Horn_2.csv"),
    ("Flute", "output\\the-avengers-theme-song-check-my-new-version_data\\Flute_1.csv"),
    ("Percussion", "output\\the-avengers-theme-song-check-my-new-version_data\\HiHat.csv"),
    ("Oboe", "output\\the-avengers-theme-song-check-my-new-version_data\\Oboe_1.csv"),
    ("Timpani", "output\\the-avengers-theme-song-check-my-new-version_data\\Quads.csv"),
    ("Snare Drum", "output\\the-avengers-theme-song-check-my-new-version_data\\Snare_drum.csv"),
    ("Suspended Cymbal", "output\\the-avengers-theme-song-check-my-new-version_data\\Suspended_cymbal.csv"),
    ("Gong", "output\\the-avengers-theme-song-check-my-new-version_data\\Tamtam.csv"),
    ("Timpani", "output\\the-avengers-theme-song-check-my-new-version_data\\Timpani.csv"),
    ("Trombone", "output\\the-avengers-theme-song-check-my-new-version_data\\Trombone_1.csv"),
    ("Trombone", "output\\the-avengers-theme-song-check-my-new-version_data\\Trombone_2.csv"),
    ("Tuba", "output\\the-avengers-theme-song-check-my-new-version_data\\Tuba.csv"),
    ("Viola", "output\\the-avengers-theme-song-check-my-new-version_data\\Viola.csv"),
    ("Violin", "output\\the-avengers-theme-song-check-my-new-version_data\\Violin_1.csv"),
    ("Violin", "output\\the-avengers-theme-song-check-my-new-version_data\\Violin_2.csv"),
]

combine_instruments(csv_files, "full_orchestra_true.mid")
