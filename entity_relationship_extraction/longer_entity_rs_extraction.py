import pandas as pd
import ast
import re
import spacy
import os
from fuzzywuzzy import fuzz, process


# Load your spaCy model
nlp = spacy.load("en_core_web_sm")


def extract_entities_rs(csv_file_path):

    # Predefined entity columns and their corresponding new column names for entity extraction
    target_cols = [
        "Student_Name",
        "Faculties",
        "Degree",
        "Major",
        "Module",
        "module_code",
        "moduleCode",
        "Skills",
        "Staff",
        "Modules_Completed",
        "department",
        "faculty",
        "prerequisite",
        "preclusion",
        "Employee Name",
        "Department",
        "Modules Taught",
        "Title",
        "Job Title",
        "Tech Skill",
        "university",
        "school",
        "degree",
        "description",
        "message",
    ]

    new_entity_cols = {
        "Student_Name": ("student_entities", "STUDENT"),
        "Degree": ("degree_entities", "DEGREE"),
        "degree": ("degree_entities", "DEGREE"),
        "Major": ("major_entities", "MAJOR"),
        "Module": ("module_entities", "MODULE"),
        "Modules_Completed": ("module_entities", "MODULE"),
        "module_code": ("module_entities", "MODULE"),
        "moduleCode": ("module_entities", "MODULE"),
        "Modules Taught": ("module_entities", "MODULE"),
        "prerequisite": ("prerequisite_entities", "PREREQUISITEGROUP"),
        "preclusion": ("preclusion_entities", "PRECLUSIONGROUP"),
        "Skills": ("skill_entities", "SKILL"),
        "Tech Skill": ("skill_entities", "SKILL"),
        "Staff": ("staff_entities", "STAFF"),
        "Employee Name": ("staff_entities", "STAFF"),
        "department": ("department_entities", "DEPARTMENT"),
        "Department": ("department_entities", "DEPARTMENT"),
        "Faculties": ("faculty_entities", "FACULTY"),
        "faculty": ("faculty_entities", "FACULTY"),
        "school": ("faculty_entities", "FACULTY"),
        "Title": ("job_entities", "JOB"),
        "Job Title": ("job_entities", "JOB"),
        "university": ("university_entities", "UNIVERSITY"),
    }

    # Relationship mappings
    relationship_mappings = {
        ("student_entities", "faculty_entities"): {
            "from_type": "STUDENT",
            "to_type": "FACULTY",
            "relationship_type": "STUDYING_UNDER",
        },
        ("student_entities", "major_entities"): {
            "from_type": "STUDENT",
            "to_type": "MAJOR",
            "relationship_type": "MAJOR_IN",
        },
        ("student_entities", "module_entities"): {
            "from_type": "STUDENT",
            "to_type": "MODULE",
            "relationship_type": "COMPLETED",
        },
        ("module_entities", "department_entities"): {
            "from_type": "MODULE",
            "to_type": "DEPARTMENT",
            "relationship_type": "BELONGS_TO",
        },
        ("module_entities", "prerequisite_entities", "MUST_HAVE_TAKEN_ONE_OF"): {
            "from_type": "MODULE",
            "to_type": "DEPARTMENT",
            "relationship_type": "MUST_HAVE_TAKEN_ONE_OF",
        },
        ("module_entities", "preclusion_entities", "MUST_NOT_HAVE_TAKEN_ONE_OF"): {
            "from_type": "MODULE",
            "to_type": "DEPARTMENT",
            "relationship_type": "MUST_NOT_HAVE_TAKEN_ONE_OF",
        },
        ("module_entities", "prerequisite_entities", "INCLUDED_AS_PREREQUISITE"): {
            "from_type": "MODULE",
            "to_type": "DEPARTMENT",
            "relationship_type": "INCLUDED_AS_PREREQUISITE",
        },
        ("module_entities", "preclusion_entities", "INCLUDED_AS_PRECLUSION"): {
            "from_type": "MODULE",
            "to_type": "DEPARTMENT",
            "relationship_type": "INCLUDED_AS_PRECLUSION",
        },
        ("module_entities", "semester_entities", "OFFERED_IN"): {
            "from_type": "MODULE",
            "to_type": "SEMESTER",
            "relationship_type": "OFFERED_IN",
        },
        ("module_entities", "staff_entities"): {
            "from_type": "MODULE",
            "to_type": "STAFF",
            "relationship_type": "TAUGHT_BY",
        },
        ("staff_entities", "department_entities"): {
            "from_type": "STAFF",
            "to_type": "DEPARTMENT",
            "relationship_type": "EMPLOYED_UNDER",
        },
        ("department_entities", "faculty_entities"): {
            "from_type": "DEPARTMENT",
            "to_type": "FACULTY",
            "relationship_type": "PART_OF",
        },
        ("job_entities", "faculty_entities"): {
            "from_type": "DEPARTMENT",
            "to_type": "FACULTY",
            "relationship_type": "PART_OF",
        },
        ("major_entities", "degree_entities"): {
            "from_type": "MAJOR",
            "to_type": "DEGREE",
            "relationship_type": "IS_UNDER",
        },
        ("job_entities", "skill_entities"): {
            "from_type": "JOB",
            "to_type": "SKILL",
            "relationship_type": "REQUIRES",
        },
        ("module_entities", "skill_entities"): {
            "from_type": "MODULE",
            "to_type": "SKILL",
            "relationship_type": "SKILL_TAUGHT",
        },
        ## ADDED
        ("university_entities", "degree_entities"): {
            "from_type": "UNIVERSTITY",
            "to_type": "DEGREE",
            "relationship_type": "OFFERS",
        },
    }

    # Extract entities function
    def extract_entities(csv_file_path):
        def parse_entity(x, entity_type):
            # Handle dictionary strings e.g.
            if isinstance(x, str) and x.startswith("{") and x.endswith("}"):
                return ast.literal_eval(x)  # Convert to dictionary
            # Handle already existing list
            elif isinstance(x, list):
                return [(str(item).strip(), entity_type) for item in flatten_list(x)]
            # Handle list strings
            elif isinstance(x, str) and x.startswith("[") and x.endswith("]"):
                try:
                    parsed_list = ast.literal_eval(
                        x
                    )  # Convert string representation of list to actual list
                    return [
                        (str(item).strip(), entity_type)
                        for item in flatten_list(parsed_list)
                    ]
                except (ValueError, SyntaxError):
                    return [(x.strip(), entity_type)]

            # Handle comma-separated strings
            # NEED TO REVISE THIS AS SOME VALUES HAVE COMMA IN ITSELF E.G. COLLEGE OF HUMANITIES, ARTS & SOCIAL SCIENCES
            elif pd.notna(x):
                return [(str(item).strip(), entity_type) for item in str(x).split(",")]

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

        df = pd.read_csv(csv_file_path)

        # Extract unique skills from the 'Skills' column in a separate CSV
        skills_csv_file_path = (
            "../../backend/data/07 - Jobs and relevant skillset (linkedin).csv"
        )
        df_skills = pd.read_csv(skills_csv_file_path)
        unique_skills = []

        if "Skills" in df_skills.columns:
            # Modified skills parsing
            skills_list = []
            for skill_text in df_skills["Skills"].dropna():
                # Handle the case where skills are comma-separated
                if isinstance(skill_text, str):
                    # Remove any square brackets if present
                    skill_text = skill_text.strip("[]")
                    # Split by comma and clean up each skill
                    skills = [
                        skill.strip().strip("\"'") for skill in skill_text.split(",")
                    ]
                    skills_list.extend(skills)

            # Clean up skills and remove duplicates
            unique_skills = list(
                set([re.sub(r"\s\(.*\)", "", skill) for skill in skills_list if skill])
            )

            # remove bracketed abbreviations from skills and the space before it
            unique_skills = [re.sub(r"\s\(.*\)", "", skill) for skill in unique_skills]

            # remove 'Microsoft ' substring before skills
            unique_skills = [
                re.sub(r"Microsoft\s", "", skill) for skill in unique_skills
            ]

        # Function to extract skills
        def extract_skills(text, threshold=80):
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
                potential_matches = process.extract(
                    text, unique_skills, limit=5, scorer=fuzz.ratio
                )
                skills = [
                    match[0] for match in potential_matches if match[1] >= threshold
                ]

            return list(set(skills))  # Remove duplicates

        # Function to extract staff names
        def extract_staff_names(text):
            if isinstance(text, str):
                doc = nlp(text)
                staff = []

                # Regex pattern to capture staff names with titles like 'Prof', 'Dr', 'Lecturer', 'Tutor'
                staff_pattern = re.compile(
                    r"\b(Prof|Professor|Dr|Lecturer|Tutor|Instructor)\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?",
                    re.IGNORECASE,
                )

                for ent in doc.ents:
                    match = staff_pattern.search(ent.text)
                    if match:
                        staff_name = match.group(0)

                        # Exclude unwanted phrases that are falsely detected as staff names
                        if not any(
                            word in staff_name.lower()
                            for word in [
                                "tutorial",
                                "attendance",
                                "assignment",
                                "participation",
                                "ratios",
                                "draft",
                                "profile",
                            ]
                        ):
                            staff.append(staff_name.strip())

                # Remove duplicates in staff
                return list(set(staff))

            return []

        # Extract semester entities
        semester_cols = ["semester_01", "semester_02", "semester_03", "semester_04"]
        if all(col in df.columns for col in semester_cols):
            df["semester_entities"] = df.apply(
                lambda row: [
                    (col, "SEMESTER") for col in semester_cols if row[col] == 1
                ],
                axis=1,
            )

        # Extract entities using appropriate functions
        for col in target_cols:
            if col in df.columns:
                # new_entity_col = new_entity_cols[col]
                new_entity_col, entity_type = new_entity_cols.get(
                    col, (col, "UNKNOWN")
                )  # Default entity type as 'UNKNOWN'

                # If the column is description or message, we apply special extraction
                if col in ["description"]:
                    df["skill_entities"] = df[col].apply(
                        lambda text: [
                            (skill, "SKILL") for skill in extract_skills(text)
                        ]
                    )

                elif col in ["description", "message"]:
                    df["skill_entities"] = df[col].apply(
                        lambda text: [
                            (skill, "SKILL") for skill in extract_skills(text)
                        ]
                    )
                    df["staff_entities"] = df[col].apply(
                        lambda text: [
                            (staff, "STAFF") for staff in extract_staff_names(text)
                        ]
                    )

                else:
                    # Create the new column with extracted entities, using the helper function
                    df[new_entity_col] = df[col].apply(
                        lambda x: parse_entity(x, entity_type)
                    )

        return df

    # Extract relationships function
    def create_dynamic_relationship(
        df, from_type, from_id_col, to_type, to_id_col, relationship_type, output_col
    ):
        # List to store formatted relationship dictionaries for each row
        relationship_column = []

        # Iterate through each row of the DataFrame
        for _, row in df.iterrows():
            # Extract the from_id and to_id values from the specified columns
            from_ids = (
                [entity[0] for entity in row[from_id_col] if isinstance(entity, tuple)]
                if isinstance(row[from_id_col], list)
                else [row[from_id_col]]
            )
            to_ids = (
                [entity[0] for entity in row[to_id_col] if isinstance(entity, tuple)]
                if isinstance(row[to_id_col], list)
                else [row[to_id_col]]
            )

            # Create a list of dictionaries
            relationship_dict = [
                {
                    "from_type": from_type,
                    "from_id": from_id,
                    "to_type": to_type,
                    "to_id": to_id,
                    "type": relationship_type,
                }
                for from_id in from_ids
                if pd.notna(from_id)
                for to_id in to_ids
                if pd.notna(to_id)  # Only include non-NaN to_id values
            ]

            # Append the relationship dictionary or an empty list if no valid to_id found
            relationship_column.append(relationship_dict if relationship_dict else [])

        # Add the relationships as a new column to the DataFrame
        df[output_col] = relationship_column

        # Return the updated DataFrame with the new relationships column
        return df

    # Step 1: Extract Entities
    df = extract_entities(csv_file_path)

    # Step 2: Extract Relationships based on predefined mappings
    for key, relationship_info in relationship_mappings.items():
        if len(key) == 3:
            from_col, to_col, rel_key = key
        elif len(key) == 2:
            from_col, to_col = key

        if from_col in df.columns and to_col in df.columns:
            output_col = f"{from_col}_to_{to_col}_{relationship_info['relationship_type'].lower()}_relationship"
            df = create_dynamic_relationship(
                df,
                relationship_info["from_type"],
                from_col,
                relationship_info["to_type"],
                to_col,
                relationship_info["relationship_type"],
                output_col,
            )

    # Combine all relationship columns into one
    relationship_columns = [col for col in df.columns if "_relationship" in col]
    if relationship_columns:
        df["relationships"] = df[relationship_columns].apply(
            lambda row: [
                item for sublist in row if isinstance(sublist, list) for item in sublist
            ],
            axis=1,
        )
        # Drop the individual relationship columns if no longer needed
        df = df.drop(columns=relationship_columns)
    else:
        # Set to a list of empty lists for each row
        df["relationships"] = [[] for _ in range(len(df))]

    # Step 3: Output final df
    return df


# Extract from existing cleaned datasets
# csv_file_path = '../../backend/data/00 - mock_student_data.csv'
csv_file_path = "../../backend/data/01 - mock_module_info.csv"
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

# Extract base name and append '_extracted'
base_name, ext = os.path.splitext(os.path.basename(csv_file_path))
new_file_name = f"{base_name}_extracted{ext}"

# Save the DataFrame to the new file
df.to_csv(new_file_name, index=False)

# Print a success message with the new file name
print(f"Data saved to: {new_file_name}")
print(df.head())
