# -*- coding: utf-8 -*-
import numpy as np
from lib.model_client import ModelClient
from mip import INTEGER, CONTINUOUS
from collections import defaultdict
import numpy as np

class IndexModel(ModelClient):
    def __init__(self, problem_instance_id, simulation_instance_ids = [], load_connection = True, disk_data = dict()):
        # Load client
        ModelClient.__init__(self, problem_instance_id, simulation_instance_ids, load_connection)
        if load_connection:
            # Load from db
            ModelClient.load_data(self)
        else:
            # Load from disk
            ModelClient.load_disk_data(self, data_dict = disk_data)

    def instantiate(self):
        # Instantiate indice sets
        self.machines = set(self.data["capacity"]["MachineId"])
        self.products = set(self.data["material"]["MaterialId"])
        self.periods = sorted(list(self.data["planning_period"]["PlanningPeriod"]))
        self.simulation_instances = set(self.data["probleminstance"]["SimulationInstanceId"])
        
        self.M = len(self.machines)
        self.P = len(self.products)
        self.T = len(self.periods)
        self.S = len(self.simulation_instances)
        
        # Instantiate initial values
        self.init_inventory = defaultdict(dict)
        self.init_backorder = defaultdict(dict)
        
        for row in self.data["initial_lot_sizing_values"].itertuples():
            self.init_inventory[row.SimulationInstanceId][row.MaterialId] = row.InitialInventory
            self.init_backorder[row.SimulationInstanceId][row.MaterialId] = row.InitialBackorder

        self.init_linked_lot_size = defaultdict(dict)

        for row in self.data["initial_linked_lot_sizing_values"].itertuples():
            self.init_linked_lot_size[row.SimulationInstanceId][row.MachineId, row.MaterialId] = row.InitialLinkedLotSize

        # Instantiate material types and unit of measures
        self.material_type = dict()
        self.material_uom  = dict()
        for row in self.data["material_type"].itertuples():
            # Filter on materials which are produced
            if row.MaterialId in self.products:
                self.material_type[(row.MaterialId)] = row.MaterialType
                self.material_uom[(row.MaterialId)] = INTEGER if row.BaseUOM == "PC" else CONTINUOUS

        # Instantiate capacities
        self.capacity = defaultdict(dict)
        for row in self.data["capacity"].itertuples():
            self.capacity[row.SimulationInstanceId][(row.MachineId, row.PlanningPeriod)] = row.CapacityPerPeriod
        
        # Instantiate material cost
        self.inventory_holding_cost = dict()
        self.backorder_cost = dict()

        for row in self.data["material_cost"].itertuples():
            self.inventory_holding_cost[(row.MaterialId, row.PlanningPeriod)] = row.InventoryHolding
            self.backorder_cost[(row.MaterialId, row.PlanningPeriod)] = row.Backorder

        # Instantiate demands
        self.demand = defaultdict(dict)

        for row in self.data["demand"].itertuples():
            self.demand[row.SimulationInstanceId][(row.MaterialId, row.PlanningPeriod)] = row.Quantity

        # Instantiate setup cost and time (sequence independent)
        self.setup_time = dict()
        self.setup_cost = dict()
        for row in self.data["setup_matrix"].itertuples():
            self.setup_time[(row.MachineId, row.MaterialId, row.PlanningPeriod)] = row.SetupTime
            self.setup_cost[(row.MachineId, row.MaterialId, row.PlanningPeriod)] = row.SetupCost
        
        # Instantiate production relevant coefficients
        self.production_time = dict()
        self.lead_time = dict()
        for row in self.data["production"].itertuples():
            self.production_time[(row.MachineId, row.MaterialId, row.PlanningPeriod)] = row.ProductionTimePerBaseUOM
            self.lead_time[(row.MachineId, row.MaterialId, row.PlanningPeriod)] = row.LeadTime
        
        # Instantiate product-to-line allocations
        self.line_to_product = defaultdict(set)
        self.product_to_line = defaultdict(set)
        for row in self.data["product_to_line"].itertuples():
            self.line_to_product[row.MachineId].add(row.MaterialId)
            self.product_to_line[row.MaterialId].add(row.MachineId)
        
        # Instantiate successor and predecessor sets 
        self.predecessor = dict()
        self.successor = dict()
        self.production_coefficient = dict()
        for row in self.data["production_structures"].itertuples():
            if (row.MachineIdGoodsReceived, row.GoodsReceived) not in self.predecessor.keys():
                self.predecessor[(row.MachineIdGoodsReceived, row.GoodsReceived, row.BOMAlternative)] = set()
            if (row.MachineIdGoodsIssued, row.GoodsIssued) not in self.successor.keys():
                self.successor[(row.MachineIdGoodsIssued, row.GoodsIssued)] = set()


        for row in self.data["production_structures"].itertuples():
            if (row.MachineIdGoodsReceived, row.GoodsReceived) != (row.MachineIdGoodsIssued, row.GoodsIssued):
                self.predecessor[(row.MachineIdGoodsReceived, row.GoodsReceived, row.BOMAlternative)].add((row.MachineIdGoodsIssued, row.GoodsIssued))
                self.successor[(row.MachineIdGoodsIssued, row.GoodsIssued)].add((row.MachineIdGoodsReceived, row.GoodsReceived, row.BOMAlternative))
                self.production_coefficient[(row.MachineIdGoodsReceived, row.GoodsReceived, row.MachineIdGoodsIssued, row.GoodsIssued, row.PlanningPeriod)] = row.Ratio
        
        # Prepare bigM value for MIP formulation
        self.big_M = defaultdict(dict)
        for row in self.data["max_production_quantity"].itertuples():
            self.big_M[row.SimulationInstanceId][(row.MachineId, row.MaterialId, row.PlanningPeriod)] = row.BigM
