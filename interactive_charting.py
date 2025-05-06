# region imports
from AlgorithmImports import *
# endregion

# Your New Python File
import plotly.graph_objects as go
from plotly.subplots import make_subplots
def equity_chart_with_signals(df, start_date, end_date, 
                                              chart_type='line', price_column='close', 
                                              num_signals=0, signal_column_names=None, 
                                              title='Interactive Equity Curve with Technical Signals',
                                              marker_symbols=None, marker_colors=None,
                                              candlestick_increasing_color='green',
                                              candlestick_decreasing_color='red'):
    """
    Create an interactive equity chart with box zoom and automatic y-axis adjustment.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing price and signal data
    start_date : str or datetime
        Start date for filtering data
    end_date : str or datetime
        End date for filtering data
    chart_type : str, default='line'
        Type of chart to display. Options: 'line' or 'candlestick'
    price_column : str, default='close'
        Column name for price data when using line chart
    num_signals : int, default=0
        Number of signal columns to plot
    signal_column_names : list[str], default=None
        List of column names for signals. Length should match num_signals.
    title : str, default='Interactive Equity Curve with Technical Signals'
        Title for the chart
    marker_symbols : list[str], default=None
        List of marker symbols for each signal. If None, defaults will be used.
    marker_colors : list[str], default=None
        List of marker colors for each signal. If None, defaults will be used.
    candlestick_increasing_color : str, default='green'
        Color for increasing candlesticks
    candlestick_decreasing_color : str, default='red'
        Color for decreasing candlesticks

    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Plotly figure object
    """
    # Validate inputs
    if chart_type not in ['line', 'candlestick']:
        raise ValueError("chart_type must be either 'line' or 'candlestick'")
    
    if chart_type == 'candlestick':
        # Check that required columns exist for candlestick
        required_cols = ['open', 'high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"For candlestick chart, DataFrame must include {required_cols}. Missing: {missing_cols}")
    
    if num_signals > 0 and signal_column_names is None:
        raise ValueError("signal_column_names must be provided when num_signals > 0")
    
    if signal_column_names is not None and len(signal_column_names) != num_signals:
        raise ValueError(f"Length of signal_column_names ({len(signal_column_names)}) must match num_signals ({num_signals})")
    
    # Filter the dataframe for the specified period
    df_filtered = df.loc[start_date:end_date].copy()
    
    # Default marker symbols and colors if not provided
    default_symbols = ['triangle-down', 'triangle-up', 'circle', 'square', 'diamond', 'cross', 'x']
    default_colors = ['green', 'red', 'blue', 'purple', 'orange', 'teal', 'magenta']
    
    if marker_symbols is None:
        marker_symbols = default_symbols
    
    if marker_colors is None:
        marker_colors = default_colors
    
    # Ensure we have enough symbols and colors
    while len(marker_symbols) < num_signals:
        marker_symbols.extend(marker_symbols)
    
    while len(marker_colors) < num_signals:
        marker_colors.extend(marker_colors)
    
    # Create the figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add the price data based on chart_type
    if chart_type == 'line':
        # Add line chart
        fig.add_trace(go.Scatter(
            x=df_filtered.index,
            y=df_filtered[price_column],
            mode='lines',
            name=f'{price_column.capitalize()} Price',
            line=dict(width=2)
        ))
    else:  # candlestick
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=df_filtered.index,
            open=df_filtered['open'],
            high=df_filtered['high'],
            low=df_filtered['low'],
            close=df_filtered['close'],
            name='OHLC',
            increasing_line_color=candlestick_increasing_color,
            decreasing_line_color=candlestick_decreasing_color,
            whiskerwidth=0.9  # Adjust the width of the candlestick
        ))
    
    # Add each signal
    for i in range(num_signals):
        signal_col = signal_column_names[i]
        
        # Get indices where signal is True
        signal_indices = df_filtered.index[df_filtered[signal_col]]
        
        # Get reference price points for positioning markers
        base_prices = df_filtered[price_column][df_filtered[signal_col]]
        
        # Add trace for this signal
        fig.add_trace(go.Scatter(
            x=signal_indices,
            y=base_prices,
            mode='markers',
            marker=dict(
                color=marker_colors[i % len(marker_colors)], 
                symbol=marker_symbols[i % len(marker_symbols)], 
                size=12,
                line=dict(width=1, color='black')
            ),
            name=signal_col
        ))
    
    # Update layout with box zoom and automatic y-axis adjustment
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis=dict(
            rangeslider=dict(visible=False),  # Disable range slider
            type='date'
        ),
        yaxis=dict(
            autorange=True,  # Enable automatic y-axis adjustment
            fixedrange=False  # Allow zooming/panning
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        template='plotly_white',
        width=1600,
        height=1000,
        hovermode='closest'
    )
    
    return fig