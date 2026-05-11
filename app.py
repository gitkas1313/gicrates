import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Canada GIC Rates", layout="wide")

# --- DATA INITIALIZATION (Simulating a Database) ---
if 'users' not in st.session_state:
    st.session_state.users = {} 
if 'ads' not in st.session_state:
    st.session_state.ads = [] 
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'editing_ad' not in st.session_state:
    st.session_state.editing_ad = None # Stores ad being created/previewed

# --- MOCK GIC DATA ---
GIC_DATA = [
    {"Bank": "Oaken Financial", "Term": "1 Year", "Rate": 4.60},
    {"Bank": "EQ Bank", "Term": "1 Year", "Rate": 4.50},
    {"Bank": "Tangerine", "Term": "1 Year", "Rate": 4.30},
    {"Bank": "RBC", "Term": "1 Year", "Rate": 3.50},
    {"Bank": "TD Bank", "Term": "1 Year", "Rate": 3.45},
    {"Bank": "Scotiabank", "Term": "1 Year", "Rate": 3.40},
    {"Bank": "BMO", "Term": "1 Year", "Rate": 3.35},
]

# --- STYLING ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .main { background-color: #f5f7f9; }
    .ad-container { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: white; }
    .promo-box { border: 2px solid #007bff; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px; background-color: #ffffff;}
    .preview-label { color: #f63366; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; font-size: 0.8rem;}
    </style>
    """, unsafe_allow_html=True)

# --- COMPONENTS ---
def render_ad_ui(caption, email):
    """Renders the ad as it appears on the homepage"""
    st.markdown(f"""
        <div class="promo-box">
            <small style="color: #666;">SPONSORED ADVERTISEMENT</small>
            <h3>{caption}</h3>
            <p>Contact: {email}</p>
        </div>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
def navigate_to(page):
    st.session_state.page = page
    st.rerun()

def logout():
    st.session_state.logged_in_user = None
    navigate_to("Home")

# --- SIDEBAR ---
st.sidebar.title("💰 GIC Tracker")
if st.session_state.logged_in_user:
    st.sidebar.write(f"User: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("My Dashboard"): navigate_to("Dashboard")
    if st.sidebar.button("Logout"): logout()
else:
    if st.sidebar.button("Login / Register"): navigate_to("Login")

if st.sidebar.button("View GIC Rates"): navigate_to("Home")

# --- PAGE: HOME ---
if st.session_state.page == "Home":
    st.title("🇨🇦 Canada GIC Rates Tracker")
    
    # Display Active Ad
    active_ads = [ad for ad in st.session_state.ads if ad['status'] == 'Published']
    if active_ads:
        latest = active_ads[-1]
        render_ad_ui(latest['caption'], latest['email'])
    else:
        st.info("Your ad could be here! Click 'Advertise with Us' below.")

    if st.button("🚀 Click to Advertise"):
        navigate_to("Login")

    st.subheader("Current GIC Rates (1-Year Term)")
    df = pd.DataFrame(GIC_DATA).sort_values(by="Rate", ascending=False)
    st.table(df.style.format({"Rate": "{:.2f}%"}))
    st.info("Contact or Support: support@kaztrix.com")

# --- PAGE: LOGIN / REGISTER ---
elif st.session_state.page == "Login":
    st.title("Advertiser Access")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        lemail = st.text_input("Email", key="login_email")
        lpw = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            if lemail in st.session_state.users and st.session_state.users[lemail]['password'] == lpw:
                st.session_state.logged_in_user = lemail
                navigate_to("Dashboard")
            else:
                st.error("Invalid credentials")
                
    with tab2:
        rname = st.text_input("Company Name")
        remail = st.text_input("Email")
        rpw = st.text_input("Password", type="password")
        if st.button("Create Account"):
            if remail and rpw:
                st.session_state.users[remail] = {"password": rpw, "name": rname}
                st.success("Account created! Please login.")
            else:
                st.error("Please fill all fields.")

# --- PAGE: DASHBOARD ---
elif st.session_state.page == "Dashboard":
    user_email = st.session_state.logged_in_user
    user_name = st.session_state.users[user_email]['name']
    st.title(f"Dashboard: {user_name}")
    
    # CASE 1: Previewing an Ad
    if st.session_state.editing_ad:
        st.warning("### 1. Preview Your Ad")
        st.write("This is exactly how your ad will appear to visitors:")
        render_ad_ui(st.session_state.editing_ad['caption'], user_email)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit Ad"):
                st.session_state.editing_ad = None
                st.rerun()
        with col2:
            st.info(f"Price: {st.session_state.editing_ad['plan'].split('(')[1].replace(')', '')}")
            st.link_button("2. Pay via PayPal", "https://www.paypal.me/kaztrix")
            if st.button("3. I've Paid, Publish My Ad!"):
                st.session_state.editing_ad['status'] = "Published"
                st.session_state.ads.append(st.session_state.editing_ad)
                st.session_state.editing_ad = None
                st.success("Success! Your ad is now live.")
                st.balloons()
                # st.sleep(2)
                st.rerun()

    # CASE 2: Normal Dashboard View
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Create New Ad")
            new_caption = st.text_input("Ad Headline/Caption", placeholder="e.g. Best Mortgage Rates in Toronto!")
            new_plan = st.selectbox("Select Duration", ["30 Days ($129.00)", "60 Days ($249.00)", "12 Months ($1199.00)"])
            if st.button("Preview Ad"):
                if new_caption:
                    st.session_state.editing_ad = {
                        "id": str(uuid.uuid4())[:8],
                        "email": user_email,
                        "caption": new_caption,
                        "plan": new_plan,
                        "status": "Awaiting Payment"
                    }
                    st.rerun()
                else:
                    st.error("Please enter a caption.")

        with col2:
            st.subheader("Your Active/Past Ads")
            user_ads = [ad for ad in st.session_state.ads if ad['email'] == user_email]
            if not user_ads:
                st.write("No ads found.")
            for ad in user_ads:
                with st.container():
                    st.markdown(f"""<div class="ad-container">
                        <b>Status:</b> {ad['status']}<br>
                        <b>Text:</b> {ad['caption']}<br>
                        <b>Plan:</b> {ad['plan']}
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"Remove Ad {ad['id']}"):
                        st.session_state.ads = [a for a in st.session_state.ads if a['id'] != ad['id']]
                        st.rerun()
