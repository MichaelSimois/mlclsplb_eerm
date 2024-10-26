# -*- coding: utf-8 -*-
from memory_profiler import profile
import sys
import time
import os

SOURCE = str(sys.argv[1])
PROBLEM_INSTANCE = str(sys.argv[2])

print("# Memory profiling of instantiation from EER model: Problem instance = %s #" % (PROBLEM_INSTANCE))

fp = open("logs/instantiation/model_instantiation_db_call_" + PROBLEM_INSTANCE + ".log", "w+")
@profile(stream = fp)
def instantiate_model(problem_instance_id):
    from lib.index_model import IndexModel
    index_model = IndexModel(
        problem_instance_id = problem_instance_id, 
        load_connection = True
    )
    index_model.instantiate()

st = time.time()
instantiate_model(problem_instance_id = PROBLEM_INSTANCE)
et = time.time()
print("# Run EER model instantiation successfully after", et - st, "seconds #")

# %% Save execution time
import pandas as pd
execution_time_report = pd.read_csv(os.path.dirname(os.path.realpath("__file__")) + "/logs/instantiation/execution_time.csv", sep=";")
execution_time_report = pd.concat([execution_time_report, pd.DataFrame(data = {"Source": [SOURCE], "LoadingType": ["DB"], "ProblemInstance": [PROBLEM_INSTANCE], "ExecutionTime": [et - st]})])
execution_time_report.to_csv(os.path.dirname(os.path.realpath("__file__")) + "/logs/instantiation/execution_time.csv", index = False, sep=";")