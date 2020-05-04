from pyomo.environ import *

# Creates two vectors that represent the number of A and B ordered machines respectively per week.
# eg. consA[2] is the number of A ordered machines ordered for the second week.
consA = [0, 55, 55, 44, 0, 45, 45, 36, 35, 35]
consB = [0, 38, 38, 30, 0, 48, 48, 58, 57, 58]

week = range(1, 10)
weekZ = range(0, 10)

# Creates linear model.
mdl = ConcreteModel()

# Creates model's constraint list.
mdl.conList = ConstraintList()

# Adds two variable vectors each representing the production of A or B machines per week.
mdl.prodA = Var(week, domain=NonNegativeIntegers)
mdl.prodB = Var(week, domain=NonNegativeIntegers)

# Adds a binary variable vector that represents the state of the production line per week.
# 0->A machines, 1->B machines
mdl.deci = Var(weekZ, domain=Binary)
# Initializes state of production line's to A machines.
mdl.conList.add(expr = mdl.deci[0] == 0)

# Adds a binary variable vector that represents a change of the state of the production line's per week.
# 0->no-change, 1->change eg. chan[2] = 0 means that the state during the second week is the same as last week's.
mdl.chan = Var(week, domain=Binary)

# Adds two variable vectors that represent the stock of A or B machines respectively per week.
mdl.storA = Var(weekZ, domain=NonNegativeIntegers)
mdl.storB = Var(weekZ, domain=NonNegativeIntegers)
# Initializes stock of A machines to 125 and B machines to 143.
mdl.conList.add(expr = mdl.storA[0] == 125)
mdl.conList.add(expr = mdl.storB[0] == 143)

# Constraint setup loop.
for i in week:
    # Constraints the production of A machines per week to 100.
    mdl.conList.add(expr = mdl.prodA[i] <= 100)

    # Constraints the production of B machines per week to 80.
    mdl.conList.add(expr = mdl.prodB[i] <=  80)

    # Constraints the stock of A machines to be more than 80% of next week's order.
    mdl.conList.add(expr = mdl.storA[i-1] >= 0.8*consA[i])

    # Constraints the stock of B machines to be more than 80% of next week's order.
    mdl.conList.add(expr = mdl.storB[i-1] >= 0.8*consB[i])

    # Constraints the production to be able to fulfill current week's order of A machines.
    #mdl.conList.add(expr = mdl.prodA[i] + mdl.storA[i-1] >= consA[i])

    # Constraints the production to be able to fulfill current week's order of B machines.
    #mdl.conList.add(expr = mdl.prodB[i] + mdl.storB[i-1] >= consB[i])

    # Defines that next week's stock of A machines is equal to:
    # last week's stock + current week's produced machines - current week's ordered machines.
    mdl.conList.add(expr = mdl.storA[i] == mdl.storA[i-1] + mdl.prodA[i] - consA[i])

    # Defines that next week's stock of B machines is equal to:
    # last week's stock + current week's produced machines - current week's ordered machines.
    mdl.conList.add(expr = mdl.storB[i] == mdl.storB[i-1] + mdl.prodB[i] - consB[i])

    # Constraints the state of the production line to be either A or B using the big-M method.
    mdl.conList.add(expr = mdl.prodA[i] <= 1000*(1-mdl.deci[i]))
    mdl.conList.add(expr = mdl.prodB[i] <= 1000*mdl.deci[i])

    # Sets the value of the variable mdl.chan.
    mdl.conList.add(expr = mdl.deci[i] - mdl.deci[i-1] <= mdl.chan[i])
    mdl.conList.add(expr = mdl.deci[i-1] - mdl.deci[i] <= mdl.chan[i])

# Creates the model's cost function.
mdl.totalCost = Objective(expr =
    sum(mdl.prodA[i]*225 + mdl.prodB[i]*310 for i in week) +
    sum(mdl.storA[i]*0.00375*225 + mdl.storB[i]*0.195/52*310 for i in week) +
    500*sum (mdl.chan[i] for i in week),
    sense = minimize)

# Solves model with glpk solver.
SolverFactory('glpk').solve(mdl).write()

# Prints cost.
print("Cost = ", mdl.totalCost())

# Prints week number.
print("week#:", end = " ")
for i in weekZ:
    print("{:6}".format(weekZ[i]), end = " ")
print()

# Prints A machines production.
print("prodA:", end = " ")
print("{:6}".format(''), end = " ")
for i in week:
    print("{:6}".format(mdl.prodA[i].value), end = " ")
print()

# Prints B machines production.
print("prodB:", end = " ")
print("{:6}".format(''), end = " ")
for i in week:
    print("{:6}".format(mdl.prodB[i].value), end = " ")
print()

# Prints A machines stock.
print("storA:", end = " ")
for i in weekZ:
    print("{:6}".format(mdl.storA[i].value), end = " ")
print()

# Prints B machines stock.
print("storB:", end = " ")
for i in weekZ:
    print("{:6}".format(mdl.storB[i].value), end = " ")
print()

# Prints state of the production line. 0->A machines, 1->B machines
print("deci: ", end = " ")
for i in weekZ:
    print("{:6}".format(mdl.deci[i].value), end = " ")
print()

# Prints change of the state of the production line. 0->no-change, 1->change
print("chan: ", end = " ")
print("{:6}".format(''), end = " ")
for i in week:
    print("{:6}".format(mdl.chan[i].value), end = " ")
print()