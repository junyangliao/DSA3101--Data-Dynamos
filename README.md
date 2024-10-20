# DSA3101- Data Dynamos
Project for DSA3101

## Make sure to check that you are working on the dev branch
### Username: datadynamos Password: DSA3101isdabest

### Prerequisites
The entire application stack runs on docker, so make sure you have Docker installed.

### Getting Started
1. git clone the repository
2. Open Docker Desktop
3. Navigate to project directory
4. ```plaintext docker-compose up --build ```

Once all containers are running the frontend app should now be accessible on ```plaintext http://localhost:3000/ ```. 

### Log-in Credentials
Username: data dynamos
Password: DSA3101isdabest

### Project Folder Structure
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
│    │    │    └── staffs.py
│    │    ├── DockerFile
│    │    ├── app.py
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
│    │    ├── App.css
│    │    ├── App.js
│    │    ├── App.test.js
│    │    ├── Home.js
│    │    ├── Modal.js
│    │    ├── /dashboard-componenets
│    │    │    ├── StudentDistributionFaculty.jsx
│    │    │    ├── StudentDistributionMajor.jsx
│    │    │    ├── StaffDistribution.jsx
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
