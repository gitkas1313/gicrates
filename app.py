import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_data(page_title="Canada GIC Rates", layout="wide")

# --- MOCK DATA (In a real app, this would come from a database or scraper) ---
if 'gic_data' not in st.session_state:
    st.session_state.gic_data = [
        {"Bank": "EQ Bank", "Term": "1 Year", "Rate": 4.50},
        {"Bank": "Tangerine", "Term": "1 Year", "Rate": 4.30},
        {"Bank": "Oaken Financial", "Term": "1 Year", "Rate": 4.60},
        {"Bank": "RBC", "Term": "1 Year", "Rate": 3.50},
        {"Bank": "TD Bank", "Term": "1 Year", "Rate": 3.45},
        {"Bank": "Scotiabank", "Term": "1 Year", "Rate": 3.40},
        {"Bank": "BMO", "Term": "1 Year", "Rate": 3.35},
    ]

if 'ads' not in st.session_state:
    st.session_state.ads = []

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .ad-space { border: 2px dashed #ccc; padding: 20px; text-align: center; margin-bottom: 20px; border-radius: 10px; background-color: #ffffff; }
    </style>
    """, unsafe_allow_type=True)

# --- MAIN PAGE ---
def main_page():
    st.title("🇨🇦 Canada GIC Rates Tracker")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")

    # --- ADVERTISING SPACE ---
    st.markdown('<div class="ad-space">', unsafe_allow_html=True)
    if st.session_state.ads:
        latest_ad = st.session_state.ads[-1]
        st.image("https://via.placeholder.com/728x90.png?text=Your+Ad+Here", use_column_width=True) # Placeholder for actual image
        st.subheader(latest_ad['caption'])
    else:
        st.write("### Your Ad Here")
        st.write("Target thousands of investors daily.")
    
    if st.button("Click to Advertise"):
        st.session_state.page = "advertise"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- GIC RATES TABLE ---
    st.subheader("Current GIC Rates (1-Year Term)")
    df = pd.DataFrame(st.session_state.gic_data)
    df = df.sort_values(by="Rate", ascending=False)
    
    # Display table
    st.table(df.style.format({"Rate": "{:.2f}%"}))

    st.info("Contact or Support: support@kaztrix.com")

# --- ADVERTISER PORTAL ---
def advertise_page():
    st.title("Advertiser Workshop")
    if st.button("← Back to Rates"):
        st.session_state.page = "main"
        st.rerun()

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Register / Create Ad")
        name = st.text_input("Company Name")
        email = st.text_input("Contact Email")
        caption = st.text_area("Ad Caption", placeholder="Enter your catchy ad text...")
        file = st.file_uploader("Upload Image or Video", type=["jpg", "png", "mp4"])
        
        plan = st.selectbox("Select Plan", [
            "30 Days ($129.00)", 
            "60 Days ($249.00)", 
            "12 Months ($1199.00)"
        ])

        if st.button("Save & Proceed to Payment"):
            if name and email and caption:
                new_ad = {"name": name, "email": email, "caption": caption, "plan": plan}
                st.session_state.ads.append(new_ad)
                st.success("Ad saved successfully!")
                st.session_state.show_payment = True
            else:
                st.error("Please fill in all fields.")

    with col2:
        if st.session_state.get('show_payment', False):
            st.subheader("2. Complete Payment")
            st.write(f"Selected Plan: **{st.session_state.ads[-1]['plan']}**")
            st.write("Please complete your payment via PayPal to finalize your order:")
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Just a placeholder
            
            paypal_link = "https://www.paypal.me/kaztrix"
            st.markdown(f'''
                <a href="{paypal_link}" target="_blank">
                    <button style="background-color: #0070ba; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px;">
                        Pay via PayPal
                    </button>
                </a>
            ''', unsafe_allow_html=True)
            
            st.info("After payment, your ad will be reviewed and published within 24 hours.")

# --- NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
    main_page()
else:
    advertise_page()
