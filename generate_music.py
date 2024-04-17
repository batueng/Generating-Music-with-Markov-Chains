import numpy as np
import os
import xml.etree.ElementTree as ET
from midiutil import MIDIFile

switcher = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
    }

def extract_data(file):
    res = []
    root = ET.parse(file).getroot()

    # Part to measure to note to pitch to step
    for measure in root.find("part").findall("measure"):
        for note in measure.findall("note"):
            try:
                res.append(note.find("pitch").find("step").text)
            except:
                continue
    return res

def build_matrix_and_initial(note_list):
    transition_matrix = np.zeros((7,7))
    for i, note in enumerate(note_list):
        if i == len(note_list)-1 or note_list[i+1] == -1 or note == -1:
            continue
        transition_matrix[ord(note)-ord('A')][ord(note_list[i+1]) - ord('A')] += 1

    for i, row in enumerate(transition_matrix):
        s = sum(row)
        if s == 0:
            continue
        for j, elem in enumerate(row):
            transition_matrix[i][j] = elem/s
    
    return transition_matrix

def get_pitch(step):
    octave = 5
    base_octave_val = 12*octave + 24
    note_val = base_octave_val + switcher[step]
    return note_val

def create_midi(song):
    track    = 0
    channel  = 0
    time     = 0.0
    duration = 0.5
    tempo    = 80
    volume   = 100
    output_midi = MIDIFile(1)
    output_midi.addTempo(track, time, tempo)
    output_midi.addProgramChange(track, channel, time, 40)

    time = 0.0
    for step in song:
        duration = float(1)
        pitch = get_pitch(step)
        output_midi.addNote(track, channel, pitch, time, duration, volume)
        time += duration

    with open("music.mid", "wb") as output_file:
        output_midi.writeFile(output_file)

def main():
    files = ["files/"+file for file in os.listdir("files/") if "musicxml" in file and "py" not in file]
    note_list = []
    for file in files:
        note_list.extend(extract_data(file))
        note_list.append(-1)

    song = []
    transition_matrix = build_matrix_and_initial(note_list)
    next_state = np.random.rand(7).T
    next_state /= np.sum(next_state)
    for _ in range(25):
        max_prob = 0
        max_prob_idx = 0
        for j, prob in enumerate(next_state):
            if prob > max_prob:
                max_prob_idx = j
                max_prob = prob
        song.append(chr(ord('A')+max_prob_idx))
        next_state = next_state @ transition_matrix

    print(song)
    create_midi(song)

if __name__=="__main__":
    main()
