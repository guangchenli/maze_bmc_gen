#!/bin/python3
# -*- coding: utf-8 -*-

# Author: Guangchen Li (guangchenli96@gmail.com)
# A Python script for generating DIMACS formated cnf files to solve the maze
# problem as specified in the homework description.

import sys, argparse

from typing import List, Tuple
from math import ceil, log2
from io import StringIO

num_bits = 0
num_states = 0

def read_maze(path: str):
    with open(path) as f:
        n = int(f.readline())
        maze = []
        for line in f:
            ln_li = list(line)[0:n]
            maze.append([int(i) for i in ln_li])
        return n, maze

    
# Encode a position to literal list, most significant bits first.
# Beware that the literals are unevaluated, they just denote signs
def get_encoded_pos(ln: int, col: int, n: int) -> List[int]:
    idx = ln * n + col
    result = []
    for i in range(0, num_bits):
        result.insert(0, idx & 0x1)
        idx >>= 1
    return [1 if i == 1 else -1 for i in result]


def get_init_state(n: int):
    init_state_sign = get_encoded_pos(0, 0, n)
    return [s * i for s, i in zip(init_state_sign, \
                                  range(1, len(init_state_sign) + 1))]


def get_final_state(n: int, offset: int):
    global num_bits
    enc = get_encoded_pos(n - 1, n - 1, n)
    return [(i + offset) * s for s, i in zip(enc, range(0, num_bits))]


def state_is_valid(maze: List[List[int]], ln: int, col: int, n: int) -> bool:
    return ln >= 0 and ln < n and col >= 0 and col < n and \
        maze[ln][col] == 0


def get_adjacent_states(maze: List[List[int]], ln: int, col: int, n: int) \
    -> List[List[int]]:
    result = []
    if state_is_valid(maze, ln - 1, col, n):
        result.append(get_encoded_pos(ln - 1, col, n))
    if state_is_valid(maze, ln + 1, col, n):
        result.append(get_encoded_pos(ln + 1, col, n))
    if state_is_valid(maze, ln, col - 1, n):
        result.append(get_encoded_pos(ln, col - 1, n))
    if state_is_valid(maze, ln, col + 1, n):
        result.append(get_encoded_pos(ln, col + 1, n))
    return result


# offset: Offset for new literals.
# return: Number of literals created in Tseitin transformation and
# the formula in CNF.
def dnf_to_cnf(dnf: List[List[int]], offset: int) -> \
    (int, List[List[int]]):
    lit_count = 0
    result = []
    for cls in dnf:
        new_lit = offset + lit_count
        # Add p->(a/\b/\c...)
        for lit in cls:
            result.append([-new_lit, lit])
        # Add (a/\b/\c...)->p
        result.append([-l for l in cls] + [new_lit])
        lit_count += 1
    # Add (p1\/p2\/p3...)
    result.append([i + offset for i in range(0, lit_count)])
    return (lit_count, result)


# Get transition function template of a maze.
# ------------------------------------------------------------
# The transition function template is in DNF, 1 means positive
# occurrence of a literal while -1 mean negative occurrence of
# a literal. 0 means that the corresponding literal does not
# actually exist in instantiated transition function template.
# It only serves as a placeholder for instantiate function to
# calculate literal number correctly.
def get_trans_func_temp(maze: List[List[int]], n: int) \
    -> List[List[int]]:
    result = []
    for ln in range(0, n):
        for col in range(0, n):
            if maze[ln][col] == 0:
                current_state = get_encoded_pos(ln, col, n)
                next_states = get_adjacent_states(maze, ln, col, n)
                for ns in next_states:
                    result.append(current_state + ns)
    return result


# Instantiate a transition function and return it in DNF
def instantiate_trans_func(temp: List[List[int]], offset: int) \
    -> List[List[int]]:
    global num_bits
    result = []
    for cls in temp:
        new_cls = []
        for i in range(0, num_bits * 2):
            lit = cls[i] * (offset + i)
            if lit != 0:
                new_cls.append(lit)
        result.append(new_cls)
    return result

# Get BMC part of the final formula in CNF form
def gen_bmc(maze: List[List[int]], n: int ,num_steps: int) \
    -> Tuple[int, List[List[int]]]:
    global num_bits
    init_state = get_init_state(n)
    end_state = get_final_state(n, num_steps * num_bits + 1)
    trans_func_tmp = get_trans_func_temp(maze, n)
    bmc_formulae = []
    tseitin_offset = (num_steps + 1) * num_bits + 1
    for i in range(0, num_steps):
        current_step_dnf = \
            instantiate_trans_func(trans_func_tmp, i * num_bits + 1)
        num_new_lit, current_step_cnf = \
            dnf_to_cnf(current_step_dnf, tseitin_offset)
        bmc_formulae += current_step_cnf
        tseitin_offset += num_new_lit
    return tseitin_offset, bmc_formulae + \
        [[i] for i in init_state] + \
        [[i] for i in end_state]


# Generate DIMACS format cnf string
def gen_dimacs(cnf: List[List[int]], num_lit: int) -> str:
    result_file = StringIO()
    result_file.write("p cnf " + str(num_lit) + " " + str(len(cnf)) + " \n")
    for cls in cnf:
        for lit in cls:
            result_file.write(str(lit))
            result_file.write(" ")
        result_file.write("0\n")
    result_file.seek(0)
    result = result_file.read()
    result_file.close()
    return result


def parse_arg() -> Tuple[str, int]:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True,
                          help="Path to the input.")
    parser.add_argument("-s", "--step", required=True,
                          help="Number of steps.", type=int)
    args = vars(parser.parse_args(sys.argv[1:]))
    return (args['input'], int(args['step']))
    

def main():
    global num_bits
    path, num_steps = parse_arg()
    n, maze = read_maze(path)
    num_bits = ceil(log2(n * n))
    tseitin_offset, bmc = gen_bmc(maze, n, num_steps)
    dimacs = gen_dimacs(bmc, tseitin_offset - 1)
    print(dimacs)


if __name__ == "__main__":
    main()
