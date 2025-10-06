import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Import plotly with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    st.error("❌ Plotly not available. Please ensure plotly is installed.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="NOCDC Planning Responder Performance Analytics",
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
    .response-time-good {
        color: #27ae60;
        font-weight: bold;
    }
    .response-time-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .response-time-slow {
        color: #e74c3c;
        font-weight: bold;
    }
    .insight-box {
        background-color: #e8f4fd;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .performance-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .badge-excellent {
        background-color: #d4edda;
        color: #155724;
    }
    .badge-good {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    .badge-average {
        background-color: #fff3cd;
        color: #856404;
    }
    .badge-slow {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from Excel file"""
    try:
        # Load responder performance data
        responder_df = pd.read_excel('nocdc_responder_analysis.xlsx', sheet_name='Responder Performance')
        
        # Load ignored messages data
        ignored_df = pd.read_excel('nocdc_responder_analysis.xlsx', sheet_name='Ignored Messages')
        
        # Load KPI data
        kpi_df = pd.read_excel('nocdc_responder_analysis.xlsx', sheet_name='KPI Summary')
        
        # Load message type performance data
        type_df = pd.read_excel('nocdc_responder_analysis.xlsx', sheet_name='Message Type Performance')
        
        # Load timing analysis data
        timing_df = pd.read_excel('nocdc_responder_analysis.xlsx', sheet_name='Timing Analysis')
        
        # Load response pairs data
        response_pairs_df = pd.read_excel('nocdc_responder_analysis.xlsx', sheet_name='Response Pairs')
        
        # Load all messages data
        messages_df = pd.read_excel('nocdc_responder_analysis.xlsx', sheet_name='All Messages')
        
        return responder_df, ignored_df, kpi_df, type_df, timing_df, response_pairs_df, messages_df
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
            <div class="kpi-value">{kpi_dict.get('Total Conversations', 'N/A')}</div>
            <div class="kpi-label">Total Conversations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        response_rate = kpi_dict.get('Response Rate (%)', 'N/A')
        st.markdown(f"""
        <div class="kpi-metric">
            <div class="kpi-value">{response_rate}%</div>
            <div class="kpi-label">Response Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_response = kpi_dict.get('Avg Response Time (min)', 'N/A')
        st.markdown(f"""
        <div class="kpi-metric">
            <div class="kpi-value">{avg_response}</div>
            <div class="kpi-label">Avg Response (min)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        ignored_count = kpi_dict.get('Total Ignored', 'N/A')
        st.markdown(f"""
        <div class="kpi-metric">
            <div class="kpi-value">{ignored_count}</div>
            <div class="kpi-label">Ignored Messages</div>
        </div>
        """, unsafe_allow_html=True)

def get_performance_badge(avg_time):
    """Get performance badge based on response time"""
    if avg_time <= 5:
        return '<span class="performance-badge badge-excellent">Excellent</span>'
    elif avg_time <= 30:
        return '<span class="performance-badge badge-good">Good</span>'
    elif avg_time <= 120:
        return '<span class="performance-badge badge-average">Average</span>'
    else:
        return '<span class="performance-badge badge-slow">Needs Improvement</span>'

def create_responder_performance_chart(responder_df):
    """Create responder performance chart"""
    if responder_df is None:
        return
    
    # Sort by average response time for better visualization
    responder_df_sorted = responder_df.sort_values('Avg_Response_Time_Minutes', ascending=True)
    
    # Create color mapping based on performance
    colors = []
    for time in responder_df_sorted['Avg_Response_Time_Minutes']:
        if time <= 5:
            colors.append('#27ae60')  # Green
        elif time <= 30:
            colors.append('#3498db')  # Blue
        elif time <= 120:
            colors.append('#f39c12')  # Orange
        else:
            colors.append('#e74c3c')  # Red
    
    fig = px.bar(
        responder_df_sorted,
        x='Avg_Response_Time_Minutes',
        y='Responder',
        orientation='h',
        title="Average Response Time by Team Member",
        color=colors,
        color_discrete_map="identity"
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Average Response Time (minutes)",
        yaxis_title="Team Member",
        font=dict(size=14),
        height=600,
        showlegend=False
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Avg Response Time: %{x} min<br>Total Responses: %{customdata}<extra></extra>',
        customdata=responder_df_sorted['Total_Responses']
    )
    
    return fig

def create_response_time_distribution_chart(timing_df):
    """Create response time distribution chart"""
    if timing_df is None:
        return
    
    # Filter out empty rows
    timing_data = timing_df[timing_df['Response_Time_Range'].notna()]
    
    if timing_data.empty:
        return None
    
    fig = px.bar(
        timing_data,
        x='Response_Time_Range',
        y='Count',
        title="Response Time Distribution",
        color='Count',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Response Time Range",
        yaxis_title="Number of Responses",
        font=dict(size=14)
    )
    
    fig.update_traces(
        hovertemplate='<b>Time Range:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>'
    )
    
    return fig

def create_message_type_performance_chart(type_df):
    """Create message type performance chart"""
    if type_df is None:
        return
    
    # Create subplot with response rate and avg response time
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Response Rate by Message Type', 'Avg Response Time by Message Type'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Response rate chart
    fig.add_trace(
        go.Bar(
            x=type_df['Message_Type'],
            y=type_df['Response_Rate_Percent'],
            name='Response Rate (%)',
            marker_color='#3498db'
        ),
        row=1, col=1
    )
    
    # Average response time chart
    fig.add_trace(
        go.Bar(
            x=type_df['Message_Type'],
            y=type_df['Avg_Response_Time_Minutes'],
            name='Avg Response Time (min)',
            marker_color='#e74c3c'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Message Type Performance Analysis",
        height=500,
        showlegend=False
    )
    
    fig.update_xaxes(title_text="Message Type", row=1, col=1)
    fig.update_xaxes(title_text="Message Type", row=1, col=2)
    fig.update_yaxes(title_text="Response Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Response Time (min)", row=1, col=2)
    
    return fig

def create_insights_section(responder_df, type_df, ignored_df):
    """Create insights section"""
    if responder_df is None or type_df is None:
        return
    
    st.markdown('<div class="section-header">💡 Key Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top performers
        top_performers = responder_df.nsmallest(3, 'Avg_Response_Time_Minutes')
        st.markdown("""
        <div class="insight-box">
            <h4>🏆 Fastest Responders</h4>
        """, unsafe_allow_html=True)
        
        for _, row in top_performers.iterrows():
            badge = get_performance_badge(row['Avg_Response_Time_Minutes'])
            st.markdown(f"• **{row['Responder']}**: {row['Avg_Response_Time_Minutes']:.1f} min avg {badge}", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Slowest responders
        slowest_performers = responder_df.nlargest(3, 'Avg_Response_Time_Minutes')
        st.markdown("""
        <div class="insight-box">
            <h4>⚠️ Slowest Responders</h4>
        """, unsafe_allow_html=True)
        
        for _, row in slowest_performers.iterrows():
            badge = get_performance_badge(row['Avg_Response_Time_Minutes'])
            st.markdown(f"• **{row['Responder']}**: {row['Avg_Response_Time_Minutes']:.1f} min avg {badge}", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Message type insights
        best_type = type_df.loc[type_df['Avg_Response_Time_Minutes'].idxmin()]
        worst_type = type_df.loc[type_df['Avg_Response_Time_Minutes'].idxmax()]
        
        st.markdown("""
        <div class="insight-box">
            <h4>📋 Message Type Insights</h4>
            <p><strong>Fastest Response:</strong> {fast_type} ({time:.1f} min)</p>
            <p><strong>Slowest Response:</strong> {slow_type} ({slow_time:.1f} min)</p>
        </div>
        """.format(
            fast_type=best_type['Message_Type'],
            time=best_type['Avg_Response_Time_Minutes'],
            slow_type=worst_type['Message_Type'],
            slow_time=worst_type['Avg_Response_Time_Minutes']
        ), unsafe_allow_html=True)
        
        # Overall stats
        total_responses = responder_df['Total_Responses'].sum()
        avg_response = responder_df['Avg_Response_Time_Minutes'].mean()
        ignored_count = len(ignored_df) if ignored_df is not None else 0
        
        st.markdown("""
        <div class="insight-box">
            <h4>📊 Overall Performance</h4>
            <p><strong>Total Responses:</strong> {total}</p>
            <p><strong>Average Response Time:</strong> {time:.1f} minutes</p>
            <p><strong>Ignored Messages:</strong> {ignored}</p>
        </div>
        """.format(
            total=total_responses,
            time=avg_response,
            ignored=ignored_count
        ), unsafe_allow_html=True)

def create_responder_comparison_chart(responder_df):
    """Create responder comparison chart with multiple metrics"""
    if responder_df is None:
        return
    
    # Create subplot with response count and avg time
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Total Responses by Team Member', 'Average Response Time by Team Member'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Sort by total responses
    responder_df_sorted = responder_df.sort_values('Total_Responses', ascending=True)
    
    # Response count chart
    fig.add_trace(
        go.Bar(
            x=responder_df_sorted['Total_Responses'],
            y=responder_df_sorted['Responder'],
            orientation='h',
            name='Total Responses',
            marker_color='#3498db'
        ),
        row=1, col=1
    )
    
    # Average response time chart
    responder_df_time_sorted = responder_df.sort_values('Avg_Response_Time_Minutes', ascending=True)
    fig.add_trace(
        go.Bar(
            x=responder_df_time_sorted['Avg_Response_Time_Minutes'],
            y=responder_df_time_sorted['Responder'],
            orientation='h',
            name='Avg Response Time (min)',
            marker_color='#e74c3c'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Team Member Performance Comparison",
        height=600,
        showlegend=False
    )
    
    fig.update_xaxes(title_text="Total Responses", row=1, col=1)
    fig.update_xaxes(title_text="Response Time (min)", row=1, col=2)
    fig.update_yaxes(title_text="Team Member", row=1, col=1)
    fig.update_yaxes(title_text="Team Member", row=1, col=2)
    
    return fig

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 NOCDC Planning Responder Performance Analytics</h1>', unsafe_allow_html=True)
    
    # Load data
    responder_df, ignored_df, kpi_df, type_df, timing_df, response_pairs_df, messages_df = load_data()
    
    if responder_df is None:
        st.error("❌ Could not load data. Please ensure 'nocdc_responder_analysis.xlsx' exists in the current directory.")
        st.info("💡 Run the responder analysis script first to generate the analysis data.")
        return
    
    # Sidebar filters
    st.sidebar.markdown("## 🔍 Filters")
    
    # Responder filter
    if not responder_df.empty:
        responder_options = ['All'] + list(responder_df['Responder'].unique())
        selected_responder = st.sidebar.selectbox("Filter by Responder", responder_options)
        
        if selected_responder != 'All':
            responder_df = responder_df[responder_df['Responder'] == selected_responder]
    
    # Performance filter
    if not responder_df.empty:
        performance_options = ['All', 'Excellent (≤5 min)', 'Good (≤30 min)', 'Average (≤120 min)', 'Needs Improvement (>120 min)']
        selected_performance = st.sidebar.selectbox("Filter by Performance", performance_options)
        
        if selected_performance == 'Excellent (≤5 min)':
            responder_df = responder_df[responder_df['Avg_Response_Time_Minutes'] <= 5]
        elif selected_performance == 'Good (≤30 min)':
            responder_df = responder_df[(responder_df['Avg_Response_Time_Minutes'] > 5) & (responder_df['Avg_Response_Time_Minutes'] <= 30)]
        elif selected_performance == 'Average (≤120 min)':
            responder_df = responder_df[(responder_df['Avg_Response_Time_Minutes'] > 30) & (responder_df['Avg_Response_Time_Minutes'] <= 120)]
        elif selected_performance == 'Needs Improvement (>120 min)':
            responder_df = responder_df[responder_df['Avg_Response_Time_Minutes'] > 120]
    
    # KPI Metrics
    st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
    create_kpi_metrics(kpi_df)
    
    # Insights Section
    create_insights_section(responder_df, type_df, ignored_df)
    
    # Responder Performance Analysis
    st.markdown('<div class="section-header">👥 Team Member Response Performance</div>', unsafe_allow_html=True)
    
    # First row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        responder_chart = create_responder_performance_chart(responder_df)
        if responder_chart:
            st.plotly_chart(responder_chart, use_container_width=True)
    
    with col2:
        comparison_chart = create_responder_comparison_chart(responder_df)
        if comparison_chart:
            st.plotly_chart(comparison_chart, use_container_width=True)
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        timing_chart = create_response_time_distribution_chart(timing_df)
        if timing_chart:
            st.plotly_chart(timing_chart, use_container_width=True)
    
    with col2:
        type_chart = create_message_type_performance_chart(type_df)
        if type_chart:
            st.plotly_chart(type_chart, use_container_width=True)
    
    # Detailed Data Tables
    st.markdown('<div class="section-header">📋 Detailed Data</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Responder Performance", "Response Pairs", "Ignored Messages", "Message Type Performance", "Timing Analysis", "All Messages"])
    
    with tab1:
        st.dataframe(responder_df, use_container_width=True)
    
    with tab2:
        if response_pairs_df is not None and not response_pairs_df.empty:
            st.dataframe(response_pairs_df, use_container_width=True)
        else:
            st.success("🎉 No response pairs found!")
    
    with tab3:
        if ignored_df is not None and not ignored_df.empty:
            st.dataframe(ignored_df, use_container_width=True)
        else:
            st.success("🎉 No ignored messages found! All conversations received responses.")
    
    with tab4:
        st.dataframe(type_df, use_container_width=True)
    
    with tab5:
        st.dataframe(timing_df, use_container_width=True)
    
    with tab6:
        st.dataframe(messages_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; margin-top: 2rem;'>
        <p>📊 NOCDC Planning Responder Performance Analytics | Generated with Streamlit</p>
        <p>💡 This dashboard shows how long each team member takes to respond to others' messages</p>
        <p>🏆 Performance badges: Excellent (≤5 min), Good (≤30 min), Average (≤120 min), Needs Improvement (>120 min)</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
