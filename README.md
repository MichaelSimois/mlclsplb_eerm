# Multi-level capacitated lot-sizing problems with probabilistic demand and relational database structures
Multi-level capacitated lot-sizing problems with linked lot sizes and backorders (MLCLSP-L-B) are used in pharmaceutical tablets manufacturing processes to right-size material production lots such that costs are kept at a minimum, production resource capacities are not exceeded, and customer demand is fulfilled. An uncertain demand behavior characterizes today’s global tablets market. Global pharmaceutical players request solution approaches that solve the MLCLSP-L-B with probabilistic demand. 
Implementing this model in industrial applications for tablets manufacturing systems requires efficient data processing due to the amount of data and the capability to store simulated demand scenarios.
This repository covers the first integration of the MLCLSP-L-B with probabilistic demands and relational database structures.

## Content
- Dockerfile: Sets up a ubuntu 22.04.1 system with PostgreSQL 14.9 database, and a Python 3.10.12 runtime environment.
- requirements.txt: Lists all Python dependencies that should be installed in the Docker image.
- init.sql: SQL script that contains all comands to create the EER model.
- docker-compose.yml: Lists all services that should run at the same time. The file maps the Dockerfile on the lot_sizing service, and the Adminer data management software to the adminer service.
- numerical_experiments\lib\: Contains Python scripts to upload, instantiate, and solve the MLCLSP-L-B.
- numerical_experiments\logs\: Directory that contains the model upload and instantiation analysis results.
- numerical_experiments\research_data\: Directory that contains the raw and migrated research datasets TAB_MAN, C_1_6, DATAB, and MULTISB.
- numerical_experiments\upload_data.sh: Bash script that uploads all migrated research data in the PostgreSQL database.
- numerical_experiments\run_instantiation_experiments.sh: Bash script that instantiates all uploaded research data from the PostgreSQL database for the MLCLSP-L-B.
- numerical_experiments\solve_model.py: Python script that solves a particular problem instance and a list of simulation instances from uploaded research data from the PostgreSQL database.

## Getting started

To make it easy for you to get started with this project, here's a list of recommended next steps.

1. Clone the repository on your computer.
2. Make sure, Docker and Docker Compose is installed on your computer ([link to docker docs](https://docs.docker.com/compose/install/)).
3. Run the command 'docker compose up' in the command line (takes approx. 6 minutes the first time). If you want to recreate the docker image, then run 'docker-compose up --build'. If a rebuild without cache should be executed, remove all containers and volumes and execute 'docker-compose build --no-cache'
4. After a successful build, two services are up and running: lot_sizing and adminer.


## Upload data
The data upload is executed manually via the command 'sh upload_data.sh' in the terminal. All problem instances from 'numerical_experiments/ProblemInstances.csv' are uploaded to the PostgreSQL database (takes approx. 90 minutes).

## Instantiate MIP
The experiment for model instantiations (processing time and RAM consumption) is executed manually via the command 'sh run_instantiation_experiments.sh' in the terminal. All problem instances from 'numerical_experiments/ProblemInstances.csv' are instantiated from PostgreSQL database and from disk load (takes approx. 4 hours).

## Solve a problem with CBC open-solver
The experiments that solve the MLCLSP-L-B with Gurobi are not available since Gurobi solver requires a commercial license.
However, a CBC open-source solver API is provided. Generally speaking, open-source solvers are performing much worse than commercial solvers. Moreover, open-source solvers often have not all tuning parameters available. Thus, the CBC solver scripts should be used for test purposes only (commercial solvers are recommended for researchers and practitioners who run studies for capacitated lot-sizing problems).
The CBC solver test scripts can be executed with the command 'python3 solve_model.py $PI $SI $CT_LIMIT' whereby the parameters can be set as follows: 
- $PI = MODEL001
- $SI = D1T1_0,D1T1_1,D1T1_2
- $CT_LIMIT = 600 (in seconds)

## Persistent table definitions
The following list provides a definition and a description of the persistent tables
within the ER model. The SQL syntax definitions are available in the file init.sql. 
First, the technical entity name is defined. Next, a description of the table’s purpose is provided by the quotes. Column type, default values,
and relationship definitions are listed in square brackets, followed by a column description.
1. ProblemInstance: "Lists all available problem instances"
* ProblemInstanceId [Varchar 36, Primary Key]: Unique problem instance identifier.
* ProblemInstanceName [Varchar 100, Default NULL]: Name of a problem instance.
* PlanningBuckets [Varchar 10, Default ’1 WEEK’]: Planning buckets representing a planning
period.
* ProductionStages [Integer, Default NULL]: Amount of production stages.
2. SimulationInstance: "Lists all available simulation instances (scenarios) per
problem instance"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on ProblemInstance]:
Unique problem instance identifier.
* SimulationInstanceId [Varchar 36, Primary Key]: Unique simulation instance identifier.
* SimulationInstanceName [Varchar 100, Default NULL]: Name of a simulation instance.
3. Material: "Lists all available materials for a problem instance"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on ProblemInstance]:
Problem instance identifier.
* MaterialId [Varchar 36, Primary Key]: Material identifier.
* MaterialName [Varchar 100, Default NULL]: Name of a material.
* BaseUOM [Varchar 100, Default ’PC’]: Base unit of measure for a material.
* BaseCurrency [Varchar 100, Default ’EUR’]: Base currency of a material.
4. Capacity: "Maps to each problem and simulation instance a set of machines
with their capacity over a validity horizon"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on SimulationInstance]:
Problem instance identifier.
* SimulationInstanceId [Varchar 36, Primary Key, Foreign Key constraint on SimulationIn-
stance]: Simulation instance identifier.
* MachineId [Varchar 36, Primary Key]: Machine identifier.
* ValidityDateTo [Date, Primary Key]: End of validity horizon.
* ValidityDateFrom [Date, Not NULL]: Start of validity horizon.
* Capacity [Decimal, Default 0]: Capacity of a machine over the validity horizon.
* MachineName [Varchar 100, Default NULL]: Name of a machine.
5. Demand: "Maps to each problem and simulation instance a requested material with a delivery date and delivery quantity"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on SimulationInstance
and Material]: Problem instance identifier.
* SimulationInstanceId [Varchar 36, Primary Key, Foreign Key constraint on SimulationIn-
stance]: Simulation instance identifier.
* MaterialId [Varchar 36, Primary Key, Foreign Key constraint on Material]: Material identifier.
* DeliveryDate [Date, Primary Key]: Delivery date of a material.
* Quantity [Decimal, Not NULL]: Delivery quantity of a material.
6. MaterialCost: "Lists all material-relevant costs per problem instance across a
validity horizon"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on Material]: Problem
instance identifier.
* MaterialId [Varchar 36, Primary Key, Foreign Key constraint on Material]: Material identifier.
* ValidityDateTo [Date, Primary Key]: End of validity horizon.
* ValidityDateFrom [Date, Not NULL]: Start of validity horizon.
* InventoryHolding [Decimal, Default 0]: Inventory costs per stored unit of a material.
* Backorder [Decimal, Default 0]: Backorder costs per stored unit of a material.
* Destruction [Decimal, Default 0]: Destruction costs per stored unit of a material.
7. SetupMatrix: "Maps to each problem instance available setup operations per
machine and allocated materials over a validity horizon"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on Material]: Problem
instance identifier.
* MachineId [Varchar 36, Primary Key]: Machine identifier.
* MaterialIdFrom [Varchar 36, Primary Key, Foreign Key constraint on Material]: From material identifier of a possible setup operation.
* MaterialIdto [Varchar 36, Primary Key, Foreign Key constraint on Material]: To material
identifier of a possible setup operation.
* ValidityDateTo [Date, Primary Key]: End of validity horizon.
* ValidityDateFrom [Date, Not NULL]: Start of validity horizon.
* SetupFamilyIdFrom [Varchar 36, Default NULL]: Assigned setup family of MaterialIdFrom.
* SetupFamilyIdTo [Varchar 36, Default NULL]: Assigned setup family of MaterialIdTo.
* SetupTime [Decimal, Default 0]: Setup time per setup operation.
* SetupCost [Decimal, Default 0]: Setup cost per setup operation.
8. BOMHeader: "Lists for each problem instance allocated materials on machines with production-relevant information across a validity horizon"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on Material]: Problem
instance identifier.
* BOMHeaderId [Varchar 36, Primary Key]: BOM header identifier.
* MachineId [Varchar 36, Not NULL]: Machine identifier.
* MaterialId [Varchar 36, Not NULL, Foreign Key constraint on Material]: Material identifier.
* ValidityDateTo [Date, Primary Key]: End of validity horizon.
* ValidityDateFrom [Date, Not NULL]: Start of validity horizon.
* LeadTime [Decimal, Default 0]: Lead time of an allocated material.
* ShelfLifeType [VARCHAR(36), Default NULL]: Shelf-life type of an allocated material.
* ShelfLifeFix [Decimal, Default 0]: Fix value of shelf-life of an allocated material.
* ProductionTime [Decimal, Not NULL]: Production time per unit of an allocated material.
* ProductionCost [Decimal, Default 0]: Production cost per unit of an allocated material.
* BatchSizeFix [Decimal, Default NULL]: Fixed batch size per unit of an allocated material.
* LotSizeMin [Decimal, Default NULL]: Minimum lot size of an allocated material.
* LotSizeMax [Decimal, Default NULL]: Maximum lot size of an allocated material.
9. BOMItem: "Lists for each BOM header entry production interdependencies
(BOM items)"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on Material]: Problem
instance identifier.
* BOMHeaderId [Varchar 36, Primary Key]: BOM header identifier.
* BOMItemId [Varchar 36, Primary Key]: BOM item identifier.
* BOMAlternative [Varchar 36, Not NULL]: BOM alternative identifier.
* MaterialId [Varchar 36, Not NULL, Foreign Key constraint on Material]: Material identifier.
* Ratio [Decimal, Default 1]: Production coefficient of a BOM header and a BOM item identifier.
* ScrapFix [Decimal, Default 0]: Fix scrap quantity of a BOM header and a BOM item identifier.
* ScrapVariable [Decimal, Default 0]: Proportional scrap quantity of a BOM header and a
BOM item identifier.
* ShelfLifeVariable [Decimal, Default 0]: Variable shelf-life of a BOM header and a BOM item
identifier.
10. InitialLotSizingValues: "Lists for each problem and simulation instance ini-
tial and final inventory quantities, backorder quantities, and initial linked lot
sizes"
* ProblemInstanceId [Varchar 36, Primary Key, Foreign Key constraint on SimulationInstance
and Material]: Problem instance identifier.
* SimulationInstanceId [Varchar 36, Primary Key, Foreign Key constraint on SimulationIn-
stance]: Simulation instance identifier.
* MaterialId [Varchar 36, Primary Key, Foreign Key constraint on Material]: Material identifier.
* MachineId [Varchar 36]: Assigned machine for an initial linked lot size.
* InitialInventory [Decimal, Default 0]: Initial inventory quantity of a material.
* FinalInventory [Decimal, Default 0]: Final inventory quantity of a material.
* InitialBackorder [Decimal, Default 0]: Initial backorder quantity of a material.
* InitialLinkedLotSize [Integer, Default 0]: Initial linked lot size state of a material.

## Virtual table definitions
The SQL syntax definitions are available in the file init.sql. The
following list provides a definition and a description of the virtual tables within EER
model.
First, the technical view name is defined. Next, a description of the view
purpose is provided by the quotes. Virtual column type, default values, and relationship definitions are listed in square brackets, followed by a virtual column description.

1. V_PlanningBuckets: "Which duration of a period (planning bucket) is as-
signed to a particular problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* PlanningBuckets [Varchar 10]: Planning buckets set for a problem instance, e.g. ‘1 WEEK’.
* PlanningBucketType [Varchar 10]: Planning bucket type, valid entries are ’DAY’, ’WEEK’,
’MONTH’, ’QUARTER’, and ’YEAR’.
* PlanningStartDate [Date]: Start date of planning horizon.
* PlanningEndDate [Date]: End date of planning horizon.
2. V_PlanningPeriod: "Which model period is mapped on which planning date
for a problem instance within the planning horizon?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* PlanningStartDate [Date]: Start date of planning horizon.
* PlanningEndDate [Date]: End date of planning horizon.
* PlanningBuckets [Varchar 10]: Planning buckets set for a problem instance, e.g. ‘1 WEEK’.
* PlanningDate [Date]: Planning date in which a lot-sizing decision can be made.
* PlanningDateIntervalEnd [Date]: End planning date of a date bucket interval.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
3. V_PeriodExpand: "Which model period is mapped on which planning date
for a problem instance, simulation instance, and material within the planning
horizon?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* SimulationInstanceId [Varchar 36]: Unique simulation instance identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* PlanningDate [Date]: Planning date in which a lot-sizing decision can be made.
* PlanningDateIntervalEnd [Date]: End planning date of a date bucket interval.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
4. V_Capacity: "What capacity is assigned to a machine in a model period for a
problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* SimulationInstanceId [Varchar 36]: Unique simulation instance identifier.
40
* MachineId [Varchar 36]: Unique machine identifier.
* PlanningDate [Date]: Planning date in which a production resource capacity is provided.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
* PlanningBuckets [Varchar 10]: Planning buckets set for a problem instance, e.g. ‘1 WEEK’.
* CapacityPerPeriod [Decimal]: Total production resource capacity in days for a machine
and planning period.
5. V_ProductToLine: "Which products are assigned to which machines for a
problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* MachineId [Varchar 36]: Unique machine identifier.
* MaterialId [Varchar 36]: Unique material identifier.
6. V_MaterialCost: "What inventory-holding and backorder costs per unit are
assigned to a material in a model period for a problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* InventoryHolding [Decimal]: Inventory-holding costs per unit of a stored material in a
planning period.
* Backorder [Decimal]: Backorder costs per unit of a stored material in a planning period.
* PlanningDate [Date]: Planning date in which material costs are provided.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
7. V_SetupMatrix: "What time and cost does a setup operation imply of an al-
located material on a machine in a model period for a particular problem in-
stance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* MachineId [Varchar 36]: Unique machine identifier.
* MaterialId [Varchar 36]: Unique material identifier of a material allocated on a machine.
* PlanningDate [Date]: Planning date in which a machine setup can be provided.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
* SetupTime [Decimal]: Setup time in days of one setup operation on a machine from an
allocated material to another allocated material in a planning period.
* SetupCost [Decimal]: Setup costs of one setup operation on a machine from an allocated
material to another allocated material in a planning period.
8. V_Production: "What lead time, production time per unit, production cost
per unit, batch size, minimum and maximum lot size, shelf-life surplus, and
shelf-life type is assigned to a material produced on a machine in a model
period for a problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* MachineId [Varchar 36]: Unique machine identifier.
* MaterialId [Varchar 36]: Unique material identifier of a material allocated on a machine.
* PlanningDate [Date]: Planning date in which a material can be produced on a machine.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
* LeadTime [Decimal]: Required lead time in days till a material that is produced is ready for
consumption.
* ProductionTimePerBaseUOM [Decimal]: Required production resource capacity to pro-
duce one unit of a material allocated on a machine.
* ProductionCostPerBaseUOM [Decimal]: Associated variable production costs to produce
one unit of a material allocated on a machine.
* BatchSizeFix [Decimal]: Fixed batch size of a material produced on a machine.
* LotSizeMin [Decimal]: Minimum campaign length of a material produced on a machine.
* LotSizeMax [Decimal]: Maximum campaign length of a material produced on a machine.
* ShelfLifeFix [Decimal]: Shelf-life surplus of material produced on a machine.
* ShelfLifeType [Varchar 36]: Name of integrated shelf-life rule, two options are available:
‘AFFINE_LINEAR’ or ‘MIN’.
9. V_ProductStructures: "Which production coefficient, fixed and variable ma-
terial yield and shelf-life rule weights are mapped to a machine-allocated good
issued by a BOM alternative from a machine-allocated good received in a model
period for a problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* MachineIdGoodsReceived [Varchar 36]: Unique machine identifier on which a goods re-
ceived is allocated.
* GoodsReceived [Varchar 36]: Unique material identifier for a unique goods received by a
production run.
* MachineIdGoodsIssued [Varchar 36]: Unique machine identifier on which a goods issued
is allocated.
* GoodsIssued [Varchar 36]: Unique material identifier for all goods issued by a production
run for a goods received.
* PlanningDate [Date]: Planning date on which a material can be produced on a machine.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
* BOMAlternative [Varchar 36]: BOM alternatives identifier (alternative production recipes)
for issued materials.
* Ratio [Decimal]: Requested units of an issued material to produce one unit of a received
material (production coefficient).
* ScrapFix [Decimal]: Fixed material yield quantity if an issued material is produced.
* ScrapVariable [Decimal]: Share of material yield quantity if an issued material is produced.
* ShelfLifeVariable [Decimal]: Remaining shelf-life weight of an issued material in integrated
shelf-life rules.
10. V_MaterialType: "Which unit of measure, currency and material type does a
material have for a problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* BaseUOM [Varchar 10]: Unit of measure of a material.
* BaseCurrency [Varchar 10]: Currency of a material.
* MaterialType [Varchar 36]: Material type, three options are possible: ‘FINISHED_GOOD’,
‘INTERMEDIATE’, or ‘RAW_MATERIAL’.
11. V_Material: "Which unit of measure, currency and material type does a man-
ufacturable material have for a problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* BaseUOM [Varchar 10]: Unit of measure of a material.
* BaseCurrency [Varchar 10]: Currency of a material.
* MaterialType [Varchar 36]: Material type, two options are possible: ‘FINISHED_GOOD’ or
‘INTERMEDIATE’.
12. V_ProblemInstance: "Which simulation instances and how many production
stages are assigned to a problem instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* ProblemInstanceName [Varchar 100]: Problem instance name.
* SimulationInstanceId [Varchar 36]: Unique simulation instance identifier.
* SimulationInstanceName [Varchar 100]: Simulation instance name.
* ProductionStages [Integer]: Amount of production stages covered by a problem instance.
13. V_PrimaryDemand: "How much is a material in a period demanded for a
problem and simulation instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* SimulationInstanceId [Varchar 36]: Unique simulation instance identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* DeliveryDate [Date]: Delivery date of requested primary/customer demand of a material.
* Quantity [Decimal]: Quantity assigned to primary/customer demand.
* BaseUOM [Varchar 10]: Unit of measure of a demanded material.
* BaseCurrency [Varchar 10]: Currency of a demanded material.
* PlanningPeriod [Integer]: Assigned planning period of a primary/customer demand based
on delivery date.
14. V_MaxProductionQuantity: "What is the maximal production quantity of a
material manufactured on a machine per planning period for a problem and
simulation instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* SimulationInstanceId [Varchar 36]: Unique simulation instance identifier.
* MachineId [Varchar 36]: Unique machine identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* PlanningPeriod [Integer]: Assigned planning period to a particular planning date in the
planning horizon.
* BigM [Decimal]: Maximal production quantity of a material manufactured on a machine
per planning period.
15. V_InitialLotSizingValues: "What initial/final inventory and backorder quantity are assigned to each material for a problem and simulation instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* SimulationInstanceId [Varchar 36]: Unique simulation instance identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* InitialInventory [Decimal]: Inventory of a material in the initial planning period 0.
* InitialBackorder [Decimal]: Backorder quantity of a material in the initial planning period
0.
* FinalInventory [Decimal]: Target inventory of a material in the last planning period T .
16. V_InitialLinkedLotSizingValues: "What initial linked lot size is assigned to
each material for a problem and simulation instance?"
* ProblemInstanceId [Varchar 36]: Unique problem instance identifier.
* SimulationInstanceId [Varchar 36]: Unique simulation instance identifier.
* MachineId [Varchar 36]: Unique machine identifier.
* MaterialId [Varchar 36]: Unique material identifier.
* InitialLinkedLotSize[Integer]: Linked lot size state of a material manufactured on a machine in the initial period 0.