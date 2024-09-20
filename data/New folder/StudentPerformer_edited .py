
import requests
import json
import pandas as pd

import numpy as np
# URL of the JSON data
url = "https://api.nusmods.com/v2/2023-2024/moduleList.json"  # Replace with your actual URL

# Fetch the data from the URL
response = requests.get(url)

# Ensure the request was successful
if response.status_code == 200:
    # Parse the JSON data
    data = response.json()  # If the response is JSON, requests can directly parse it
    module_codes = [module['moduleCode'] for module in data]
     # Do something with the data, like printing or further processing
else:
    print(f"Failed to retrieve data: {response.status_code}")
# Load the two CSV files into separate DataFrames 
# Load the Excel file into a DataFrame
file_path = r"..\Student_Performance_Data.xlsx"


df1 = pd.read_excel(file_path)
print(df1.head()) # Display the first few rows




# 

# Ensure that you have the right number of module codes available
# Assign random module codes to each student in the DataFrame
df1['module_codes'] = np.random.choice(module_codes, len(df1))

# Save the updated DataFrame to a new CSV file
df1.to_excel('Student_Performance_Data.xlsx', index=False)

print("Module codes added and saved to 'Student_Performance_Data.xlsx'")
print(df1.head())

# Merge the DataFrames based on a common column
# For example, merge on the 'id' column
#merged_df = pd.merge(df1, df2, on='id', how='inner')
