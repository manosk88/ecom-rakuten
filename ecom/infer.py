from . import bpv, data, scoring
from .slimai import to_np

from kerosene import torch_util

import fire
import numpy as np


def infer(model, dl, with_f1=True, is_test=False):
    probs = []
    targs = []
    for x, y in dl:
        probs.append(to_np(model(torch_util.variable(x))))
        targs.append(to_np(y))
    probs, targs = np.concatenate(probs), np.concatenate(targs)
    if with_f1:
        pcuts = scoring.pred_from_probs(probs)
        probs[probs < pcuts] = 0
        probs[:, -1] += 1e-9
    return probs.argmax(axis=1), targs


def main(model_file):
    n_emb, n_hid = 50, 512
    enc, cenc = data.load_encoders()
    n_inp, n_out = len(enc.itos), len(cenc.itos)
    model = data.load_model(
        torch_util.to_gpu(bpv.BalancedPoolLSTM(n_inp, n_emb, n_hid, n_out)),
        model_file,
    )

    _, val_dl = data.load_dataloaders()
    preds, targs = infer(model, val_dl)
    print(scoring.score(targs, preds))


if __name__ == '__main__':
    fire.Fire(main)
