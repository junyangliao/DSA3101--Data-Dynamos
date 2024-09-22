import numpy as np
import re
import pandas as pd
# clean mock_module_info_csv
import re
import pdfplumber
from sdv.tabular import GaussianCopula

# Example of searching for a specific pattern in the extracted text
pdf_path = r"Undergraduate in NUS composition.pdf"
 # Change to whatever you're searching for

# Extracting data from PDF
data = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        lines = text.split('\n')
        
        for line in lines:
            # Use regex to match the expected pattern
            match = re.match(r'^(.*?)(\d+)\s+(\d+)\s+(\d+)$', line)
            if match:
                department, male, female, total = match.groups()
                data.append({'Department': department.strip(), 'Male': int(male), 'Female': int(female), 'Total': int(total)})

# Convert to DataFrame
df = pd.DataFrame(data)

# Clean and process DataFrame as needed
print(df.head())

# Save to CSV
df.to_csv("NUS Student Composition.csv", index=False)
            #print(text)
file_path_modules = r"..\school_info\02 - mock_module_info.csv"
# Fetch the data from the csv folder
df2 = pd.read_csv(file_path_modules)
# response = requests.get(url)
data = df2[['moduleCode', 'faculty', 'attributes']]
# # wide_df = data.pivot(index='Student_ID', columns='UE', values='Marks')
Faculties= df2['faculty'].unique()
data['UE'] = data['attributes'].apply(lambda x: 1 if  isinstance(x, str) and 'su' in x else 0)

# Print the counts of 1s and 0s

# Ensure the request was successful
# if response.status_code == 200:
#     # Parse the JSON data
#     data = response.json()  
#     for module in data: # If the response is JSON, requests can directly parse it
#         module_codes.append(module['moduleCode'])
#         faculty.append(module['faculty'])
#         if module['attribute'] 
#      # Do something with the data, like printing or further processing
# else:
#     print(f"Failed to retrieve data: {response.status_code}")

# Read Student Performance excel 
file_path_studentperformance = r"..\Student_Performance_Data.xlsx"
df1 = pd.read_excel(file_path_studentperformance)
print(df1.head()) # Display the first few rows

# fit students with faculties 
unique_student_ids = df1['Student_ID'].unique()
# Save the updated DataFrame to a new CSV file
random_faculties = np.random.choice(Faculties, len(unique_student_ids))
print(len(unique_student_ids))
# student_facu_map = dict(zip(unique_student_ids, random_faculties))

# Map the department back to the original dataframe
#df1['Faculties'] = df1['Student_ID'].map(student_facu_map)

#df1.to_excel('Student_Performance_Data.xlsx', index=False)

#print("Module codes added and saved to 'Student_Performance_Data.xlsx'")


# URL of the JSON data
# url = "https://api.nusmods.com/v2/2023-2024/moduleInfo.json"  
