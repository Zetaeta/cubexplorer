#!/bin/bash
cp data/cubes{,.bak} -r
python util/getcubedata.py both
mv data/tree.txt{,.bak}
Rscript process.r
mv data/tree.json{,.bak}
python util/parsetree.py > data/tree.json
export PYTHONPATH=.:/usr/lib/python
python -i util/covdb.py
python util/computecubes.py
