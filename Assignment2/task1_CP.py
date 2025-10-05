from z3 import *
import csv
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
start = [[Int(f"start_{j}_{h}") for h in range(n_machines)] for j in range(n_jobs)]
Cmax = Int("C")

# objective function =========================================================
opt = Optimize()
opt.minimize(Cmax)

# constraints =========================================================

# job's operating sequence constraint
for j in range(n_jobs):
    for h in range(n_machines-1):
        opt.add(start[j][h+1] >= start[j][h] + q[j][h])

# machine mutex constraint
for m in range(n_machines):
    tasks = machine_tasks[m]
    for a in range(len(tasks)):
        for b in range(a+1, len(tasks)):
            j1,h1 = tasks[a]
            j2,h2 = tasks[b]

            opt.add(Or(start[j1][h1] >= start[j2][h2] + q[j2][h2],
                       start[j2][h2] >= start[j1][h1] + q[j1][h1]))

# minimize time constraint
for j in range(n_jobs):
    opt.add(Cmax >= start[j][n_machines-1] + q[j][n_machines-1])

# variable range
H = sum(sum(row) for row in q)  #upper bound

for j in range(n_jobs):
    for h in range(n_machines):
        opt.add(start[j][h] >= 0)
        opt.add(start[j][h] <= H)
opt.add(Cmax >= 0)
opt.add(Cmax <= H)

# solve the problem =========================================================
z3.set_param('verbose', 5)

result = opt.check()

if result == sat:
    model = opt.model()
    print("Cmax =", model[Cmax])
    for j in range(n_jobs):
        for h in range(n_machines):
            print(f"Job {j}, Option {h}, start = {model[start[j][h]]}")
