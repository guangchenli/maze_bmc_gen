#!/bin/bash

INPUT_FILE=$1
MAX_STEPS=$2
SOLVER_PATH=$3

if [ ! -e $INPUT_FILE ]
then
    echo "The file $INPUT_FILE does not exits."
    exit 1
fi

DIM=$(head -n 1 $INPUT_FILE)

function solve_for_some_step () {
    local step=$1
    local ret=0
    python3 maze_cnf_gen.py -i $INPUT_FILE -s $step > ${step}.cnf
    $SOLVER_PATH ${step}.cnf > ${step}_result.txt
    if [[ $(cat ${step}_result.txt | grep '^s SATISFIABLE') ]]
    then
	echo 'The result is: '
	python3 parse_model.py -i ${step}_result.txt -d $DIM -s $step
	ret=1
    fi
    rm ${step}.cnf ${step}_result.txt
    return $ret
}

for i in $(seq $DIM $MAX_STEPS)
do
    solve_for_some_step $i
    if [ $? -eq 1 ]
    then
	exit 0
    fi
done

echo 'Max steps reached and a solution can not be found. Try increase MAX_STEPS.'
