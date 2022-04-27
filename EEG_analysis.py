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

# If you look into the channel names you only see number when instead the EEG setup
# uses electrode names that give information about their position on the scalp
# (Cz, TP10, ...).

raw.info["chs"]

# In order to change the mapping name, we need a dictionary that
# transforms the numbers 1 - 64 into corresponding naming conventions.

mapping = {"1": "Fp1", "2": "Fp2", "3": "F7", "4": "F3", "5": "Fz", "6": "F4",
           "7": "F8", "8": "FC5", "9": "FC1", "10": "FC2", "11": "FC6",
           "12": "T7", "13": "C3", "14": "Cz", "15": "C4", "16": "T8", "17": "TP9",
           "18": "CP5", "19": "CP1", "20": "CP2", "21": "CP6", "22": "TP10",
           "23": "P7", "24": "P3", "25": "Pz", "26": "P4", "27": "P8", "28": "PO9",
           "29": "O1", "30": "Oz", "31": "O2", "32": "PO10", "33": "AF7", "34": "AF3",
           "35": "AF4", "36": "AF8", "37": "F5", "38": "F1", "39": "F2", "40": "F6",
           "41": "FT9", "42": "FT7", "43": "FC3", "44": "FC4", "45": "FT8", "46": "FT10",
           "47": "C5", "48": "C1", "49": "C2", "50": "C6", "51": "TP7", "52": "CP3",
           "53": "CPz", "54": "CP4", "55": "TP8", "56": "P5", "57": "P1", "58": "P2",
           "59": "P6", "60": "PO7", "61": "PO3", "62": "POz", "63": "PO4", "64": "PO8"}
# We can then use the mapping variable together with the rename_channels function
# to rename all the channels.

raw.rename_channels(mapping)

# Look at the channel names again, can you see the difference?

raw.info["chs"]

# We further need the information of relative electrodes positions on the scalp to
# plot topographies and sensor positions on the scalp. The BrainVision company has
# their own file which contains the exact coordinates for their EEG setup, so we
# load that into the montage variable and set the montage into our Raw Object.

montage_path = DIR / "AS-96_REF.bvef"
montage = mne.channels.read_custom_montage(fname=montage_path)
raw.set_montage(montage)


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
# Select certain intervals in the joint plot and look at the topography. Does it look
# as expected? Where do we expect electric activity on the scalp to be highest for
# auditory evoked potentials?

epochs.average().plot_joint()

# We can plot the sensors ("topomap" or "3d") and decide on what electrodes we want
# to take as reference. We then select these as the reference or simply take an average
# of all electrodes activity as reference. You decide, which reference would in
# theory make most sense?

epochs.plot_sensors(kind="topomap", ch_type='all')
reference = ["TP10", "TP9"]

# After decision on which reference to choose, we can simply set and apply the
# reference.

epochs.set_eeg_reference(ref_channels=reference)

# Look at the ERP again: does the response look all right now, and how do you know?

epochs.average().plot_joint()

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
