import streamlit as st
import pandas as pd
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

# --- 1. Page Configuration (Must be first) ---
st.set_page_config(page_title="Electricity Consumption Predictor", page_icon="⚡", layout="wide")

# --- 2. Premium Custom CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding-bottom: 10px; }
    .center-text { text-align: center; }
    .stTextInput>div>div>input { border-radius: 10px; background-color: rgba(255, 255, 255, 0.05); color: white; border: 1px solid rgba(255, 255, 255, 0.2); }
    .stSelectbox>div>div>div { background-color: rgba(255, 255, 255, 0.05); color: white; border-radius: 10px; }
    .stButton>button { background-image: linear-gradient(to right, #00c6ff 0%, #0072ff 100%); color: white !important; border: none; border-radius: 20px; font-weight: bold; font-size: 16px; height: 3em; width: 100%; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3); }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 114, 255, 0.5); }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 8px 8px 0px 0px; padding: 10px 20px; color: #b0bec5; }
    .stTabs [aria-selected="true"] { background-color: rgba(255, 255, 255, 0.1); border-bottom: 3px solid #00c6ff; color: white; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 5% 5% 5% 10%;
        border-radius: 10px;
        color: white;
    }
            
    div[data-testid="stAlert"] p {
        color: white !important;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Secure Database Management ---
DB_FILE = 'users.json'

SECURITY_QUESTIONS = [
    "What is the name of your first pet?",
    "In what city were you born?",
    "What is your mother's maiden name?",
    "What was the name of your first school?"
]

def load_users():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"password": "password123", "sec_q": "What is the name of your first pet?", "sec_a": "fluffy"}}
        with open(DB_FILE, 'w') as f: json.dump(default_db, f)
        return default_db
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_user(username, password, sec_q, sec_a):
    users = load_users()
    users[username] = {"password": password, "sec_q": sec_q, "sec_a": sec_a.lower().strip()}
    with open(DB_FILE, 'w') as f: json.dump(users, f)

# --- 3.1 Session Persistence Logic (The Refresh Fix!) ---
if "logged_in" in st.query_params and st.query_params["logged_in"] == "true":
    st.session_state['logged_in'] = True
    st.session_state['username'] = st.query_params.get("user", "User")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""

# --- 4. Electricity Slab Calculator ---
def calculate_bill(units):
    energy_charge = 0
    fixed_charges = 50.0 
    customer_charge = 0.0
    
    if units <= 100:
        if units <= 50:
            energy_charge = units * 1.95; customer_charge = 50.0
        else:
            energy_charge = (50 * 1.95) + ((units - 50) * 3.10); customer_charge = 70.0
    elif units <= 200:
        energy_charge = (100 * 3.40) + ((units - 100) * 4.80); customer_charge = 90.0
    else:
        if units <= 300:
            energy_charge = (200 * 5.10) + ((units - 200) * 7.70); customer_charge = 100.0
        elif units <= 400:
            energy_charge = (200 * 5.10) + (100 * 7.70) + ((units - 300) * 9.00); customer_charge = 120.0
        elif units <= 800:
            energy_charge = (200 * 5.10) + (100 * 7.70) + (100 * 9.00) + ((units - 400) * 9.50); customer_charge = 140.0
        else:
            energy_charge = (200 * 5.10) + (100 * 7.70) + (100 * 9.00) + (400 * 9.50) + ((units - 800) * 10.00); customer_charge = 160.0
        
    duty = units * 0.06 
    total_bill = energy_charge + fixed_charges + customer_charge + duty
    
    return {
        'energy': round(energy_charge, 2), 'fixed': round(fixed_charges, 2),
        'customer': round(customer_charge, 2), 'duty': round(duty, 2), 'total': round(total_bill, 2)
    }

def generate_sample_data():
    months = list(range(1, 13))
    seasons = ['Winter', 'Winter', 'Summer', 'Summer', 'Summer', 'Monsoon', 'Monsoon', 'Monsoon', 'Post-Monsoon', 'Post-Monsoon', 'Winter', 'Winter']
    temps = [22, 26, 33, 39, 42, 32, 29, 28, 29, 28, 24, 21]
    units = [75, 82, 115, 135, 150, 125, 110, 105, 100, 95, 85, 78]
    bills = [calculate_bill(u)['total'] for u in units]
    return pd.DataFrame({'Month': months, 'Season': seasons, 'Avg_Temperature': temps, 'Units_Consumed': units, 'Bill_Amount': bills})

# --- 5. Authentication ---
def login_page():
    st.write("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='center-text'>⚡ Electricity Consumption Predictor</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='center-text'>AI-Powered Energy Management & Analytics</h3><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🔄 Reset Password"])
        
        with tab1:
            st.write("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                login_user = st.text_input("Username", placeholder="Enter your username")
                login_pass = st.text_input("Password", type="password", placeholder="Enter your password")
                st.write("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Secure Login")
                
            if submit_login:
                users = load_users()
                if login_user in users and users[login_user]["password"] == login_pass:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_user
                    # Save persistence token to URL!
                    st.query_params["logged_in"] = "true"
                    st.query_params["user"] = login_user
                    st.rerun()
                else: 
                    st.error("Invalid credentials.")
                
        with tab2:
            st.write("<br>", unsafe_allow_html=True)
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                st.markdown("**Account Recovery Security**")
                sec_q = st.selectbox("Select a Security Question", SECURITY_QUESTIONS)
                sec_a = st.text_input("Your Answer", placeholder="Keep this safe!")
                st.write("<br>", unsafe_allow_html=True)
                submit_register = st.form_submit_button("Register Account")
                
            if submit_register:
                users = load_users()
                if new_user in users: st.error("Username already exists!")
                elif new_user == "" or new_pass == "" or sec_a == "": st.error("All fields are required!")
                else: 
                    save_user(new_user, new_pass, sec_q, sec_a)
                    st.success("Account created successfully! You can now login.")
                    
        with tab3:
            st.write("<br>", unsafe_allow_html=True)
            st.info("Answer your security question to verify your identity.")
            with st.form("reset_form"):
                reset_user = st.text_input("Username")
                reset_q = st.selectbox("Which Security Question did you choose?", SECURITY_QUESTIONS)
                reset_a = st.text_input("Your Answer", type="password")
                new_reset_pass = st.text_input("Enter New Password", type="password")
                st.write("<br>", unsafe_allow_html=True)
                submit_reset = st.form_submit_button("Verify & Reset Password")
            
            if submit_reset:
                users = load_users()
                if reset_user in users:
                    db_q = users[reset_user]["sec_q"]
                    db_a = users[reset_user]["sec_a"]
                    if reset_q == db_q and reset_a.lower().strip() == db_a:
                        save_user(reset_user, new_reset_pass, db_q, db_a)
                        st.success("Identity verified. Password reset successfully!")
                    else: st.error("Verification failed. Incorrect question or answer.")
                elif reset_user == "": st.warning("Please enter your username.")
                else: st.error("Username not found.")

# --- 6. MULTI-PAGE ROUTING SYSTEM ---

def page_predictor(dataset, model):
    st.markdown("<h1>🔮 AI Prediction Engine</h1>", unsafe_allow_html=True)
    st.write("Leverage Random Forest Machine Learning to forecast your upcoming electricity costs.")
    st.write("---")
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    with st.form("prediction_form"):
        selected_month_idx = st.selectbox("1. Select Upcoming Month to Predict", range(1, 13), format_func=lambda x: month_names[x-1])
        
        month_data = dataset[dataset['Month'] == selected_month_idx]
        if not month_data.empty:
            auto_temp = month_data['Avg_Temperature'].mean()
            auto_season_code = month_data['Season_Code'].mode()[0]
            auto_season_name = month_data['Season'].mode()[0]
        else:
            auto_temp = dataset['Avg_Temperature'].mean()
            auto_season_code = dataset['Season_Code'].mode()[0]
            auto_season_name = dataset['Season'].mode()[0]
        
        st.info(f"Historical data shows {auto_season_name} averages around **{auto_temp:.1f}°C**.")
        expected_temp = st.slider("2. Adjust Expected Temperature (°C)", min_value=15.0, max_value=50.0, value=float(auto_temp), step=0.5)
        
        submit_button = st.form_submit_button("Analyze & Predict Next Bill")

    if submit_button:
        input_data = pd.DataFrame({'Avg_Temperature': [expected_temp], 'Season_Code': [auto_season_code]})
        predicted_units = model.predict(input_data)[0]
        bill_details = calculate_bill(predicted_units)
        
        st.info(f"⚡ **AI Predicted Consumption:** {predicted_units:.0f} Units")
        st.markdown("#### 🧾 Estimated Bill Breakdown")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Energy Charge", f"₹{bill_details['energy']:.2f}")
        m2.metric("Fixed Charges", f"₹{bill_details['fixed']:.2f}")
        m3.metric("Customer Charges", f"₹{bill_details['customer']:.2f}")
        m4.metric("Electricity Duty", f"₹{bill_details['duty']:.2f}")
        
        st.success(f"### 💰 Total Estimated Bill: ₹{bill_details['total']:.2f}")

def page_analytics(dataset):
    st.markdown("<h1>📊 Advanced Analytics</h1>", unsafe_allow_html=True)
    st.write("Visualize your historical consumption trends and billing data.")
    st.write("---")
    
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    fig2.patch.set_facecolor('#1a1a1a')
    ax2.set_facecolor('#1a1a1a')
    ax2.tick_params(colors='white')
    ax2.xaxis.label.set_color('white')
    ax2.yaxis.label.set_color('white')
    ax2.title.set_color('white')
    for spine in ax2.spines.values(): spine.set_edgecolor('#4facfe')
    ax2.plot(dataset['Month'], dataset['Units_Consumed'], marker='o', linestyle='-', color='#00f2fe', linewidth=2)
    ax2.set_title("Monthly Unit Consumption Trends")
    ax2.set_xlabel("Month (1-12)")
    ax2.set_ylabel("Units Consumed")
    ax2.set_xticks(dataset['Month']) 
    ax2.grid(True, alpha=0.1, color='white')
    st.pyplot(fig2)
    
    st.write("---")
    st.markdown("### 🗃️ Raw Historical Data")
    st.dataframe(dataset, use_container_width=True)

def page_profile():
    st.markdown("<h1>⚙️ Account Settings</h1>", unsafe_allow_html=True)
    st.write("Manage your user profile and application settings.")
    st.write("---")
    st.info(f"👤 **Logged in as:** {st.session_state['username']}")
    st.write("You are currently using the AI-Powered Energy Management system with a secure JSON database connection.")
    
    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("Logout of Application", type="primary"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        # Wipe the token out of the URL to actually log them out!
        st.query_params.clear()
        st.rerun()

# --- Main App Controller ---
def main_app():
    # 1. Global Sidebar Navigation
    with st.sidebar:
        st.markdown(f"<h2>Hello, {st.session_state['username']}! 👋</h2>", unsafe_allow_html=True)
        st.write("---")
        
        selected_page = option_menu(
            menu_title="Navigation",
            options=["Predictor", "Analytics", "Profile"],
            icons=["lightning", "bar-chart-line", "person-gear"],
            menu_icon="compass",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#00c6ff", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px 0px",
                    "--hover-color": "rgba(255,255,255,0.05)",
                    "border-radius": "8px",
                    "color": "white"
                },
                "nav-link-selected": {
                    "background-color": "rgba(0, 198, 255, 0.2)",
                    "border": "1px solid #00c6ff",
                    "color": "white",
                    "font-weight": "bold"
                },
            }
        )
        
        st.write("---")
        st.markdown("### 📂 Global Data Source")
        uploaded_file = st.file_uploader("Upload your completed CSV", type=["csv"])
        
        # --- FIXED: Explicit instructions added back to the sidebar! ---
        with st.expander("ℹ️ How to use the template", expanded=True):
            st.markdown("""
            1. **Download** the template below.
            2. **Open it** (in Excel or Notepad).
            3. **Replace** the dummy numbers with your **actual** data.
            4. **Save & Upload** it above.
            """)
            sample_df = generate_sample_data()
            @st.cache_data
            def convert_df(df): return df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Realistic Template", convert_df(sample_df), "electricity_bills.csv", "text/csv")

    # 2. Page Routing Logic
    if selected_page == "Profile":
        page_profile()
    else:
        if uploaded_file:
            dataset = pd.read_csv(uploaded_file)
            dataset['Season_Code'] = dataset['Season'].astype('category').cat.codes
            X = dataset[['Avg_Temperature', 'Season_Code']]
            y = dataset['Units_Consumed']
            model = RandomForestRegressor(n_estimators=100, random_state=42) 
            model.fit(X, y)
            
            # Route to the correct data page
            if selected_page == "Predictor":
                page_predictor(dataset, model)
            elif selected_page == "Analytics":
                page_analytics(dataset)
        else:
            # --- FIXED: Upgraded Welcome Screen with clear onboarding steps ---
            st.markdown("<h1 class='center-text'>⚡ Welcome to Electricity Consumption Predictor</h1>", unsafe_allow_html=True)
            st.write("---")
            
            st.markdown("""
            ### 🚀 Let's get started!
            To generate highly accurate, AI-powered predictions, the engine needs to learn from your unique historical consumption habits.
            
            **How to begin:**
            1. Look at the **Global Data Source** section in the sidebar.
            2. If you don't have a dataset yet, expand the **'How to use the template'** section.
            3. Download the realistic template file.
            4. ⚠️ **CRITICAL:** Open the file and replace the sample numbers with your actual monthly usage and temperatures.
            5. Upload your updated CSV file.
            """)
            
            st.info("🔓 *Once your custom data is uploaded, the Predictor and Analytics dashboards will automatically unlock!*")

# --- Run App ---
if st.session_state['logged_in']: main_app()
else: login_page()