from music21 import *
import numpy as np
import keras
from keras.models import Sequential
from statistics import mode
from keras.layers import Dense, Dropout, LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
import sys


class ChordGenerator:
    """
    ChordGenerator is a class for creating recurrent LSTM NN for reading music data and creating chord progressions.
    """
    def __init__(self):
        self.model = Sequential()
        self.train_x = None
        self.train_y = None

    def process_music_data(self, path):
        """
        Parses music data, determines chord progressions and converts data to usable format to train NN
        :param path: path where music file is located
        :return: list of integers representing chords mapped based on root note and chord quality, broken up by measure
        """
        song_data = converter.parse(path)

        song_chords = song_data.chordify()
        # song_chords.show()

        return_list = []
        chord_count = [0] * 24

        for m in song_chords.recurse().getElementsByClass('Measure'):
            current_measure = []
            for c in m.recurse().getElementsByClass('Chord'):
                # Get chords on each downbeat of each measure
                if c.offset in [0.0, 1.0, 2.0, 3.0]:
                    # TODO: transpose so that every song is the same root note
                    # current process is mapping every chord on interval [0-23]
                    # Two mapping for each tone, majors evens minors odds
                    if c.quality == "minor":
                        note_mapping = 2 * c.root().pitchClass + 1
                    else:
                        note_mapping = 2 * c.root().pitchClass
                    chord_count[note_mapping] += 1
                    current_measure.append(note_mapping)

            if len(current_measure) == 0:
                fill_measure = mode(chord_count)
            else:
                fill_measure = current_measure[-1]
            while len(current_measure) < 4:
                current_measure.append(fill_measure)

            for each_chord in current_measure:
                return_list.append(each_chord)

        return return_list

    def generate_model(self):
        self.model.add(LSTM(256, input_shape=(self.train_x.shape[1], self.train_x.shape[2])))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(self.train_y.shape[1], activation='softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='adam')

        file_path = r"C:\Users\Connor\PycharmProjects\untitled\best_weights.hdf5"
        checkpoint = ModelCheckpoint(file_path, monitor='loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]

        self.model.fit(self.train_x, self.train_y, epochs=20, batch_size=16, callbacks=callbacks_list)

    def load_test_data(self, chord_data, seq_length=4):
        raw_x = []
        raw_y = []

        for i in range(0, len(chord_data) - seq_length):
            sequence_in = chord_data[i:i + seq_length]
            sequence_out = chord_data[i + seq_length]
            raw_x.append([x for x in sequence_in])
            raw_y.append(sequence_out)

        raw_x = np.reshape(raw_x, (len(raw_x), seq_length, 1))
        processed_x = raw_x / float(23)
        processed_y = np_utils.to_categorical(raw_y)

        self.train_x = processed_x
        self.train_y = processed_y

    def predict(self):
        #TODO: figure out best way to handle file name
        filename = r"C:\Users\Connor\PycharmProjects\untitled\best_weights.hdf5"
        self.model.load_weights(filename)
        self.model.compile(loss='categorical_crossentropy', optimizer='adam')

        start = np.random.randint(0, len(self.train_x) - 1)
        pattern = self.train_x[start]
        print("Seed:")
        print([self.decode(int(n)) for n in pattern])

        for i in range(32):
            x = np.reshape(pattern, (1, len(pattern), 1))
            x = x / float(len(self.train_x))
            prediction = self.model.predict(x, verbose=0)
            index = np.argmax(prediction)
            result = self.decode(index)
            seq_in = [self.decode(int(n)) for n in pattern]

            sys.stdout.write(result)
            # print(pattern)
            # print(type(pattern))
            pattern = np.append(pattern, [index])
            pattern = pattern[1:len(pattern)]
        print("\nDone.")

    @staticmethod
    def decode(number):

        chord_from_number = pitch.Pitch(number // 2).name
        if number % 2 == 1:
            chord_from_number += " minor "
        else:
            chord_from_number += " major "

        return chord_from_number
