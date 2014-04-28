from __future__ import division
import numpy as np
import ctw
import argparse
import re
import subprocess
import os.path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('--depth', type=int, default=6)
    args = parser.parse_args()

    print 'Comparing with tree depth {}...'.format(args.depth)

    with open(args.input_file, 'r') as infile:
        plaintext = infile.read()
    alphas = np.linspace(0, 1, 11)
    ratios = []
    for alpha in alphas:
        msg_len, phases_encoded = ctw.encode_phases(plaintext, args.depth,
                                                    weight=alpha)  # TODO
        phases_ratio = len(phases_encoded) / len(plaintext) * 8
        ratios.append(phases_ratio)

    for alpha, ratio in zip(alphas, ratios):
        print 'weight={}:\t {} bits/byte'.format(alpha, ratio)
