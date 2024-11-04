# DSA3101- Data Dynamos
👋 Hello! This is the repo for our group's application stack. 

### Make sure to check that you are working on the dev branch

## Prerequisites
The entire application stack runs on docker, so make sure you have Docker installed.

## Getting Started
1. git clone the repository
2. Open Docker Desktop
3. Navigate to project directory
4. ```docker-compose up --build ```

Once all containers are running the frontend app should now be accessible on ```http://localhost:3000/ ```.

To find out more about how to operate the application, you can check out our user guide. *insert url here*

## Log-in Credentials
- Username: data dynamos
- Password: DSA3101isdabest

## Project Folder Structure
```plaintext
.
├── README.md
├── /backend
│    ├── /data
│    │    ├──
│    │
│    │
|    ├── /src
│    │    ├── /main_functions
│    │    │    ├── job_skills.py
│    │    │    ├── modules.py
│    │    │    ├── students.py
│    │    │    ├── staffs.py
│    │    │    └── job_recommendations.py
│    │    ├── DockerFile
│    │    ├── app.py
│    │    ├── ontology_config.json
│    │    ├── requirements.txt
│    │    └── utils.py
│    └── test.py
├── /entity_extraction
├── /frontend
│    ├── /src
│    │    ├── /pages
│    │    │    ├── Dashboard.jsx
│    │    │    ├── Jobs.jsx
│    │    │    ├── Login.jsx
│    │    │    ├── Modules.jsx
│    │    │    ├── Students.jsx
│    │    │    ├── Staffs.jsx
│    │    │    └── Query.jsx
│    │    ├── App.css
│    │    ├── App.js
│    │    ├── App.test.js
│    │    ├── Home.js
│    │    ├── Modal.js
│    │    ├── /dashboard-componenets
│    │    │    ├── background.jpg 
│    │    │    ├── StudentDistributionFaculty.jsx
│    │    │    └── StudentDistributionMajor.jsx
│    │    ├── index.css
│    │    └── index.js
│    ├── public
│    └── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .dockerignore
├── package.json
└── package-lock.json

```
