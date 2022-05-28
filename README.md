# README

## How the Scripts Work

Basically, the script `maze_cnf_gen.py` will translate the maze solving problem to a bounded model checking problem with n steps. The SAT solver will try to solve the generated CNF. If satisfiable, the script `parse_model.py` will parse the model and print solution. Otherwise the script will increase number of steps and solve again.

## How to Use the Scripts

To use the scripts, first make sure that your machine has `python3` installed. Then run the `solve.sh` script with:

```
bash solve.sh <input_file> <maximum_steps> <solver_path>
```

where:
- <input_file> is the path to the input file
- <maximum_steps> is the maximum number of steps the script will try to search
- <solver_path> is the path to some SAT solver binary, I tested this script with kissat, other solvers may not work properly