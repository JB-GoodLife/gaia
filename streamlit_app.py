import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Calculation App",
    page_icon="✨",
    layout="centered"
)

# State management shortcuts
state = st.session_state

# Initialize state variables
def init_state(key, value):
    if key not in state:
        state[key] = value

# Initialize all required state variables
init_state('authenticated', False)
init_state('calculation_done', False)
init_state('form_data', {})
init_state('password', '')

# Generic callback to set state
def _set_state_cb(**kwargs):
    for state_key, widget_key in kwargs.items():
        val = state.get(widget_key, None)
        if val is not None or val == "":
            state[state_key] = state[widget_key]

# Authentication callback
def _login_cb(password):
    if password == st.secrets["Site_Pass"]:
        state.authenticated = True
    else:
        state.login_error = True

# Logout callback
def _logout_cb():
    state.authenticated = False
    state.calculation_done = False
    state.form_data = {}

# Calculation callback
def _calculate_cb(input_fields):
    state.form_data = input_fields
    state.calculation_done = True
    
    # Replace this with your actual calculation logic
    state.result = input_fields["field1"] + input_fields["field2"] + input_fields["field3"]

# Function to send email
def send_email(subject, body, recipient):
    try:
        # Get credentials from secrets
        smtp_user = st.secrets["SMTP_User"]
        smtp_pass = st.secrets["SMTP_Pass"]
        
        # Create message
        message = MIMEMultipart()
        message["From"] = "lead@goodlife.dk"  # Changed as requested
        message["To"] = recipient
        message["Subject"] = subject
        
        # Attach body
        message.attach(MIMEText(body, "html"))
        
        # Connect to SMTP server (smtp2go)
        server = smtplib.SMTP("mail.smtp2go.com", 2525)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        
        # Send email
        server.send_message(message)
        server.quit()
        
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# Display logo
logo_path = "assets/logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=200)

# Authentication system
def login_page():
    st.title("Login")
    
    password = st.text_input("Password", type="password", key="password_input", 
                             on_change=_set_state_cb, kwargs={'password': 'password_input'})
    
    if st.button("Login", on_click=_login_cb, args=(state.password,)):
        pass
    
    if state.get('login_error', False):
        st.error("Incorrect password")

# Main application
def main_app():
    st.title("Calculation Form")
    
    # Form inputs
    with st.form("calculation_form", clear_on_submit=False):
        # Creating 9 input fields arranged in 3 columns
        st.subheader("Enter your information")
        col1, col2, col3 = st.columns(3)
        
        input_fields = {}
        
        with col1:
            input_fields["name"] = st.text_input("Name", key="name_input")
            input_fields["field1"] = st.number_input("Field 1", value=0.0, key="field1_input")
            input_fields["field4"] = st.number_input("Field 4", value=0.0, key="field4_input")
            
        with col2:
            input_fields["email"] = st.text_input("Email", key="email_input")
            input_fields["field2"] = st.number_input("Field 2", value=0.0, key="field2_input")
            input_fields["field5"] = st.number_input("Field 5", value=0.0, key="field5_input")
            
        with col3:
            input_fields["phone"] = st.text_input("Phone", key="phone_input")
            input_fields["field3"] = st.number_input("Field 3", value=0.0, key="field3_input")
            input_fields["field6"] = st.number_input("Field 6", value=0.0, key="field6_input")
        
        # Submit button
        submitted = st.form_submit_button("Calculate", on_click=_calculate_cb, args=(input_fields,))

    # Display calculation results if calculation is done
    if state.calculation_done:
        st.success(f"Calculation Result: {state.result}")
        
        # Email section
        st.subheader("Send Results via Email")
        recipient = st.text_input("Recipient Email", value=state.form_data.get("email", ""), key="recipient_input")
        
        if st.button("Send Email"):
            # Prepare email content
            subject = "Calculation Results"
            
            # Create HTML body with form data and results
            body = f"""
            <h2>Calculation Results</h2>
            <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <h3>Form Data:</h3>
            <ul>
            """
            
            # Add all form fields
            for key, value in state.form_data.items():
                body += f"<li><strong>{key}:</strong> {value}</li>"
            
            # Add calculation result
            body += f"</ul><h3>Calculation Result: {state.result}</h3>"
            
            # Send the email
            success, message = send_email(subject, body, recipient)
            if success:
                st.success(message)
            else:
                st.error(message)

# Main app flow
if state.authenticated:
    main_app()
    
    # Add Lorem Ipsum bullets to sidebar
    st.sidebar.title("Information")
    st.sidebar.markdown("""
    • Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor velit vitae justo finibus, at varius arcu facilisis.
    
    • Sed non risus magna. Duis sed felis vel nisi ultrices tincidunt. Vestibulum ante ipsum primis in faucibus orci.
    
    • Phasellus ullamcorper, magna in vestibulum elementum, eros urna vulputate nisl, at tincidunt erat augue vel eros.
    
    • Curabitur porta sapien ac neque consectetur, vel tempor mauris fringilla. Nulla facilisi. Donec ultrices urna vel.
    
    • Maecenas venenatis ante ut neque convallis, in eleifend magna tempus. Nunc feugiat nulla sit amet diam mattis.
    """)
    
    # Logout option
    if st.sidebar.button("Logout", on_click=_logout_cb):
        pass
else:
    login_page()
