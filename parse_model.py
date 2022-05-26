#!/bin/python3
# -*- coding: utf-8 -*-

# Author: Guangchen Li (guangchenli96@gmail.com)
# A Python script for parsing the model returned by sat solvers

import argparse, math, sys

from typing import Tuple, List

def parse_arg() -> Tuple[str, int]:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True,
                        help="Path to the input.")
    parser.add_argument("-d", "--dim", required=True,
                        help="Dimension of the maze.", type=int)
    args = vars(parser.parse_args(sys.argv[1:]))
    return (args['input'], int(args['dim']))

def read_model_array(input: List[str]) -> List[int]:
    model = []
    for line in input:
        words = line.split()
        if words[0] == 'v':
            for w in words[1:]:
                if int(w) > 0:
                    model.append(1)
                else:
                    model.append(0)
    return model

def offset_to_pos(offset: int, dim: int):
    return (offset // dim, offset % dim)

def parse_result():
    filename, dim = parse_arg()
    num_bits = math.ceil(math.log2(dim * dim))
    model = None
    with open(filename) as f:
        lines = f.readlines()
        model = read_model_array(lines)
    result = []
    for i in range(0, len(model) // num_bits):
        idx = 0
        for j in range(0, num_bits):
            idx += model[i * num_bits + j] << (num_bits - j - 1)
        result.append(offset_to_pos(idx, dim))
    return result
    

def main():
    result = parse_result()
    print(result)
    

if __name__ == "__main__":
    main()
