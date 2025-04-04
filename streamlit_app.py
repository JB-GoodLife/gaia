import streamlit as st

# Set page configuration (must be at the top)
st.set_page_config(page_title="Tilbudsmodul", layout="centered")

# Initialize session state for authentication.
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Create a placeholder for the login form.
login_placeholder = st.empty()

if not st.session_state["authenticated"]:
    with login_placeholder.form("login_form"):
        st.title("Skriv password")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == "TestPass":
                st.session_state["authenticated"] = True
                login_placeholder.empty()  # Remove the login form.
            else:
                st.error("Incorrect password!")

if st.session_state["authenticated"]:
    # Tilbudsmodul page content
    st.title("Tilbudsmodul")
    
    # --- Udbetaling ---
    st.subheader("Udbetaling")
    col1, col2, col3 = st.columns(3)
    with col1:
        monthly = st.number_input(
            "Månedlig udbetaling (DKK):",
            min_value=0,
            value=0,
            step=1000
        )
    with col2:
        lump_sum = st.number_input(
            "Engangsudbetaling (DKK):",
            min_value=0,
            value=0,
            step=1000
        )
    with col3:
        payout_period = st.selectbox(
            "Udbetalingsperiode:",
            ["5 år", "10 år", "15 år"],
            index=0
        )
    
    # --- Boligkarakteristika ---
    st.subheader("Boligkarakteristika")
    col4, col5, col6 = st.columns(3)
    with col4:
        boligvaerdi = st.number_input(
            "Boligværdi (DKK):",
            min_value=0,
            value=5000000,
            step=100000
        )
    with col5:
        frivaerdi = st.number_input(
            "Friværdi (DKK):",
            min_value=0,
            value=3500000,
            step=100000
        )
    with col6:
        afdrag = st.selectbox(
            "Afdrages lånet løbende?",
            ["Ja", "Nej"],
            index=0
        )
    
    # --- Kundeforhold ---
    st.subheader("Kundeforhold")
    col7, col8 = st.columns(2)
    with col7:
        alder = st.number_input(
            "Yngste ejers alder:",
            min_value=0,
            value=60,
            step=1
        )
    with col8:
        postnummer = st.text_input("Postnummer:", "")
    
    # --- Beregn button ---
    beregn = st.button("Beregn")
    if beregn:
        st.write("Beregning udført!")
