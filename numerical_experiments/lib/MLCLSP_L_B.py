# -*- coding: utf-8 -*-
from mip import *
from lib.index_model import IndexModel

# Define optimization class
class MLCLSP_L_B(IndexModel):
    def __init__(self, problem_instance_id: str, simulation_instance_ids: list, load_connection = True, disk_data = dict()):
        if load_connection:
            IndexModel.__init__(self, problem_instance_id, simulation_instance_ids, load_connection)
        else:
            IndexModel.__init__(self, problem_instance_id, simulation_instance_ids, load_connection, disk_data)
        IndexModel.instantiate(self)
 
        self.model_lb = float("inf")
        self.objective_value = float("inf")
        self.optimzation_state = None
        self.optimzation_status = None
        self.solution = dict()

    def build(self, use_gbr = False):
        # Instantiate a model for cost mnimization
        if use_gbr:
            self.model = Model(sense = MINIMIZE, solver_name = GRB)
        else:
            self.model = Model(sense = MINIMIZE, solver_name = CBC)

        # Define decision variables
        x_p = dict() # Production quantity
        x_inv = dict() # Inventory on hand
        x_bo = dict() # Backorder quantity
        x_su = dict() # Machine setup operation
        x_l = dict() # Setup carry-over (linked lot size)
        x_tsu = dict() # Total setup state

        for scenario in self.simulation_instances:
            for product in self.products:
                # Initial period
                x_inv[(scenario, product, 0)] = self.model.add_var(name = "INVENTORY_ON_HAND_{}_{}_0".format(scenario, product), var_type = self.material_uom[product])
                x_bo[(scenario, product, 0)] = self.model.add_var(name = "BACKORDER_QUANTITY_{}_{}_0".format(scenario, product), var_type = self.material_uom[product])
                for machine in self.machines:
                    x_l[(scenario, machine, product, 0)] = self.model.add_var(name = "LINKED_LOT_SIZE_{}_{}_{}_0".format(scenario, machine, product), var_type = BINARY)
                
                for period in self.periods:
                    x_inv[(scenario, product, period)] = self.model.add_var(name = "INVENTORY_ON_HAND_{}_{}_{}".format(scenario, product, period), var_type = self.material_uom[product])
                    x_bo[(scenario, product, period)] = self.model.add_var(name = "BACKORDER_QUANTITY_{}_{}_{}".format(scenario, product, period), var_type = self.material_uom[product])
                    for machine in self.product_to_line[product]:
                        x_p[(scenario, machine, product, period)] = self.model.add_var(name = "PRODUCTION_QUANTITY_{}_{}_{}_{}".format(scenario, machine, product, period), var_type = self.material_uom[product])
                        x_tsu[(scenario, machine, product, period)] = self.model.add_var(name = "TOTAL_SETUP_{}_{}_{}_{}".format(scenario, machine, product, period), var_type = BINARY)
                        x_su[(scenario, machine, product, period)] = self.model.add_var(name = "SETUP_STATE_{}_{}_{}_{}".format(scenario, machine, product, period), var_type = BINARY)
                        x_l[(scenario, machine, product, period)] = self.model.add_var(name = "LINKED_LOT_SIZE_{}_{}_{}_{}".format(scenario, machine, product, period), var_type = BINARY)
        
        # Define objective function
        objective_terms = list()
        for scenario in self.simulation_instances:
            for product in self.products:
                for period in self.periods:
                    objective_terms.append(self.inventory_holding_cost[(product, period)] * x_inv[(scenario, product, period)])
                    objective_terms.append(self.backorder_cost[(product, period)] * x_bo[(scenario, product, period)])
                    for machine in self.product_to_line[product]:
                            objective_terms.append(self.setup_cost[(machine, product, period)] * x_su[(scenario, machine, product, period)])
            
            self.model.objective = minimize(1 / self.S * xsum(objective_terms))
        
        # Define constraints
        constraints = list()
        
        # Add initial and final inventories/backorders
        for scenario, dict_values in self.init_inventory.items():
            for product, initial_inventory in dict_values.items():
                constraints.append(x_inv[(scenario, product, 0)] == initial_inventory)
                constraints.append(x_inv[(scenario, product, self.T)] == 0)
        
        for scenario, dict_values in self.init_backorder.items():
            for product, initial_backorder in dict_values.items():
                constraints.append(x_bo[(scenario, product, 0)] == initial_backorder)
                constraints.append(x_bo[(scenario, product, self.T)] == 0)
        
        # Add initial linked lot-sizes
        for scenario, dict_values in self.init_linked_lot_size.items():
            for key, initial_linked_lot_size in dict_values.items():
                constraints.append(x_l[(scenario, key[0], key[1], 0)] == initial_linked_lot_size)
        
        # Production quantities equal zero if t + lead time > T
        for key, values in self.lead_time.items():
            # Positive lead times
            if values > 0:
                for t in range(self.T + 1 - values, self.T + values):
                    for scenario in self.simulation_instances: 
                        constraints.append(x_p[(scenario, key[0], key[1], t)] == 0)

        # Material balance equation
        for scenario in self.simulation_instances:
            for product in self.products:
                for period in self.periods:
                    secondary_demand = list()
                    for successor in self.successor:
                        secondary_demand.append(xsum(x_p[(scenario, successor_machine, successor, period)] for successor_machine in self.product_to_line[successor]))
                    
                    if len(secondary_demand) == 0:
                        constraints.append(x_inv[(scenario, product, period - 1)] + x_bo[(scenario, product, period)] + xsum(x_p[(scenario, machine, product, period + self.lead_time[machine, product, period])] for machine in self.product_to_line[product]) == x_inv[(scenario, product, period)] + x_bo[(scenario, product, period - 1)] + self.demand[scenario][(product, period)])
                    else:
                        constraints.append(x_inv[(scenario, product, period - 1)] + x_bo[(scenario, product, period)] + xsum(x_p[(scenario, machine, product, period + self.lead_time[machine, product, period])] for machine in self.product_to_line[product]) == x_inv[(scenario, product, period)] + x_bo[(scenario, product, period - 1)] + self.demand[scenario][(product, period)] + xsum(secondary_demand))
  
        # Capacity constraints
        for scenario in self.simulation_instances:
            for period in self.periods:
                for machine in self.machines:
                    # Capacity restriction
                    constraints_term = [self.production_time[(machine, product, period)] * x_p[(scenario, machine, product, period)] + self.setup_time[(machine, product, period)] * x_su[(scenario, machine, product, period)] for product in self.line_to_product[machine]]
                    constraints.append(xsum(constraints_term)  <= self.capacity[scenario][(machine, period)])
        
        for scenario in self.simulation_instances:
            for period in self.periods:
                for product in self.products:
                    for machine in self.product_to_line[product]:
                        # Big-M formulation
                        constraints.append(x_p[(scenario, machine, product, period)] <= self.big_M[scenario][(machine, product, period)] * (x_su[(scenario, machine, product, period)] + x_l[(scenario, machine, product, period - 1)]))
                        # Total setup definition
                        constraints.append(x_tsu[(scenario, machine, product, period)] == x_su[(scenario, machine, product, period)] + x_l[(scenario, machine, product, period - 1)])
        
        # Linked lot size synchronizations
        for scenario in self.simulation_instances:
            for period in self.periods:
                for machine in self.machines:
                    constraints_term = [x_l[(scenario, machine, product, period)] for product in self.line_to_product[machine]]
                    constraints.append(xsum(constraints_term) <= 1)
                    for product in self.line_to_product[machine]:
                        constraints.append(x_l[(scenario, machine, product, period)] - x_su[(scenario, machine, product, period)] - x_l[(scenario, machine, product, period - 1)] <= 0)
                        for product2 in self.products:
                            if product2 != product:
                                constraints.append(x_l[(scenario, machine, product, period)] + x_l[(scenario, machine, product, period - 1)] - x_su[(scenario, machine, product, period)] + x_su[(scenario, machine, product2, period)]  <= 2)
        
        self.constraints = constraints
        for constraint in self.constraints:
            self.model += constraint

    def solve(self, max_seconds = 100.0):
        status = self.model.optimize(max_seconds=max_seconds)
        result = dict()
        if status == OptimizationStatus.OPTIMAL:
            self.model_lb = self.model.objective_value
            self.objective_value = self.model.objective_value
            self.optimzation_state = "optimal solution cost {} found".format(self.model.objective_value)
        elif status == OptimizationStatus.FEASIBLE:
            self.model_lb = self.model.objective_bound
            self.objective_value = self.model.objective_value
            self.optimzation_state = "sol.cost {} found, best possible: {}".format(self.model.objective_value, self.model.objective_bound)
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            self.optimzation_state = "no feasible solution found, lower bound is: {}".format(self.model.objective_bound)
        elif status == OptimizationStatus.INFEASIBLE:
            self.optimzation_state = "model is infeasible. Check constrains."
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            for v in self.model.vars:
                result[v.name] = v.x
        
        self.optimzation_status = status
        self.solution = result
        
        return status