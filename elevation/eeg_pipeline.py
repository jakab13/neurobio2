import mne
import pathlib
import pickle
from autoreject import AutoReject
# define paths to current folders
DIR = pathlib.Path.cwd()
eeg_DIR = DIR / 'elevation' / "data"
import matplotlib
matplotlib.use('TkAgg')

# load raw data
raw = mne.io.read_raw_brainvision(eeg_DIR / 'vanessa_1.vhdr', preload=True)

# load channel name mapping and rename channels
with open('channel_mapping.pkl', 'rb') as f:
    mapping = pickle.load(f)
raw.rename_channels(mapping)

# load and apply montage
montage_path = DIR / "AS-96_REF.bvef"
montage = mne.channels.read_custom_montage(fname=montage_path)
raw.set_montage(montage)

# bandpass filter raw data
raw.filter(l_freq=0.5, h_freq=40)

# load and name events
events = mne.events_from_annotations(raw)[0] # load events
event_id = dict(up=1, down=2, left=3, right=4, front=5)  # assign event id's to the trigger numbers

# set epoch times
tmin = -0.2
tmax = 0.4

# set trial rejection parameters
reject_criteria = dict(eeg=200e-6)   # 200 µV
flat_criteria = dict(eeg=2e-6)   # 2 µV

# get epoched data with applied baseline and automatic trial rejection
# (should not remove eye movements and blinks yet)
epochs = mne.Epochs(raw, events, event_id, tmin=tmin, tmax=tmax, baseline=(tmin, 0),
                    reject=reject_criteria, flat=flat_criteria,
                    reject_by_annotation=False, preload=True)
epochs.plot_drop_log() # summary of rejected epochs per channel

# # hold on
# if too many epochs where dropped due to a single channel,
# consider removing and interpolating these channels in the raw data:
raw.info['bads'] += ['FT8', 'FC2']
raw.interpolate_bads()
# in that case, get new epochs from raw with interpolated channels
epochs = mne.Epochs(raw, events, event_id, tmin=tmin, tmax=tmax,
                    reject=reject_criteria, flat=flat_criteria,
                    reject_by_annotation=False, preload=True)

# re-reference
reference = ['PO9', 'PO10']  # set average of both mastoid electrodes as reference
epochs.set_eeg_reference(reference)

# ICA
ica = mne.preprocessing.ICA(n_components=0.99, method="fastica")
ica.fit(epochs)
# ica.plot_components()  # plot components
# ica_sources = ica.get_sources(epochs)
# ica_sources.plot(picks="all")  # plot time trace of components
# ica.plot_properties(epochs, picks=[11])  # take a closer look
ica.exclude = [0]  # remove selected components
ica.apply(epochs)  # apply ICA

# ---- here we might want to save the pre-processed epochs object
epochs.save(eeg_DIR / 'vanessa-epo.fif', overwrite=True)  # save preprocessed data

# read saved epochs
epochs = mne.read_epochs(eeg_DIR / 'vanessa-epo.fif', proj=True, preload=True, verbose=None)


evoked_front = epochs['front'].average()
evoked_up = epochs['up'].average()
evoked_down = epochs['down'].average()
evoked_left = epochs['left'].average()
evoked_right = epochs['right'].average()

# plot evoked topo
mne.viz.plot_evoked_topo(evoked_up)
mne.viz.plot_evoked_topo(evoked_up)
# plot evoked
mne.viz.plot_evoked(evoked_front, picks=['Cz'])
mne.viz.plot_evoked(evoked_up, picks=['Cz'])
mne.viz.plot_evoked(evoked_down, picks=['Cz'])
mne.viz.plot_evoked(evoked_left, picks=['Cz'])
mne.viz.plot_evoked(evoked_right, picks=['Cz'])

# create difference waves
# up - standard
evoked_diff = mne.combine_evoked([evoked_up, evoked_front], weights=[1, -1])
evoked_diff.plot_topo(color='b', legend=True)
# left - standard
evoked_diff = mne.combine_evoked([evoked_left, evoked_front], weights=[1, -1])
evoked_diff.plot_topo(color='b', legend=True)
# right - standard
evoked_diff = mne.combine_evoked([evoked_right, evoked_front], weights=[1, -1])
evoked_diff.plot_topo(color='b', legend=True)

# plot evoked pattern on topographic map
evoked_up.plot_joint()
evoked_up.plot_topomap(times=[0., 0.08, 0.1, 0.12, 0.2])

