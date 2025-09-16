import gurobipy as gp
from gurobipy import Model, GRB
import numpy as np

tax = np.array([0.3, 0.15, 0.2, 0.3])
material_cost = np.array([0.57, 0.6, 0.55, 0.45])
salary = np.array([20000, 11000, 20000, 26000])
manhour = np.array([40, 45, 38, 100])
min_prod = np.array([120000, 100000, 80000, 15000])

price = np.array([[86e3, 92e3, 100e3, 0],
                  [106e3, 136e3, 150e3, 427e3],
                  [150e3, 170e3, 0, 550e3],
                  [112e3, 150e3, 170e3, 500e3]])
price_home = np.array([106e3, 92e3, 150e3, 427e3])
delivery_cost = np.array([[800, 0, 12e3, 0],
                          [0, 1000, 0, 0],
                          [3500, 2800, 0, 5000],
                          [2000, 1600, 2200, 2500]])
demand = np.array([[75e3, 20e3, 10e3, 0],
                   [35e3, 40e3, 80e3, 8e3],
                   [40e3, 50e3, 0, 3e3],
                   [2e3, 5e3, 1e3, 1e3]])
export_tax = np.array([[0, 0, 2.5e-2, 0]]).T

man_cost = salary * manhour / 160
material_cost = material_cost * price_home
total_cost = man_cost + material_cost + delivery_cost
profit = price - total_cost - price*export_tax
net_income = (1-tax) * profit

model = Model("Task_2")

# variables
country_num = 4
car_num = 4
x = model.addVars(country_num, car_num, vtype=GRB.INTEGER, name="x")

# objective function
net_income_allcars = gp.quicksum(net_income[i, j] * x[i, j] for i in range(4) for j in range(4))
model.setObjective(net_income_allcars, GRB.MAXIMIZE)

# budget constraint
total_cost_allcars = gp.quicksum(total_cost[i, j] * x[i, j] for i in range(4) for j in range(4))
model.addConstr(total_cost_allcars <= 40e9, "budget_constraint")

# minimum production
for j in range(car_num):
    model.addConstr(gp.quicksum(x[i, j] for i in range(4)) >= min_prod[j], name=f"minimum_production_{j}")

# minimum demand
for i in range(4):
    for j in range(4):
        model.addConstr(x[i, j] >= demand[i, j], name=f"minimum_demand_{i}_{j}")

# no export of Musa & Giulia
model.addConstr(x[0, 3] == 0, name="Giulia2Poland")
model.addConstr(x[2, 2] == 0, name="Musa2US")


model.optimize()

if model.status == GRB.OPTIMAL:
    x_sol = np.array([[x[i, j].X for j in range(4)] for i in range(4)])
    print("Optimal solution (x matrix):")
    print(x_sol)

    print(f"Optimal objective value: {model.objVal}")
else:
    print("No optimal solution found.")
