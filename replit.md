# Stock Financial Dashboard

## Overview

This is a Streamlit-based web application that provides real-time stock market analysis and visualization. The application allows users to search for stock symbols and view their financial performance across different time periods with various segmentation views. It leverages the Yahoo Finance API (via yfinance) to fetch live stock data and uses Plotly for interactive data visualizations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework Choice: Streamlit**
- **Problem**: Need a simple, fast way to create an interactive financial dashboard without building a complex web application
- **Solution**: Streamlit provides a Python-native approach to building web UIs with minimal code
- **Rationale**: Enables rapid prototyping and deployment while maintaining Python for both data processing and presentation
- **Trade-offs**: Less control over UI customization compared to React/Vue, but significantly faster development time

**Layout Pattern: Wide Layout with Columnar Design**
- Uses Streamlit's column system for responsive layout
- Primary input column (2/3 width) for stock symbol entry
- Secondary control column (1/3 width) for segmentation options
- Horizontal radio buttons for time period selection optimize screen real estate

### Data Processing Architecture

**Real-time Data Fetching**
- **Problem**: Need current and historical stock market data
- **Solution**: Direct API calls to Yahoo Finance via yfinance library on each user interaction
- **Alternatives Considered**: Pre-caching data or using a dedicated financial data API service
- **Pros**: Simple implementation, no API keys required, real-time data
- **Cons**: Dependent on Yahoo Finance availability, potential rate limiting, no data persistence

**Time Period Mapping**
- Implements a dictionary-based mapping between user-friendly labels (1M, 3M, etc.) and yfinance API parameters
- Provides standardized time period options: 1 month, 3 months, 6 months, 1 year, and 5 years
- Default selection set to 1 year for balanced historical context

### Visualization Architecture

**Charting Library: Plotly**
- **Problem**: Need interactive, professional-grade financial charts
- **Solution**: Plotly Graph Objects and Plotly Express for different visualization needs
- **Rationale**: Provides interactive features (zoom, pan, hover) essential for financial analysis
- **Trade-offs**: Larger bundle size than static charts, but superior user experience for data exploration

**Segmentation Views**
- Supports multiple analytical perspectives: Industry, Market Capitalization, Sector, and Geographic Region
- Architecture designed to accommodate different grouping and comparison strategies
- Enables comparative analysis across different market segments

### Error Handling Strategy

**Data Validation**
- Empty dataset detection for invalid stock symbols
- Missing data field handling with fallback values (e.g., currentPrice vs regularMarketPrice)
- User-friendly error messages with actionable guidance
- Loading states with spinners to indicate data fetching progress

## External Dependencies

### Third-party Libraries

**yfinance (Yahoo Finance API)**
- Purpose: Fetch real-time and historical stock market data
- Data Retrieved: Stock prices, company information, historical performance
- No authentication required

**Streamlit**
- Purpose: Web application framework for Python
- Enables rapid UI development with minimal frontend code
- Built-in components for inputs, layouts, and data display

**Plotly**
- Purpose: Interactive data visualization
- Components Used: plotly.graph_objects for custom charts, plotly.express for simplified plotting
- Provides zoom, pan, and hover interactions for financial charts

**Pandas**
- Purpose: Data manipulation and analysis
- Used for processing time-series stock data
- DataFrame operations for data transformation

**NumPy**
- Purpose: Numerical computing support
- Imported for potential statistical calculations and array operations

### Python Standard Library

**datetime**
- Time period calculations
- Date range management for historical data queries