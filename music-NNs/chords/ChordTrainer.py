from music21 import *


test = converter.parse(r'C:\Users\Connor\Downloads\ColdPlay-_Viva_la_vida.mxl')

test_chords = test.chordify()
# test_chords.show()
count = 0
for m in test_chords.recurse().getElementsByClass('Measure'):
    for c in m.recurse().getElementsByClass('Chord'):
        if c.offset == 0.0 or c.offset == 2.0:
            # normalOrder = c.normalOrder
            # firstPitch = normalOrder[0]
            # c = chord.Chord([(pc - firstPitch) % 12 for pc in normalOrder])
            print(c.root().unicodeName + " " + c.quality)
