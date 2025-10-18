"""AeroLine Risk Orchestrator - Professional Enterprise UI"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import httpx
from datetime import datetime, timedelta
import json
import os
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="AeroLine | Risk Orchestrator",
    page_icon="./favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("API_KEY", "dev-key-123")
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8080"
if "snowflake_connected" not in st.session_state:
    st.session_state.snowflake_connected = False

# Professional color scheme
COLORS = {
    "primary": "#1e3a5f",      # Navy blue
    "secondary": "#4a90e2",     # Sky blue
    "success": "#27ae60",       # Green
    "warning": "#f39c12",       # Orange
    "danger": "#e74c3c",        # Red
    "dark": "#2c3e50",          # Dark gray
    "light": "#ecf0f1",         # Light gray
    "white": "#ffffff",
    "background": "#f8f9fa",
    "text": "#333333"
}

# Custom CSS for professional styling
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: {COLORS['background']};
        color: {COLORS['text']};
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Professional header */
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 2rem 2rem 1rem 2rem;
        margin: -3rem -3rem 2rem -3rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .main-title {{
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    
    .main-subtitle {{
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 0.5rem;
        opacity: 0.95;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: {COLORS['dark']};
    }}
    
    .css-1d391kg .stMarkdown {{
        color: {COLORS['white']};
    }}
    
    /* Cards and containers */
    .metric-card {{
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        font-weight: 500;
        color: {COLORS['dark']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 2.25rem;
        font-weight: 700;
        color: {COLORS['primary']};
        line-height: 1.2;
    }}
    
    .metric-delta {{
        font-size: 0.875rem;
        font-weight: 500;
        margin-top: 0.25rem;
    }}
    
    .metric-delta.positive {{
        color: {COLORS['success']};
    }}
    
    .metric-delta.negative {{
        color: {COLORS['danger']};
    }}
    
    /* Status badges */
    .status-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .status-connected {{
        background-color: {COLORS['success']};
        color: white;
    }}
    
    .status-disconnected {{
        background-color: {COLORS['danger']};
        color: white;
    }}
    
    .status-warning {{
        background-color: {COLORS['warning']};
        color: white;
    }}
    
    /* Tables */
    .dataframe {{
        font-size: 0.875rem;
        border: none !important;
    }}
    
    .dataframe thead th {{
        background-color: {COLORS['primary']} !important;
        color: white !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        padding: 0.75rem !important;
    }}
    
    .dataframe tbody tr:hover {{
        background-color: {COLORS['light']} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background-color: {COLORS['white']};
        border-radius: 8px 8px 0 0;
        padding: 0;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 1rem 2rem;
        font-weight: 500;
        font-size: 0.9rem;
        border-radius: 0;
        color: {COLORS['dark']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']};
        color: white;
    }}
    
    /* Section headers */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {COLORS['primary']};
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS['light']};
    }}
    
    /* Risk indicators */
    .risk-high {{
        background-color: {COLORS['danger']};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
    }}
    
    .risk-medium {{
        background-color: {COLORS['warning']};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
    }}
    
    .risk-low {{
        background-color: {COLORS['success']};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 1.75rem;
        }}
        
        .metric-value {{
            font-size: 1.75rem;
        }}
    }}
</style>
""", unsafe_allow_html=True)


def api_call(endpoint: str, method: str = "GET", data: Optional[dict] = None) -> Optional[dict]:
    """Make API call with error handling."""
    headers = {"x-api-key": st.session_state.api_key}
    url = f"{st.session_state.api_base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = httpx.get(url, headers=headers, timeout=10.0)
        elif method == "POST":
            response = httpx.post(url, headers=headers, json=data, timeout=10.0)
        else:
            return None
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def render_header():
    """Render professional header."""
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">AeroLine Risk Orchestrator</h1>
        <p class="main-subtitle">Enterprise Air-to-Floor Risk Management Platform</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render professional sidebar."""
    with st.sidebar:
        st.markdown("""
        <style>
            .sidebar-header {
                color: white;
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-header">System Configuration</div>', unsafe_allow_html=True)
        
        # API Configuration
        with st.expander("API Settings", expanded=True):
            api_key = st.text_input(
                "API Key", 
                value=st.session_state.api_key, 
                type="password",
                help="Authentication key for API access"
            )
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
            
            api_base = st.text_input(
                "API Base URL",
                value=st.session_state.api_base_url,
                help="Base URL for the AeroLine API"
            )
            if api_base != st.session_state.api_base_url:
                st.session_state.api_base_url = api_base
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Test Connection", use_container_width=True):
                    result = api_call("/health")
                    if result and result.get("status") == "ok":
                        st.success("Connected")
                        st.session_state.snowflake_connected = True
                    else:
                        st.error("Connection Failed")
                        st.session_state.snowflake_connected = False
        
        # System Status
        st.markdown('<div class="sidebar-header">System Status</div>', unsafe_allow_html=True)
        
        if st.session_state.snowflake_connected:
            st.markdown('<span class="status-badge status-connected">CONNECTED</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-disconnected">DISCONNECTED</span>', unsafe_allow_html=True)
        
        # Environment Info
        config = api_call("/config")
        if config:
            st.info(f"Database: {config.get('snowflake', {}).get('database', 'N/A')}")
            st.info(f"Warehouse: {config.get('snowflake', {}).get('warehouse', 'N/A')}")
        
        # System Actions
        st.markdown('<div class="sidebar-header">System Actions</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Refresh Scores", use_container_width=True):
                result = api_call("/scores/refresh", method="POST")
                if result:
                    st.success("Refreshed")
        
        with col2:
            if st.button("Load Sample Data", use_container_width=True):
                flights_result = api_call("/flights/ingest/sample", method="POST")
                machines_result = api_call("/machines/ingest/sample", method="POST")
                if flights_result or machines_result:
                    st.success("Data Loaded")


def render_kpis():
    """Render KPI cards with professional styling."""
    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
    
    summary = api_call("/scores/summary")
    
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average FRS</div>
                <div class="metric-value">{summary.get('avg_frs', 0.5):.2f}</div>
                <div class="metric-delta negative">{summary.get('high_frs_count', 0)} high risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average FLS</div>
                <div class="metric-value">{summary.get('avg_fls', 0.5):.2f}</div>
                <div class="metric-delta negative">{summary.get('high_fls_count', 0)} high risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Actions Required</div>
                <div class="metric-value">{summary.get('actions_needed', 0)}</div>
                <div class="metric-delta">Pending execution</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            otif_lift = summary.get('actions_needed', 0) * 0.15
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">OTIF Improvement</div>
                <div class="metric-value">+{otif_lift:.1f}%</div>
                <div class="metric-delta positive">Projected impact</div>
            </div>
            """, unsafe_allow_html=True)


def render_flights_table():
    """Render flights table with professional styling."""
    st.markdown('<div class="section-header">Flight Operations Monitor</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        flights_data = api_call("/flights/live")
        
        if flights_data and flights_data.get("flights"):
            df = pd.DataFrame(flights_data["flights"])
            
            if "FRS" not in df.columns:
                df["FRS"] = pd.Series([0.3, 0.75, 0.82, 0.35, 0.91] * (len(df) // 5 + 1))[:len(df)]
            
            df["Risk Level"] = df["FRS"].apply(
                lambda x: "HIGH" if x > 0.7 else "MEDIUM" if x > 0.4 else "LOW"
            )
            
            # Style the dataframe
            styled_df = df[["callsign", "origin_country", "lat", "lon", "velocity", "FRS", "Risk Level"]].head(10)
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "FRS": st.column_config.ProgressColumn(
                        "FRS",
                        help="Flight Risk Score",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    ),
                    "velocity": st.column_config.NumberColumn(
                        "Velocity",
                        help="Speed in m/s",
                        format="%.1f m/s",
                    ),
                    "lat": st.column_config.NumberColumn("Latitude", format="%.4f"),
                    "lon": st.column_config.NumberColumn("Longitude", format="%.4f"),
                }
            )
            
            st.caption(f"Data Source: {flights_data.get('source', 'unknown').upper()} | Total Flights: {flights_data.get('total', 0)}")
    
    with col2:
        if flights_data and flights_data.get("flights"):
            df_map = pd.DataFrame(flights_data["flights"])
            df_map = df_map.dropna(subset=["lat", "lon"])
            
            if not df_map.empty:
                view_state = pdk.ViewState(
                    latitude=df_map["lat"].mean(),
                    longitude=df_map["lon"].mean(),
                    zoom=2,
                    pitch=0
                )
                
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=df_map,
                    get_position=["lon", "lat"],
                    get_color=[30, 58, 95, 200],
                    get_radius=50000,
                    pickable=True
                )
                
                deck = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{callsign}\n{origin_country}"},
                    map_style="mapbox://styles/mapbox/light-v10"
                )
                
                st.pydeck_chart(deck)


def render_machines_table():
    """Render machines table with professional styling."""
    st.markdown('<div class="section-header">Manufacturing Equipment Status</div>', unsafe_allow_html=True)
    
    machines_status = api_call("/machines/status")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        machines_df = pd.DataFrame({
            "Machine ID": ["M-01", "M-02", "M-03", "M-04", "M-05"],
            "Type": ["L", "M", "H", "M", "L"],
            "Tool Wear": [42, 170, 26, 72, 225],
            "Temperature": [300.7, 304.2, 299.6, 300.8, 303.7],
            "FLS": [0.25, 0.68, 0.18, 0.28, 0.71],
            "Status": ["Operational", "Warning", "Operational", "Operational", "Critical"]
        })
        
        st.dataframe(
            machines_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "FLS": st.column_config.ProgressColumn(
                    "FLS",
                    help="Failure Likelihood Score",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                ),
                "Tool Wear": st.column_config.NumberColumn(
                    "Tool Wear",
                    format="%d units",
                ),
                "Temperature": st.column_config.NumberColumn(
                    "Temperature",
                    format="%.1f K",
                ),
            }
        )
    
    with col2:
        fig = go.Figure(data=[
            go.Bar(
                x=machines_df["Machine ID"],
                y=machines_df["FLS"],
                marker_color=machines_df["FLS"].apply(
                    lambda x: COLORS['danger'] if x > 0.65 else COLORS['warning'] if x > 0.4 else COLORS['success']
                ),
                text=machines_df["FLS"].apply(lambda x: f"{x:.2f}"),
                textposition='outside',
            )
        ])
        
        fig.update_layout(
            title="FLS Distribution by Machine",
            xaxis_title="Machine ID",
            yaxis_title="Failure Likelihood Score",
            height=350,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter, sans-serif"),
            title_font_size=16,
            title_font_color=COLORS['primary']
        )
        
        fig.update_xaxes(gridcolor=COLORS['light'])
        fig.update_yaxes(gridcolor=COLORS['light'])
        
        st.plotly_chart(fig, use_container_width=True)


def render_risk_join():
    """Render risk assessment and prescriptions."""
    st.markdown('<div class="section-header">Risk Assessment & Prescriptions</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        action_filter = st.selectbox(
            "Filter by Action",
            ["All", "EXPEDITE", "PULL_SPARES", "RESCHEDULE", "NO_ACTION"],
            label_visibility="visible"
        )
    
    with col2:
        min_roi = st.number_input("Minimum ROI ($)", value=0, step=1000)
    
    with col3:
        if st.button("Generate Prescriptions", use_container_width=True):
            result = api_call("/prescriptions/generate", method="POST")
            if result:
                st.success(f"Generated {result.get('prescriptions_generated', 0)} prescriptions")
    
    params = {}
    if action_filter != "All":
        params["action_filter"] = action_filter
    if min_roi > 0:
        params["min_roi"] = min_roi
    
    prescriptions = api_call(f"/prescriptions?{'&'.join(f'{k}={v}' for k, v in params.items())}")
    
    if prescriptions and prescriptions.get("prescriptions"):
        df = pd.DataFrame(prescriptions["prescriptions"])
        
        st.dataframe(
            df[["job_id", "machine_id", "callsign", "frs", "fls", "roi", "action"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "frs": st.column_config.ProgressColumn("FRS", format="%.2f", min_value=0, max_value=1),
                "fls": st.column_config.ProgressColumn("FLS", format="%.2f", min_value=0, max_value=1),
                "roi": st.column_config.NumberColumn("ROI", format="$%.0f"),
            }
        )
        
        st.markdown('<div class="section-header">Prescription Details</div>', unsafe_allow_html=True)
        
        for _, row in df.iterrows():
            with st.expander(f"Job {row['job_id']} - {row['action']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Risk Metrics:**")
                    st.write(f"- Flight Risk Score: {row['frs']:.2f}")
                    st.write(f"- Failure Likelihood Score: {row['fls']:.2f}")
                    st.write(f"- Return on Investment: ${row['roi']:.0f}")
                
                with col2:
                    st.markdown("**Decision Analysis:**")
                    explain = row.get("explain_json", {})
                    if isinstance(explain, str):
                        try:
                            explain = json.loads(explain)
                        except:
                            explain = {"raw": explain}
                    
                    if "triggers" in explain:
                        st.write("Risk Triggers:", ", ".join(explain["triggers"]))
                    if "decision_rationale" in explain:
                        st.write("Rationale:", explain["decision_rationale"])


def render_whatif():
    """Render what-if analysis panel."""
    st.markdown('<div class="section-header">Scenario Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Input Parameters")
        
        expedite_cost = st.slider(
            "Expedite Cost ($)",
            min_value=1000,
            max_value=10000,
            value=3000,
            step=500,
            format="$%d"
        )
        
        downtime_cost = st.slider(
            "Downtime Cost ($)",
            min_value=1000,
            max_value=10000,
            value=3000,
            step=500,
            format="$%d"
        )
        
        otif_value = st.slider(
            "OTIF Value ($)",
            min_value=5000,
            max_value=20000,
            value=10000,
            step=1000,
            format="$%d"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            frs = st.number_input(
                "Flight Risk Score",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                format="%.2f"
            )
        
        with col_b:
            fls = st.number_input(
                "Failure Likelihood Score",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                format="%.2f"
            )
        
        if st.button("Run Analysis", type="primary", use_container_width=True):
            data = {
                "expedite_cost": expedite_cost,
                "downtime_cost": downtime_cost,
                "otif_value": otif_value,
                "frs": frs,
                "fls": fls
            }
            
            result = api_call("/whatif", method="POST", data=data)
            
            if result:
                st.session_state.whatif_result = result
    
    with col2:
        st.markdown("### Analysis Results")
        
        if "whatif_result" in st.session_state:
            result = st.session_state.whatif_result
            
            # Display metrics
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Recommended Action", result['action'])
            with metric_col2:
                st.metric("Expected ROI", f"${result['roi']:.0f}")
            
            if "explanation" in result:
                explain = result["explanation"]
                
                if "risk_assessment" in explain:
                    assessment = explain["risk_assessment"]
                    st.markdown("**Risk Assessment**")
                    risk_data = pd.DataFrame({
                        "Metric": ["Overall Risk", "FRS Level", "FLS Level"],
                        "Value": [
                            assessment.get('overall', 'N/A'),
                            assessment.get('frs_level', 'N/A'),
                            assessment.get('fls_level', 'N/A')
                        ]
                    })
                    st.table(risk_data)
                
                if "decision_rationale" in explain:
                    st.info(explain["decision_rationale"])
                
                if "cost_analysis" in explain:
                    costs = explain["cost_analysis"].get(result["action"], {}).get("costs", {})
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=list(costs.keys()),
                            y=list(costs.values()),
                            marker_color=[COLORS['danger'], COLORS['warning'], COLORS['success']],
                            text=[f"${v:.0f}" for v in costs.values()],
                            textposition='outside',
                        )
                    ])
                    
                    fig.update_layout(
                        title="Cost Breakdown Analysis",
                        xaxis_title="Cost Category",
                        yaxis_title="Amount ($)",
                        height=300,
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family="Inter, sans-serif")
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Configure parameters and click 'Run Analysis' to see results")


def main():
    """Main application."""
    render_header()
    render_sidebar()
    
    if not st.session_state.snowflake_connected:
        st.warning("System not connected. Please configure API connection in the sidebar.")
        health = api_call("/health")
        if health and health.get("status") == "ok":
            st.session_state.snowflake_connected = True
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Flight Operations", "Equipment Status", "Prescriptions", "Scenario Analysis"])
    
    with tab1:
        render_kpis()
        col1, col2 = st.columns(2)
        with col1:
            render_flights_table()
        with col2:
            render_machines_table()
    
    with tab2:
        render_flights_table()
    
    with tab3:
        render_machines_table()
    
    with tab4:
        render_risk_join()
    
    with tab5:
        render_whatif()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f'<p style="text-align: center; color: {COLORS["dark"]}; font-size: 0.875rem;">AeroLine Risk Orchestrator v1.0.0 | Powered by Snowflake</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()