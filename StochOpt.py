import h5py
import time
import numpy as np
import gurobipy
import cvxpy as cp
import operator
import functools
# Read the product costs and prices dictionary calcuated earlier after the simluations. This dictionary is strctured as follows
#dic={product ID: [product cost, product price]} where prod ID =[0,25699], and each product has a array with the cost and price
#being the first and second element
def sumproduct(*lists):
    return sum(functools.reduce(operator.mul, data) for data in zip(*lists))
product_pricet={}
s = open('product-price.txt', 'r').read()
product_pricet = eval(s)
cost=[]
price=[]
num_scen =10
for k,v in product_pricet.items():
    cost.append(product_pricet[k][0])
    price.append(product_pricet[k][1])
C_u=[p-c for p,c in zip(price,cost)]# coefficient of underage costs for each product ( C_u = price - cost)
C_o= cost # coeficient of overage costs for each product.We assume zero salvage and the whole excesss inventory is written off
print(len(C_u))
start= time.time()   
with h5py.File('store-scen.hdf5', 'r+') as f:
    dtest = f['Scenarios']
    #Defining the decision variables
    X= cp.Variable(len(product_pricet))
    obj =0
    con =[]
    for k in range(num_scen):
        a = cp.Variable(len(product_pricet))
        b = cp.Variable(len(product_pricet))
        over = [x- d for x,d in zip(X,dtest[k])]
        obj+= sumproduct(a,C_o)  + sumproduct(b, C_u)
        con.append(a>=0)
        con.append(b>=0)
        con.append([a[o]>=over[o] for o in range(len(over))])
        con.append([b[o]>=-over[o] for o in range(len(over))])
        print(k)
    e1 = time.time()
    print("added objective and constraints", e1-start)
    
    OptSol ={}
    prob = cp.Problem(cp.Minimize(obj/num_scen),con)
    prob.solve(solver = cp.gurobi)
    e2 = time.time()
    print("SOLVED", e2-e1)
    OptSol[0]= (prob.value)
    for k in range(1,len(product_pricet)+1):
        OptSol[k]=(X.value[k-1])
    with open('optimalproducts.txt', 'w') as write:
        print(OptSol, file=write)
f.close()

end = time.time()
print("TOTAL RUN TIME", end- start)

