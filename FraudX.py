import streamlit as st
import sqlite3
import hashlib
import time
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# --------------------------
# Database Setup
# --------------------------
def init_db():
    conn = sqlite3.connect('fraudcases.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  password TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Cases table 
    c.execute('''CREATE TABLE IF NOT EXISTS cases
                 (case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  case_name TEXT NOT NULL,
                  case_type TEXT,
                  status TEXT DEFAULT 'Open',
                  description TEXT,
                  location TEXT,
                  amount_involved REAL,
                  currency TEXT DEFAULT 'USD',
                  date_detected DATE,
                  date_reported DATE,
                  date_resolved DATE,
                  parties_involved TEXT,
                  investigation_agency TEXT,
                  court_reference TEXT,
                  source_url TEXT,
                  created_by TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  severity TEXT CHECK(severity IN ('Low', 'Medium', 'High', 'Critical')),
                  FOREIGN KEY(created_by) REFERENCES users(username))''')
    
    # Case categories 
    c.execute('''CREATE TABLE IF NOT EXISTS case_categories
                 (category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category_name TEXT UNIQUE,
                  description TEXT)''')
    
    
    c.execute("SELECT COUNT(*) FROM case_categories")
    if c.fetchone()[0] == 0:
        categories = [
            ('Ponzi Scheme', 'Investment fraud promising high returns'),
            ('Insurance Fraud', 'False claims or deliberate damage'),
            ('Bank Fraud', 'Fraud involving banking systems'),
            ('Identity Theft', 'Using someone else\'s identity'),
            ('Cyber Fraud', 'Online scams and hacking'),
            ('Public Sector Fraud', 'Government-related corruption'),
            ('Corporate Fraud', 'Company financial misrepresentation'),
            ('Tax Evasion', 'Illegal avoidance of tax payments'),
            ('Money Laundering', 'Processing illicit funds'),
            ('Procurement Fraud', 'Bid rigging, kickbacks in purchasing')
        ]
        c.executemany("INSERT INTO case_categories (category_name, description) VALUES (?, ?)", categories)
    
    
    c.execute("SELECT COUNT(*) FROM cases")
    if c.fetchone()[0] == 0:
        # Zimbabwean fraud cases - recent and historical
        fraud_cases = [
            ("Zimbabwe Gold Scam 2023", "Ponzi Scheme", "Investors defrauded in fake gold scheme", 
             "Harare", 2500000, "USD", "2023-05-15", "2023-06-01", None, 
             "XYZ Investment, ABC Bank", "ZRP Commercial Crimes", "HC 1234/23", 
             "https://www.zimbabwesituation.com/news/gold-scam", "admin", "High"),
            
            ("NSSA Pension Fraud", "Public Sector Fraud", "Misuse of pension funds", 
             "Nationwide", 50000000, "USD", "2018-01-01", "2019-03-15", "2022-08-20", 
             "NSSA officials", "ZACC", "HC 5678/19", 
             "https://www.newsday.co.zw/nssa-scandal", "admin", "Critical"),
            
            ("BancABC Internal Fraud", "Bank Fraud", "Employee siphoned client funds", 
             "Bulawayo", 120000, "USD", "2022-11-10", "2022-11-15", "2023-02-28", 
             "Bank employee", "Internal Audit", "MC 9012/22", 
             None, "admin", "Medium"),
            
            ("Harare City Housing Scam", "Public Sector Fraud", "Illegal sale of council land", 
             "Harare", 3500000, "USD", "2020-07-01", "2021-01-10", None, 
             "Council officials, Developers", "ZACC", "HC 3456/21", 
             "https://www.herald.co.zw/city-housing-scam", "admin", "High"),
            
            ("EcoCash Fraud Ring", "Cyber Fraud", "SIM swap fraud targeting mobile money", 
             "Nationwide", 850000, "USD", "2021-03-01", "2021-04-15", "2022-05-10", 
             "15 suspects", "ZRP Cyber Crime", "HC 7890/21", 
             "https://www.techzim.co.zw/ecocash-fraud", "admin", "High"),
            
            ("ZIMRA Tax Evasion", "Tax Evasion", "Undervaluation of imports", 
             "Beitbridge", 12000000, "USD", "2019-05-01", "2020-02-20", "2021-11-15", 
             "Clearing agents, Businesses", "ZIMRA", "HC 2345/20", 
             "https://www.chronicle.co.zw/zimra-case", "admin", "Critical"),
            
            ("Cottco Manager Fraud", "Corporate Fraud", "Ghost workers payroll fraud", 
             "Gweru", 450000, "USD", "2022-02-01", "2022-03-10", "2022-09-30", 
             "HR Manager", "Internal Audit", None, 
             None, "admin", "Medium"),
            
            ("COVID-19 Fund Misuse", "Public Sector Fraud", "Diverted pandemic relief funds", 
             "Nationwide", 3000000, "USD", "2020-06-01", "2021-01-05", None, 
             "Govt officials", "ZACC", "HC 6789/21", 
             "https://www.newzimbabwe.com/covid-funds", "admin", "High"),
            
            ("ZSE Insider Trading", "Corporate Fraud", "Illegal share trading", 
             "Harare", 1800000, "USD", "2021-07-01", "2021-09-15", "2022-04-20", 
             "Stockbrokers, Executives", "SECZ", "HC 1234/21", 
             "https://www.businessweekly.co.zw/zse-case", "admin", "High"),
            
            ("Fuel Coupon Scam", "Procurement Fraud", "Fraudulent fuel procurement", 
             "Nationwide", 7500000, "USD", "2017-01-01", "2018-03-01", "2020-12-15", 
             "Govt officials, Suppliers", "ZACC", "HC 4567/18", 
             "https://www.sundaymail.co.zw/fuel-scam", "admin", "Critical")
        ]
        
        
        additional_cases = [
            ("Chinhoyi Ponzi Scheme 2025", "Ponzi Scheme", "Investors promised high returns", 
             "Chinhoyi", 197300, "USD", "2025-04-15", "2025-04-20", None, 
             "2 suspects", "ZRP Commercial Crimes", "CRB 1234/25", 
             "https://lawportalzim.co.zw/cases/criminal/213/fraud-and-criminal-promise", "admin", "High"),
            
            ("Insurance Fraud Harare", "Insurance Fraud", "False claims submission", 
             "Harare", 1000000, "ZWL", "2025-04-10", "2025-04-12", None, 
             "Insurance client", "Insurance Council", "CRB 5678/25", 
             "https://lawportalzim.co.zw/cases/criminal/215/insurance-fraud", "admin", "Medium"),
            
            ("Fake ID Syndicate", "Identity Theft", "Production of fake IDs", 
             "Bulawayo", 0, "USD", "2025-04-05", "2025-04-08", None, 
             "5 suspects", "ZRP CID", "CRB 9012/25", 
             "https://lawportalzim.co.zw/cases/criminal/217/fake-ids", "admin", "High"),
            
            ("Forex Fraud Harare", "Bank Fraud", "Illegal forex trading", 
             "Harare", 322000, "USD", "2025-03-28", "2025-04-01", None, 
             "Forex dealer", "RBZ Financial Intelligence", "CRB 3456/25", 
             "https://lawportalzim.co.zw/cases/criminal/219/forex-fraud", "admin", "Critical"),
            
            ("Health Insurance Fraud", "Insurance Fraud", "False medical claims", 
             "Nationwide", 0, "USD", "2025-03-20", "2025-03-25", None, 
             "Medical providers", "Insurance Council", None, 
             "https://lawportalzim.co.zw/cases/criminal/221/health-fraud", "admin", "Medium"),
            
            # Historical cases from Zimbabwe
            ("Zimbabwe Housing Scam 2000s", "Public Sector Fraud", "Illegal land allocations", 
             "Harare", 50000000, "USD", "2005-01-01", "2007-03-15", "2010-12-20", 
             "Government officials", "ZACC", "HC 1234/07", 
             "https://www.herald.co.zw/housing-scandal", "admin", "Critical"),
            
            ("Zimbabwe Bank Closure 2004", "Bank Fraud", "Bank collapse due to fraud", 
             "Nationwide", 300000000, "USD", "2004-01-01", "2004-03-01", "2006-05-15", 
             "Bank executives", "RBZ", "HC 5678/04", 
             "https://www.financialgazette.co.zw/bank-collapse", "admin", "Critical"),
            
            ("Zimbabwe Diamond Fraud", "Public Sector Fraud", "Diamond revenue leakages", 
             "Marange", 2000000000, "USD", "2008-01-01", "2012-03-01", None, 
             "Mining companies, Officials", "ZACC", "HC 9012/12", 
             "https://www.zimbabwesituation.com/diamond-report", "admin", "Critical"),
            
            ("Zimbabwe Command Agric", "Public Sector Fraud", "Misuse of farming inputs", 
             "Nationwide", 3000000000, "USD", "2016-01-01", "2019-01-01", None, 
             "Govt officials, Suppliers", "ZACC", "HC 3456/19", 
             "https://www.newsday.co.zw/command-agric", "admin", "Critical"),
            
            ("Zimbabwe Fuel Scam 2019", "Procurement Fraud", "Fraudulent fuel imports", 
             "Nationwide", 1500000000, "USD", "2019-01-01", "2019-07-01", None, 
             "Fuel companies, Officials", "ZACC", "HC 7890/19", 
             "https://www.sundaymail.co.zw/fuel-imports", "admin", "Critical"),
            
            # Regional cases
            ("VBS Bank Heist SA", "Bank Fraud", "Looting of municipal funds", 
             "South Africa", 2000000000, "ZAR", "2016-01-01", "2018-03-01", "2021-06-15", 
             "Bank executives", "Hawks", "GPV 1234/18", 
             "https://www.dailymaverick.co.za/vbs-bank", "admin", "Critical"),
            
            ("Steinhoff Scandal", "Corporate Fraud", "Accounting irregularities", 
             "South Africa", 10000000000, "ZAR", "2015-01-01", "2017-12-01", None, 
             "Company executives", "JSE", "GPV 5678/17", 
             "https://www.businesslive.co.za/steinhoff", "admin", "Critical"),
            
            ("Tongaat Hulett Fraud", "Corporate Fraud", "Revenue overstatement", 
             "South Africa", 6500000000, "ZAR", "2014-01-01", "2019-05-01", "2022-03-15", 
             "Company executives", "JSE", "GPV 9012/19", 
             "https://www.moneyweb.co.za/tongaat", "admin", "Critical"),
            
            ("Eswatini Health Fraud", "Public Sector Fraud", "COVID funds misappropriation", 
             "Eswatini", 250000000, "SZL", "2020-06-01", "2021-03-01", None, 
             "Health officials", "Anti-Corruption", "HC 2345/21", 
             "https://www.times.co.sz/health-scandal", "admin", "High"),
            
            ("Zambia Fire Tender Scam", "Procurement Fraud", "Overpriced fire trucks", 
             "Zambia", 42000000, "USD", "2017-01-01", "2018-01-01", "2020-06-15", 
             "Govt officials", "ACC", "HC 6789/18", 
             "https://www.lusakatimes.com/fire-tenders", "admin", "High"),
            
            ("Malawi Cashgate", "Public Sector Fraud", "Looting of govt funds", 
             "Malawi", 32000000, "USD", "2013-01-01", "2013-09-01", "2016-12-15", 
             "Civil servants", "ACB", "HC 1234/13", 
             "https://www.nyasatimes.com/cashgate", "admin", "Critical"),
            
            ("Namibia Fishrot", "Public Sector Fraud", "Fishing quotas corruption", 
             "Namibia", 150000000, "NAD", "2014-01-01", "2019-11-01", None, 
             "Ministers, Businessmen", "ACU", "HC 5678/19", 
             "https://www.namibian.com.na/fishrot", "admin", "Critical"),
            
            ("Botswana Housing Scam", "Public Sector Fraud", "Irregular land allocation", 
             "Botswana", 50000000, "BWP", "2018-01-01", "2019-03-01", "2021-06-15", 
             "Council officials", "DCEC", "HC 9012/19", 
             "https://www.mmegi.bw/housing-scam", "admin", "High"),
            
            ("Mozambique Tuna Bonds", "Public Sector Fraud", "Hidden govt debt", 
             "Mozambique", 2000000000, "USD", "2013-01-01", "2016-04-01", None, 
             "Govt officials, Bankers", "Public Prosecutor", "HC 3456/16", 
             "https://www.zitamar.com/tuna-bonds", "admin", "Critical"),
            
            ("Kenya NYS Scandal", "Public Sector Fraud", "Theft of youth funds", 
             "Kenya", 800000000, "KES", "2015-01-01", "2018-05-01", None, 
             "Govt officials", "EACC", "HC 7890/18", 
             "https://www.nation.co.ke/nys", "admin", "Critical")
        ]
        
        # Insert all cases
        for case in fraud_cases + additional_cases:
            c.execute('''INSERT INTO cases 
                        (case_name, case_type, description, location, amount_involved, currency, 
                         date_detected, date_reported, date_resolved, parties_involved, 
                         investigation_agency, court_reference, source_url, created_by, severity)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', case)
    
    conn.commit()
    conn.close()

# --------------------------
# Case Management Functions
# --------------------------
def get_all_cases():
    conn = sqlite3.connect('fraudcases.db')
    df = pd.read_sql("SELECT * FROM cases ORDER BY date_reported DESC", conn)
    conn.close()
    return df

def get_case_types():
    conn = sqlite3.connect('fraudcases.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT case_type FROM cases")
    types = [row[0] for row in c.fetchall()]
    conn.close()
    return types

def add_new_case(case_data):
    conn = sqlite3.connect('fraudcases.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO cases 
                    (case_name, case_type, description, location, amount_involved, currency,
                     date_detected, date_reported, date_resolved, parties_involved,
                     investigation_agency, court_reference, source_url, created_by, severity)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  case_data)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding case: {str(e)}")
        return False
    finally:
        conn.close()


def make_hashes(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text


def create_user(username, password):
    try:
        conn = sqlite3.connect('fraudcases.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?,?)', 
                  (username, make_hashes(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    conn = sqlite3.connect('fraudcases.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    return data is not None and check_hashes(password, data[0])

# --------------------------
# UI Components
# --------------------------
def apply_custom_styles():
    st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Input field styling */
    .stTextInput input, .stTextInput input:focus,
    .stTextInput input:hover {
        background-color: #ffffff !important;
        border: 1px solid #e1e5eb !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
        transition: all 0.3s ease;
        font-weight: 500 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f0c29, #302b63, #24243e) !important;
        color: white !important;
        padding: 1.5rem 1rem !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4,
    [data-testid="stSidebar"] .stMarkdown h5,
    [data-testid="stSidebar"] .stMarkdown h6 {
        color: white !important;
    }
    
    /* Card styling */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border-left: 3px solid transparent;
    }
    
    .sidebar-card:hover {
        background: rgba(255, 255, 255, 0.2);
        border-left: 3px solid #667eea;
        transform: translateX(5px);
    }
    
    .sidebar-card.active {
        background: rgba(255, 255, 255, 0.25);
        border-left: 3px solid #667eea;
    }
    
    .sidebar-card .emoji {
        font-size: 1.2rem;
        margin-right: 0.8rem;
    }
    
    .sidebar-card .title {
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .sidebar-card .coming-soon {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 0.2rem;
    }
    
    /* Main content cards */
    .content-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.03);
    }
    
    /* Logo styling */
    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Logout button */
    .logout-btn {
        position: absolute;
        bottom: 2rem;
        width: calc(100% - 2rem);
    }
    
    .logout-btn .stButton>button {
        background: linear-gradient(135deg, #ff4d4d 0%, #f94444 100%) !important;
        width: 100%;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.3);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.4);
    }
    
    /* Login page specific */
    .login-container {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        max-width: 500px;
        margin: 2rem auto;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    .login-header p {
        color: #6c757d;
        font-size: 0.95rem;
    }
    
    .login-tabs .stTabs [data-baseweb="tab-list"] {
        gap: 0;
    }
    
    .login-tabs .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 2rem;
        background: transparent !important;
        color: #6c757d !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.3s ease;
    }
    
    .login-tabs .stTabs [data-baseweb="tab"]:hover {
        color: #495057 !important;
    }
    
    .login-tabs .stTabs [aria-selected="true"] {
        color: #764ba2 !important;
        border-bottom: 2px solid #764ba2 !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    with st.sidebar:
        selected = option_menu(
            "Navigation", 
            ["Launch Pad", "Summary Dashboard", "Case Builder", "Case Analysis", "Reports"],
            icons=["house", "bar-chart", "clipboard", "search", "file-earmark"],
            menu_icon="cast", 
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#0f0c29"},
                "icon": {"color": "white", "font-size": "16px"}, 
                "nav-link": {"color":"white", "font-size": "16px", "text-align": "left", "margin":"0px"},
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
        st.session_state['current_page'] = selected
    
        
        # Logout button at the bottom
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("❌ Sign Out", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def login_page():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    }
    .login-header {
        text-align: center;
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 4rem;
        margin-bottom: 0.5rem;
    }
    .login-sub {
        text-align: center;
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-header">🔐 Welcome to FraudCaseX</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Forensic Case Management Portal – Securely log in or create your account below.</div>', unsafe_allow_html=True)

    login_tab, signup_tab = st.tabs(["🔑 Login", "🆕 Register"])

    with login_tab:
        with st.form("Login Form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if authenticate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with signup_tab:
        with st.form("Signup Form"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")

            if st.form_submit_button("Register"):
                if not new_user:
                    st.error("Username cannot be empty")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match")
                else:
                    if create_user(new_user, new_pass):
                        st.success("Account created! You can now log in.")
                    else:
                        st.error("Username already exists")

def launch_pad():
    st.markdown("""
    <style>
    .welcome-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .welcome-subheader {
        font-size: 1.2rem;
        color: #6c757d;
        margin-bottom: 2rem;
    }

    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    .feature-card h3 {
        margin-top: 0;
        color: #343a40;
    }

    .feature-card p {
        color: #6c757d;
        margin-bottom: 0;
    }

    .feature-card .emoji {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="welcome-header">Welcome to FraudCaseX</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-subheader">Automating the Fight Against Financial Fraud</div>', unsafe_allow_html=True)

    st.markdown("""
    FraudCaseX is a comprehensive forensic case management platform designed to help investigators 
    streamline fraud detection, case building, and analysis workflows. Our system brings automation 
    and advanced analytics to forensic accounting and fraud examination.
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="emoji">🔍</div>
            <h3>Case Analysis</h3>
            <p>Advanced tools for analyzing financial transactions, patterns, and anomalies with visualization capabilities.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="emoji">📊</div>
            <h3>Dashboard</h3>
            <p>Real-time overview of all active cases with key metrics and status indicators.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="emoji">📝</div>
            <h3>Case Builder</h3>
            <p>Structured workflow for creating and documenting fraud cases with evidentiary support.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="emoji">📑</div>
            <h3>Reporting</h3>
            <p>Generate professional reports with findings, visualizations, and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
def show_summary_dashboard():
    import locale
    locale.setlocale(locale.LC_ALL, '')  

    st.markdown("## 📊 Summary Dashboard")
    
    df = get_all_cases()
    
    if df.empty:
        st.warning("No data available.")
        return

    # Ensure correct datetime format
    df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')

    # Key summary metrics
    total_cases = len(df)
    total_amount = df['amount_involved'].sum()
    avg_amount = df['amount_involved'].mean()

    # Format with commas
    formatted_total = f"${total_amount:,.2f}"
    formatted_avg = f"${avg_amount:,.2f}"

    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Fraud Cases", total_cases)
    col2.metric("Total Amount Involved", formatted_total)
    col3.metric("Average Fraud Amount", formatted_avg)

    st.markdown("---")

    # Fraud cases by year
    st.markdown("### 📅 Fraud Cases Reported by Year")
    df['year'] = df['date_reported'].dt.year
    yearly_counts = df['year'].value_counts().sort_index()
    fig1 = px.bar(
        yearly_counts,
        x=yearly_counts.index,
        y=yearly_counts.values,
        labels={"x": "Year", "y": "Number of Cases"},
        title="Fraud Cases by Year"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 🔍 Top Fraud Categories by Frequency")
    category_counts = df['case_type'].value_counts().nlargest(10).reset_index()
    category_counts.columns = ['Fraud Type', 'Cases']
    fig2 = px.bar(
        category_counts,
        x='Fraud Type',
        y='Cases',
        title="Top 10 Most Common Fraud Types",
        color='Cases',
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 💰 High-Impact Fraud Types")
    impact = df.groupby('case_type')['amount_involved'].sum().nlargest(10).reset_index()
    impact.columns = ['Fraud Type', 'Total Amount']
    fig3 = px.bar(
        impact,
        x='Fraud Type',
        y='Total Amount',
        title="Top 10 Fraud Types by Amount Involved",
        labels={'Total Amount': 'Amount (USD)'},
        color='Total Amount',
        color_continuous_scale='reds'
    )
    st.plotly_chart(fig3, use_container_width=True)


def show_case_builder():
    st.markdown("## 🏗️ Case Builder")

    if st.session_state.username != "Admin@fraudcases123*":
        st.error("🔒 Only the Admin can access the Case Builder.")
        return

    st.markdown("""
    <style>
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        max-width: 800px;
        margin: auto;
        border-left: 5px solid #764ba2;
    }
    .form-header {
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">Add New Fraud Case</div>', unsafe_allow_html=True)

    with st.form("case_entry_form"):
        case_name = st.text_input("Case Name")
        case_type = st.selectbox("Case Type", get_case_types())
        description = st.text_area("Description")
        location = st.text_input("Location")
        amount_involved = st.number_input("Amount Involved", min_value=0.0, step=100.0)
        currency = st.selectbox("Currency", ["USD", "ZWL", "ZAR", "BWP", "NAD", "KES", "SZL"])
        date_detected = st.date_input("Date Detected")
        date_reported = st.date_input("Date Reported")
        date_resolved = st.date_input("Date Resolved (Optional)", value=None)
        parties = st.text_input("Parties Involved")
        agency = st.text_input("Investigation Agency")
        court_ref = st.text_input("Court Reference")
        source_url = st.text_input("Source URL (optional)")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])

        submitted = st.form_submit_button("➕ Submit Case")

        if submitted:
            case_data = (
                case_name, case_type, description, location,
                amount_involved, currency, str(date_detected),
                str(date_reported), str(date_resolved) if date_resolved else None,
                parties, agency, court_ref if court_ref else None,
                source_url if source_url else None,
                st.session_state.username,
                severity
            )

            success = add_new_case(case_data)
            if success:
                st.success("✅ Case added successfully!")
            else:
                st.error("❌ Failed to add case. Please check your inputs.")

    st.markdown('</div>', unsafe_allow_html=True)


def show_case_analysis():
    st.markdown("## 🔍 Case Analysis")
    st.markdown("Analyze fraud patterns and trends")
    
    df = get_all_cases()
    
    if not df.empty:
        # Convert dates for analysis
        df['date_reported'] = pd.to_datetime(df['date_reported'])
        df['year'] = df['date_reported'].dt.year
        df['month'] = df['date_reported'].dt.month_name()
        
        # Analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Trend Analysis", "Geographic Distribution", "Case Types", "Pattern Discovery"])

        
        
        with tab1:
            st.markdown("### Fraud Cases Over Time")
            
            # Time series analysis
            time_agg = st.radio("Time Aggregation", ["Monthly", "Quarterly", "Yearly"], horizontal=True)
            
            # Ensure correct month order
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                           'July', 'August', 'September', 'October', 'November', 'December']

            df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)

            if time_agg == "Monthly":
                df_time = df.groupby(['year', 'month']).size().reset_index(name='count')
                df_time.sort_values(by='month', inplace=True)
                
                fig = px.bar(
                    df_time,
                    x='month',
                    y='count',
                    color='year',
                    barmode='group',
                    title="Monthly Fraud Cases by Year",
                    labels={'month': 'Month', 'count': 'Number of Cases'}
                )
            elif time_agg == "Quarterly":
                df['quarter'] = df['date_reported'].dt.quarter
                df_time = df.groupby(['year', 'quarter']).size().reset_index(name='count')
                
                fig = px.bar(
                    df_time,
                    x='quarter',
                    y='count',
                    color='year',
                    barmode='group',
                    title="Quarterly Fraud Cases by Year",
                    labels={'quarter': 'Quarter', 'count': 'Number of Cases'}
                )

            elif time_agg == "Quarterly":
                df['quarter'] = df['date_reported'].dt.quarter
                df_time = df.groupby(['year', 'quarter']).size().reset_index(name='count')
                fig = px.line(df_time, x='quarter', y='count', color='year',
                              title="Quarterly Fraud Cases by Year",
                              labels={'quarter': 'Quarter', 'count': 'Number of Cases'})
            else:  # Yearly
                df_time = df.groupby('year').size().reset_index(name='count')
                fig = px.bar(df_time, x='year', y='count',
                             title="Annual Fraud Cases",
                             labels={'year': 'Year', 'count': 'Number of Cases'})
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Amount analysis
            st.markdown("### Financial Impact Analysis")
            df_amount = df[df['amount_involved'] > 0].groupby('year')['amount_involved'].sum().reset_index()
            fig = px.bar(df_amount, x='year', y='amount_involved',
                         title="Total Fraud Amounts by Year",
                         labels={'year': 'Year', 'amount_involved': 'Total Amount (USD)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("### Geographic Distribution")
            
            # Zimbabwe-specific coordinates
            zimbabwe_locations = {
                'Harare': (-17.8292, 31.0522),
                'Bulawayo': (-20.1325, 28.6265),
                'Chinhoyi': (-17.3667, 30.2000),
                'Gweru': (-19.4500, 29.8167),
                'Beitbridge': (-22.2167, 30.0000),
                'Nationwide': (-19.0154, 29.1549)  # Center of Zimbabwe
            }
            
            # Add coordinates to dataframe
            df['lat'] = df['location'].apply(lambda x: zimbabwe_locations.get(x, (-19.0154, 29.1549))[0])
            df['lon'] = df['location'].apply(lambda x: zimbabwe_locations.get(x, (-19.0154, 29.1549))[1])

            
            fig = px.scatter_mapbox(df, lat='lat', lon='lon', 
                                   color='case_type', size='amount_involved',
                                   hover_name='case_name', hover_data=['date_reported', 'severity'],
                                   zoom=5, height=600)
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
            
            # Location frequency
            st.markdown("#### Cases by Location")
            loc_counts = df['location'].value_counts().reset_index()
            loc_counts.columns = ['Location', 'Cases']
            fig = px.bar(loc_counts, x='Location', y='Cases', color='Location')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### Case Type Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Distribution by Type")
                type_counts = df['case_type'].value_counts().reset_index()
                type_counts.columns = ['Case Type', 'Count']
                fig = px.pie(type_counts, values='Count', names='Case Type')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Severity Analysis")
                severity_counts = df.groupby(['case_type', 'severity']).size().reset_index(name='count')
                fig = px.bar(severity_counts, x='case_type', y='count', color='severity',
                             labels={'case_type': 'Case Type', 'count': 'Number of Cases'})
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Average Amount by Case Type")
            df_amount = df[df['amount_involved'] > 0]
            if not df_amount.empty:
                avg_amount = df_amount.groupby('case_type')['amount_involved'].mean().reset_index()
                fig = px.bar(avg_amount, x='case_type', y='amount_involved',
                             labels={'case_type': 'Case Type', 'amount_involved': 'Average Amount (USD)'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No financial data available for analysis")
    with tab4:
        st.markdown("### 🔍 Pattern Discovery by Fraud Type")
        st.info("Explore dominant characteristics across fraud types based on severity, location, financial amounts, and seasonality.")

        fraud_types = df['case_type'].unique().tolist()
        selected_type = st.selectbox("Select Fraud Type to Explore", fraud_types)

        df_type = df[df['case_type'] == selected_type]

        if not df_type.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🔢 Summary Stats")
                stats = {
                    "Number of Cases": len(df_type),
                    "Average Amount Involved (USD)": round(df_type['amount_involved'].mean(), 2),
                    "Most Common Severity": df_type['severity'].mode()[0],
                    "Top Location": df_type['location'].mode()[0],
                    "Earliest Case": df_type['date_reported'].min().strftime("%Y-%m-%d"),
                    "Latest Case": df_type['date_reported'].max().strftime("%Y-%m-%d"),
                }
                st.json(stats)

            with col2:
                st.markdown("#### 📅 Seasonality Trend")
                df_type['month'] = df_type['date_reported'].dt.month_name()
                month_counts = df_type['month'].value_counts().reindex([
                    "January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"
                ])
                fig = px.bar(month_counts, x=month_counts.index, y=month_counts.values,
                             labels={"x": "Month", "y": "Number of Cases"},
                             title=f"Monthly Distribution for {selected_type}")
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### 🗺️ Location Distribution")
            loc_data = df_type['location'].value_counts().reset_index()
            loc_data.columns = ['Location', 'Count']
            fig = px.bar(loc_data, x='Location', y='Count', color='Location',
                         title=f"Locations Involved in {selected_type}")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### 🚨 Severity Distribution")
            severity_counts = df_type['severity'].value_counts().reset_index()
            severity_counts.columns = ['Severity', 'Count']
            fig = px.pie(severity_counts, names='Severity', values='Count',
                         title=f"Severity Levels in {selected_type}")
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No data found for this fraud type.")
        
def show_reports():
    st.markdown("## 📑 Reports")
    st.markdown("Generate detailed fraud case reports")

    df = get_all_cases()

    if not df.empty:
        # Convert to datetime safely
        df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')

        # Report filters
        col1, col2, col3 = st.columns(3)

        with col1:
            case_type_filter = st.multiselect("Filter by Case Type", get_case_types())

        with col2:
            severity_filter = st.multiselect("Filter by Severity", ["Low", "Medium", "High", "Critical"])

        with col3:
            valid_years = df['date_reported'].dropna().dt.year.unique()
            year_filter = st.multiselect("Filter by Year", sorted(valid_years, reverse=True))

        # Apply filters
        if case_type_filter:
            df = df[df['case_type'].isin(case_type_filter)]
        if severity_filter:
            df = df[df['severity'].isin(severity_filter)]
        if year_filter:
            df = df[df['date_reported'].dt.year.isin(year_filter)]

        if not df.empty:
            # Optional: drop geospatial or derived fields for export clarity
            columns_to_drop = [col for col in ['lat', 'lon', 'year', 'month'] if col in df.columns]
            df_display = df.drop(columns=columns_to_drop)

            st.dataframe(df_display, use_container_width=True)

            st.markdown("### Export Reports")

            col1, col2 = st.columns(2)

            with col1:
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download CSV", data=csv, file_name="fraud_cases_report.csv", mime="text/csv")

            with col2:
                excel_buffer = pd.ExcelWriter("fraud_cases_report.xlsx", engine="xlsxwriter")
                df_display.to_excel(excel_buffer, index=False, sheet_name="Report")
                excel_buffer.close()
                with open("fraud_cases_report.xlsx", "rb") as f:
                    st.download_button("⬇️ Download Excel", data=f, file_name="fraud_cases_report.xlsx", mime="application/vnd.ms-excel")
        else:
            st.warning("No cases matched the selected filters.")
    else:
        st.warning("No cases available for reporting.")

# --------------------------
# Main App
# --------------------------
def main():
    # Initialize database
    init_db()
    
    # Page configuration
    st.set_page_config(
        page_title="FraudCaseX | Forensic Case Management Portal",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Check authentication
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        create_sidebar()
    if st.session_state.get('current_page') == "Case Builder":
        show_case_builder()
    elif st.session_state.get('current_page') == "Summary Dashboard":
        show_summary_dashboard()
    elif st.session_state.get('current_page') == "Case Analysis":
        show_case_analysis()
    elif st.session_state.get('current_page') == "Reports":
        show_reports()
    else:
            launch_pad()
        

if __name__ == "__main__":
    main()