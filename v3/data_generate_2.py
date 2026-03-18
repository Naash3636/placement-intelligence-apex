import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker("en_IN")

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------

YEARS = list(range(2016, 2026))

STUDENTS_PER_BRANCH = 120

COMPANY_COUNT = 500
BRANCHES = [

"Computer Science & Engineering (CSE)",
"Computer Science & Engineering – Data Science",
"CSE – Cloud Technology & Information Security",
"CSE – Mobile Applications & Cloud Technology",
"CSE – Artificial Intelligence & Machine Learning",
"CSE – Artificial Intelligence & Data Engineering",
"CSE – Blockchain Technology",
"CSE – Cyber Physical Systems",
"CSE – AI-Driven DevOps",
"Computer Science & Business Systems",
"CSE – Internet of Things (IoT)",
"Computer Engineering – Software Engineering",
"CSE – Artificial Intelligence",

"Mechanical Engineering",
"Mechanical Engineering – Mechatronics",
"Mechanical Engineering – Robotics",

"Civil Engineering",
"Civil Engineering – Environmental Geotechnology",
"Civil Engineering – Construction Technology",

"Electronics & Communication Engineering (ECE)",
"ECE – VLSI Design & Technology",
"ECE – Robotics",

"Electrical & Electronics Engineering (EEE)",
"EEE – Electric Vehicles / Microgrid Technologies"

]

PROGRAM_CATEGORY = {

# -------- CORE CSE --------
"Computer Science & Engineering (CSE)" : "CSE_CORE",

# -------- DATA SCIENCE --------
"Computer Science & Engineering – Data Science" : "DATA_SCIENCE",

# -------- AI ML --------
"CSE – Artificial Intelligence & Machine Learning" : "AI_ML",
"CSE – Artificial Intelligence" : "AI_ML",

# -------- DATA ENGINEERING --------
"CSE – Artificial Intelligence & Data Engineering" : "DATA_ENGINEERING",

# -------- CLOUD --------
"CSE – Cloud Technology & Information Security" : "CLOUD",
"CSE – Mobile Applications & Cloud Technology" : "CLOUD",

# -------- BLOCKCHAIN --------
"CSE – Blockchain Technology" : "BLOCKCHAIN",

# -------- CYBER --------
"CSE – Cyber Physical Systems" : "CYBER",

# -------- DEVOPS --------
"CSE – AI-Driven DevOps" : "DEVOPS",

# -------- IOT --------
"CSE – Internet of Things (IoT)" : "IOT",

# -------- BUSINESS SYSTEMS --------
"Computer Science & Business Systems" : "BUSINESS",

# -------- SOFTWARE ENGINEERING --------
"Computer Engineering – Software Engineering" : "SOFTWARE",

# -------- OTHER BRANCHES --------
"Mechanical Engineering":"MECH",
"Mechanical Engineering – Mechatronics":"MECH",
"Mechanical Engineering – Robotics":"MECH",

"Civil Engineering":"CIVIL",
"Civil Engineering – Environmental Geotechnology":"CIVIL",
"Civil Engineering – Construction Technology":"CIVIL",

"Electronics & Communication Engineering (ECE)":"ECE",
"ECE – VLSI Design & Technology":"ECE",
"ECE – Robotics":"ECE",

"Electrical & Electronics Engineering (EEE)":"EEE",
"EEE – Electric Vehicles / Microgrid Technologies":"EEE"

}
PROGRAM_SUBJECTS = {

"CSE_CORE":[
["Maths1","Physics","Programming_C","Engineering_Graphics"],
["Maths2","Data_Structures","Digital_Logic","Electronics"],
["OOP","Computer_Organization","Discrete_Maths","DBMS"],
["Operating_Systems","Computer_Networks","Software_Engineering","Web_Tech"],
["Artificial_Intelligence","Machine_Learning","Cloud_Computing","Compiler"],
["Big_Data","Cyber_Security","DevOps","Data_Engineering"],
["Blockchain","IoT","Deep_Learning","Distributed_Systems"],
["Major_Project","Internship","Seminar","Capstone"]
],

"DATA_SCIENCE":[
["Maths1","Statistics","Python","Engineering_Graphics"],
["Probability","Data_Structures","Linear_Algebra","Python_Advanced"],
["Data_Mining","Data_Visualization","DBMS","Statistics_Advanced"],
["Machine_Learning","Big_Data","Cloud_Data","Data_Engineering"],
["Deep_Learning","NLP","Data_Warehousing","Spark"],
["AI","Reinforcement_Learning","MLOps","Data_Pipelines"],
["Advanced_AI","AI_Analytics","Research_Methods","Distributed_AI"],
["Major_Project","Internship","Seminar","Capstone"]
],

"AI_ML":[
["Maths1","Python","Engineering_Graphics","Physics"],
["Probability","Linear_Algebra","Data_Structures","Python_Advanced"],
["Machine_Learning","AI","DBMS","Computer_Vision"],
["Deep_Learning","NLP","Robotics","Cloud_AI"],
["Reinforcement_Learning","AI_Planning","MLOps","Edge_AI"],
["Advanced_DL","AI_Optimization","Explainable_AI","AutoML"],
["Research_AI","Advanced_AI_Systems","AI_Project","Seminar"],
["Major_Project","Internship","Seminar","Capstone"]
],

"CLOUD":[
["Maths1","Programming_C","Physics","Engineering_Graphics"],
["Data_Structures","Operating_Systems","Networks","Virtualization"],
["Cloud_Computing","Distributed_Systems","DBMS","Containers"],
["AWS","Azure","DevOps","Microservices"],
["Kubernetes","Serverless","Cloud_Security","Monitoring"],
["Cloud_AI","Edge_Computing","Big_Data","SRE"],
["Cloud_Architecture","Advanced_Cloud","Scalable_Systems","DevOps_Project"],
["Major_Project","Internship","Seminar","Capstone"]
],

"BLOCKCHAIN":[
["Maths1","Programming_C","Physics","Engineering_Graphics"],
["Data_Structures","Cryptography","Digital_Logic","DBMS"],
["Blockchain_Fundamentals","Distributed_Ledger","Networks","Security"],
["Smart_Contracts","Ethereum","Hyperledger","Web3"],
["Blockchain_Security","DeFi","Tokenomics","Cloud_Blockchain"],
["Advanced_Blockchain","Decentralized_AI","Crypto_Economics","Blockchain_Apps"],
["Blockchain_Research","Blockchain_Systems","Seminar","Project"],
["Major_Project","Internship","Seminar","Capstone"]
]

}

SKILLS = [
"Python","Java","C++","SQL","Machine Learning","Deep Learning",
"Cloud Computing","AWS","DevOps","Docker","Kubernetes",
"Cybersecurity","Blockchain","IoT","Data Science",
"React","NodeJS","TensorFlow","PyTorch","Linux"
]

COMPANY_BRANCH_MAP = {

"TCS":["CSE","ECE","EEE"],
"Infosys":["CSE","ECE"],
"Wipro":["CSE","ECE","Mechanical"],
"Amazon":["CSE"],
"Google":["CSE"],
"Microsoft":["CSE"],
"L&T":["Civil","Mechanical"],
"Tata Motors":["Mechanical"],
"Bosch":["Mechanical","ECE"]

}

# ---------------------------------------------------
# COMPANIES
# ---------------------------------------------------

companies = []

for i in range(COMPANY_COUNT):

    companies.append({
        "CompanyID": i+1,
        "Company": fake.company(),
        "Industry": random.choice(["IT","Finance","Consulting","Manufacturing"]),
        "Headquarters": fake.city(),
        "Employees": random.randint(100,100000),
        "Founded": random.randint(1980,2020),
        "Tier": random.choice(["Tier1","Tier2","Tier3"]),
        "Difficulty_Index": round(np.random.uniform(1,10),2)
    })

companies_df = pd.DataFrame(companies)
companies_df.to_csv("companies_master.csv",index=False)

company_list = companies_df["Company"].tolist()

# ---------------------------------------------------
# STUDENTS
# ---------------------------------------------------

students = []
sid = 1

for year in YEARS:

    for branch in BRANCHES:

        for i in range(STUDENTS_PER_BRANCH):

            skills = ",".join(random.sample(SKILLS,5))

            students.append({

                "StudentID": sid,
                "Name": fake.name(),
                "Gender": random.choice(["Male","Female"]),
                "DOB": fake.date_of_birth(minimum_age=18, maximum_age=23),
                "Email": fake.email(),
                "Phone": fake.phone_number(),
                "Branch": branch,
                "Year": year,
                "CGPA": round(np.random.uniform(6.0,9.8),2),

                "Skills": skills,

                "Hackathons": random.randint(0,5),
                "Papers": random.randint(0,3),
                "Conferences": random.randint(0,2),
                "Sports": random.randint(0,3),
                "Clubs": random.randint(0,4),
                "Internships": random.randint(0,2),

                "Resume_Score": random.randint(50,100),
                "GitHub_Score": random.randint(0,100),
                "LeetCode_Rating": random.randint(800,2200),

                "Placement_Probability": round(np.random.uniform(0.3,0.95),2),

                "Father": fake.name(),
                "Mother": fake.name(),
                "Address": fake.address()

            })

            sid += 1

students_df = pd.DataFrame(students)
students_df.to_csv("placement_master_10yr_full_dataset.csv",index=False)

academic_rows = []

for _, row in students_df.iterrows():

    record = {

        "StudentID": row["StudentID"],
        "Year": row["Year"]

    }

    # SGPA Attendance Backlogs
    for i in range(1,9):

        record[f"SGPA_Sem{i}"] = round(np.random.uniform(6.5,9.5),2)
        record[f"Attendance_Sem{i}"] = random.randint(65,95)
        record[f"Backlogs_Sem{i}"] = random.randint(0,2)

    # Detect program category
    branch = row["Branch"]

    eligible_companies = []

    for company in company_list:

        if company in COMPANY_BRANCH_MAP:

            if any(b in branch for b in COMPANY_BRANCH_MAP[company]):
                eligible_companies.append(company)

        else:
            eligible_companies.append(company)

    company = random.choice(eligible_companies)
    program = PROGRAM_CATEGORY.get(branch,"CSE_CORE")

    # Generate subjects dynamically
    subjects_structure = PROGRAM_SUBJECTS.get(program, PROGRAM_SUBJECTS["CSE_CORE"])

    for sem in range(1,9):

        subjects = subjects_structure[sem-1]

        for subject in subjects:

            record[f"{subject}_Sem{sem}"] = random.randint(50,100)

    academic_rows.append(record)

academic_df = pd.DataFrame(academic_rows)
academic_df.to_csv("academic_history_10years.csv", index=False)

# ---------------------------------------------------
# PLACEMENT HISTORY
# ---------------------------------------------------

placements = []

for _,row in students_df.iterrows():

    attempts = random.randint(3,8)

    for a in range(attempts):

        company = random.choice(company_list)

        status = random.choices(
            ["Placed","Rejected"],
            weights=[0.35,0.65]
        )[0]

        tier = companies_df.loc[companies_df["Company"]==company,"Tier"].values[0]

        if tier == "Tier1":
            package = np.random.uniform(18,40)

        elif tier == "Tier2":
            package = np.random.uniform(8,18)

        else:
            package = np.random.uniform(3,8)

        job_type = random.choices(

        ["Full Time","Internship","Internship + PPO"],

        weights=[0.55,0.30,0.15]

        )[0]
        if job_type == "Internship + PPO":

            status = random.choices(

            ["Placed","Rejected"],

            weights=[0.60,0.40]

            )[0]

        else:

            status = random.choices(

            ["Placed","Rejected"],

            weights=[0.35,0.65]

            )[0]

        placements.append({

            "StudentID": row["StudentID"],
            "Year": row["Year"],
            "Company": company,
            "Package": round(package,2),
            "Status": status,
            "InterviewMode": random.choice(["Online","Offline"]),
            
            "Interview_Rounds": random.randint(2,5),
            "Placed_Date": fake.date_between(start_date='-10y', end_date='today')

        })

placement_df = pd.DataFrame(placements)
placement_df.to_csv("placement_history_10years.csv",index=False)

# ---------------------------------------------------
# MIS DRIVES
# ---------------------------------------------------

drives = []

for year in YEARS:

    visiting = random.sample(company_list, random.randint(100,180))

    for c in visiting:

        drives.append({

            "Year": year,
            "Company": c,
            "Drive_ID": fake.uuid4(),
            "Drive_Mode": random.choice(["Online","Offline"]),
            "Eligible_Branches": ",".join(random.sample(BRANCHES,5)),
            "Students_Eligible": random.randint(200,2000),
            "Students_Applied": random.randint(100,1500),
            "Students_Shortlisted": random.randint(50,500),
            "Students_Selected": random.randint(5,200)

        })

drives_df = pd.DataFrame(drives)
drives_df.to_csv("mis_drives_10years.csv",index=False)

print("ENTERPRISE DATASET CREATED SUCCESSFULLY")