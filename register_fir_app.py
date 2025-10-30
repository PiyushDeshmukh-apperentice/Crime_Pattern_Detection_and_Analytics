"""
FIR Registration App
--------------------
Lightweight Streamlit app to register a new FIR and append it to
`synthetic_fir1.csv`. Uses `Formatting.parse_fir_description` to
construct the `Formatted` column (no external API calls).

Run with:
    streamlit run register_fir_app.py

This script:
 - Presents a form with fields matching `synthetic_fir1.csv` columns.
 - Builds a `Formatted` value using the parser in `Formatting.py`.
 - Appends the new FIR to `synthetic_fir1.csv` safely.
"""

import streamlit as st
import pandas as pd
import os
from datetime import date, datetime
import uuid

# Import the parser from Formatting.py (uses local parse_fir_description)
from Formatting import parse_fir_description
# Import hierarchical data from generate_data.py
from generate_data import POLICE_STRUCTURE, CRIMINAL_ACTS, OFFICERS

# Path to the dataset (same as app.py uses synthetic_fir1.csv)
CSV_PATH = "/mnt/StorageHDD/Projects/DAA_PBL/synthetic_fir1.csv"

# UI helper functions
def get_all_police_stations():
    """Get all police stations from all divisions."""
    stations = []
    for division_stations in POLICE_STRUCTURE.values():
        stations.extend(division_stations.keys())
    return sorted(list(set(stations)))

def get_all_localities():
    """Get all localities from all stations."""
    localities = []
    for division_stations in POLICE_STRUCTURE.values():
        for station_localities in division_stations.values():
            localities.extend(station_localities)
    return sorted(list(set(localities)))

def get_all_modus_operandi():
    """Get all modus operandi from all criminal acts."""
    modi = []
    for act_modi in CRIMINAL_ACTS.values():
        modi.extend(act_modi)
    return sorted(list(set(modi)))

# Expected columns/order in synthetic_fir1.csv
CSV_COLUMNS = [
    "FIR_ID","Police_Division","Police_Station","Date_of_FIR_Filing",
    "Criminal_Act","Criminal_Activity","Locality","Investigating_Officer",
    "Case_Solved","Criminal_Act_Applied","Victim_Gender",
    "Victim_Count_Female","Victim_Count_Male","Convicted_Count",
    "Convicted_Count_Male","Convicted_Count_Female","Modus_Operandi",
    "FIR_Description","Formatted"
]

st.set_page_config(page_title="Register FIR", layout="wide")
st.title("📋 Register New FIR")
st.write("Fill the form below to append a new FIR record to the dataset.")

with st.form(key="fir_form"):
    # Create three columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Location Details")
        
        # All available options in dropdowns
        police_division = st.selectbox(
            "Police Division",
            options=sorted(list(POLICE_STRUCTURE.keys())),
            help="Select the police division",
            key="division_select"
        )
        
        police_station = st.selectbox(
            "Police Station",
            options=get_all_police_stations(),
            help="Select the police station",
            key="station_select"
        )
        
        locality = st.selectbox(
            "Locality",
            options=get_all_localities(),
            help="Select the locality",
            key="locality_select"
        )
        
        filing_date = st.date_input(
            "Date of FIR Filing",
            value=date.today(),
            help="Select the date when FIR was filed"
        )
        
        investigating_officer = st.selectbox(
            "Investigating Officer",
            options=OFFICERS,
            help="Select the investigating officer"
        )
        
        case_solved = st.selectbox(
            "Case Solved",
            options=["No", "Yes"],
            index=0,
            help="Is the case solved?"
        )
    
    with col2:
        st.subheader("🚨 Crime Details")
        # All available options for crime details
        criminal_act = st.selectbox(
            "Criminal Act",
            options=sorted(list(CRIMINAL_ACTS.keys())),
            help="Select the type of crime"
        )
        
        modus_operandi = st.selectbox(
            "Modus Operandi",
            options=get_all_modus_operandi(),
            help="Select how the crime was committed"
        )
        
        criminal_activity = st.selectbox(
            "Criminal Activity",
            options=["Individual", "Gang", "Other"],
            index=0,
            help="Select whether individual or gang activity"
        )

    st.markdown("---")
    
    # Create two columns for victim and convict details
    vcol1, vcol2 = st.columns(2)
    
    with vcol1:
        st.subheader("👥 Victim Details")
        victim_gender = st.selectbox(
            "Primary Victim Gender",
            options=["Male", "Female", "Other", "Unknown"],
            index=3,
            help="Select the primary victim's gender"
        )
        victim_count_female = st.number_input(
            "Female Victims",
            min_value=0,
            value=0,
            help="Number of female victims"
        )
        victim_count_male = st.number_input(
            "Male Victims",
            min_value=0,
            value=0,
            help="Number of male victims"
        )
    
    with vcol2:
        st.subheader("⚖️ Case Details")
        criminal_act_applied = st.text_input(
            "Criminal Act Applied",
            value=criminal_act,  # Default to selected criminal act
            help="Formal charge text (defaults to Criminal Act)"
        )
        
        # Convict counts with proper sync
        convicted_count_male = st.number_input(
            "Male Convicts",
            min_value=0,
            value=0,
            help="Number of male convicts"
        )
        convicted_count_female = st.number_input(
            "Female Convicts",
            min_value=0,
            value=0,
            help="Number of female convicts"
        )
        # Total is calculated from male + female
        convicted_count = convicted_count_male + convicted_count_female
        st.info(f"Total Convicts: {convicted_count}")

    st.markdown("---")
    st.subheader("📝 Description")
    
    # Auto-generate a basic description
    default_desc = f"{criminal_act} by {modus_operandi} in {locality}"
    fir_description = st.text_area(
        "FIR Description",
        value=default_desc,
        help="Edit the auto-generated description or provide your own",
        height=100
    )
    
    col_submit1, col_submit2, col_submit3 = st.columns([2,1,2])
    with col_submit2:
        submit = st.form_submit_button("📋 Register FIR", use_container_width=True)

if submit:
    # Basic validation
    if not police_division or not police_station or not criminal_act:
        st.error("Please fill Police Division, Police Station and Criminal Act fields.")
    else:
        # Generate FIR_ID
        fir_id = uuid.uuid4().hex.upper()[0:8]

        # Build formatted text using parse_fir_description; fall back to constructed string
        try:
            formatted_text = parse_fir_description(fir_description or f"{criminal_act} by {modus_operandi} in {locality}")
        except Exception as e:
            # In case parsing fails, create a safe fallback
            formatted_text = f"{criminal_act} {modus_operandi} {locality}".strip()

        # Build new row in the same column order
        new_row = {
            "FIR_ID": fir_id,
            "Police_Division": police_division,
            "Police_Station": police_station,
            "Date_of_FIR_Filing": pd.to_datetime(filing_date).strftime("%Y-%m-%d"),
            "Criminal_Act": criminal_act,
            "Criminal_Activity": criminal_activity,
            "Locality": locality,
            "Investigating_Officer": investigating_officer,
            "Case_Solved": case_solved,
            "Criminal_Act_Applied": criminal_act_applied or criminal_act,
            "Victim_Gender": victim_gender,
            "Victim_Count_Female": int(victim_count_female),
            "Victim_Count_Male": int(victim_count_male),
            "Convicted_Count": int(convicted_count),
            "Convicted_Count_Male": int(convicted_count_male),
            "Convicted_Count_Female": int(convicted_count_female),
            "Modus_Operandi": modus_operandi,
            "FIR_Description": fir_description,
            "Formatted": formatted_text,
        }

        # Append safely to CSV
        try:
            if os.path.exists(CSV_PATH):
                df = pd.read_csv(CSV_PATH, dtype=str)
                # Ensure columns exist; if not, reindex to expected columns
                for c in CSV_COLUMNS:
                    if c not in df.columns:
                        df[c] = ""
                df = df[CSV_COLUMNS]
                # Append
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True, sort=False)
                df.to_csv(CSV_PATH, index=False, encoding='utf-8')
            else:
                # Create new DataFrame with proper columns
                df = pd.DataFrame([new_row], columns=CSV_COLUMNS)
                df.to_csv(CSV_PATH, index=False, encoding='utf-8')

            st.success(f"✅ FIR successfully registered!")
            
            # Show success details in columns
            dc1, dc2 = st.columns(2)
            with dc1:
                st.info(f"📋 FIR ID: {fir_id}")
                st.info(f"📍 Location: {locality}, {police_station}")
                st.info(f"👮 Officer: {investigating_officer}")
            
            with dc2:
                st.info(f"🏷️ Crime: {criminal_act} ({modus_operandi})")
                st.info(f"👥 Victims: {int(victim_count_female) + int(victim_count_male)}")
                st.info(f"⚖️ Status: {case_solved}")
            
            with st.expander("View Complete Record"):
                st.json(new_row)

        except Exception as e:
            st.error(f"❌ Failed to append to CSV: {e}")
            raise
