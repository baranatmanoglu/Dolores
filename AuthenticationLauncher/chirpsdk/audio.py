#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2017, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

import struct
import math
import wave

import pyaudio

from .constants import *
from .protocol import Protocol


class AudioSession(object):
    """ Plays audio to sound hardware from an AudioGenerator object. """

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.generator = AudioGenerator()
        self.stream = self.pyaudio.open(format=pyaudio.paInt16,
                                        rate=int(CHIRP_SAMPLERATE),
                                        channels=1,
                                        output=True)
        self.set_protocol()

    def set_protocol(self, protocol=None):
        self.protocol = protocol or Protocol()
        self.generator.set_protocol(self.protocol)

    def play(self, encoded):
        """ Play an encoded message, which must be a tuple of ints.
        Prepends the frontdoor. """
        self.stream.write(self.generator.generate(list(encoded)))

    def close(self):
        """ End this audio session. """
        self.stream.close()
        self.pyaudio.terminate()


class AudioWavetable(object):
    """ Generates a fixed-size table of sinosoidal samples and steps through
    it based on a given frequency, with linear interpolation.
    """

    def __init__(self, wavetable_length = 4096):
        # Array of raw floats comprising a sinusoidal waveform
        self.wavetable_length = wavetable_length
        self.wavetable = [math.sin(2.0 * math.pi * n / wavetable_length)
                          for n in range(wavetable_length)]
        self.wavetable.append(self.wavetable[0])
        self.wavetable.append(self.wavetable[1])

        # Wavetable phase
        self.phase = 0.0
        self.phase_inc = 0.0

    def set_protocol(self, protocol):
        self.protocol = protocol

    def set_frequency(self, frequency):
        self.phase_inc = frequency * self.wavetable_length / CHIRP_SAMPLERATE

    def next(self):
        phase_round = int(self.phase)
        phase_fraction = self.phase - phase_round

        # Update wavetable phase
        self.phase += self.phase_inc;
        if self.phase > self.wavetable_length:
            self.phase -= self.wavetable_length
        if self.phase < 0:
            self.phase += self.wavetable_length

        # Calculate return value via linear interpolation
        return (self.wavetable[phase_round] + phase_fraction *
                (self.wavetable[phase_round + 1] - self.wavetable[phase_round]))


class AudioGenerator(object):
    """ Class to generate audio samples for a chirp. """

    def __init__(self):
        self.wavetable = AudioWavetable()

    def set_protocol(self, protocol):
        self.protocol = protocol
        self.wavetable.set_protocol(protocol)

    def _generate(self, sequence, note_length_samples, silence_length_samples):
        freq = None
        freq_target = None
        freq_change_per_sample = 0.0
        amp = 0.0
        sample_cnt = 0
        note_length_samples -= silence_length_samples

        for note in sequence:
            freq_target = self.protocol.note_index_to_frequency(note)

            if freq is None:
                freq = freq_target
            if self.protocol.portamento > 0:
                freq_change_per_sample = (freq_target - freq) / float(
                    self.protocol.portamento_samples)
            else:
                freq_change_per_sample = 0
                freq = freq_target

            for n in range(note_length_samples):
                if n < self.protocol.envelope_attack_samples :
                    amp = ENV_SUSTAIN * n / float(self.protocol.envelope_attack_samples)
                elif n < (note_length_samples -
                          self.protocol.envelope_release_samples):
                    amp = ENV_SUSTAIN
                else:
                    amp = (ENV_SUSTAIN * (1.0 - ((n - (
                        float(note_length_samples -
                              self.protocol.envelope_release_samples))
                    ) / float(self.protocol.envelope_release_samples))))

                if n < self.protocol.portamento_samples:
                    freq += freq_change_per_sample

                # Update internal phase increment based on desired frequency
                self.wavetable.set_frequency(freq)

                sample = self.wavetable.next() * amp * 32768
                yield struct.pack('h', float(sample))

            for n in range(silence_length_samples):
                yield struct.pack('h', 0.0)

    def generate(self, message):
        samples = b''
        for sample in self._generate(self.protocol.frontdoor,
                                     self.protocol.frontdoor_note_length_samples,
                                     self.protocol.frontdoor_silence_length_samples):
            samples += sample
        for sample in self._generate(message,
                                     self.protocol.message_note_length_samples,
                                     self.protocol.message_silence_length_samples):
            samples += sample
        return samples

    def save_wav(self, code, filename):
        wav = wave.open(filename, 'wb')
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(CHIRP_SAMPLERATE)
        wav.writeframes(self.generate(code))
        wav.close()
