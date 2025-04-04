import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Set page configuration (must be at the top)
st.set_page_config(page_title="Tilbudsmodul", layout="centered")

# Decide on base directory (fallback if __file__ is missing)
if "__file__" in globals():
    BASE_DIR = Path(__file__).parent
else:
    # Fallback to current working directory
    BASE_DIR = Path.cwd()

json_path = BASE_DIR / "assets" / "postnumre.json"
logo_path = BASE_DIR / "assets" / "logo.png"

# Initialize session state for authentication.
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Create a placeholder for the login form.
login_placeholder = st.empty()

if not st.session_state["authenticated"]:
    with login_placeholder.form("login_form"):
        st.title("Skriv password (v3)")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == "TestPass":
                st.session_state["authenticated"] = True
                login_placeholder.empty()  # Remove the login form.
            else:
                st.error("Incorrect password!")

if st.session_state["authenticated"]:
    # --- Main App Code ---
    # Read the JSON data
    with open(json_path, encoding='utf-8') as data_file:
        data = pd.DataFrame(json.load(data_file))
    
    postnumre = data["nr"]
    byer = dict(zip(data['nr'], data['navn']))
    
    # Add logos
    left_co, cent_co, right_co = st.columns(3)
    with cent_co:
        st.image(str(logo_path))
    st.markdown('##')
    
    # App title with version counter
    st.title("Tilbudsmodul v3")
    st.divider()
    
    # Input row 1
    st.write("**Udbetaling**")
    left_co, cent_co, right_co = st.columns(3)
    with left_co:
        recurring_monthly_payment = st.number_input("Månedlig udbetaling (DKK):", min_value=0, step=500, format="%d")
    with cent_co:
        upfront_payment = st.number_input("Engangsudbetaling (DKK):", min_value=0, step=500)
    with right_co:
        duration_options = [("5 år", 20), ("10 år", 40)]
        duration = st.selectbox(
            "Udbetalingsperiode:",
            options=duration_options,
            format_func=lambda x: x[0]
        )[1]
    
    st.write("")
    
    # Input form row 2
    st.write("**Boligkarakteristika**")
    left_co, cent_co, right_co = st.columns(3)
    with left_co:
        prop_value = st.number_input("Boligværdi (DKK):", min_value=0, step=5000, value=5000000)
    with cent_co:
        equity = st.number_input("Friværdi (DKK):", min_value=0, step=5000, value=3500000)
    with right_co:
        debt_options = [("Ja", True), ("Nej", False)]
        afdrag = st.selectbox(
            "Afdrages lånet løbende?",
            options=debt_options,
            format_func=lambda x: x[0]
        )[1]
    
    st.write("")
    
    # Setup postnummer input field and corresponding city field
    st.write("**Kundeforhold**")
    left_co, cent_co, right_co = st.columns(3)
    with left_co:
        st.number_input(label="Alder", step=1, min_value=60)
    with cent_co:
        postnr = st.selectbox(
            "Postnummer:",
            postnumre,
            index=None,
            placeholder="Skriv postnummer",
        )
    with right_co:
        st.text_input(label="", placeholder=byer.get(postnr, ""), disabled=True)
    
    st.write("")
    
    # Calculate quarterly payment from monthly payment
    recurring_quarterly_payment = recurring_monthly_payment * 3
    
    # Generate the DataFrame
    quarters = [f"Q{i}" for i in range(1, duration + 1)]
    payments = [recurring_quarterly_payment] * duration
    payments[0] += upfront_payment  # Add the upfront payment to the first quarter
    
    df = pd.DataFrame([payments], columns=quarters, index=["Udbetaling"])
    
    # Ensure quarters are sorted correctly for visualization
    df = df.T
    df.index = pd.Categorical(df.index, categories=quarters, ordered=True)
    df = df.sort_index()
    
    # Simple logic for demonstration
    if (sum(df["Udbetaling"]) < 1500000) & afdrag:
        besked = ":green[Høj]"
    else:
        besked = ":red[Lav]"
    
    st.write("")
    if st.button(label="Beregn", type="primary", use_container_width=True, key="Beregn"):
        st.divider()
        st.header(f'Sandsynlighed: {besked}')
        st.divider()
        with st.expander("Se detaljer"):
            st.subheader("Samlet beløb")
            st.metric(
                label=f'Udbetalt over {duration/4:.0f} år',
                value=f'{duration*recurring_quarterly_payment+upfront_payment:,} kr.'.replace(',', '.')
            )
            df_t = df.T
            st.subheader("Udbetalingsprofil")
            st.dataframe(df_t.style.format(thousands="."), use_container_width=True)
            st.subheader("Illustration")
            st.bar_chart(df, color=['#295237'])
