#!/bin/bash

# Run experiments
CSV_LIST="ProblemInstances.csv"
DATA=${CSV_LIST}

# Prepare problem instance file
sed -i "s/\r//g" ${DATA}

# Run experiments for model instantiation
while IFS=, read -r Source ProblemInstance DataPath; do
    echo "##### Run Experiments for Problem Instance: ${ProblemInstance} #####"

    echo "### Run instantiation tests ###"
    python3 instantiate_model_disk_call.py $Source $ProblemInstance $DataPath
    python3 instantiate_model_eer_call.py $Source $ProblemInstance
done < ${DATA}