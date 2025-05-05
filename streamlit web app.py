# Internship/Job Application Tracker using Streamlit + SQLite

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION SECTION ---
# Define the path for the SQLite database file
DB_PATH = "job_applications.db"

# Define the path for storing uploaded resumes
RESUME_DIR = Path("resumes")
RESUME_DIR.mkdir(exist_ok=True)  # Create the folder if it doesn't exist

# --- DATABASE INITIALIZATION ---
# Connect to the SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Create the applications table to store job application records
cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        role TEXT,
        status TEXT,
        contact TEXT,
        notes TEXT,
        resume_path TEXT,
        date_added TEXT
    )
''')
conn.commit()  # Commit the changes to save the table

# --- FUNCTION DEFINITIONS ---
# Function to add a new job application to the database
def add_application(company, role, status, contact, notes, resume_path):
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Capture the current timestamp
    cursor.execute('''
        INSERT INTO applications (company, role, status, contact, notes, resume_path, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (company, role, status, contact, notes, resume_path, date_added))
    conn.commit()  # Save the new record to the database

# Function to retrieve all job application records as a DataFrame
def get_applications():
    return pd.read_sql("SELECT * FROM applications", conn)

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(page_title="Internship Tracker", layout="wide")

# Display the main page title
st.title("\U0001F4BC Internship / Job Application Tracker")

# --- FORM FOR NEW APPLICATION ENTRY ---
# Create an interactive form where users can input application details
with st.form("add_form", clear_on_submit=True):
    st.subheader("Add New Application")
    
    # Form input fields for application data
    company = st.text_input("Company Name")
    role = st.text_input("Role Title")
    status = st.selectbox("Application Status", ["Applied", "Interview", "Rejected"])
    contact = st.text_input("Recruiter Contact")
    notes = st.text_area("Notes")
    resume = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    submit = st.form_submit_button("Submit")  # Submit button for form

    # --- PROCESS FORM SUBMISSION ---
    if submit:
        resume_path = ""

        # Save uploaded resume to the resumes directory
        if resume is not None:
            resume_path = str(RESUME_DIR / resume.name)
            with open(resume_path, "wb") as f:
                f.write(resume.read())

        # Insert the application into the database
        add_application(company, role, status, contact, notes, resume_path)
        st.success("\u2705 Application added!")  # Show success message

# --- DISPLAY ALL SAVED APPLICATIONS ---
st.subheader("\U0001F4CB Applications Overview")
df = get_applications()  # Fetch all application data

# Display a message if no data is found
if df.empty:
    st.info("No applications yet.")
else:
    # Create a 3-column layout for Kanban-style status display
    statuses = ["Applied", "Interview", "Rejected"]
    cols = st.columns(3)

    # Loop through each status and populate the respective column
    for i, status in enumerate(statuses):
        with cols[i]:
            st.markdown(f"### {status}")
            for _, row in df[df["status"] == status].iterrows():
                # Display job application details in each card
                st.markdown(f"*{row['company']}* — {row['role']}")
                st.markdown(f"\U0001F4DE {row['contact']}")
                st.markdown(f"\U0001F4DC {row['notes'][:100] + '...' if len(row['notes']) > 100 else row['notes']}")

                # Provide clickable resume link if available
                if row["resume_path"]:
                    st.markdown(f"[View Resume]({row['resume_path']})", unsafe_allow_html=True)
                st.markdown("---")  # Add a horizontal divider between applications