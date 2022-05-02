import slab
import freefield
import numpy as np

# initializing
freefield.initialize(setup='dome', default='play_rec')

# stimulus generation
stim = slab.Sound.pinknoise(duration=0.1)
stim = stim.ramp(when='both', duration=0.1)
silence = slab.Sound.silence(duration=0.5)
sound_seq = slab.Sound.sequence(stim, silence)

trials = slab.Trialsequence(conditions=1, n_reps=750, deviant_freq=0.2)

# start trial block
for trial in trials:
    deviant = None
    if trial == 0:
        deviant = np.random.randint(0,4)
        if deviant == 0:    # az: 0, ele: 37.5
            speaker_index = 20
        elif deviant == 1: # az: 0, ele: -37.5
            speaker_index = 26
        elif deviant == 2: # az: -35, ele: 0
            speaker_index = 8
        elif deviant == 3:  # az: 35, ele: 0
            speaker_index = 38
        freefield.set_signal_and_speaker(signal=sound_seq, speaker=speaker_index, equalize=False)
        freefield.write(tag='trigcode', value=deviant, processors='RX82')
        # set loudspeaker to position
    else:
        # play from central speaker
        freefield.write(tag='trigcode', value=4, processors='RX82')
        freefield.set_signal_and_speaker(signal=sound_seq, speaker=23, equalize=False)

    freefield.play()
    freefield.wait_to_finish_playing()


# stimulus: pinknoise
# duration: 100 ms
# isi: 500 ms
# probability: standard: 0.8,  4X deviant: 0.05
# n_trials: 1500

# azimuthal angles: +/- 30°

# elevation angles: +/- 30°
