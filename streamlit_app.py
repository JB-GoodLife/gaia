import streamlit as st

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Create a placeholder for the login form.
login_placeholder = st.empty()

if not st.session_state["authenticated"]:
    with login_placeholder.form("login_form"):
        st.title("Enter Password")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == "TestPass":
                st.session_state["authenticated"] = True
                login_placeholder.empty()  # Remove the login form.
            else:
                st.error("Incorrect password!")

if st.session_state["authenticated"]:
    st.title("Fun Project")
    st.write("Welcome! Enjoy the fun function below.")

    # A simple fun form that reverses the user's input.
    with st.form("fun_form"):
        user_input = st.text_input("Enter some text:")
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            result = user_input[::-1]
            st.success(f"Reversed: {result}")
