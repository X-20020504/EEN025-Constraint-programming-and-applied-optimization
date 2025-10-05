import csv
from gurobipy import Model, GRB
import numpy as np


# read file =========================================================
filename = "data/"+"ft10.txt"
q = []
machine = []
with open(filename, "r") as f:
    reader = csv.reader(f, delimiter=" ", skipinitialspace=True)

    header1 = next(reader)  # "+++++++++++++++++++++++++++++"
    header2 = next(reader)  # "                             "
    header3 = next(reader)  # "instance ft06                "
    header4 = next(reader)  # "                             "
    header5 = next(reader)  # "+++++++++++++++++++++++++++++"
    desc = next(reader)     # "Fisher and Thompson..."

    n_jobs, n_machines = map(int, next(reader))

    for j in range(n_jobs):
        row = [int(x) for x in next(reader) if x.strip() != ""]
        # ops = [(row[i], row[i + 1]) for i in range(0, len(row), 2)]
        # jobs.append(ops)
        machine_j = [row[i] for i in range(0, len(row), 2)]
        q_j = [row[i+1] for i in range(0, len(row), 2)]
        machine.append(machine_j)
        q.append(q_j)

q = np.array(q)
machine = np.array(machine)

machine_tasks = [[] for i in range(n_machines)]
for j in range(n_jobs):
    for h in range(n_machines):
        m = machine[j][h]
        machine_tasks[m].append((j, h))

# variables =========================================================
model = Model("Task_1")
t = model.addVars(n_jobs, n_machines, vtype=GRB.INTEGER, lb=0, name="t")  # t[j,h] - time of job j's h-th operation starts
C = model.addVar(vtype=GRB.INTEGER, lb=0, name="C")  # time of the last operation ends
delta = model.addVars(n_jobs, n_machines, n_jobs, n_machines, vtype=GRB.BINARY, name="delta") # delta[j1, h1, j2, h2]

# objective function =========================================================
model.setObjective(C, GRB.MINIMIZE)

# constraints =========================================================

# job's operating sequence constraint
for j in range(n_jobs):
    for h in range(n_machines-1):
        model.addConstr(t[j, h+1] >= t[j, h] + q[j][h], name=f"job's_operating_sequence")

# machine mutex constraint
H = sum(sum(row) for row in q)

for m in range(n_machines):
    tasks = machine_tasks[m]

    for a in range(len(tasks)):
        for b in range(a + 1, len(tasks)):
            j1, h1 = tasks[a]
            j2, h2 = tasks[b]

            model.addConstr(t[j1, h1] >= t[j2, h2] + q[j2][h2] - H * delta[j1,h1,j2,h2], name=f"machine_seq2_{m}_{j1}_{h1}_{j2}_{h2}")
            model.addConstr(t[j2, h2] >= t[j1, h1] + q[j1][h1] - H * (1 - delta[j1,h1,j2,h2]), name=f"machine_seq1_{m}_{j1}_{h1}_{j2}_{h2}")

# minimize time constraint
for j in range(n_jobs):
    model.addConstr(C >= t[j, n_machines-1] + q[j][n_machines-1], name=f"job_{j}_finishing_time")

# solve the problem =========================================================
model.optimize()

if model.status == GRB.OPTIMAL:
    print(f"Optimal objective value: {model.objVal}")
else:
    print("No optimal solution found.")
