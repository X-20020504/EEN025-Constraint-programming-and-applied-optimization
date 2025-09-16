import gurobipy as gp
from gurobipy import Model, GRB
import numpy as np

capacity = np.array([100, 150, 80, 200])

production_rate = np.array([[10, 15, 5],
                            [15, 10, 5],
                            [20, 5, 10],
                            [10, 15, 20]])

model = Model("Task_3")

# variables
line_num = 4
component_num = 3
x = model.addVars(line_num, component_num, vtype=GRB.INTEGER, name="x")

# objective function
component1 = gp.quicksum(production_rate[i, 0] * x[i, 0] for i in range(line_num))
model.setObjective(component1, GRB.MAXIMIZE)

# capacity constraint
for i in range(line_num):
    hours = gp.quicksum(x[i, j] for j in range(component_num))
    model.addConstr(hours <= capacity[i], name=f"capacity_{i}")

# components constraint
component1 = gp.quicksum(production_rate[i, 0] * x[i, 0] for i in range(line_num))
component2 = gp.quicksum(production_rate[i, 1] * x[i, 1] for i in range(line_num))
component3 = gp.quicksum(production_rate[i, 2] * x[i, 2] for i in range(line_num))
model.addConstr(component1 == component2, "component1&2")
model.addConstr(component2 == component3, "component2&3")

model.optimize()

if model.status == GRB.OPTIMAL:
    x_sol = np.array([[x[i, j].X for i in range(line_num)] for j in range(component_num)])
    print("Optimal solution (x matrix):")
    print(x_sol)

    print(f"Optimal objective value: {model.objVal}")
else:
    print("No optimal solution found.")
