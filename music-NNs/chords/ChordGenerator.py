from music21 import *
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM


class ChordGenerator:
    """
    ChordGenerator is a class for creating recurrent LSTM NN for reading music data and creating chord progressions.
    """
    def __init__(self):

    def process_music_data(self, path):
        """
        Parses music data, determines chord progressions and converts data to usable format to train NN
        :param path: path where music file is located
        :return: list of chords, broken up by measure, in format of char sequence based on pitch value
        """
        song_data = converter.parse(path)

        song_chords = song_data.chordify()
        song_chords.show()

        return_list = [[]]
        for m in song_chords.recurse().getElementsByClass('Measure'):
            current_measure = []
            for c in m.recurse().getElementsByClass('Chord'):
                if c.offset == 0.0 or c.offset == 2.0:
                    # TODO: transpose so that every song is the same root note
                    print(c.root().unicodeName + " " + c.quality)
                    pitch_numbers = ""
                    for n in c.notes():
                        # TODO: fix this to be properly formatted
                        pitch_numbers = pitch_numbers + n.pitch.pitchClassString
                    current_measure.append(pitch_numbers)
            return_list.append(current_measure)

        return return_list

    def generate_model(self):
        return


