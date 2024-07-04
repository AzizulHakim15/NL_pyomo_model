#Azizul Hakim
#Working group: Optimization and Optimal Control
#Project: HyBit

from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   

# Define file paths
pv_file_path = "C:\\Users\\azizul\\Desktop\\hyBit\\Project\\sample\\pv_1m.csv"
wm_file_path = "C:\\Users\\azizul\\Desktop\\hyBit\\Project\\sample\\wm_1m.csv"

# Load data from CSV files
pv_data = pd.read_csv(pv_file_path, header=None)
wm_data = pd.read_csv(wm_file_path, header=None)
#Timestamp
timestamps = pd.date_range('2024-01-01 00:00:00', periods=1441, freq='T')


# Define Pyomo model
model = ConcreteModel()
Gen_neg = pv_data[1].to_list()
PV =  [- x for x in Gen_neg]    
Gen_wm = wm_data[1].to_list()
Device =  [ x for x in Gen_wm]    #Device Consumption
D = [1000.0] *( len(PV))   #Basic consumption

#Define Buy and Sell price
priceImport = 0.23 / 1000 / 60
priceExport = 0.06 / 1000 / 60
Cbat = 5000 * 60       #Capacity of the Battery
eff = 0.9              #Efficiency of the Battery
h = 1.0
n = len(PV)
l = len(Device)


# Create variables in the model
model.IndexSet = RangeSet(0,n)

# Initialize indexed variables
model.u0 = Var(model.IndexSet, bounds=(0, 1e20), within = NonNegativeIntegers, initialize = 0)
model.C = Var(model.IndexSet, bounds=(0, 1e20), within = NonNegativeReals, initialize = 0)
model.is_start = Var(model.IndexSet, bounds =(0.0, 1.0), within = NonNegativeReals, initialize = 0)
model.bin = Var(model.IndexSet, bounds=(0,1), within = Binary, initialize = 0)



# Set objective
def objective_rule(model):
    return sum(
        (model.C[i] - model.u0[i]) * priceImport - (PV[i] - model.u0[i]) * priceExport 
        for i in range(0, n)
    )
model.obj = Objective(rule=objective_rule, sense=minimize)



# Add constraints
model.const = ConstraintList()

#Loop 0 to n-1
for i in range(0, n):
    
    model.const.add( PV[i] - model.u0[i] >= 0)
    model.const.add(  model.u0[i] - model.C[i] <= 0)
    



#####################################################
#for i in range(0,n):
#    sum(model.is_start[i])==1
#    #model.is_start[i].fix(1)

def start_constraint_rule(model):
    return sum(model.is_start[i] for i in model.IndexSet) == 1
model.start_constraint = Constraint(rule=start_constraint_rule)

for i in range(n-l, n):
   model.is_start[i] == 0


######################################################



temp= 0
# Case 1: i in {0, ..., l-1}
for i in range(0,l):
    temp += sum(model.bin[i - j] * Device[j] for j in range(0,i+1))  
    model.const.add(model.C[i] == D[i] + temp)
    #model.C[i] = D[i] + temp

# Case 2: i in {l, ..., n-1}
for i in range(l, n):
    temp += sum(model.bin[i - j] * Device[j] for j in range(0,l))
    model.const.add(model.C[i] == D[i] + temp)
    #model.C[i] = D[i] + temp
'''
temp= 0
for i in range(0,n):
    
    # Case 2: i in {0, ..., l-1}
    for i in range(0,l):
        temp += sum(model.bin[i - j] * Device[j] for j in range(0,i+1))  
        model.const.add(model.C[i] == D[i] + temp)
        #model.C[i] = D[i] + temp

    #temp= 0
    # Case 1: i in {l, ..., n-1}
    for i in range(l, n):
       temp += sum(model.bin[i - j] * Device[j] for j in range(0,l))
       model.const.add(model.C[i] == D[i] + temp)
       #model.C[i] = D[i] + temp    


'''


# Solve the model...
solver = SolverFactory('gurobi')
solver.options['NonConvex'] = 2  # Set NonConvex parameter to 2
results = solver.solve(model, tee=True)
#model.display()
#model.pprint()
#results.write()
print(value(model.obj))



####### PLot #######

#Extract values of u0, u1, u2, P, and SOC
u0_values = [value(model.u0[i]) for i in model.IndexSet]
u0_values = u0_values[:len(timestamps)]
C_values = [value(model.C[i]) for i in model.IndexSet]
C_values = C_values[:len(timestamps)]
is_start_values = [value(model.is_start[i]) for i in model.IndexSet]
is_start_values = is_start_values[:len(timestamps)]
#device_values = [value(Device)]
device_values = timestamps[:len(Device)]



plt.plot(timestamps, PV, label='PV')
plt.fill_between(timestamps, PV, color='skyblue', alpha=0.4)
plt.plot(timestamps, C_values, label='Overall Consumption')
plt.fill_between(timestamps, C_values, color='orange', alpha=0.4)
#plt.plot(timestamps, D, label='Basic Consumption')
#plt.fill_between(timestamps, D, color='yellow', alpha=0.4)
plt.plot(timestamps, u0_values, label='self Consumption')
plt.fill_between(timestamps, u0_values, color='pink', alpha=0.4)
plt.plot(device_values, Device, label='Device')
plt.fill_between(device_values, Device, color='purple', alpha=0.4)

plt.legend()
plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval= 1))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter( '%H'))

plt.show()
