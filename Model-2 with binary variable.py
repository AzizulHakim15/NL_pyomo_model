#Azizul Hakim
#Working group: Optimization and Optimal Control
#Project: HyBit

from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   

# Define file paths
pv_file_path = "/media/azizul/TANVIR/windows/New folder/data/PV1d.csv"
wm_file_path = "/media/azizul/TANVIR/windows/New folder/wm_1m.csv"

# Load data from CSV files
pv_data = pd.read_csv(pv_file_path, header=None)
wm_data = pd.read_csv(wm_file_path, header=None)
#Timestamp
#timestamps = pd.date_range('2024-01-01 00:00:00', periods=1440, freq='T')


# Define Pyomo model
model = ConcreteModel()
Gen_neg = pv_data[4].to_list()
PV =  [ x for x in Gen_neg]    
Gen_wm = wm_data[1].to_list()
Device =  [ x for x in Gen_wm]    #Device Consumption
D = [20000.0] *( len(PV))   #Basic consumption

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
#model.D = RangeSet(0,l)
# Initialize indexed variables
model.u0 = Var(model.IndexSet, bounds=(0, 1e20), within = NonNegativeReals, initialize = 0)
model.C = Var(model.IndexSet, bounds=(0, 1e20), within = NonNegativeReals, initialize = 0)
model.is_start = Var(model.IndexSet, bounds =(0, 1), within = Binary)



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
    
    model.const.add( model.u0[i] - PV[i] <= 0)
    model.const.add(  model.u0[i] - model.C[i] <= 0)
    
model.const.add( sum(model.is_start[i] for i in model.IndexSet) == 1)   


for i in range(n-l, n):
   model.const.add(model.is_start[i] == 0)


######################################################

# Case 1: i in {l, ..., n-1}
for i in range(l, n):
    model.const.add(model.C[i] == D[i] + sum(model.is_start[i - j] * Device[j] for j in range(0,l)))
    
# Case 2: i in {0, ..., l-1}
for i in range(0, l): 
    model.const.add(model.C[i] == D[i] + sum(model.is_start[i - j] * Device[j] for j in range(0,i+1)))


    


# Solve the model...
solver = SolverFactory('gurobi')
# Specify the SCIP options

#scip_options = {'settings': "/home/azizul/Downloads/scip-9.0.1"} 

# Solve the model with the specified parameter file
results = solver.solve(model, tee=True)#, options=scip_options)
#model.display()
#model.pprint()
#results.write()
print(value(model.obj))

################################################################################################# 
# Count total number of high Bits
model.num_ones = Expression(expr=sum(model.is_start[i] for i in model.IndexSet))
# Get the locations where model.is_start[i] == 1
locations_of_ones = [i for i in model.IndexSet if value(model.is_start[i]) == 1]
############################################################

#Solver time

solver_time = results.solver.time
print('Solver time =', solver_time)
print("Number of ones in model_is_start:", value(model.num_ones))
print("Locations of ones:", locations_of_ones)


######################## PLot ################################

#Extract values of u0, C, P, and SOC
u0_values = [value(model.u0[i]) for i in model.IndexSet]
C_values = [value(model.C[i]) for i in model.IndexSet]
is_start_values = [value(model.is_start[i]) for i in model.IndexSet]


# Create x-axis values (assuming index set)
x_values = list(range(0, len(u0_values)))
PV__values = list(range(0, n))
c_val = list(range(0, len(C_values)))
D_val = list(range(0, l))
#Declare Rows, columns and Figure size of subplots
fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))

# Plot u0, D, PV, and Consumptions
axs[0].plot(x_values, u0_values, label='Self Consumed')
axs[0].plot(PV__values, PV, label='PV')
axs[0].plot(PV__values, D, label='Basic demand')
#axs[0].plot(D_val, Device, label='Device')
#axs[0].plot(t_val, temp_values, label='Device')
axs[0].plot(c_val, C_values, label='Overall consumptions')
axs[0].set_title('PV , Basic Demand, self consumed and overall consumptions')
axs[0].fill_between(x_values, u0_values, color='blue', alpha=0.6)
axs[0].fill_between(PV__values, D, color='green', alpha=0.2)
axs[0].fill_between(PV__values, PV, color='orange', alpha=0.2)
axs[0].fill_between(c_val, C_values, color='red', alpha=0.1)
#axs[0].fill_between(D_val, Device, color='red', alpha=0.1)


# Plot on the second subplot
axs[1].plot(c_val, C_values, label='Overall consumptions')
axs[1].fill_between(c_val, C_values, color='blue', alpha=0.4)
#axs[1].plot(D_val, Device, label='Device')


# Add legend to the first subplot
axs[0].legend()
axs[1].legend()

# Adjust layout and display the plot
plt.subplots_adjust(hspace=1.5)
plt.show()


