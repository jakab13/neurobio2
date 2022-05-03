import slab
import freefield
import numpy as np

# initialize processors
freefield.initialize(setup='dome', default='play_rec')
freefield.set_logger('warning')  # set logging output level

# stimulus generation
stim = slab.Sound.pinknoise(duration=0.1)
stim = stim.ramp(when='both', duration=0.1)  # ramp the waveform to avoid 'click' at the end of noise
silence = slab.Sound.silence(duration=0.5)  # add a silence for duration of ISI
sound_seq = slab.Sound.sequence(stim, silence)  # combine the two sounds

""" Generate trial sequence with 600 trials and deviants with 20% probability """
# 6 minutes runtime per block of trials
trial_seq = slab.Trialsequence(conditions=1, n_reps=167, deviant_freq=0.2)
# todo work around; avoid shuffling 600 elements until
#  "np.min(np.diff(np.random.choice(range(1000)), 200, replace=False))) < min_dist" is satisfied
for i in range(2):
    trial_seq.trials.extend(slab.Trialsequence(conditions=1, n_reps=167, deviant_freq=0.2).trials)
trial_seq.n_remaining, trial_seq.n_trials = 600, 600  # modify class attributes
# check that deviants don't occur twice in a row:
if np.min(np.diff([i for i, e in enumerate(trial_seq.trials) if e == 0])) < 2:
    print('Warning: trial sequence contains 2 deviant stimuli in a row.')
else:
    for trial in trial_seq:
        i += 1  # introduce counting variable
        deviant = None
        if trial == 0:  # deviant trial
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
        if i % 50 == 0:  # every 50 trials
            print('\n Point laser at previous sound source and press button to continue. \n')
            freefield.wait_for_button()
    print('Block complete :)')

# stimulus: pinknoise
# duration: 100 ms
# isi: 500 ms
# probability: standard: 0.8,  4X deviant: 0.05
# n_trials: 1500
# standard stim: 0° az, 0° ele
# azimuthal angles: +/- 30°
# elevation angles: +/- 30°
