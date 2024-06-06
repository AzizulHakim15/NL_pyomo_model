#Azizul Hakim
#Working group: Optimization and Optimal Control
#Project: HyBit

from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
import matplotlib.pyplot as plt   

# Define file paths
pv_file_path = "C:\\Users\\azizul\\Desktop\\hyBit\\Project\\sample\\pv_1m.csv"
wm_file_path = "C:\\Users\\azizul\\Desktop\\hyBit\\Project\\sample\\wm_1m.csv"

# Load data from CSV files
pv_data = pd.read_csv(pv_file_path, header=None)
wm_data = pd.read_csv(wm_file_path, header=None)

# Extract WM1 data
device = {'WM1': wm_data.iloc[:, 0].tolist()}

# Define Pyomo model
model = ConcreteModel()

Gen_neg = pv_data[1].to_list()
PV =  [- x for x in Gen_neg]       
D = [3000.0] * len(PV)    #consumption
#Define Buy and Sell price
priceImport = 0.23 / 1000 / 60
priceExport = 0.06 / 1000 / 60
Cbat = 5000 * 60       #Capacity of the Battery
eff = 0.9              #Efficiency of the Battery
h = 1.0

# Create variables in the 

model.IndexSet = RangeSet(0,len(PV))

# Initialize indexed variables
model.u0 = Var(model.IndexSet, within = NonNegativeReals, initialize = 0)
model.u1 = Var(model.IndexSet, bounds=(0, Cbat), within = NonNegativeReals, initialize = 0 )
model.u2 = Var(model.IndexSet, bounds=(0, Cbat), within = NonNegativeReals, initialize = 0)
model.u3 = Var(model.IndexSet, within = NonNegativeReals, initialize = 0)
model.SOC = Var(model.IndexSet, bounds=(0.2, 0.9), within = NonNegativeReals, initialize = 0.5)
model.grid_in = Var(model.IndexSet, within = NonNegativeReals, initialize = 0)
model.grid_out = Var(model.IndexSet, within = NonNegativeReals, initialize = 0)

# Add constraints
model.const = ConstraintList()


model.const.add(model.SOC[0] == 0.8)
model.const.add(model.SOC[len(PV)] == 0.4)
#Loop 0 to n-1
for i in range(0, len(PV)):

    model.const.add(model.u0[i] + model.u1[i] + model.grid_in[i] - PV[i]<= 0)
    model.const.add(model.u0[i] + model.u2[i] +model.grid_out[i] - D[i]<= 0)
    model.const.add(model.u1[i] * model.u2[i] == 0)
    
    model.const.add(PV[i] - model.u0[i] - model.u1[i] == model.grid_in[i])
    model.const.add(D[i] - model.u0[i] - model.u2[i] == model.grid_out[i])
    #model.const.add( (PV[i] - model.u1[i] - model.u0[i])- (D[i] - model.u0[i] - model.u2[i]) == model.u3[i])
    
    

# Loop 0 to n-2
for i in range(0, (len(PV)-1)):

    model.const.add((model.SOC[i + 1]- model.SOC[i] - (h / 2) * (((model.u1[i + 1] + model.u3[i + 1] - model.u2[i + 1]) * eff )/ Cbat + ((model.u1[i] + model.u3[i + 1] - model.u2[i]) * eff )/ Cbat)) == 0)

#Grid_values = 0


# Set objective
def objective_rule(model):
    return sum(
        (D[i] - model.u0[i] - model.u2[i]+ model.u3[i]) * priceImport - (PV[i] - model.u0[i] - model.u1[i]) * priceExport 
        for i in range(len(PV))
    )
model.obj = Objective(rule=objective_rule, sense=minimize)


# Solve the model...
solver = SolverFactory('scip')

# Specify the SCIP options

#scip_options = {'settings': "/home/azizul/Downloads/scip-9.0.1"}

# Solve the model with the specified parameter file
results = solver.solve(model, tee=True)#, options=scip_options)
#model.display()
#model.pprint()
#results.write()
print(value(model.obj))


#Solver time
solver_time = results.solver.time


####### PLot #######

#Extract values of u0, u1, u2, PV, and SOC

u0_values = [value(model.u0[i]) for i in model.IndexSet]
u1_values = [value(model.u1[i]) for i in model.IndexSet]
u2_values = [value(model.u2[i]) for i in model.IndexSet]
u3_values = [value(model.u3[i]) for i in model.IndexSet]
grid_out_values = [value(model.grid_out[i]) for i in model.IndexSet]
#grid__values = [value(Grid_values[i]) for i in model.IndexSet]
 
SOC_values = [value(model.SOC[i]) for i in model.IndexSet]
SOC_percent = [val * 100 for val in SOC_values]


# Create x-axis values (assuming index set)
x_values = list(range(len(u0_values)))
PV__values = list(range(len(PV)))

#Declare Rows, columns and Figure size of subplots
fig, axs = plt.subplots(nrows=5, ncols=1, figsize=(10, 10))

# Plot u0, u1, u2, P, and SOC
axs[0].plot(x_values, u0_values, label='PV')
axs[0].plot(x_values, u1_values, label='Battery Charge from PV')
axs[0].plot(x_values, u2_values, label='Battery Discharge')

axs[0].set_title('PV to Demand, Battery Charge and Discharge')


# Plot on the second subplot


axs[1].plot(x_values, u3_values, label='Grid to Battery')
axs[1].set_title('Grid to battery')

axs[2].plot(x_values, grid_out_values, label='Grid to Demand')
axs[2].set_title('Grid to Demand')

axs[3].plot(x_values, SOC_percent, label='SOC')
axs[3].set_title('State of Charge in % ')

# Plot on the third subplot
axs[4].plot(PV__values, PV, label='Power Generation' )
axs[4].plot(PV__values, D, label='Basic Consumption' )
axs[4].set_title('Power Generation & Consumption')


# Add legend to the first subplot
axs[0].legend()
axs[1].legend()
axs[2].legend()
axs[3].legend()
axs[4].legend()

# Adjust layout and display the plot
plt.subplots_adjust(hspace=0.5)
plt.show()
