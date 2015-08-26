#!/usr/bin/env python
import pygame
import time
import pygame.midi
import random 

import signal
import sys


pygame.midi.init()
device = pygame.midi.get_default_output_id()
print device

player= pygame.midi.Output(device)
player.set_instrument(11,1)
player.set_instrument(12,2)
player.set_instrument(58,3)


minor=[0,3,7,0]
major=[0,4,7,0]
major7=[0,4,7,11]
dom7=[0,4,7,10]
minor7=[0,3,7,10]
minormaj7=[0,3,7,11]
dimmaj7=[0,3,6,11]

start_note = 60
current_note = start_note

tempo = 1200
ratio = 60.0 / tempo

iterations = 0


def play(notes, beats):
    for i in range(len(notes)):
        player.note_on(notes[i], 127,1)
    time.sleep(beats * ratio)
    for i in range(len(notes)):
        player.note_off(notes[i], 127,1)


def arp(base,ints):
    for n in ints:
        go([base]+n)

def chord_on(base, ints, chan):
    player.note_on(base,127,chan)
    player.note_on(base+ints[1],127,chan)
    player.note_on(base+ints[2],127,chan)
    player.note_on(base+ints[3],127,chan)

def chord_off(base,ints, chan):
    player.note_off(base,127,chan)
    player.note_off(base+ints[1],127,chan)
    player.note_off(base+ints[2],127,chan)
    player.note_off(base+ints[3],127,chan)

def all_chords_off(base, chan):
    chord_off(base, dimmaj7, chan)
    chord_off(base, minormaj7, chan)
    chord_off(base, minor7, chan)
    chord_off(base, major7, chan)
    chord_off(base, minor, chan)
    chord_off(base, dom7, chan)
    chord_off(base, major, chan)

def end():
    pygame.midi.quit()
    pygame.quit()


def play_get(start_note):
    return [[start_note+4],[start_note+7],[start_note-2],[start_note+random.randint(0,4)]]


def play_post(start_note):
    return [[start_note],[start_note-3],[start_note-7]]

def play_put(start_note):
    return [[start_note+2],[start_note+4],[start_note-6]]

def play_delete(start_note):
    return [[start_note+2],[start_note-2],[start_note-3]]


def play_log(verb, length, forwared_for, agent, status):
    global current_note
    global iterations
    iterations = iterations + 1
    note_length = 1
    chord_chan = 2

    if iterations > 3:
        iterations = 0
        current_note = start_note + random.randint(-7,7)

    if (verb == "GET"):
        fragment = play_get(current_note)
    if (verb == "POST"):
        fragment = play_post(current_note)
    if (verb == "PUT"):
        fragment = play_put(current_note)
    if (verb == "DELETE"):
        fragment = play_delete(current_note)

    chord_base = current_note - 12
    if (status == 400):
        chord_chan = 3
        note_length=3
        chord_on(chord_base, minormaj7, chord_chan)
    if (status == 200):
        chord_on(chord_base, major, chord_chan)
    if (status == 304):
        chord_on(chord_base, dom7, chord_chan)
    if (status == 404):
        note_length=3
        chord_chan=3
        chord_on(chord_base, dimmaj7, chord_chan)

    current_note = fragment[-1][0]

    for i in range(len(fragment)):
        play(fragment[i],note_length)
        time.sleep(ratio)
        # TODO attenuate sleep time by content length
    
    all_chords_off(chord_base, chord_chan)


def close():
        print "closing midi"
        all_chords_off(current_note)
        player.close()
        end()


#play_log("GET",200,"10.99.100.23","stuff",200)
#play_log("POST",200,"10.99.100.23","stuff",200)
#play_log("PUT",200,"10.99.100.23","stuff",200)
#play_log("DELETE",200,"10.99.100.23","stuff",400)
#
#play_log("GET",200,"10.99.100.23","stuff",200)
#
#
#chord(60,dimmaj7)
#del player
#end()
