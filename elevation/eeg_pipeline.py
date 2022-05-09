import mne
import pathlib
import pickle
from autoreject import AutoReject
# define paths to current folders
DIR = pathlib.Path.cwd()
eeg_DIR = DIR / 'elevation' / "data"

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

# set baseline parameters
tmin = -0.2
tmax = +0.4

# set trial rejection parameters
reject_criteria = dict(eeg=200e-6)  # 200 µV
flat_criteria = dict(eeg=2e-6)  # 1 µV

# get epoched data with applied baseline and automatic trial rejection
# (should not remove eye movements and blinks yet)
epochs = mne.Epochs(raw, events, event_id, tmin=tmin, tmax=tmax,
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
ica.plot_properties(epochs, picks=[0])  # take a closer look
ica.exclude = [0]  # remove selected components
ica.apply(epochs)  # apply ICA

epochs.save(eeg_DIR / 'vanessa-epo.fif')  # save preprocessed data

