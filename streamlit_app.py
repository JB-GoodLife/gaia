import streamlit as st
import pandas as pd
import json
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Page configuration
st.set_page_config(page_title="Tilbudsmodul", layout="centered")

def authenticate(logo_path):
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        cols = st.columns([1, 2, 1])
        with cols[1]:
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

def load_data(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = pd.DataFrame(json.load(f))
    postnumre = data["nr"]
    byer = dict(zip(data["nr"], data["navn"]))
    return postnumre, byer

def display_header(logo_path):
    cols = st.columns(3)
    with cols[1]:
        st.image(str(logo_path))
    st.title("Tilbudsmodul (v5)")
    st.divider()

def get_udbetaling_inputs():
    st.subheader("Udbetaling")
    col1, col2, col3 = st.columns(3)
    with col1:
        recurring_monthly_payment = st.number_input(
            "Månedlig udbetaling (DKK):", min_value=0, step=500, format="%d"
        )
    with col2:
        upfront_payment = st.number_input(
            "Engangsudbetaling (DKK):", min_value=0, step=500
        )
    with col3:
        duration_options = [("5 år", 20), ("10 år", 40)]
        duration = st.selectbox(
            "Udbetalingsperiode:", options=duration_options, format_func=lambda x: x[0]
        )[1]
    return recurring_monthly_payment, upfront_payment, duration

def get_bolig_inputs():
    st.subheader("Boligkarakteristika")
    col1, col2, col3 = st.columns(3)
    with col1:
        prop_value = st.number_input(
            "Boligværdi (DKK):", min_value=0, step=5000, value=5000000
        )
    with col2:
        equity = st.number_input(
            "Friværdi (DKK):", min_value=0, step=5000, value=3500000
        )
    with col3:
        debt_options = [("Ja", True), ("Nej", False)]
        afdrag = st.selectbox(
            "Afdrages lånet løbende?", options=debt_options, format_func=lambda x: x[0]
        )[1]
    return prop_value, equity, afdrag

def get_kundeforhold_inputs(postnumre, byer):
    st.subheader("Kundeforhold")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Alder", step=1, min_value=60)
    with col2:
        postnr = st.selectbox("Postnummer:", postnumre)
    with col3:
        st.text_input("", placeholder=byer.get(postnr, ""), disabled=True)
    return age, postnr

def calculate_payments(recurring_monthly_payment, upfront_payment, duration):
    recurring_quarterly_payment = recurring_monthly_payment * 3
    quarters = [f"Q{i}" for i in range(1, duration + 1)]
    payments = [recurring_quarterly_payment] * duration
    payments[0] += upfront_payment
    df = pd.DataFrame([payments], columns=quarters, index=["Udbetaling"]).T
    df.index = pd.Categorical(df.index, categories=quarters, ordered=True)
    df = df.sort_index()
    return df, recurring_quarterly_payment

def determine_probability(df, afdrag):
    total_payment = df["Udbetaling"].sum()
    return ":green[Høj]" if (total_payment < 1500000) and afdrag else ":red[Lav]"

def send_email():
    SMTP_SERVER = "mail.smtp2go.com"
    SMTP_PORT = 587  # Use 465 for SSL, 587 for STARTTLS
    USERNAME = st.secrets["SMTP_User"]
    PASSWORD = st.secrets["SMTP_Pass"]

    sender_email = "lead@goodlife.dk"
    receiver_email = "jb@goodlife.dk"
    subject = "Test Email from Lead Tool"
    body = (
        "Hello,\n\nThis is a test email sent through Streamlit using SMTP2GO and Python."
    )

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def main():
    BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
    json_path = BASE_DIR / "assets" / "postnumre.json"
    logo_path = BASE_DIR / "assets" / "logo.png"

    # Authentication
    authenticate(logo_path)

    # Data Loading and Header
    postnumre, byer = load_data(json_path)
    display_header(logo_path)

    # Collect User Inputs
    recurring_monthly_payment, upfront_payment, duration = get_udbetaling_inputs()
    prop_value, equity, afdrag = get_bolig_inputs()
    age, postnr = get_kundeforhold_inputs(postnumre, byer)

    # Calculate and Determine Results
    df, recurring_quarterly_payment = calculate_payments(
        recurring_monthly_payment, upfront_payment, duration
    )
    besked = determine_probability(df, afdrag)

    if st.button("Beregn", type="primary", use_container_width=True):
        st.divider()
        st.header(f'Sandsynlighed: {besked}')
        st.divider()
        with st.expander("Se detaljer"):
            st.subheader("Samlet beløb")
            total_years = duration / 4
            total_payment = duration * recurring_quarterly_payment + upfront_payment
            st.metric(
                label=f'Udbetalt over {total_years:.0f} år',
                value=f'{total_payment:,} kr.'.replace(',', '.')
            )
            st.subheader("Udbetalingsprofil")
            st.dataframe(df.T.style.format(thousands="."), use_container_width=True)
            st.subheader("Illustration")
            st.bar_chart(df, color=['#295237'])

        if st.button("Send e-mail", type="primary", use_container_width=True):
            send_email()

if __name__ == "__main__":
    main()
