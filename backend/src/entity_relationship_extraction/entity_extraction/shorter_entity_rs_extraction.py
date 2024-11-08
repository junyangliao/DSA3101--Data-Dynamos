




# Extract from existing cleaned datasets 
# csv_file_path = '../../backend/data/00 - mock_student_data.csv'
csv_file_path = '../../backend/data/01 - mock_module_info.csv'
# csv_file_path = '../../backend/data/02 - mock_department_list.csv'
# csv_file_path = '../../backend/data/03 - mock_staff_info.csv'
# csv_file_path = '../../backend/data/04 - mock_module_reviews.csv'
# csv_file_path = '../../backend/data/05 - mock_venue_info.csv'
# csv_file_path = '../../backend/data/06 - nus_undergraduate_programmes.csv'
# csv_file_path = '../../backend/data/07 - Jobs abd relevant skillset (linkedin).csv'
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