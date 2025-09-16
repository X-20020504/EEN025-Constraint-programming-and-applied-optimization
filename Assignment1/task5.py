import gurobipy as gp
from gurobipy import Model, GRB
import numpy as np

rating = np.array([2, 3, 1, 4, 5])
duration = np.array([9, 15, 4, 3, 2])
revenue = np.array([4.5e-2, 5.4e-2, 5.1e-2, 4.4e-2, 6.1e-2])
tax = np.array([0, 0, 0.3, 0.3, 0])

model = Model("Task_5")

x = model.addVars(5, vtype=GRB.INTEGER, name="x")

# objective function
total_revenue = gp.quicksum(x[i] * revenue[i] * (1-tax[i]) for i in range(5))
model.setObjective(total_revenue, GRB.MAXIMIZE)

# total budget constraint
total_budget = gp.quicksum(x[i] for i in range(5))
model.addConstr(total_budget == 1e9, "constraint0")

# government+public constraint
model.addConstr(x[1] + x[2] + x[3] >= 0.4 * 1e9, "constraint1")

# average duration constraint
ave_duration = gp.quicksum(duration[i] * x[i] for i in range(5)) / 1e9
model.addConstr(ave_duration <= 5, "constraint2")

# avarage risk constraint
ave_risk = gp.quicksum(rating[i] * x[i] for i in range(5)) / 1e9
model.addConstr(ave_risk <= 1.5, "constraint3")

# mutex constraint between C and D
deltaC = model.addVar(vtype=GRB.BINARY, name="deltaC")
deltaD = model.addVar(vtype=GRB.BINARY, name="deltaD")
M = 1e9
model.addConstr(x[2] <= deltaC*M, "constraint4-1")
model.addConstr(x[3] <= deltaD*M, "constraint4-2")
model.addConstr(deltaC + deltaD <= 1, "constraint4-3")

# conditional constraint between A and E
deltaAE = model.addVar(vtype=GRB.BINARY, name="deltaAE")
M = 1e9
model.addConstr(x[0] >= 1e6 * deltaAE, "constraint5-1")
model.addConstr(x[4] <= M * deltaAE, "constraint5-2")

model.optimize()

if model.status == GRB.OPTIMAL:
    x_sol = np.array([x[i].X for i in range(5)])
    print("Optimal solution (x matrix):")
    print(x_sol)

    print(f"Optimal objective value: {model.objVal}")
else:
    print("No optimal solution found.")
