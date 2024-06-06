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
D = [1000.0] * len(PV)    #consumption

#Define Buy and Sell price
priceImport = 0.23 / 1000 / 60
priceExport = 0.06 / 1000 / 60
Cbat = 5000 * 60       #Capacity of the Battery
eff = 0.9              #Efficiency of the Battery
h = 1.0
n = len(PV)
# Create variables in the model
model.IndexSet = RangeSet(0,len(PV))


# Initialize indexed variables
model.u0 = Var(model.IndexSet, bounds=(0, 1e20), within = Reals, initialize = 0)
model.C = Var(model.IndexSet,bounds =(0, 1e20), within = NonNegativeReals, initialize = 0)
model.is_start = Var(model.IndexSet, bounds=(0, 1), within = Binary)
model.bin = Var(model.IndexSet, bounds=(0, 1), within = Binary)


# Add constraints
model.const = ConstraintList()


#Loop 0 to n-1
for i in range(0, n):

    model.const.add(model.u0[i] - PV[i] <= 0)
    model.const.add(model.u0[i] - model.C[i] <= 0)
    model.const.add(model.is_start[i] >= 0.5 if model.bin[i] == 1 else Constraint.Skip)
    model.const.add(model.is_start[i] <= 0.5 if model.bin[i] == 0 else Constraint.Skip)
   
    
    

# Loop 0 to n-2
for i in range(0, n):

    model.const.add(sum(model.is_start[i] == 1 ))


for i in range(n - l, n):
    model.const.add(model.is_start[i] == 0)

# Additional constraints based on nested sums
def constr_C_D_temp(model, i):
    temp = sum(model.bin[i-j] * device[0][j] for j in range(min(i+1, l)))
    return model.C[i] == D[i] + temp
model.constr_C_D_temp = Constraint(model.IndexSet, rule=constr_C_D_temp)

model.const.add(C[i]== D[i]+ )


# Set objective
def objective_rule(model):
    return sum(
        (model.C[i] - model.u0[i]) * priceImport - (PV[i] - model.u0[i]) * priceExport 
        for i in range(0, n)
    )
model.obj = Objective(rule=objective_rule, sense=minimize)

# Solve the model...
solver = SolverFactory('gurobi')
solver.options['NonConvex'] = 2  # Set NonConvex parameter to 2
results = solver.solve(model, tee=True)
#model.display()
#model.pprint()
#results.write()
print(value(model.obj))



'''
####### PLot #######

#Extract values of u0, u1, u2, P, and SOC
u0_values = [value(model.u0[i]) for i in model.IndexSet]
 
is_start_values = [value(model.is_start[i]) for i in model.IndexSet]
#SOC_percent = [val * 100 for val in SOC_values]


# Create x-axis values (assuming index set)
x_values = list(range(len(u0_values)))
PV__values = list(range(len(PV)))

#Declare Rows, columns and Figure size of subplots
fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))

# Plot u0, u1, u2, P, and SOC
axs[0].plot(x_values, u0_values, label='PV to Demand')
axs[0].plot(x_values, u1_values, label='Battery Charge')
axs[0].plot(x_values, u2_values, label='Battery Discharge')
axs[0].set_title('PV to Demand, Battery Charge and Discharge')


# Plot on the second subplot

axs[1].plot(x_values, SOC_percent)
axs[1].set_title('State of Charge in % ')

# Plot on the third subplot
axs[2].plot(PV__values, PV, label='Power Generation' )
axs[2].plot(PV__values, Consumption, label='Consumption' )
axs[2].set_title('Power Generation & Consumption')

# Add legend to the first subplot
axs[0].legend()


# Adjust layout and display the plot
plt.subplots_adjust(hspace=0.5)
plt.show()

'''