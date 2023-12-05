# Network Analysis
A set of tools to generate networks from CSV or RData file, and analyze them.

## How to run
```
python generate_networks.py
```
This read all the CSV and RData file within the ```data``` directory and generates the corrisponding NetworkX networks.
By deafult the so generated networks will be stored inside ```networks``` directory.

```
python analyze_networks.py
```
This script analyzes all the networks inside the ```networks``` directory computing their global and local measures.
The tabular results are save in ```results``` folder and the plots in ```plots``` folder.
