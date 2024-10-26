------ Initial SQL files that build persistent and virtual tables of the EER model ------

---- Clean up ----
-- Drop all persistent tables if they exist
DROP TABLE IF EXISTS "BOMItem" CASCADE;
DROP TABLE IF EXISTS "BOMHeader" CASCADE;
DROP TABLE IF EXISTS "SetupMatrix" CASCADE;
DROP TABLE IF EXISTS "Demand" CASCADE;
DROP TABLE IF EXISTS "MaterialCost" CASCADE;
DROP TABLE IF EXISTS "Material" CASCADE;
DROP TABLE IF EXISTS "Capacity" CASCADE;
DROP TABLE IF EXISTS "SimulationInstance" CASCADE;
DROP TABLE IF EXISTS "ProblemInstance" CASCADE;
DROP TABLE IF EXISTS "InitialLotSizingValues" CASCADE;

-- Drop all virtual tables if they exist
DROP VIEW IF EXISTS "V_PlanningBuckets" CASCADE;
DROP VIEW IF EXISTS "V_PlanningPeriod" CASCADE;
DROP VIEW IF EXISTS "V_PeriodExpand" CASCADE;
DROP VIEW IF EXISTS "V_Capacity" CASCADE;
DROP VIEW IF EXISTS "V_ProductToLine" CASCADE;
DROP VIEW IF EXISTS "V_Material" CASCADE;
DROP VIEW IF EXISTS "V_MaterialCost" CASCADE;
DROP VIEW IF EXISTS "V_SetupMatrix" CASCADE;
DROP VIEW IF EXISTS "V_Production" CASCADE;
DROP VIEW IF EXISTS "V_ProductStructures" CASCADE;
DROP VIEW IF EXISTS "V_MaterialType" CASCADE;
DROP VIEW IF EXISTS "V_ProblemInstance" CASCADE;
DROP VIEW IF EXISTS "V_PrimaryDemand" CASCADE;
DROP VIEW IF EXISTS "V_MaxProductionQuantity" CASCADE;
DROP VIEW IF EXISTS "V_InitialLotSizingValues" CASCADE;
DROP VIEW IF EXISTS "V_InitialLinkedLotSizingValues" CASCADE;
DROP VIEW IF EXISTS "V_DemandPropagation" CASCADE;
DROP VIEW IF EXISTS "V_ShelfLifePropagation" CASCADE;

-- Drop result table
DROP TABLE IF EXISTS "LotSizingResult" CASCADE;

---- Define persistent entities ----
CREATE TABLE "ProblemInstance"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "ProblemInstanceName" VARCHAR(100) DEFAULT NULL,
    "PlanningBuckets" VARCHAR(10) NOT NULL DEFAULT '1 WEEK',
    "ProductionStages" INTEGER DEFAULT NULL,
    PRIMARY KEY("ProblemInstanceId")
);

CREATE TABLE "SimulationInstance"(
    "SimulationInstanceId" VARCHAR(36) NOT NULL,
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "SimulationInstanceName" VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY("ProblemInstanceId", "SimulationInstanceId"),
    CONSTRAINT "ConstraintSimulationInstanceProblemInstance" FOREIGN KEY ("ProblemInstanceId") REFERENCES "ProblemInstance"("ProblemInstanceId") ON DELETE CASCADE
);

CREATE TABLE "Material"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "MaterialId" VARCHAR(36) NOT NULL,
    "MaterialName" VARCHAR(100) DEFAULT NULL,
    "ShelfLifeTolerance" DECIMAL DEFAULT 0,
    "AlphaServiceLevelTarget" DECIMAL DEFAULT 0,
    "BetaServiceLevelTarget" DECIMAL DEFAULT 0,
    "BaseUOM" VARCHAR(10) DEFAULT 'PC',
    "BaseCurrency" VARCHAR(10) DEFAULT 'EUR',
    PRIMARY KEY("ProblemInstanceId", "MaterialId"),
    CONSTRAINT "ConstraintMaterialProblemInstance" FOREIGN KEY ("ProblemInstanceId") REFERENCES "ProblemInstance"("ProblemInstanceId") ON DELETE CASCADE
);

CREATE TABLE "Capacity"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "SimulationInstanceId" VARCHAR(36) NOT NULL,
    "MachineId" VARCHAR(36) NOT NULL,
    "ValidityDateTo" DATE NOT NULL,
    "ValidityDateFrom" DATE NOT NULL,
    "Capacity" DECIMAL DEFAULT 0,
    "MachineName" VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY("ProblemInstanceId", "SimulationInstanceId", "MachineId", "ValidityDateTo"),
    CONSTRAINT "ConstraintCapacitySimulationInstance" FOREIGN KEY ("ProblemInstanceId", "SimulationInstanceId") REFERENCES "SimulationInstance"("ProblemInstanceId", "SimulationInstanceId") ON DELETE CASCADE
);

CREATE TABLE "Demand"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "SimulationInstanceId" VARCHAR(36) NOT NULL,
    "MaterialId" VARCHAR(36) NOT NULL,
    "DeliveryDate" DATE NOT NULL,
    "Quantity" DECIMAL NOT NULL,
    PRIMARY KEY("ProblemInstanceId", "SimulationInstanceId", "MaterialId", "DeliveryDate"),
    CONSTRAINT "ConstraintDemandMaterial" FOREIGN KEY ("ProblemInstanceId", "MaterialId") REFERENCES "Material"("ProblemInstanceId", "MaterialId") ON DELETE CASCADE,
    CONSTRAINT "ConstraintDemandSimulationInstance" FOREIGN KEY ("ProblemInstanceId", "SimulationInstanceId") REFERENCES "SimulationInstance"("ProblemInstanceId", "SimulationInstanceId") ON DELETE CASCADE
);

CREATE TABLE "MaterialCost"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "MaterialId" VARCHAR(36) NOT NULL,
    "ValidityDateTo" DATE NOT NULL,
    "ValidityDateFrom" DATE NOT NULL,
    "InventoryHolding" DECIMAL DEFAULT 0,
    "Backorder" DECIMAL DEFAULT 0,
    "Destruction" DECIMAL DEFAULT 0,
    "LostSales" DECIMAL DEFAULT 0,
    PRIMARY KEY("ProblemInstanceId", "MaterialId", "ValidityDateTo"),
    CONSTRAINT "ConstraintMaterialCostMaterial" FOREIGN KEY ("ProblemInstanceId", "MaterialId") REFERENCES "Material"("ProblemInstanceId", "MaterialId") ON DELETE CASCADE
);

CREATE TABLE "SetupMatrix"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "MachineId" VARCHAR(36) NOT NULL,
    "MaterialIdFrom" VARCHAR(36) NOT NULL,
    "MaterialIdTo" VARCHAR(36) NOT NULL,
    "SetupFamilyIdFrom" VARCHAR(36) DEFAULT NULL,
    "SetupFamilyIdTo" VARCHAR(36) DEFAULT NULL,
    "ValidityDateTo" DATE NOT NULL,
    "ValidityDateFrom" DATE NOT NULL,
    "SetupTime" DECIMAL DEFAULT 0,
    "SetupCost" DECIMAL DEFAULT 0,
    PRIMARY KEY("ProblemInstanceId", "MachineId", "MaterialIdFrom", "MaterialIdTo", "ValidityDateTo"),
    CONSTRAINT "ConstraintSetupMatrixMaterial1" FOREIGN KEY ("ProblemInstanceId", "MaterialIdFrom") REFERENCES "Material"("ProblemInstanceId", "MaterialId") ON DELETE CASCADE,
    CONSTRAINT "ConstraintSetupMatrixMaterial2" FOREIGN KEY ("ProblemInstanceId", "MaterialIdTo") REFERENCES "Material"("ProblemInstanceId", "MaterialId") ON DELETE CASCADE
);

CREATE TABLE "BOMHeader"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "BOMHeaderId" VARCHAR(36) NOT NULL,
    "MachineId" VARCHAR(36) NOT NULL,
    "MaterialId" VARCHAR(36) NOT NULL,
    "ValidityDateTo" DATE NOT NULL,
    "ValidityDateFrom" DATE NOT NULL,
    "LeadTime" DECIMAL DEFAULT 0,
    "ShelfLifeType" VARCHAR(36) DEFAULT NULL,
    "ShelfLifeFix" DECIMAL DEFAULT 0,
    "ProductionTime" DECIMAL NOT NULL,
    "ProductionCost" DECIMAL DEFAULT 0,
    "BatchSizeFix" DECIMAL DEFAULT NULL,
    "LotSizeMin" DECIMAL DEFAULT NULL,
    "LotSizeMax" DECIMAL DEFAULT NULL,
    PRIMARY KEY("ProblemInstanceId", "BOMHeaderId", "ValidityDateTo"),
    CONSTRAINT "ConstraintBOMHeaderMaterial" FOREIGN KEY ("ProblemInstanceId", "MaterialId") REFERENCES "Material"("ProblemInstanceId", "MaterialId") ON DELETE CASCADE
);

CREATE TABLE "BOMItem"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "BOMHeaderId" VARCHAR(36) NOT NULL,
    "BOMItemId" VARCHAR(36) NOT NULL,
    "BOMAlternative" VARCHAR(36) NOT NULL,
    "MaterialId" VARCHAR(36) NOT NULL,
    "Ratio" DECIMAL DEFAULT 1,
    "ScrapFix" DECIMAL DEFAULT 0,
    "ScrapVariable" DECIMAL DEFAULT 0,
    "ShelfLifeVariable" DECIMAL DEFAULT 0,
    PRIMARY KEY("ProblemInstanceId", "BOMHeaderId", "BOMItemId"),
    CONSTRAINT "ConstraintBOMItemMaterial" FOREIGN KEY ("ProblemInstanceId", "MaterialId") REFERENCES "Material"("ProblemInstanceId", "MaterialId") ON DELETE CASCADE
);

CREATE TABLE "InitialLotSizingValues"(
	"ProblemInstanceId" VARCHAR(36) NOT NULL,
    "SimulationInstanceId" VARCHAR(36) NOT NULL,
    "MaterialId" VARCHAR(36) NOT NULL,
    "MachineId" VARCHAR(36) DEFAULT NULL,
    "InitialInventory" DECIMAL DEFAULT 0,
    "InitialBackorder" DECIMAL DEFAULT 0,
    "FinalInventory" DECIMAL DEFAULT 0,
    "InitialLinkedLotSize" INTEGER DEFAULT 0,
    PRIMARY KEY("ProblemInstanceId", "SimulationInstanceId", "MaterialId"),
    CONSTRAINT "ConstraintInitialValuesMaterial" FOREIGN KEY ("ProblemInstanceId", "MaterialId") REFERENCES "Material"("ProblemInstanceId", "MaterialId") ON DELETE CASCADE,
    CONSTRAINT "ConstraintInitialValuesSimulationInstance" FOREIGN KEY ("ProblemInstanceId", "SimulationInstanceId") REFERENCES "SimulationInstance"("ProblemInstanceId", "SimulationInstanceId") ON DELETE CASCADE
);


---- Result tables ----
CREATE TABLE "LotSizingResult"(
    "ProblemInstanceId" VARCHAR(36) NOT NULL,
    "MaterialId" VARCHAR(36) NOT NULL,
    "ConfiguredLotSize" DECIMAL DEFAULT 0,
    "ExpectedExpiredInventory" DECIMAL DEFAULT 0,
    "ExpectedAlphaServiceLevel" DECIMAL DEFAULT 0,
    "ExpectedBetaServiceLevel" DECIMAL DEFAULT 0,
    "ExpectedUtilization" DECIMAL DEFAULT 0,
    "ExpectedTotalManufacturingCost" DECIMAL DEFAULT 0,
    "ExpectedTotalInventoryCost" DECIMAL DEFAULT 0,
    "ExpectedTotalBackorderCost" DECIMAL DEFAULT 0,
    "ExpectedTotalSetupCost" DECIMAL DEFAULT 0,
    "ExpectedTotalLostSales" DECIMAL DEFAULT 0,
    "ExpectedTotalDestructionCost" DECIMAL DEFAULT 0,
    PRIMARY KEY("ProblemInstanceId","MaterialId")
);

---- Define virtual tables ----
CREATE VIEW "V_PlanningBuckets" AS
SELECT t_pi."ProblemInstanceId", t_pi."PlanningBuckets", j_c."PlanningEndDate", j_c."PlanningStartDate",
	CASE
		WHEN UPPER(t_pi."PlanningBuckets") LIKE '%DAY' THEN 'DAY' 
		WHEN UPPER(t_pi."PlanningBuckets") LIKE '%WEEK' THEN 'WEEK' 
		WHEN UPPER(t_pi."PlanningBuckets") LIKE '%MONTH' THEN 'MONTH' 
		WHEN UPPER(t_pi."PlanningBuckets") LIKE '%QUARTER' THEN 'QUARTER' 
		WHEN UPPER(t_pi."PlanningBuckets") LIKE '%YEAR' THEN 'YEAR' 
		ELSE 'DAY' END AS "PlanningBucketType"
FROM "ProblemInstance" AS t_pi
INNER JOIN (
	SELECT t_c."ProblemInstanceId", MAX(t_c."ValidityDateTo") AS "PlanningEndDate", MIN(t_c."ValidityDateFrom") AS "PlanningStartDate"
	FROM "Capacity" AS t_c 
	GROUP BY t_c."ProblemInstanceId"
) AS j_c ON t_pi."ProblemInstanceId" = j_c."ProblemInstanceId";

CREATE VIEW "V_PlanningPeriod" AS 
SELECT s_v_pb."ProblemInstanceId", s_v_pb."PlanningStartDate", s_v_pb."PlanningEndDate", 
	s_v_pb."PlanningBuckets", s_v_pb."PlanningDate", 
	DATE(s_v_pb."PlanningDate" +  s_v_pb."PlanningBuckets"::INTERVAL - '1 DAY'::INTERVAL) AS "PlanningDateIntervalEnd",
	ROW_NUMBER() OVER(PARTITION BY s_v_pb."ProblemInstanceId" ORDER BY s_v_pb."PlanningDate") AS "PlanningPeriod" FROM 
(
	SELECT v_pb."ProblemInstanceId", v_pb."PlanningStartDate", v_pb."PlanningEndDate", v_pb."PlanningBuckets",
		DATE(DATE_TRUNC(v_pb."PlanningBucketType", DATE(GENERATE_SERIES(v_pb."PlanningStartDate", v_pb."PlanningEndDate", v_pb."PlanningBuckets"::INTERVAL)))) AS "PlanningDate" 
	FROM "V_PlanningBuckets"  AS v_pb
	GROUP BY v_pb."ProblemInstanceId", v_pb."PlanningStartDate", v_pb."PlanningEndDate", v_pb."PlanningBuckets", v_pb."PlanningBucketType"
) AS s_v_pb;

CREATE VIEW "V_PeriodExpand" AS
SELECT v_pp."ProblemInstanceId" AS "ProblemInstanceId", t_si."SimulationInstanceId", t_m."MaterialId",
	v_pp."PlanningStartDate", v_pp."PlanningEndDate", v_pp."PlanningBuckets", v_pp."PlanningDate", v_pp."PlanningDateIntervalEnd", v_pp."PlanningPeriod"
FROM "V_PlanningPeriod" AS v_pp
INNER JOIN "Material" AS t_m ON v_pp."ProblemInstanceId" = t_m."ProblemInstanceId"
INNER JOIN "SimulationInstance" AS t_si ON v_pp."ProblemInstanceId" = t_si."ProblemInstanceId";

CREATE VIEW "V_Capacity" AS 
SELECT t_c."ProblemInstanceId", t_c."SimulationInstanceId", t_c."MachineId", j_v_pp1."PlanningDate", j_v_pp1."PlanningPeriod", j_v_pp1."PlanningBuckets", 
	AVG(t_c."Capacity" / (j_t_pi."CapacityDayRange" * j_v_pp2."MaxPlanningPeriods" / j_v_pp_3."DaysInPlanningHorizon")) AS "CapacityPerPeriod"
FROM "Capacity" AS t_c
INNER JOIN "V_PlanningPeriod" AS j_v_pp1 ON t_c."ProblemInstanceId" = j_v_pp1."ProblemInstanceId"
INNER JOIN (
	SELECT "ProblemInstanceId", MAX("PlanningPeriod") AS "MaxPlanningPeriods" 
	FROM "V_PlanningPeriod" 
	GROUP BY "ProblemInstanceId"
	) AS j_v_pp2 ON t_c."ProblemInstanceId" = j_v_pp2."ProblemInstanceId"
INNER JOIN (
	SELECT "ProblemInstanceId", MAX("ValidityDateTo" - "ValidityDateFrom") + 1 AS "CapacityDayRange" 
	FROM "Capacity" 
	GROUP BY "ProblemInstanceId"
	) AS j_t_pi ON t_c."ProblemInstanceId" = j_t_pi."ProblemInstanceId"
INNER JOIN (
	SELECT "ProblemInstanceId", MAX("PlanningEndDate" - "PlanningStartDate") + 1 AS "DaysInPlanningHorizon" 
	FROM "V_PlanningPeriod" 
	GROUP BY "ProblemInstanceId"
	) AS j_v_pp_3 ON t_c."ProblemInstanceId" = j_v_pp_3."ProblemInstanceId"
WHERE t_c."ValidityDateTo" >= j_v_pp1."PlanningDate" AND t_c."ValidityDateFrom" <= j_v_pp1."PlanningDate" 
GROUP BY t_c."ProblemInstanceId", t_c."SimulationInstanceId", t_c."MachineId", j_v_pp1."PlanningDate", j_v_pp1."PlanningPeriod", j_v_pp1."PlanningBuckets";

CREATE VIEW "V_ProductToLine" AS
SELECT DISTINCT "ProblemInstanceId", "MachineId", "MaterialIdFrom" AS "MaterialId" FROM "SetupMatrix";

CREATE VIEW "V_SetupMatrix" AS
SELECT t_sm."ProblemInstanceId", t_sm."MachineId", t_sm."MaterialIdFrom" AS "MaterialId", j_v_pp."PlanningDate", j_v_pp."PlanningPeriod", 
	AVG(t_sm."SetupTime") AS "SetupTime", AVG(t_sm."SetupCost") AS "SetupCost"
FROM "SetupMatrix" AS t_sm
INNER JOIN "V_PlanningPeriod" AS j_v_pp ON t_sm."ProblemInstanceId" = j_v_pp."ProblemInstanceId"
WHERE t_sm."ValidityDateTo" >= j_v_pp."PlanningDate" AND t_sm."ValidityDateFrom" <= j_v_pp."PlanningDate"
GROUP BY t_sm."ProblemInstanceId", t_sm."MachineId", t_sm."MaterialIdFrom", j_v_pp."PlanningDate", j_v_pp."PlanningPeriod";

CREATE VIEW "V_Production" AS
SELECT t_bh."ProblemInstanceId", t_bh."MachineId", t_bh."MaterialId", 
	j_v_pp."PlanningDate", j_v_pp."PlanningPeriod", AVG(t_bh."LeadTime") AS "LeadTime", AVG(t_bh."ProductionTime") AS "ProductionTimePerBaseUOM", 
	AVG(t_bh."ProductionCost") AS "ProductionCostPerBaseUOM",
	AVG(t_bh."BatchSizeFix") AS "BatchSizeFix", AVG(t_bh."LotSizeMin") AS "LotSizeMin", AVG(t_bh."LotSizeMax") AS "LotSizeMax", 
	AVG(t_bh."ShelfLifeFix") AS "ShelfLifeFix", MAX(t_bh."ShelfLifeType") AS "ShelfLifeType"
FROM "BOMHeader" AS t_bh
INNER JOIN "V_PlanningPeriod" AS j_v_pp ON t_bh."ProblemInstanceId" = j_v_pp."ProblemInstanceId"
WHERE t_bh."ValidityDateTo" >= j_v_pp."PlanningDate" AND t_bh."ValidityDateFrom" <= j_v_pp."PlanningDate"
GROUP BY t_bh."ProblemInstanceId", t_bh."MachineId", t_bh."MaterialId", j_v_pp."PlanningDate", j_v_pp."PlanningPeriod";


CREATE VIEW "V_ProductStructures" AS
SELECT t_bh."ProblemInstanceId", t_bh."MachineId" AS "MachineIdGoodsReceived", t_bh."MaterialId" AS "GoodsReceived", j_t_bi."MachineId" AS "MachineIdGoodsIssued", 
	j_t_bi."MaterialId" AS "GoodsIssued", j_v_pp."PlanningDate", j_v_pp."PlanningPeriod", j_t_bi."BOMAlternative", 
	AVG(j_t_bi."Ratio") AS "Ratio", AVG(j_t_bi."ScrapFix") AS "ScrapFix", AVG(j_t_bi."ScrapVariable") AS "ScrapVariable", 
	AVG(j_t_bi."ShelfLifeVariable") AS "ShelfLifeVariable"
FROM "BOMHeader" AS t_bh
INNER JOIN "V_PlanningPeriod" AS j_v_pp ON t_bh."ProblemInstanceId" = j_v_pp."ProblemInstanceId"
LEFT JOIN (
	SELECT t_bi."ProblemInstanceId", t_bi."MaterialId", t_bi."BOMAlternative", t_bi."Ratio", t_bi."ScrapFix", 
		t_bi."ScrapVariable", j_t_bh."MachineId", t_bi."BOMHeaderId", t_bi."ShelfLifeVariable"
	FROM "BOMItem" AS t_bi
	INNER JOIN "BOMHeader" AS j_t_bh ON t_bi."ProblemInstanceId" = j_t_bh."ProblemInstanceId" AND t_bi."MaterialId" = j_t_bh."MaterialId"
) AS j_t_bi ON t_bh."ProblemInstanceId" = j_t_bi."ProblemInstanceId" AND t_bh."BOMHeaderId" = j_t_bi."BOMHeaderId"
WHERE t_bh."ValidityDateTo" >= j_v_pp."PlanningDate" AND t_bh."ValidityDateFrom" <= j_v_pp."PlanningDate" AND j_t_bi."MaterialId" IS NOT NULL 
GROUP BY t_bh."ProblemInstanceId", t_bh."MachineId", t_bh."MaterialId", j_t_bi."MachineId", 
	j_t_bi."MaterialId", j_v_pp."PlanningDate", j_v_pp."PlanningPeriod", j_t_bi."BOMAlternative";

CREATE VIEW "V_MaterialType" AS
SELECT DISTINCT t_m."ProblemInstanceId", t_m."MaterialId", t_m."AlphaServiceLevelTarget", t_m."ShelfLifeTolerance", t_m."BetaServiceLevelTarget", t_m."BaseUOM", t_m."BaseCurrency",
	CASE 
		WHEN t_m."MaterialId" = j_v_ps1."GoodsReceived" AND j_v_ps2."GoodsIssued" IS NULL AND t_m."MaterialId" = j_v_sm."MaterialId" THEN 'FINISHED_GOOD'
		WHEN t_m."MaterialId" = j_v_ps2."GoodsIssued" AND t_m."MaterialId" = j_v_sm."MaterialId" THEN 'INTERMEDIATE'
		WHEN j_v_ps1."GoodsReceived" IS NULL AND j_v_ps2."GoodsIssued" IS NULL AND j_v_sm."MaterialId" IS NOT NULL THEN 'FINISHED_GOOD'
		ELSE 'RAW_MATERIAL'
	END AS "MaterialType"
FROM "Material" AS t_m
LEFT JOIN (SELECT DISTINCT v_ps1."ProblemInstanceId", v_ps1."GoodsReceived" FROM "V_ProductStructures" AS v_ps1) AS j_v_ps1 ON t_m."ProblemInstanceId" = j_v_ps1."ProblemInstanceId" AND t_m."MaterialId" = j_v_ps1."GoodsReceived"
LEFT JOIN (SELECT DISTINCT v_ps2."ProblemInstanceId", v_ps2."GoodsIssued" FROM "V_ProductStructures" AS v_ps2) AS j_v_ps2 ON t_m."ProblemInstanceId" = j_v_ps2."ProblemInstanceId" AND t_m."MaterialId" = j_v_ps2."GoodsIssued"
LEFT JOIN (SELECT DISTINCT "ProblemInstanceId", "MaterialId" FROM "V_SetupMatrix") AS j_v_sm ON t_m."ProblemInstanceId" = j_v_sm."ProblemInstanceId" AND t_m."MaterialId" = j_v_sm."MaterialId";

CREATE VIEW "V_Material" AS
SELECT "ProblemInstanceId", "MaterialId", "BaseUOM", "ShelfLifeTolerance", "AlphaServiceLevelTarget", "BetaServiceLevelTarget", "BaseCurrency", "MaterialType"
FROM "V_MaterialType" 
WHERE "MaterialType" != 'RAW_MATERIAL';

CREATE VIEW "V_MaterialCost" AS
SELECT t_mc."ProblemInstanceId", t_mc."MaterialId", AVG(t_mc."LostSales") AS "LostSales", AVG(t_mc."Destruction") AS "Destruction", AVG(t_mc."InventoryHolding") AS "InventoryHolding", AVG(t_mc."Backorder") AS "Backorder", j_v_pp."PlanningDate", j_v_pp."PlanningPeriod"
FROM "MaterialCost" AS t_mc
INNER JOIN "V_PlanningPeriod" AS j_v_pp ON t_mc."ProblemInstanceId" = j_v_pp."ProblemInstanceId"
INNER JOIN "V_Material" AS j_v_m ON t_mc."ProblemInstanceId" = j_v_m."ProblemInstanceId" AND t_mc."MaterialId" = j_v_m."MaterialId"
WHERE t_mc."ValidityDateTo" >= j_v_pp."PlanningDate" AND t_mc."ValidityDateFrom" <= j_v_pp."PlanningDate"
GROUP BY t_mc."ProblemInstanceId", t_mc."MaterialId", j_v_pp."PlanningDate", j_v_pp."PlanningPeriod";

CREATE VIEW "V_PrimaryDemand" AS 
	SELECT s_t_d."ProblemInstanceId", s_t_d."SimulationInstanceId", s_t_d."MaterialId", s_t_d."DeliveryDate",
	SUM(s_t_d."Quantity") AS "Quantity", s_t_d."PlanningPeriod", s_t_d."BaseUOM", s_t_d."BaseCurrency"
	FROM (
		SELECT j_pe."ProblemInstanceId", j_pe."SimulationInstanceId", j_pe."MaterialId", j_pe."PlanningDate" AS "DeliveryDate",
			CASE WHEN j_t_d."Quantity" IS NULL THEN 0 ELSE j_t_d."Quantity" END AS "Quantity", j_pe."PlanningPeriod", j_v_m."BaseUOM", j_v_m."BaseCurrency"
		FROM (
			SELECT t_d."ProblemInstanceId", t_d."SimulationInstanceId", t_d."MaterialId", 
				DATE(DATE_TRUNC(j_v_pp."PlanningBucketType", t_d."DeliveryDate")) AS "DeliveryDate", SUM(t_d."Quantity") AS "Quantity"
			FROM
			  "Demand" AS t_d
			INNER JOIN "V_PlanningBuckets" AS j_v_pp ON t_d."ProblemInstanceId" = j_v_pp."ProblemInstanceId"
			GROUP BY t_d."ProblemInstanceId", t_d."SimulationInstanceId", t_d."MaterialId", DATE_TRUNC(j_v_pp."PlanningBucketType", t_d."DeliveryDate")
		) AS j_t_d 
		RIGHT JOIN "V_PeriodExpand" AS j_pe ON j_t_d."ProblemInstanceId" = j_pe."ProblemInstanceId" AND 
		   (j_t_d."DeliveryDate" BETWEEN j_pe."PlanningDate" AND j_pe."PlanningDateIntervalEnd") AND
			j_t_d."MaterialId" = j_pe."MaterialId" AND j_t_d."SimulationInstanceId" = j_pe."SimulationInstanceId"
		INNER JOIN "V_Material" AS j_v_m ON j_pe."ProblemInstanceId" = j_v_m."ProblemInstanceId" AND j_pe."MaterialId" = j_v_m."MaterialId"
	) AS s_t_d
GROUP BY s_t_d."ProblemInstanceId", s_t_d."SimulationInstanceId", s_t_d."MaterialId", s_t_d."DeliveryDate", s_t_d."PlanningPeriod", s_t_d."BaseUOM", s_t_d."BaseCurrency";

CREATE VIEW "V_ProblemInstance" AS
SELECT t_pi."ProblemInstanceId", t_pi."ProblemInstanceName", j_t_si."SimulationInstanceId", j_t_si."SimulationInstanceName", t_pi."ProductionStages" AS "ProductionStages"
FROM "ProblemInstance" AS t_pi
INNER JOIN "SimulationInstance" AS j_t_si ON t_pi."ProblemInstanceId" = j_t_si."ProblemInstanceId";

CREATE VIEW "V_MaxProductionQuantity" AS
SELECT s_bm."ProblemInstanceId", s_bm."SimulationInstanceId", s_bm."MachineId", s_bm."MaterialId", s_bm."PlanningPeriod",
	CASE
		WHEN s_bm."QuantityCumSum" <= s_bm."MaxProductionQuantity" AND v_m."MaterialType" = 'FINISHED_GOOD' THEN s_bm."QuantityCumSum"
		ELSE s_bm."MaxProductionQuantity" END AS "BigM"
FROM (
	SELECT v_pd."ProblemInstanceId", v_pd."SimulationInstanceId", v_ptl."MachineId", v_pd."MaterialId", v_pd."PlanningPeriod",
		CASE
			WHEN j_v_p."ProductionTimePerBaseUOM" = 0 THEN 0 
			ELSE j_v_c."CapacityPerPeriod" / j_v_p."ProductionTimePerBaseUOM" END AS "MaxProductionQuantity",
		SUM(v_pd."Quantity") OVER (PARTITION BY v_pd."ProblemInstanceId", v_pd."SimulationInstanceId", v_pd."MaterialId" ORDER BY v_pd."PlanningPeriod") AS "QuantityCumSum"
	FROM "V_PrimaryDemand" AS v_pd
	INNER JOIN "V_ProductToLine" AS v_ptl ON v_ptl."ProblemInstanceId" = v_pd."ProblemInstanceId" AND v_ptl."MaterialId" = v_pd."MaterialId"
	INNER JOIN (
		SELECT v_p."ProblemInstanceId", v_p."MachineId", v_p."MaterialId", v_p."PlanningPeriod", v_p."ProductionTimePerBaseUOM" FROM "V_Production" AS v_p
		) AS j_v_p ON j_v_p."ProblemInstanceId" = v_pd."ProblemInstanceId" AND j_v_p."MachineId" = v_ptl."MachineId" AND 
			j_v_p."MaterialId" = v_pd."MaterialId" AND j_v_p."PlanningPeriod" = v_pd."PlanningPeriod"
	INNER JOIN (
		SELECT DISTINCT v_c."ProblemInstanceId", v_c."MachineId", v_c."PlanningPeriod", v_c."CapacityPerPeriod" FROM "V_Capacity" AS v_c
		) AS j_v_c ON j_v_c."ProblemInstanceId" = v_pd."ProblemInstanceId" AND 
			j_v_c."MachineId" = v_ptl."MachineId" AND j_v_c."PlanningPeriod" = v_pd."PlanningPeriod"
) AS s_bm
INNER JOIN "V_Material" AS v_m ON s_bm."ProblemInstanceId" = v_m."ProblemInstanceId" AND s_bm."MaterialId" = v_m."MaterialId"
ORDER BY s_bm."ProblemInstanceId", s_bm."SimulationInstanceId", s_bm."MachineId", s_bm."MaterialId", s_bm."PlanningPeriod";

CREATE VIEW "V_InitialLotSizingValues" AS 
SELECT t_m."ProblemInstanceId" AS "ProblemInstanceId", j_t_si."SimulationInstanceId" AS "SimulationInstanceId", 
   t_m."MaterialId" AS "MaterialId",
	CASE WHEN j_t_ilsv."InitialInventory" IS NULL THEN 0 ELSE j_t_ilsv."InitialInventory" END AS "InitialInventory",
	CASE WHEN j_t_ilsv."InitialBackorder" IS NULL THEN 0 ELSE j_t_ilsv."InitialBackorder" END AS "InitialBackorder",
    CASE WHEN j_t_ilsv."FinalInventory" IS NULL THEN 0 ELSE j_t_ilsv."FinalInventory" END AS "FinalInventory"
FROM "Material" AS t_m
INNER JOIN "SimulationInstance" AS j_t_si ON t_m."ProblemInstanceId" = j_t_si."ProblemInstanceId"
LEFT JOIN "InitialLotSizingValues" AS j_t_ilsv ON t_m."ProblemInstanceId" = j_t_ilsv."ProblemInstanceId" AND 
    t_m."MaterialId" = j_t_ilsv."MaterialId" AND j_t_si."SimulationInstanceId" = j_t_ilsv."SimulationInstanceId";

CREATE VIEW "V_InitialLinkedLotSizingValues" AS 
SELECT t_m."ProblemInstanceId" AS "ProblemInstanceId", j_t_si."SimulationInstanceId" AS "SimulationInstanceId", 
    v_ptl."MachineId", t_m."MaterialId" AS "MaterialId",
    CASE WHEN j_t_ilsv."InitialLinkedLotSize" IS NULL THEN 0 ELSE j_t_ilsv."InitialLinkedLotSize" END AS "InitialLinkedLotSize"
FROM "Material" AS t_m
INNER JOIN "SimulationInstance" AS j_t_si ON t_m."ProblemInstanceId" = j_t_si."ProblemInstanceId"
INNER JOIN "V_ProductToLine" AS v_ptl ON t_m."ProblemInstanceId" = v_ptl."ProblemInstanceId" AND t_m."MaterialId" = v_ptl."MaterialId"
LEFT JOIN "InitialLotSizingValues" AS j_t_ilsv ON t_m."ProblemInstanceId" = j_t_ilsv."ProblemInstanceId" AND 
    t_m."MaterialId" = j_t_ilsv."MaterialId" AND j_t_si."SimulationInstanceId" = j_t_ilsv."SimulationInstanceId" AND 
    v_ptl."MachineId" = j_t_ilsv."MachineId";

CREATE VIEW "V_DemandPropagation" AS 
	WITH RECURSIVE cte AS
	(
	    SELECT
	    	  "ProblemInstanceId",
	        "BOMHeaderId",
	        "BOMItemId",
	        "MaterialId",
	        "Ratio"
	    FROM "BOMItem"
	
	    UNION ALL
	
	    SELECT
	        cte."ProblemInstanceId",
	        cte."BOMHeaderId",
	        "BOMItem"."BOMItemId",
			  "BOMItem"."MaterialId",
	        cte."Ratio" * "BOMItem"."Ratio"
	    FROM cte
	    INNER JOIN "BOMHeader"
	    ON "BOMHeader"."MaterialId" = cte."MaterialId" AND "BOMHeader"."ProblemInstanceId" = cte."ProblemInstanceId"
	    INNER JOIN "BOMItem"
	    ON "BOMItem"."BOMHeaderId" = "BOMHeader"."BOMHeaderId" AND "BOMItem"."ProblemInstanceId" = "BOMHeader"."ProblemInstanceId"
	)
	SELECT
		 cte."ProblemInstanceId" AS "ProblemInstanceId",
	    cte."BOMHeaderId" AS "BOMHeaderId",
	    "BOMHeader"."MaterialId" AS "GoodsReceived",
	    cte."MaterialId" AS "GoodsIssued",
	    SUM(cte."Ratio") AS "Ratio"
	FROM cte
	INNER JOIN "BOMHeader"
	ON "BOMHeader"."BOMHeaderId" = cte."BOMHeaderId" AND "BOMHeader"."ProblemInstanceId" = cte."ProblemInstanceId"
	INNER JOIN "V_MaterialType"
	ON "V_MaterialType"."MaterialId" = "BOMHeader"."MaterialId" AND "V_MaterialType"."ProblemInstanceId" = cte."ProblemInstanceId"
	WHERE "V_MaterialType"."MaterialType" = 'FINISHED_GOOD'
	GROUP BY cte."ProblemInstanceId", cte."BOMHeaderId", "BOMHeader"."MaterialId", cte."MaterialId"
	ORDER BY
	    cte."ProblemInstanceId",
	    "BOMHeader"."MaterialId";

CREATE VIEW "V_ShelfLifePropagation" AS 
	WITH RECURSIVE cte AS
	(
		SELECT -- BOM headers at the last production stage
	    	  a."ProblemInstanceId" AS "ProblemInstanceId",
	    	  a."BOMHeaderId" AS "BOMHeaderId",
	        a."MachineId" AS "MachineId",
	        a."MaterialId" AS "MaterialId",
	        a."ShelfLifeFix" AS "ShelfLifeFix",
	        a."ShelfLifeFix" AS "MaxRemainingShelfLife",
	        a."ShelfLifeType" AS "ShelfLifeType"
	   FROM "BOMHeader" AS a 
	   LEFT JOIN "BOMItem" AS aa ON aa."ProblemInstanceId" = a."ProblemInstanceId" AND aa."BOMHeaderId" = a."BOMHeaderId"
	   WHERE aa."ShelfLifeVariable" IS NULL
	    UNION ALL
		 SELECT DISTINCT
		        c."ProblemInstanceId",
		        c."BOMHeaderId",
		        c."MachineId",
		        c."MaterialId",
				  c."ShelfLifeFix",
				  CASE WHEN c."ShelfLifeType" = 'MIN' 
				  		THEN c."ShelfLifeFix" + MIN(cte."MaxRemainingShelfLife" * b."ShelfLifeVariable") OVER (PARTITION BY c."ProblemInstanceId", c."BOMHeaderId")
				  		ELSE c."ShelfLifeFix" + SUM(cte."MaxRemainingShelfLife" * b."ShelfLifeVariable") OVER (PARTITION BY c."ProblemInstanceId", c."BOMHeaderId")
				  END AS "MaxRemainingShelfLife",
				  c."ShelfLifeType"
		    FROM cte
		    INNER JOIN "BOMItem" AS b
		    ON b."ProblemInstanceId" = cte."ProblemInstanceId" AND b."MaterialId" = cte."MaterialId"
		    INNER JOIN "BOMHeader" AS c
		    ON c."ProblemInstanceId" = b."ProblemInstanceId" AND c."BOMHeaderId" = b."BOMHeaderId"
	)
	SELECT
		cte."ProblemInstanceId",
		cte."BOMHeaderId",
	   cte."MachineId",
	   cte."MaterialId",
	   cte."ShelfLifeFix",
	 	cte."MaxRemainingShelfLife",
	 	cte."ShelfLifeType"
	FROM cte;