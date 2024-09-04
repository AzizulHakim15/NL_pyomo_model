#Azizul Hakim
#Working group: Optimization and Optimal Control
#Project: HyBit

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   

# Define file paths
wm_file_path = "C:\\Users\\azizul\\Desktop\\hyBit\\Project\\Model\\Data\\Output\\wm_1m.csv"

# Load data from CSV files

wm_data = pd.read_csv(wm_file_path, header=None)
Gen_wm = wm_data[1].to_list()
Device =  [ x for x in Gen_wm]  
plt.plot(Device)
plt.title('Device used in Mixed Integer Non-Linear Programming model')
plt.xlabel('Time')
plt.ylabel('Power (W)')
plt.show()