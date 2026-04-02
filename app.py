import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import jwt
import datetime
import re
from difflib import get_close_matches




# ==========================
# SESSION INITIALIZATION
# ==========================

if "role" not in st.session_state:
    st.session_state["role"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

st.set_page_config(
    page_title="Placement Intelligence Apex",
    layout="wide",
    page_icon="  "
)

# ================================
# CUSTOM CSS FOR LOGIN PAGE 
# ================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(135deg,#0f172a,#020617);
    color:white;
}

/* Glass card style */
.glass-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}

/* Glass header */
.glass-header {
    background: rgba(139,92,246,0.35);
    backdrop-filter: blur(15px);
    border-radius: 14px;
    padding: 20px;
    text-align:center;
    font-size:28px;
    font-weight:bold;
    color:white;
}

/* KPI glass cards */
.metric-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 15px;
    border:1px solid rgba(255,255,255,0.12);
}

/* Input glass */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.08);
    color:white;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)
# ================================
# SESSION INIT
# ================================

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

# ================================
# SECRET KEY
# ================================
SECRET_KEY = "PLACEMENT_INTELLIGENCE_APEX_ENTERPRISE_SECURITY_2026"


# ================================
# OFFICIAL USERS
# ================================

OFFICIAL_USERS = {
    "placement_officer": {"password": "official123", "role": "Official"},
    "coordinator": {"password": "official123", "role": "Official"},
    "naash": {"password": "naash123", "role": "Official"},
    "vellai_pandhu": {"password": "kusu123", "role": "Official"}
}

# ================================
# COMPANY ADMINS
# ================================

COMPANY_ADMINS = {
    "tcs_admin": {"password": "tcs123", "company": "TCS", "role": "Admin"},
    "infosys_admin": {"password": "infosys123", "company": "Infosys", "role": "Admin"},
}

# ================================
# JWT TOKEN
# ================================

def create_token(payload):

    payload["exp"] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8)

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


def verify_token(token):

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded

    except:
        return None


# ================================
# LOGIN PAGE
# ================================

def login_page():

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.title("   Placement Intelligence Apex")
        st.caption("AI Powered Placement Analytics Portal")

        login_type = st.selectbox(
            "Login As",
            [
                "Official (Placement Cell)",
                "Student",
                "Company Admin"
            ]
        )

        username = st.text_input("Username / StudentID")

        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            # =============================
            # OFFICIAL LOGIN
            # =============================

            if login_type == "Official (Placement Cell)":

                if username in OFFICIAL_USERS and password == OFFICIAL_USERS[username]["password"]:

                    token = create_token({
                        "role": "Official",
                        "username": username
                    })

                    st.session_state["auth_token"] = token
                    st.session_state["role"] = "Official"
                    st.session_state["username"] = username

                    st.success("Official Login Successful")
                    st.rerun()

                else:
                    st.error("Invalid Official Credentials")

            # =============================
            # STUDENT LOGIN
            # =============================

            elif login_type == "Student":

                if password == "student":

                    token = create_token({
                        "role": "Student",
                        "student_id": username
                    })

                    st.session_state["auth_token"] = token
                    st.session_state["role"] = "Student"
                    st.session_state["student_id"] = username

                    st.success("Student Login Successful")
                    st.rerun()

                else:
                    st.error("Invalid Student Password")

            # =============================
            # COMPANY ADMIN LOGIN
            # =============================

            elif login_type == "Company Admin":

                if username in COMPANY_ADMINS and password == COMPANY_ADMINS[username]["password"]:

                    token = create_token({
                        "role": "Admin",
                        "username": username,
                        "company": COMPANY_ADMINS[username]["company"]
                    })

                    st.session_state["auth_token"] = token
                    st.session_state["role"] = "Admin"
                    st.session_state["company"] = COMPANY_ADMINS[username]["company"]
                    st.session_state["username"] = username

                    st.success("Company Admin Login Successful")
                    st.rerun()

                else:
                    st.error("Invalid Company Admin Credentials")

        st.markdown('</div>', unsafe_allow_html=True)


# ================================
# AUTH CHECK
# ================================

if st.session_state["auth_token"] is None:
    login_page()
    st.stop()

user = verify_token(st.session_state["auth_token"])

if user is None:
    st.error("Session expired. Please login again.")
    st.session_state["auth_token"] = None
    st.rerun()
role = user["role"]

st.write("Logged Role:", role)

# GET ROLE FROM TOKEN
role = user["role"]
username = user.get("username", "")
student_id = user.get("student_id", "")
company = user.get("company", "")

@st.cache_data(show_spinner=False)
def load_and_prepare_data():

    # ================= LOAD FILES =================
    df_master = pd.read_csv("placement_master_10yr_full_dataset.csv", low_memory=False)
    academics = pd.read_csv("academic_history_10years.csv", low_memory=False)
    placements = pd.read_csv("placement_history_10years.csv", low_memory=False)
    companies = pd.read_csv("companies_master.csv", low_memory=False)
    drives = pd.read_csv("mis_drives_10years.csv", low_memory=False)

    # ================= CLEAN COLUMNS =================
    df_master.columns = df_master.columns.str.strip()
    academics.columns = academics.columns.str.strip()
    placements.columns = placements.columns.str.strip()

    # ================= MERGE =================
    df = df_master.merge(placements, on="StudentID", how="left")
    df = df.merge(academics, on="StudentID", how="left")

    # ================= AUTO GENERATE DATA =================
    for i in range(1, 9):

        if f"SGPA_Sem{i}" not in df.columns:
            df[f"SGPA_Sem{i}"] = np.random.uniform(6.5, 9.5, len(df)).round(2)

        if f"Backlogs_Sem{i}" not in df.columns:
            df[f"Backlogs_Sem{i}"] = np.random.randint(0, 2, len(df))

        if f"Attendance_Sem{i}" not in df.columns:
            df[f"Attendance_Sem{i}"] = np.random.uniform(70, 95, len(df)).round(1)

    subjects = ["Maths", "DSA", "OS", "DBMS", "AI"]

    for s in subjects:
        for sem in range(1, 9):
            col = f"{s}_Sem{sem}"
            if col not in df.columns:
                df[col] = np.random.randint(55, 100, len(df))

    return df, companies, drives
df, companies, drives = load_and_prepare_data()


# ==============================
# COLUMN STABILIZER
# ==============================

required_cols = {
    "StudentID": "Unknown",
    "Name": "Unknown",
    "Branch": "Unknown",
    "Company": "Not Applied",
    "Status": "Not Placed",
    "Package": 0,
    "Year": 2026,
    "Skills": "Python,SQL"
}

for col, default in required_cols.items():
    if col not in df.columns:
        df[col] = default

# Convert date column if present
if "Placed_Date" in df.columns:
    df["Placed_Date"] = pd.to_datetime(df["Placed_Date"], errors="coerce")

# ==========================================================
# UNIVERSAL GRAPH GENERATOR FOR ALL DATASET ATTRIBUTES
# ==========================================================

import plotly.express as px
import re

def universal_graph_ai(question, df):

    q = question.lower()

    columns = df.columns.tolist()

    detected = []

    # Detect columns mentioned in question
    for col in columns:

        col_name = col.lower()

        if col_name in q:
            detected.append(col)

    # Detect graph type
    graph_type = "scatter"

    if "bar" in q:
        graph_type = "bar"

    elif "line" in q or "trend" in q:
        graph_type = "line"

    elif "hist" in q or "distribution" in q:
        graph_type = "hist"

    elif "box" in q:
        graph_type = "box"

    # Detect year filter
    year_match = re.search(r"\b20\d{2}\b", q)

    data = df.copy()

    if year_match and "Year" in df.columns:

        year = int(year_match.group())

        data = data[data["Year"] == year]

    # =========================
    # ONE COLUMN GRAPH
    # =========================

    if len(detected) == 1:

        col = detected[0]

        if graph_type == "hist":

            fig = px.histogram(data, x=col,
                               title=f"{col} Distribution")

        elif graph_type == "box":

            fig = px.box(data, y=col,
                         title=f"{col} Spread")

        else:

            counts = data[col].value_counts().reset_index()

            fig = px.bar(counts,
                         x="index",
                         y=col,
                         title=f"{col} Frequency")

        return fig

    # =========================
    # TWO COLUMN GRAPH
    # =========================

    if len(detected) >= 2:

        x = detected[0]
        y = detected[1]

        if graph_type == "scatter":

            fig = px.scatter(data,
                             x=x,
                             y=y,
                             title=f"{x} vs {y}")

        elif graph_type == "line":

            fig = px.line(data,
                          x=x,
                          y=y,
                          title=f"{x} vs {y} Trend")

        elif graph_type == "bar":

            grouped = data.groupby(x)[y].mean().reset_index()

            fig = px.bar(grouped,
                         x=x,
                         y=y,
                         title=f"{x} vs {y}")

        elif graph_type == "box":

            fig = px.box(data,
                         x=x,
                         y=y,
                         title=f"{x} vs {y}")

        else:

            fig = px.scatter(data, x=x, y=y)

        return fig

    return None


# ==========================================================
# AI NARRATIVE INTERPRETATION ENGINE
# ==========================================================

def generate_narrative_report(df):

    placed = df[df["Status"] == "Placed"].copy()

    report = {}

    # ---------------- Hiring Performance ----------------
    company_hires = placed["Company"].value_counts()
    top_company = company_hires.idxmax() if not company_hires.empty else "N/A"
    top_count = company_hires.max() if not company_hires.empty else 0
    top_count = company_hires.max()

    report["Hiring Performance"] = (
        f"{top_company} recruited the highest number of students "
        f"with {top_count} successful hires, indicating strong "
        f"recruitment activity from this company."
    )

    # ---------------- Package Analysis ----------------
    avg_package = placed.groupby("Company")["Package"].mean()

    highest_company = avg_package.idxmax()
    highest_package = avg_package.max()

    median_salary = placed["Package"].median()

    report["Package Analysis"] = (
        f"{highest_company} offers the highest average package "
        f"at   {round(highest_package,2)} LPA. "
        f"The median package across companies is about "
        f"  {round(median_salary,2)} LPA."
    )

    # ---------------- Branch Analysis ----------------
    branch_hires = placed["Branch"].value_counts()
    top_branch = branch_hires.idxmax()

    report["Branch Performance"] = (
        f"The {top_branch} branch shows the strongest placement "
        f"performance with the highest number of successful placements."
    )

    # ---------------- Placement Rate ----------------
    total_students = df["StudentID"].nunique()
    placed_students = placed["StudentID"].nunique()

    placement_rate = (placed_students / total_students) * 100

    report["Placement Rate"] = (
        f"The university placement rate is {round(placement_rate,2)}%, "
        f"with {placed_students} students placed out of {total_students}."
    )

    # ---------------- Company Difficulty ----------------
    applicants = df.groupby("Company")["StudentID"].count()
    selected = placed.groupby("Company")["StudentID"].count()

    difficulty = (applicants / selected).replace(np.inf,0)
    hardest_company = difficulty.idxmax()

    report["Company Difficulty"] = (
        f"{hardest_company} appears to be the most competitive company "
        f"based on the applicant-to-selection ratio."
    )

    # ---------------- Skill Demand ----------------
    skills = df["Skills"].str.split(",", expand=True).stack().value_counts()
    top_skill = skills.idxmax()

    report["Skill Demand"] = (
        f"The most demanded skill among placed students is {top_skill}."
    )

    # ---------------- Placement Trend ----------------
    yearly = placed.groupby("Year")["StudentID"].nunique()
    best_year = yearly.idxmax()

    report["Placement Trend"] = (
        f"The strongest placement performance occurred in {best_year}."
    )

    return report


# ==========================================================
# RULE-BASED AI COPILOT
# ==========================================================

def placement_ai_copilot(question, df):

    placed = df[df["Status"]=="Placed"]
    question = question.lower()

    if "highest package" in question or "top paying" in question:

        avg_package = placed.groupby("Company")["Package"].mean()
        company = avg_package.idxmax()
        package = avg_package.max()

        return f"The highest paying company is {company} offering about   {round(package,2)} LPA."

    elif "most students" in question or "most hiring" in question:

        hires = placed["Company"].value_counts()
        company = hires.idxmax()
        count = hires.max()

        return f"{company} hired the highest number of students ({count})."

    elif "placement rate" in question:

        total = df["StudentID"].nunique()
        placed_students = placed["StudentID"].nunique()

        rate = (placed_students/total)*100

        return f"The placement rate is {round(rate,2)}%."

    elif "best branch" in question:

        branch = placed["Branch"].value_counts().idxmax()

        return f"The branch with the highest placements is {branch}."

    elif "skills" in question:

        skills = df["Skills"].str.split(",",expand=True).stack().value_counts()
        top_skill = skills.idxmax()

        return f"The most demanded skill is {top_skill}."

    else:
        return "Try asking about companies, packages, branches, skills, or placement rate."


# ============================================================
# COLUMN INTELLIGENCE ENGINE
# ============================================================

def detect_columns(question, df):

    q = question.lower()
    columns = list(df.columns)

    detected = []

    for col in columns:

        name = col.lower().replace("_"," ")

        if name in q:
            detected.append(col)

        else:

            words = name.split()

            for w in words:

                if w in q:
                    detected.append(col)

    # fuzzy matching
    for word in q.split():

        match = get_close_matches(word, columns, n=1, cutoff=0.8)

        if match:
            detected.append(match[0])

    return list(set(detected))


# ============================================================
# YEAR DETECTION
# ============================================================

def detect_year(question):

    year_match = re.search(r"\b20\d{2}\b", question)

    if year_match:
        return int(year_match.group())

    return None


# ============================================================
# UNIVERSAL DATA ANALYSIS ENGINE
# ============================================================

def dataset_ai_engine(question, df):

    q = question.lower()

    data = df.copy()

    detected_columns = detect_columns(q, df)

    year = detect_year(q)

    if year and "Year" in df.columns:

        data = data[data["Year"] == year]


    # ========================================================
    # MOST / HIGHEST
    # ========================================================

    if "most" in q or "highest" in q or "maximum" in q:

        if "company" in q:

            placed = data[data["Status"] == "Placed"]

            counts = placed["Company"].value_counts()

            company = counts.idxmax()

            count = counts.max()

            return f"{company} hired the most students ({count})."


        if "package" in q:

            row = data.loc[data["Package"].idxmax()]

            return f"""
Highest Package Analysis

Student : {row['Name']}

Company : {row['Company']}

Package :   {row['Package']} LPA
"""


        if "cgpa" in q:

            row = data.loc[data["CGPA"].idxmax()]

            return f"{row['Name']} has the highest CGPA of {row['CGPA']}."


        if "branch" in q:

            placed = data[data["Status"] == "Placed"]

            branch = placed["Branch"].value_counts().idxmax()

            return f"{branch} branch has the highest placements."


    # ========================================================
    # TOP N ANALYSIS
    # ========================================================

    if "top" in q:

        number = re.search(r"\d+", q)

        n = 5

        if number:
            n = int(number.group())

        if "package" in q:

            top = data.sort_values("Package", ascending=False).head(n)

            result = f"Top {n} Highest Packages\n\n"

            for _, r in top.iterrows():

                result += f"{r['Name']} - {r['Company']} -   {r['Package']} LPA\n"

            return result


        if "cgpa" in q:

            top = data.sort_values("CGPA", ascending=False).head(n)

            result = f"Top {n} Students by CGPA\n\n"

            for _, r in top.iterrows():

                result += f"{r['Name']} - {r['CGPA']}\n"

            return result


    # ========================================================
    # COUNT QUERIES
    # ========================================================

    if "how many" in q or "count" in q:

        if "students" in q:

            return f"Total Students : {data['StudentID'].nunique()}"


        if "placed" in q:

            placed = data[data["Status"] == "Placed"]

            return f"Placed Students : {placed['StudentID'].nunique()}"


        if "company" in q:

            return f"Total Companies : {data['Company'].nunique()}"


    # ========================================================
    # AVERAGE ANALYSIS
    # ========================================================

    if "average" in q or "mean" in q:

        if "package" in q:

            avg = data["Package"].mean()

            return f"Average Package :   {round(avg,2)} LPA"


        if "cgpa" in q:

            avg = data["CGPA"].mean()

            return f"Average CGPA : {round(avg,2)}"


    # ========================================================
    # GENERAL DATA EXPLORATION
    # ========================================================

    if detected_columns:

        col = detected_columns[0]

        if data[col].dtype in ["int64","float64"]:

            return f"""
Statistics for {col}

Mean : {round(data[col].mean(),2)}

Max : {data[col].max()}

Min : {data[col].min()}
"""

        else:

            return f"""
Top values for {col}

{data[col].value_counts().head(5)}
"""


    return "I analyzed the dataset but could not fully interpret the question."

# ==========================================================
# PLACEMENT SCORE
# ==========================================================

def placement_score(profile):

    sgpa = np.mean([profile[f"SGPA_Sem{i}"] for i in range(1, 9)])
    backlogs = sum([profile[f"Backlogs_Sem{i}"] for i in range(1, 9)])
    skills = len(str(profile.get("Skills", "")).split(","))
    attendance = np.mean([profile[f"Attendance_Sem{i}"] for i in range(1, 9)])

    score = (
        sgpa * 10 * 0.4 +
        (skills * 5) * 0.2 +
        attendance * 0.2 -
        backlogs * 5
    )

    return max(0, min(100, round(score, 2)))


# ==========================================================
# AI SUMMARY
# ==========================================================

def ai_summary(profile):

    sgpa = np.mean([profile[f"SGPA_Sem{i}"] for i in range(1, 9)])
    backlogs = sum([profile[f"Backlogs_Sem{i}"] for i in range(1, 9)])
    skills = len(str(profile.get("Skills", "")).split(","))

    if sgpa > 8 and backlogs == 0:
        return "Excellent academic performance. Strong placement potential."

    elif sgpa > 7:
        return "Good academic record. Improve skills to increase placement chances."

    elif backlogs > 2:
        return "Backlogs are affecting placement chances. Focus on clearing them."

    else:
        return "Moderate performance. Needs improvement in academics and skills."


# ==========================================================
# ML MODEL TRAINING
# ==========================================================

from sklearn.ensemble import RandomForestClassifier

@st.cache_resource
def train_model_cached():
    df_model, _, _ = load_and_prepare_data()

    model_df = df_model.copy()

    model_df["Placed_Flag"] = (model_df["Status"] == "Placed").astype(int)

    model_df["Avg_SGPA"] = model_df[[f"SGPA_Sem{i}" for i in range(1,9)]].mean(axis=1)
    model_df["Total_Backlogs"] = model_df[[f"Backlogs_Sem{i}" for i in range(1,9)]].sum(axis=1)
    model_df["Avg_Attendance"] = model_df[[f"Attendance_Sem{i}" for i in range(1,9)]].mean(axis=1)
    model_df["Skill_Count"] = model_df["Skills"].apply(lambda x: len(str(x).split(",")))

    X = model_df[["Avg_SGPA","Total_Backlogs","Avg_Attendance","Skill_Count"]]
    y = model_df["Placed_Flag"]

    model = RandomForestClassifier(n_estimators=30, max_depth=8)
    model.fit(X, y)

    return model

# Load model once
model = train_model_cached()


# ==========================================================
# STUDENT RANKING
# ==========================================================

def rank_students(df, model):

    temp = df.copy()

    temp["Avg_SGPA"] = temp[[f"SGPA_Sem{i}" for i in range(1, 9)]].mean(axis=1)
    temp["Total_Backlogs"] = temp[[f"Backlogs_Sem{i}" for i in range(1, 9)]].sum(axis=1)
    temp["Avg_Attendance"] = temp[[f"Attendance_Sem{i}" for i in range(1, 9)]].mean(axis=1)
    temp["Skill_Count"] = temp["Skills"].apply(lambda x: len(str(x).split(",")))

    X = temp[["Avg_SGPA", "Total_Backlogs", "Avg_Attendance", "Skill_Count"]]

    temp["Score"] = model.predict_proba(X)[:, 1]
    temp["Rank"] = temp["Score"].rank(ascending=False)

    return temp


# ==========================================================
# GRAPH INTERPRETER
# ==========================================================

def interpret_graph(title, data):

    if title == "SGPA":
        avg = data["SGPA"].mean()
        trend = "improving" if data["SGPA"].iloc[-1] > data["SGPA"].iloc[0] else "declining"
        return f"The student's academic performance is {trend} with an average SGPA of {round(avg, 2)}."

    elif title == "Backlogs":
        total = data["Backlogs"].sum()
        return f"The student has {total} total backlogs across semesters."

    elif title == "Attendance":
        avg = data["Attendance"].mean()
        status = "good" if avg > 75 else "poor"
        return f"Average attendance is {round(avg, 1)}%, indicating {status} consistency."

    elif title == "Subjects":
        top = data.sort_values("Marks", ascending=False).iloc[0]["Subject"]
        return f"The strongest subject appears to be {top}."

    elif title == "Placement":
        offers = len(data[data["Status"] == "Placed"])
        attempts = len(data)
        rate = round((offers / attempts) * 100, 2) if attempts > 0 else 0
        return f"The student has a placement success rate of {rate}%."

    return "No interpretation available."
# =======================
# HEADER DESIGN
# =======================
# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}
header {
    visibility: hidden;
}
.block-container {
    padding-top: 1rem;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
}
.purple-header {
    background: linear-gradient(90deg, #6a11cb, #8e44ad);
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-size: 22px;
    font-weight: bold;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="purple-header">Interactive Student Performance Tracking App</div>', unsafe_allow_html=True)


role = st.session_state["role"]
if role == "Official":
    tabs = st.tabs([
        "Home",
        "University Dashboard",
        "Student Dashboard",
        "Admin Company Analysis",
        "New Company Drive"
    ])

elif role == "Admin":
    tabs = st.tabs([
        "Home",
        "Admin Company Analysis",
        "New Company Drive"
    ])

elif role == "Student":
    tabs = st.tabs([
        "Home",
        "Student Dashboard"
        
    ])

with tabs[0]:

    import datetime

    username = st.session_state.get("username", "User")

    # ---------- HEADER ----------
    col1, col2 = st.columns([8,1])

    with col1:
        st.markdown("""
        <div class="glass-header">
           Placement Intelligence Apex
        </div>
        """, unsafe_allow_html=True)
        st.write(f"Welcome **{username}**")

    with col2:
        if st.button("Logout"):
            st.session_state["auth_token"] = None
            st.session_state["role"] = None
            st.session_state["username"] = None
            st.rerun()

    now = datetime.datetime.now()
    st.caption(now.strftime("%A | %d %B %Y | %H:%M:%S"))

    st.markdown("---")

    # ================= KPI CARDS =================

    total_students = df["StudentID"].nunique()
    placed_students = df[df["Status"]=="Placed"]["StudentID"].nunique()
    companies = df["Company"].nunique()
    avg_package = round(df[df["Status"]=="Placed"]["Package"].mean(),2)
    placement_rate = round((placed_students/total_students)*100,2)

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric(" Students", total_students)
    c2.metric(" Placements", placed_students)
    c3.metric("   Companies", companies)
    c4.metric("   Avg Package", f"{avg_package} LPA")
    c5.metric("   Placement Rate", f"{placement_rate}%")

    st.markdown("---")

   
    # ================= ai =================

    st.subheader("   AI Dataset Analyst")

    question = st.text_input("Ask anything about the dataset")

    if question:

        answer = dataset_ai_engine(question, df)

        st.success(answer)

    st.subheader("   AI Graph Generator")

    graph_query = st.text_input("Ask for any graph")

    if graph_query:

        fig = universal_graph_ai(graph_query, df)

        if fig:

            st.plotly_chart(fig, use_container_width=True)

        else:

            st.warning("AI could not detect attributes in the question.")

    st.markdown("---")
    

# =======================
# UNIVERSITY DASHBOARD
# =======================
with tabs[1]:
    st.markdown("##    Placement Overview Dashboard")

    # ================= YEAR DISTRIBUTION =================

    st.subheader("   Year-wise Student Distribution")

    year_count = df.groupby("Year")["StudentID"].nunique().reset_index()
    year_count.columns = ["Year", "Student Count"]

    fig1 = px.bar(
        year_count,
        x="Year",
        y="Student Count",
        text="Student Count",
        color="Student Count",
        template="plotly_dark"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- YEAR-WISE PLACEMENT RATE ----------------
    st.markdown("###    Year-wise Placement Rate")

    year_placement = df.groupby("Year").apply(
        lambda x: round((x[x["Status"]=="Placed"]["StudentID"].nunique()
                         / x["StudentID"].nunique())*100,2)
    ).reset_index()

    year_placement.columns = ["Year", "Placement Rate (%)"]

    fig2 = px.line(
        year_placement,
        x="Year",
        y="Placement Rate (%)",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- YEAR-WISE AVERAGE PACKAGE ----------------
    st.markdown("###    Year-wise Average Package")

    year_package = df[df["Status"]=="Placed"].groupby("Year")["Package"].mean().reset_index()
    year_package["Package"] = round(year_package["Package"],2)

    fig3 = px.area(
        year_package,
        x="Year",
        y="Package"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------- STATUS DISTRIBUTION ----------------
    st.markdown("###    Overall Placement Distribution")

    status_count = df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Count"]

    fig4 = px.pie(
        status_count,
        names="Status",
        values="Count",
        hole=0.5
    )
    st.plotly_chart(fig4, use_container_width=True)


    #-----------------Year-wise Placement Performance
    st.subheader("Year-wise Placement Performance")
    yearly = df[df["Status"]=="Placed"].groupby("Year")["StudentID"].nunique().reset_index()
    fig1 = px.bar(yearly, x="Year", y="StudentID", template="plotly_dark",
                  title="Year-wise Unique Placements")
    st.plotly_chart(fig1, use_container_width=True)


    # ================= BRANCH PERFORMANCE =================

    st.subheader("   Branch Placement Contribution")

    branch_perf = df[df["Status"]=="Placed"].groupby("Branch")["StudentID"].nunique().reset_index()

    fig5 = px.pie(
        branch_perf,
        names="Branch",
        values="StudentID",
        hole=0.4,
        template="plotly_dark"
    )

    st.plotly_chart(fig5, use_container_width=True)

    # ================= TOP COMPANIES =================

    st.subheader("   Top Hiring Companies")

    top_companies = df[df["Status"]=="Placed"]["Company"].value_counts().head(10).reset_index()
    top_companies.columns = ["Company","Placements"]

    fig6 = px.bar(
        top_companies,
        x="Company",
        y="Placements",
        template="plotly_dark"
    )

    st.plotly_chart(fig6, use_container_width=True)


# =======================
# STUDENT DASHBOARD
# =======================
with tabs[2]:
    st.markdown("## Student Profile Portal")

    # Ensure "Name" column exists for the search filter
    if "Name" not in df.columns:
        name_cols = [c for c in df.columns if "name" in c.lower()]
        if name_cols:
            df.rename(columns={name_cols[0]: "Name"}, inplace=True)

    search = st.text_input("Search Student (ID or Name)", key="student_search_box")

    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df["StudentID"].astype(str).str.contains(search, na=False) |
            filtered_df["Name"].str.contains(search, case=False, na=False)
        ]

    student_list = filtered_df["StudentID"].unique().tolist()

    selected_student = st.selectbox(
        "Select Student ID",
        ["Select Student"] + student_list,
        key="student_select_main"
    )

    if selected_student != "Select Student":

        st.session_state["selected_student"] = selected_student

    if "selected_student" in st.session_state:

        stu_data = df[df["StudentID"].astype(str) == str(st.session_state["selected_student"])]

        if not stu_data.empty:

            profile = stu_data.iloc[0]

            st.success(f"Loaded Student: {profile['Name']}")

        else:
            st.warning("No data found")

    if selected_student == "Select Student":
        st.info("Please select a student")

    else:
        stu_data = df[df["StudentID"].astype(str) == str(selected_student)]

        if stu_data.empty:
            st.warning("No data available")

        else:
            profile = stu_data.iloc[0]

            
            # ==========================================================
            # CLUBBED STUDENT SECTIONS
            # ==========================================================

            student_tabs = st.tabs([
                "Profile",
                "Academics",
                "Skills & Activities",
                "Placements"
            ])

            # ==========================================================
            # PROFILE TAB
            # ==========================================================

            with student_tabs[0]:

                # =========================
                # 🎨 CLEAN CSS
                # =========================
                st.markdown("""
                <style>
                .title {font-size:28px;font-weight:bold;color:#a78bfa;}
                .sub {color:#cbd5f5;margin-bottom:10px;}
                .card {
                    background: rgba(255,255,255,0.05);
                    padding:15px;
                    border-radius:12px;
                    margin-bottom:12px;
                }
                .chip {
                    display:inline-block;
                    padding:6px 12px;
                    margin:4px;
                    background:#6366f1;
                    border-radius:20px;
                    color:white;
                    font-size:12px;
                }
                </style>
                """, unsafe_allow_html=True)

                # =========================
                # 👤 HEADER
                # =========================
                c1,c2 = st.columns([1,4])
                with c1:
                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
                with c2:
                    st.markdown(f'<div class="title">{profile["Name"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="sub">{profile["Branch"]} | ID: {profile["StudentID"]}</div>', unsafe_allow_html=True)

                st.markdown("---")

                # =========================
                # 📊 KPI ROW
                # =========================
                cgpa = round(np.mean([profile[f"SGPA_Sem{i}"] for i in range(1,9)]),2)
                backlogs = sum([profile[f"Backlogs_Sem{i}"] for i in range(1,9)])
                skills = profile["Skills"].split(",")
                placed = "Placed" if profile["Status"]=="Placed" else "Not Placed"

                k1,k2,k3,k4 = st.columns(4)
                k1.metric("CGPA", cgpa)
                k2.metric("Placement", placed)
                k3.metric("Backlogs", backlogs)
                k4.metric("Skills", len(skills))

                # Prepare student input
                input_data = pd.DataFrame({
                    "Avg_SGPA": [np.mean([profile[f"SGPA_Sem{i}"] for i in range(1,9)])],
                    "Total_Backlogs": [sum([profile[f"Backlogs_Sem{i}"] for i in range(1,9)])],
                    "Avg_Attendance": [np.mean([profile[f"Attendance_Sem{i}"] for i in range(1,9)])],
                    "Skill_Count": [len(profile["Skills"].split(","))]
                })

                

                prob = model.predict_proba(input_data)[0][1] * 100
                prob = round(prob,2)

                st.markdown("### 🎯 Placement Prediction")

                col1, col2 = st.columns([3,1])

                with col1:
                    st.progress(prob/100)

                with col2:
                    st.metric("Probability", f"{prob}%")

                # Color feedback
                if prob > 75:
                    st.success("High chance of placement 🚀")

                elif prob > 50:
                    st.warning("Moderate chance ⚠ Improve skills")

                else:
                    st.error("Low placement probability ❗")

                # =========================
                # 📚 ACADEMIC SNAPSHOT
                # =========================
                st.markdown("###  Academic Snapshot")

                sgpas = [profile[f"SGPA_Sem{i}"] for i in range(1,9)]

                best_sem = sgpas.index(max(sgpas)) + 1
                weak_sem = sgpas.index(min(sgpas)) + 1

                a1,a2,a3 = st.columns(3)
                a1.metric("Avg SGPA", round(np.mean(sgpas),2))
                a2.metric("Best Semester", f"Sem {best_sem}")
                a3.metric("Weak Semester", f"Sem {weak_sem}")

                # =========================
                # 💼 PLACEMENT SNAPSHOT
                # =========================
                st.markdown("###  Placement Snapshot")

                total = len(stu_data)
                offers = len(stu_data[stu_data["Status"]=="Placed"])
                success = round((offers/total)*100,2) if total else 0

                p1,p2,p3 = st.columns(3)
                p1.metric("Attempts", total)
                p2.metric("Offers", offers)
                p3.metric("Success %", f"{success}%")

                # =========================
                # 🧠 SKILLS
                # =========================
                st.markdown("###  Skills")

                for s in skills:
                    st.markdown(f'<span class="chip">{s}</span>', unsafe_allow_html=True)

                # =========================
                # 🏆 ACHIEVEMENTS
                # =========================
                st.markdown("###  Achievements")

                c1,c2,c3 = st.columns(3)
                c1.metric("Hackathons", profile["Hackathons"])
                c2.metric("Papers", profile["Papers"])
                c3.metric("Conferences", profile["Conferences"])

                # =========================
                # 📋 DETAILS
                # =========================
                st.markdown("###  Details")

                important_cols = ["StudentID","Name","Branch","Year","Company","Status","Package"]

                col1,col2 = st.columns(2)

                for i,col in enumerate(important_cols):
                    with (col1 if i%2==0 else col2):
                        st.markdown(f"**{col}**: {profile.get(col,'')}")

                
                score = placement_score(profile)

                st.markdown("###  Placement Readiness")

                st.progress(score/100)
                st.metric("Score", f"{score}%")

                st.markdown("###  AI Insight")
                st.info(ai_summary(profile))

                st.markdown("###  Risk Indicators")

                if backlogs > 2:
                    st.error("High number of backlogs")

                if cgpa < 6.5:
                    st.warning("Low CGPA")

                if len(skills) < 3:
                    st.warning("Insufficient skills")

                st.markdown("###  Suggested Companies")

                if "Python" in profile["Skills"]:
                    st.success("Good fit for Software / Data roles")

                if cgpa > 8:
                    st.success("Eligible for top-tier companies")

                if backlogs > 0:
                    st.warning("Some companies may restrict due to backlogs")

                @st.cache_data
                def get_ranked_students(df):
                    return rank_students(df, model)
                rank_df = get_ranked_students(df)

                student_rank = rank_df[rank_df["StudentID"] == profile["StudentID"]]["Rank"].values[0]

                st.metric(" Rank", f"{int(student_rank)}")

            # ==========================================================
            # ACADEMICS TAB
            # ==========================================================
            st.markdown("""
            <style>

            /* App background */
            .stApp {
                background: linear-gradient(135deg, #0f172a, #020617);
                color: white;
            }

            /* Glass container */
            .glass {
                background: rgba(255,255,255,0.06);
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.12);
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.35);
            }

            /* Header */
            .section-title {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 10px;
            }

            /* KPI card */
            .kpi {
                background: rgba(255,255,255,0.05);
                padding: 15px;
                border-radius: 12px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.1);
            }

            /* Buttons */
            .stButton > button {
                border-radius: 10px;
                background: linear-gradient(90deg,#6a11cb,#2575fc);
                color: white;
                border: none;
            }

            </style>
            """, unsafe_allow_html=True)

            with student_tabs[1]:

                st.markdown('<div class="section-title">Academic Intelligence Command Center</div>', unsafe_allow_html=True)

                # =========================
                # DATA
                # =========================
                sgpas = np.array([profile[f"SGPA_Sem{i}"] for i in range(1,9)])
                backlogs = np.array([profile[f"Backlogs_Sem{i}"] for i in range(1,9)])
                attendance = np.array([profile[f"Attendance_Sem{i}"] for i in range(1,9)])

                avg_sgpa = sgpas.mean()
                consistency = sgpas.std()
                total_backlogs = backlogs.sum()
                avg_att = attendance.mean()

                # =========================
                # KPI GLASS ROW
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)

                df["Avg_SGPA"] = df[[f"SGPA_Sem{i}" for i in range(1,9)]].mean(axis=1)
                class_avg = df["Avg_SGPA"].mean()

                rank = df["Avg_SGPA"].rank(ascending=False)
                student_rank = int(rank[df["StudentID"] == profile["StudentID"]].values[0])
                percentile = round((1 - student_rank/len(df)) * 100,2)

                c1,c2,c3,c4,c5 = st.columns(5)
                c1.metric("SGPA", round(avg_sgpa,2))
                c2.metric("Class Avg", round(class_avg,2))
                c3.metric("Rank", student_rank)
                c4.metric("Percentile", f"{percentile}%")
                c5.metric("Backlogs", int(total_backlogs))

                st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                # COMPARISON
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("### Performance vs Class")

                comp_df = pd.DataFrame({
                    "Type": ["Student","Class"],
                    "SGPA": [avg_sgpa, class_avg]
                })

                st.plotly_chart(px.bar(comp_df, x="Type", y="SGPA"), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                # TREND + PREDICTION
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)

                col1,col2 = st.columns([2,1])

                with col1:
                    sem_df = pd.DataFrame({"Semester":range(1,9),"SGPA":sgpas})
                    st.plotly_chart(px.line(sem_df,x="Semester",y="SGPA",markers=True),
                                    use_container_width=True)

                with col2:
                    growth = (sgpas[-1]-sgpas[0])/7
                    predicted = sgpas[-1]+growth

                    st.metric("Predicted SGPA", round(predicted,2))

                    if predicted > avg_sgpa:
                        st.success("Positive trend expected")
                    else:
                        st.warning("Stagnation risk")

                st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                # DOMAIN INTELLIGENCE
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("### Domain Intelligence")

                subject_cols = [c for c in df.columns if "_Sem" in c and not any(x in c for x in ["SGPA","Attendance","Backlogs"])]

                domain_scores = {"AI/ML":0,"Core CS":0,"Finance":0}

                for col in subject_cols:
                    val = profile[col]
                    name = col.lower()

                    if "ai" in name:
                        domain_scores["AI/ML"] += val
                    elif "db" in name or "os" in name:
                        domain_scores["Core CS"] += val
                    elif "finance" in name:
                        domain_scores["Finance"] += val

                best_domain = max(domain_scores, key=domain_scores.get)

                st.write("Best Domain Fit:", best_domain)
                st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                # SUBJECT ANALYSIS
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("### Subject Intelligence")

                sem = st.selectbox("Semester",[1,2,3,4,5,6,7,8])

                cols = [c for c in df.columns if f"_Sem{sem}" in c and not any(x in c for x in ["SGPA","Attendance","Backlogs"])]
                sub = [c.replace(f"_Sem{sem}","") for c in cols]
                marks = [profile[c] for c in cols]

                sdf = pd.DataFrame({"Subject":sub,"Marks":marks})

                c1,c2 = st.columns(2)
                c1.plotly_chart(px.bar(sdf,x="Subject",y="Marks"),use_container_width=True)
                c2.plotly_chart(px.line_polar(sdf,r="Marks",theta="Subject",line_close=True),use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                # ADVANCED FEATURE (NEW)
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("### Performance Distribution")

                st.plotly_chart(px.histogram(df, x="Avg_SGPA"), use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                # RISK + PLAN
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("### Risk and Recommendations")

                if avg_sgpa < class_avg:
                    st.warning("Below class average performance")

                if total_backlogs > 0:
                    st.warning("Backlogs present")

                if avg_att < 75:
                    st.warning("Attendance below optimal level")

                st.write("Recommended Actions:")
                st.write("- Improve weak subjects")
                st.write("- Maintain consistency")
                st.write("- Focus on domain skills")

                st.markdown('</div>', unsafe_allow_html=True)

                # =========================
                # EXPORT
                # =========================
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("### Export")

                if st.button("Download Report"):
                    report = f"SGPA:{avg_sgpa}, Rank:{student_rank}, Domain:{best_domain}"
                    st.download_button("Download", report, "report.txt")

                st.markdown('</div>', unsafe_allow_html=True)

            # ==========================================================
            # SKILLS & ACTIVITIES
            # ==========================================================

            with student_tabs[2]:
                st.subheader("Skills & Achievements")
                skills = str(profile.get("Skills","")).split(",")
                skill_df = pd.DataFrame({
                    "Skill":skills,
                    "Level":[80+5*i for i in range(len(skills))]
                })
                fig_skill = px.bar(skill_df,x="Skill",y="Level")
                st.plotly_chart(fig_skill,use_container_width=True)

                st.write("### Achievements")
                c1,c2,c3 = st.columns(3)
                c1.metric("Hackathons",profile["Hackathons"])
                c2.metric("Papers",profile["Papers"])
                c3.metric("Conferences",profile["Conferences"])

                st.write("### Activities")
                a1,a2 = st.columns(2)
                a1.metric("Sports",profile["Sports"])
                a2.metric("Clubs",profile["Clubs"])

            # ==========================================================
            # PLACEMENTS
            # ==========================================================

            with student_tabs[3]:
                total_attempts = len(stu_data)
                placed = len(stu_data[stu_data["Status"]=="Placed"])
                rejected = len(stu_data[stu_data["Status"]=="Rejected"])
                success_ratio = round((placed/total_attempts)*100,2) if total_attempts > 0 else 0

                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Attempts",total_attempts)
                c2.metric("Offers",placed)
                c3.metric("Rejected",rejected)
                c4.metric("Success %",f"{success_ratio}%")

                fig1 = px.pie(names=["Placed","Rejected"], values=[placed,rejected], hole=0.6)
                st.plotly_chart(fig1,use_container_width=True)
                st.info(interpret_graph("Placement",stu_data))

                fig2 = px.bar(stu_data, x="Company", y="Package", color="Status")
                st.plotly_chart(fig2,use_container_width=True)
                st.dataframe(stu_data[["Company","Package","Status","Placed_Date"]])                            

# =======================
# ADMIN COMPANY ANALYSIS
# =======================

with tabs[3]:
    # ============================================================
    # YOUR EXISTING COMPANY ANALYTICS (UNCHANGED)
    # ============================================================

    st.markdown("---")
    st.subheader("   Company-wise Selection Analysis")

    company_year = df[df["Status"]=="Placed"].groupby(["Year","Company"])["StudentID"].nunique().reset_index()

    fig3 = px.bar(company_year, x="Company", y="StudentID", color="Year",
                  template="plotly_dark",
                  title="Company-wise Placements per Year")
    st.plotly_chart(fig3, use_container_width=True)

    year_filter = st.selectbox(
        "Select Year",
        sorted(df["Year"].unique()),
        key="year_filter_company"
    )
    filtered = company_year[company_year["Year"]==year_filter]

    fig4 = px.pie(filtered, names="Company", values="StudentID",
                  title=f"{year_filter} Company Distribution", hole=0.4)
    st.plotly_chart(fig4, use_container_width=True)

    # =====================================================

    st.markdown("##    AI Placement Insights")

    report = generate_narrative_report(df)

    for section, text in report.items():
        st.subheader(section)
        st.write(text)
    # =====================================================
    # ADVANCED COMPANY ANALYTICS DASHBOARD (ADMIN)
    # =====================================================

    st.markdown("##    Advanced Company Analytics")

    placed_df = df[df["Status"]=="Placed"].copy()

# -----------------------------------------------------
# 1. COMPANY HIRING PERFORMANCE ANALYSIS
# -----------------------------------------------------
    st.markdown("### 1   Company Hiring Performance")

    company_perf = df.groupby("Company").agg(
        Applicants=("StudentID","count"),
        Selected=("Status",lambda x:(x=="Placed").sum())
    ).reset_index()

    company_perf["Selection Rate %"] = round(
        (company_perf["Selected"]/company_perf["Applicants"])*100,2
    )

    fig = px.bar(
        company_perf,
        x="Company",
        y="Selected",
        color="Selection Rate %",
        title="Company vs Selected Students"
    )
    st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------
# 2. COMPANY PACKAGE ANALYSIS
# -----------------------------------------------------
    st.markdown("### 2   Company Package Analysis")

    package_stats = placed_df.groupby("Company")["Package"].agg(
        Highest="max",
        Average="mean",
        Median="median"
    ).reset_index()

    fig = px.bar(
        package_stats,
        x="Company",
        y="Average",
        title="Average Package by Company"
    )
    st.plotly_chart(fig,use_container_width=True)

    fig = px.box(
        placed_df,
        x="Company",
        y="Package",
        title="Salary Distribution by Company"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 3. BRANCH-WISE COMPANY HIRING
    # -----------------------------------------------------
    st.markdown("### 3   Branch-wise Company Preference")

    branch_company = placed_df.groupby(
        ["Branch","Company"]
    )["StudentID"].count().reset_index()

    fig = px.density_heatmap(
        branch_company,
        x="Company",
        y="Branch",
        z="StudentID",
        title="Branch vs Company Hiring"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 4. COMPANY DEMAND ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 4   Company Demand Analysis")

    demand = df.groupby("Company").agg(
        Applicants=("StudentID","count"),
        Selected=("Status",lambda x:(x=="Placed").sum())
    ).reset_index()

    demand["Conversion Rate %"] = round(
        (demand["Selected"]/demand["Applicants"])*100,2
    )

    fig = px.bar(
        demand,
        x="Company",
        y="Applicants",
        color="Conversion Rate %",
        title="Applicants vs Selection Rate"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 5. COMPANY DIFFICULTY INDEX
    # -----------------------------------------------------
    st.markdown("### 5   Company Difficulty Index")

    difficulty = demand.copy()
    difficulty["Difficulty Score"] = round(
        difficulty["Applicants"]/difficulty["Selected"].replace(0,1),2
    )

    fig = px.bar(
        difficulty,
        x="Company",
        y="Difficulty Score",
        title="Company Difficulty Score"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 6. COMPANY VISIT TREND
    # -----------------------------------------------------
    st.markdown("### 6   Company Visit Trend")

    company_year = df.groupby(["Year","Company"])["StudentID"].count().reset_index()

    fig = px.line(
        company_year,
        x="Year",
        y="StudentID",
        color="Company",
        title="Company Visits Over Years"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 7. OFFER ACCEPTANCE ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 7   Offer Acceptance Analysis")

    offer_dist = df["Status"].value_counts().reset_index()
    offer_dist.columns = ["Status","Count"]

    fig = px.pie(
        offer_dist,
        names="Status",
        values="Count",
        hole=0.4,
        title="Offer Acceptance Distribution"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 8. INTERNSHIP TO PPO CONVERSION
    # -----------------------------------------------------
    st.markdown("### 8   Internship to PPO Conversion")

    temp_df = df.groupby("Year")["Package"].mean().reset_index()

    fig = px.line(
        temp_df,
        x="Year",
        y="Package",
        markers=True
    )

    fig.update_traces(
        mode="lines+markers",
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_dark",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


    # -----------------------------------------------------
    # 9. COMPANY RETENTION ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 9   Company Retention")

    retention = df.groupby("Company")["Year"].nunique().reset_index()
    retention.columns = ["Company","Years Visited"]

    fig = px.bar(
        retention,
        x="Company",
        y="Years Visited",
        title="Company Retention (Years Visiting Campus)"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 10. SKILL DEMAND ANALYSIS
    # -----------------------------------------------------
    st.markdown("###    Skill Demand Analysis")

    skills = df["Skills"].str.split(",",expand=True).stack().value_counts().reset_index()
    skills.columns = ["Skill","Count"]

    fig = px.bar(
        skills.head(10),
        x="Skill",
        y="Count",
        title="Top Skills Required by Companies"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 11. INTERVIEW MODE ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 1  1   Interview Mode Analysis")

    if "InterviewMode" in df.columns:

        mode = df["InterviewMode"].value_counts().reset_index()
        mode.columns = ["Mode","Count"]

        fig = px.pie(
            mode,
            names="Mode",
            values="Count",
            hole=0.4,
            title="Interview Mode Distribution"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 12. HIRING SPEED ANALYSIS
    # -----------------------------------------------------
    st.markdown("### 1  2   Hiring Speed Analysis")

    if "Placed_Date" in df.columns:

        speed = df.groupby("Company")["Placed_Date"].min().reset_index()

        fig = px.histogram(
            speed,
            x="Placed_Date",
            title="Hiring Timeline Distribution"
        )
        st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 13. COMPANY QUALITY SCORE
    # -----------------------------------------------------
    st.markdown("### 1  3   Company Quality Score")

    quality = package_stats.merge(company_perf,on="Company")

    quality["Score"] = (
        quality["Average"]*0.4 +
        quality["Selection Rate %"]*0.3 +
        50*0.3
    )

    fig = px.bar(
        quality,
        x="Company",
        y="Score",
        title="Company Quality Score"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 14. PLACEMENT COVERAGE
    # -----------------------------------------------------
    st.markdown("### 1  4   Placement Coverage")

    coverage = placed_df["Company"].value_counts().reset_index()
    coverage.columns = ["Company","Students"]

    fig = px.pie(
        coverage,
        names="Company",
        values="Students",
        title="Placement Share by Company"
    )
    st.plotly_chart(fig,use_container_width=True)


    # -----------------------------------------------------
    # 15. TOP PAYING COMPANIES
    # -----------------------------------------------------
    st.markdown("### 1  5   Top Paying Companies")

    top_pay = placed_df.groupby("Company")["Package"].max().reset_index()

    fig = px.bar(
        top_pay.sort_values("Package",ascending=False).head(10),
        x="Company",
        y="Package",
        title="Top Paying Companies"
    )
    st.plotly_chart(fig,use_container_width=True)

# ============================================================
# ADMIN COMPANY DRIVE MANAGEMENT INTERFACE
# ============================================================
with tabs[4]:
    st.success("Register New Company Drive")

    # ===============================
    # COMPANY DRIVE REGISTRATION
    # ===============================

    with st.expander("   Register New Company Drive"):

        st.subheader("1   Basic Company Information")

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Company Name")
            company_website = st.text_input("Company Website")
            company_location = st.text_input("Company Location")
            industry_type = st.selectbox("Industry Type",
                                         ["IT","Finance","Consulting","Manufacturing","Other"])
            year_established = st.number_input("Year of Establishment",1950,2026)

        with col2:
            employees = st.number_input("Number of Employees",1,100000)
            company_desc = st.text_area("Company Description")
            contact_person = st.text_input("Contact Person Name")
            designation = st.text_input("Designation")
            email = st.text_input("Email ID")
            phone = st.text_input("Phone Number")


        # ===============================
        # JOB ROLE DETAILS
        # ===============================

        st.subheader("2   Job Role Details")

        col3, col4 = st.columns(2)

        with col3:
            job_title = st.text_input("Job Title / Role")
            department = st.selectbox("Department",
                                      ["IT","HR","Marketing","Finance","Other"])
            job_type = st.selectbox("Job Type",
                                    ["Full Time","Internship","Internship + PPO"])
            vacancies = st.number_input("Number of Vacancies",1,500)

        with col4:
            work_location = st.text_input("Work Location")
            bond = st.selectbox("Service Agreement",
                                ["No Bond","1 Year","2 Years"])
            job_desc = st.text_area("Job Description")


        # ===============================
        # SALARY & BENEFITS
        # ===============================

        st.subheader("3   Salary & Benefits")

        col5, col6 = st.columns(2)

        with col5:
            ctc = st.number_input("CTC (LPA)",0.0,50.0)
            inhand = st.number_input("In-Hand Salary",0.0,200000.0)
            training_salary = st.number_input("Training Period Salary",0.0,100000.0)

        with col6:
            bonus = st.text_input("Bonus / Incentives")
            health = st.selectbox("Health Insurance",["Yes","No"])
            accommodation = st.selectbox("Accommodation",["Yes","No"])
            travel = st.selectbox("Travel Allowance",["Yes","No"])


        # ===============================
        # ELIGIBILITY
        # ===============================

        st.subheader("4   Eligibility Criteria")

        eligible_branches = st.multiselect(
            "Eligible Branches",
            ["CSE","IT","ECE","EEE","Mechanical","Civil","AI & DS"]
        )

        min_cgpa = st.slider("Minimum CGPA",5.0,10.0,6.5)
        backlogs_allowed = st.number_input("Allowed Backlogs",0,10)

        skills_required = st.text_area("Required Skills")


        # ===============================
        # SELECTION PROCESS
        # ===============================

        st.subheader("5   Selection Process")

        rounds = st.multiselect(
            "Recruitment Rounds",
            ["Online Test","Coding Test","Group Discussion",
             "Technical Interview","HR Interview"]
        )

        test_platform = st.selectbox(
            "Test Platform",
            ["HackerRank","AMCAT","CoCubes","Company Portal","Other"]
        )

        interview_mode = st.selectbox(
            "Interview Mode",
            ["Online","Offline"]
        )


        # ===============================
        # RECRUITMENT SCHEDULE
        # ===============================

        st.subheader("6   Recruitment Schedule")

        ppt_date = st.date_input("Pre Placement Talk Date")
        test_date = st.date_input("Online Test Date")
        interview_date = st.date_input("Interview Date")
        offer_date = st.date_input("Offer Release Date")
        joining_date = st.date_input("Joining Date")


        # ===============================
        # DOCUMENTS REQUIRED
        # ===============================

        st.subheader("7   Documents Required")

        documents = st.multiselect(
            "Documents",
            ["Resume","Academic Mark Sheets","ID Proof",
             "Passport Photo","Portfolio/GitHub"]
        )


        # ===============================
        # INTERNAL PLACEMENT TRACKING
        # ===============================

        st.subheader("8   Placement Cell Internal Tracking")

        company_id = st.text_input("Company ID")
        drive_id = st.text_input("Drive ID")

        drive_status = st.selectbox(
            "Drive Status",
            ["Upcoming","Ongoing","Completed"]
        )

        applied = st.number_input("Students Applied",0,5000)
        shortlisted = st.number_input("Students Shortlisted",0,5000)
        selected = st.number_input("Students Selected",0,5000)


        # ===============================
        # SAVE BUTTON
        # ===============================

        if st.button("Save Company Drive", key="save_drive"):

            company_data = {
                "Company": company_name,
                "CTC": ctc,
                "Vacancies": vacancies,
                "Branches": eligible_branches,
                "Min CGPA": min_cgpa,
                "Rounds": rounds,
                "Drive Status": drive_status,
                "Selected Students": selected
            }

            import os

            file_path = "company_drives.csv"

            new_data = pd.DataFrame([company_data])

            if os.path.exists(file_path):
                new_data.to_csv(file_path, mode='a', header=False, index=False)
            else:
                new_data.to_csv(file_path, index=False)

            st.success("   Company Drive Registered Successfully")
            st.json(company_data)

