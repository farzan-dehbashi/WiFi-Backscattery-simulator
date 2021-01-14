#!/usr/bin/env bash
for run in {1..2}
do
	python sim.py $1 $2 $3 $4
done
