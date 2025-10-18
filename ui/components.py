"""Reusable components for Streamlit UI."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional, Any


def create_risk_gauge(score: float, title: str = "Risk Score") -> go.Figure:
    """
    Create a gauge chart for risk scores.
    
    Args:
        score: Risk score between 0 and 1
        title: Title for the gauge
        
    Returns:
        Plotly gauge figure
    """
    # Determine color based on score
    if score > 0.7:
        color = "red"
    elif score > 0.4:
        color = "yellow"
    else:
        color = "green"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 0.5},
        gauge={
            'axis': {'range': [None, 1]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 0.4], 'color': "lightgray"},
                {'range': [0.4, 0.7], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig


def create_time_series_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: Optional[str] = None
) -> go.Figure:
    """
    Create a time series line chart.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis (time)
        y_col: Column name for y-axis
        title: Chart title
        color_col: Optional column for color grouping
        
    Returns:
        Plotly line chart figure
    """
    if color_col:
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            markers=True
        )
    else:
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=title,
            markers=True
        )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=y_col,
        hovermode="x unified",
        height=400
    )
    
    return fig


def create_heatmap(
    data: List[List[float]],
    x_labels: List[str],
    y_labels: List[str],
    title: str = "Risk Heatmap"
) -> go.Figure:
    """
    Create a heatmap for risk visualization.
    
    Args:
        data: 2D array of values
        x_labels: Labels for x-axis
        y_labels: Labels for y-axis
        title: Chart title
        
    Returns:
        Plotly heatmap figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale='RdYlGn_r',
        colorbar=dict(title="Risk Level"),
        text=data,
        texttemplate="%{text:.2f}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Machines",
        yaxis_title="Flights",
        height=400
    )
    
    return fig


def create_action_distribution_pie(actions_count: Dict[str, int]) -> go.Figure:
    """
    Create a pie chart for action distribution.
    
    Args:
        actions_count: Dictionary with action counts
        
    Returns:
        Plotly pie chart figure
    """
    colors = {
        "NO_ACTION": "#00cc00",
        "EXPEDITE": "#ffa500",
        "PULL_SPARES": "#ff6b6b",
        "RESCHEDULE": "#ff4b4b"
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(actions_count.keys()),
        values=list(actions_count.values()),
        hole=0.3,
        marker=dict(
            colors=[colors.get(k, "#888888") for k in actions_count.keys()]
        )
    )])
    
    fig.update_layout(
        title="Action Distribution",
        height=300,
        showlegend=True
    )
    
    return fig


def render_metric_card(
    title: str,
    value: Any,
    delta: Optional[str] = None,
    delta_color: str = "normal"
) -> None:
    """
    Render a styled metric card.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta text
        delta_color: Color scheme for delta
    """
    st.markdown(
        f"""
        <div class="kpi-card">
            <h4>{title}</h4>
            <h2>{value}</h2>
            {f'<p style="color: {"green" if delta_color == "normal" else "red"};">{delta}</p>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def create_cost_waterfall(
    costs: Dict[str, float],
    title: str = "Cost Breakdown"
) -> go.Figure:
    """
    Create a waterfall chart for cost breakdown.
    
    Args:
        costs: Dictionary of cost components
        title: Chart title
        
    Returns:
        Plotly waterfall chart figure
    """
    # Prepare data for waterfall
    x = ["OTIF Value"] + list(costs.keys()) + ["Net ROI"]
    
    # Calculate measures
    otif = costs.get("otif_value", 10000)
    measures = [otif]
    
    for key, value in costs.items():
        if key != "otif_value":
            measures.append(-abs(value))  # Costs are negative
    
    # Calculate final ROI
    roi = otif + sum(measures[1:])
    measures.append(roi)
    
    # Create text labels
    text = [f"${abs(m):,.0f}" for m in measures]
    
    # Determine colors
    colors = ["green"] + ["red"] * (len(costs) - 1) + ["blue"]
    
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=["absolute"] + ["relative"] * (len(costs) - 1) + ["total"],
        x=x,
        textposition="outside",
        text=text,
        y=measures,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "red"}},
        increasing={"marker": {"color": "green"}},
        totals={"marker": {"color": "blue"}}
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=400
    )
    
    return fig


def create_risk_matrix(
    frs_values: List[float],
    fls_values: List[float],
    labels: List[str]
) -> go.Figure:
    """
    Create a risk matrix scatter plot.
    
    Args:
        frs_values: List of FRS values
        fls_values: List of FLS values
        labels: List of labels for points
        
    Returns:
        Plotly scatter plot figure
    """
    # Determine colors based on risk levels
    colors = []
    for frs, fls in zip(frs_values, fls_values):
        if frs > 0.7 and fls > 0.6:
            colors.append("red")
        elif frs > 0.5 or fls > 0.5:
            colors.append("yellow")
        else:
            colors.append("green")
    
    fig = go.Figure()
    
    # Add quadrant backgrounds
    fig.add_shape(
        type="rect", x0=0, y0=0, x1=0.5, y1=0.5,
        fillcolor="lightgreen", opacity=0.2
    )
    fig.add_shape(
        type="rect", x0=0.5, y0=0, x1=1, y1=0.5,
        fillcolor="yellow", opacity=0.2
    )
    fig.add_shape(
        type="rect", x0=0, y0=0.5, x1=0.5, y1=1,
        fillcolor="yellow", opacity=0.2
    )
    fig.add_shape(
        type="rect", x0=0.5, y0=0.5, x1=1, y1=1,
        fillcolor="lightcoral", opacity=0.2
    )
    
    # Add scatter points
    fig.add_trace(go.Scatter(
        x=frs_values,
        y=fls_values,
        mode='markers+text',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=2, color='black')
        ),
        text=labels,
        textposition="top center"
    ))
    
    fig.update_layout(
        title="Risk Matrix (FRS vs FLS)",
        xaxis_title="Flight Risk Score (FRS)",
        yaxis_title="Failure Likelihood Score (FLS)",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        height=500,
        showlegend=False
    )
    
    # Add threshold lines
    fig.add_hline(y=0.6, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_vline(x=0.7, line_dash="dash", line_color="red", opacity=0.5)
    
    return fig


def format_alert_message(
    job_id: str,
    frs: float,
    fls: float,
    action: str,
    severity: str = "INFO"
) -> str:
    """
    Format an alert message with styling.
    
    Args:
        job_id: Job identifier
        frs: Flight Risk Score
        fls: Failure Likelihood Score
        action: Recommended action
        severity: Alert severity level
        
    Returns:
        Formatted HTML alert message
    """
    color_map = {
        "CRITICAL": "#ff4b4b",
        "WARNING": "#ffa500",
        "INFO": "#00cc00"
    }
    
    color = color_map.get(severity, "#888888")
    
    return f"""
    <div style="
        background-color: {color}20;
        border-left: 4px solid {color};
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    ">
        <strong style="color: {color};">[{severity}]</strong> Job {job_id}<br>
        FRS: {frs:.2f} | FLS: {fls:.2f}<br>
        <strong>Action Required:</strong> {action}
    </div>
    """
