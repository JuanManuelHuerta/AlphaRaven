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
                
                tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                    "📈 Price Chart", 
                    "📊 Financial Data", 
                    "📑 Financial Statements",
                    "🔄 Stock Comparison",
                    "💼 Portfolio",
                    "🎯 Segmentation Analysis", 
                    "💾 Download Data"
                ])
                
                with tab1:
                    st.subheader(f"{stock_symbol} Stock Price - {time_period}")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        chart_type = st.selectbox("Chart Type:", ["Line Chart", "Candlestick Chart"])
                    with col2:
                        show_ma = st.checkbox("Moving Averages", value=False)
                    with col3:
                        show_rsi = st.checkbox("RSI Indicator", value=False)
                    
                    if chart_type == "Candlestick Chart":
                        fig = go.Figure(data=[go.Candlestick(
                            x=hist_data.index,
                            open=hist_data['Open'],
                            high=hist_data['High'],
                            low=hist_data['Low'],
                            close=hist_data['Close'],
                            name='Price'
                        )])
                    else:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=hist_data['Close'],
                            mode='lines',
                            name='Close Price',
                            line=dict(color='#1f77b4', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(31, 119, 180, 0.1)'
                        ))
                    
                    if show_ma:
                        hist_data['MA20'] = hist_data['Close'].rolling(window=20).mean()
                        hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()
                        
                        fig.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=hist_data['MA20'],
                            mode='lines',
                            name='MA 20',
                            line=dict(color='orange', width=1.5, dash='dash')
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=hist_data['MA50'],
                            mode='lines',
                            name='MA 50',
                            line=dict(color='red', width=1.5, dash='dash')
                        ))
                    
                    fig.update_layout(
                        height=400,
                        hovermode='x unified',
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    if show_rsi:
                        st.subheader("RSI (Relative Strength Index)")
                        
                        delta = hist_data['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        
                        fig_rsi = go.Figure()
                        fig_rsi.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=rsi,
                            mode='lines',
                            name='RSI',
                            line=dict(color='purple', width=2)
                        ))
                        
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
                        
                        fig_rsi.update_layout(
                            height=200,
                            xaxis_title="Date",
                            yaxis_title="RSI",
                            showlegend=False,
                            yaxis_range=[0, 100]
                        )
                        
                        st.plotly_chart(fig_rsi, use_container_width=True)
                    
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
                            f"${info.get('fiftyTwoWeekHigh', 0):,.2f}" if info.get('fiftyTwoWeekHigh') else 'N/A',
                            f"${info.get('fiftyTwoWeekLow', 0):,.2f}" if info.get('fiftyTwoWeekLow') else 'N/A',
                            market_cap_formatted,
                            f"{pe_ratio:.2f}" if pe_ratio != 'N/A' else 'N/A',
                            f"{info.get('forwardPE', 0):.2f}" if info.get('forwardPE') else 'N/A',
                            f"{info.get('pegRatio', 0):.2f}" if info.get('pegRatio') else 'N/A',
                            f"{info.get('priceToBook', 0):.2f}" if info.get('priceToBook') else 'N/A',
                            f"{dividend_yield_pct:.2f}%" if dividend_yield else 'N/A',
                            f"${info.get('trailingEps', 0):.2f}" if info.get('trailingEps') else 'N/A',
                            f"${info.get('totalRevenue', 0) / 1e9:.2f}B" if info.get('totalRevenue') else 'N/A',
                            f"{info.get('profitMargins', 0) * 100:.2f}%" if info.get('profitMargins') else 'N/A',
                            f"{info.get('operatingMargins', 0) * 100:.2f}%" if info.get('operatingMargins') else 'N/A',
                            f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get('returnOnEquity') else 'N/A',
                            f"{info.get('beta', 0):.2f}" if info.get('beta') else 'N/A',
                            f"{info.get('volume', 0):,}" if info.get('volume') else 'N/A',
                            f"{info.get('averageVolume', 0):,}" if info.get('averageVolume') else 'N/A',
                            f"{info.get('sharesOutstanding', 0):,}" if info.get('sharesOutstanding') else 'N/A'
                        ]
                    }
                    
                    df_financial = pd.DataFrame(financial_data)
                    st.dataframe(df_financial, use_container_width=True, hide_index=True)
                
                with tab3:
                    st.subheader("📑 Financial Statements")
                    
                    try:
                        income_stmt = stock.income_stmt
                        balance_sheet = stock.balance_sheet
                        cashflow = stock.cashflow
                        
                        statement_type = st.selectbox(
                            "Select Statement:",
                            ["Income Statement", "Balance Sheet", "Cash Flow Statement"]
                        )
                        
                        if statement_type == "Income Statement" and not income_stmt.empty:
                            st.markdown("**Income Statement** (in millions)")
                            income_display = income_stmt / 1e6
                            st.dataframe(income_display.T, use_container_width=True)
                            
                            if len(income_stmt.columns) >= 2:
                                revenue_data = income_stmt.loc['Total Revenue'] / 1e9 if 'Total Revenue' in income_stmt.index else None
                                if revenue_data is not None:
                                    fig_rev = px.bar(
                                        x=revenue_data.index.astype(str),
                                        y=revenue_data.values,
                                        title="Total Revenue Trend (Billions)",
                                        labels={'x': 'Period', 'y': 'Revenue ($B)'}
                                    )
                                    st.plotly_chart(fig_rev, use_container_width=True)
                        
                        elif statement_type == "Balance Sheet" and not balance_sheet.empty:
                            st.markdown("**Balance Sheet** (in millions)")
                            balance_display = balance_sheet / 1e6
                            st.dataframe(balance_display.T, use_container_width=True)
                            
                            if len(balance_sheet.columns) >= 2:
                                assets_row = 'Total Assets' if 'Total Assets' in balance_sheet.index else None
                                liabilities_row = 'Total Liabilities Net Minority Interest' if 'Total Liabilities Net Minority Interest' in balance_sheet.index else None
                                
                                if assets_row and liabilities_row:
                                    fig_balance = go.Figure()
                                    fig_balance.add_trace(go.Bar(
                                        x=balance_sheet.columns.astype(str),
                                        y=balance_sheet.loc[assets_row] / 1e9,
                                        name='Total Assets'
                                    ))
                                    fig_balance.add_trace(go.Bar(
                                        x=balance_sheet.columns.astype(str),
                                        y=balance_sheet.loc[liabilities_row] / 1e9,
                                        name='Total Liabilities'
                                    ))
                                    fig_balance.update_layout(
                                        title="Assets vs Liabilities (Billions)",
                                        xaxis_title="Period",
                                        yaxis_title="Amount ($B)",
                                        barmode='group'
                                    )
                                    st.plotly_chart(fig_balance, use_container_width=True)
                        
                        elif statement_type == "Cash Flow Statement" and not cashflow.empty:
                            st.markdown("**Cash Flow Statement** (in millions)")
                            cashflow_display = cashflow / 1e6
                            st.dataframe(cashflow_display.T, use_container_width=True)
                            
                            if len(cashflow.columns) >= 2:
                                operating_cf = cashflow.loc['Operating Cash Flow'] / 1e9 if 'Operating Cash Flow' in cashflow.index else None
                                if operating_cf is not None:
                                    fig_cf = px.line(
                                        x=operating_cf.index.astype(str),
                                        y=operating_cf.values,
                                        title="Operating Cash Flow Trend (Billions)",
                                        labels={'x': 'Period', 'y': 'Cash Flow ($B)'}
                                    )
                                    st.plotly_chart(fig_cf, use_container_width=True)
                        else:
                            st.info("No data available for this statement.")
                            
                    except Exception as e:
                        st.warning(f"Financial statements data not available: {str(e)}")
                
                with tab4:
                    st.subheader("🔄 Stock Comparison")
                    
                    st.markdown("Compare multiple stocks side by side")
                    
                    comparison_symbols = st.text_input(
                        "Enter stock symbols separated by commas (e.g., AAPL, MSFT, GOOGL):",
                        value=f"{stock_symbol}, MSFT"
                    )
                    
                    if comparison_symbols:
                        symbols = [s.strip().upper() for s in comparison_symbols.split(',')]
                        
                        if st.button("Compare Stocks"):
                            comparison_data = []
                            all_hist_data = {}
                            
                            for symbol in symbols:
                                try:
                                    comp_stock = yf.Ticker(symbol)
                                    comp_info = comp_stock.info
                                    comp_hist = comp_stock.history(period=period_map[time_period])
                                    
                                    if not comp_hist.empty:
                                        all_hist_data[symbol] = comp_hist
                                        
                                        first_price = comp_hist['Close'].iloc[0]
                                        last_price = comp_hist['Close'].iloc[-1]
                                        period_return = ((last_price - first_price) / first_price) * 100
                                        
                                        comparison_data.append({
                                            'Symbol': symbol,
                                            'Company': comp_info.get('longName', 'N/A'),
                                            'Current Price': f"${comp_info.get('currentPrice', comp_info.get('regularMarketPrice', 0)):,.2f}",
                                            'Market Cap': f"${comp_info.get('marketCap', 0) / 1e9:.2f}B",
                                            'P/E Ratio': f"{comp_info.get('trailingPE', 0):.2f}" if comp_info.get('trailingPE') else 'N/A',
                                            'Period Return': f"{period_return:.2f}%",
                                            'Volume': f"{comp_info.get('volume', 0):,}",
                                            'Beta': f"{comp_info.get('beta', 0):.2f}" if comp_info.get('beta') else 'N/A'
                                        })
                                except Exception as e:
                                    st.warning(f"Could not fetch data for {symbol}")
                            
                            if comparison_data:
                                df_comparison = pd.DataFrame(comparison_data)
                                st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                                
                                st.subheader("Price Comparison Chart")
                                fig_comp = go.Figure()
                                
                                for symbol, hist in all_hist_data.items():
                                    normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
                                    fig_comp.add_trace(go.Scatter(
                                        x=hist.index,
                                        y=normalized,
                                        mode='lines',
                                        name=symbol,
                                        line=dict(width=2)
                                    ))
                                
                                fig_comp.update_layout(
                                    height=400,
                                    title="Normalized Price Comparison (Base 100)",
                                    xaxis_title="Date",
                                    yaxis_title="Normalized Price",
                                    hovermode='x unified',
                                    showlegend=True
                                )
                                
                                st.plotly_chart(fig_comp, use_container_width=True)
                                
                                st.subheader("Metrics Heatmap")
                                
                                heatmap_data = []
                                for item in comparison_data:
                                    try:
                                        heatmap_data.append({
                                            'Symbol': item['Symbol'],
                                            'P/E': float(item['P/E Ratio']) if item['P/E Ratio'] != 'N/A' else 0,
                                            'Return %': float(item['Period Return'].replace('%', '')),
                                            'Beta': float(item['Beta']) if item['Beta'] != 'N/A' else 0
                                        })
                                    except:
                                        continue
                                
                                if heatmap_data:
                                    df_heatmap = pd.DataFrame(heatmap_data)
                                    df_heatmap_values = df_heatmap.set_index('Symbol')
                                    
                                    fig_heatmap = px.imshow(
                                        df_heatmap_values.T,
                                        labels=dict(x="Stock", y="Metric", color="Value"),
                                        x=df_heatmap_values.index,
                                        y=df_heatmap_values.columns,
                                        color_continuous_scale='RdYlGn',
                                        aspect="auto"
                                    )
                                    
                                    fig_heatmap.update_layout(height=300)
                                    st.plotly_chart(fig_heatmap, use_container_width=True)
                
                with tab5:
                    st.subheader("💼 Portfolio Tracking")
                    
                    st.markdown("Build and track your stock portfolio")
                    
                    if 'portfolio' not in st.session_state:
                        st.session_state.portfolio = []
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        portfolio_symbol = st.text_input("Stock Symbol:", key="portfolio_symbol")
                    with col2:
                        portfolio_shares = st.number_input("Number of Shares:", min_value=0.0, value=1.0, step=0.1, key="portfolio_shares")
                    with col3:
                        if st.button("Add to Portfolio"):
                            if portfolio_symbol:
                                st.session_state.portfolio.append({
                                    'symbol': portfolio_symbol.upper(),
                                    'shares': portfolio_shares
                                })
                                st.success(f"Added {portfolio_shares} shares of {portfolio_symbol.upper()}")
                    
                    if st.session_state.portfolio:
                        portfolio_data = []
                        sector_composition = {}
                        total_value = 0
                        
                        for item in st.session_state.portfolio:
                            try:
                                p_stock = yf.Ticker(item['symbol'])
                                p_info = p_stock.info
                                current_price = p_info.get('currentPrice', p_info.get('regularMarketPrice', 0))
                                position_value = current_price * item['shares']
                                total_value += position_value
                                
                                sector = p_info.get('sector', 'Unknown')
                                if sector in sector_composition:
                                    sector_composition[sector] += position_value
                                else:
                                    sector_composition[sector] = position_value
                                
                                portfolio_data.append({
                                    'Symbol': item['symbol'],
                                    'Shares': item['shares'],
                                    'Current Price': f"${current_price:,.2f}",
                                    'Position Value': f"${position_value:,.2f}",
                                    'Sector': sector
                                })
                            except:
                                continue
                        
                        if portfolio_data:
                            st.markdown(f"**Total Portfolio Value: ${total_value:,.2f}**")
                            
                            df_portfolio = pd.DataFrame(portfolio_data)
                            st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
                            
                            if sector_composition:
                                st.subheader("Sector Composition")
                                
                                fig_pie = px.pie(
                                    values=list(sector_composition.values()),
                                    names=list(sector_composition.keys()),
                                    title="Portfolio by Sector"
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)
                            
                            if st.button("Clear Portfolio"):
                                st.session_state.portfolio = []
                                st.rerun()
                    else:
                        st.info("Your portfolio is empty. Add stocks above to get started.")
                
                with tab6:
                    st.subheader(f"🎯 {segmentation} Analysis")
                    
                    st.info("💡 Segmentation averages shown below are estimated benchmarks. Enable peer comparison to analyze actual stocks in the same segment.")
                    
                    show_peer_comparison = st.checkbox("Show Peer Stock Comparison", value=False)
                    
                    if segmentation == "Industry":
                        industry = info.get('industry', 'Unknown')
                        sector = info.get('sector', 'Unknown')
                        st.markdown(f"**Industry:** {industry}")
                        st.markdown(f"**Sector:** {sector}")
                        
                        if show_peer_comparison:
                            st.markdown("### Peer Stocks Comparison")
                            peer_symbols_input = st.text_input(
                                f"Enter peer stocks in {industry} (comma-separated):",
                                value="",
                                key="peer_industry"
                            )
                            
                            if peer_symbols_input:
                                peer_symbols = [s.strip().upper() for s in peer_symbols_input.split(',')]
                                peer_comparison_data = []
                                
                                peer_comparison_data.append({
                                    'Symbol': stock_symbol,
                                    'Company': info.get('longName', 'N/A'),
                                    'P/E Ratio': pe_ratio if pe_ratio != 'N/A' else 0,
                                    'Profit Margin': info.get('profitMargins', 0) * 100,
                                    'Market Cap ($B)': info.get('marketCap', 0) / 1e9,
                                    'Type': 'Your Stock'
                                })
                                
                                for peer in peer_symbols:
                                    try:
                                        peer_stock = yf.Ticker(peer)
                                        peer_info = peer_stock.info
                                        peer_comparison_data.append({
                                            'Symbol': peer,
                                            'Company': peer_info.get('longName', 'N/A'),
                                            'P/E Ratio': peer_info.get('trailingPE', 0) if peer_info.get('trailingPE') else 0,
                                            'Profit Margin': peer_info.get('profitMargins', 0) * 100,
                                            'Market Cap ($B)': peer_info.get('marketCap', 0) / 1e9,
                                            'Type': 'Peer'
                                        })
                                    except:
                                        continue
                                
                                if len(peer_comparison_data) > 1:
                                    df_peers = pd.DataFrame(peer_comparison_data)
                                    
                                    st.dataframe(df_peers, use_container_width=True, hide_index=True)
                                    
                                    fig_peer_comparison = px.bar(
                                        df_peers,
                                        x='Symbol',
                                        y=['P/E Ratio', 'Profit Margin'],
                                        title="Peer Comparison - Key Metrics",
                                        barmode='group',
                                        color_discrete_sequence=['#636efa', '#00cc96']
                                    )
                                    st.plotly_chart(fig_peer_comparison, use_container_width=True)
                                    
                                    metrics_for_heatmap = df_peers[['Symbol', 'P/E Ratio', 'Profit Margin', 'Market Cap ($B)']].set_index('Symbol')
                                    
                                    fig_peer_heatmap = px.imshow(
                                        metrics_for_heatmap.T,
                                        labels=dict(x="Stock", y="Metric", color="Value"),
                                        x=metrics_for_heatmap.index,
                                        y=metrics_for_heatmap.columns,
                                        color_continuous_scale='RdYlGn',
                                        aspect="auto",
                                        title="Peer Metrics Heatmap"
                                    )
                                    st.plotly_chart(fig_peer_heatmap, use_container_width=True)
                        
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
                        
                        if show_peer_comparison:
                            st.markdown("### Peer Stocks Comparison")
                            peer_symbols_input = st.text_input(
                                f"Enter peer stocks in {cap_category} (comma-separated):",
                                value="",
                                key="peer_marketcap"
                            )
                            
                            if peer_symbols_input:
                                peer_symbols = [s.strip().upper() for s in peer_symbols_input.split(',')]
                                peer_comparison_data = []
                                
                                peer_comparison_data.append({
                                    'Symbol': stock_symbol,
                                    'Company': info.get('longName', 'N/A'),
                                    'Market Cap ($B)': market_cap_value / 1e9,
                                    'Volume (M)': info.get('volume', 0) / 1e6,
                                    'Beta': info.get('beta', 1.0) if info.get('beta') != 'N/A' else 1.0,
                                    'Type': 'Your Stock'
                                })
                                
                                for peer in peer_symbols:
                                    try:
                                        peer_stock = yf.Ticker(peer)
                                        peer_info = peer_stock.info
                                        peer_comparison_data.append({
                                            'Symbol': peer,
                                            'Company': peer_info.get('longName', 'N/A'),
                                            'Market Cap ($B)': peer_info.get('marketCap', 0) / 1e9,
                                            'Volume (M)': peer_info.get('volume', 0) / 1e6,
                                            'Beta': peer_info.get('beta', 1.0) if peer_info.get('beta') != 'N/A' else 1.0,
                                            'Type': 'Peer'
                                        })
                                    except:
                                        continue
                                
                                if len(peer_comparison_data) > 1:
                                    df_peers = pd.DataFrame(peer_comparison_data)
                                    st.dataframe(df_peers, use_container_width=True, hide_index=True)
                                    
                                    metrics_for_heatmap = df_peers[['Symbol', 'Market Cap ($B)', 'Volume (M)', 'Beta']].set_index('Symbol')
                                    
                                    fig_peer_heatmap = px.imshow(
                                        metrics_for_heatmap.T,
                                        labels=dict(x="Stock", y="Metric", color="Value"),
                                        x=metrics_for_heatmap.index,
                                        y=metrics_for_heatmap.columns,
                                        color_continuous_scale='RdYlGn',
                                        aspect="auto",
                                        title="Peer Metrics Heatmap"
                                    )
                                    st.plotly_chart(fig_peer_heatmap, use_container_width=True)
                        
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
                        
                        if show_peer_comparison:
                            st.markdown("### Peer Stocks Comparison")
                            peer_symbols_input = st.text_input(
                                f"Enter peer stocks in {sector} sector (comma-separated):",
                                value="",
                                key="peer_sector"
                            )
                            
                            if peer_symbols_input:
                                peer_symbols = [s.strip().upper() for s in peer_symbols_input.split(',')]
                                peer_comparison_data = []
                                
                                peer_comparison_data.append({
                                    'Symbol': stock_symbol,
                                    'Company': info.get('longName', 'N/A'),
                                    'ROE (%)': info.get('returnOnEquity', 0.15) * 100,
                                    'Debt to Equity': info.get('debtToEquity', 0.5) if info.get('debtToEquity') else 0.5,
                                    'Current Ratio': info.get('currentRatio', 1.5) if info.get('currentRatio') else 1.5,
                                    'Type': 'Your Stock'
                                })
                                
                                for peer in peer_symbols:
                                    try:
                                        peer_stock = yf.Ticker(peer)
                                        peer_info = peer_stock.info
                                        peer_comparison_data.append({
                                            'Symbol': peer,
                                            'Company': peer_info.get('longName', 'N/A'),
                                            'ROE (%)': peer_info.get('returnOnEquity', 0) * 100 if peer_info.get('returnOnEquity') else 0,
                                            'Debt to Equity': peer_info.get('debtToEquity', 0) if peer_info.get('debtToEquity') else 0,
                                            'Current Ratio': peer_info.get('currentRatio', 0) if peer_info.get('currentRatio') else 0,
                                            'Type': 'Peer'
                                        })
                                    except:
                                        continue
                                
                                if len(peer_comparison_data) > 1:
                                    df_peers = pd.DataFrame(peer_comparison_data)
                                    st.dataframe(df_peers, use_container_width=True, hide_index=True)
                                    
                                    metrics_for_heatmap = df_peers[['Symbol', 'ROE (%)', 'Debt to Equity', 'Current Ratio']].set_index('Symbol')
                                    
                                    fig_peer_heatmap = px.imshow(
                                        metrics_for_heatmap.T,
                                        labels=dict(x="Stock", y="Metric", color="Value"),
                                        x=metrics_for_heatmap.index,
                                        y=metrics_for_heatmap.columns,
                                        color_continuous_scale='RdYlGn',
                                        aspect="auto",
                                        title="Peer Metrics Heatmap"
                                    )
                                    st.plotly_chart(fig_peer_heatmap, use_container_width=True)
                        
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
                        
                        if show_peer_comparison:
                            st.markdown("### Peer Stocks Comparison")
                            peer_symbols_input = st.text_input(
                                f"Enter peer stocks from {country} (comma-separated):",
                                value="",
                                key="peer_region"
                            )
                            
                            if peer_symbols_input:
                                peer_symbols = [s.strip().upper() for s in peer_symbols_input.split(',')]
                                peer_comparison_data = []
                                
                                peer_comparison_data.append({
                                    'Symbol': stock_symbol,
                                    'Company': info.get('longName', 'N/A'),
                                    'Revenue Growth (%)': info.get('revenueGrowth', 0.10) * 100 if info.get('revenueGrowth') else 10,
                                    'Profit Margin (%)': info.get('profitMargins', 0.15) * 100,
                                    'P/E Ratio': pe_ratio if pe_ratio != 'N/A' else 20,
                                    'Type': 'Your Stock'
                                })
                                
                                for peer in peer_symbols:
                                    try:
                                        peer_stock = yf.Ticker(peer)
                                        peer_info = peer_stock.info
                                        peer_pe = peer_info.get('trailingPE', 0) if peer_info.get('trailingPE') else 0
                                        peer_comparison_data.append({
                                            'Symbol': peer,
                                            'Company': peer_info.get('longName', 'N/A'),
                                            'Revenue Growth (%)': peer_info.get('revenueGrowth', 0) * 100 if peer_info.get('revenueGrowth') else 0,
                                            'Profit Margin (%)': peer_info.get('profitMargins', 0) * 100 if peer_info.get('profitMargins') else 0,
                                            'P/E Ratio': peer_pe,
                                            'Type': 'Peer'
                                        })
                                    except:
                                        continue
                                
                                if len(peer_comparison_data) > 1:
                                    df_peers = pd.DataFrame(peer_comparison_data)
                                    st.dataframe(df_peers, use_container_width=True, hide_index=True)
                                    
                                    metrics_for_heatmap = df_peers[['Symbol', 'Revenue Growth (%)', 'Profit Margin (%)', 'P/E Ratio']].set_index('Symbol')
                                    
                                    fig_peer_heatmap = px.imshow(
                                        metrics_for_heatmap.T,
                                        labels=dict(x="Stock", y="Metric", color="Value"),
                                        x=metrics_for_heatmap.index,
                                        y=metrics_for_heatmap.columns,
                                        color_continuous_scale='RdYlGn',
                                        aspect="auto",
                                        title="Peer Metrics Heatmap"
                                    )
                                    st.plotly_chart(fig_peer_heatmap, use_container_width=True)
                        
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
                
                with tab7:
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
