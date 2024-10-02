import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

COLOR_SCHEME = {
    'primary': '#1e88e5',
    'secondary': '#43a047',
    'tertiary': '#fdd835',
    'background': '#f5f5f5',
    'text': '#212121'
}

@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard/day_clean.csv")
    day_df['dateday'] = pd.to_datetime(day_df['dateday'])
    
    hour_df = pd.read_csv("dashboard/hour_clean.csv")
    hour_df['dateday'] = pd.to_datetime(hour_df['dateday'])
    
    return day_df, hour_df

def create_monthly_data(df):
    monthly_data = df.groupby(df['dateday'].dt.to_period('M')).agg({
        'count': 'sum',
        'casual': 'sum',
        'registered': 'sum'
    }).reset_index()
    monthly_data['dateday'] = monthly_data['dateday'].dt.to_timestamp()
    return monthly_data

def create_season_data(df):
    return df.groupby('season').agg({
        'count': 'sum',
        'casual': 'sum',
        'registered': 'sum'
    }).reset_index()

def create_weather_data(df):
    return df.groupby('weather').agg({'count': 'sum'}).reset_index()

def create_hourly_data(df):
    return df.groupby('hr')['count'].sum().reset_index()

def create_daily_data(df):
    return df.groupby('dateday').agg({
        'count': 'sum',
        'casual': 'sum',
        'registered': 'sum'
    }).reset_index()

def main():
    st.set_page_config(page_title="Bike Rental Dashboard", page_icon="🚲", layout="wide")
    
    st.title('🚲 Bike Rental Dashboard')

    day_df, hour_df = load_data()

    st.sidebar.header("📅 Filter")
    min_date = day_df['dateday'].min().date()
    max_date = day_df['dateday'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    day_mask = (day_df['dateday'].dt.date >= start_date) & (day_df['dateday'].dt.date <= end_date)
    filtered_day_df = day_df.loc[day_mask]
    hour_mask = (hour_df['dateday'].dt.date >= start_date) & (hour_df['dateday'].dt.date <= end_date)
    filtered_hour_df = hour_df.loc[hour_mask]

    st.header("📊 Summary Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    
    total_rentals = filtered_day_df['count'].sum()
    casual_users = filtered_day_df['casual'].sum()
    registered_users = filtered_day_df['registered'].sum()
    avg_daily_rentals = filtered_day_df['count'].mean()

    col1.metric("🚲 Total Rentals", f"{total_rentals:,}")
    col2.metric("👤 Casual Users", f"{casual_users:,}")
    col3.metric("🔑 Registered Users", f"{registered_users:,}")
    col4.metric("📅 Avg. Daily Rentals", f"{avg_daily_rentals:.0f}")

    st.header("📈 Daily Rentals")
    daily_data = create_daily_data(filtered_day_df)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_data['dateday'], daily_data['count'], marker='', linestyle='-', color=COLOR_SCHEME['primary'])
    ax.fill_between(daily_data['dateday'], daily_data['count'], alpha=0.3, color=COLOR_SCHEME['primary'])
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Rentals')
    ax.set_title('Daily Rental Trend')
    st.pyplot(fig)

    st.header("📈 Monthly Rentals")
    monthly_data = create_monthly_data(filtered_day_df)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(monthly_data['dateday'], monthly_data['count'], marker='o', color=COLOR_SCHEME['primary'])
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Rentals')
    ax.set_title('Monthly Rental Trend')
    st.pyplot(fig)

    col1, col2 = st.columns(2)

    with col1:
        st.header("🍂 Rentals by Season")
        season_data = create_season_data(filtered_day_df)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='season', y='count', data=season_data, ax=ax, palette=[COLOR_SCHEME['primary'], COLOR_SCHEME['secondary'], COLOR_SCHEME['tertiary'], COLOR_SCHEME['text']])
        ax.set_xlabel('Season')
        ax.set_ylabel('Total Rentals')
        ax.set_title('Rentals by Season')
        st.pyplot(fig)

    with col2:
        st.header("🌤️ Rentals by Weather")
        weather_data = create_weather_data(filtered_day_df)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='weather', y='count', data=weather_data, ax=ax, palette=[COLOR_SCHEME['primary'], COLOR_SCHEME['secondary'], COLOR_SCHEME['tertiary'], COLOR_SCHEME['text']])
        ax.set_xlabel('Weather Condition')
        ax.set_ylabel('Total Rentals')
        ax.set_title('Rentals by Weather Condition')
        st.pyplot(fig)

    st.header("🕰️ Hourly Rentals")
    hourly_data = create_hourly_data(filtered_hour_df)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='hr', y='count', data=hourly_data, ax=ax, color=COLOR_SCHEME['primary'])
    ax.set_xlabel('Hour (24-hour format)')
    ax.set_ylabel('Total Rentals')
    ax.set_title('Rentals by Hour of Day')
    st.pyplot(fig)

if __name__ == '__main__':
    main()