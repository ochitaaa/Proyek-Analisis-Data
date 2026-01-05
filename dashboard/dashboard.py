import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

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
    if month in [12, 1, 2]: return 'Winter'
    elif month in [3, 4, 5]: return 'Spring'
    elif month in [6, 7, 8]: return 'Summer'
    else: return 'Autumn'

# ========== LOAD DATA ==========
df = load_data()
df['season'] = df['month'].apply(get_season)

# ========== DASHBOARD ==========
st.set_page_config(page_title="Beijing Air Quality Dashboard", layout="wide")

# Header Utama
st.markdown("""
    <h1 style='text-align: center; color: #2c3e50; font-size: 35px;'>🌍 Beijing Air Quality</h1>
    <h3 style='text-align: center; color: #7f8c8d; font-size: 21px;'>Period: 2013–2017</h3>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
    <style>
        /* === TAB === */
        .stTabs button {
            font-size: 24px !important;
            font-weight: bold;
            padding: 10px 16px !important;
        }

        /* === SIDEBAR === */
        [data-testid="stSidebar"] h2 {
            font-size: 20px !important;
            font-weight: bold;
        }
        [data-testid="stSidebar"] .stMetric label {
            font-size: 18px !important;
        }
        [data-testid="stSidebar"] .stMetric div[data-testid="stMetricValue"] {
            font-size: 18px !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Data Statistics")
    
    total_observasi = len(df)
    total_stasiun = df['station'].nunique()
    start_date = df.index.min().strftime('%Y-%m-%d')
    end_date = df.index.max().strftime('%Y-%m-%d')
    
    st.metric("Total Observations", f"{total_observasi:,}")
    st.metric("Number of Stations", total_stasiun)
    st.metric("Time Range", f"{start_date} – {end_date}")

# Tab
tab1, tab2, tab3 = st.tabs([
    "📈 Time Trend",
    "📍 By Station",
    "🫁 Air Quality Overall"
])

# ---------- TAB 1: TIME TREND ----------
with tab1:
    st.subheader("PM2.5 Trends Over Time")
    
    # Hitung agregat
    pm25_yearly = df.groupby('year')['PM2.5'].mean()
    pm25_hourly = df.groupby('hour')['PM2.5'].mean()
    pm25_daily = df.groupby('day_of_week')['PM2.5'].mean()
    pm25_seasonal = df.groupby('season')['PM2.5'].mean().reindex(['Spring', 'Summer', 'Autumn', 'Winter'])
    
    # Buat figure 2x2 dengan ukuran lebih kecil
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
       
    # Per Jam
    axes[0, 1].plot(pm25_hourly.index, pm25_hourly.values, marker='o', color='red', linewidth=2)
    axes[0, 1].set_title('Hourly Average PM2.5', fontsize=10)
    axes[0, 1].set_xlabel('Hour', fontsize=7)
    axes[0, 1].set_ylabel('PM2.5 (µg/m³)', fontsize=9)
    axes[0, 1].grid(True, alpha=0.5)
    axes[0, 1].set_xticks(range(0, 24))
    
    # Per Hari
    axes[1, 0].plot(pm25_daily.index, pm25_daily.values, marker='o', color='green', linewidth=2)
    axes[1, 0].set_title('Daily Average PM2.5', fontsize=10)
    axes[1, 0].set_xlabel('Day', fontsize=9)
    axes[1, 0].set_ylabel('PM2.5 (µg/m³)', fontsize=9)
    axes[1, 0].grid(True, alpha=0.5)
    axes[1, 0].set_xticks(range(0, 7))
    axes[1, 0].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=8)
    
    # Per Tahun
    axes[0, 0].plot(pm25_yearly.index, pm25_yearly.values, marker='o', color='blue', linewidth=2)
    axes[0, 0].set_title('Annual Average PM2.5', fontsize=10)
    axes[0, 0].set_xlabel('Year', fontsize=9)
    axes[0, 0].set_ylabel('PM2.5 (µg/m³)', fontsize=9)
    axes[0, 0].grid(True, alpha=0.5)
    axes[0, 0].set_xticks(pm25_yearly.index)

    # Per Musim
    axes[1, 1].plot(pm25_seasonal.index, pm25_seasonal.values, marker='o', color='purple', linewidth=2)
    axes[1, 1].set_title('Seasonal Average PM2.5', fontsize=10)
    axes[1, 1].set_xlabel('Season', fontsize=9)
    axes[1, 1].set_ylabel('PM2.5 (µg/m³)', fontsize=9)
    axes[1, 1].grid(True, alpha=0.5)
    
    plt.tight_layout()
    st.pyplot(fig)

# ---------- TAB 2: STATIONS ----------

with tab2:
    st.subheader("Stations with Highest Pollution")

    yearly_pm25 = (
        df.groupby(['year', 'station'])['PM2.5']
        .mean()
        .reset_index()
    )

    top5 = (
        df.groupby('station')['PM2.5']
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )
    top5_names = top5.index

    # TREND CHART
    fig1, ax1 = plt.subplots(figsize=(4, 4))

    for station in top5_names:
        data_station = yearly_pm25[yearly_pm25['station'] == station]
        ax1.plot(
            data_station['year'],
            data_station['PM2.5'],
            marker='o',
            linewidth=1.8,
            markersize=4,
            label=station
        )

    ax1.set_title(
        'Annual PM2.5 Trend (Top 5 Stations)',
        fontsize=7,
        pad=8
    )
    ax1.set_xlabel('Year', fontsize=6)
    ax1.set_ylabel('PM2.5 (µg/m³)', fontsize=6)

    years = sorted(yearly_pm25['year'].unique())
    ax1.set_xticks(years)
    ax1.set_xticklabels(years)

    ax1.tick_params(axis='both', labelsize=6)
    ax1.grid(True, linestyle='--', alpha=0.4)

    ax1.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.30),
        ncol=3,
        fontsize=6,
        frameon=False
    )

    plt.tight_layout()
    st.pyplot(fig1, use_container_width=False)

    st.markdown("---")

    # BAR + RANKING
    col1, col2 = st.columns([3, 1])

    with col1:
        fig2, ax2 = plt.subplots(figsize=(4, 3))

        ax2.bar(
            top5.index,
            top5.values,
            color='firebrick',
            edgecolor='black',
            width=0.7
        )

        ax2.set_title(
            'Top 5 Stations by Average PM2.5',
            fontsize=8,
            pad=7
        )
        ax2.set_ylabel('PM2.5 (µg/m³)', fontsize=6)
        ax2.set_xlabel('')
        ax2.tick_params(axis='x', labelsize=6)
        ax2.tick_params(axis='y', labelsize=6)
        ax2.grid(axis='y', linestyle='--', alpha=0.4)

        plt.tight_layout()
        st.pyplot(fig2, use_container_width=False)

    with col2:
        st.markdown("### 📊 Ranking")
        for i, (station, value) in enumerate(top5.items(), 1):
            st.markdown(
                f"**{i}. {station}**  \n"
                f"<span style='color:#ff6b6b'>{value:.2f} µg/m³</span>",
                unsafe_allow_html=True
            )


# ---------- TAB 3: AIR QUALITY ----------
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
    
    # Gunakan data harian (rata-rata per stasiun per hari)
    df['date'] = df.index.date
    daily_data = df.groupby(['station', 'date'])['PM2.5'].mean().reset_index()
    daily_data['category'] = daily_data['PM2.5'].apply(categorize_pm25)
    
    # Hitung distribusi
    dist = daily_data['category'].value_counts().reindex(['Good', 'Moderate', 'Unhealthy', 'Very Unhealthy'])
    
    # Pie chart
    fig, ax = plt.subplots(figsize=(5, 5))
    colors = {'Good': 'green', 'Moderate': 'yellow', 'Unhealthy': 'red', 'Very Unhealthy': 'black'}
    wedges, texts, autotexts = ax.pie(
        dist.values,
        labels=dist.index,
        autopct='%1.1f%%',
        colors=[colors[cat] for cat in dist.index],
        startangle=90,
        textprops={'fontsize': 8}
    )
    ax.set_title('Daily Air Quality Distribution (2013–2017)', fontsize=10)
    
    # Atur teks putih untuk kategori gelap
    for i, autotext in enumerate(autotexts):
        if colors[dist.index[i]] == 'black':
            autotext.set_color('white')
    
    ax.axis('equal')
    plt.tight_layout()
    
    st.pyplot(fig, use_container_width=False)