# -*- coding: utf-8 -*-
from memory_profiler import profile
import sys
import os
import time

SOURCE = str(sys.argv[1])
PROBLEM_INSTANCE = str(sys.argv[2])
DATA_PATH = os.path.dirname(os.path.realpath("__file__")) + str(sys.argv[3])

print("Memory profiling of instantiation (Disk load): Problem instance = %s" % (PROBLEM_INSTANCE))

fp = open("logs/instantiation/model_instantiation_disk_load_" + PROBLEM_INSTANCE + ".log", "w+")
@profile(stream = fp)
def instantiate_model(problem_instance_id, data_path):
    # For data preparation
    from lib.index_model import IndexModel
    from lib.prepare_data_in_memory import DataDiskLoader
    disk_load = DataDiskLoader(problem_instance_id, data_path)

    index_model = IndexModel(
        problem_instance_id = problem_instance_id,
        load_connection = False, 
        disk_data = disk_load.data_disk_load
    )
    index_model.instantiate()

st = time.time()
instantiate_model(problem_instance_id = PROBLEM_INSTANCE, data_path = DATA_PATH)
et = time.time()
print("#### Script executed successfully after", et - st, "seconds #####")

# %% Save execution time
import pandas as pd
execution_time_report = pd.read_csv(os.path.dirname(os.path.realpath("__file__")) + "/logs/instantiation/execution_time.csv", sep=";")
execution_time_report = pd.concat([execution_time_report, pd.DataFrame(data = {"Source": [SOURCE], "LoadingType": ["DISK"], "ProblemInstance": [PROBLEM_INSTANCE], "ExecutionTime": [et - st]})])
execution_time_report.to_csv(os.path.dirname(os.path.realpath("__file__")) + "/logs/instantiation/execution_time.csv", index = False, sep=";")