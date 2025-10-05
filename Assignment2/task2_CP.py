from z3 import *
import csv
import numpy as np
from A_star import *
from math import ceil

# read file =========================================================
filename = "data/"+"ft06.txt"
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


coordinates = {"warehouse": {"i": 2, "j": 0},
               "delivery": {"i": 2, "j": 7},
               "M1": {"i": 1, "j": 4},
               "M2": {"i": 3, "j": 3},
               "M3": {"i": 3, "j": 5},
               "M4": {"i": 0, "j": 2},
               "M5": {"i": 2, "j": 2},
               "M6": {"i": 0, "j": 6}}

# variables =========================================================
t = [[Int(f"start_{j}_{h}") for h in range(n_machines)] for j in range(n_jobs)]
Cmax = Int("C")

# objective function =========================================================
opt = Optimize()
opt.minimize(Cmax)

# constraints =========================================================

# job's operating sequence constraint
for j in range(n_jobs):
    start = coordinates["warehouse"]
    end = coordinates[f"M{machine[j][0]+1}"]
    distance = A_star(start, end)
    moving_time = ceil(distance/5)

    opt.add(t[j][0] >= moving_time)

for j in range(n_jobs):
    for h in range(n_machines-1):
        start = coordinates[f"M{machine[j][h]+1}"]
        end = coordinates[f"M{machine[j][h+1]+1}"]
        distance = A_star(start, end)
        moving_time = ceil(distance / 5)

        opt.add(t[j][h+1] >= t[j][h] + q[j][h] + moving_time)

# machine mutex constraint
for m in range(n_machines):
    tasks = machine_tasks[m]
    for a in range(len(tasks)):
        for b in range(a+1, len(tasks)):
            j1,h1 = tasks[a]
            j2,h2 = tasks[b]

            opt.add(Or(t[j1][h1] >= t[j2][h2] + q[j2][h2],
                       t[j2][h2] >= t[j1][h1] + q[j1][h1]))

# minimize time constraint
for j in range(n_jobs):
    start = coordinates[f"M{machine[j][-1]+1}"]
    end = coordinates["delivery"]
    distance = A_star(start, end)
    moving_time = ceil(distance/5)

    opt.add(Cmax >= t[j][n_machines-1] + q[j][n_machines-1] + moving_time)

# variable range
move_start = np.array([A_star(coordinates["warehouse"], coordinates[f"M{machine[j][0]+1}"]) for j in range(n_jobs)])
move_between = np.array([[A_star(coordinates[f"M{machine[j][h]+1}"], coordinates[f"M{machine[j][h+1]+1}"]) for h in range(n_machines-1)] for j in range(n_jobs)])
move_end = np.array([A_star(coordinates[f"M{machine[j][-1]+1}"], coordinates["delivery"]) for j in range(n_jobs)])

H = (sum(sum(row) for row in q)
     + np.sum(np.ceil(move_start/5))
     + np.sum(np.ceil(move_between/5))
     + np.sum(np.ceil(move_end/5)))  # upper bound

for j in range(n_jobs):
    for h in range(n_machines):
        opt.add(t[j][h] >= 0)
        opt.add(t[j][h] <= H)
opt.add(Cmax >= 0)
opt.add(Cmax <= H)

# solve the problem =========================================================
z3.set_param('verbose', 5)

opt.minimize(Cmax)
best = None

while opt.check() == sat:
    m = opt.model()
    val = m[Cmax].as_long()
    print("Feasible:", val)
    if best is None or val < best:
        best = val
    opt.add(Cmax < val)

