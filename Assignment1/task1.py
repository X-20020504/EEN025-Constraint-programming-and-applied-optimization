import gurobipy as gp
from gurobipy import Model, GRB
import numpy as np

tax = np.array([0.3, 0.15, 0.2, 0.3])
price = np.array([106000, 136000, 150000, 427000])
material_cost = np.array([0.57, 0.6, 0.55, 0.45])
salary = np.array([20000, 11000, 20000, 26000])
manhour = np.array([40, 45, 38, 100])
min_prod = np.array([120000, 100000, 80000, 15000])

man_cost = salary * manhour / 160
material_cost = material_cost * price
total_cost = man_cost + material_cost
profit = price - total_cost
net_income = (1-tax) * profit

model = Model("Task_1")

x1 = model.addVar(vtype=GRB.INTEGER, name="Panda")
x2 = model.addVar(vtype=GRB.INTEGER, name="500")
x3 = model.addVar(vtype=GRB.INTEGER, name="Musa")
x4 = model.addVar(vtype=GRB.INTEGER, name="Giulia")

model.setObjective(net_income[0]*x1 + net_income[1]*x2 + net_income[2]*x3 + net_income[3]*x4, GRB.MAXIMIZE)

model.addConstr(total_cost[0]*x1 + total_cost[1]*x2 + total_cost[2]*x3 + total_cost[3]*x4 <= 40e9, "budget_constraint")
model.addConstr(x1 >= min_prod[0], "number_constraint1")
model.addConstr(x2 >= min_prod[1], "number_constraint2")
model.addConstr(x3 >= min_prod[2], "number_constraint3")
model.addConstr(x4 >= min_prod[3], "number_constraint4")
model.addConstr(x1 + x3 <= 3e5, "marketing_constraint")

model.optimize()

if model.status == GRB.OPTIMAL:
    print(f"Optimal solution: x1 = {x1.x}, x2 = {x2.x}, x3 = {x3.x}, x4 = {x4.x}")
    print(f"Optimal objective value: {model.objVal}")
else:
    print("No optimal solution found.")
