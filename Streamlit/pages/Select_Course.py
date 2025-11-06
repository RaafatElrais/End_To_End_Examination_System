# pages/Select_Course.py
import streamlit as st
import sqlalchemy as sa
import pandas as pd
from datetime import datetime, timedelta
import base64

# --- Page Configuration and Styling ---
st.set_page_config(page_title="Select Course", layout="wide", initial_sidebar_state="collapsed")
# --- 2. Helper Function to get the logo image ---
def get_image_as_base_64(path):
    """Gets a local image as a base64 string."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.error("Logo file 'ITI-Logo.webp' not found. Please ensure it is in the same folder as app.py.")
        return None
    
encoded_logo = get_image_as_base_64("ITI-Logo.webp")
if encoded_logo:
    st.markdown(
        f'<img src="data:image/webp;base64,{encoded_logo}" style="position: fixed; top: 5rem; left: 1.5rem; width: 220px; z-index: 999;">',
        unsafe_allow_html=True
    )


st.markdown("""
<style>
    div[data-testid="stSidebar"] { display: none; }
    /* Style for the primary (red) button */
    button[kind="primary"] {
        background: linear-gradient(135deg, #ff4d4d, #ff1a1a);
        color: white; border: none; box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
    /* Style for the secondary (grey) button */
    button[kind="secondary"] {
        background-color: #E0E0E0; color: #333333; border: 1px solid #C0C0C0;
    }
</style>
""", unsafe_allow_html=True)


# --- Security Check ---
if not st.session_state.get("logged_in"):
    st.error("Please log in first.")
    st.stop()

# --- Database Functions ---
def get_db_engine():
    connection_string = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=ELRAIS\MSSQLSERVER02;'
        r'DATABASE=test;'
        r'Trusted_Connection=yes;'
    )
    quoted_conn_str = sa.engine.url.quote_plus(connection_string)
    engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_conn_str}")
    return engine

def fetch_courses(engine):
    try:
        df = pd.read_sql("SELECT Crs_ID, Crs_Name FROM dbo.Course", engine)
        return {name: id for id, name in df.itertuples(index=False)}
    except Exception as e:
        st.error(f"Could not fetch courses: {e}")
        return {}

def create_and_register_exam(engine, student_id, course_id):
    try:
        with engine.connect() as connection:
            with connection.begin() as transaction:
                start_time = datetime.now().time()
                end_time = (datetime.now() + timedelta(hours=2)).time()
                connection.execute(sa.text("EXEC Add_Exam :start, :end, :crs_id"),
                                   {"start": start_time, "end": end_time, "crs_id": course_id})
                result = connection.execute(sa.text("SELECT TOP 1 Ex_ID FROM Exam WHERE Crs_ID = :crs_id ORDER BY Ex_ID DESC"),
                                            {"crs_id": course_id}).scalar_one()
                new_exam_id = int(result)
                connection.execute(sa.text("EXEC Register_Student :st_id, :ex_id"),
                                   {"st_id": int(student_id), "ex_id": new_exam_id})
                return new_exam_id
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# --- Page Content ---
st.markdown("<h1 style='text-align: center;'>📚 Select Your Course</h1>", unsafe_allow_html=True)
st.write(" ")

col1, col2, col3 = st.columns([1.5, 2, 1.5])
with col2:
    db_engine = get_db_engine()
    courses_dict = fetch_courses(db_engine)
    if not courses_dict:
        st.warning("No courses found in the database.")
    else:
        course_names = list(courses_dict.keys())
        selected_course_name = st.selectbox("Choose a course to begin the exam:", course_names)
        
        # --- THIS IS THE STYLING FIX ---
        if st.button("Start Exam", use_container_width=True, type="primary"):
            st.session_state.course_id = courses_dict[selected_course_name]
            with st.spinner("Preparing your exam..."):
                new_exam_id = create_and_register_exam(db_engine, st.session_state.student_id, st.session_state.course_id)
                if new_exam_id:
                    st.session_state.exam_id = new_exam_id
                    st.success("Exam created successfully! Starting now...")
                    st.switch_page("pages/Take_Exam.py")
                else:
                    st.error("Failed to create the exam. Please try again.")

    st.divider()
    if st.button("⬅️ Back to Login Page", use_container_width=True, type="secondary"):
        st.switch_page("pages/Student_Login.py")