# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import numpy as np
from pyxlsb import convert_date

class DataDiskLoader():
    def __init__(self, PROBLEM_INSTANCE, DATA_PATH):
        # Store metadata
        self.PROBLEM_INSTANCE = PROBLEM_INSTANCE
        self.DATA_PATH = DATA_PATH

        # Read data template
        all_spreadsheets = pd.ExcelFile(DATA_PATH).sheet_names

        ProblemInstance = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "ProblemInstance"))
        SimulationInstance = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "SimulationInstance"))
        Material = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "Material"))
        Capacity = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "Capacity"))
        Demand = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "Demand"))
        MaterialCost = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "MaterialCost"))
        SetupMatrix = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "SetupMatrix"))
        BOMHeader = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "BOMHeader"))
        BOMItem = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "BOMItem"))
        if "InitialLotSizingValues" in all_spreadsheets:
            InitialLotSizingValues = self.convert_dates(pd.read_excel(DATA_PATH, sheet_name = "InitialLotSizingValues"))
        else:
            InitialLotSizingValues = pd.DataFrame(columns=["ProblemInstanceId", "SimulationInstanceId", "MaterialId", "InitialInventory", "InitialBackorder"])

        # Fill default values
        Material["BaseUOM"] = np.where(Material["BaseUOM"].isnull(), "PC", Material["BaseUOM"])
        Material["BaseCurrency"] = np.where(Material["BaseCurrency"].isnull(), "EUR", Material["BaseCurrency"])

        Capacity["Capacity"] = np.where(Capacity["Capacity"].isnull(), 0.0, Capacity["Capacity"])

        MaterialCost["InventoryHolding"] = np.where(MaterialCost["InventoryHolding"].isnull(), 0.0, MaterialCost["InventoryHolding"])
        MaterialCost["Backorder"] = np.where(MaterialCost["Backorder"].isnull(), 0.0, MaterialCost["Backorder"])
        MaterialCost["Destruction"] = np.where(MaterialCost["Destruction"].isnull(), 0.0, MaterialCost["Destruction"])

        SetupMatrix["SetupTime"] = np.where(SetupMatrix["SetupTime"].isnull(), 0.0, SetupMatrix["SetupTime"])
        SetupMatrix["SetupCost"] = np.where(SetupMatrix["SetupCost"].isnull(), 0.0, SetupMatrix["SetupCost"])

        BOMHeader["LeadTime"] = np.where(BOMHeader["LeadTime"].isnull(), 0.0, BOMHeader["LeadTime"])
        BOMHeader["ShelfLifeFix"] = np.where(BOMHeader["ShelfLifeFix"].isnull(), 0.0, BOMHeader["ShelfLifeFix"])
        BOMHeader["ProductionCost"] = np.where(BOMHeader["ProductionCost"].isnull(), 0.0, BOMHeader["ProductionCost"])

        BOMItem["Ratio"] = np.where(BOMItem["Ratio"].isnull(), 1.0, BOMItem["Ratio"])
        BOMItem["ScrapFix"] = np.where(BOMItem["ScrapFix"].isnull(), 0.0, BOMItem["ScrapFix"])
        BOMItem["ScrapVariable"] = np.where(BOMItem["ScrapVariable"].isnull(), 0.0, BOMItem["ScrapVariable"])
        BOMItem["ShelfLifeVariable"] = np.where(BOMItem["ShelfLifeVariable"].isnull(), 0.0, BOMItem["ShelfLifeVariable"])

        InitialLotSizingValues["InitialInventory"] = np.where(InitialLotSizingValues["InitialInventory"].isnull(), 0.0, InitialLotSizingValues["InitialInventory"])
        InitialLotSizingValues["InitialBackorder"] = np.where(InitialLotSizingValues["InitialBackorder"].isnull(), 0.0, InitialLotSizingValues["InitialBackorder"])

        # Create V_PlanningBuckets
        planning_bucket = ProblemInstance["PlanningBuckets"].iloc[0]
        planning_bucket = planning_bucket.replace(" WEEK", "W") 
        planning_bucket = planning_bucket.replace(" MONTH", "M")
        planning_bucket = planning_bucket.replace(" QUARTER", "Q") 
        planning_bucket = planning_bucket.replace(" YEAR", "Y") 

        V_PlanningBuckets = ProblemInstance.filter(["ProblemInstanceId"]).copy()
        V_PlanningBuckets["PlanningBuckets"] = planning_bucket
        V_PlanningBuckets["PlanningEndDate"] = Capacity["ValidityDateTo"].max()
        V_PlanningBuckets["PlanningStartDate"] = Capacity["ValidityDateFrom"].min()

        # Create V_PlanningPeriod
        V_PlanningPeriod = pd.DataFrame(columns=["PlanningDate"], 
                            data = pd.date_range(
                                V_PlanningBuckets["PlanningStartDate"].iloc[0], 
                                V_PlanningBuckets["PlanningEndDate"].iloc[0] + datetime.timedelta(days=400), 
                                freq=V_PlanningBuckets["PlanningBuckets"].iloc[0], inclusive='both'))
        V_PlanningPeriod["PlanningDate"] = V_PlanningPeriod["PlanningDate"].dt.to_period(V_PlanningBuckets["PlanningBuckets"].iloc[0]).dt.start_time
        V_PlanningPeriod = V_PlanningPeriod[V_PlanningPeriod["PlanningDate"] <= V_PlanningBuckets["PlanningEndDate"].iloc[0]]
        V_PlanningPeriod["ProblemInstanceId"] = PROBLEM_INSTANCE

        V_PlanningPeriod = ProblemInstance.merge(V_PlanningPeriod, how = "inner", on = ["ProblemInstanceId"]) \
            .filter(["ProblemInstanceId", "PlanningBuckets", "PlanningDate"]) \
            .sort_values("PlanningDate")
        V_PlanningPeriod["PlanningPeriod"] = range(1, V_PlanningPeriod.shape[0] + 1)
        V_PlanningPeriod["PlanningStartDate"] = V_PlanningBuckets["PlanningStartDate"].iloc[0]
        V_PlanningPeriod["PlanningEndDate"] = V_PlanningBuckets["PlanningEndDate"].iloc[0]
        V_PlanningPeriod = V_PlanningPeriod.filter(["ProblemInstanceId", "PlanningStartDate", "PlanningEndDate", 
                                                    "PlanningBuckets", "PlanningDate", "PlanningPeriod"])

        # Create V_PeriodExpand
        V_PeriodExpand = V_PlanningPeriod.merge(Material, how = "inner", on = ["ProblemInstanceId"]) \
            .merge(SimulationInstance, how = "inner", on = ["ProblemInstanceId"]) \
            .filter(["ProblemInstanceId", "SimulationInstanceId", "MaterialId", "PlanningStartDate", "PlanningEndDate", 
                    "PlanningBuckets", "PlanningDate", "PlanningPeriod"])

        # Create V_Capacity
        V_Capacity = V_PlanningPeriod.merge(Capacity, how = "inner", on = ["ProblemInstanceId"])
        V_Capacity = V_Capacity[(V_Capacity["ValidityDateTo"] >= V_Capacity["PlanningDate"]) & (V_Capacity["ValidityDateFrom"] <= V_Capacity["PlanningDate"])]
        V_Capacity["DaysInPlanningHorizon"] = ((V_PlanningBuckets["PlanningEndDate"] - V_PlanningBuckets["PlanningStartDate"]).dt.days + 1).max()
        V_Capacity["CapacityDayRange"] = ((V_Capacity["ValidityDateTo"] - V_Capacity["ValidityDateFrom"]).dt.days + 1).max()
        V_Capacity["MaxPlanningPeriods"] = V_PlanningPeriod["PlanningPeriod"].max()
        V_Capacity["CapacityPerPeriod"] = V_Capacity["Capacity"] / (V_Capacity["CapacityDayRange"] * V_Capacity["MaxPlanningPeriods"] / V_Capacity["DaysInPlanningHorizon"])
        V_Capacity = V_Capacity.filter(["ProblemInstanceId", "SimulationInstanceId", "MachineId", "PlanningDate", "PlanningPeriod", "PlanningBuckets", "CapacityPerPeriod"])

        # Create V_ProductToLine
        V_ProductToLine = SetupMatrix[["ProblemInstanceId", "MachineId", "MaterialIdFrom"]] \
            .drop_duplicates() \
            .rename(columns = {"MaterialIdFrom": "MaterialId"})

        # Create V_SetupMatrix
        V_SetupMatrix = SetupMatrix.merge(V_PlanningPeriod, how = "inner", on = ["ProblemInstanceId"])
        V_SetupMatrix = V_SetupMatrix[(V_SetupMatrix["ValidityDateTo"] >= V_SetupMatrix["PlanningDate"]) & (V_SetupMatrix["ValidityDateFrom"] <= V_SetupMatrix["PlanningDate"])]
        V_SetupMatrix = V_SetupMatrix.groupby(["ProblemInstanceId", "MachineId", "MaterialIdFrom", "PlanningDate", "PlanningPeriod"])[["SetupTime", "SetupCost"]].agg(np.mean).reset_index() \
            .rename(columns = {"MaterialIdFrom": "MaterialId"}) \
            .filter(["ProblemInstanceId", "MachineId", "MaterialId", "PlanningDate", 
                    "PlanningPeriod", "SetupTime", "SetupCost"])

        # Create V_Production
        V_Production = BOMHeader.merge(V_PlanningPeriod, how = "inner", on = ["ProblemInstanceId"])
        V_Production = V_Production[(V_Production["ValidityDateTo"] >= V_Production["PlanningDate"]) & (V_Production["ValidityDateFrom"] <= V_Production["PlanningDate"])]
        V_Production = V_Production.rename(columns = {"ProductionTime": "ProductionTimePerBaseUOM", "ProductionCost": "ProductionCostPerBaseUOM"})
        V_Production = V_Production.filter(["ProblemInstanceId", "MachineId", "MaterialId", "PlanningDate", "PlanningPeriod", 
                                            "LeadTime", "ProductionTimePerBaseUOM", "ProductionCostPerBaseUOM", "BatchSizeFix", 
                                            "LotSizeMin", "LotSizeMax", "ShelfLifeFix", "ShelfLifeType"])

        # Create V_ProductStructures
        V_ProductStructures = BOMHeader.merge(V_PlanningPeriod, how = "inner", on = ["ProblemInstanceId"])
        V_ProductStructures = V_ProductStructures[(V_ProductStructures["ValidityDateTo"] >= V_ProductStructures["PlanningDate"]) & (V_ProductStructures["ValidityDateFrom"] <= V_ProductStructures["PlanningDate"])]

        production_structure_helper = BOMItem.merge(
                    BOMHeader[["ProblemInstanceId", "MaterialId", "MachineId"]].drop_duplicates(), 
                    how = "inner", 
                    on = ["ProblemInstanceId", "MaterialId"]) \
            .rename(columns = {"MachineId": "MachineIdGoodsIssued", "MaterialId": "GoodsIssued"})

        V_ProductStructures = V_ProductStructures.merge(
                production_structure_helper,
                how = "left", 
                on = ["ProblemInstanceId", "BOMHeaderId"]) \
            .rename(columns = {"MachineId": "MachineIdGoodsReceived", "MaterialId": "GoodsReceived"}) \
            .filter(["ProblemInstanceId", "MachineIdGoodsReceived", "GoodsReceived", "MachineIdGoodsIssued", "GoodsIssued", 
                    "PlanningDate", "PlanningPeriod", "BOMAlternative", "Ratio", "ScrapFix", "ScrapVariable",
                    "ShelfLifeVariable"])

        V_ProductStructures = V_ProductStructures[~V_ProductStructures["GoodsIssued"].isnull()]

        # Create V_MaterialType
        V_MaterialType = Material.merge(
                V_ProductStructures[["ProblemInstanceId", "GoodsReceived"]].drop_duplicates(), 
                how = "left", left_on = ["ProblemInstanceId", "MaterialId"], 
                right_on = ["ProblemInstanceId", "GoodsReceived"]) \
            .merge(
                V_ProductStructures[["ProblemInstanceId", "GoodsIssued"]].drop_duplicates(), 
                how = "left", left_on = ["ProblemInstanceId", "MaterialId"], 
                right_on = ["ProblemInstanceId", "GoodsIssued"]) \
            .merge(
                V_SetupMatrix[["ProblemInstanceId", "MaterialId"]].drop_duplicates(), 
                how = "left", 
                on = ["ProblemInstanceId", "MaterialId"])
        V_MaterialType["MaterialType"] = np.where(
            (V_MaterialType["MaterialId"] == V_MaterialType["GoodsReceived"]) & (V_MaterialType["GoodsIssued"].isnull()) & (V_MaterialType["MaterialId"] == V_MaterialType["MaterialId"]),
            "FINISHED_GOOD",
            np.where(
                (V_MaterialType["MaterialId"] == V_MaterialType["GoodsIssued"]) & (V_MaterialType["MaterialId"] == V_MaterialType["MaterialId"]),
                "INTERMEDIATE",
                np.where(
                    (V_MaterialType["GoodsReceived"].isnull()) & (V_MaterialType["GoodsIssued"].isnull()) & (~V_MaterialType["MaterialId"].isnull()),
                    "FINISHED_GOOD",
                    "RAW_MATERIAL"
                    )
                )
            )
        V_MaterialType = V_MaterialType.filter(["ProblemInstanceId", "MaterialId", "BaseUOM", "BaseCurrency", "MaterialType"]) \
            .drop_duplicates()
            

        # Create V_Material
        V_Material = V_MaterialType[V_MaterialType["MaterialType"] != "RAW_MATERIAL"].copy()

        # Create V_MaterialCost
        V_MaterialCost = MaterialCost.merge(V_PlanningPeriod, how = "inner", on = ["ProblemInstanceId"]) \
            .merge(V_Material, how = "inner", on = ["ProblemInstanceId", "MaterialId"])

        V_MaterialCost = V_MaterialCost[(V_MaterialCost["ValidityDateTo"] >= V_MaterialCost["PlanningDate"]) & (V_MaterialCost["ValidityDateFrom"] <= V_MaterialCost["PlanningDate"]) & (~V_MaterialCost["InventoryHolding"].isnull()) & (~V_MaterialCost["Backorder"].isnull())]
        V_MaterialCost = V_MaterialCost.filter(["ProblemInstanceId", "MaterialId", "InventoryHolding", "Backorder", "PlanningDate", "PlanningPeriod"])

        # Create V_PrimaryDemand
        date_range_demand = pd.date_range(
            V_PlanningBuckets["PlanningStartDate"].iloc[0], 
            V_PlanningBuckets["PlanningEndDate"].iloc[0] + datetime.timedelta(days=400), 
            freq=V_PlanningBuckets["PlanningBuckets"].iloc[0], inclusive='both')

        V_PrimaryDemand = pd.DataFrame(columns=["PlanningDate"], data = date_range_demand)
        V_PrimaryDemand["PlanningDate"] = V_PrimaryDemand["PlanningDate"].dt.to_period(V_PlanningBuckets["PlanningBuckets"].iloc[0]).dt.start_time
        date_range_demand_to = V_PrimaryDemand["PlanningDate"]
        V_PrimaryDemand = V_PrimaryDemand[V_PrimaryDemand["PlanningDate"] <= V_PlanningBuckets["PlanningEndDate"].iloc[0]]
        V_PrimaryDemand["PlanningDateTo"] = date_range_demand_to[1:(V_PrimaryDemand.shape[0] + 1)].tolist()
        V_PrimaryDemand["ProblemInstanceId"] = PROBLEM_INSTANCE
        V_PrimaryDemand = V_PrimaryDemand.merge(Demand, how = "inner", on = ["ProblemInstanceId"])
        V_PrimaryDemand = V_PrimaryDemand[(V_PrimaryDemand["DeliveryDate"] >= V_PrimaryDemand["PlanningDate"]) & (V_PrimaryDemand["DeliveryDate"] < V_PrimaryDemand["PlanningDateTo"])]
        V_PrimaryDemand = V_PrimaryDemand.merge(V_PeriodExpand, how = "right", on = ["ProblemInstanceId", "PlanningDate", "MaterialId", "SimulationInstanceId"])
        V_PrimaryDemand["Quantity"] = np.where(V_PrimaryDemand["Quantity"].isnull(), 0 , V_PrimaryDemand["Quantity"])
        V_PrimaryDemand = V_PrimaryDemand.groupby(["ProblemInstanceId", "SimulationInstanceId", "MaterialId", "PlanningDate", "PlanningPeriod"])["Quantity"].agg("sum").reset_index() \
            .rename(columns = {"PlanningDate": "DeliveryDate"})

        # Create V_ProblemInstance
        V_ProblemInstance = ProblemInstance.merge(SimulationInstance, how = "inner", on = ["ProblemInstanceId"]) \
            .filter(["ProblemInstanceId", "ProblemInstanceName", "SimulationInstanceId", "MaterialId", "SimulationInstanceName", "ProductionStages"])

        # Create V_MaxProductionQuantity
        V_MaxProductionQuantity = V_PrimaryDemand.copy()

        V_MaxProductionQuantity["QuantityCumSum"] = V_PrimaryDemand.sort_values(["ProblemInstanceId", "SimulationInstanceId", "MaterialId", "PlanningPeriod"]) \
            .groupby(["ProblemInstanceId", "SimulationInstanceId", "MaterialId"])["Quantity"] \
            .cumsum()

        V_MaxProductionQuantity = V_MaxProductionQuantity.merge(V_ProductToLine, how = "inner", on = ["ProblemInstanceId", "MaterialId"])
        V_MaxProductionQuantity = V_MaxProductionQuantity.merge(V_Production[["ProblemInstanceId", "MachineId", "MaterialId", "PlanningPeriod", "ProductionTimePerBaseUOM"]], how = "inner", on = ["ProblemInstanceId", "MachineId", "MaterialId", "PlanningPeriod"])
        V_MaxProductionQuantity = V_MaxProductionQuantity.merge(V_Capacity[["ProblemInstanceId", "SimulationInstanceId", "MachineId", "PlanningPeriod", "CapacityPerPeriod"]], how = "inner", on = ["ProblemInstanceId", "SimulationInstanceId", "MachineId", "PlanningPeriod"])
        V_MaxProductionQuantity["MaxProductionQuantity"] = np.where(V_MaxProductionQuantity["ProductionTimePerBaseUOM"] == 0, 0, V_MaxProductionQuantity["CapacityPerPeriod"] / V_MaxProductionQuantity["ProductionTimePerBaseUOM"])
        V_MaxProductionQuantity["BigM"] = np.where(V_MaxProductionQuantity["QuantityCumSum"] <= V_MaxProductionQuantity["MaxProductionQuantity"], V_MaxProductionQuantity["QuantityCumSum"], V_MaxProductionQuantity["MaxProductionQuantity"])
        V_MaxProductionQuantity = V_MaxProductionQuantity.filter(["ProblemInstanceId", "SimulationInstanceId", "MachineId", "MaterialId", "PlanningPeriod", "BigM"])

        # Create V_InitialLotSizingValues
        V_InitialLotSizingValues = Material.merge(SimulationInstance, how = "inner", on = ["ProblemInstanceId"]) \
            .merge(InitialLotSizingValues, how = "left", on = ["ProblemInstanceId", "SimulationInstanceId", "MaterialId"]) \
            .filter(["ProblemInstanceId", "SimulationInstanceId", "MaterialId", "InitialInventory", "InitialBackorder", "InitialLinkedLotSize"]) \
            .fillna(0)

        # Save data
        self.ProblemInstance = ProblemInstance
        self.SimulationInstance = SimulationInstance
        self.Material = Material
        self.Capacity = Capacity
        self.Demand = Demand
        self.MaterialCost = MaterialCost
        self.SetupMatrix = SetupMatrix
        self.BOMHeader = BOMHeader
        self.BOMItem = BOMItem
        self.InitialLotSizingValues = InitialLotSizingValues

        # Save views
        self.V_ProblemInstance = V_ProblemInstance
        self.V_Capacity = V_Capacity
        self.V_PrimaryDemand = V_PrimaryDemand
        self.V_Material = V_Material
        self.V_MaterialCost = V_MaterialCost
        self.V_MaterialType = V_MaterialType
        self.V_PlanningPeriod = V_PlanningPeriod
        self.V_Production = V_Production
        self.V_ProductStructures = V_ProductStructures
        self.V_ProductToLine = V_ProductToLine
        self.V_SetupMatrix = V_SetupMatrix
        self.V_InitialLotSizingValues = V_InitialLotSizingValues
        self.V_MaxProductionQuantity = V_MaxProductionQuantity
        
        # Prepare data for model consumption
        self.data_disk_load = {
            "probleminstance": V_ProblemInstance,
            "capacity": V_Capacity,
            "demand": V_PrimaryDemand,
            "material": V_Material,
            "material_cost": V_MaterialCost,
            "material_type": V_MaterialType,
            "planning_period": V_PlanningPeriod,
            "production": V_Production,
            "production_structures": V_ProductStructures,
            "product_to_line": V_ProductToLine,
            "setup_matrix": V_SetupMatrix,
            "initial_lot_sizing_values": V_InitialLotSizingValues,
            "max_production_quantity": V_MaxProductionQuantity
            }

        # %% Helperfunctions
    def convert_dates(self, data):
        data = data[data["ProblemInstanceId"] == self.PROBLEM_INSTANCE].copy()
        if "ValidityDateTo" in data.columns:
            data["ValidityDateTo"] = data.apply(lambda x: convert_date(x['ValidityDateTo']), axis=1)
        if "ValidityDateFrom" in data.columns:
            data["ValidityDateFrom"] = data.apply(lambda x: convert_date(x['ValidityDateFrom']), axis=1)
        if "DeliveryDate" in data.columns:
            data["DeliveryDate"] = data.apply(lambda x: convert_date(x['DeliveryDate']), axis=1)
        return data