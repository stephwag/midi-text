import argparse
import midi
from midi import *
import os
import json
import sys
import json

def gen_vocab(tick_max, include_resolutions = False, resolutions = False):
    events = [i for i in dir(midi.events) if i.find('Event') >= 0]
    vocab = {}
    count = 0

    # tracks
    for i in range(16):
        for e in events:
            vocab[str(i) + e] = count
            count += 1

    for i in range(tick_max + 1):
        vocab[str(i) + 't'] = count
        count += 1

    # channels
    for i in range(128):
        vocab[str(i) + 'c'] = count
        count += 1

    # data array
    for i in range(128):
        vocab[str(i) + 'd'] = count
        count += 1

    # resolutions
    if include_resolutions:
        for r in resolutions:
            vocab[str(r) + 'r'] = count
            count += 1

    with open('vocab.json', 'w') as f:
        f.write(json.dumps(vocab))

    print("Generated vocab.json in {}".format(os.path.dirname(os.path.realpath('vocab.json'))))

def demidi(midi_dir, data_dir, out_dir, include_resolutions, tick_max, generate_vocab):
    midifiles = []
    for root, dirs, filenames in os.walk(midi_dir):
        for f in filenames:
            if f.endswith(".mid"):
                midifiles.append(f)

    # 96 is quarter notes, but if giving music with variing notes, do not set this.
    masterresolution = 96
    # mother 3 music is 24 (and highest tick is only 2489)
    # undertale/deltarune is 96

    biggest_tick = 0
    fff = ''
    goodticks = []
    badsongs = []
    resolutions = []
    events_blacklist = ['CopyrightMetaEvent', 'AbstractEvent', 'MetaEvent', 'MarkerEvent', 'SomethingEvent', 'CuePointEvent']

    for midifile in midifiles:
        try:
            pattern = midi.read_midifile("{}/{}".format(midi_dir, midifile))
        except:
            continue

        resolutions.append(pattern.resolution)
        count = 0
        words = []
        word = ""
        write_file = True
        for p in pattern:
            for e in p:
                if e.__class__.__name__ not in events_blacklist:
                    word = ""
                    word += str(count) + e.__class__.__name__.lower()
                    word += str(e.tick) + 't'

                    if tick_max >= 0:
                        if e.tick >= tick_max:
                            badsongs.append(midifile)
                        else:
                            goodticks.append(e.tick)

                        if e.tick > biggest_tick:
                            biggest_tick = e.tick

                    if e.__class__.__name__ not in ['InstrumentNameEvent', 'MarkerEvent', 'TrackNameEvent', 'TimeSignatureEvent', 'SetTempoEvent', 'EndOfTrackEvent', 'CopyrightMetaEvent', 'KeySignatureEvent']:
                        word += str(e.channel) + 'c'
                    else:
                        print(e)

                    for d in e.data:
                        word += str(d) + 'd'
                    words.append(word)
            count += 1

        if midifile not in badsongs or tick_max < 0:
            with open("{}/{}.txt".format(data_dir, midifile), 'w') as f:
                if include_resolutions:
                    f.write("{} {}".format(pattern.resolution, " ".join(words)))
                else:
                    f.write(" ".join(words))

        resolutions = list(set(resolutions))

        print("Largest tick found: {}\nResolutions found: {}".format(biggest_tick, resolutions))

        if generate_vocab:
            gen_vocab(biggest_tick, include_resolutions=include_resolutions, resolutions=resolutions)

def main(args):
    if args.midi_dir is None or args.data_dir is None:
        parser.print_help()
        return 0

    demidi(args.midi_dir, args.data_dir, args.include_resolutions, args.tick_max, args.generate_vocab)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Flatten midi files and generate vocab for training neural networks. More info at https://github.com/stephwag/midi-rnn')
    parser.add_argument('--mididir', metavar='-M', dest='midi_dir', default=None,
                       help='Absolute path to data directory')
    parser.add_argument('--outdir', metavar='-O', dest='data_dir', default=None,
                       help='Absolute path to output directory')

    parser.add_argument('--include-resolutions', action='store_true', dest='include_resolutions', help='Midi resolution of the out file (default: 96)')
    parser.add_argument('--vocab', dest='generate_vocab', action='store_true', help='Generate vocab (default: false)')

    parser.add_argument('--tickmax', metavar='-T', dest='tick_max', nargs=1, default=-1, type=int,
                       help='Only process midis that are less or equal to this value. The lower the value, the lower the size of the vocab (default: no max)')

    args = parser.parse_args()
    main(args)
    



