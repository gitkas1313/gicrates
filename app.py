import streamlit as st
import pandas as pd
import uuid
import time
import base64
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Canada GIC Rates", layout="wide")

# --- GLOBAL DATA SIMULATION ---
# In a real app, this would be a database. 
# We use @st.cache_resource to persist data across all user sessions.
@st.cache_resource
def get_global_data():
    return {"ads": [], "users": {}}

global_data = get_global_data()

# --- SESSION STATE (Per User) ---
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'editing_ad' not in st.session_state:
    st.session_state.editing_ad = None
if 'ad_index' not in st.session_state:
    st.session_state.ad_index = 0

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
    </style>
    """, unsafe_allow_html=True)

# --- HELPERS ---
def render_ad_ui(ad):
    """Renders an ad with support for images and videos"""
    st.markdown('<div class="promo-box">', unsafe_allow_html=True)
    st.caption("SPONSORED ADVERTISEMENT")
    
    if ad.get('file_bytes'):
        if ad['file_type'].startswith('image'):
            st.image(ad['file_bytes'], use_column_width=True)
        elif ad['file_type'].startswith('video'):
            st.video(ad['file_bytes'])
            
    st.subheader(ad['caption'])
    st.write(f"Contact: {ad['email']}")
    st.markdown('</div>', unsafe_allow_html=True)

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
    if st.sidebar.button("Logout"): logout()
    if st.sidebar.button("My Dashboard"): 
        st.session_state.editing_ad = None
        navigate_to("Dashboard")
else:
    if st.sidebar.button("Login / Register"): navigate_to("Login")

if st.sidebar.button("View GIC Rates"): navigate_to("Home")

# --- PAGE: HOME ---
if st.session_state.page == "Home":
    st.title("🇨🇦 Canada GIC Rates Tracker")
    
    active_ads = [ad for ad in global_data['ads'] if ad['status'] == 'Published']
    
    if active_ads:
        # Get current ad based on index
        idx = st.session_state.ad_index % len(active_ads)
        current_ad = active_ads[idx]
        
        # Display the ad
        ad_placeholder = st.empty()
        with ad_placeholder.container():
            render_ad_ui(current_ad)
        
        # Script to trigger refresh after 20 seconds
        time.sleep(20)
        st.session_state.ad_index += 1
        st.rerun()
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
            if lemail in global_data['users'] and global_data['users'][lemail]['password'] == lpw:
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
                global_data['users'][remail] = {"password": rpw, "name": rname}
                st.success("Account created! Please login.")
            else:
                st.error("Please fill all fields.")

# --- PAGE: DASHBOARD ---
elif st.session_state.page == "Dashboard":
    user_email = st.session_state.logged_in_user
    user_name = global_data['users'][user_email]['name']
    st.title(f"Dashboard: {user_name}")
    
    if st.session_state.get('show_preview', False):
        st.warning("### Preview Your Ad")
        render_ad_ui(st.session_state.editing_ad)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit Again"):
                st.session_state.show_preview = False
                st.rerun()
        with col2:
            st.info(f"Price: {st.session_state.editing_ad['plan'].split('(')[1].replace(')', '')}")
            st.link_button("Pay via PayPal", "https://www.paypal.me/kaztrix")
            if st.button("Confirm Payment & Publish"):
                # Remove old version if editing
                global_data['ads'] = [a for a in global_data['ads'] if a['id'] != st.session_state.editing_ad['id']]
                
                # Add new version
                st.session_state.editing_ad['status'] = "Published"
                global_data['ads'].append(st.session_state.editing_ad)
                st.session_state.editing_ad = None
                st.session_state.show_preview = False
                st.success("Success! Your ad is now live.")
                st.balloons()
                time.sleep(2)
                navigate_to("Home")
    
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.session_state.editing_ad:
                st.subheader("Edit Your Ad")
                curr_cap = st.session_state.editing_ad['caption']
                curr_plan = st.session_state.editing_ad['plan']
            else:
                st.subheader("Create New Ad")
                curr_cap = ""
                curr_plan = "30 Days ($129.00)"

            edit_caption = st.text_input("Ad Headline", value=curr_cap)
            edit_plan = st.selectbox("Select Duration", ["30 Days ($129.00)", "60 Days ($249.00)", "12 Months ($1199.00)"], 
                                     index=["30 Days ($129.00)", "60 Days ($249.00)", "12 Months ($1199.00)"].index(curr_plan))
            
            uploaded_file = st.file_uploader("Upload Image or Video", type=["jpg", "png", "mp4"])
            
            if st.button("Preview & Proceed"):
                if edit_caption:
                    file_bytes = None
                    file_type = None
                    if uploaded_file:
                        file_bytes = uploaded_file.getvalue()
                        file_type = uploaded_file.type

                    if not st.session_state.editing_ad:
                        st.session_state.editing_ad = {"id": str(uuid.uuid4())[:8], "email": user_email}
                    
                    st.session_state.editing_ad.update({
                        "caption": edit_caption, 
                        "plan": edit_plan, 
                        "status": "Awaiting Payment",
                        "file_bytes": file_bytes,
                        "file_type": file_type
                    })
                    st.session_state.show_preview = True
                    st.rerun()
                else:
                    st.error("Please enter a caption.")

        with col2:
            st.subheader("Your Ads")
            user_ads = [ad for ad in global_data['ads'] if ad['email'] == user_email]
            if not user_ads:
                st.write("No ads found.")
            for ad in user_ads:
                with st.container():
                    st.markdown(f"""<div class="ad-container">
                        <b>ID:</b> {ad['id']} | <b>Status:</b> {ad['status']}<br>
                        <b>Text:</b> {ad['caption']}<br>
                        <b>Plan:</b> {ad['plan']}
                    </div>""", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"Edit", key=f"edit_{ad['id']}"):
                            st.session_state.editing_ad = ad
                            st.rerun()
                    with c2:
                        if st.button(f"Delete", key=f"del_{ad['id']}"):
                            global_data['ads'] = [a for a in global_data['ads'] if a['id'] != ad['id']]
                            st.rerun()
