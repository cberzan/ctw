from __future__ import division
import ctw
import argparse
import re
import subprocess
import os.path


CTW_BINARY = ['../ctw_baseline/ctw', 'e', '-dX', '-k', 'INPUT', '/tmp/ctw.txt']


def run_baseline(input_path, depth=6):
    args = CTW_BINARY[:]
    args[2] = '-d{}'.format(depth)
    args[4] = input_path
    result = subprocess.check_output(args).split('\n')
    subprocess.call(['rm', '-f', '/tmp/ctw.txt'])
    return float(result[20].split()[2])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('--depth', type=int, default=6)
    args = parser.parse_args()

    if not os.path.exists(CTW_BINARY[0]):
        print 'CTW baseline binary not found! Did you compile it?'
        exit(1)

    print 'Comparing with tree depth {}...'.format(args.depth)
    baseline_ratio = run_baseline(args.input_file, args.depth)

    with open(args.input_file, 'r') as infile:
        plaintext = infile.read()
    msg_len, bit_encoded = ctw.encode(plaintext, args.depth * 8)  # TODO
    bit_ratio = len(bit_encoded) / len(plaintext) * 8
    msg_len, phases_encoded = ctw.encode_phases(plaintext, args.depth)  # TODO
    phases_ratio = len(phases_encoded) / len(plaintext) * 8

    print 'Compression ratios (bits/byte):'
    print 'Baseline implementation:\t{}'.format(baseline_ratio)
    print 'Bits implementation:\t{}'.format(bit_ratio)
    print 'Phases implementation:\t{}'.format(phases_ratio)
