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

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# Function to send email
def send_email(subject, body, recipient):
    try:
        # Get credentials from secrets
        smtp_user = st.secrets["SMTP_User"]
        smtp_pass = st.secrets["SMTP_Pass"]
        
        # Create message
        message = MIMEMultipart()
        message["From"] = smtp_user
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
    
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == st.secrets["Site_Pass"]:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password")

# Main application
def main_app():
    st.title("Calculation Form")
    
    # Form inputs
    with st.form("calculation_form"):
        # Creating 9 input fields
        input_fields = {}
        
        # You can customize these fields based on your requirements
        input_fields["name"] = st.text_input("Name")
        input_fields["email"] = st.text_input("Email")
        input_fields["phone"] = st.text_input("Phone")
        input_fields["field1"] = st.number_input("Field 1", value=0.0)
        input_fields["field2"] = st.number_input("Field 2", value=0.0)
        input_fields["field3"] = st.number_input("Field 3", value=0.0)
        input_fields["field4"] = st.number_input("Field 4", value=0.0)
        input_fields["field5"] = st.number_input("Field 5", value=0.0)
        input_fields["field6"] = st.number_input("Field 6", value=0.0)
        
        # Submit button
        submitted = st.form_submit_button("Calculate")
        
        if submitted:
            # Store the form data in session state
            st.session_state.form_data = input_fields
            
            # Perform calculations (placeholder - you'll replace this later)
            result = input_fields["field1"] + input_fields["field2"] + input_fields["field3"]
            
            # Display result
            st.success(f"Calculation Result: {result}")
            
            # Email section becomes available
            st.session_state.calculation_done = True

    # Email section (only visible after calculation)
    if st.session_state.get("calculation_done", False):
        st.subheader("Send Results via Email")
        recipient = st.text_input("Recipient Email", value=st.session_state.form_data.get("email", ""))
        
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
            for key, value in st.session_state.form_data.items():
                body += f"<li><strong>{key}:</strong> {value}</li>"
            
            # Add calculation result
            result = st.session_state.form_data["field1"] + st.session_state.form_data["field2"] + st.session_state.form_data["field3"]
            body += f"</ul><h3>Calculation Result: {result}</h3>"
            
            # Send the email
            success, message = send_email(subject, body, recipient)
            if success:
                st.success(message)
            else:
                st.error(message)

# Main app flow
if st.session_state.authenticated:
    main_app()
    
    # Logout option
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.calculation_done = False
        st.experimental_rerun()
else:
    login_page()
