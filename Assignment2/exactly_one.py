from z3 import*

x=[[Bool('allo_res%s_op%s' % (i+1,j+1)) for j in range(5)] for i in range(5)]

# if I want n variables to be true out of the whole set:
n = 1

# this is how to manually use the EXACTLY ONE function
exactly=[
    And(
        PbEq(((x[0][0],1),(x[0][1],1)),n),
        PbEq(((x[1][0],1),(x[1][1],1)),n)
# N.B. the number 1 in the expression after the variable is required for the constraint to work
    )
]

print(exactly)

# this is how to iterate the EXACTLY one constraint over a list of variables

exactly_2 = [
    PbGe( [    (x[i][j],1) for j in range(5)],n) for i in range(5)
]

print(exactly_2)

# it is possible to define also constraints such as AT MOST and AT LEAST just in the same way

#try to substitute PbEq with PbLe or PbGe