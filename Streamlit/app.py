# app.py (Final Welcome Page - Sidebar Removed, All Buttons Red)
import streamlit as st
import base64

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Welcome",
    layout="wide"
)

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



# --- 3. Custom CSS ---
st.markdown("""
<style>
    /* THIS IS THE FIX: Completely removes the sidebar */
    div[data-testid="stSidebar"] {
        display: none;
    }

    /* THIS IS THE FIX: Styles ALL buttons on this page to be red */
    .stButton>button {
        background: linear-gradient(135deg, #ff4d4d, #ff1a1a);
        color: white;
        border: none;
        padding: 1.2rem 2.5rem; /* Adjusted padding slightly */
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease-in-out;
        margin-top: 2rem; /* Added margin-top back */
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #cc0000, #e60000); /* Darker red on hover */
    }

    /* Your other styles */
    .stApp {
        background-color: #ffffff;
    }
    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 1rem 0;
        background-color: #f5f3f4;
        font-size: 0.9rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)


# --- 4. Page Content ---

# Display the fixed logo in the top left corner
encoded_logo = get_image_as_base_64("ITI-Logo.webp")
if encoded_logo:
    st.markdown(
        f'<img src="data:image/webp;base64,{encoded_logo}" style="position: fixed; top: 5rem; left: 1.5rem; width: 220px; z-index: 999;">',
        unsafe_allow_html=True
    )

# Display the centered title and subtitle
st.markdown("<h1 style='text-align: center; margin-top: 5rem;'>Welcome To Our Examination System 👋</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: grey;'>Click the button below to begin.</h3>", unsafe_allow_html=True)
st.write(" ") # Spacer

# Use columns to center the "Start Now" button
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    # We removed type="primary" as the CSS now styles all buttons
    if st.button("Start Now 🚀", use_container_width=True):
        st.switch_page("pages/Student_Login.py")

# Footer (Optional - Keep or remove if not needed on this page)
st.markdown('<div class="custom-footer">© 2025 Examination System. All rights reserved.</div>', unsafe_allow_html=True)