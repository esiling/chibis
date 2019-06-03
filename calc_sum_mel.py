import librosa
import numpy as np
import glob
import os.path

for filename in glob.glob('train/*.mp3'):
    x, fs = librosa.load(filename)
    spec = librosa.feature.melspectrogram(x, sr=fs, n_mels=128)
    spec_mean = np.mean(spec, axis=1)
    print(os.path.basename(filename), *list(spec_mean), sep="\t")
