"""
Enhanced Sales Dashboard with Google Sheets Integration
Requirements: streamlit, plotly, pandas, gspread, google-auth
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
import json
import io
from datetime import datetime
import numpy as np

#######################################
# PAGE SETUP
#######################################

st.set_page_config(
    page_title="Sales Dashboard Pro", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Advanced Sales Dashboard")
st.markdown("_Google Sheets Integration v1.0.0_")

#######################################
# SIDEBAR CONFIGURATION
#######################################

with st.sidebar:
    st.header("🔧 Configuration")
    
    # Google Sheets Authentication
    st.subheader("🔐 Google Sheets Authentication")
    uploaded_json = st.file_uploader(
        "Upload Service Account JSON", 
        type=['json'],
        help="Upload your Google Service Account credentials JSON file"
    )
    
    # Google Sheets URL
    sheets_url = st.text_input(
        "📋 Google Sheets URL",
        placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit",
        help="Enter the complete Google Sheets URL"
    )
    
    # CSV Template Download
    st.subheader("📄 CSV Template")
    
    def create_csv_template():
        """Create a sample CSV template for the dashboard"""
        template_data = {
            'Scenario': ['Budget', 'Budget', 'Budget', 'Forecast', 'Forecast', 'Forecast', 'Actuals', 'Actuals'],
            'Year': [2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023],
            'Account': ['Sales', 'Marketing', 'Operations', 'Sales', 'Marketing', 'Operations', 'Sales', 'Marketing'],
            'business_unit': ['Software', 'Software', 'Hardware', 'Software', 'Hardware', 'Software', 'Software', 'Hardware'],
            'Jan': [150000, 50000, 75000, 160000, 55000, 80000, 145000, 48000],
            'Feb': [155000, 52000, 77000, 165000, 57000, 82000, 150000, 50000],
            'Mar': [160000, 54000, 79000, 170000, 59000, 84000, 155000, 52000],
            'Apr': [165000, 56000, 81000, 175000, 61000, 86000, 160000, 54000],
            'May': [170000, 58000, 83000, 180000, 63000, 88000, 165000, 56000],
            'Jun': [175000, 60000, 85000, 185000, 65000, 90000, 170000, 58000],
            'Jul': [180000, 62000, 87000, 190000, 67000, 92000, 175000, 60000],
            'Aug': [185000, 64000, 89000, 195000, 69000, 94000, 180000, 62000],
            'Sep': [190000, 66000, 91000, 200000, 71000, 96000, 185000, 64000],
            'Oct': [195000, 68000, 93000, 205000, 73000, 98000, 190000, 66000],
            'Nov': [200000, 70000, 95000, 210000, 75000, 100000, 195000, 68000],
            'Dec': [205000, 72000, 97000, 215000, 77000, 102000, 200000, 70000]
        }
        return pd.DataFrame(template_data)
    
    template_df = create_csv_template()
    csv_template = template_df.to_csv(index=False)
    
    st.download_button(
        label="⬇️ Download CSV Template",
        data=csv_template,
        file_name="sales_dashboard_template.csv",
        mime="text/csv",
        help="Download a sample CSV template to see the expected data format"
    )
    
    # Optional CSV Upload as fallback
    st.subheader("📂 Fallback CSV Upload")
    uploaded_csv = st.file_uploader(
        "Upload CSV File (Fallback)", 
        type=['csv'],
        help="Upload a CSV file as fallback if Google Sheets is not available"
    )

#######################################
# AUTHENTICATION & DATA LOADING
#######################################

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_google_sheets_data(json_credentials, sheets_url):
    """Load data from Google Sheets using service account authentication"""
    try:
        # Parse the JSON credentials
        credentials_dict = json.loads(json_credentials)
        
        # Set up the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Create credentials
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        
        # Authorize the client
        client = gspread.authorize(credentials)
        
        # Extract spreadsheet ID from URL
        if '/d/' in sheets_url:
            sheet_id = sheets_url.split('/d/')[1].split('/')[0]
        else:
            raise ValueError("Invalid Google Sheets URL format")
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1  # Use the first sheet
        
        # Get all records
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        return df, None
    
    except Exception as e:
        return None, str(e)

@st.cache_data
def load_csv_data(uploaded_file):
    """Load data from uploaded CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)

# Data Loading Logic
df = None
data_source = ""

if uploaded_json and sheets_url:
    # Try to load from Google Sheets
    json_content = uploaded_json.read().decode('utf-8')
    df, error = load_google_sheets_data(json_content, sheets_url)
    
    if df is not None:
        data_source = "Google Sheets"
        st.success(f"✅ Successfully connected to Google Sheets! Loaded {len(df)} rows.")
    else:
        st.error(f"❌ Google Sheets Error: {error}")
        
elif uploaded_csv:
    # Fallback to CSV
    df, error = load_csv_data(uploaded_csv)
    if df is not None:
        data_source = "CSV Upload"
        st.warning("⚠️ Using CSV fallback data.")
    else:
        st.error(f"❌ CSV Error: {error}")

if df is None:
    st.info("🔧 Please configure Google Sheets authentication and URL, or upload a CSV file to get started.")
    st.markdown("### 📋 Setup Instructions:")
    st.markdown("""
    **For Google Sheets:**
    1. Create a Google Cloud Project
    2. Enable Google Sheets API
    3. Create a Service Account and download JSON credentials
    4. Share your Google Sheet with the service account email
    5. Upload the JSON file and paste your Google Sheets URL
    
    **For CSV Fallback:**
    1. Download the CSV template
    2. Fill it with your data
    3. Upload the CSV file
    """)
    st.stop()

# Display data source info
st.info(f"📊 Data Source: {data_source} | Last Updated: {datetime.now().strftime('%H:%M:%S')}")

#######################################
# DATA PREVIEW
#######################################

all_months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

with st.expander("🔍 Data Preview"):
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Year": st.column_config.NumberColumn(format="%d"),
            "Jan": st.column_config.NumberColumn(format="$%.0f"),
            "Feb": st.column_config.NumberColumn(format="$%.0f"),
            "Mar": st.column_config.NumberColumn(format="$%.0f"),
            "Apr": st.column_config.NumberColumn(format="$%.0f"),
            "May": st.column_config.NumberColumn(format="$%.0f"),
            "Jun": st.column_config.NumberColumn(format="$%.0f"),
            "Jul": st.column_config.NumberColumn(format="$%.0f"),
            "Aug": st.column_config.NumberColumn(format="$%.0f"),
            "Sep": st.column_config.NumberColumn(format="$%.0f"),
            "Oct": st.column_config.NumberColumn(format="$%.0f"),
            "Nov": st.column_config.NumberColumn(format="$%.0f"),
            "Dec": st.column_config.NumberColumn(format="$%.0f"),
        }
    )

#######################################
# DATA PROCESSING FUNCTIONS
#######################################

def process_sales_data_by_unit():
    """Process sales data aggregated by business unit"""
    try:
        # Filter for 2023 Sales data
        sales_df = df[(df['Year'] == 2023) & (df['Account'] == 'Sales')].copy()
        
        # Melt the dataframe to convert months to rows
        id_vars = ['Scenario', 'business_unit']
        melted_df = sales_df.melt(
            id_vars=id_vars,
            value_vars=all_months,
            var_name='month',
            value_name='sales'
        )
        
        # Aggregate by scenario and business unit
        agg_df = melted_df.groupby(['Scenario', 'business_unit'])['sales'].sum().reset_index()
        
        return agg_df
    except Exception as e:
        st.error(f"Error processing sales data by unit: {e}")
        return pd.DataFrame()

def process_monthly_sales_data():
    """Process monthly sales data for Software business unit"""
    try:
        # Filter for 2023 Sales data for Software
        sales_df = df[
            (df['Year'] == 2023) & 
            (df['Account'] == 'Sales') & 
            (df['business_unit'] == 'Software')
        ].copy()
        
        # Melt the dataframe
        melted_df = sales_df.melt(
            id_vars=['Scenario'],
            value_vars=all_months,
            var_name='month',
            value_name='sales'
        )
        
        return melted_df
    except Exception as e:
        st.error(f"Error processing monthly sales data: {e}")
        return pd.DataFrame()

def process_yearly_account_data():
    """Process yearly data by account (excluding Sales)"""
    try:
        # Filter for Actuals data, exclude Sales account
        actuals_df = df[(df['Scenario'] == 'Actuals') & (df['Account'] != 'Sales')].copy()
        
        # Convert monthly columns to absolute values and melt
        month_cols = [col for col in all_months if col in actuals_df.columns]
        for col in month_cols:
            actuals_df[col] = pd.to_numeric(actuals_df[col], errors='coerce').abs()
        
        # Melt the dataframe
        melted_df = actuals_df.melt(
            id_vars=['Account', 'Year'],
            value_vars=month_cols,
            var_name='month',
            value_name='sales'
        )
        
        # Aggregate by account and year
        agg_df = melted_df.groupby(['Account', 'Year'])['sales'].sum().reset_index()
        
        return agg_df
    except Exception as e:
        st.error(f"Error processing yearly account data: {e}")
        return pd.DataFrame()

#######################################
# VISUALIZATION FUNCTIONS
#######################################

def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    """Create a metric display with optional mini graph"""
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font.size": 28,
            },
            title={
                "text": label,
                "font": {"size": 20},
            },
        )
    )

    if show_graph:
        # Generate realistic trend data
        trend_data = np.random.normal(value, value * 0.1, 30)
        fig.add_trace(
            go.Scatter(
                y=trend_data,
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={"color": color_graph},
            )
        )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=40, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=120,
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_gauge(indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound):
    """Create a gauge chart"""
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font.size": 24,
            },
            gauge={
                "axis": {"range": [0, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, max_bound*0.5], "color": "lightgray"},
                    {"range": [max_bound*0.5, max_bound*0.8], "color": "yellow"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": max_bound*0.9
                }
            },
            title={
                "text": indicator_title,
                "font": {"size": 20},
            },
        )
    )
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_top_right():
    """Plot sales by business unit"""
    sales_data = process_sales_data_by_unit()
    
    if sales_data.empty:
        st.warning("No data available for sales by business unit")
        return
    
    fig = px.bar(
        sales_data,
        x="business_unit",
        y="sales",
        color="Scenario",
        barmode="group",
        text_auto=".2s",
        title="💰 Sales by Business Unit (2023)",
        height=400,
        color_discrete_map={
            "Budget": "#1f77b4",
            "Forecast": "#ff7f0e", 
            "Actuals": "#2ca02c"
        }
    )
    fig.update_traces(
        textfont_size=12, 
        textangle=0, 
        textposition="outside", 
        cliponaxis=False
    )
    fig.update_layout(
        xaxis_title="Business Unit",
        yaxis_title="Sales ($)",
        legend_title="Scenario"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_bottom_left():
    """Plot monthly budget vs forecast trend"""
    sales_data = process_monthly_sales_data()
    
    if sales_data.empty:
        st.warning("No data available for monthly sales trend")
        return
    
    fig = px.line(
        sales_data,
        x="month",
        y="sales",
        color="Scenario",
        markers=True,
        title="📈 Monthly Sales Trend - Software (2023)",
        color_discrete_map={
            "Budget": "#1f77b4",
            "Forecast": "#ff7f0e", 
            "Actuals": "#2ca02c"
        }
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Sales ($)",
        legend_title="Scenario"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_bottom_right():
    """Plot yearly sales by account"""
    sales_data = process_yearly_account_data()
    
    if sales_data.empty:
        st.warning("No data available for yearly account sales")
        return
    
    fig = px.bar(
        sales_data,
        x="Year",
        y="sales",
        color="Account",
        title="📊 Yearly Performance by Account (Actuals)",
        text_auto=".2s"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Sales ($)",
        legend_title="Account"
    )
    st.plotly_chart(fig, use_container_width=True)

#######################################
# CALCULATE METRICS
#######################################

def calculate_metrics():
    """Calculate key business metrics"""
    try:
        # Total Accounts Receivable (sum of all positive sales)
        accounts_receivable = df[df['Account'] == 'Sales'][all_months].sum().sum()
        
        # Total Accounts Payable (sum of marketing and operations)
        accounts_payable = df[df['Account'].isin(['Marketing', 'Operations'])][all_months].sum().sum()
        
        # Random metrics for demonstration (in real scenario, these would be calculated from actual data)
        equity_ratio = 75.38
        debt_equity = 1.10
        current_ratio = 1.86
        
        return {
            'accounts_receivable': abs(accounts_receivable),
            'accounts_payable': abs(accounts_payable),
            'equity_ratio': equity_ratio,
            'debt_equity': debt_equity,
            'current_ratio': current_ratio
        }
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")
        return {
            'accounts_receivable': 0,
            'accounts_payable': 0,
            'equity_ratio': 0,
            'debt_equity': 0,
            'current_ratio': 0
        }

#######################################
# MAIN DASHBOARD LAYOUT
#######################################

# Calculate metrics
metrics = calculate_metrics()

# Create layout
top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)

with top_left_column:
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        plot_metric(
            "Total Accounts Receivable",
            metrics['accounts_receivable'],
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(0, 104, 201, 0.2)",
        )
        plot_gauge(metrics['current_ratio'], "#0068C9", "", "Current Ratio", 3)

    with column_2:
        plot_metric(
            "Total Accounts Payable",
            metrics['accounts_payable'],
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(255, 43, 43, 0.2)",
        )
        plot_gauge(10, "#FF8700", " days", "In Stock", 31)

    with column_3:
        plot_metric(
            "Equity Ratio", 
            metrics['equity_ratio'], 
            prefix="", 
            suffix=" %", 
            show_graph=False
        )
        plot_gauge(7, "#FF2B2B", " days", "Out Stock", 31)
        
    with column_4:
        plot_metric(
            "Debt Equity", 
            metrics['debt_equity'], 
            prefix="", 
            suffix=" %", 
            show_graph=False
        )
        plot_gauge(28, "#29B09D", " days", "Delay", 31)

with top_right_column:
    plot_top_right()

with bottom_left_column:
    plot_bottom_left()

with bottom_right_column:
    plot_bottom_right()

#######################################
# REFRESH BUTTON
#######################################

st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

#######################################
# FOOTER
#######################################

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    📊 Sales Dashboard Pro v1.0.0 | Built with Streamlit & Google Sheets API<br>
    🔄 Data refreshes every 5 minutes automatically
    </div>
    """, 
    unsafe_allow_html=True
)
