import streamlit as st

# Initialize session state for authentication.
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Display login form if not authenticated.
if not st.session_state["authenticated"]:
    st.title("Enter Password")
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == "TestPass":
                st.session_state["authenticated"] = True
            else:
                st.error("Incorrect password!")

# Show main app if authenticated.
if st.session_state["authenticated"]:
    st.title("Fun Project")
    st.write("Welcome! Enjoy the fun function below.")
    
    # Fun form that reverses the user's input.
    with st.form("fun_form"):
        user_input = st.text_input("Enter some text:")
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            result = user_input[::-1]
            st.success(f"Reversed: {result}")
