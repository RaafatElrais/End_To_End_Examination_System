# pages/4_🎉_Thank_You.py
import streamlit as st
import sqlalchemy as sa
import base64

# --- Security Check ---
if not st.session_state.get("logged_in"):
    st.error("Please log in first.")
    st.stop()

# --- Page Configuration and Styling ---
st.set_page_config(page_title="Finished!", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    div[data-testid="stSidebar"] { display: none; }
    .stApp { background-color: white; }
    button[kind="primary"] {
        background: linear-gradient(135deg, #ff4d4d, #ff1a1a); color: white; border: none;
    }
</style>
""", unsafe_allow_html=True)


# --- THIS IS THE NEW PART: Database Functions ---
def get_db_engine():
    """Creates a SQLAlchemy engine with autocommit enabled."""
    connection_string = (r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=ELRAIS\MSSQLSERVER02;DATABASE=test;Trusted_Connection=yes;')
    quoted_conn_str = sa.engine.url.quote_plus(connection_string)
    engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_conn_str}", connect_args={"autocommit": True})
    return engine

def get_final_score(engine, st_id, ex_id):
    """
    Fetches the final score directly from the Student_Exam table.
    """
    try:
        with engine.connect() as connection:
            score_query = sa.text("SELECT Score FROM Student_Exam WHERE ST_ID = :st_id AND Ex_ID = :ex_id")
            result = connection.execute(score_query, {"st_id": int(st_id), "ex_id": int(ex_id)}).scalar_one_or_none()
            return int(result) if result is not None else 0
    except Exception as e:
        st.error(f"Failed to retrieve score: {e}")
        return 0

# --- Helper Function to Calculate Grade ---
def calculate_grade(score_percentage):
    if score_percentage >= 85: return "A (Excellent)"
    elif score_percentage >= 75 and score_percentage < 85: return "B (Very Good)"
    elif score_percentage >= 65 and score_percentage < 75: return "C (Good)"
    elif score_percentage >= 50 and score_percentage < 65: return "D (Pass)"
    else: return "F (Fail)"


# --- Main Page Content ---
db_engine = get_db_engine()
student_id = st.session_state.get("student_id")
exam_id = st.session_state.get("exam_id")

# Fetch the score directly on this page
final_score = get_final_score(db_engine, student_id, exam_id)
score_percentage = final_score * 10
grade = calculate_grade(score_percentage)

# --- Display the results ---
st.markdown(f"<h2 style='text-align: center; margin-top: 2rem;'>Your Score: {score_percentage} / 100</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: grey;'>Grade: {grade}</p>", unsafe_allow_html=True)
st.write("---")

st.balloons()
st.markdown(f"<h1 style='text-align: center;'>Thank You, {st.session_state.get('student_name', '')}! 😊</h1>", unsafe_allow_html=True)

if st.button("End and Return to Welcome Page", use_container_width=True, type="primary"):
    # Clean up all session data for security
    keys_to_delete = ['logged_in', 'student_id', 'student_name', 'exam_id', 'course_id']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.switch_page("app.py")