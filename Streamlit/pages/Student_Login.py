# pages/1_🔑_Student_Login.py
import streamlit as st
import sqlalchemy as sa
import pandas as pd
import base64

# --- Page Configuration ---
st.set_page_config(page_title="Student Login", layout="wide", initial_sidebar_state="collapsed")

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
    # Display the fixed logo in the top left corner
encoded_logo = get_image_as_base_64("ITI-Logo.webp")
if encoded_logo:
    st.markdown(
        f'<img src="data:image/webp;base64,{encoded_logo}" style="position: fixed; top: 5rem; left: 1.5rem; width: 220px; z-index: 999;">',
        unsafe_allow_html=True
    )


# --- Custom CSS ---
st.markdown("""
<style>
    div[data-testid="stSidebar"] { display: none; }
    button[kind="primary"] {
        background: linear-gradient(135deg, #ff4d4d, #ff1a1a);
        color: white; border: none; box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
    button[kind="secondary"] {
        background-color: #E0E0E0; color: #333333; border: 1px solid #C0C0C0;
    }
</style>
""", unsafe_allow_html=True)

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

# --- THIS IS THE UPDATED FUNCTION ---
def check_student_credentials(email, password):
    """Verifies credentials and returns the student's ID and full name."""
    engine = get_db_engine()
    try:
        # We now use your correct query to get the full name.
        query = "SELECT st_ID, Fname+' '+Lname AS StudentName FROM dbo.Student WHERE Email = ? AND Password = ?"
        df = pd.read_sql(query, engine, params=(email, password))
        
        if not df.empty:
            # Return both values if login is successful
            student_id = df['st_ID'].iloc[0]
            student_name = df['StudentName'].iloc[0]
            return student_id, student_name
        return None, None # Return None for both if login fails
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return None, None

# --- Page Content ---
st.markdown("<h1 style='text-align: center;'>Student Login 🔑</h1>", unsafe_allow_html=True)
st.write(" ")

col1, col2, col3 = st.columns([1.5, 2, 1.5])
with col2:
    with st.form("login_form"):
        email = st.text_input("Student Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            # We now receive two variables: student_id and student_name.
            student_id, student_name = check_student_credentials(email, password)
            
            if student_id is not None:
                st.session_state.logged_in = True
                st.session_state.student_id = student_id
                # We save the student's full name in the session state.
                st.session_state.student_name = student_name 
                
                st.success("Login Successful! Redirecting...")
                st.switch_page("pages/Select_Course.py")
            else:
                st.error("Incorrect email or password.")

    st.divider()
    if st.button("⬅️ Back to Welcome Page", use_container_width=True, type="secondary"):
        st.switch_page("app.py")