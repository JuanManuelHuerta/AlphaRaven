import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Stock Financial Dashboard", layout="wide")

st.title("📊 Stock Financial Data Dashboard")
st.markdown("Analyze stock performance with visual segmentation and key financial metrics")

col1, col2 = st.columns([2, 1])

with col1:
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, TSLA):", value="AAPL").upper()

with col2:
    segmentation = st.selectbox(
        "Segmentation View:",
        ["Industry", "Market Capitalization", "Sector", "Geographic Region"]
    )

time_period = st.radio(
    "Select Time Period:",
    ["1M", "3M", "6M", "1Y", "5Y"],
    horizontal=True,
    index=3
)

period_map = {
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y"
}

if stock_symbol:
    try:
        with st.spinner(f"Fetching data for {stock_symbol}..."):
            stock = yf.Ticker(stock_symbol)
            info = stock.info
            hist_data = stock.history(period=period_map[time_period])
            
            if hist_data.empty or not info:
                st.error(f"❌ No data found for symbol '{stock_symbol}'. Please check the symbol and try again.")
            else:
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                previous_close = info.get('previousClose', 'N/A')
                
                if current_price != 'N/A' and previous_close != 'N/A':
                    price_change = current_price - previous_close
                    price_change_pct = (price_change / previous_close) * 100
                else:
                    price_change = 'N/A'
                    price_change_pct = 'N/A'
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="Current Price",
                        value=f"${current_price:,.2f}" if current_price != 'N/A' else 'N/A',
                        delta=f"{price_change_pct:.2f}%" if price_change_pct != 'N/A' else None
                    )
                
                with col2:
                    market_cap = info.get('marketCap', 'N/A')
                    if market_cap != 'N/A':
                        market_cap_formatted = f"${market_cap / 1e9:.2f}B"
                    else:
                        market_cap_formatted = 'N/A'
                    st.metric(label="Market Cap", value=market_cap_formatted)
                
                with col3:
                    pe_ratio = info.get('trailingPE', 'N/A')
                    st.metric(
                        label="P/E Ratio",
                        value=f"{pe_ratio:.2f}" if pe_ratio != 'N/A' else 'N/A'
                    )
                
                with col4:
                    dividend_yield = info.get('dividendYield', 0)
                    if dividend_yield:
                        dividend_yield_pct = dividend_yield * 100
                        st.metric(label="Dividend Yield", value=f"{dividend_yield_pct:.2f}%")
                    else:
                        st.metric(label="Dividend Yield", value="N/A")
                
                st.markdown("---")
                
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Chart", "📊 Financial Data", "🎯 Segmentation Analysis", "💾 Download Data"])
                
                with tab1:
                    st.subheader(f"{stock_symbol} Stock Price - {time_period}")
                    
                    fig = go.Figure()
                    
                    colors = ['green' if hist_data['Close'].iloc[i] >= hist_data['Close'].iloc[i-1] 
                             else 'red' for i in range(1, len(hist_data))]
                    colors.insert(0, 'gray')
                    
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Close'],
                        mode='lines',
                        name='Close Price',
                        line=dict(color='#1f77b4', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(31, 119, 180, 0.1)'
                    ))
                    
                    fig.update_layout(
                        height=400,
                        hovermode='x unified',
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("Trading Volume")
                    
                    fig_volume = go.Figure()
                    
                    volume_colors = ['green' if hist_data['Close'].iloc[i] >= hist_data['Close'].iloc[i-1] 
                                    else 'red' for i in range(1, len(hist_data))]
                    volume_colors.insert(0, 'gray')
                    
                    fig_volume.add_trace(go.Bar(
                        x=hist_data.index,
                        y=hist_data['Volume'],
                        name='Volume',
                        marker_color=volume_colors
                    ))
                    
                    fig_volume.update_layout(
                        height=250,
                        xaxis_title="Date",
                        yaxis_title="Volume",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_volume, use_container_width=True)
                
                with tab2:
                    st.subheader("📋 Key Financial Metrics")
                    
                    financial_data = {
                        "Metric": [
                            "Company Name",
                            "Symbol",
                            "Current Price",
                            "Previous Close",
                            "Day Change",
                            "Day Change %",
                            "52 Week High",
                            "52 Week Low",
                            "Market Cap",
                            "P/E Ratio (Trailing)",
                            "Forward P/E",
                            "PEG Ratio",
                            "Price to Book",
                            "Dividend Yield",
                            "EPS (Trailing)",
                            "Revenue",
                            "Profit Margin",
                            "Operating Margin",
                            "Return on Equity",
                            "Beta",
                            "Volume",
                            "Avg Volume",
                            "Shares Outstanding"
                        ],
                        "Value": [
                            info.get('longName', 'N/A'),
                            stock_symbol,
                            f"${current_price:,.2f}" if current_price != 'N/A' else 'N/A',
                            f"${previous_close:,.2f}" if previous_close != 'N/A' else 'N/A',
                            f"${price_change:,.2f}" if price_change != 'N/A' else 'N/A',
                            f"{price_change_pct:,.2f}%" if price_change_pct != 'N/A' else 'N/A',
                            f"${info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}" if info.get('fiftyTwoWeekHigh') != 'N/A' else 'N/A',
                            f"${info.get('fiftyTwoWeekLow', 'N/A'):,.2f}" if info.get('fiftyTwoWeekLow') != 'N/A' else 'N/A',
                            market_cap_formatted,
                            f"{pe_ratio:.2f}" if pe_ratio != 'N/A' else 'N/A',
                            f"{info.get('forwardPE', 'N/A'):.2f}" if info.get('forwardPE') != 'N/A' else 'N/A',
                            f"{info.get('pegRatio', 'N/A'):.2f}" if info.get('pegRatio') != 'N/A' else 'N/A',
                            f"{info.get('priceToBook', 'N/A'):.2f}" if info.get('priceToBook') != 'N/A' else 'N/A',
                            f"{dividend_yield_pct:.2f}%" if dividend_yield else 'N/A',
                            f"${info.get('trailingEps', 'N/A'):.2f}" if info.get('trailingEps') != 'N/A' else 'N/A',
                            f"${info.get('totalRevenue', 0) / 1e9:.2f}B" if info.get('totalRevenue') else 'N/A',
                            f"{info.get('profitMargins', 0) * 100:.2f}%" if info.get('profitMargins') else 'N/A',
                            f"{info.get('operatingMargins', 0) * 100:.2f}%" if info.get('operatingMargins') else 'N/A',
                            f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get('returnOnEquity') else 'N/A',
                            f"{info.get('beta', 'N/A'):.2f}" if info.get('beta') != 'N/A' else 'N/A',
                            f"{info.get('volume', 'N/A'):,}" if info.get('volume') != 'N/A' else 'N/A',
                            f"{info.get('averageVolume', 'N/A'):,}" if info.get('averageVolume') != 'N/A' else 'N/A',
                            f"{info.get('sharesOutstanding', 'N/A'):,}" if info.get('sharesOutstanding') != 'N/A' else 'N/A'
                        ]
                    }
                    
                    df_financial = pd.DataFrame(financial_data)
                    st.dataframe(df_financial, use_container_width=True, hide_index=True)
                
                with tab3:
                    st.subheader(f"🎯 {segmentation} Analysis")
                    
                    if segmentation == "Industry":
                        industry = info.get('industry', 'Unknown')
                        sector = info.get('sector', 'Unknown')
                        st.markdown(f"**Industry:** {industry}")
                        st.markdown(f"**Sector:** {sector}")
                        
                        segment_data = {
                            'Category': ['Your Stock', 'Industry Avg (Est.)', 'Market Avg'],
                            'P/E Ratio': [
                                pe_ratio if pe_ratio != 'N/A' else 20,
                                25,
                                22
                            ],
                            'Profit Margin': [
                                info.get('profitMargins', 0.15) * 100,
                                18,
                                15
                            ],
                            'Revenue Growth': [
                                info.get('revenueGrowth', 0.10) * 100 if info.get('revenueGrowth') else 10,
                                12,
                                8
                            ]
                        }
                        
                    elif segmentation == "Market Capitalization":
                        market_cap_value = info.get('marketCap', 0)
                        
                        if market_cap_value > 200e9:
                            cap_category = "Mega Cap (>$200B)"
                        elif market_cap_value > 10e9:
                            cap_category = "Large Cap ($10B-$200B)"
                        elif market_cap_value > 2e9:
                            cap_category = "Mid Cap ($2B-$10B)"
                        elif market_cap_value > 300e6:
                            cap_category = "Small Cap ($300M-$2B)"
                        else:
                            cap_category = "Micro Cap (<$300M)"
                        
                        st.markdown(f"**Market Cap Category:** {cap_category}")
                        st.markdown(f"**Market Cap:** {market_cap_formatted}")
                        
                        segment_data = {
                            'Category': ['Your Stock', 'Peers Avg (Est.)', 'Market Avg'],
                            'Market Cap (B)': [
                                market_cap_value / 1e9 if market_cap_value else 10,
                                50,
                                100
                            ],
                            'Trading Volume (M)': [
                                info.get('volume', 0) / 1e6,
                                20,
                                15
                            ],
                            'Beta': [
                                info.get('beta', 1.0) if info.get('beta') != 'N/A' else 1.0,
                                1.2,
                                1.0
                            ]
                        }
                        
                    elif segmentation == "Sector":
                        sector = info.get('sector', 'Unknown')
                        st.markdown(f"**Sector:** {sector}")
                        
                        segment_data = {
                            'Category': ['Your Stock', 'Sector Avg (Est.)', 'Market Avg'],
                            'ROE (%)': [
                                info.get('returnOnEquity', 0.15) * 100,
                                18,
                                15
                            ],
                            'Debt to Equity': [
                                info.get('debtToEquity', 0.5) if info.get('debtToEquity') else 0.5,
                                0.8,
                                0.6
                            ],
                            'Current Ratio': [
                                info.get('currentRatio', 1.5) if info.get('currentRatio') else 1.5,
                                1.8,
                                1.6
                            ]
                        }
                        
                    else:
                        country = info.get('country', 'Unknown')
                        st.markdown(f"**Country:** {country}")
                        
                        segment_data = {
                            'Category': ['Your Stock', 'Regional Avg (Est.)', 'Global Avg'],
                            'Revenue Growth (%)': [
                                info.get('revenueGrowth', 0.10) * 100 if info.get('revenueGrowth') else 10,
                                12,
                                10
                            ],
                            'Profit Margin (%)': [
                                info.get('profitMargins', 0.15) * 100,
                                18,
                                16
                            ],
                            'P/E Ratio': [
                                pe_ratio if pe_ratio != 'N/A' else 20,
                                22,
                                20
                            ]
                        }
                    
                    df_segment = pd.DataFrame(segment_data)
                    
                    for col in df_segment.columns[1:]:
                        fig_bar = px.bar(
                            df_segment,
                            x='Category',
                            y=col,
                            title=f"{col} Comparison",
                            color='Category',
                            color_discrete_map={
                                'Your Stock': '#00cc96',
                                df_segment['Category'][1]: '#636efa',
                                df_segment['Category'][2]: '#ef553b'
                            }
                        )
                        
                        fig_bar.update_layout(
                            showlegend=False,
                            height=300,
                            xaxis_title="",
                            yaxis_title=col
                        )
                        
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown("**📊 Segmentation Data Table**")
                    st.dataframe(df_segment, use_container_width=True, hide_index=True)
                    
                    first_price = hist_data['Close'].iloc[0]
                    last_price = hist_data['Close'].iloc[-1]
                    period_return = ((last_price - first_price) / first_price) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Period Return", f"{period_return:.2f}%")
                    with col2:
                        volatility = hist_data['Close'].pct_change().std() * np.sqrt(252) * 100
                        st.metric("Annualized Volatility", f"{volatility:.2f}%")
                    with col3:
                        max_price = hist_data['Close'].max()
                        min_price = hist_data['Close'].min()
                        price_range = ((max_price - min_price) / min_price) * 100
                        st.metric("Price Range", f"{price_range:.2f}%")
                
                with tab4:
                    st.subheader("💾 Download Data")
                    
                    st.markdown("**Financial Data Table**")
                    csv_financial = df_financial.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Financial Data as CSV",
                        data=csv_financial,
                        file_name=f"{stock_symbol}_financial_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
                    st.markdown("**Segmentation Analysis Data**")
                    csv_segment = df_segment.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Segmentation Data as CSV",
                        data=csv_segment,
                        file_name=f"{stock_symbol}_segmentation_{segmentation.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
                    st.markdown("**Historical Price Data**")
                    hist_data_export = hist_data.reset_index()
                    csv_hist = hist_data_export.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Historical Price Data as CSV",
                        data=csv_hist,
                        file_name=f"{stock_symbol}_historical_prices_{time_period}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
    
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        st.info("Please verify the stock symbol is correct and try again.")

else:
    st.info("👆 Enter a stock symbol above to get started")

st.markdown("---")
st.markdown("**Data Source:** Yahoo Finance via yfinance library")
st.caption("Note: Peer averages and comparisons are estimated values for demonstration purposes. Historical data and company-specific metrics are real-time from Yahoo Finance.")
