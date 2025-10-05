import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Page configuration
st.set_page_config(
    page_title="WhatsApp Support Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .kpi-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    .kpi-metric {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from Excel file"""
    try:
        # Load issues data
        issues_df = pd.read_excel('support_analysis.xlsx', sheet_name='Issues')
        
        # Load messages data
        messages_df = pd.read_excel('support_analysis.xlsx', sheet_name='Messages')
        
        # Load KPI data
        kpi_df = pd.read_excel('support_analysis.xlsx', sheet_name='KPI Summary')
        
        # Load categories data
        categories_df = pd.read_excel('support_analysis.xlsx', sheet_name='Categories')
        
        # Load support performance data
        support_df = pd.read_excel('support_analysis.xlsx', sheet_name='Support Performance')
        
        # Load timing analysis data (optional sheet)
        try:
            timing_df = pd.read_excel('support_analysis.xlsx', sheet_name='Timing Analysis')
        except Exception:
            timing_df = None
        
        return issues_df, messages_df, kpi_df, categories_df, support_df, timing_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None

def create_kpi_metrics(kpi_df):
    """Create KPI metrics cards"""
    if kpi_df is None:
        return
    
    # Convert KPI dataframe to dictionary
    kpi_dict = dict(zip(kpi_df['Metric'], kpi_df['Value']))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-metric">
            <div class="kpi-value">{kpi_dict.get('Total Issues', 'N/A')}</div>
            <div class="kpi-label">Total Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        resolution_rate = kpi_dict.get('Resolution Rate (%)', 'N/A')
        st.markdown(f"""
        <div class="kpi-metric">
            <div class="kpi-value">{resolution_rate}%</div>
            <div class="kpi-label">Resolution Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        response_rate = kpi_dict.get('Response Rate (%)', 'N/A')
        st.markdown(f"""
        <div class="kpi-metric">
            <div class="kpi-value">{response_rate}%</div>
            <div class="kpi-label">Response Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_response = kpi_dict.get('Avg Response Time (min)', 'N/A')
        st.markdown(f"""
        <div class="kpi-metric">
            <div class="kpi-value">{avg_response}</div>
            <div class="kpi-label">Avg Response (min)</div>
        </div>
        """, unsafe_allow_html=True)

def create_status_distribution_chart(issues_df):
    """Create issue status distribution chart"""
    if issues_df is None:
        return
    
    status_counts = issues_df['Status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Issue Status Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title_x=0.5,
        font=dict(size=14),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01
        )
    )
    
    return fig

def create_category_chart(categories_df):
    """Create issue category distribution chart"""
    if categories_df is None:
        return
    
    fig = px.bar(
        categories_df,
        x='Category',
        y='Count',
        title="Issues by Category",
        color='Count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Category",
        yaxis_title="Number of Issues",
        font=dict(size=14)
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )
    
    return fig

def create_response_time_chart(issues_df):
    """Create response time analysis chart"""
    if issues_df is None:
        return
    
    # Filter out null values
    response_times = issues_df[issues_df['First Response Time (minutes)'].notna()]
    
    if response_times.empty:
        return None
    
    fig = px.histogram(
        response_times,
        x='First Response Time (minutes)',
        nbins=20,
        title="Response Time Distribution",
        color_discrete_sequence=['#3498db']
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Response Time (minutes)",
        yaxis_title="Number of Issues",
        font=dict(size=14)
    )
    
    fig.update_traces(
        hovertemplate='<b>Response Time:</b> %{x} minutes<br><b>Count:</b> %{y}<extra></extra>'
    )
    
    return fig

def create_timing_analysis_chart(timing_df):
    """Create timing analysis chart"""
    if timing_df is None:
        return
    
    # Check if we have response time range data
    if 'Response Time Range' in timing_df.columns and 'Count' in timing_df.columns:
        # Filter out empty rows
        response_data = timing_df[timing_df['Response Time Range'].notna()]
        
        if response_data.empty:
            return None
        
        fig = px.bar(
            response_data,
            x='Response Time Range',
            y='Count',
            title="Response Time Distribution",
            color='Count',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            title_x=0.5,
            xaxis_title="Response Time Range",
            yaxis_title="Number of Issues",
            font=dict(size=14)
        )
        
        fig.update_traces(
            hovertemplate='<b>Time Range:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>'
        )
        
        return fig
    
    return None

def create_hour_analysis_chart(issues_df):
    """Create hour analysis chart from issues data"""
    if issues_df is None or issues_df.empty:
        return None
    
    # Convert Start Time to datetime if it's not already
    issues_df['Start Time'] = pd.to_datetime(issues_df['Start Time'])
    
    # Extract hour from Start Time
    issues_df['Hour'] = issues_df['Start Time'].dt.hour
    
    # Count issues by hour
    hour_counts = issues_df['Hour'].value_counts().sort_index()
    
    if hour_counts.empty:
        return None
    
    # Create DataFrame for plotting
    hour_data = pd.DataFrame({
        'Hour': hour_counts.index,
        'Count': hour_counts.values
    })
    
    fig = px.bar(
        hour_data,
        x='Hour',
        y='Count',
        title="Issues by Hour of Day",
        color='Count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Hour of Day",
        yaxis_title="Number of Issues",
        font=dict(size=14)
    )
    
    fig.update_traces(
        hovertemplate='<b>Hour:</b> %{x}:00<br><b>Issues:</b> %{y}<extra></extra>'
    )
    
    return fig

def create_support_performance_chart(support_df):
    """Create support staff performance chart"""
    if support_df is None:
        return
    
    fig = px.bar(
        support_df,
        x='Support Staff',
        y='Issues Handled',
        title="Support Staff Performance",
        color='Issues Handled',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Support Staff",
        yaxis_title="Issues Handled",
        font=dict(size=14),
        xaxis_tickangle=-45
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Issues Handled: %{y}<extra></extra>'
    )
    
    return fig

def create_resolution_time_chart(issues_df):
    """Create resolution time analysis chart"""
    if issues_df is None:
        return
    
    # Filter out null values
    resolution_times = issues_df[issues_df['Resolution Time (hours)'].notna()]
    
    if resolution_times.empty:
        return None
    
    fig = px.box(
        resolution_times,
        y='Resolution Time (hours)',
        title="Resolution Time Distribution",
        color_discrete_sequence=['#e74c3c']
    )
    
    fig.update_layout(
        title_x=0.5,
        yaxis_title="Resolution Time (hours)",
        font=dict(size=14)
    )
    
    fig.update_traces(
        hovertemplate='<b>Resolution Time:</b> %{y} hours<extra></extra>'
    )
    
    return fig

def create_trend_analysis(issues_df):
    """Create trend analysis over time"""
    if issues_df is None:
        return
    
    # Convert Start Time to datetime if it's not already
    issues_df['Start Time'] = pd.to_datetime(issues_df['Start Time'])
    
    # Group by date
    daily_issues = issues_df.groupby(issues_df['Start Time'].dt.date).size().reset_index()
    daily_issues.columns = ['Date', 'Issues']
    
    fig = px.line(
        daily_issues,
        x='Date',
        y='Issues',
        title="Daily Issue Trends",
        markers=True
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Number of Issues",
        font=dict(size=14)
    )
    
    fig.update_traces(
        hovertemplate='<b>Date:</b> %{x}<br><b>Issues:</b> %{y}<extra></extra>'
    )
    
    return fig

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 WhatsApp Support Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    issues_df, messages_df, kpi_df, categories_df, support_df, timing_df = load_data()
    
    if issues_df is None:
        st.error("❌ Could not load data. Please ensure 'support_analysis.xlsx' exists in the current directory.")
        return
    
    # Sidebar filters
    st.sidebar.markdown("## 🔍 Filters")
    
    # Date range filter
    if not issues_df.empty:
        issues_df['Start Time'] = pd.to_datetime(issues_df['Start Time'])
        min_date = issues_df['Start Time'].min().date()
        max_date = issues_df['Start Time'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            issues_df = issues_df[
                (issues_df['Start Time'].dt.date >= start_date) & 
                (issues_df['Start Time'].dt.date <= end_date)
            ]
    
    # Status filter
    if not issues_df.empty:
        status_options = ['All'] + list(issues_df['Status'].unique())
        selected_status = st.sidebar.selectbox("Filter by Status", status_options)
        
        if selected_status != 'All':
            issues_df = issues_df[issues_df['Status'] == selected_status]
    
    # Category filter
    if not issues_df.empty:
        category_options = ['All'] + list(issues_df['Category'].unique())
        selected_category = st.sidebar.selectbox("Filter by Category", category_options)
        
        if selected_category != 'All':
            issues_df = issues_df[issues_df['Category'] == selected_category]
    
    # KPI Metrics
    st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
    create_kpi_metrics(kpi_df)
    
    # Charts section
    st.markdown('<div class="section-header">📊 Analytics Overview</div>', unsafe_allow_html=True)
    
    # First row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        status_chart = create_status_distribution_chart(issues_df)
        if status_chart:
            st.plotly_chart(status_chart, use_container_width=True)
    
    with col2:
        category_chart = create_category_chart(categories_df)
        if category_chart:
            st.plotly_chart(category_chart, use_container_width=True)
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        response_chart = create_response_time_chart(issues_df)
        if response_chart:
            st.plotly_chart(response_chart, use_container_width=True)
    
    with col2:
        resolution_chart = create_resolution_time_chart(issues_df)
        if resolution_chart:
            st.plotly_chart(resolution_chart, use_container_width=True)
    
    # Third row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        timing_chart = create_timing_analysis_chart(timing_df)
        if timing_chart:
            st.plotly_chart(timing_chart, use_container_width=True)
        else:
            # Fallback to hour analysis from issues data
            hour_chart = create_hour_analysis_chart(issues_df)
            if hour_chart:
                st.plotly_chart(hour_chart, use_container_width=True)
    
    with col2:
        trend_chart = create_trend_analysis(issues_df)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
    
    # Support Performance
    st.markdown('<div class="section-header">👥 Support Staff Performance</div>', unsafe_allow_html=True)
    
    support_chart = create_support_performance_chart(support_df)
    if support_chart:
        st.plotly_chart(support_chart, use_container_width=True)
    
    # Detailed Data Tables
    st.markdown('<div class="section-header">📋 Detailed Data</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Issues", "Messages", "Support Performance"])
    
    with tab1:
        st.dataframe(issues_df, use_container_width=True)
    
    with tab2:
        st.dataframe(messages_df, use_container_width=True)
    
    with tab3:
        st.dataframe(support_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; margin-top: 2rem;'>
        <p>📊 WhatsApp Support Analytics Dashboard | Generated with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
