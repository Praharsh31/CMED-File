
import streamlit as st
from db import test_connection, authenticate_user

st.set_page_config(
    page_title="CMED Tutoring Hub",
    page_icon="🎓",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None

st.title("College of Medicine")
st.header("CMED Tutoring Hub")
st.subheader("Learn together. Go further.")
st.write("Welcome to the CMED Tutoring Hub")

st.divider()

if st.session_state.user is None:
    st.subheader("Login")

    role = st.selectbox(
        "Login as",
        ["Student", "Tutor", "Admin"]
    )

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not email or not password:
            st.warning("Please enter your email and password.")
        else:
            try:
                user = authenticate_user(role, email, password)

                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error(
                        "Login unsuccessful. Check your credentials "
                        "or contact the project administrator."
                    )
            except Exception as error:
                st.error("Unable to complete login.")
                st.code(str(error))

else:
    user = st.session_state.user

    st.success(f"Welcome, {user['name']}!")
    st.write("Role:", user["role"])
    st.write("Email:", user["email"])

    if user["role"] == "Student":
        st.subheader("Student Portal")
        st.write("Your student dashboard will be built here.")

    elif user["role"] == "Tutor":
        st.subheader("Tutor Portal")
        st.write("Your tutor dashboard will be built here.")

    elif user["role"] == "Admin":
        st.subheader("Admin Portal")
        st.write("Your admin dashboard will be built here.")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

st.divider()

with st.expander("Database connection test"):
    if st.button("Test MySQL Connection"):
        try:
            database, version = test_connection()
            st.success("MySQL connection successful!")
            st.write("Database:", database)
            st.write("MySQL Version:", version)
        except Exception as error:
            st.error("MySQL connection failed.")
            st.code(str(error))
