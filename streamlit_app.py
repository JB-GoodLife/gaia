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
init_state('email_data', {})
init_state('password', '')
init_state('result', 0)

# Generic callback to set state
def _set_state_cb(**kwargs):
    for state_key, widget_key in kwargs.items():
        val = state.get(widget_key, None)
        if val is not None or val == "":
            state[state_key] = state[widget_key]

# Authentication callback
def _login_cb():
    if state.password == st.secrets["Site_Pass"]:
        state.authenticated = True
    else:
        state.login_error = True

# Password change callback (for Enter key)
def password_entered():
    # This will be called when Enter is pressed in the password field
    _login_cb()

# Logout callback
def _logout_cb():
    state.authenticated = False
    state.calculation_done = False
    state.form_data = {}
    state.email_data = {}
    
# Function to send email
def send_email(subject, body):
    try:
        # Hardcoded recipient
        recipient = "ehz@goodlife.dk"
        cc = "jb@goodlife.dk"
        
        # Get credentials from secrets
        smtp_user = st.secrets["SMTP_User"]
        smtp_pass = st.secrets["SMTP_Pass"]
        
        # Create message
        message = MIMEMultipart()
        message["From"] = "lead@goodlife.dk"
        message["To"] = recipient
        message["Cc"] = cc
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
        
        return True, f"Lead sendt til {recipient}!"
    except Exception as e:
        return False, f"Fejl i afsendelse af lead: {str(e)}"

# Display logo
logo_path = "assets/logo.png"
if os.path.exists(logo_path):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
         st.image(logo_path, width=300)

# Authentication system
def login_page():
    st.title("Login")
    
    # Set up password field with on_change callback for Enter key
    st.text_input("Password", type="password", key="password", on_change=password_entered)
    
    # Button is still provided as an alternative login method
    if st.button("Login"):
        _login_cb()
    
    if state.get('login_error', False):
        st.error("Incorrect password")

# Main application
def main_app():
    st.title("Rådgiver- og henvisningsværktøj")
    
    # Main content inside an expander (open initially)
    with st.expander("**Tilbudsmodul**", expanded=True):
        # Using regular inputs instead of a form
        input_fields = {}

        # --- Udbetaling ---
        st.subheader("Udbetaling")
        col1, col2, col3 = st.columns(3)
        with col1:
            input_fields["field1"] = st.number_input(
                "Månedlig udbetaling (DKK)",
                value=0.0,
                key="maanedlig_udbetaling"
            )
        with col2:
            input_fields["field2"] = st.number_input(
                "Engangsudbetaling (DKK)",
                value=0.0,
                key="engangsudbetaling"
            )
        with col3:
            # Selectbox for period; parse integer from selected string
            period = st.selectbox(
                "Udbetalingsperiode",
                ["5 år", "10 år"]
            )
            # Convert selected option (e.g., "5 år") into an integer (5)
            input_fields["field3"] = int(period.split()[0])

        # --- Boligkarakteristika ---
        st.subheader("Boligkarakteristika")
        col1, col2, col3 = st.columns(3)
        with col1:
            input_fields["field4"] = st.number_input(
                "Boligværdi (DKK)",
                value=5000000,
                key="boligvaerdi"
            )
        with col2:
            input_fields["field5"] = st.number_input(
                "Friværdi (DKK)",
                value=3500000,
                key="frivaerdi"
            )
        with col3:
            input_fields["field6"] = st.selectbox(
                "Afdrages lånet løbende?",
                ["Ja", "Nej"],
                key="afdrag"
            )

        # --- Kundeforhold ---
        st.subheader("Kundeforhold")
        col1, col2, col3 = st.columns(3)
        with col1:
            input_fields["field7"] = st.number_input(
                "Yngste ejers alder",
                min_value=18,
                max_value=120,
                value=60,
                step=1
            )
        with col2:
            input_fields["field8"] = st.text_input(
                "Postnummer",
                key="postnummer"
            )

        # Calculate button outside form
        if st.button("Beregn"):
            # Replace this with your actual calculation logic
            state.result = input_fields["field1"] + input_fields["field2"] + input_fields["field3"]
            state.form_data = input_fields
            state.calculation_done = True

    # Display calculation results if calculation is done
    if state.calculation_done:
        st.success(f"Sandsynlighed: Høj. (Beregning: {state.result})")
        
        # Email section inside a collapsible container (collapsed by default)
        with st.expander("Send lead", expanded=False):
            with st.form("email_form", border=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    navn = st.text_input("Navn *", key="navn_email")
                    email = st.text_input("Email *", value=state.form_data.get("email", ""), key="email_email")
                with col2:
                    adresse = st.text_input("Adresse *", key="adresse_email")
                    alder = st.number_input("Alder (Yngste ejer) *", min_value=18, max_value=120, step=1, value=30, key="alder_email")
                with col3:
                    telefonnummer = st.text_input("Telefonnummer *", value=state.form_data.get("phone", ""), key="telefonnummer_email")
                kommentar = st.text_area("Kommentar (valgfri)", height=150, key="kommentar_email")
                email_submitted = st.form_submit_button("Send lead")
                if email_submitted:
                    # Validate required fields
                    required_fields = {
                        "Navn": navn,
                        "Adresse": adresse,
                        "Telefonnummer": telefonnummer,
                        "Email": email,
                        "Alder (Yngste ejer)": alder
                    }
                    missing_fields = [field for field, value in required_fields.items() if not value]
                    if missing_fields:
                        st.error(f"Venligst udfyld alle påkrævede felter: {', '.join(missing_fields)}")
                    else:
                        email_data = {
                            "navn": navn,
                            "adresse": adresse,
                            "telefonnummer": telefonnummer,
                            "email": email,
                            "alder": alder,
                            "kommentar": kommentar
                        }
                        subject = "Ny beregning fra formular"
                        body = f"""
                        <h2>Calculation Results</h2>
                        <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <h3>Original Input Data:</h3>
                        <ul>
                        """
                        for key, value in state.form_data.items():
                            body += f"<li><strong>{key}:</strong> {value}</li>"
                        body += f"</ul><h3>Calculation Result: {state.result}</h3>"
                        body += f"""
                        <h3>Personal Information:</h3>
                        <ul>
                        <li><strong>Navn:</strong> {navn}</li>
                        <li><strong>Adresse:</strong> {adresse}</li>
                        <li><strong>Telefonnummer:</strong> {telefonnummer}</li>
                        <li><strong>Email:</strong> {email}</li>
                        <li><strong>Alder (Yngste ejer):</strong> {alder}</li>
                        """
                        if kommentar:
                            body += f"<li><strong>Kommentar:</strong> {kommentar}</li>"
                        body += "</ul>"
                        success, message = send_email(subject, body)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

    # Sidebar and logout
    st.sidebar.title("Delsalg i korte træk.")
    st.sidebar.markdown("""
- **Et delsalg er et salg af en del af boligen** for at få glæde af sin friværdi uden likviditetsmæssig belastning.

- Kunden modtager en **kontant udbetaling**, og GoodLife bliver **passiv medejer.**

- **Når boligen sælges, får GoodLife sin andel af værdien**. Indtil da er der ingen løbende likviditetsbelastning for kunden.

- Da det ikke er et lån, kræver det **ingen vurdering af kundens økonomi eller kreditvurdering**.

- Kunden bliver boende og **bestemmer selv over boligen** – også hvornår den skal sælges.

- **Kunden betaler leje for den solgte del**. Det sker gennem ejerandelen ("med mursten") i stedet for med penge. Derfor er **GoodLifes ejerandel også større, end udbetalingen isoleret set svarer til.**

    """)
    
    if st.sidebar.button("Logout", on_click=_logout_cb):
        pass

# Main app flow
if state.authenticated:
    main_app()
else:
    login_page()
