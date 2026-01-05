import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# LOAD DATA
# =========================
def load_data():
    BASE_DIR = Path(__file__).resolve().parent
    data_path = BASE_DIR / "main_data.parquet"

    df = pd.read_parquet(data_path)

    df['year'] = df.index.year
    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month

    return df

def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

df = load_data()
df['season'] = df['month'].apply(get_season)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    layout="wide"
)

# =========================
# HEADER
# =========================
st.markdown("""
<h1 style='text-align:center; color:#2c3e50;'>🌍 Beijing Air Quality Dashboard</h1>
<h3 style='text-align:center; color:#7f8c8d;'>Period: 2013–2017</h3>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR INFO
# =========================
with st.sidebar:
    st.header("📊 Data Overview")

    st.metric("Total Observations", f"{len(df):,}")
    st.metric("Number of Stations", df['station'].nunique())
    st.metric(
        "Time Range",
        f"{df.index.min().date()} – {df.index.max().date()}"
    )

    st.markdown("---")
    st.header("🔎 Filter Data")

    # Filter tahun
    year_min, year_max = int(df['year'].min()), int(df['year'].max())
    selected_years = st.slider(
        "Select Year Range",
        year_min, year_max,
        (year_min, year_max)
    )

    # Filter stasiun
    stations = sorted(df['station'].unique())
    selected_stations = st.multiselect(
        "Select Stations",
        stations,
        default=stations
    )

# =========================
# APPLY FILTER (GLOBAL)
# =========================
df_filtered = df[
    (df['year'].between(selected_years[0], selected_years[1])) &
    (df['station'].isin(selected_stations))
]

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs([
    "📈 Time Trend",
    "📍 By Station",
    "🫁 Air Quality Overall"
])

# TAB 1 — TIME TREND (FILTERED)

with tab1:
    st.subheader("PM2.5 Trends Over Time")

    st.metric(
        "Average PM2.5 (Filtered)",
        f"{df_filtered['PM2.5'].mean():.2f} µg/m³"
    )

    pm25_yearly = df_filtered.groupby('year')['PM2.5'].mean()
    pm25_hourly = df_filtered.groupby('hour')['PM2.5'].mean()
    pm25_daily = df_filtered.groupby('day_of_week')['PM2.5'].mean()
    pm25_seasonal = (
        df_filtered.groupby('season')['PM2.5']
        .mean()
        .reindex(['Spring', 'Summer', 'Autumn', 'Winter'])
    )

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

    # Hourly
    axes[0, 1].plot(pm25_hourly.index, pm25_hourly.values, marker='o')
    axes[0, 1].set_title("Hourly Average PM2.5")
    axes[0, 1].set_xlabel("Hour")
    axes[0, 1].set_xticks(range(0, 24))
    axes[0, 1].grid(True, alpha=0.4)

    # Daily
    axes[1, 0].plot(pm25_daily.index, pm25_daily.values, marker='o')
    axes[1, 0].set_title("Daily Average PM2.5")
    axes[1, 0].set_xticks(range(7))
    axes[1, 0].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    axes[1, 0].grid(True, alpha=0.4)

    # Yearly
    axes[0, 0].plot(pm25_yearly.index, pm25_yearly.values, marker='o')
    axes[0, 0].set_title("Annual Average PM2.5")
    axes[0, 0].set_xlabel("Year")
    axes[0, 0].grid(True, alpha=0.4)
    axes[0, 0].set_xticks(pm25_yearly.index)

    # Seasonal
    axes[1, 1].plot(pm25_seasonal.index, pm25_seasonal.values, marker='o')
    axes[1, 1].set_title("Seasonal Average PM2.5")
    axes[1, 1].grid(True, alpha=0.4)

    plt.tight_layout()
    st.pyplot(fig)

# TAB 2 — BY STATION (FILTERED)

with tab2:
    st.subheader("Stations with Highest Pollution")

    yearly_station = (
        df_filtered.groupby(['year', 'station'])['PM2.5']
        .mean()
        .reset_index()
    )

    top5 = (
        df_filtered.groupby('station')['PM2.5']
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )

    # ---------- TREND ----------
    fig1, ax1 = plt.subplots(figsize=(5, 3))

    for station in top5.index:
        d = yearly_station[yearly_station['station'] == station]
        ax1.plot(d['year'], d['PM2.5'], marker='o', label=station)

    ax1.set_title("Annual PM2.5 Trend (Top 5 Stations)", fontsize=7, pad=6)
    ax1.set_xlabel("Year", fontsize=6)
    ax1.set_ylabel("PM2.5 (µg/m³)", fontsize=6)
    years = sorted(pm25_yearly.index.unique())
    ax1.set_xticks(years)
    ax1.set_xticklabels(years)
    ax1.tick_params(axis='both', labelsize=6)
    ax1.grid(True, linestyle='--', alpha=0.4)

    ax1.legend(ncol=3, fontsize=5)

    st.pyplot(fig1, use_container_width=False)

    st.markdown("---")

    # ---------- BAR + RANKING ----------
    col1, col2 = st.columns([3, 1])

    with col1:
        fig2, ax2 = plt.subplots(figsize=(4, 3))

        bars = ax2.barh(
            top5.index,
            top5.values,
            color='firebrick'
        )

        ax2.set_title(
            "Top 5 Stations by Average PM2.5",
            fontsize=6,
            pad=6
        )
        ax2.set_xlabel("PM2.5 (µg/m³)", fontsize=6)

        ax2.tick_params(axis='x', labelsize=6)
        ax2.tick_params(axis='y', labelsize=6)

        ax2.grid(axis='x', linestyle='--', alpha=0.4)

        for bar in bars:
            ax2.text(
                bar.get_width() + max(top5.values) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.1f}",
                va='center',
                fontsize=6
            )

        plt.tight_layout()
        st.pyplot(fig2, use_container_width=False)

    with col2:
        st.markdown("### 📊 Ranking")
        for i, (station, value) in enumerate(top5.items(), 1):
            st.markdown(
                f"**{i}. {station}**  \n"
                f"<span style='color:#ff6b6b; font-size:15px'>{value:.2f} µg/m³</span>",
                unsafe_allow_html=True
            )

# TAB 3 — AIR QUALITY (FILTERED)

with tab3:
    st.subheader("Air Quality Based on Health Standards")

    def categorize_pm25(pm25):
        if pm25 <= 15:
            return 'Good'
        elif pm25 <= 25:
            return 'Moderate'
        elif pm25 <= 150:
            return 'Unhealthy'
        else:
            return 'Very Unhealthy'

    df_filtered['date'] = df_filtered.index.date

    daily = (
        df_filtered.groupby(['station', 'date'])['PM2.5']
        .mean()
        .reset_index()
    )
    daily['category'] = daily['PM2.5'].apply(categorize_pm25)

    dist = daily['category'].value_counts().reindex(
        ['Good', 'Moderate', 'Unhealthy', 'Very Unhealthy']
    )

    fig, ax = plt.subplots(figsize=(5, 5))
    colors = {
    'Good': 'green',
    'Moderate': 'yellow',
    'Unhealthy': 'red',
    'Very Unhealthy': 'black'
  }

    wedges, texts, autotexts = ax.pie(
        dist.values,
        labels=dist.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=[colors[cat] for cat in dist.index],
        textprops={'fontsize': 8}
    )

    for i, autotext in enumerate(autotexts):
        if colors[dist.index[i]] == 'black':
            autotext.set_color('white')

    ax.set_title("Air Quality Distribution", fontsize=10, pad=6)
    ax.axis('equal')

    st.pyplot(fig, use_container_width=False)
