import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

import soundfile as sf
import torch
from speechbrain.inference.speaker import EncoderClassifier

model = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec"
)

def generate_embedding(file_path: str):
    signal, sample_rate = sf.read(file_path)

    # convert to torch tensor
    signal = torch.tensor(signal).float()

    # handle stereo → mono
    if len(signal.shape) > 1:
        signal = signal.mean(dim=1)

    # add batch dimension
    signal = signal.unsqueeze(0)

    embedding = model.encode_batch(signal)

    return embedding.squeeze().tolist()