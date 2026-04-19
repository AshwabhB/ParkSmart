import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="ParkSmart — SJSU Parking",
    page_icon="🅿️",
    layout="wide"
)

GARAGES = ['North Garage', 'South Garage', 'West Garage', 'South Campus Garage']
CSV_FILES = {
    'North Garage': 'north_garage.csv',
    'South Garage': 'south_garage.csv',
    'West Garage': 'west_garage.csv',
    'South Campus Garage': 'south_campus_garage.csv',
}
DAYS_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


@st.cache_data(ttl=300)
def load_all_data():
    frames = []
    for garage, path in CSV_FILES.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df['Hour'] = df['Timestamp'].dt.hour
            df['Day'] = df['Timestamp'].dt.day_name()
            df['Occupancy'] = pd.to_numeric(df['Occupancy'], errors='coerce')
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def latest_occupancy(df):
    if df.empty:
        return {}
    idx = df.groupby('Garage Name')['Timestamp'].idxmax()
    return df.loc[idx].set_index('Garage Name')['Occupancy'].to_dict()


def occupancy_color(pct):
    if pct >= 85:
        return "#d9534f"
    if pct >= 60:
        return "#f0ad4e"
    return "#5cb85c"


st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/en/thumb/9/9b/SJSU_seal.svg/200px-SJSU_seal.svg.png",
    width=80,
)
st.sidebar.title("ParkSmart")
st.sidebar.caption("SJSU Parking Availability Predictor")

selected_garage = st.sidebar.selectbox("Select Garage", GARAGES)
selected_day = st.sidebar.selectbox("Filter by Day", ["All Days"] + DAYS_ORDER)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Data is collected every **15 minutes** via AWS Lambda. "
    "Historical records are stored in S3 and mirrored locally as CSV files."
)

st.title("🅿️ ParkSmart — SJSU Parking Dashboard")
st.markdown("Real-time occupancy status and historical trends for all four SJSU parking garages.")

df = load_all_data()

if df.empty:
    st.error("No data files found. Make sure the CSV files are present in the working directory.")
    st.stop()

st.subheader("Current Occupancy")
latest = latest_occupancy(df)
cols = st.columns(4)
for col, garage in zip(cols, GARAGES):
    pct = latest.get(garage)
    with col:
        if pct is not None:
            color = occupancy_color(pct)
            status = "FULL" if pct >= 100 else f"{int(pct)}%"
            st.markdown(
                f"""
                <div style='background:{color};padding:16px;border-radius:10px;text-align:center;color:white;'>
                    <b style='font-size:13px;'>{garage}</b><br>
                    <span style='font-size:32px;font-weight:bold;'>{status}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.metric(label=garage, value="N/A")

st.markdown("---")
st.subheader(f"Occupancy Trend — {selected_garage}")

garage_df = df[df['Garage Name'] == selected_garage].copy()
if selected_day != "All Days":
    garage_df = garage_df[garage_df['Day'] == selected_day]

if not garage_df.empty:
    tab_time, tab_day = st.tabs(["By Hour", "By Day of Week"])

    with tab_time:
        hourly_avg = (
            garage_df.groupby('Hour')['Occupancy']
            .mean()
            .reset_index()
            .sort_values('Hour')
        )
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(hourly_avg['Hour'], hourly_avg['Occupancy'], marker='o', linewidth=2, color='#003366')
        ax.axhline(y=85, color='red', linestyle='--', alpha=0.4, label='85% threshold')
        ax.fill_between(hourly_avg['Hour'], hourly_avg['Occupancy'], alpha=0.15, color='#003366')
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Average Occupancy (%)")
        ax.set_ylim(0, 105)
        ax.set_xticks(range(0, 24))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, fontsize=8)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)
        plt.close(fig)

    with tab_day:
        day_avg = (
            garage_df.groupby('Day')['Occupancy']
            .mean()
            .reindex([d for d in DAYS_ORDER if d in garage_df['Day'].values])
            .reset_index()
        )
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(day_avg['Day'], day_avg['Occupancy'], color='#003366', alpha=0.8)
        ax.axhline(y=85, color='red', linestyle='--', alpha=0.4, label='85% threshold')
        ax.set_ylabel("Average Occupancy (%)")
        ax.set_ylim(0, 105)
        ax.set_xticklabels(day_avg['Day'], rotation=30, ha='right')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        for bar, val in zip(bars, day_avg['Occupancy']):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{val:.0f}%", ha='center', va='bottom', fontsize=9)
        st.pyplot(fig)
        plt.close(fig)
else:
    st.info("No data available for the selected filters.")

st.markdown("---")
st.subheader("All Garages — Average Occupancy by Hour")

compare_df = df.copy()
if selected_day != "All Days":
    compare_df = compare_df[compare_df['Day'] == selected_day]

garage_colors = {
    'North Garage': '#003366',
    'South Garage': '#2ca02c',
    'West Garage': '#9467bd',
    'South Campus Garage': '#d62728',
}

fig, ax = plt.subplots(figsize=(12, 5))
for garage in GARAGES:
    gdf = compare_df[compare_df['Garage Name'] == garage]
    if not gdf.empty:
        hourly = gdf.groupby('Hour')['Occupancy'].mean().reset_index().sort_values('Hour')
        ax.plot(
            hourly['Hour'], hourly['Occupancy'],
            label=garage, color=garage_colors[garage],
            linewidth=2, marker='o', markersize=4
        )
ax.axhline(y=85, color='red', linestyle='--', alpha=0.3, label='85% threshold')
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Average Occupancy (%)")
ax.set_ylim(0, 105)
ax.set_xticks(range(0, 24))
ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, fontsize=8)
ax.legend(loc='upper left')
ax.grid(True, linestyle='--', alpha=0.4)
st.pyplot(fig)
plt.close(fig)

st.markdown("---")

with st.expander("Raw Data Explorer"):
    show_df = df[df['Garage Name'] == selected_garage].copy()
    if selected_day != "All Days":
        show_df = show_df[show_df['Day'] == selected_day]
    show_df = show_df.sort_values('Timestamp', ascending=False).reset_index(drop=True)
    st.dataframe(show_df[['Timestamp', 'Garage Name', 'Occupancy', 'Last Updated Day',
                           'Last Updated Month', 'Last Updated Date', 'Last Updated Time']],
                 use_container_width=True)

st.caption("ParkSmart · Data collected via AWS Lambda every 15 minutes · SJSU Parking Status Portal")
