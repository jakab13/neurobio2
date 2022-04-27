#### EEG data processing with MNE Python - example script (EEG Practical Neuro 2, SS2020) ####

# For a guide on installing python and mne see:
# https://mne.tools/stable/install/mne_python.html
# For a detailed description of MNE-python you can read the paper
# Gramfort et al. (2014): MNE software for processing MEG and EEG data or
# see their website: https://mne.tools/0.13/tutorials.html

# import needed modules
import mne
import pathlib

# define paths to current folders
DIR = pathlib.Path.cwd()
eeg_DIR = DIR / "data"

# load raw data
raw = mne.io.read_raw_brainvision(eeg_DIR / '20220302_pilot_4l8g2m_trial_1.vhdr', preload=True)

# plot  and inspect raw data. Are there any data segments that
# should be removed for further analyis?
raw.plot()

# To remove power line noise, we apply a lowpass filter with a 40 Hz cutoff
raw.filter(0.01, 40)

# WARNING: filtering alters the data and can produce artifacts and lead
# to incorrect conclusions. It is thus important to understand the effect of
# filters applied. We will ignore this for now but you can see this paper:
# Widmann et al. (2015): Digital filter design for electrophysiological data – a practical approach.

raw.plot()  # plot data again, can you see the difference?

# From the raw data we are going to get the 'events' which are the time points
# at which a stimulus trigger was recorded.

events = mne.events_from_annotations(raw)[0]
mne.viz.plot_events(events)

# We will now cut the data into equally long segments around the stimuli to
# obtain the so-called epochs. For this we need to define some parameters:

tmin = -0.2
tmax = 0.5
reject_criteria = dict(eeg=200e-6)
flat_criteria = dict(eeg=1e-6)
event_id = {
    'tone_500': 1,
    'tone_2000': 2
}
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, reject=reject_criteria, flat=flat_criteria,
                    reject_by_annotation=True, preload=True)

# We can now average over the epochs to obtain the ERP (= event-related potential).
# This is what we will work with in the next section.
epochs.average().plot()

# However, this does not look right. There are big differences in the channels' baseline
# which overshadows the actual ERP. We can circumvent this by setting a channel-
# specific baseline. To do this we select a certain interval in the Epoch. For
# each channel, the mean of that interval will be subtracted from the rest of
# the epoch.
baseline = (-0.2, 0)
epochs.apply_baseline(baseline)
epochs.average().plot()
# The baseline can also be given as an argument when computing the epochs but
# we did not do this here for educational reasons.

# Now you can play with the parameters (start, stop and baseline) and see how
# the evoked response changes. For example: Try choosing an interval that
# contains more than one stimulus. Try using an interval with strong stimulus
# related activity as baseline.

# Assignment 1: plot the epoch average with different filter configurations,
# epoch intervals (tmin / tmax) and baseline intervals

evoked_tone_500 = epochs['tone_500'].average()
evoked_tone_2000 = epochs['tone_2000'].average()

mne.viz.plot_compare_evokeds([
    evoked_tone_500,
    evoked_tone_2000
    ],
    title='Average evoked responses'
)