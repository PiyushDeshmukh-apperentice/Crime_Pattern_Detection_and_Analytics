
"""
FIR Pattern Analysis & Visualization Dashboard (KMP Integrated)
---------------------------------------------------------------
This app:
1. Takes a text input pattern (FIR keyword/phrase).
2. Uses KMP.py to filter the dataset.
3. Generates filtered_fir.csv.
4. Displays police-use analytics (KPIs, map, charts, correlations, wordcloud, and more).

Run with:
    streamlit run fir_dashboard_app.py
"""

import streamlit as st
import pandas as pd
import os
import io
from KMP import filter_csv_by_pattern, KMP  # your KMP file (KMP function used for in-memory matching)
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# --- Paths ---
INPUT_CSV = "/mnt/StorageHDD/Projects/DAA_PBL/synthetic_fir1.csv"
FILTERED_CSV = "filtered_fir.csv"

st.set_page_config(page_title="FIR Pattern Dashboard", layout="wide")

# --- Sidebar Filters ---
st.sidebar.title("Filters")
if os.path.exists(FILTERED_CSV):
    df_temp = pd.read_csv(FILTERED_CSV)  # Temp load for filter options
    divisions = st.sidebar.multiselect("Select Police Divisions", options=df_temp['Police_Division'].dropna().unique(), default=df_temp['Police_Division'].dropna().unique())
    stations = st.sidebar.multiselect("Select Police Stations", options=df_temp['Police_Station'].dropna().unique(), default=df_temp['Police_Station'].dropna().unique())

    # Safely parse date bounds; handle NaT or missing values by falling back to sensible defaults
    try:
        df_temp['Date_of_FIR_Filing'] = pd.to_datetime(df_temp['Date_of_FIR_Filing'], errors='coerce')
        min_ts = df_temp['Date_of_FIR_Filing'].min()
        max_ts = df_temp['Date_of_FIR_Filing'].max()
    except Exception:
        min_ts = None
        max_ts = None

    # Fallbacks: if either bound is NaT/None, set to today or a sensible earlier date
    today = pd.to_datetime("today").normalize()
    if pd.isna(min_ts) or min_ts is None:
        # choose 1 year before today as a default lower bound
        min_ts = today - pd.DateOffset(years=1)
    if pd.isna(max_ts) or max_ts is None:
        max_ts = today

    # Convert to Python date objects for Streamlit's date_input
    start_date = pd.to_datetime(min_ts).date()
    end_date = pd.to_datetime(max_ts).date()
    date_range = st.sidebar.date_input("Select Date Range", [start_date, end_date])
else:
    divisions = []
    stations = []
    date_range = [None, None]

# --- 1. Pattern Input ---
st.title("🔍 FIR Pattern Analysis Dashboard")
st.write("This app filters FIR records using the KMP algorithm and visualizes the results. (Internal Police Use Only)")

pattern = st.text_input("Enter the keyword or pattern to search for (case-insensitive):")

if st.button("Run KMP Filtering"):
    if not pattern.strip():
        st.warning("Please enter a valid search pattern.")
    else:
        st.info("Running KMP filter on dataset...")
        try:
            filter_csv_by_pattern(INPUT_CSV, FILTERED_CSV, pattern)
            st.success(f"Filtered rows saved to {FILTERED_CSV}")
        except Exception as e:
            st.error(f"Error during filtering: {e}")

# --- Enhanced: Accept full FIR description and auto-extract keywords ---
st.subheader("OR: Paste full FIR description to auto-extract keywords")
description = st.text_area("Paste FIR description here (the app will extract keywords and search the dataset):")

def filter_by_description(desc, input_csv=INPUT_CSV, output_csv=FILTERED_CSV):
    """Tokenize a long FIR description into keywords, then match against the 'Formatted' column using KMP.
    Writes `output_csv` with rows that match any extracted keyword.
    """
    import re
    # Extract alphanumeric tokens of length >=3
    tokens = re.findall(r"\b[a-zA-Z0-9]{3,}\b", (desc or "").lower())
    tokens = list(dict.fromkeys(tokens))  # preserve order, unique
    if not tokens:
        raise ValueError("No valid keywords found in description (need tokens length>=3).")

    # Read CSV once and perform in-memory matching for efficiency
    df_src = pd.read_csv(input_csv)
    matched_rows = []
    for _, row in df_src.iterrows():
        formatted = (str(row.get('Formatted') or "")).lower()
        for tok in tokens:
            try:
                if KMP(tok, formatted):
                    matched_rows.append(row)
                    break
            except Exception:
                # if KMP fails for any reason, skip this token/row
                continue

    if matched_rows:
        out_df = pd.DataFrame(matched_rows)
    else:
        out_df = pd.DataFrame(columns=df_src.columns)

    out_df.to_csv(output_csv, index=False, encoding='utf-8')
    return out_df

if st.button("Filter from Description (auto-extract keywords)"):
    if not description or not description.strip():
        st.warning("Please paste a FIR description to extract keywords from.")
    else:
        st.info("Extracting keywords and running KMP matching...")
        try:
            outdf = filter_by_description(description, INPUT_CSV, FILTERED_CSV)
            st.success(f"Filtered rows saved to {FILTERED_CSV} ({len(outdf)} rows)")
        except Exception as e:
            st.error(f"Error filtering from description: {e}")

# --- 2. Load Filtered Data ---
if os.path.exists(FILTERED_CSV):
    df = pd.read_csv(FILTERED_CSV)
    df['Date_of_FIR_Filing'] = pd.to_datetime(df['Date_of_FIR_Filing'], errors='coerce')
    df['Total_Victims'] = df['Victim_Count_Female'] + df['Victim_Count_Male']
    df['Total_Convicts'] = df['Convicted_Count_Male'] + df['Convicted_Count_Female']
    df['Year'] = df['Date_of_FIR_Filing'].dt.year
    df['Month'] = df['Date_of_FIR_Filing'].dt.month
    df['Day_of_Week'] = df['Date_of_FIR_Filing'].dt.day_name()

    # Apply Filters
    df_filtered = df.copy()
    if divisions:
        df_filtered = df_filtered[df_filtered['Police_Division'].isin(divisions)]
    if stations:
        df_filtered = df_filtered[df_filtered['Police_Station'].isin(stations)]
    if date_range[0] and date_range[1]:
        df_filtered = df_filtered[(df_filtered['Date_of_FIR_Filing'] >= pd.to_datetime(date_range[0])) & 
                                  (df_filtered['Date_of_FIR_Filing'] <= pd.to_datetime(date_range[1]))]

    st.success(f"Loaded {len(df_filtered)} filtered FIR records after applying filters.")
else:
    st.warning("No filtered file found. Please run filtering first.")
    st.stop()

# --- 3. Identify Columns ---
cols = [c.lower() for c in df_filtered.columns]
date_col = 'Date_of_FIR_Filing'  # Hardcode since we know it
division_col = 'Police_Division'
station_col = 'Police_Station'
locality_col = 'Locality'
crime_col = 'Criminal_Act'  # Adjusted based on dataset
activity_col = 'Criminal_Activity'
solved_col = 'Case_Solved'
officer_col = 'Investigating_Officer'
victim_gender_col = 'Victim_Gender'
desc_col = 'FIR_Description'  # Or 'Formatted'
lat_col = next((c for c in df_filtered.columns if "lat" in c.lower()), None)
lon_col = next((c for c in df_filtered.columns if "lon" in c.lower() or "lng" in c.lower()), None)

# --- 4. KPIs ---
st.subheader("📊 Key Performance Indicators (KPIs)")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total FIRs (Filtered)", len(df_filtered))
if crime_col in df_filtered:
    top_crime = df_filtered[crime_col].mode()[0] if not df_filtered[crime_col].dropna().empty else "N/A"
    k2.metric("Most Common Crime Type", top_crime)
if division_col in df_filtered:
    k3.metric("Active Divisions", df_filtered[division_col].nunique())
k4.metric("Solved Cases (%)", f"{(df_filtered[solved_col].value_counts(normalize=True).get('Yes', 0) * 100):.1f}%")

# --- 5. Map Visualization ---
st.subheader("🗺️ Geographical Hotspots")
if lat_col and lon_col and not df_filtered[lat_col].isna().all():
    fig_map = px.scatter_mapbox(df_filtered, lat=lat_col, lon=lon_col,
        hover_name=crime_col, color=crime_col, zoom=6, height=500)
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("No latitude/longitude data found for mapping. Using location-based charts instead.")

# --- Temporal Visualizations ---
st.subheader("📅 Temporal Analysis")

col1, col2 = st.columns(2)

# Crime Frequency Over Time (Existing, enhanced with filters)
if date_col in df_filtered:
    with col1:
        time_series = df_filtered.groupby(df_filtered[date_col].dt.to_period("M")).size().reset_index(name="Count")
        time_series[date_col] = time_series[date_col].astype(str)
        fig_ts = px.line(time_series, x=date_col, y="Count", title="Crime Frequency Over Time (Monthly)")
        st.plotly_chart(fig_ts, use_container_width=True)

# Bar Chart: FIRs by Year
with col2:
    yearly = df_filtered.groupby(['Year', solved_col]).size().unstack().fillna(0)
    fig_year = px.bar(yearly, barmode='stack', title="FIRs by Year (Stacked by Solved Status)")
    st.plotly_chart(fig_year, use_container_width=True)

# Heatmap Calendar: FIRs by Day of Week/Month
if not df_filtered.empty:
    pivot = df_filtered.pivot_table(index='Day_of_Week', columns='Month', aggfunc='size', fill_value=0)
    fig_heat, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot, annot=True, cmap="YlGnBu", ax=ax)
    ax.set_title("FIRs by Day of Week and Month")
    st.pyplot(fig_heat)

# --- Location/Categorical Visualizations ---
st.subheader("📍 Location and Categorical Analysis")

col3, col4 = st.columns(2)

# Bar Chart: FIRs by Police Division
with col3:
    div_counts = df_filtered.groupby([division_col, solved_col]).size().unstack().fillna(0)
    fig_div = px.bar(div_counts, orientation='h', barmode='stack', title="FIRs by Police Division")
    st.plotly_chart(fig_div, use_container_width=True)

# Pie Chart: Distribution by Police Station
with col4:
    station_counts = df_filtered[station_col].value_counts()
    fig_pie_station = px.pie(names=station_counts.index, values=station_counts.values, title="Distribution by Police Station")
    st.plotly_chart(fig_pie_station, use_container_width=True)

# Treemap: Hierarchy of Locations
if not df_filtered.empty:
    treemap_df = df_filtered.groupby([division_col, station_col, locality_col]).size().reset_index(name='Count')
    fig_tree = px.treemap(treemap_df, path=[division_col, station_col, locality_col], values='Count', title="Location Hierarchy Treemap")
    st.plotly_chart(fig_tree, use_container_width=True)

col5, col6 = st.columns(2)

# Bar Chart: FIRs by Criminal Activity Type
with col5:
    if activity_col in df_filtered and not df_filtered[activity_col].dropna().empty:
        act_counts = df_filtered[activity_col].value_counts()
        act_df = act_counts.reset_index()
        act_df.columns = [activity_col, 'count']
        fig_act = px.bar(act_df, x=activity_col, y='count', title="FIRs by Criminal Activity (Individual vs Gang)")
        st.plotly_chart(fig_act, use_container_width=True)
    else:
        st.info("No criminal activity data available.")

# Pie Chart: Case Solved Status
with col6:
    solved_counts = df_filtered[solved_col].value_counts()
    fig_pie_solved = px.pie(names=solved_counts.index, values=solved_counts.values, title="Case Solved Status")
    st.plotly_chart(fig_pie_solved, use_container_width=True)

# Bar Chart: Cases by Investigating Officer
officer_counts = df_filtered.groupby([officer_col, solved_col]).size().unstack().fillna(0)
fig_officer = px.bar(officer_counts, barmode='stack', title="Cases by Investigating Officer")
st.plotly_chart(fig_officer, use_container_width=True)

# Bar Chart: Victim Gender Distribution
gender_counts = df_filtered[victim_gender_col].value_counts()
fig_gender = px.bar(x=gender_counts.index, y=gender_counts.values, title="Victim Gender Distribution")
st.plotly_chart(fig_gender, use_container_width=True)

# --- Numerical Visualizations (Victim/Convict) ---
st.subheader("🔢 Victim and Convict Analysis")

col7, col8 = st.columns(2)

# Histogram: Distribution of Total Victims
with col7:
    fig_hist_vict = px.histogram(df_filtered, x='Total_Victims', title="Distribution of Total Victims per FIR")
    st.plotly_chart(fig_hist_vict, use_container_width=True)

# Box Plot: Victim Counts by Division
with col8:
    fig_box_vict = px.box(df_filtered, x=division_col, y='Total_Victims', title="Victim Counts by Division")
    st.plotly_chart(fig_box_vict, use_container_width=True)

# Stacked Bar: Victims by Gender and Division
victim_sums = df_filtered.groupby(division_col)[['Victim_Count_Female', 'Victim_Count_Male']].sum()
fig_stack_vict = px.bar(victim_sums, barmode='stack', title="Victims by Gender and Division")
st.plotly_chart(fig_stack_vict, use_container_width=True)

# Similar for Convicted Counts
col9, col10 = st.columns(2)

# Histogram: Distribution of Total Convicts
with col9:
    fig_hist_conv = px.histogram(df_filtered, x='Total_Convicts', title="Distribution of Total Convicts per FIR")
    st.plotly_chart(fig_hist_conv, use_container_width=True)

# Box Plot: Convict Counts by Division
with col10:
    fig_box_conv = px.box(df_filtered, x=division_col, y='Total_Convicts', title="Convict Counts by Division")
    st.plotly_chart(fig_box_conv, use_container_width=True)

# Stacked Bar: Convicts by Gender and Division
convict_sums = df_filtered.groupby(division_col)[['Convicted_Count_Female', 'Convicted_Count_Male']].sum()
fig_stack_conv = px.bar(convict_sums, barmode='stack', title="Convicts by Gender and Division")
st.plotly_chart(fig_stack_conv, use_container_width=True)

# --- Relational Visualizations ---
st.subheader("🔗 Relational Analysis")

# Scatter Plot: Victims vs. Convicts
# fig_scatter = px.scatter(df_filtered, x='Total_Victims', y='Total_Convicts', color=solved_col, 
#                          hover_data=[division_col], title="Victims vs. Convicts (Colored by Solved Status)")
# st.plotly_chart(fig_scatter, use_container_width=True)

# Correlation Heatmap (Existing)
# num_df = df_filtered.select_dtypes(include=[np.number])
# if not num_df.empty:
#     fig_corr = px.imshow(num_df.corr(), text_auto=True, aspect="auto", title="Numeric Feature Correlation")
#     st.plotly_chart(fig_corr, use_container_width=True)
# else:
#     st.info("No numeric columns found for correlation analysis.")

# --- Top Crimes (Existing, adapted) ---
if crime_col in df_filtered:
    st.subheader("Top Crime Categories")
    top10 = df_filtered[crime_col].value_counts().nlargest(10)
    fig_bar = px.bar(x=top10.values, y=top10.index, orientation="h", labels={"x":"Count", "y":"Crime Type"})
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Word Cloud (Existing, enhanced) ---
# st.subheader("🗣️ Keyword Density (Word Cloud)")
# if desc_col in df_filtered:
#     text = " ".join(df_filtered[desc_col].dropna().astype(str))
#     if text.strip():
#         wc = WordCloud(width=800, height=400, background_color="white", stopwords=["sexual", "harassment", "stalking"]).generate(text)  # Enhanced with custom stopwords
#         fig, ax = plt.subplots(figsize=(10,5))
#         ax.imshow(wc, interpolation="bilinear")
#         ax.axis("off")
#         st.pyplot(fig)
#     else:
#         st.info("No descriptive text found.")
# else:
#     st.info("No descriptive column found for word cloud.")

# --- 10. Data Preview & Download ---
st.subheader("Data Preview")
st.dataframe(df_filtered.head(50))
csv_buf = io.StringIO()
df_filtered.to_csv(csv_buf, index=False)
st.download_button("Download Filtered CSV", data=csv_buf.getvalue(), file_name="filtered_fir.csv", mime="text/csv")

st.markdown("---")
st.caption("Internal Police Analytics Dashboard — uses KMP for FIR pattern filtering. Run securely on intranet.")