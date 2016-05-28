import os
import wave
from .audio import SoundData

__all__ = ["load_wav_file", "load_file"]

def load_wav_file(fname):
    """Loads a WAV encoded audio file into a SoundData object."""
    fp = wave.open(fname, "rb")
    channels = fp.getnchannels()
    bitrate = fp.getsampwidth() * 8
    samplerate = fp.getframerate()
    buf = fp.readframes(fp.getnframes())
    return SoundData(buf, channels, bitrate, len(buf), samplerate)


# supported extensions
_EXTENSIONS = {".wav": load_wav_file}


#try:
#    from ..ogg import vorbisfile as vorbis
#
#    @experimental
#    def load_ogg_file(fname):
#        """Loads an Ogg-Vorbis encoded audio file into a SoundData object."""
#        fp = vorbis.fopen(fname)
#        finfo = vorbis.info(fp)
#        length = vorbis.pcm_total(fp)
#        buf = vorbis.read(fp, length, word=2)[0]
#        return SoundData(buf, finfo.channels, 16, length, finfo.rate)
#
#    _EXTENSIONS[".ogg"] = load_ogg_file
#
#except ImportError:
#    pass


def load_file(fname):
    """Loads an audio file into a SoundData object."""
    ext = os.path.splitext(fname)[1].lower()
    funcptr = _EXTENSIONS.get(ext, None)
    if not funcptr:
        raise ValueError("unsupported audio file type")
    return funcptr(fname)


def load_stream(source):
    """Loads an audio stream into a SoundData object."""
    raise NotImplementedError("not implemented yet")

