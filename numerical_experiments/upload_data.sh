#!/bin/bash

# Report model 
du -h "research_data/">"logs/storage_analysis/output.txt"

# Run experiments
CSV_LIST="ProblemInstances.csv"
DATA=${CSV_LIST}

# Prepare problem instance file
sed -i "s/\r//g" ${DATA}

# Upload data for all problem instances
while IFS=, read -r Source ProblemInstance DataPath; do
    echo "##### Upload migrated data model from provider ${Source} in ${DataPath} with problem instance ${ProblemInstance} into EER model #####"
    python3 upload_data.py $ProblemInstance $DataPath
done < ${DATA}