import sqlite3
import random
import uuid
import csv
from datetime import datetime, timedelta

# --- Configurable Data ---

POLICE_STRUCTURE = {
    "Swargate Division": {
        "Market Yard Police Station": ["KK Market", "Hadapsar", "Bhekrai Nagar", "Magarpatta"],
        "Bharati Vidyapeeth Police Station": ["Trimurti Nagar", "Ambegaon Khurd", "Bharati Vidyapeeth"],
        "Bibvewadi Police Station": ["Katraj", "Dhankawadi", "Parwati"]
    },
    "Vishrambaug and Deccan Division": {
        "Shivajinagar Police Station": ["Shivajinagar", "FC Road", "JM Road"],
        "Kothrud Police Station": ["Paud Road", "Ideal Colony", "Karve Nagar", "Vanaz"],
        "Warje-Malwadi Police Station": ["Shivane", "Warje"]
    },
    "Sinhagad-Road Division": {
        "Sinhagad Road Police Station": ["Anandnagar", "Hingne", "Manik Baug"],
        "Nanded City Police Station": ["Nanded", "Dhayari", "Kirkatwadi", "Khadakwasla"],
        "Narhe Police Station": ["Narhegaon", "Ambegaon Budruk", "Mokarwadi"]
    },
    "Pune Division": {
        "Camp Police Station": ["Camp", "Laxmi Road", "Shaniwar Wada"],
        "Kalyani Nagar Police Station": ["Kalyani Nagar", "Viman Nagar", "Koregaon Park"],
    }
}

CRIMINAL_ACTS = {
    "Homicide": ["Poisoning", "Stabbing", "Gunshot", "Strangulation", "Hit-and-run"],
    "Kidnapping": ["Luring victim", "Threatening with weapon", "Drugging", "Abduction in vehicle", "Online enticement"],
    "Murder": ["Knife attack", "Firearm", "Blunt object", "Premeditated assault", "Gang violence"],
    "Sexual Harassment": ["Workplace misconduct", "Stalking", "Verbal abuse", "Physical harassment", "Online harassment"],
    "Domestic Abuse": ["Physical beating", "Emotional abuse", "Financial control", "Verbal threats", "Neglect"],
    "Robbery": ["Snatching", "Armed robbery", "Breaking and entering", "Highway robbery", "ATM theft"],
    "Cyber Crime": ["Phishing", "Identity theft", "Online fraud", "Hacking", "Ransomware"],
    "Fraud": ["Fake documents", "Ponzi schemes", "Tax evasion", "Insurance fraud", "Bank scam"],
    "Drug Trafficking": ["Hidden compartments", "Body packing", "Courier parcels", "Sea route", "Air smuggling"],
    "Smuggling": ["Underground tunnels", "Hidden in vehicles", "Cargo mislabeling", "Coastal boats", "Human mules"],
    "Extortion": ["Threat calls", "Blackmail", "Kidnapping threats", "Business coercion", "Cyber extortion"],
    "Human Trafficking": ["Job fraud", "Forced marriage", "Sex trafficking", "Bonded labor", "Child trafficking"],
    "Assault": ["Street fight", "Road rage", "Bar fight", "Domestic assault", "Political rally violence"],
    "Burglary": ["Night break-in", "Lock picking", "Window entry", "Impersonating delivery", "Inside job"],
    "Illegal Arms Possession": ["Unlicensed firearm", "Smuggled weapons", "Homemade arms", "Black market purchase", "Hidden cache"]
}

OFFICERS = [
    "Rajesh Patil", "Sunil Deshmukh", "Anjali Kulkarni", "Prashant Jadhav",
    "Sneha Shinde", "Mahesh Pawar", "Neha Bhosale", "Sandeep Gaikwad",
    "Ramesh More", "Vaishali Chavan", "Nitin Kadam", "Swati Joshi"
]

VICTIM_GENDERS = ["Male", "Female", "Other"]

# --- Functions ---

def random_date(start_days=1000):
    start_date = datetime.now() - timedelta(days=start_days)
    random_days = random.randint(0, start_days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

def generate_fir_record():
    division = random.choice(list(POLICE_STRUCTURE.keys()))
    station = random.choice(list(POLICE_STRUCTURE[division].keys()))
    locality = random.choice(POLICE_STRUCTURE[division][station])
    
    fir_id = str(uuid.uuid4())[:8].upper()
    date_filing = random_date()
    act = random.choice(list(CRIMINAL_ACTS.keys()))
    activity_type = random.choice(["Gang", "Individual"])
    officer = random.choice(OFFICERS)
    case_solved = random.choice(["Yes", "No"])
    
    victim_gender = random.choice(VICTIM_GENDERS)
    victim_count_female = random.randint(0, 3)
    victim_count_male = random.randint(0, 3)
    total_victims = victim_count_female + victim_count_male
    convicted_count = random.randint(0, total_victims)
    convicted_male = random.randint(0, convicted_count)
    convicted_female = convicted_count - convicted_male
    
    modus_operandi = random.choice(CRIMINAL_ACTS[act])
    
    victim_text = f"{total_victims} victim" if total_victims == 1 else f"{total_victims} victims"
    fir_description = f"{act} by {modus_operandi} in {locality} on {date_filing}, {victim_text}"
    
    return [
        fir_id, division, station, date_filing, act, activity_type, locality,
        officer, case_solved, act, victim_gender,
        victim_count_female, victim_count_male,
        convicted_count, convicted_male, convicted_female,
        modus_operandi, fir_description
    ]

def create_database():
    conn = sqlite3.connect("synthetic_fir.db")
    cur = conn.cursor()
    
    cur.execute("""CREATE TABLE IF NOT EXISTS FIR_Records (
        FIR_ID TEXT PRIMARY KEY,
        Police_Division TEXT,
        Police_Station TEXT,
        Date_of_FIR_Filing TEXT,
        Criminal_Act TEXT,
        Criminal_Activity TEXT,
        Locality TEXT,
        Investigating_Officer TEXT,
        Case_Solved TEXT,
        Criminal_Act_Applied TEXT,
        Victim_Gender TEXT,
        Victim_Count_Female INTEGER,
        Victim_Count_Male INTEGER,
        Convicted_Count INTEGER,
        Convicted_Count_Male INTEGER,
        Convicted_Count_Female INTEGER,
        Modus_Operandi TEXT,
        FIR_Description TEXT
    )""")
    
    conn.commit()
    return conn

def insert_and_export(num_records):
    conn = create_database()
    cur = conn.cursor()
    
    header = [
        "FIR_ID","Police_Division","Police_Station","Date_of_FIR_Filing",
        "Criminal_Act","Criminal_Activity","Locality","Investigating_Officer",
        "Case_Solved","Criminal_Act_Applied","Victim_Gender",
        "Victim_Count_Female","Victim_Count_Male","Convicted_Count",
        "Convicted_Count_Male","Convicted_Count_Female",
        "Modus_Operandi","FIR_Description"
    ]
    
    with open("synthetic_fir.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for _ in range(num_records):
            record = generate_fir_record()
            cur.execute("""INSERT INTO FIR_Records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", record)
            writer.writerow(record)
    
    conn.commit()
    conn.close()
    print(f"✅ Inserted {num_records} FIRs into synthetic_fir.db and synthetic_fir.csv")

# --- Main ---
if __name__ == "__main__":
    num = int(input("Enter number of FIR records to generate: "))
    insert_and_export(num)
