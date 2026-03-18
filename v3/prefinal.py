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
def load_data():

    df_master = pd.read_csv("placement_master_10yr_full_dataset.csv", low_memory=False)
    academics = pd.read_csv("academic_history_10years.csv", low_memory=False)
    placements = pd.read_csv("placement_history_10years.csv", low_memory=False)
    companies = pd.read_csv("companies_master.csv", low_memory=False)
    drives = pd.read_csv("mis_drives_10years.csv", low_memory=False)

    return df_master, academics, placements, companies, drives

df_master, academics, placements, companies, drives = load_data()


# ==============================
# CREATE MASTER DATASET
# ==============================

df = df_master.merge(
    placements,
    on=["StudentID","Year"],
    how="left"
)
df["Status"] = df["Status"].fillna("Rejected")
df["Package"] = df["Package"].fillna(0)
df["Company"] = df["Company"].fillna("Not Attempted")
 
# ======================================
# CREATE MAIN ANALYTICS DATASET
# ======================================

# Merge datasets
df = df_master.merge(placements, on=["StudentID","Year"], how="left")
df = df.merge(academics, on=["StudentID","Year"], how="left")

# Clean column names
df.columns = df.columns.str.strip()

# Ensure important columns exist
required_cols = ["StudentID","Name","Branch","Company","Package","Status","Year","Skills"]

for col in required_cols:
    if col not in df.columns:
        df[col] = "Unknown"

# Convert date
if "Placed_Date" in df.columns:
    df["Placed_Date"] = pd.to_datetime(df["Placed_Date"], errors="coerce")

# Ensure academic columns exist
for i in range(1,9):

    if f"SGPA_Sem{i}" not in df.columns:
        df[f"SGPA_Sem{i}"] = np.random.uniform(6.5,9.5,len(df)).round(2)

    if f"Attendance_Sem{i}" not in df.columns:
        df[f"Attendance_Sem{i}"] = np.random.randint(70,95,len(df))

    if f"Backlogs_Sem{i}" not in df.columns:
        df[f"Backlogs_Sem{i}"] = np.random.randint(0,2,len(df))

def generate_narrative_report(df):

    placed = df[df["Status"]=="Placed"].copy()

    report = {}

    # Hiring performance
    company_hires = placed["Company"].value_counts()

    if not company_hires.empty:
        top_company = company_hires.idxmax()
        report["Hiring Performance"] = f"{top_company} hired the most students."

    # Package analysis
    if "Package" in placed.columns:
        avg_package = placed["Package"].mean()
        report["Package Analysis"] = f"Average package across companies is {round(avg_package,2)} LPA."

    # Branch analysis
    branch_perf = placed["Branch"].value_counts()

    if not branch_perf.empty:
        top_branch = branch_perf.idxmax()
        report["Branch Performance"] = f"{top_branch} has the highest placements."

    # Placement rate
    total = df["StudentID"].nunique()
    placed_students = placed["StudentID"].nunique()

    rate = (placed_students / total) * 100 if total > 0 else 0

    report["Placement Rate"] = f"Overall placement rate is {round(rate,2)}%."

    return report

# =========================================
# SIMPLE DATASET AI ENGINE
# =========================================

def dataset_ai_engine(question, df):

    q = question.lower()

    if "placement rate" in q:
        total = df["StudentID"].nunique()
        placed = df[df["Status"]=="Placed"]["StudentID"].nunique()

        rate = (placed/total)*100 if total>0 else 0

        return f"Placement rate is {round(rate,2)}%."

    if "highest package" in q:

        row = df.loc[df["Package"].idxmax()]

        return f"{row['Name']} got the highest package of {row['Package']} LPA at {row['Company']}."

    if "top company" in q:

        comp = df[df["Status"]=="Placed"]["Company"].value_counts().idxmax()

        return f"{comp} hired the most students."

    return "Try asking about placement rate, highest package, or top company."

# =========================================
# GRAPH AI
# =========================================

def universal_graph_ai(question, df):

    q = question.lower()

    if "package" in q and "company" in q:

        fig = px.box(
            df,
            x="Company",
            y="Package",
            title="Package Distribution by Company"
        )

        return fig

    if "branch" in q:

        counts = df["Branch"].value_counts().reset_index()

        fig = px.bar(
            counts,
            x="index",
            y="Branch",
            title="Students by Branch"
        )

        return fig

    return None

# ================================
# AI PLACEMENT PREDICTION MODEL
# ================================

@st.cache_resource
def train_placement_model(df):

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    model_df = df.copy()

    model_df["Placed"] = model_df["Status"].apply(lambda x: 1 if x=="Placed" else 0)

    model_df["Skill_Count"] = model_df["Skills"].apply(lambda x: len(str(x).split(",")))

    features = [
        "CGPA",
        "Internships",
        "Hackathons",
        "Resume_Score",
        "GitHub_Score",
        "LeetCode_Rating",
        "Skill_Count"
    ]

    X = model_df[features]
    y = model_df["Placed"]

    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

    model = RandomForestClassifier(n_estimators=150)

    model.fit(X_train,y_train)

    return model


placement_model = train_placement_model(df)
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

    search = st.text_input("Search Student (ID or Name)", key="student_search_box")

    filtered_df = df.copy()

    student_list = filtered_df["StudentID"].unique().tolist()

    selected_student = st.selectbox(
        "Select Student ID",
        ["Select Student"] + student_list,
        key="student_select_1"
    )

    if selected_student == "Select Student":
        st.info("Please select a student")

    else:

        stu_data = df[df["StudentID"].astype(str) == str(selected_student)]

        if stu_data.empty:
            st.warning("No data available")

        else:

            profile = stu_data.iloc[0]

            # ===============================
            # STUDENT TABS
            # ===============================

            student_tabs = st.tabs([
                "Profile",
                "Academics",
                "Skills & Activities",
                "Placements"
            ])

            # =====================================================
            # PROFILE TAB
            # =====================================================

            with student_tabs[0]:

                st.markdown("## Student Intelligence Dashboard")

                col1, col2 = st.columns([1,3,])

                # PHOTO
                with col1:
                    st.image(
                        "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                        width=170
                    )

                # STUDENT INFO
                with col2:

                    st.markdown("### Student Information")

                    info1, info2 = st.columns(2)

                    with info1:
                        st.write("Name:", profile["Name"])
                        st.write("Student ID:", profile["StudentID"])
                        st.write("Branch:", profile["Branch"])
                        st.write("Gender:", profile["Gender"])

                    with info2:
                        st.write("Email:", profile["Email"])
                        st.write("Phone:", profile["Phone"])
                        st.write("Father:", profile["Father"])
                        st.write("Mother:", profile["Mother"])

                

                st.markdown("---")

                # KPI CARDS
                k1,k2,k3,k4,k5,k6 = st.columns(6)

                k1.metric("CGPA", profile["CGPA"])
                k2.metric("Internships", profile["Internships"])
                k3.metric("Hackathons", profile["Hackathons"])
                k4.metric("Research Papers", profile["Papers"])
                k5.metric("Clubs", profile["Clubs"])
                k6.metric("LeetCode", profile["LeetCode_Rating"])

                st.markdown("---")
                st.markdown("### AI Placement Predictor")

                skill_count = len(profile["Skills"].split(","))

                input_data = pd.DataFrame({

                    "CGPA":[profile["CGPA"]],
                    "Internships":[profile["Internships"]],
                    "Hackathons":[profile["Hackathons"]],
                    "Resume_Score":[profile["Resume_Score"]],
                    "GitHub_Score":[profile["GitHub_Score"]],
                    "LeetCode_Rating":[profile["LeetCode_Rating"]],
                    "Skill_Count":[skill_count]

                })

                prediction = placement_model.predict(input_data)[0]
                prob = placement_model.predict_proba(input_data)[0][1]

                col1,col2 = st.columns(2)

                with col1:

                    if prediction == 1:
                        st.success("High Placement Probability")
                    else:
                        st.warning("Placement Risk Detected")

                with col2:

                    st.metric("Placement Probability", f"{round(prob*100,2)}%")
                
                if prob > 0.75:

                    st.info(
                    "Analysis: The student has strong academic and skill indicators. "
                    "High probability of securing placement in upcoming drives."
                    )

                elif prob > 0.5:

                    st.info(
                    "Analysis: The student has moderate placement potential but "
                    "improvement in skills or internships can increase chances."
                    )

                else:

                    st.error(
                    "AI Analysis: The student currently has low placement probability. "
                    "Recommended to improve coding skills, internships and projects."
                    )
                st.markdown("### AI Student Intelligence Analysis")

                colA,colB,colC = st.columns(3)

                # =============================
                # PLACEMENT READINESS SCORE
                # =============================

                cgpa_score = profile["CGPA"] * 10
                skill_score = len(profile["Skills"].split(",")) * 8
                intern_score = profile["Internships"] * 15
                coding_score = profile["LeetCode_Rating"] / 20

                placement_score = cgpa_score + skill_score + intern_score + coding_score

                with colA:

                    st.metric("Placement Readiness Score", round(placement_score,2))

                    if placement_score > 220:
                        st.success("Highly Placement Ready")
                    elif placement_score > 180:
                        st.info("Moderately Ready")
                    else:
                        st.warning("Needs Preparation")


                # =============================
                # INTERVIEW READINESS INDEX
                # =============================

                interview_index = (
                    profile["CGPA"]*5 +
                    profile["Hackathons"]*10 +
                    profile["Internships"]*15 +
                    profile["LeetCode_Rating"]/50
                )

                with colB:

                    st.metric("Interview Readiness Index", round(interview_index,2))

                    if interview_index > 80:
                        st.success("Strong Interview Readiness")
                    elif interview_index > 60:
                        st.info("Average Interview Preparation")
                    else:
                        st.warning("Needs Interview Practice")


                # =============================
                # RESUME STRENGTH
                # =============================

                resume_strength = (
                    profile["Resume_Score"] +
                    profile["GitHub_Score"]/2 +
                    profile["Papers"]*10 +
                    profile["Internships"]*15
                )

                with colC:

                    st.metric("Resume Strength Score", round(resume_strength,2))

                    if resume_strength > 120:
                        st.success("Strong Resume")
                    elif resume_strength > 80:
                        st.info("Average Resume")
                    else:
                        st.warning("Resume Needs Improvement")

                st.markdown("---")

                # =====================================
                # CAREER DOMAIN PREDICTION
                # =====================================

                st.subheader("AI Career Domain Prediction")

                skills = profile["Skills"].split(",")

                domain_scores = {

                    "Data Science": sum(s in ["Python","Machine Learning","Deep Learning","SQL","TensorFlow"] for s in skills),

                    "Software Development": sum(s in ["Java","C++","React","NodeJS","SQL"] for s in skills),

                    "Cloud Engineering": sum(s in ["AWS","Docker","Kubernetes","DevOps","Linux"] for s in skills),

                    "Cybersecurity": sum(s in ["Cybersecurity","Linux","Networking"] for s in skills),

                }

                best_domain = max(domain_scores, key=domain_scores.get)

                col1,col2 = st.columns(2)

                with col1:
                    st.metric("Best Career Domain", best_domain)

                with col2:
                    st.write("Domain Score Distribution")

                    domain_df = pd.DataFrame({
                        "Domain":domain_scores.keys(),
                        "Score":domain_scores.values()
                    })

                    fig = px.bar(domain_df,x="Domain",y="Score")

                    st.plotly_chart(fig,use_container_width=True)

                st.markdown("---")

                # =====================================
                # SKILL MARKET DEMAND MATCH
                # =====================================

                st.subheader("Market Skill Demand Match")

                market_skills = [
                    "Python","Machine Learning","SQL",
                    "Cloud Computing","DevOps",
                    "System Design","Docker",
                    "Kubernetes","AI","Data Engineering"
                ]

                student_skills = profile["Skills"].split(",")

                match_score = len(set(student_skills).intersection(market_skills)) / len(market_skills) * 100

                col1,col2 = st.columns(2)

                with col1:
                    st.metric("Market Skill Match", f"{round(match_score,2)}%")

                with col2:
                    missing = list(set(market_skills) - set(student_skills))

                    st.write("Recommended Skills")

                    for m in missing[:5]:
                        st.warning(m)

                st.markdown("---")

                # =====================================
                # STUDENT RISK DETECTION
                # =====================================

                st.subheader("Academic Risk Detection")

                backlogs = sum([
                    profile["Backlogs_Sem1"],
                    profile["Backlogs_Sem2"],
                    profile["Backlogs_Sem3"],
                    profile["Backlogs_Sem4"],
                    profile["Backlogs_Sem5"],
                    profile["Backlogs_Sem6"],
                    profile["Backlogs_Sem7"],
                    profile["Backlogs_Sem8"]
                ])

                risk_score = (backlogs*15) + (8-profile["CGPA"])*10

                if risk_score < 20:
                    st.success("Low Academic Risk")
                elif risk_score < 50:
                    st.info("Moderate Academic Risk")
                else:
                    st.error("High Academic Risk – Needs Intervention")

                # ======================================
                # SGPA + SKILL RADAR
                # ======================================

                colA, colB = st.columns(2)

                # SGPA GRAPH
                with colA:

                    sgpa_df = pd.DataFrame({
                        "Semester":[1,2,3,4,5,6,7,8],
                        "SGPA":[
                            profile["SGPA_Sem1"],
                            profile["SGPA_Sem2"],
                            profile["SGPA_Sem3"],
                            profile["SGPA_Sem4"],
                            profile["SGPA_Sem5"],
                            profile["SGPA_Sem6"],
                            profile["SGPA_Sem7"],
                            profile["SGPA_Sem8"]
                        ]
                    })

                    fig = px.line(sgpa_df, x="Semester", y="SGPA", markers=True)

                    st.plotly_chart(fig, use_container_width=True)

                # SKILL RADAR
                with colB:

                    skills = profile["Skills"].split(",")

                    radar_df = pd.DataFrame({
                        "Skill": skills,
                        "Score": np.random.randint(70,95,len(skills))
                    })

                    fig = px.line_polar(
                        radar_df,
                        r="Score",
                        theta="Skill",
                        line_close=True
                    )

                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")

                # SKILL GAP
                st.subheader("Skill Gap Analysis")

                demanded_skills = [
                    "Python","SQL","Machine Learning","Cloud Computing",
                    "Data Structures","System Design","DevOps","AI"
                ]

                student_skills = profile["Skills"].split(",")

                missing = list(set(demanded_skills) - set(student_skills))

                col1,col2 = st.columns(2)

                with col1:
                    st.markdown("### Student Skills")
                    for s in student_skills:
                        st.success(s)

                with col2:
                    st.markdown("### Recommended Skills")
                    for s in missing[:5]:
                        st.warning(s)

                st.markdown("---")

                # ADDRESS
                st.subheader("Address")
                st.write(profile["Address"])

            # =====================================================
            # ACADEMICS TAB
            # =====================================================

            with student_tabs[1]:

                st.markdown("## Academic Intelligence Dashboard")

                # =============================
                # AI INTERPRETATION ENGINE
                # =============================

                def academic_ai(graph, data):

                    if graph == "sgpa":
                        avg = data["SGPA"].mean()
                        trend = "improving" if data["SGPA"].iloc[-1] > data["SGPA"].iloc[0] else "declining"

                        if avg >= 8.5:
                            level = "excellent"
                        elif avg >= 7:
                            level = "moderate"
                        else:
                            level = "weak"

                        return f"AI Insight: The SGPA trend is {trend}. Average SGPA is {round(avg,2)}, indicating {level} academic performance."

                    if graph == "attendance":
                        avg = data["Attendance"].mean()

                        if avg > 85:
                            return "AI Insight: Attendance levels are consistently strong showing high academic discipline."
                        elif avg > 75:
                            return "AI Insight: Attendance levels are acceptable but can be improved."
                        else:
                            return "AI Insight: Low attendance may impact academic performance and placement readiness."

                    if graph == "backlogs":
                        total = data["Backlogs"].sum()

                        if total == 0:
                            return "AI Insight: Student maintains a clean academic record with no backlogs."
                        else:
                            return f"AI Insight: Student has accumulated {total} backlogs which may affect eligibility for certain companies."

                    if graph == "subjects":
                        top = data.sort_values("Marks",ascending=False).iloc[0]["Subject"]
                        weak = data.sort_values("Marks").iloc[0]["Subject"]

                        return f"AI Insight: Strongest subject is {top}. Improvement recommended in {weak}."

                    return "AI analysis completed."


                # =============================
                # SGPA DATA
                # =============================

                sgpa_df = pd.DataFrame({
                    "Semester":[1,2,3,4,5,6,7,8],
                    "SGPA":[
                        profile["SGPA_Sem1"],
                        profile["SGPA_Sem2"],
                        profile["SGPA_Sem3"],
                        profile["SGPA_Sem4"],
                        profile["SGPA_Sem5"],
                        profile["SGPA_Sem6"],
                        profile["SGPA_Sem7"],
                        profile["SGPA_Sem8"]
                    ]
                })


                # =============================
                # ATTENDANCE DATA
                # =============================

                att_df = pd.DataFrame({
                    "Semester":[1,2,3,4,5,6,7,8],
                    "Attendance":[
                        profile["Attendance_Sem1"],
                        profile["Attendance_Sem2"],
                        profile["Attendance_Sem3"],
                        profile["Attendance_Sem4"],
                        profile["Attendance_Sem5"],
                        profile["Attendance_Sem6"],
                        profile["Attendance_Sem7"],
                        profile["Attendance_Sem8"]
                    ]
                })


                # =============================
                # BACKLOG DATA
                # =============================

                back_df = pd.DataFrame({
                    "Semester":[1,2,3,4,5,6,7,8],
                    "Backlogs":[
                        profile["Backlogs_Sem1"],
                        profile["Backlogs_Sem2"],
                        profile["Backlogs_Sem3"],
                        profile["Backlogs_Sem4"],
                        profile["Backlogs_Sem5"],
                        profile["Backlogs_Sem6"],
                        profile["Backlogs_Sem7"],
                        profile["Backlogs_Sem8"]
                    ]
                })


                # =============================
                # ROW 1 — SGPA & ATTENDANCE
                # =============================

                col1, col2 = st.columns(2)

                with col1:

                    st.subheader("SGPA Trend")

                    fig = px.line(
                        sgpa_df,
                        x="Semester",
                        y="SGPA",
                        markers=True,
                        template="plotly_dark"
                    )

                    st.plotly_chart(fig,use_container_width=True,key=f"sgpa_{selected_student}")

                    st.info(academic_ai("sgpa", sgpa_df))


                with col2:

                    st.subheader("Attendance Trend")

                    fig = px.bar(
                        att_df,
                        x="Semester",
                        y="Attendance",
                        template="plotly_dark"
                    )

                    st.plotly_chart(fig,use_container_width=True,key=f"attendance_{selected_student}")

                    st.info(academic_ai("attendance", att_df))


                # =============================
                # ROW 2 — BACKLOG + SUBJECT
                # =============================

                col3, col4 = st.columns(2)

                with col3:

                    st.subheader("Backlog Trend")

                    fig = px.bar(
                        back_df,
                        x="Semester",
                        y="Backlogs",
                        template="plotly_dark",
                        color="Backlogs"
                    )

                    st.plotly_chart(fig,use_container_width=True,key=f"backlog_{selected_student}")

                    st.info(academic_ai("backlogs", back_df))


                with col4:

                    st.subheader("Subject Performance")

                    sem = st.selectbox(
                        "Select Semester",
                        [1,2,3,4,5,6,7,8],
                        key=f"semester_select_{selected_student}"
                    )

                    subject_cols = [
                        c for c in df.columns
                        if f"_Sem{sem}" in c
                        and "SGPA" not in c
                        and "Attendance" not in c
                        and "Backlogs" not in c
                    ]

                    subjects = []
                    marks = []

                    for col in subject_cols:
                        subjects.append(col.replace(f"_Sem{sem}",""))
                        marks.append(profile.get(col,0))

                    subject_df = pd.DataFrame({
                        "Subject":subjects,
                        "Marks":marks
                    })

                    fig = px.bar(
                        subject_df,
                        x="Subject",
                        y="Marks",
                        template="plotly_dark"
                    )

                    st.plotly_chart(fig,use_container_width=True,key=f"subjects_{selected_student}")

                    st.info(academic_ai("subjects", subject_df))


                # =============================
                # SUBJECT RADAR
                # =============================

                st.subheader("Subject Strength Radar")

                fig = px.line_polar(
                    subject_df,
                    r="Marks",
                    theta="Subject",
                    line_close=True
                )

                st.plotly_chart(fig,use_container_width=True,key=f"radar_{selected_student}")


                # =============================
                # SGPA DISTRIBUTION
                # =============================

                st.subheader("SGPA Distribution")

                fig = px.histogram(
                    sgpa_df,
                    x="SGPA",
                    nbins=8
                )

                st.plotly_chart(fig,use_container_width=True,key=f"sgpa_hist_{selected_student}")


                # =============================
                # ACADEMIC PERFORMANCE INDEX
                # =============================

                st.subheader("Academic Performance Index")

                academic_score = (
                    np.mean(sgpa_df["SGPA"])*10 +
                    np.mean(att_df["Attendance"])*0.3 -
                    np.sum(back_df["Backlogs"])*5
                )

                if academic_score > 120:
                    level = "Excellent"
                elif academic_score > 100:
                    level = "Good"
                else:
                    level = "Needs Improvement"

                c1,c2 = st.columns(2)

                c1.metric("Academic Score", round(academic_score,2))
                c2.metric("Academic Level", level)
            # =====================================================
            # SKILLS TAB
            # =====================================================

            with student_tabs[2]:

                st.subheader("Skills & Achievements")

                skills = profile["Skills"].split(",")

                skill_df = pd.DataFrame({
                    "Skill":skills,
                    "Level":[80+5*i for i in range(len(skills))]
                })

                fig = px.bar(skill_df,x="Skill",y="Level")

                st.plotly_chart(fig,use_container_width=True)

            # =====================================================
            # PLACEMENTS TAB
            # =====================================================

            with student_tabs[3]:

                total_attempts = len(stu_data)
                placed = len(stu_data[stu_data["Status"]=="Placed"])
                rejected = len(stu_data[stu_data["Status"]=="Rejected"])

                success_ratio = round((placed/total_attempts)*100,2)

                c1,c2,c3,c4 = st.columns(4)

                c1.metric("Attempts",total_attempts)
                c2.metric("Offers",placed)
                c3.metric("Rejected",rejected)
                c4.metric("Success %",f"{success_ratio}%")

                fig = px.pie(
                    names=["Placed","Rejected"],
                    values=[placed,rejected],
                    hole=0.6
                )

                st.plotly_chart(fig,use_container_width=True)
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

    if "JobType" in df.columns:
        ppo = df["JobType"].value_counts().reset_index()
        ppo.columns = ["Type","Count"]

        fig = px.bar(
            ppo,
            x="Type",
            y="Count",
            title="Internship vs Full-time Hiring"
        )
        st.plotly_chart(fig,use_container_width=True)


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

            st.success("   Company Drive Registered Successfully")
            st.json(company_data)

