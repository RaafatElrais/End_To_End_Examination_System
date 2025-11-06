# pages/3_📝_Take_Exam.py
import streamlit as st
import sqlalchemy as sa
import pandas as pd
import base64

# --- Security Check to ensure user is logged in ---
if not st.session_state.get("logged_in"):
    st.error("Please log in first.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="Exam", layout="centered", initial_sidebar_state="collapsed")

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

# --- Custom CSS ---
st.markdown("""
<style>
    div[data-testid="stSidebar"] { display: none; }
    .stApp { background-color: white; }
    button[kind="primary"] {
        background: linear-gradient(135deg, #ff4d4d, #ff1a1a);
        color: white; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# --- Database Engine and Functions ---
def get_db_engine():
    """Creates and returns a SQLAlchemy engine with autocommit enabled."""
    connection_string = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=ELRAIS\MSSQLSERVER02;'
        r'DATABASE=test;'
        r'Trusted_Connection=yes;'
    )
    quoted_conn_str = sa.engine.url.quote_plus(connection_string)
    engine = sa.create_engine(
        f"mssql+pyodbc:///?odbc_connect={quoted_conn_str}",
        connect_args={"autocommit": True}
    )
    return engine

def fetch_exam_data(st_id, ex_id, crs_id):
    """Fetches the final, correctly joined exam data."""
    engine = get_db_engine()
    try:
        with engine.connect() as connection:
            check_query = f"SELECT COUNT(*) FROM Stu_Exam_Qs WHERE Stu_ID = {st_id} AND Ex_ID = {ex_id}"
            question_count = connection.execute(sa.text(check_query)).scalar()
            if question_count == 0:
                connection.execute(sa.text(f"EXEC Generate_And_Show_Exam @St_ID={st_id}, @Ex_ID={ex_id}, @Crs_ID={crs_id}"))
            final_data_query = f"""
            SELECT q.Qs_ID, q.Qs_Body, c.Options_Header, c.Options_Value
            FROM Stu_Exam_Qs seq JOIN Questions q ON seq.Qs_ID = q.Qs_ID JOIN Choices c ON q.Qs_ID = c.Qs_ID
            WHERE seq.Stu_ID = {st_id} AND Ex_ID = {ex_id}
            ORDER BY seq.Question_Order, c.Options_Header;
            """
            return pd.read_sql(final_data_query, connection)
    except Exception as e:
        st.error(f"Error fetching exam data: {e}")
        return pd.DataFrame()

# --- THIS IS THE FINAL FIX ---
def submit_answers(engine, st_id, ex_id, answers_list):
    """
    Submits answers and then runs a second query to fetch the calculated score.
    The 'with connection.begin()' block is removed to rely on autocommit.
    """
    valid_answers = [ans for ans in answers_list if ans is not None]
    answers_string = ",".join(valid_answers)
    try:
        with engine.connect() as connection:
            # Step 1: Execute your procedure. Autocommit ensures this is saved immediately.
            connection.execute(
                sa.text("EXEC SubmitExamAnswers :st_id, :ex_id, :answers"),
                {"st_id": int(st_id), "ex_id": int(ex_id), "answers": answers_string}
            )

            # Step 2: Now that the first step is committed, fetch the score.
            score_query = sa.text("SELECT Score FROM Student_Exam WHERE ST_ID = :st_id AND Ex_ID = :ex_id")
            result = connection.execute(
                score_query,
                {"st_id": int(st_id), "ex_id": int(ex_id)}
            ).scalar_one_or_none()

            # Save the score in the session state for the next page
            score = int(result) if result is not None else 0
            st.session_state.final_score = score
            
            return True
    except Exception as e:
        st.error(f"Failed to submit answers: {e}")
        return False

# --- Page Content ---
st_name = st.session_state.get("student_name", "Student")
st.title(f"Take Your Exam, {st_name}! 📝")

student_id = st.session_state.get("student_id")
exam_id = st.session_state.get("exam_id")
course_id = st.session_state.get("course_id")

if not all([student_id, exam_id, course_id]):
    st.error("Exam information missing. Please start over.")
    st.stop()

exam_df = fetch_exam_data(student_id, exam_id, course_id)
if exam_df.empty:
    st.error("Could not load exam questions. The course may not have any assigned.")
else:
    with st.form("exam_form"):
        st.header("Please choose the correct answers for the following questions:")
        st.write("---")
        student_answers_list = []
        for i, (q_id, group) in enumerate(exam_df.groupby('Qs_ID', sort=False)):
            question_body = group['Qs_Body'].iloc[0]
            values_list = group['Options_Value'].tolist()
            options_map = {row['Options_Value']: f"{row['Options_Header'].strip()}) {row['Options_Value']}" for index, row in group.iterrows()}
            st.subheader(f"Question {i + 1}: {question_body}")
            answer = st.radio(
                "Your Answer:", options=values_list, index=None,
                format_func=lambda value: options_map.get(value, value),
                key=q_id, label_visibility="collapsed"
            )
            student_answers_list.append(answer)
            st.write("---")
        submitted = st.form_submit_button("Submit Exam", type="primary")
        if submitted:
            if None in student_answers_list:
                st.warning("Please answer all questions before submitting.")
            else:
                with st.spinner("Submitting your answers..."):
                    db_engine = get_db_engine()
                    success = submit_answers(db_engine, student_id, exam_id, student_answers_list)
                    if success:
                        st.switch_page("pages/Thank_You.py")