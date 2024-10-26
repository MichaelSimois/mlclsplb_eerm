# -*- coding: utf-8 -*-
import sys
import time

# Get system variables
PROBLEM_INSTANCE = str(sys.argv[1])
SIMULATION_INSTANCES = str(sys.argv[2]).split(",")
CT_LIMIT = int(sys.argv[3])

# Solver function
def solve_model(problem_instance_id: str, simulation_instance_ids: list):
    from lib.MLCLSP_L_B import MLCLSP_L_B
    print("Solve problem instance = %s #" % (PROBLEM_INSTANCE))
    st = time.time()
    m = MLCLSP_L_B(
        problem_instance_id = problem_instance_id,
        simulation_instance_ids = simulation_instance_ids,
        load_connection = True
    )
    m.build()
    et = time.time()
    OPTIMIZATION_TIME = max(0, CT_LIMIT - float(et - st))
    print("Optimization time = %s #" % (OPTIMIZATION_TIME))
    m.solve(max_seconds = OPTIMIZATION_TIME)
    print("Optimization finished - Status: %s, MIP Gap: #" % (m.status, abs(m.objective_value - m.model_lb) / m.objective_value))

# Solve a problem with scenarios
solve_model(problem_instance_id = PROBLEM_INSTANCE, simulation_instance_ids = SIMULATION_INSTANCES)