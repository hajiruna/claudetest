import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re

st.set_page_config(
    page_title="株価分析アプリ",
    page_icon="📈",
    layout="wide"
)

st.title("📈 株価分析アプリ")
st.write("Yahoo Financeから株価データを取得して分析します")

col1, col2 = st.columns(2)

with col1:
    symbol = st.text_input(
        "ティッカーシンボルを入力してください", 
        value="AAPL",
        help="例: AAPL (Apple), MSFT (Microsoft), GOOGL (Google)"
    )
    
    if symbol and not re.match(r'^[A-Z]{1,5}$', symbol.upper()):
        st.error("無効なティッカーシンボルです。1-5文字のアルファベットを入力してください。")
        st.stop()

with col2:
    period = st.selectbox(
        "期間を選択してください",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )

if st.button("分析開始", type="primary"):
    try:
        with st.spinner(f"{symbol}の株価データを取得中..."):
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if df.empty:
                st.error(f"ティッカーシンボル '{symbol}' のデータが見つかりません。")
            else:
                info = stock.info
                
                st.subheader(f"{info.get('longName', symbol)} ({symbol})")
                
                col1, col2, col3, col4 = st.columns(4)
                
                current_price = df['Close'].iloc[-1]
                
                if len(df) < 2:
                    st.warning("データが不足しているため、前日比較ができません。")
                    change = 0
                    change_pct = 0
                else:
                    prev_price = df['Close'].iloc[-2]
                    change = current_price - prev_price
                    change_pct = (change / prev_price) * 100
                
                with col1:
                    st.metric("現在価格", f"${current_price:.2f}", f"{change:+.2f}")
                
                with col2:
                    st.metric("変化率", f"{change_pct:+.2f}%")
                
                with col3:
                    st.metric("最高値", f"${df['High'].max():.2f}")
                
                with col4:
                    st.metric("最安値", f"${df['Low'].min():.2f}")
                
                st.subheader("📊 株価チャート")
                
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name="株価"
                ))
                
                fig.update_layout(
                    title=f"{symbol} 株価チャート",
                    yaxis_title="価格 ($)",
                    xaxis_title="日付",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📈 出来高")
                
                fig_volume = px.bar(
                    df, 
                    x=df.index, 
                    y='Volume',
                    title=f"{symbol} 出来高"
                )
                fig_volume.update_layout(template="plotly_white")
                
                st.plotly_chart(fig_volume, use_container_width=True)
                
                st.subheader("📋 統計情報")
                
                stats_data = {
                    "項目": [
                        "平均価格", "標準偏差", "最高価格", "最低価格", 
                        "平均出来高", "価格レンジ"
                    ],
                    "値": [
                        f"${df['Close'].mean():.2f}",
                        f"${df['Close'].std():.2f}",
                        f"${df['High'].max():.2f}",
                        f"${df['Low'].min():.2f}",
                        f"{df['Volume'].mean():,.0f}",
                        f"${df['High'].max() - df['Low'].min():.2f}"
                    ]
                }
                
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df, use_container_width=True)
                
                st.subheader("📊 移動平均線")
                
                data_length = len(df)
                if data_length >= 20:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                if data_length >= 50:
                    df['MA50'] = df['Close'].rolling(window=50).mean()
                
                fig_ma = go.Figure()
                
                fig_ma.add_trace(go.Scatter(
                    x=df.index, y=df['Close'], 
                    mode='lines', name='終値'
                ))
                
                if data_length >= 20 and 'MA20' in df.columns:
                    fig_ma.add_trace(go.Scatter(
                        x=df.index, y=df['MA20'], 
                        mode='lines', name='20日移動平均'
                    ))
                
                if data_length >= 50 and 'MA50' in df.columns:
                    fig_ma.add_trace(go.Scatter(
                        x=df.index, y=df['MA50'], 
                        mode='lines', name='50日移動平均'
                    ))
                
                fig_ma.update_layout(
                    title=f"{symbol} 価格と移動平均線",
                    yaxis_title="価格 ($)",
                    xaxis_title="日付",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_ma, use_container_width=True)
                
                with st.expander("生データ"):
                    st.dataframe(df)
                    
    except (ValueError, KeyError) as e:
        st.error(f"データ処理エラー: {str(e)}")
        st.info("ティッカーシンボルを確認してください。")
    except ConnectionError as e:
        st.error("ネットワーク接続エラー: インターネット接続を確認してください。")
    except Exception as e:
        st.error(f"予期しないエラーが発生しました: {str(e)}")
        st.info("問題が続く場合は、しばらく待ってから再試行してください。")

st.sidebar.header("ℹ️ 使い方")
st.sidebar.write("""
1. ティッカーシンボルを入力（例: AAPL, MSFT, GOOGL）
2. 分析期間を選択
3. 「分析開始」ボタンをクリック
4. 株価チャート、出来高、統計情報を確認
""")

st.sidebar.header("📝 注意事項")
st.sidebar.write("""
- データはYahoo Financeから取得
- リアルタイムデータではありません
- 投資判断は自己責任で行ってください
""")