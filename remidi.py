import argparse
import midi
from midi import *
import os
from random import randint
import json
import sys



def get_pair(text):
    number = int(''.join(filter(str.isdigit, text)))
    l = len(str(number))
    return (number, text[l:])

def remidi(data_file, out_file, resolution=96):
    events_list = [i for i in dir(midi.events) if i.find('Event') >= 0]
    events_hash = {}
    for evt in events_list:
        events_hash[evt.lower()] = evt

    with open(data_file, 'r') as f:
        textdata = f.read().split(" ")

    pattern = midi.Pattern()
    start_index = 0

    try:
        pattern.resolution = int(textdata[0])
        start_index = 1
    except:
        pattern.resolution = resolution

    tracks = {}

    for index in range(start_index, len(textdata)):

        t = textdata[index]
        result = t

        params = {}

        tick = None
        channel = None
        data = []

        i = t.find('event') + 5

        etext = t[:i]
        ev_num, ev = get_pair(etext)
        print(ev)
        c = getattr(midi, events_hash[ev])
        t = t[i:]

        params["track"] = ev_num
        params["event"] = ev
        params["class"] = c

        if t.find('t') >= 0 and len(t) > 0:
            ttext = t[:t.find('t')]
            if len(ttext) > 0:
                params['tick'] = get_pair(ttext)[0]
                t = t[t.find('t'):]

        if t.find('c') >= 0 and len(t) > 0:
            ctext = t[:t.find('c')]
            if len(ctext) > 0:
                params['channel'] = get_pair(ctext)[0]
                t = t[t.find('c'):]

        if t.find('d') >= 0 and len(t) > 0:
            params['data'] = []
            ds = t.split('d')
            for dd in ds:
                if len(dd) > 0:
                    params['data'].append(get_pair(dd)[0])

        if ev_num not in tracks:
            tracks[ev_num] = [ params ]
        else:
            tracks[ev_num].append(params)

    keys = sorted(tracks.keys())
    for k in keys:
        trk = midi.Track()
        tname_param = None
        for pm in tracks[k]:
            if pm['class'].__name__ == 'TrackNameEvent':
                klass = pm['class']
                trk.append(TrackNameEvent(tick=pm["tick"], text='TRACK ' + str(k), data=pm["data"]))

        for pm in tracks[k]:
            if pm['class'].__name__ != 'TrackNameEvent' and pm['class'].__name__ != 'CopyrightMetaEvent':
                klass = pm['class']
                trk.append(klass(**pm))
        pattern.append(trk)
    print(pattern)

    midi.write_midifile(out_file, pattern)

def main(args):
    if args.data_file is None or args.out_file is None:
        parser.print_help()
        return 0

    remidi(args.data_file, args.out_file, args.resolution)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create midi files from data that use demidi.py syntax. More info at https://github.com/stephwag/midi-rnn')
    parser.add_argument('--datafile', metavar='-M', dest='data_file', default=None,
                       help='Path to a single data file (must be an absolute path)')

    parser.add_argument('--outfile', metavar='-O', dest='out_file', default=None, help='Output file path (must be an absolute path)')
    parser.add_argument('--resolution', metavar='-R', dest='resolution', default=96, type=int, help='Midi resolution of the out file (default: 96)')

    args = parser.parse_args()
    main(args)
    



