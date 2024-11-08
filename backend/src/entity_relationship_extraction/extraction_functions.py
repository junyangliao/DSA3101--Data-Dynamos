import pandas as pd
import ast 
import re
import spacy
from spacy.matcher import PhraseMatcher
import os 

# Load your spaCy model
nlp = spacy.load('en_core_web_sm')

## Main Functions
def extract_entities_rs(data,df_skills): 

    # Predefined entity columns and their corresponding new column names for entity extraction 
    target_cols = ['Matric_Number', 'Faculties', 'Degree', 'Major', 'Module', 'module_code', 'moduleCode', 'Skills', 'Staff', 
                   'Modules_Completed', 'department', 'faculty', 'Employee Name', 
                   'Department', 'Modules Taught', 'Title', 'Job Title', 'Tech Skills', 'university',
                   'school', 'degree', 'description', 'message']

    new_entity_cols = {
        'Matric_Number': ('student_entities', 'Student'),
        'Degree': ('degree_entities', 'Degree'),
        'degree': ('degree_entities', 'Degree'),
        'Major': ('major_entities', 'Major'),
        'Module': ('module_entities', 'Module'),
        'Modules_Completed': ('module_entities', 'Module'),
        'module_code': ('module_entities', 'Module'),
        'moduleCode': ('module_entities', 'Module'),
        'Modules Taught': ('module_entities', 'Module'),
        'Skills': ('skill_entities', 'Skill'),
        'Tech Skills': ('skill_entities', 'Skill'),
        'Staff': ('staff_entities', 'Staff'),
        'Employee Name': ('staff_entities', 'Staff'),
        'department': ('department_entities', 'Department'), 
        'Department': ('department_entities', 'Department'), 
        'Faculties': ('faculty_entities', 'Faculty'),
        'faculty': ('faculty_entities', 'Faculty'),
        'school': ('faculty_entities', 'Faculty'),
        'Title': ('job_entities', 'Job'),
        'Job Title': ('job_entities', 'Job'),
        'university': ('university_entities', 'University'),
    }

    # Relationship mappings
    relationship_mappings = {
        ('student_entities', 'faculty_entities'): {"from_type": "Student", "to_type": "Faculty", "relationship_type": "STUDYING_UNDER"},
        ('student_entities', 'major_entities'): {"from_type": "Student", "to_type": "Major", "relationship_type": "MAJOR_IN"},
        ('student_entities', 'module_entities'): {"from_type": "Student", "to_type": "Module", "relationship_type": "COMPLETED"},
        ('module_entities', 'department_entities'): {"from_type": "Module", "to_type": "Department", "relationship_type": "BELONGS_TO"},

        # take note of prerequisiteGroup and preclusionGroup 
        ('module_entities', 'staff_entities'): {"from_type": "Module", "to_type": "Staff", "relationship_type": "TAUGHT_BY"},
        ('staff_entities', 'department_entities'): {"from_type": "Staff", "to_type": "Department", "relationship_type": "EMPLOYED_UNDER"},
        ('department_entities', 'faculty_entities'): {"from_type": "Department", "to_type": "Faculty", "relationship_type": "PART_OF"},
        ('job_entities', 'faculty_entities'): {"from_type": "Department", "to_type": "Faculty", "relationship_type": "PART_OF"},
        ('major_entities', 'degree_entities'): {"from_type": "Major", "to_type": "Degree", "relationship_type": "IS_UNDER"},
        ('job_entities', 'skill_entities'): {"from_type": "Job", "to_type": "Skill", "relationship_type": "REQUIRES"},
        ('module_entities', 'skill_entities'): {"from_type": "Module", "to_type": "Skill", "relationship_type": "SKILL_TAUGHT"},
        ## ADDED
        ('university_entities', 'degree_entities'): {"from_type": "University", "to_type": "Degree", "relationship_type": "OFFERS"},

    }

    # Step 1: Extract Entities 
    df = extract_entities(data,target_cols,new_entity_cols,df_skills)

    # Step 2: Extract Relationships based on predefined mappings 
    for key, relationship_info in relationship_mappings.items():
        if len(key) == 3:
            from_col, to_col, rel_key = key
        elif len(key) == 2:
            from_col, to_col = key
            rel_key = ''  # Set rel_key as an empty string or any default value as needed

        if from_col in df.columns and to_col in df.columns:
            output_col = f"{from_col}_to_{to_col}_{relationship_info['relationship_type'].lower()}_relationship"
            df = create_dynamic_relationship(
                df,
                relationship_info['from_type'],
                from_col,
                relationship_info['to_type'],
                to_col,
                relationship_info['relationship_type'],
                output_col
            )

    # Combine all relationship columns into one
    relationship_columns = [col for col in df.columns if '_relationship' in col]
    df['relationships'] = df[relationship_columns].apply(lambda row: [item for sublist in row if isinstance(sublist, list) for item in sublist], axis=1)

    # Drop the individual relationship columns if no longer needed
    df = df.drop(columns=relationship_columns)

    # Step 3: Output final df
    return df

# Extract entities function 
def extract_entities(df,target_cols,new_entity_cols,df_skills):

    # Extract unique skills from the 'Skills' column in a separate CSV
    unique_skills = []
    
    if 'Skills' in df_skills.columns:
        # Modified skills parsing
        skills_list = []
        for skill_text in df_skills["Skills"].dropna():
            # Handle the case where skills are comma-separated
            if isinstance(skill_text, str):
                # Remove square brackets if present
                skill_text = skill_text.strip('[]')
                # Split by comma, clean up each skill, and add as a list
                skills = [skill.strip().strip('"\'') for skill in skill_text.split(',')]

                # Remove bracketed abbreviations from each skill and clean "Microsoft" prefix
                cleaned_skills = [
                    re.sub(r'\s\(.*\)', '', re.sub(r'Microsoft\s', '', skill)) for skill in skills if skill
                ]

                # Append the cleaned list of skills for this row
                skills_list.append(cleaned_skills)
        
        # Clean up skills and remove duplicates
        unique_skills = list(set([re.sub(r'\s\(.*\)', '', skill[0]) for skill in skills_list if skill]))

        # remove bracketed abbreviations from skills and the space before it
        unique_skills = [re.sub(r'\s\(.*\)', '', skill[0]) for skill in unique_skills]

        # remove 'Microsoft ' substring before skills
        unique_skills = [re.sub(r'Microsoft\s', '', skill[0]) for skill in unique_skills]
    
    # Initialize the matcher with the nlp vocabulary
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp(skill) for skill in unique_skills]  # Assuming unique_skills is defined globally
    matcher.add("Skills", patterns)

    # Extract entities using appropriate functions 
    for col in target_cols:
        if col in df.columns:
            # new_entity_col = new_entity_cols[col]     
            new_entity_col, entity_type = new_entity_cols.get(col, (col, 'Unknown'))  # Default entity type as 'UNKNOWN'  

            # If the column is description or message, we apply special extraction
            if col in ['description']:
                df['skill_entities'] = df[col].apply(lambda text: [(skill, 'Skill') for skill in extract_skills_using_phrasematcher(text, matcher)])

            elif col in ['description', 'message']:
                df['skill_entities'] = df[col].apply(lambda text: [(skill, 'Skill') for skill in extract_skills_using_phrasematcher(text, matcher)])
                df['staff_entities'] = df[col].apply(lambda text: [(staff, 'Staff') for staff in extract_staff_names(text)])

            else:
                # Create the new column with extracted entities, using the helper function
                df[new_entity_col] = df[col].apply(lambda x: parse_entity(x, entity_type))

    
    return df

# Helper Functions
def parse_entity(x, entity_type):
    # Handle dictionary strings e.g. 
    if isinstance(x, str) and x.startswith('{') and x.endswith('}'):
        return ast.literal_eval(x)  # Convert to dictionary
    # Handle already existing list 
    elif isinstance(x, list):
        return [(str(item).strip(), entity_type) for item in flatten_list(x)]
    # Handle list strings
    elif isinstance(x, str) and x.startswith('[') and x.endswith(']'):
        try:
            parsed_list = ast.literal_eval(x)  # Convert string representation of list to actual list
            return [(str(item).strip(), entity_type) for item in flatten_list(parsed_list)]
        except (ValueError, SyntaxError):
            # return [x.strip()] 
            return [(x.strip(), entity_type)]
        
    # Handle comma-separated strings
    # NEED TO REVISE THIS AS SOME VALUES HAVE COMMA IN ITSELF E.G. COLLEGE OF HUMANITIES, ARTS & SOCIAL SCIENCES 
    elif pd.notna(x):
        return [(x.strip(), entity_type)]
    
    # Return an empty list for NaN or other invalid entries
    return []

# Helper function to flatten nested lists
def flatten_list(nested_list):
    flat_list = []
    for i in nested_list:
        if isinstance(i, list):
            flat_list.extend(flatten_list(i))
        else:
            flat_list.append(i)
    return flat_list

# Function to extract skills using PhraseMatcher
def extract_skills_using_phrasematcher(text, matcher):
    if not isinstance(text, str):
        return []  # Return empty list if not a valid string
    doc = nlp(text)
    matches = matcher(doc)
    skills = [doc[start:end].text for match_id, start, end in matches]
    return list(set(skills))  # Remove duplicates

# Function to extract staff names
def extract_staff_names(text):
    if isinstance(text, str):
        doc = nlp(text)
        staff = []

        # Regex pattern to capture staff names with titles like 'Prof', 'Dr', 'Lecturer', 'Tutor'
        staff_pattern = re.compile(r'\b(Prof|Professor|Dr|Lecturer|Tutor|Instructor)\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', re.IGNORECASE)
        
        for ent in doc.ents:
            match = staff_pattern.search(ent.text)
            if match:
                staff_name = match.group(0)

                # Exclude unwanted phrases that are falsely detected as staff names
                if not any(word in staff_name.lower() for word in ['tutorial', 'attendance', 'assignment', 'participation', 'ratios', 'draft', 'profile']):
                    staff.append(staff_name.strip())

        # Remove duplicates in staff
        return list(set(staff))  
    
    return [] 

# Extract relationships function 
def create_dynamic_relationship(df, from_type, from_id_col, to_type, to_id_col, relationship_type, output_col):
    # List to store formatted relationship dictionaries for each row
    relationship_column = []

    # Iterate through each row of the DataFrame
    for _, row in df.iterrows():
        # Extract the from_id and to_id values from the specified columns
        from_ids = [entity[0] for entity in row[from_id_col] if isinstance(entity, tuple)] if isinstance(row[from_id_col], list) else [row[from_id_col]]
        to_ids = [entity[0] for entity in row[to_id_col] if isinstance(entity, tuple)] if isinstance(row[to_id_col], list) else [row[to_id_col]]

        # Create a list of dictionaries
        relationship_dict = [
            {
                "from_type": from_type,
                "from_id": from_id,
                "to_type": to_type,
                "to_id": to_id,
                "type": relationship_type
            }
            for from_id in from_ids if pd.notna(from_id)
            for to_id in to_ids if pd.notna(to_id)  # Only include non-NaN to_id values
        ]

        # Append the relationship dictionary or an empty list if no valid to_id found
        relationship_column.append(relationship_dict if relationship_dict else [])

    # Add the relationships as a new column to the DataFrame
    df[output_col] = relationship_column
    
    # Return the updated DataFrame with the new relationships column
    return df