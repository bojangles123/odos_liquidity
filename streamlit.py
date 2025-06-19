import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def calculate_yield(total_pool_size, daily_volume, percent_in_range):
    """Calculate liquidity pool yields"""
    fee_tier = 0.006  # Fixed at 0.6%
    our_total_position_percent = 0.68  # Fixed at 68%
    
    our_total_position = total_pool_size * our_total_position_percent
    our_in_range_position = our_total_position * (percent_in_range / 100)
    
    # Calculate total in-range liquidity
    others_position = total_pool_size * (1 - our_total_position_percent)
    # Assume others are 100% in range for simplicity
    total_in_range = others_position + our_in_range_position
    
    daily_fees = daily_volume * fee_tier
    annual_fees = daily_fees * 365
    
    our_share = our_in_range_position / total_in_range if total_in_range > 0 else 0
    our_annual_yield = annual_fees * our_share
    our_monthly_yield = our_annual_yield / 12
    our_apr = (our_annual_yield / our_in_range_position) * 100 if our_in_range_position > 0 else 0
    
    return {
        'our_total_position': our_total_position,
        'our_in_range_position': our_in_range_position,
        'our_out_of_range_position': our_total_position - our_in_range_position,
        'total_in_range': total_in_range,
        'daily_fees': daily_fees,
        'annual_fees': annual_fees,
        'our_share': our_share * 100,
        'our_annual_yield': our_annual_yield,
        'our_monthly_yield': our_monthly_yield,
        'our_apr': our_apr
    }

# Streamlit App
st.set_page_config(page_title="LP Yield Calculator", layout="wide")

st.title("Liquidity Pool Yield Calculator")
st.markdown("Calculate yields based on your position allocation in the liquidity pool")

# Sidebar for inputs
st.sidebar.header("Pool Parameters")

# Input fields
total_pool_size = st.sidebar.number_input(
    "Total LP Pool Size ($)", 
    min_value=0.0, 
    value=147000.0, 
    step=1000.0,
    format="%.0f"
)

daily_volume = st.sidebar.number_input(
    "Daily Trading Volume ($)", 
    min_value=0.0, 
    value=100000.0, 
    step=1000.0,
    format="%.0f"
)

percent_in_range = st.sidebar.slider(
    "% of Our Position In Range", 
    min_value=0.0, 
    max_value=100.0, 
    value=100.0, 
    step=5.0,
    format="%.0f%%"
)

# Fixed parameters display
st.sidebar.markdown("---")
st.sidebar.markdown("**Fixed Parameters:**")
st.sidebar.markdown("• Fee Tier: 0.6%")
st.sidebar.markdown("• Our Pool Share: 68%")

# Calculate results
results = calculate_yield(total_pool_size, daily_volume, percent_in_range)

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Monthly Yield", 
        f"${results['our_monthly_yield']:,.0f}",
        delta=f"{results['our_monthly_yield']/results['our_in_range_position']*100:.1f}% monthly return" if results['our_in_range_position'] > 0 else None
    )

with col2:
    st.metric(
        "Annual Yield", 
        f"${results['our_annual_yield']:,.0f}",
        delta=f"{results['our_apr']:.1f}% APR"
    )

with col3:
    st.metric(
        "Share of In-Range Fees", 
        f"{results['our_share']:.1f}%",
        delta=f"${results['total_in_range']:,.0f} total in-range"
    )

with col4:
    st.metric(
        "Daily Fees Earned", 
        f"${results['our_monthly_yield']/30:.0f}",
        delta=f"${results['daily_fees']:,.0f} total daily fees"
    )

# Position breakdown
st.subheader("Position Breakdown")

pos_col1, pos_col2, pos_col3 = st.columns(3)

with pos_col1:
    st.metric(
        "Our Total Position",
        f"${results['our_total_position']:,.0f}",
        delta="68% of pool"
    )

with pos_col2:
    st.metric(
        "Our In-Range Position",
        f"${results['our_in_range_position']:,.0f}",
        delta=f"{percent_in_range:.0f}% of our position"
    )

with pos_col3:
    st.metric(
        "Our Out-of-Range Position",
        f"${results['our_out_of_range_position']:,.0f}",
        delta=f"{100-percent_in_range:.0f}% of our position"
    )

# Detailed breakdown
st.subheader("Calculation Breakdown")

breakdown_data = {
    "Metric": [
        "Total Pool Size",
        "Our Pool Share",
        "Our Total Position",
        "% of Our Position In Range",
        "Our In-Range Position",
        "Our Out-of-Range Position",
        "Total In-Range Liquidity",
        "Daily Trading Volume",
        "Fee Tier",
        "Daily Fees Generated (Total)",
        "Annual Fees Generated (Total)",
        "Our Share of In-Range Fees",
        "Our Annual Yield",
        "Our Monthly Yield",
        "Our APR (on in-range capital)"
    ],
    "Value": [
        f"${total_pool_size:,.0f}",
        "68%",
        f"${results['our_total_position']:,.0f}",
        f"{percent_in_range:.0f}%",
        f"${results['our_in_range_position']:,.0f}",
        f"${results['our_out_of_range_position']:,.0f}",
        f"${results['total_in_range']:,.0f}",
        f"${daily_volume:,.0f}",
        "0.6%",
        f"${results['daily_fees']:,.0f}",
        f"${results['annual_fees']:,.0f}",
        f"{results['our_share']:.1f}%",
        f"${results['our_annual_yield']:,.0f}",
        f"${results['our_monthly_yield']:,.0f}",
        f"{results['our_apr']:.1f}%"
    ]
}

df_breakdown = pd.DataFrame(breakdown_data)
st.dataframe(df_breakdown, use_container_width=True, hide_index=True)

# Sensitivity Analysis
st.subheader("Sensitivity Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**In-Range % Sensitivity**")
    range_percentages = [0, 25, 50, 75, 100]
    range_results = []
    
    for pct in range_percentages:
        result = calculate_yield(total_pool_size, daily_volume, pct)
        range_results.append({
            'In-Range %': f"{pct}%",
            'Monthly Yield': f"${result['our_monthly_yield']:,.0f}",
            'APR': f"{result['our_apr']:.1f}%"
        })
    
    df_range = pd.DataFrame(range_results)
    st.dataframe(df_range, use_container_width=True, hide_index=True)

with col2:
    st.markdown("**Volume Sensitivity**")
    volume_range = [25000, 50000, 100000, 150000, 200000, 300000]
    volume_results = []
    
    for vol in volume_range:
        result = calculate_yield(total_pool_size, vol, percent_in_range)
        volume_results.append({
            'Daily Volume': f"${vol:,.0f}",
            'Monthly Yield': f"${result['our_monthly_yield']:,.0f}",
            'APR': f"{result['our_apr']:.1f}%"
        })
    
    df_volume = pd.DataFrame(volume_results)
    st.dataframe(df_volume, use_container_width=True, hide_index=True)

# Charts
st.subheader("Visualization")

# In-Range Percentage vs Yield Chart
range_chart_data = []
for pct in range(0, 101, 5):
    result = calculate_yield(total_pool_size, daily_volume, pct)
    range_chart_data.append({
        'In-Range Percentage': pct,
        'Monthly Yield': result['our_monthly_yield'],
        'APR': result['our_apr']
    })

df_chart = pd.DataFrame(range_chart_data)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_chart['In-Range Percentage'],
    y=df_chart['Monthly Yield'],
    mode='lines+markers',
    name='Monthly Yield ($)',
    line=dict(color='#00CC96', width=3)
))

fig.update_layout(
    title="Monthly Yield vs % of Position In Range",
    xaxis_title="% of Our Position In Range",
    yaxis_title="Monthly Yield ($)",
    template="plotly_white",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Methodology
st.subheader("Methodology")

st.markdown("### Calculation Formulas")

formula_col1, formula_col2 = st.columns(2)

with formula_col1:
    st.markdown("""
    **Position Calculations:**
    ```
    Our Total Position = Total Pool Size × 68%
    
    Our In-Range Position = Our Total Position × (% In Range / 100)
    
    Our Out-of-Range Position = Our Total Position - Our In-Range Position
    
    Others Position = Total Pool Size × 32%
    
    Total In-Range Liquidity = Others Position + Our In-Range Position
    ```
    """)

with formula_col2:
    st.markdown("""
    **Yield Calculations:**
    ```
    Daily Fees Generated = Daily Volume × 0.006
    
    Annual Fees Generated = Daily Fees × 365
    
    Our Share of Fees = Our In-Range Position / Total In-Range Liquidity
    
    Our Annual Yield = Annual Fees × Our Share
    
    Our Monthly Yield = Our Annual Yield / 12
    
    Our APR = (Our Annual Yield / Our In-Range Position) × 100
    ```
    """)

st.markdown("### Key Assumptions")
assumptions_data = {
    "Assumption": [
        "Fee Tier",
        "Our Pool Ownership",
        "Others' Position Status",
        "Fee Distribution",
        "Compounding"
    ],
    "Value": [
        "0.6% on all trades",
        "Fixed at 68% of total pool",
        "100% in-range (conservative estimate)",
        "Proportional to in-range liquidity share",
        "Not included (manual harvest assumed)"
    ]
}

df_assumptions = pd.DataFrame(assumptions_data)
st.dataframe(df_assumptions, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("*This calculator assumes others maintain 100% in-range positions. Actual yields may vary based on competitor behavior.*")
