import oss

class VolumeControl:
    def __init__(self):
        self.mixer=oss.open_mixer()

    def get(self, wantstereo=0):
        (left, right) = self.mixer.read_channel(oss.SOUND_MIXER_VOLUME)
        if wantstereo:
            return (left, right)
        else:
            return (left+right)/2

    def set(self, vol_left, vol_right=None):
        (left, right) = self.mixer.read_channel(oss.SOUND_MIXER_VOLUME)
        if vol_right==None:
            average=(left+right)/2.0
            if average==0:
                left=right=vol_left
            else:
                left=int(left/average * vol_left)
                right=int(right/average * vol_left)
        else:
            left=vol_left
            right=vol_right
        if left<0:
            left=0
        if left>100:
            left=100
        if right<0:
            right=0
        if right>100:
            right=100
        self.mixer.write_channel(oss.SOUND_MIXER_VOLUME, (left, right))
        return self.get()

    def adjust(self, adjust_left=5, adjust_right=None):
        if adjust_right==None:
            adjust_right=adjust_left
        (left, right) = self.mixer.read_channel(oss.SOUND_MIXER_VOLUME)
        self.set(left+adjust_left, right+adjust_right)

    def inc(self, adjust=None):
        if adjust==None:
            adjust=5
        self.adjust(adjust)

    def dec(self, adjust=None):
        if adjust==None:
            adjust=-5
        self.adjust(adjust)
