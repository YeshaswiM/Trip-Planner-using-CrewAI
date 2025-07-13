"""
VacAIgent Analytics Dashboard
Monitor agent performance, user interactions, and trip planning success rates.
"""

import streamlit as st
import datetime
import json
import os
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="📊 VacAIgent Analytics",
    page_icon="📊",
    layout="wide"
)

def load_analytics_data():
    """Load analytics data from logs or Weave."""
    # In a real implementation, this would connect to Weave or load from log files
    # For now, we'll create sample data
    sample_data = {
        "user_sessions": [
            {
                "session_id": "session_20250713_140530",
                "timestamp": "2025-01-13T14:05:30",
                "trip_mode": "🎯 Single Destination",
                "origin": "San Francisco, CA",
                "destination": "Tokyo, Japan",
                "execution_time": 45.2,
                "success": True,
                "agents_used": ["flight_search", "city_selection", "local_expert", "travel_concierge"]
            },
            {
                "session_id": "session_20250713_141230",
                "timestamp": "2025-01-13T14:12:30",
                "trip_mode": "🗺️ Bucket List",
                "origin": "New York, NY",
                "destinations": ["Paris, France", "Tokyo, Japan", "Bali, Indonesia"],
                "execution_time": 120.5,
                "success": True,
                "agents_used": ["weather_analysis", "flight_search", "city_selection", "local_expert"]
            },
            {
                "session_id": "session_20250713_142015",
                "timestamp": "2025-01-13T14:20:15",
                "trip_mode": "🎯 Single Destination",
                "origin": "Los Angeles, CA",
                "destination": "Santorini, Greece",
                "execution_time": 38.7,
                "success": True,
                "agents_used": ["flight_search", "city_selection", "local_expert", "travel_concierge"]
            }
        ],
        "agent_performance": {
            "flight_search": {"success_rate": 0.95, "avg_execution_time": 8.2, "usage_count": 156},
            "weather_analysis": {"success_rate": 0.92, "avg_execution_time": 12.1, "usage_count": 89},
            "city_selection": {"success_rate": 0.98, "avg_execution_time": 6.8, "usage_count": 203},
            "local_expert": {"success_rate": 0.97, "avg_execution_time": 15.3, "usage_count": 187},
            "travel_concierge": {"success_rate": 0.94, "avg_execution_time": 22.4, "usage_count": 172}
        },
        "popular_destinations": {
            "Tokyo, Japan": 45,
            "Paris, France": 38,
            "Bali, Indonesia": 32,
            "Santorini, Greece": 28,
            "New York, NY": 25,
            "London, UK": 22,
            "Dubai, UAE": 19,
            "Sydney, Australia": 17
        }
    }
    return sample_data

def create_agent_performance_chart(agent_data: Dict):
    """Create agent performance visualization."""
    agents = list(agent_data.keys())
    success_rates = [agent_data[agent]["success_rate"] * 100 for agent in agents]
    execution_times = [agent_data[agent]["avg_execution_time"] for agent in agents]
    usage_counts = [agent_data[agent]["usage_count"] for agent in agents]
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=["Agent Performance Metrics"]
    )
    
    # Success rate bars
    fig.add_trace(
        go.Bar(
            x=agents,
            y=success_rates,
            name="Success Rate (%)",
            marker_color="lightgreen",
            text=[f"{rate:.1f}%" for rate in success_rates],
            textposition="auto"
        ),
        secondary_y=False
    )
    
    # Execution time line
    fig.add_trace(
        go.Scatter(
            x=agents,
            y=execution_times,
            mode="lines+markers",
            name="Avg Execution Time (s)",
            line=dict(color="red", width=3),
            marker=dict(size=8)
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_xaxes(title_text="Agents")
    fig.update_yaxes(title_text="Success Rate (%)", secondary_y=False)
    fig.update_yaxes(title_text="Execution Time (seconds)", secondary_y=True)
    
    fig.update_layout(
        title="Agent Performance Overview",
        height=400,
        showlegend=True
    )
    
    return fig

def create_destination_popularity_chart(destination_data: Dict):
    """Create popular destinations chart."""
    destinations = list(destination_data.keys())
    counts = list(destination_data.values())
    
    fig = px.bar(
        x=counts,
        y=destinations,
        orientation='h',
        title="Most Popular Destinations",
        labels={'x': 'Number of Trips Planned', 'y': 'Destinations'},
        color=counts,
        color_continuous_scale="viridis"
    )
    
    fig.update_layout(height=400, showlegend=False)
    return fig

def create_usage_trends_chart():
    """Create usage trends over time."""
    # Sample time series data
    dates = pd.date_range(start='2025-01-01', end='2025-01-13', freq='D')
    single_dest = [12, 15, 18, 14, 22, 25, 19, 28, 32, 24, 29, 35, 31]
    bucket_list = [8, 10, 12, 9, 15, 18, 14, 20, 24, 18, 22, 26, 23]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=single_dest,
        mode='lines+markers',
        name='Single Destination',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=bucket_list,
        mode='lines+markers',
        name='Bucket List',
        line=dict(color='orange', width=3)
    ))
    
    fig.update_layout(
        title="Trip Planning Mode Usage Trends",
        xaxis_title="Date",
        yaxis_title="Number of Plans Generated",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def main():
    st.title("📊 VacAIgent Analytics Dashboard")
    st.markdown("Monitor agent performance, user interactions, and trip planning success rates.")
    
    # Load data
    analytics_data = load_analytics_data()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Sessions",
            len(analytics_data["user_sessions"]),
            delta="+5 today"
        )
    
    with col2:
        avg_success = sum(
            agent["success_rate"] for agent in analytics_data["agent_performance"].values()
        ) / len(analytics_data["agent_performance"])
        st.metric(
            "Avg Success Rate",
            f"{avg_success:.1%}",
            delta="+2.3%"
        )
    
    with col3:
        total_destinations = sum(analytics_data["popular_destinations"].values())
        st.metric(
            "Plans Generated",
            total_destinations,
            delta="+12 today"
        )
    
    with col4:
        avg_time = sum(
            session["execution_time"] for session in analytics_data["user_sessions"]
        ) / len(analytics_data["user_sessions"])
        st.metric(
            "Avg Planning Time",
            f"{avg_time:.1f}s",
            delta="-5.2s"
        )
    
    st.divider()
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_agent_performance_chart(analytics_data["agent_performance"]),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_destination_popularity_chart(analytics_data["popular_destinations"]),
            use_container_width=True
        )
    
    # Usage trends
    st.plotly_chart(
        create_usage_trends_chart(),
        use_container_width=True
    )
    
    # Recent sessions table
    st.subheader("Recent Planning Sessions")
    
    # Convert sessions to DataFrame
    sessions_df = pd.DataFrame(analytics_data["user_sessions"])
    if not sessions_df.empty:
        sessions_df["timestamp"] = pd.to_datetime(sessions_df["timestamp"])
        sessions_df = sessions_df.sort_values("timestamp", ascending=False)
        
        # Display formatted table
        st.dataframe(
            sessions_df[[
                "timestamp", "trip_mode", "origin", 
                "execution_time", "success"
            ]].head(10),
            use_container_width=True
        )
    
    # Agent details expander
    with st.expander("🤖 Detailed Agent Statistics"):
        for agent_name, stats in analytics_data["agent_performance"].items():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{agent_name.replace('_', ' ').title()}**")
            with col2:
                st.write(f"Success: {stats['success_rate']:.1%}")
            with col3:
                st.write(f"Avg Time: {stats['avg_execution_time']:.1f}s")
            with col4:
                st.write(f"Usage: {stats['usage_count']} times")
    
    # Tips and insights
    st.subheader("📈 Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "**🎯 High Performance Agents**\n\n"
            "• City Selection Agent has the highest success rate (98%)\n"
            "• Local Expert provides the most detailed insights\n"
            "• Flight Search maintains 95% accuracy"
        )
    
    with col2:
        st.warning(
            "**⚡ Optimization Opportunities**\n\n"
            "• Weather Analysis could be faster (12.1s avg)\n"
            "• Consider caching for popular destinations\n"
            "• Bucket list mode shows growing demand"
        )

if __name__ == "__main__":
    main()
