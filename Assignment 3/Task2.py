# task2_robot_sorting_z3.py
# Robot sorting problem (Task 2) -- Z3 implementation
# Supports two objectives: "moves" (min total moves) and "manhattan" (min total Manhattan distance)
# Author: (you)
from z3 import *

def index_of(x, y, n):
    return x * n + y

def coord_of(index, n):
    # In model extraction: x = index // n, y = index % n
    return (index // n, index % n)

def robot_sorting_z3(B, n, T, init_positions, goal_positions, objective='moves', optimize=True, debug=True):
    """
    B: number of bricks (int)
    n: grid side (int) -> P = n*n cells, indexed 0..P-1
    T: horizon (int) number of steps (must be >= 1)
    init_positions, goal_positions: lists of length B of (x,y) tuples (0-based)
    objective: 'moves' or 'manhattan' or 'squared_euclid'
    optimize: if True use Optimize() and minimize objective; otherwise just check satisfiability
    debug: print plan
    """
    assert len(init_positions) == B and len(goal_positions) == B
    P = n * n

    # Z3 solver (Optimize to support minimization)
    solver = Optimize() if optimize else Solver()

    # Variables
    pos = [[Int(f"pos_{b}_{t}") for t in range(T+1)] for b in range(B)]
    move = [[Bool(f"move_{b}_{t}") for t in range(T)] for b in range(B)]

    # Domains: 0 .. P-1
    for b in range(B):
        for t in range(T+1):
            solver.add(pos[b][t] >= 0, pos[b][t] < P)

    # No-overlap: pairwise distinct per time
    for t in range(T+1):
        for b1 in range(B):
            for b2 in range(b1+1, B):
                solver.add(pos[b1][t] != pos[b2][t])

    # Move equivalence: move(b,t) <-> pos[b,t] != pos[b,t+1]
    for b in range(B):
        for t in range(T):
            solver.add(move[b][t] == (pos[b][t] != pos[b][t+1]))

    # Single action per step (single robot)
    for t in range(T):
        solver.add(PbLe([ (move[b][t], 1) for b in range(B) ], 1))

    # Initial and goal positions
    for b in range(B):
        ix0 = index_of(init_positions[b][0], init_positions[b][1], n)
        ixf = index_of(goal_positions[b][0], goal_positions[b][1], n)
        solver.add(pos[b][0] == ix0)
        solver.add(pos[b][T] == ixf)

    # Objective construction
    if objective == 'moves':
        total_moves = Sum([ If(move[b][t], 1, 0) for b in range(B) for t in range(T) ])
        if optimize:
            solver.minimize(total_moves)
        else:
            solver.add(total_moves <= sum([1 for _ in range(B)]))  # placeholder
    elif objective == 'manhattan' or objective == 'squared_euclid':
        # helper to get x,y from pos int: x = pos / n, y = pos % n
        cost_terms = []
        for b in range(B):
            for t in range(T):
                p_cur = pos[b][t]
                p_nxt = pos[b][t+1]
                # x and y extraction (integer)
                x_cur = p_cur / n        # integer division in Z3
                y_cur = Mod(p_cur, n)
                x_nxt = p_nxt / n
                y_nxt = Mod(p_nxt, n)
                dx = x_nxt - x_cur
                dy = y_nxt - y_cur
                abs_dx = If(dx >= 0, dx, -dx)
                abs_dy = If(dy >= 0, dy, -dy)
                if objective == 'manhattan':
                    per_move_cost = abs_dx + abs_dy
                else: # squared euclid
                    per_move_cost = dx*dx + dy*dy
                cost_terms.append( If(move[b][t], per_move_cost, 0) )
        total_cost = Sum(cost_terms) if cost_terms else IntVal(0)
        if optimize:
            solver.minimize(total_cost)
        else:
            # no minimization: optionally constrain to some budget
            pass
    else:
        raise ValueError("Unknown objective")

    # Solve
    if debug:
        print(f"Solving: B={B}, grid={n}x{n}, T={T}, objective={objective}, optimize={optimize}")

    if optimize:
        res = solver.check()
        if res == sat or res == sat:
            m = solver.model()
        else:
            print("UNSAT or UNKNOWN")
            return None
    else:
        if solver.check() != sat:
            print("UNSAT: No solution for given horizon")
            return None
        m = solver.model()

    # Extract plan: list moves
    plan = []
    for t in range(T):
        moved = False
        for b in range(B):
            if is_true(m.eval(move[b][t])):
                p0 = m.eval(pos[b][t]).as_long()
                p1 = m.eval(pos[b][t+1]).as_long()
                x0, y0 = divmod(p0, n)
                x1, y1 = divmod(p1, n)
                plan.append( (t, b, (x0,y0), (x1,y1)) )
                moved = True
                break
        if not moved:
            plan.append( (t, None, None, None) )  # idle step

    if debug:
        print("Plan (time, brick, from, to):")
        for step in plan:
            if step[1] is None:
                print(f" Step {step[0]}: (idle)")
            else:
                print(f" Step {step[0]+1}: move brick {step[1]} from {step[2]} to {step[3]}")
        if objective == 'moves':
            tv = m.eval(Sum([ If(move[b][t], 1, 0) for b in range(B) for t in range(T) ]))
            print("Total moves (model):", tv)
        else:
            # evaluate cost expression (recreate)
            if objective == 'manhattan':
                total = 0
                for b in range(B):
                    for t in range(T):
                        if is_true(m.eval(move[b][t])):
                            p0 = m.eval(pos[b][t]).as_long()
                            p1 = m.eval(pos[b][t+1]).as_long()
                            x0,y0 = divmod(p0,n); x1,y1 = divmod(p1,n)
                            total += abs(x1-x0)+abs(y1-y0)
                print("Total Manhattan (model):", total)
            else:
                total = 0
                for b in range(B):
                    for t in range(T):
                        if is_true(m.eval(move[b][t])):
                            p0 = m.eval(pos[b][t]).as_long()
                            p1 = m.eval(pos[b][t+1]).as_long()
                            x0,y0 = divmod(p0,n); x1,y1 = divmod(p1,n)
                            total += (x1-x0)**2 + (y1-y0)**2
                print("Total squared Euclidean (model):", total)

    return m, plan

# Example usage
if __name__ == "__main__":
    # small example: 3x3 grid, 3 bricks
    n = 3
    B = 3
    # initial positions (x,y)
    init = [(0,0), (0,1), (0,2)]
    goal = [(2,2), (2,1), (2,0)]
    T = 7  # horizon (guess)
    # Try minimizing moves
    model, plan = robot_sorting_z3(B=B, n=n, T=T, init_positions=init, goal_positions=goal,
                                  objective='moves', optimize=True, debug=True)
