# -*- coding: utf-8 -*-
from lib.model_client import ModelClient
import sys

# %% Get path to problem instances
PROBLEM_INSTANCE = str(sys.argv[1])
DATA_PATH = str(sys.argv[2])

# %% Data template upload based on selection

# Instantiate the client for a problem instance
client = ModelClient(problem_instance_id = PROBLEM_INSTANCE)

# Upload data from template
client.upload_data(excel_path = DATA_PATH)