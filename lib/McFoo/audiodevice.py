import os
import fcntl
import struct
import errno

class AudioDevice:
    def __init__(self):
        self.dsp = os.open("/dev/dsp", os.O_WRONLY|os.O_NONBLOCK)

        # make sure it's blocking.
        flags = fcntl.fcntl(self.dsp, fcntl.F_GETFL)
        flags = flags & ~os.O_NONBLOCK
        fcntl.fcntl(self.dsp, fcntl.F_SETFL, flags)
        
        # A horrible, ugly kludge. These values are from
        # linux/soundcard.h, extracted with
        """
        #include <stdio.h>
        #include <linux/soundcard.h>
        int main(void) {
          printf("%d\n%d\n%d\n%u\n%u\n",
            SNDCTL_DSP_SAMPLESIZE,
            SNDCTL_DSP_SPEED,
            SNDCTL_DSP_STEREO,
            AFMT_S16_LE,
            AFMT_S16_BE);
          return 0;
        }
        """

        SNDCTL_DSP_SAMPLESIZE = -1073459195
        SNDCTL_DSP_SPEED = -1073459198
        SNDCTL_DSP_STEREO = -1073459197
        AFMT_S16_LE = 16
        AFMT_S16_BE = 32
        
        stereo=struct.pack('i', 1)
        fcntl.ioctl(self.dsp, SNDCTL_DSP_STEREO, stereo)
        
        size=struct.pack('i', AFMT_S16_LE)
        size = fcntl.ioctl(self.dsp, SNDCTL_DSP_SAMPLESIZE, size)
        
        speed=struct.pack('i', 44100)
        speed = fcntl.ioctl(self.dsp, SNDCTL_DSP_SPEED, speed)

    def play(self, data, bytes):
        return os.write(self.dsp, data[:bytes])

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        self.__init__()
