import freefield
import slab
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
slab.set_default_samplerate(44100)

tone1 = slab.Sound.tone(duration=0.25, level=90, frequency=500)
tone2 = slab.Sound.tone(duration=0.25, level=90, frequency=2000)
tone1 = tone1.ramp(when='both', duration=0.01)
tone2 = tone2.ramp(when='both', duration=0.01)

silence = slab.Sound.silence(duration=0.6)
stims = [slab.Sound.sequence(tone1, silence), slab.Sound.sequence(tone2, silence)]

freefield.initialize('dome', zbus=True, default='play_rec')
freefield.set_logger('WARNING')

# seq = slab.Trialsequence(conditions=300)
seq = slab.Trialsequence(conditions=stims, n_reps=100)

for trial in seq:
    # print(seq.trials[seq.this_n])
    freefield.set_signal_and_speaker(signal=trial, speaker=23, equalize=False)
    freefield.write(tag='trigcode', value=seq.trials[seq.this_n], processors='RX82')
    freefield.play()
    print('Playing stimulus:', seq.this_n + 1)
    freefield.wait_to_finish_playing()




