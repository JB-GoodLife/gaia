import streamlit as st

# Initialize session state to track authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Password authentication function
def check_password():
    if st.session_state.password == "TestPass":
        st.session_state.authenticated = True
        # Clean up the password field from session state for security
        del st.session_state.password
        # Rerun the app to show the main content
        st.rerun()

# Login screen if not authenticated
if not st.session_state.authenticated:
    st.title("Login Required")
    
    # Simple password field
    st.text_input("Enter password", type="password", key="password", on_change=check_password)
    
    # Exit early - don't show the main app content
    st.stop()

# Main app content (only shown after authentication)
st.title("Tilbudsmodul")

st.markdown("---")

# Udbetaling (Payment) section
st.header("Udbetaling")

col1, col2, col3 = st.columns(3)

with col1:
    st.text("Månedlig udbetaling (DKK):")
    monthly_payment = st.number_input("", min_value=0, value=0, key="monthly_payment", label_visibility="collapsed")

with col2:
    st.text("Engangsudbetaling (DKK):")
    one_time_payment = st.number_input("", min_value=0, value=0, key="one_time_payment", label_visibility="collapsed")

with col3:
    st.text("Udbetalingsperiode:")
    payment_period = st.selectbox("", ["5 år"], key="payment_period", label_visibility="collapsed")

# Boligkarakteristika (Housing Characteristics) section
st.header("Boligkarakteristika")

col1, col2, col3 = st.columns(3)

with col1:
    st.text("Boligværdi (DKK):")
    property_value = st.number_input("", min_value=0, value=5000000, key="property_value", label_visibility="collapsed")

with col2:
    st.text("Friværdi (DKK):")
    equity_value = st.number_input("", min_value=0, value=3500000, key="equity_value", label_visibility="collapsed")

with col3:
    st.text("Afdrages lånet løbende?")
    repayment_loan = st.selectbox("", ["Ja"], key="repayment_loan", label_visibility="collapsed")

# Kundeforhold (Customer Relationship) section
st.header("Kundeforhold")

col1, col2, col3 = st.columns(3)

with col1:
    st.text("Yngste ejers alder")
    youngest_owner_age = st.number_input("", min_value=0, value=60, key="youngest_owner_age", label_visibility="collapsed")

with col2:
    st.text("Postnummer:")
    postal_code = st.selectbox("Skriv postnummer", [""], key="postal_code", label_visibility="collapsed")

# Add extra padding before the button
st.write("")
st.write("")

# Button at the bottom
st.button("Beregn", type="primary", use_container_width=True)

# Optional logout button (can be placed anywhere in the app)
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
