import numpy as np
import re
import pandas as pd
# clean mock_module_info_csv
import re
import pdfplumber
import random

# Your DataFrame
file_path = r'Student_Performance_Faculties.xlsx'
df = pd.read_excel(file_path)

# Define possible majors for each faculty
faculty_to_majors = {
    'Yong Loo Lin Sch of Medicine': ['Medicine', 'Nursing'],
    'College of Design and Engineering': ['Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering','Computer Engineering','Landscape Architecture','Architecture','Industrial Design'],
    'NUS Business School': ['Business Administration'],
    'Arts and Social Science': ['Psychology', 'Sociology', 'History','Geography','Social Work','Economics'],
    'Science': ['Physics', 'Chemistry', 'Life Science','Pharmacy','Pharmaceutical Science', 'Data Science and Analytics','Philosophy, Politics &Economics','Data Science and Economics','Environmental Studies','Food Science and Technology'],
    'Computing': ['Computer Science', 'Information Systems', 'Business Analytics'],
    'YST Conservatory of Music': ['Music'],
    'Dentistry': ['Dentistry'],
    'Law': ['Law']
}


# Function to randomly assign majors and potentially a second major from another faculty
def assign_majors(faculty):
    # Assign the primary major based on the faculty
    majors = faculty_to_majors.get(faculty, [])
    if not majors:
        return (None, None)  # In case the faculty is not listed
    
    primary_major = random.choice(majors)
    
    # Only assign a second major if the faculty is not Medicine, Dentistry, or Law
    second_major = None
    if faculty not in ['Yong Loo Lin Sch of Medicine', 'Dentistry', 'Law']:
        # 20% chance of getting a second major
        if random.random() < 0.2:
            # Choose from a different faculty
            eligible_faculties = [fac for fac in faculty_to_majors if fac != faculty and fac not in ['Dentistry', 'Law', 'Yong Loo Lin Sch of Medicine']]
            second_faculty = random.choice(eligible_faculties)
            second_major = random.choice(faculty_to_majors[second_faculty])
    
    return primary_major, second_major

# Apply the major assignment to the DataFrame
df['Major'] = df['Faculties'].apply(lambda x: assign_majors(x)[0])
df['Second Major'] = df['Faculties'].apply(lambda x: assign_majors(x)[1])

# Save the updated DataFrame back to CSV
df.to_csv('updated_file_with_majors.csv', index=False)

# Print the first few rows of the updated DataFrame to check the output
print(df.head())




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
file_path_modules = r"..\school_info\02 - mock_module_info.csv"
file_path_studentperformance = r"..\Student_Performance_Data.xlsx"
df1 = pd.read_excel(file_path_studentperformance)
print(df1.head()) # Display the first few rows
df2 = pd.read_csv(file_path_modules)
Faculties= ['Yong Loo Lin Sch of Medicine','College of Design and Engineering',
 'NUS Business School','Arts and Social Science','Science','Computing','YST Conservatory of Music', 
 'Dentistry','Law']
# fit students with faculties 
print(Faculties)
unique_student_ids = df1['Student_ID'].unique()
# Save the updated DataFrame to a new CSV file
random_faculties = np.random.choice(Faculties, len(unique_student_ids))

student_facu_map = dict(zip(unique_student_ids, random_faculties))

# Map the department back to the original dataframe
df1['Faculties'] = df1['Student_ID'].map(student_facu_map)

df1.to_excel('Student_Performance_Faculties.xlsx', index=False)