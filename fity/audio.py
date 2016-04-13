from __future__ import division
from contextlib import contextmanager
from collections import OrderedDict
import wave
import six
import mutagen.mp3, mutagen.flac, mutagen.oggvorbis, mutagen.asf, mutagen.mp4
from .base import Filetype, ExtractionError, hexbytes, literal, regexpr, hexadecimals
from .categories import AudioType


class WAVAudio(AudioType):
    mimetype = 'audio/wav'
    extension = 'wav'
    description = 'Waveform audio file'
    signatures = [
        hexbytes('52 49 46 46 ? ? ? ? 57 41 56 45 66 6D 74 20'),
    ]

    @classmethod
    def extract(cls, file):
        try:
            w = wave.open(file, 'rb')
        except wave.Error as e:
            six.raise_from(ExtractionError('Error opening Wave file'), e)
        try:
            frames = w.getnframes()
            framerate = w.getframerate()
            return cls(
                file,
                OrderedDict([
                    ('channels', w.getnchannels()),
                    ('samplerate', framerate),
                    ('duration', frames/framerate),
                ])
            )
        finally:
            w.close()


def fake_open(path, mode=None):
    # make sure we actually got a file-like instead of a path
    assert hasattr(path, 'read'), 'not file-like: %r' % path
    # return the file-like we got as the newly opened file
    return path


class MutagenMixin(object):
    mutagen_type = NotImplemented

    def __init__(self, file):
        self._properties = None
        self.file = file

    @contextmanager
    def _override_open(self):
        # since mutagen only supports opening audio files by path,
        # we override the builtin open temporarily to accept file-like objects
        real_open = __builtins__['open']
        __builtins__['open'] = fake_open
        yield
        __builtins__['open'] = real_open

    def _get_properties(self):
        with self._override_open():
            try:
                audio = self.mutagen_type(self.file)
            except Exception as e:
                # cannot raise error here
                return {}
        if isinstance(audio, mutagen.StreamInfo):
            info = audio
        elif isinstance(audio, mutagen.FileType):
            info = audio.info
        else:
            raise TypeError(audio)
        return OrderedDict([
            ('channels', info.channels),
            ('samplerate', info.sample_rate),
            ('duration', info.length),
        ])

    @classmethod
    def extract(cls, file):
        "Extract the filetype from a file."
        return cls(file)

    @property
    def properties(self):
        if self._properties is None:
            self._properties = self._get_properties()
        return self._properties


class MP3Audio(MutagenMixin, AudioType):
    mimetype = 'audio/mpeg'
    extension = 'mp3'
    description = 'MP3 audio file'
    # TODO distinguish from UTF16 Little Endian
    signatures = [
        # an ID3 tag
        hexbytes('49 44 33'),
        # some mp3 files start with a variable number of zero bytes
        regexpr(br'\00+\xFF\xFB\x70\x04', 1024, 4),
        regexpr(br'\00+\xFF\xFB\x80\x04', 1024, 4),
        regexpr(br'\00+\xFF\xFB\xB0\x00', 1024, 4),
        regexpr(br'\00+\xFF\xFB\xA0\x00', 1024, 4),
        regexpr(br'\00+\xFF\xFB\x90\xC0', 1024, 4),
        regexpr(br'\00+\xFF\xFA\x90\x00', 1024, 4),
        # since the number of leading zero bytes can be greater than the window
        # in which we search for the signature, we need to match the case
        # where the whole window contains zero bytes (with a small likeliness)
        literal(b'\x00' * 1024, 0.5),
    ] + [hexbytes(p % x) for p in ['FF E%s', 'FF F%s'] for x in hexadecimals]

    mutagen_type = mutagen.mp3.MPEGInfo


class VorbisAudio(MutagenMixin, AudioType):
    mimetype = 'audio/ogg'
    extension = 'ogg'
    description = 'Ogg Vorbis audio file'
    signature = hexbytes(
        '4F 67 67 53 '  # capture patter 'OggS'
        '00 02 00 00 00 00 00 00 00 00 '  # version, flags, granule position
        '?? ?? ?? ?? '  # serial number
        '00 00 00 00 '  # page sequence number
        '?? ?? ?? ?? '  # checksum
        '01 '           # segments
        '1E 01 76 6F 72 62 69 73 00 00 00 00 02'  # segment table (vorbis)
    )

    mutagen_type = mutagen.oggvorbis.OggVorbis


class FLACAudio(MutagenMixin, AudioType):
    mimetype = 'audio/flac'
    extension = 'flac'
    description = 'Free Lossless Audio Codec file'
    signature = hexbytes('66 4C 61 43 00 00 00 22')

    mutagen_type = mutagen.flac.FLAC


class WindowsMediaAudio(MutagenMixin, AudioType):
    mimetype = 'audio/x-ms-wma'
    extension = 'wma'
    description = 'Windows Media Audio file'
    # TODO distinguish from .wmv and .asf
    signature = hexbytes(
        '30 26 B2 75 8E 66 CF 11 A6 D9 00 AA 00 62 CE 6C '
        '?? ?? 00 00 00 00 00 00 ?? 00 00 00 01 02 40 A4 '
        'D0 D2 07 E3 D2 11 97 F0 00 A0 C9 5E A8 50'
    )

    mutagen_type = mutagen.asf.ASF


class AppleLosslessAudio(MutagenMixin, AudioType):
    mimetype = 'audio/mp4'
    extension = 'm4a'
    description = 'Apple Lossless Audio Codec file'
    signatures = [
        hexbytes('00 00 00 20 66 74 79 70 4D 34 41 20'),
        hexbytes('?? ?? ?? ?? 66 74 79 70 4D 34 41 20'),  # probably could match more bytes here
    ]

    mutagen_type = mutagen.mp4.MP4
