import slab
import freefield
import numpy as np

# initialize processors
freefield.initialize(setup='dome', default='play_rec')

# stimulus generation
stim = slab.Sound.pinknoise(duration=0.1)
stim = stim.ramp(when='both', duration=0.1)  # ramp the waveform to avoid 'click' at the end of noise
silence = slab.Sound.silence(duration=0.5)  # add a silence for duration of ISI
sound_seq = slab.Sound.sequence(stim, silence)  # combine the two sounds

# generate trial sequence
trials = slab.Trialsequence(conditions=1, n_reps=750, deviant_freq=0.2)

# start trial block
for trial in trials:
    deviant = None
    if trial == 0: # deviant trial
        deviant = np.random.randint(0,4) # randomly select one out of 4 deviants from uniform distribution
        if deviant == 0:
            speaker_index = 20  # az: 0, ele: 37.5
        elif deviant == 1:
            speaker_index = 26  # az: 0, ele: -37.5
        elif deviant == 2:
            speaker_index = 8  # az: -35, ele: 0
        elif deviant == 3:
            speaker_index = 38  # az: 35, ele: 0
        # set loudspeaker position, depending on deviant index
        freefield.set_signal_and_speaker(signal=sound_seq, speaker=speaker_index, equalize=False)
        # set trigger value to index of deviant stimulus
        freefield.write(tag='trigcode', value=deviant, processors='RX82')
    else:
        # play from central speaker
        freefield.set_signal_and_speaker(signal=sound_seq, speaker=23, equalize=False)
        # set trigger value to 4 when playing standard stimulus
        freefield.write(tag='trigcode', value=4, processors='RX82')
    # play and wait until the sound is played before continuing with next trial (loop iteration)
    freefield.wait_to_finish_playing()

# stimulus: pinknoise
# duration: 100 ms
# isi: 500 ms
# probability: standard: 0.8,  4X deviant: 0.05
# n_trials: 1500
# standard stim: 0° az, 0° ele
# azimuthal angles: +/- 30°
# elevation angles: +/- 30°
