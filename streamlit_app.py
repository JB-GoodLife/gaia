import streamlit as st
import pandas as pd
import json
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Page configuration
st.set_page_config(page_title="Tilbudsmodul", layout="centered")

# Base directory and asset paths
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
json_path = BASE_DIR / "assets" / "postnumre.json"
logo_path = BASE_DIR / "assets" / "logo.png"

# Always display header and logo
def display_header():
    cols = st.columns(3)
    with cols[1]:
        st.image(str(logo_path))
    st.title("Tilbudsmodul (v5)")
    st.divider()

display_header()

# -------------------------------------------------------------------
# Authentication (fixed: uses a form and st.form_submit_button)
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "password" not in st.session_state:
    st.session_state["password"] = ""

def login_callback():
    if st.session_state["password"] == st.secrets["password"]:
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False

with st.form("login_form"):
    st.subheader("Login")
    st.text_input("Password", type="password", key="password")
    # IMPORTANT: form_submit_button is required in forms
    login_clicked = st.form_submit_button("Login", on_click=login_callback)

# If login was just clicked but password is wrong, show error
if login_clicked and not st.session_state["authenticated"]:
    st.error("Incorrect password!")

# If user is still not authenticated, stop here
if not st.session_state["authenticated"]:
    st.stop()
# -------------------------------------------------------------------

# Load JSON data
with open(json_path, encoding="utf-8") as f:
    data = pd.DataFrame(json.load(f))
postnumre = data["nr"]
byer = dict(zip(data["nr"], data["navn"]))

# Section: Udbetaling
st.subheader("Udbetaling")
col1, col2, col3 = st.columns(3)
with col1:
    recurring_monthly_payment = st.number_input("Månedlig udbetaling (DKK):", min_value=0, step=500, format="%d")
with col2:
    upfront_payment = st.number_input("Engangsudbetaling (DKK):", min_value=0, step=500)
with col3:
    duration_options = [("5 år", 20), ("10 år", 40)]
    duration = st.selectbox("Udbetalingsperiode:", options=duration_options, format_func=lambda x: x[0])[1]

# Section: Boligkarakteristika
st.subheader("Boligkarakteristika")
col1, col2, col3 = st.columns(3)
with col1:
    prop_value = st.number_input("Boligværdi (DKK):", min_value=0, step=5000, value=5000000)
with col2:
    equity = st.number_input("Friværdi (DKK):", min_value=0, step=5000, value=3500000)
with col3:
    debt_options = [("Ja", True), ("Nej", False)]
    afdrag = st.selectbox("Afdrages lånet løbende?", options=debt_options, format_func=lambda x: x[0])[1]

# Section: Kundeforhold
st.subheader("Kundeforhold")
col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Alder", step=1, min_value=60)
with col2:
    postnr = st.selectbox("Postnummer:", postnumre)
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

total_payment = df["Udbetaling"].sum()
besked = ":green[Høj]" if (total_payment < 1500000) and afdrag else ":red[Lav]"

if st.button("Beregn", type="primary", use_container_width=True):
    st.divider()
    st.header(f'Sandsynlighed: {besked}')
    st.divider()
    with st.expander("Se detaljer"):
        st.subheader("Samlet beløb")
        total_years = duration / 4
        st.metric(
            label=f'Udbetalt over {total_years:.0f} år',
            value=f'{total_payment:,} kr.'.replace(',', '.')
        )
        st.subheader("Udbetalingsprofil")
        st.dataframe(df.T.style.format(thousands="."), use_container_width=True)
        st.subheader("Illustration")
        st.bar_chart(df, color=['#295237'])

    # Email Sending Section
    st.divider()
    st.subheader("Send e-mail")
    sender_email = st.text_input("Sender Email", "lead@goodlife.dk", key="sender_email")
    receiver_email = st.text_input("Receiver Email", "jb@goodlife.dk", key="receiver_email")
    subject = st.text_input("Subject", "Test Email from SMTP2GO", key="email_subject")
    body = st.text_area("Body", "Hello,\n\nThis is a test email sent using SMTP2GO and Python.", key="email_body")

    if st.button("Send Email", key="send_email"):
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        SMTP_SERVER = "mail.smtp2go.com"
        SMTP_PORT = 587
        USERNAME = st.secrets["SMTP_USER"]
        PASSWORD = st.secrets["SMTP_PASS"]

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server
