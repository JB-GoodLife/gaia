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
def send_email(subject, body):
    try:
        # Hardcoded recipient
        recipient = "jb@goodlife.dk"
        
        # Get credentials from secrets
        smtp_user = st.secrets["SMTP_User"]
        smtp_pass = st.secrets["SMTP_Pass"]
        
        # Create message
        message = MIMEMultipart()
        message["From"] = "lead@goodlife.dk"
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
        
        return True, f"Email sent successfully to {recipient}!"
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
        # Creating mandatory fields and the numeric fields
        st.subheader("Personlige oplysninger")
        col1, col2, col3 = st.columns(3)
        
        input_fields = {}
        
        with col1:
            input_fields["navn"] = st.text_input("Navn *", key="navn_input")
            input_fields["field1"] = st.number_input("Field 1", value=0.0, key="field1_input")
            
        with col2:
            input_fields["adresse"] = st.text_input("Adresse *", key="adresse_input")
            input_fields["field2"] = st.number_input("Field 2", value=0.0, key="field2_input")
            
        with col3:
            input_fields["telefonnummer"] = st.text_input("Telefonnummer *", key="telefonnummer_input")
            input_fields["field3"] = st.number_input("Field 3", value=0.0, key="field3_input")
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            input_fields["email"] = st.text_input("Email *", key="email_input")
            input_fields["field4"] = st.number_input("Field 4", value=0.0, key="field4_input")
            
        with col5:
            input_fields["alder"] = st.number_input("Alder (Yngste ejer) *", min_value=18, max_value=120, step=1, value=30, key="alder_input")
            input_fields["field5"] = st.number_input("Field 5", value=0.0, key="field5_input")
            
        with col6:
            # Empty space to align with other columns
            st.text("")
            input_fields["field6"] = st.number_input("Field 6", value=0.0, key="field6_input")
        
        # Optional comment field spanning all columns
        st.subheader("Yderligere oplysninger")
        input_fields["kommentar"] = st.text_area("Kommentar (valgfri)", height=150, key="kommentar_input")
        
        # Submit button
        submitted = st.form_submit_button("Calculate", on_click=_calculate_cb, args=(input_fields,))

    # Validation for mandatory fields
    if state.calculation_done:
        required_fields = ["navn", "adresse", "telefonnummer", "email", "alder"]
        missing_fields = [field for field in required_fields if not state.form_data.get(field)]
        
        if missing_fields:
            st.error(f"Venligst udfyld alle påkrævede felter: {', '.join(missing_fields)}")
            state.calculation_done = False
        else:
            st.success(f"Calculation Result: {state.result}")
            
            # Email section
            st.subheader("Send Results via Email")
            
            if st.button("Send Email"):
                # Prepare email content
                subject = "Ny beregning fra formular"
                
                # Create HTML body with form data and results
                body = f"""
                <h2>Calculation Results</h2>
                <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                
                <h3>Personlige oplysninger:</h3>
                <ul>
                <li><strong>Navn:</strong> {state.form_data['navn']}</li>
                <li><strong>Adresse:</strong> {state.form_data['adresse']}</li>
                <li><strong>Telefonnummer:</strong> {state.form_data['telefonnummer']}</li>
                <li><strong>Email:</strong> {state.form_data['email']}</li>
                <li><strong>Alder (Yngste ejer):</strong> {state.form_data['alder']}</li>
                """
                
                # Add comment if provided
                if state.form_data.get('kommentar'):
                    body += f"<li><strong>Kommentar:</strong> {state.form_data['kommentar']}</li>"
                
                body += "</ul>"
                
                # Add numeric field data
                body += f"""
                <h3>Indtastede værdier:</h3>
                <ul>
                <li><strong>Field 1:</strong> {state.form_data['field1']}</li>
                <li><strong>Field 2:</strong> {state.form_data['field2']}</li>
                <li><strong>Field 3:</strong> {state.form_data['field3']}</li>
                <li><strong>Field 4:</strong> {state.form_data['field4']}</li>
                <li><strong>Field 5:</strong> {state.form_data['field5']}</li>
                <li><strong>Field 6:</strong> {state.form_data['field6']}</li>
                </ul>
                """
                
                # Add calculation result
                body += f"<h3>Calculation Result: {state.result}</h3>"
                
                # Send the email
                success, message = send_email(subject, body)
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
