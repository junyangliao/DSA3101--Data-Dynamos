Cover page
Title, grp no. and stuff

Names and stuff
Table of Content (this will auto update)
7. Deployment
8. Technical Implementation
Repository Structure
Setup Instructions
Dependency Management
9. Analytical Findings

7. Deployment

Endpoints

Route 
HTTP Method
Description
/create-student
/create-module 
/create-staff
/create-job
POST
Create a new student/module/staff/job in the database along with their associated attributes
/upload-csv
POST
Execute the entity_relationship extraction function and create new nodes in the database along with their associated attributes
/delete-student
/delete-module
/delete-staff
/delete-job
POST
Delete an existing student/module/staff/job in the database along with their existing relationship
/student-distribution-faculty
GET
Run cypher query to get student distribution across faculties and then retrieve the output to be displayed in the frontend app
/student-distribution-major
GET
Run cypher query to get student distribution across majors and then retrieve the output to be displayed in the frontend app
/visualize-module
/visualize-student
/visualize-staff
POST
Retrieves all information about the particular module/student/staff node to be visualized in a comprehensive graph layout 
/visualizations/<path:filename>
GET
Serves the visualization to the frontend app
/process_query
POST
Processes the user input to be passed to the RAG model to output a cypher query which is then executed and the results are shown to the user in a user-friendly format
/api/job-recommendations
POST
Processes the user input and then outputs job recommendations in a table format 


Instructions for running the Docker container

Ensure Docker Desktop is up and running
Git clone the repository from the Github Page
Navigate to the project directory on Git Bash
Run ```docker-compose up –build``` in Git Bash
When you see the message that “... compiled successfully” on docker, you can now access the application at http://localhost:3000

Monitoring and Maintenance Considerations



8. Technical Implementation
Repository Structure
The repository is structured to separate the backend and frontend codebases and includes various data, configuration, and utility files for efficient project organization:
Root Files:
docker-compose.yml: Defines the multi-container Docker application setup.
README.md: Project documentation, including setup and usage instructions.
backend/:
data/: Contains sample datasets, including CSV and Excel files, organized into various categories:
coursera_reviews/: Reviews datasets for Coursera.
ONET grad job data/: Data files from the O*NET program, including skills, tools, and abilities for different job profiles.
Students_information/: Student and module information from NUS, with PDF and CSV files for reference.
src/: Holds backend source code files, organized as follows:
main_functions/: Key modules such as job_recommendations.py, modules.py, students.py, etc., handling core business logic.
DockerFile: Docker configuration for the backend.
requirements.txt: Lists Python dependencies.
entity_relationship_extraction/: A separate directory for scripts and configurations related to entity and relationship extraction, including:
entity_extraction/: Houses configuration files and Python scripts for entity extraction.
extracted_csv_output/: Stores output CSV files resulting from entity extraction processes.
frontend/:
public/: Static files for the frontend, including icons and the index.html template.
src/: Contains frontend source code, organized into two main areas:
dashboard-components/: React components for dashboard functionalities, such as StudentDistributionFaculty and StudentDistributionMajor.
pages/: Main application pages including Dashboard, Jobs, Login, Modules, Query, Staffs, and Students.
DockerFile: Docker configuration for the frontend.
package.json: Lists JavaScript dependencies.
Setup Instructions
Setup: Make sure Docker Desktop is running in the system. Follow instructions to set up the docker container stated in section 7 here. The application can then be viewed on the browser.
Local: http://localhost:3000 or on Your Network: http://<your network IPv4 address>:3000.
Dependency Management

Dependencies can be viewed in the repository folder, separated by backend or frontend.
backend/src/requirements.txt for the full backend dependencies, and frontend/package.json for the full frontend dependencies. 

Code Style Guide Adherence



9. Analytical Findings


11. 
12. 


10. Recommendations
Prioritized List of Recommendations

High Priority
Module Recommendation Enhancement
Current: Basic relevancy scoring using ‘all-MiniLM-L6-v2’ model
Improvement: Implement more sophisticated scoring that considers:
Module difficulty levels
Student’s past performance in related modules
Historical student success patterns
This provides more personalized and accurate module recommendations

Preclusion / Prerequisite Handling
Current: Basic prerequisite checking and preclusion filtering
Improvement: Add:
Multi-level prerequisite chain analysis
Alternative prerequisite path suggestions
Better visualization of module dependencies
This allows for clearer academic planning for students

Job-Skill Mapping
Current: Simple job title extraction and skill matching
Improvement: Enhance with:
Industry-specific skill weighting
Real-time job market skill requirements
More granular skill level assessment
This would give a better alignment with industry needs

Medium Priority
Data Sources Integration
Current: Relies mainly on Neo4j database and Wikidata
Improvement: Integrate:
Linkedin job market data
Industry certification requirements
Alumni career path data
This would provide more comprehensive career guidance
Performance Optimization
Current: Basic caching with @lru_cache
Improvement: Implement:
More efficient batch processing
Smarter caching strategies
Query optimization for large datasets
Faster response times and better scalability
Implementation Roadmap

Phase 1 (0-3 months): Core Functionality Enhancement
Module recommendation System Upgrade
Integrate module difficulty analysis, student performance correlation and develop historical success pattern analysis
Key Deliverable: Enhanced recommendation algorithm
Dependencies: Current relevancy scorer implementation
Prerequisite System Improvement
Build prerequisite chain analyzer, develop an alternative path suggestion system and create a visualization prototype
Key Deliverable: Advanced prerequisite management system
Dependencies: Existing Neo4j prerequisite data

Phase 2 (3-6 months): Industry Integration and Performance
Job-Skill Mapping Enhancement
Implement industry skill-weighting system, develop real-time job requirement integration and create a skill level assessment framework
Key Deliverable: Enhanced job-skill correlation
Dependencies: Phase 1 completion
Data Source Integration
Develop LinkedIn API integration, create a certification requirement database and build tracking for alumni career path
Key Deliverable: Multi-source data integration system
Dependencies: Job-skill mapping enhancement

Phase 3 (6-9 months): Optimization and Scaling
Performance Enhancement
Implement advanced caching system, optimize batch processing and enhance query performance
Key Deliverable: Optimized system architecture
Dependencies: Data Source Integration
System Scaling
Deploy load balancing, implement database sharing and optimize the memory usage
Key Deliverable: Scalable system infrastructure
Dependencies: Performance enhancement completion
Expected Impact

Technical Benefits
Improved recommendation accuracy
Better system performance
More robust data handling
Reduced error rates in module matching
Increased scalability to handle higher user load

User Benefits
Personalized module recommendations based on individual academic performance
Real-time visualization of prerequisite chains and alternative paths
Reduced module selection time (estimated 50% reduction)
Clear skill gap analysis for chosen career paths
Improved career planning with industry-aligned skill tracking
Better informed decision making with historical student success data
Seamless integration with academic requirements and career goals
