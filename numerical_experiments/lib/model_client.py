# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
import pandas as pd
from pyxlsb import convert_date
import json
import os
import tempfile

class ModelClient:
    def __init__(self, problem_instance_id = None, simulation_instance_ids = [], load_connection = True):

        # Load JSON configuration
        self.project_path = os.path.dirname(os.path.realpath("__file__"))
        self.problem_instance_id = problem_instance_id
        self.simulation_instance_ids = simulation_instance_ids

        if load_connection:
            f = open(self.project_path + "/lib/connection.json",)
            self.config = json.load(f)
            self.engine = create_engine("postgresql://%s:%s@%s/%s" % (self.config["user"], self.config["password"], self.config["host"], self.config["database"]))
        
        # Define available data sources
        self.data = dict()
        self.prepared_data = dict()
        self.data_def = [
            {"view": "V_ProblemInstance", "data_key": "probleminstance"},
            {"view": "V_Capacity", "data_key": "capacity"},
            {"view": "V_PrimaryDemand", "data_key": "demand"},
            {"view": "V_Material", "data_key": "material"},
            {"view": "V_MaterialCost", "data_key": "material_cost"},
            {"view": "V_MaterialType", "data_key": "material_type"},
            {"view": "V_PlanningPeriod", "data_key": "planning_period"},
            {"view": "V_Production", "data_key": "production"},
            {"view": "V_ProductStructures", "data_key": "production_structures"},
            {"view": "V_ProductToLine", "data_key": "product_to_line"},
            {"view": "V_SetupMatrix", "data_key": "setup_matrix"},
            {"view": "V_InitialLotSizingValues", "data_key": "initial_lot_sizing_values"},
            {"view": "V_InitialLinkedLotSizingValues", "data_key": "initial_linked_lot_sizing_values"},
            {"view": "V_MaxProductionQuantity", "data_key": "max_production_quantity"}
        ]
        self.table_names = ["ProblemInstance", "SimulationInstance", "Material", "Capacity", "Demand", "MaterialCost", "SetupMatrix", "BOMHeader", "BOMItem", "InitialLotSizingValues"]

    def set_problem_instance_id(self, problem_instance_id: str):
        self.problem_instance_id = problem_instance_id

    def load_disk_data(self, data_dict):
        for key, data in data_dict.items():
            
            self.data[key] = data.copy()
            print("Read data %s from disk sucessfully" % key)

    def upload_data(self, excel_path, problem_instance_id = None):
        if problem_instance_id is not None:
            self.problem_instance_id = problem_instance_id

        self.truncate_data()
        all_spreadsheets = pd.ExcelFile(self.project_path + excel_path).sheet_names

        for table_name in self.table_names:
            if table_name not in all_spreadsheets:
                print("Info: Spreadsheet %s of the EER model was not found, using default values instead" % table_name)
                continue
            data = pd.read_excel(self.project_path + excel_path, sheet_name = table_name)
            if "ValidityDateTo" in data.columns:
                data["ValidityDateTo"] = data.apply(lambda x: convert_date(x['ValidityDateTo']), axis=1)
            if "ValidityDateFrom" in data.columns:
                data["ValidityDateFrom"] = data.apply(lambda x: convert_date(x['ValidityDateFrom']), axis=1)
            if "DeliveryDate" in data.columns:
                data["DeliveryDate"] = data.apply(lambda x: convert_date(x['DeliveryDate']), axis=1)
            data = data[data["ProblemInstanceId"] == self.problem_instance_id]
            with self.engine.begin() as connection:
                data.to_sql(table_name, con = connection, if_exists = "append", index = False)
                print("Uploaded data to table %s succesfully with problem instance id %s" % (table_name, self.problem_instance_id))

    def truncate_data(self, delete_all = False):
        tables_to_truncate = self.table_names.copy()
        tables_to_truncate.reverse()
        for table_name in tables_to_truncate:
            with self.engine.begin() as connection:
                if delete_all:
                    connection.execute("TRUNCATE TABLE \"%s\"" % (table_name))
                    print("Truncate table %s succesfully" % (table_name))
                else:
                    connection.execute("DELETE FROM \"%s\" WHERE \"ProblemInstanceId\" = '%s'" % (table_name, self.problem_instance_id))
                    print("Deleted data in table %s succesfully for the problem instance %s" % (table_name, self.problem_instance_id))

    def load_data(self):
        si_filter = list()
        for i in self.simulation_instance_ids:
            si_filter.append("'" + i + "'")

        connection = self.engine.raw_connection()
        for data_dict in self.data_def:
            # Problem instance dependent views
            if (len(self.simulation_instance_ids) == 0) | (data_dict["data_key"] in ["material", "material_cost", "material_type", "planning_period",
                                         "production", "production_structures", "product_to_line", "setup_matrix"]):
                self.data[data_dict["data_key"]] = self.__read_sql_tmpfile(conn = connection, query = "SELECT * FROM \"%s\" where \"ProblemInstanceId\" = '%s'" % (data_dict["view"], self.problem_instance_id))
            # Problem and simulation instance dependent views
            else:
                self.data[data_dict["data_key"]] = self.__read_sql_tmpfile(conn = connection, query = "SELECT * FROM \"%s\" where \"ProblemInstanceId\" = '%s' AND \"SimulationInstanceId\" IN (%s)" % (data_dict["view"], self.problem_instance_id, ",".join(si_filter)))
            
            print("Loaded model %s succesfully" % (data_dict["data_key"]))

    def __read_sql_tmpfile(self, conn, query):
        with tempfile.TemporaryFile() as tmpfile:
            copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(query=query, head="HEADER")
            cur = conn.cursor()
            cur.copy_expert(copy_sql, tmpfile)
            tmpfile.seek(0)
            df = pd.read_csv(tmpfile)
            return df