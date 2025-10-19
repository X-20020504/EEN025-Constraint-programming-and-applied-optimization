from z3 import *

def tower_of_hanoi(ds=3, tws=3, ts=7):
    # Boolean variables
    on = [[[Bool(f"on_{d}_{tw}_{t}") for t in range(ts+1)]
            for tw in range(tws)] for d in range(ds)]
    obj = [[Bool(f"obj_{d}_{t}") for t in range(ts)] for d in range(ds)]
    from_ = [[Bool(f"from_{tw}_{t}") for t in range(ts)] for tw in range(tws)]
    to_   = [[Bool(f"to_{tw}_{t}") for t in range(ts)] for tw in range(tws)]

    s = Solver()

    # (3) Precondition I
    for d in range(ds):
        for tw in range(tws):
            for t in range(ts):
                smaller = Or([on[k][tw][t] for k in range(d)])
                s.add(Implies(And(on[d][tw][t], smaller), Not(obj[d][t])))

    # (4) Precondition II
    for d in range(ds):
        for tw in range(tws):
            for twp in range(tws):
                for t in range(ts):
                    smaller_dest = Or([on[k][twp][t] for k in range(d)])
                    s.add(Implies(And(on[d][tw][t], smaller_dest),
                                  Not(And(obj[d][t], to_[twp][t]))))

    # (5) Uniqueness of from
    for d in range(ds):
        for tw in range(tws):
            for t in range(ts):
                others = [Not(from_[x][t]) for x in range(tws) if x != tw]
                s.add(Implies(And(on[d][tw][t], obj[d][t]),
                              And(from_[tw][t], *others)))

    # (6) One destination tower per step
    for t in range(ts):
        s.add(AtMost(*[to_[tw][t] for tw in range(tws)], 1))
        s.add(AtLeast(*[to_[tw][t] for tw in range(tws)], 1))

    # (7) One object per step
    for t in range(ts):
        s.add(AtMost(*[obj[d][t] for d in range(ds)], 1))
        s.add(AtLeast(*[obj[d][t] for d in range(ds)], 1))

    # (8) Non-moving disks
    for d in range(ds):
        for tw in range(tws):
            for t in range(ts):
                others = [Not(on[d][tw2][t+1]) for tw2 in range(tws) if tw2 != tw]
                s.add(Implies(And(Not(obj[d][t]), on[d][tw][t]),
                              And(on[d][tw][t+1], *others)))

    # (9) Distinct from/to
    for tw in range(tws):
        for t in range(ts):
            s.add(Implies(from_[tw][t], Not(to_[tw][t])))

    # (10) Update rule
    for d in range(ds):
        for tw in range(tws):
            for twp in range(tws):
                for t in range(ts):
                    if t < ts:
                        others = [Not(on[d][x][t+1]) for x in range(tws) if x != twp]
                        s.add(Implies(And(obj[d][t], from_[tw][t], to_[twp][t]),
                                      And(on[d][twp][t+1], *others)))

    # (11) Initial/Final state
    for d in range(ds):
        s.add(on[d][0][0])
        for tw in range(1, tws):
            s.add(Not(on[d][tw][0]))
        s.add(on[d][tws-1][ts])
        for tw in range(tws-1):
            s.add(Not(on[d][tw][ts]))

    # Solve
    print(f"Solving Tower of Hanoi with {ds} disks, {tws} towers, {ts} steps...")
    if s.check() == sat:
        m = s.model()
        print("SAT – solvable sequence found.\n")
        for t in range(ts):
            for d in range(ds):
                if m[obj[d][t]]:
                    src = [i for i in range(tws) if m[from_[i][t]]][0]
                    dst = [i for i in range(tws) if m[to_[i][t]]][0]
                    print(f"Step {t+1}: move disk {d+1} from tower {src+1} to tower {dst+1}")
    else:
        print("UNSAT – puzzle not solvable in given number of steps.")

# Example run
for disks in range(3, 8):
    tower_of_hanoi(ds=disks, tws=3, ts=2**disks - 1)
