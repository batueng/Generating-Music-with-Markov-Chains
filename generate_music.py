import numpy as np
import os
import xml.etree.ElementTree as ET
from midiutil import MIDIFile
import random


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
    octave = 2
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
    output_midi.addProgramChange(track, channel, time, 0)

    time = 0.0
    for step in song:
        duration = float(1)
        pitch = get_pitch(step)
        output_midi.addNote(track, channel, pitch, time, duration, volume)
        time += duration

    with open("music.mid", "wb") as output_file:
        output_midi.writeFile(output_file)

def simulate_distribution_np(probabilities):
    # Step 1: Normalize probabilities
    probabilities = np.array(probabilities)
    normalized_probabilities = probabilities / np.sum(probabilities)
    
    # Step 2: Generate a random number between 0 and 1
    rand_num = np.random.rand()
    
    # Step 3: Find the index where cumulative probability exceeds the random number
    cumulative_prob = np.cumsum(normalized_probabilities)
    selected_index = np.argmax(cumulative_prob >= rand_num)
    
    return selected_index

def main():
    files = ["files/"+file for file in os.listdir("files/")]
    note_list = []
    for file in files:
        note_list.extend(extract_data(file))
        note_list.append(-1)

    song = []
    transition_matrix = build_matrix_and_initial(note_list)
    next_state = np.random.rand(7).T
    next_state /= np.sum(next_state)
    for _ in range(30):
        idx = simulate_distribution_np(next_state)
        song.append(chr(ord('A')+idx))
        next_state = np.zeros(7)
        next_state[idx] = 1
        next_state = next_state @ transition_matrix

    print(song)
    create_midi(song)

if __name__=="__main__":
    main()
