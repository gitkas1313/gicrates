import streamlit as st
import pandas as pd
import uuid
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- CONFIGURATION ---
# Corrected: st.set_page_config instead of st.set_page_data
st.set_page_config(page_title="Canada GIC Rates", layout="wide")

# --- GLOBAL DATA SIMULATION (Users & Ads) ---
@st.cache_resource
def get_global_store():
    return {"ads": [], "users": {}, "ad_index": 0}

global_data = get_global_store()

# --- REAL GIC DATA SCRAPER ---
@st.cache_data(ttl=3600) # Refresh data every hour
def fetch_gic_data():
    url = "https://www.highinterestsavings.ca/gic-rates/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the main comparison table
        table = soup.find('table') 
        if not table:
            raise Exception("Table not found")

        rows = table.find_all('tr')
        data = []
        
        for row in rows[1:]: # Skip header
            cols = row.find_all('td')
            if len(cols) >= 2:
                bank_name = cols[0].text.strip()
                # Clean up the rate string
                rate_text = cols[1].text.replace('%', '').strip()
                try:
                    rate = float(rate_text)
                    data.append({"Bank": bank_name, "Term": "1 Year", "Rate": rate})
                except ValueError:
                    continue
        
        if not data:
            raise Exception("No data parsed")
            
        return data, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        # FALLBACK DATA if scraping fails
        fallback_data = [
            {"Bank": "Oaken Financial", "Term": "1 Year", "Rate": 4.60},
            {"Bank": "EQ Bank", "Term": "1 Year", "Rate": 4.50},
            {"Bank": "Tangerine", "Term": "1 Year", "Rate": 4.30},
            {"Bank": "RBC", "Term": "1 Year", "Rate": 3.50},
            {"Bank": "TD Bank", "Term": "1 Year", "Rate": 3.45},
        ]
        return fallback_data, f"Offline Mode (Last Attempt: {datetime.now().strftime('%H:%M:%S')})"

# --- SESSION STATE (Per User) ---
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'editing_ad' not in st.session_state:
    st.session_state.editing_ad = None

# --- STYLING ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .main { background-color: #f5f7f9; }
    .ad-container { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: white; }
    .promo-box { border: 2px solid #007bff; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px; background-color: #ffffff;}
    .timestamp { font-size: 0.8rem; color: #666; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPERS ---
def render_ad_ui(ad):
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

# --- SIDEBAR ---
st.sidebar.title("💰 GIC Tracker")
if st.session_state.logged_in_user:
    st.sidebar.write(f"User: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None
        navigate_to("Home")
    if st.sidebar.button("My Dashboard"): 
        st.session_state.editing_ad = None
        navigate_to("Dashboard")
else:
    if st.sidebar.button("Login / Register"): navigate_to("Login")

if st.sidebar.button("View GIC Rates"): navigate_to("Home")

# --- PAGE: HOME ---
if st.session_state.page == "Home":
    st.title("🇨🇦 Canada GIC Rates Tracker")
    
    # Fetch Data
    gic_list, last_updated = fetch_gic_data()
    st.markdown(f'<div class="timestamp">Market data last updated: {last_updated}</div>', unsafe_allow_html=True)
    
    # Display Active Ad
    active_ads = [ad for ad in global_data['ads'] if ad['status'] == 'Published']
    if active_ads:
        idx = global_data['ad_index'] % len(active_ads)
        render_ad_ui(active_ads[idx])
        # Auto-rotate setup
        global_data['ad_index'] += 1
        time.sleep(20)
        st.rerun()
    else:
        st.info("Your ad could be here! Click 'Advertise with Us' below.")

    if st.button("🚀 Click to Advertise"):
        navigate_to("Login")

    st.subheader("Current GIC Rates (1-Year Term)")
    df = pd.DataFrame(gic_list).sort_values(by="Rate", ascending=False)
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
                global_data['ads'] = [a for a in global_data['ads'] if a['id'] != st.session_state.editing_ad['id']]
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
                curr_cap, curr_plan = "", "30 Days ($129.00)"

            edit_caption = st.text_input("Ad Headline", value=curr_cap)
            edit_plan = st.selectbox("Select Duration", ["30 Days ($129.00)", "60 Days ($249.00)", "12 Months ($1199.00)"], 
                                     index=["30 Days ($129.00)", "60 Days ($249.00)", "12 Months ($1199.00)"].index(curr_plan))
            uploaded_file = st.file_uploader("Upload Image or Video", type=["jpg", "png", "mp4"])
            
            if st.button("Preview & Proceed"):
                if edit_caption:
                    file_bytes = uploaded_file.getvalue() if uploaded_file else None
                    file_type = uploaded_file.type if uploaded_file else None
                    if not st.session_state.editing_ad:
                        st.session_state.editing_ad = {"id": str(uuid.uuid4())[:8], "email": user_email}
                    st.session_state.editing_ad.update({"caption": edit_caption, "plan": edit_plan, "status": "Awaiting Payment", "file_bytes": file_bytes, "file_type": file_type})
                    st.session_state.show_preview = True
                    st.rerun()
                else:
                    st.error("Please enter a caption.")
            if st.session_state.editing_ad and st.button("Cancel Edit"):
                st.session_state.editing_ad = None
                st.rerun()

        with col2:
            st.subheader("Your Existing Ads")
            user_ads = [ad for ad in global_data['ads'] if ad['email'] == user_email]
            if not user_ads: st.write("No ads found.")
            for ad in user_ads:
                with st.container():
                    st.markdown(f"""<div class="ad-container"><b>ID:</b> {ad['id']} | <b>Status:</b> {ad['status']}<br><b>Text:</b> {ad['caption']}</div>""", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Edit", key=f"ed_{ad['id']}"):
                            st.session_state.editing_ad = ad
                            st.rerun()
                    with c2:
                        if st.button("Delete", key=f"del_{ad['id']}"):
                            global_data['ads'] = [a for a in global_data['ads'] if a['id'] != ad['id']]
                            st.rerun()
