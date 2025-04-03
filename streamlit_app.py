import streamlit as st

# Initialize session state for authentication.
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Password screen.
if not st.session_state.authenticated:
    st.title("Enter Password")
    password = st.text_input("Password", type="password")
    if password:
        if password == "TestPass":
            st.session_state.authenticated = True
            st.experimental_rerun()  # Refresh to show the main app.
        else:
            st.error("Incorrect password!")
else:
    st.title("Fun Project")
    st.write("Welcome! Enjoy the fun function below.")
    
    # A simple form with a fun function.
    with st.form("fun_form"):
        user_input = st.text_input("Enter some text:")
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            # Fun function: reverse the input text.
            result = user_input[::-1]
            st.success(f"Reversed: {result}")
