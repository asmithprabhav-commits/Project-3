# to humlog ko sabse pehle modules install karna hoga 1. stramlit 2. bcrypt 3. zxcvbn 4. sqlite3
import streamlit as st
import bcrypt
import sqlite3
import time
from zxcvbn import zxcvbn
from datetime import datetime

# Ab page ka configuration banynge
st.set_page_config(page_title="Project 3", layout="wide")

# background ka colour define karenge
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    </style>
    """, unsafe_allow_html=True)
# ab idea ko implement karenge ki user ka data secure rahe aur unka password hash ho. Hum sqlite3 ka use karenge database ke liye.
conn = sqlite3.connect('secure_vault.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (timestamp TEXT, event TEXT, username TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS reviews (username TEXT, content TEXT, timestamp TEXT)''')
conn.commit()
#bhaisaab isko krte krte ye samajh aa rha ki FAt k 4 ho jata
#security ke liye hum log event ko log karenge
def log_event(event, username="System"):
    c.execute("INSERT INTO audit_logs VALUES (?, ?, ?)", (str(datetime.now()), event, username))
    conn.commit()

# session state ka use karenge user authentication ke liye
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'current_user' not in st.session_state: st.session_state['current_user'] = None

# soch rhe ki ek side bar bna le jaise ki user easily navigate kar ske
menu = ["Login", "Register"]
if st.session_state['auth']:
    menu = ["Dashboard"]
    if st.session_state['current_user'] == 'admin':
        menu.append("Admin Panel")

choice = st.sidebar.selectbox("Menu", menu)

if st.session_state['auth']:
    st.sidebar.write(f"Logged in as: **{st.session_state['current_user']}**")
    if st.sidebar.button("Logout"):
        st.session_state['auth'] = False
        st.session_state['current_user'] = None
        st.rerun()

# ab hum user ko register aur login karne ka option denge
#yarrr gemini ka help lene pdega itta advanced features ke liye
st.title("🛡️ Project 3: Secure Vault")

if choice == "Register":
    new_user = st.text_input("Username")
    new_pwd = st.text_input("Password", type="password")
    if st.button("Register"):
        hashed = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (new_user, hashed.decode('utf-8')))
        conn.commit()
        st.success("Account Created!")

elif choice == "Login":
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        c.execute("SELECT password FROM users WHERE username = ?", (user,))
        data = c.fetchone()
        if data and bcrypt.checkpw(pwd.encode('utf-8'), data[0].encode('utf-8')):
            st.session_state['auth'] = True
            st.session_state['current_user'] = user
            log_event("LOGIN_SUCCESS", user)
            st.toast("Welcome back! Have a nice day! ☀️", icon="👋")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid credentials.")

       elif choice == "Dashboard":
            st.subheader(f"Welcome back, {st.session_state['current_user']}!")
    
    # ab hum user ko reviews aur challenge ka option denge
    tab1, tab2 = st.tabs(["📝 Reviews", "🧩 Challenge"])
    
    with tab1:
        content = st.text_area("Share your thoughts:")
        if st.button("Submit Review"):
            c.execute("INSERT INTO reviews VALUES (?, ?, ?)", (st.session_state['current_user'], content, str(datetime.now())))
            conn.commit()
            st.success("Review Added!")
        
        elif choice == "Login":
             user = st.text_input("Username")
             pwd = st.text_input("Password", type="password")
        if st.button("Login"):
        c.execute("SELECT password FROM users WHERE username = ?", (user,))
        data = c.fetchone()
        
        if data and bcrypt.checkpw(pwd.encode('utf-8'), data[0].encode('utf-8')):
            st.session_state['auth'] = True
            st.session_state['current_user'] = user
            
            # Logs the successful attempt
            log_event("LOGIN_SUCCESS", user) 
            
            st.toast("Welcome back! Have a nice day! ☀️", icon="👋")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid credentials.")
            
            # ADD THIS LINE: Logs the failed attempt
            log_event("LOGIN_FAILED", user)
        
        st.subheader("Recent Reviews")
        c.execute("SELECT * FROM reviews ORDER BY timestamp DESC")
        for row in c.fetchall():
            st.write(f"**{row[0]}** ({row[2]}): {row[1]}")

    with tab2:
        st.subheader("Password Cracking Simulator")
        target = 660851
        if 'attempts' not in st.session_state: st.session_state['attempts'] = 0
        guess = st.text_input("Guess the simple hash:")
        if st.button("Crack it!"):
            st.session_state['attempts'] += 1
            if (sum(ord(c) for c in guess) * 31 % 1000000) == target:
                st.balloons()
                st.success("Correct!")
            else:
                st.error(f"Try again! Attempts: {st.session_state['attempts']}")

elif choice == "Admin Panel":
    st.subheader("System Audit Logs")
    c.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC")
    st.table(c.fetchall())
    #kya mtlb ab ye ho gya syd baki k kaam baad m add kiya jayegA YA IMPLEMENT KIYA JAYEGa
    # game k liye shree ko bol dete wo dimaag lagyega ab 
