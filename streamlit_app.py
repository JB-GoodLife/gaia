import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Page configuration
st.set_page_config(page_title="Tilbudsmodul", layout="centered")

# Define base directory and asset paths
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
json_path = BASE_DIR / "assets" / "postnumre.json"
logo_path = BASE_DIR / "assets" / "logo.png"

# Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Login form with centered logo
if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image(str(logo_path))
    with st.form("login_form"):
        st.title("Skriv password (v5)")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == st.secrets["password"]:
                st.session_state["authenticated"] = True
            else:
                st.error("Incorrect password!")
    st.stop()

# Main App Code

# Load JSON data
with open(json_path, encoding="utf-8") as f:
    data = pd.DataFrame(json.load(f))
postnumre = data["nr"]
byer = dict(zip(data["nr"], data["navn"]))

# Header with centered logo
col1, col2, col3 = st.columns(3)
with col2:
    st.image(str(logo_path))
st.title("Tilbudsmodul (v5)")
st.divider()

# Udbetaling Section
st.subheader("Udbetaling")
col1, col2, col3 = st.columns(3)
with col1:
    recurring_monthly_payment = st.number_input("Månedlig udbetaling (DKK):", min_value=0, step=500, format="%d")
with col2:
    upfront_payment = st.number_input("Engangsudbetaling (DKK):", min_value=0, step=500)
with col3:
    duration_options = [("5 år", 20), ("10 år", 40)]
    duration = st.selectbox("Udbetalingsperiode:", options=duration_options, format_func=lambda x: x[0])[1]

# Boligkarakteristika Section
st.subheader("Boligkarakteristika")
col1, col2, col3 = st.columns(3)
with col1:
    prop_value = st.number_input("Boligværdi (DKK):", min_value=0, step=5000, value=5000000)
with col2:
    equity = st.number_input("Friværdi (DKK):", min_value=0, step=5000, value=3500000)
with col3:
    debt_options = [("Ja", True), ("Nej", False)]
    afdrag = st.selectbox("Afdrages lånet løbende?", options=debt_options, format_func=lambda x: x[0])[1]

# Kundeforhold Section
st.subheader("Kundeforhold")
col1, col2, col3 = st.columns(3)
with col1:
    st.number_input("Alder", step=1, min_value=60)
with col2:
    postnr = st.selectbox("Postnummer:", postnumre, index=None, placeholder="Skriv postnummer")
with col3:
    st.text_input("", placeholder=byer.get(postnr, ""), disabled=True)

# Calculation and DataFrame creation
recurring_quarterly_payment = recurring_monthly_payment * 3
quarters = [f"Q{i}" for i in range(1, duration + 1)]
payments = [recurring_quarterly_payment] * duration
payments[0] += upfront_payment
df = pd.DataFrame([payments], columns=quarters, index=["Udbetaling"]).T
df.index = pd.Categorical(df.index, categories=quarters, ordered=True)
df = df.sort_index()

# Determine probability message
besked = ":green[Høj]" if (sum(df["Udbetaling"]) < 1500000) and afdrag else ":red[Lav]"

if st.button("Beregn", type="primary", use_container_width=True):
    st.divider()
    st.header(f'Sandsynlighed: {besked}')
    st.divider()
    with st.expander("Se detaljer"):
        st.subheader("Samlet beløb")
        st.metric(
            label=f'Udbetalt over {duration/4:.0f} år',
            value=f'{duration * recurring_quarterly_payment + upfront_payment:,} kr.'.replace(',', '.')
        )
        st.subheader("Udbetalingsprofil")
        st.dataframe(df.T.style.format(thousands="."), use_container_width=True)
        st.subheader("Illustration")
        st.bar_chart(df, color=['#295237'])

    if st.button("Beregn", type="primary", use_container_width=True):
        # SMTP2GO settings
        SMTP_SERVER = "mail.smtp2go.com"
        SMTP_PORT = 587  # Use 465 for SSL, 587 for STARTTLS
        USERNAME = st.secrets["SMTP-User"]
        PASSWORD = st.secrets["SMTP-Pass"]

        # Email details
        sender_email = "lead@goodlife.dk"
        receiver_email = "jb@goodlife.dk"
        subject = "Test Email from Lead Tool"
        body = "Hello,\n\nThis is a test email sent through Streamlit using SMTP2GO and Python."

        # Compose the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send the email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(USERNAME, PASSWORD)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                print("Email sent successfully!")
        except Exception as e:
            print("Failed to send email:", e)
