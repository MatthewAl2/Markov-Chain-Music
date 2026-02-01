from music21 import converter

# Load the file
score = converter.parse('my_song.xml')

# Accessing data
for part in score.parts:
    print(f"Part: {part.partName}")
    for measure in part.measures(1, 5):  # First 5 measures
        for note in measure.notes:
            print(f"Note: {note.pitch.nameWithOctave} Duration: {note.duration.quarterLength}")

# Show the score in notation software (like MuseScore)
# score.show()