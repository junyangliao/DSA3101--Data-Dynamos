import pandas as pd
import ast 
import re
import spacy
import os 
import yaml
from fuzzywuzzy import fuzz, process
from multiprocessing import Pool, cpu_count

# Load your spaCy model
nlp = spacy.load('en_core_web_sm')

def load_config():
    # Load configuration from YAML file.
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)
    
# Helper functions moved outside
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
            return [(x.strip(), entity_type)]
        
    # Handle comma-separated strings
    # NEED TO REVISE THIS AS SOME VALUES HAVE COMMA IN ITSELF E.G. COLLEGE OF HUMANITIES, ARTS & SOCIAL SCIENCES 
    elif pd.notna(x):
        return [(str(item).strip(), entity_type) for item in str(x).split(',')]
    
    # Return an empty list for NaN or other invalid entries
    return []

def flatten_list(nested_list):
    flat_list = []
    for i in nested_list:
        if isinstance(i, list):
            flat_list.extend(flatten_list(i))
        else:
            flat_list.append(i)
    return flat_list

# Function to extract skills 
def extract_skills(text, unique_skills, threshold=80):
    if not isinstance(text, str):
        return []
    
    skills = []
    # extract skill entities
    for skill in unique_skills:
        # create a regex pattern with word boundaries around the skills 
        pattern = r"\b" + re.escape(skill) + r"\b"

        # search for the skills in the text (case-insensitive)
        if re.search(pattern, text, re.IGNORECASE):
            skills.append(skill)

    # Fuzzy match for entity resolution if no exact matches found
    if not skills:
        potential_matches = process.extract(text, unique_skills, limit=5, scorer=fuzz.ratio)
        skills = [match[0] for match in potential_matches if match[1] >= threshold]
    
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

# Process chunk function moved outside
def process_chunk(args):
    chunk, unique_skills, col, new_entity_col, entity_type = args
    
    if col in ['description']:
        chunk['skill_entities'] = chunk[col].apply(
            lambda text: [(skill, 'Skill') for skill in extract_skills(text, unique_skills)])
    elif col in ['description', 'message']:
        chunk['skill_entities'] = chunk[col].apply(
            lambda text: [(skill, 'Skill') for skill in extract_skills(text, unique_skills)])
        chunk['staff_entities'] = chunk[col].apply(
            lambda text: [(staff, 'Staff') for staff in extract_staff_names(text)])
    else:
        chunk[new_entity_col] = chunk[col].apply(lambda x: parse_entity(x, entity_type))
    
    return chunk

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
    
def extract_entities_rs(csv_file_path): 
    config = load_config()
    target_cols = config['target_cols']
    entity_mappings = config['entity_mappings']
    relationship_mappings = config['relationship_mappings']

    # Convert entity_mappings to the format expected by the rest of the code
    new_entity_cols = {
        col: (mapping['new_col'], mapping['type'])
        for col, mapping in entity_mappings.items()
    }
    # Read data
    df = pd.read_csv(csv_file_path)
    
    # Extract unique skills
    skills_csv_file_path = '../../backend/data/07 - Jobs and relevant skillset (linkedin).csv'
    df_skills = pd.read_csv(skills_csv_file_path)
    unique_skills = []
    
    if 'Skills' in df_skills.columns:
        # Modified skills parsing
        skills_list = []
        for skill_text in df_skills["Skills"].dropna():
            # Handle the case where skills are comma-separated
            if isinstance(skill_text, str):
                # Remove any square brackets if present
                skill_text = skill_text.strip('[]')
                # Split by comma and clean up each skill
                skills = [skill.strip().strip('"\'') for skill in skill_text.split(',')]
                skills_list.extend(skills)
        
        # Clean up skills and remove duplicates
        unique_skills = list(set([re.sub(r'\s\(.*\)', '', skill) for skill in skills_list if skill]))

        # remove bracketed abbreviations from skills and the space before it
        unique_skills = [re.sub(r'\s\(.*\)', '', skill) for skill in unique_skills]

        # remove 'Microsoft ' substring before skills
        unique_skills = [re.sub(r'Microsoft\s', '', skill) for skill in unique_skills]

    # Parallel processing for entity extraction
    num_cores = cpu_count()
    chunk_size = max(1, len(df) // (num_cores * 2))
    
    for col in target_cols:
        if col in df.columns:
            new_entity_col, entity_type = new_entity_cols.get(col, (col, 'UNKNOWN'))
            chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
            
            # Prepare data for parallel processing with unique_skills
            chunk_data = [(chunk, unique_skills, col, new_entity_col, entity_type) for chunk in chunks]
            
            # Process chunks in parallel
            with Pool(processes=num_cores) as pool:
                processed_chunks = pool.map(process_chunk, chunk_data)
            
            # Combine processed chunks
            df = pd.concat(processed_chunks, axis=0)

    # Extract relationships based on predefined mappings
    for rel_key, rel_info in relationship_mappings.items():
        from_col = rel_info['from_col']
        to_col = rel_info['to_col']
        
        if from_col in df.columns and to_col in df.columns:
            output_col = f"{from_col}_to_{to_col}_{rel_info['relationship_type'].lower()}_relationship"
            df = create_dynamic_relationship(
                df,
                rel_info['from_type'],
                from_col,
                rel_info['to_type'],
                to_col,
                rel_info['relationship_type'],
                output_col
            )

    # Combine all relationship columns into one
    relationship_columns = [col for col in df.columns if '_relationship' in col]
    if relationship_columns:
        df['relationships'] = df[relationship_columns].apply(lambda row: [item for sublist in row if isinstance(sublist, list) for item in sublist], axis=1)
        df = df.drop(columns=relationship_columns)
    else: 
        df['relationships'] = [[] for _ in range(len(df))]  

    return df

# Main execution
if __name__ == '__main__':
    # Extract from existing cleaned datasets 
    # csv_file_path = '../../backend/data/00 - mock_student_data.csv'
    csv_file_path = '../../backend/data/01 - mock_module_info.csv'
    # csv_file_path = '../../backend/data/02 - mock_department_list.csv'
    # csv_file_path = '../../backend/data/03 - mock_staff_info.csv'
    # csv_file_path = '../../backend/data/04 - mock_module_reviews.csv'
    # csv_file_path = '../../backend/data/05 - mock_venue_info.csv'
    # csv_file_path = '../../backend/data/06 - nus_undergraduate_programmes.csv'
    # csv_file_path = '../../backend/data/07 - Jobs and relevant skillset (linkedin).csv'
    # csv_file_path = '../../backend/data/08 - jobs_and_tech (ONET).csv'
    # csv_file_path = '../../backend/data/09 - jobs_and_skills (ONET).csv'
    # csv_file_path = '../../backend/data/10 - Graduate Employment Survey.csv'
    
    # Extract Entities and Relationships
    df = extract_entities_rs(csv_file_path)
    # Define the path for the 'extracted_csv_output' folder, which is beside the .py file's folder
    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../entity_extraction/extracted_csv_output')
    # Save results
    base_name, ext = os.path.splitext(os.path.basename(csv_file_path))
    new_file_name = f"{base_name}_extracted{ext}"
    new_file_path = os.path.join(output_dir, new_file_name)
    df.to_csv(new_file_path, index=False)
    
    # Print a success message with the new file name
    print(f"Data saved to: {new_file_name}")
    print(df.head())
