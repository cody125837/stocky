import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import urllib3
import plotly.graph_objects as go

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
st.set_page_config(page_title="家庭專屬理財助手", page_icon="💡", layout="wide")

# ==========================================
# 🎨 專屬 UI/UX 美化 CSS (深色模式優化版)
# ==========================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton>button {
        border-radius: 12px;
        font-size: 18px !important;
        font-weight: bold;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
        transition: 0.3s;
        border: 1px solid #333;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 12px rgba(239, 83, 80, 0.2);
        border: 1px solid #EF5350;
    }
    
    .stTextInput>div>div>input {
        border-radius: 10px;
        font-size: 18px;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800;
        color: #F8F9FA !important; 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================

st.markdown("<h1 style='text-align: center; color: #EF5350;'>💖 家庭專屬理財與存股小幫手</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #BDBDBD; margin-bottom: 30px;'>投資理財穩穩賺，讓時間陪我們慢慢變富 ✨</h4>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 個股健康檢查", "🔥 今日市場熱點", "💰 真實存股計算機"])

# ----------------- 分頁 1：個股健康檢查 -----------------
with tab1:
    st.markdown("### 🩺 輸入股票代號，馬上幫你做體檢！")
    col1, col2 = st.columns([3, 1])
    with col1:
        stock_id = st.text_input("💡 請在這裡輸入代號 (上市/上櫃皆可，例如 2330 或 8069)", value="2330", key="tab1_input")
    with col2:
        st.write("") 
        search_btn = st.button("🚀 開始健康檢查", width="stretch")
    
    if search_btn:
        with st.spinner('📡 正在幫您調閱最新的市場數據...'):
            df = yf.Ticker(f"{stock_id}.TW").history(period="6mo")
            if df.empty:
                df = yf.Ticker(f"{stock_id}.TWO").history(period="6mo")
                
            if not df.empty:
                df['5MA'] = df['Close'].rolling(window=5).mean()
                df['20MA'] = df['Close'].rolling(window=20).mean()
                df['60MA'] = df['Close'].rolling(window=60).mean()
                
                df['STD'] = df['Close'].rolling(window=20).std()
                df['布林上軌'] = df['20MA'] + (df['STD'] * 2)
                df['布林下軌'] = df['20MA'] - (df['STD'] * 2)
                
                delta = df['Close'].diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                df['RSI'] = 100 - (100 / (1 + rs))

                latest_close = df['Close'].iloc[-1]
                latest_20ma = df['20MA'].iloc[-1]
                prev_20ma = df['20MA'].iloc[-2]
                bias = ((latest_close - latest_20ma) / latest_20ma) * 100
                ma_is_up = latest_20ma > prev_20ma
                
                st.markdown("### 🎯 專屬進場時機判定")
                if ma_is_up and (0 <= bias <= 4):
                    st.markdown("""<div style='background-color: rgba(76, 175, 80, 0.15); padding: 25px; border-radius: 15px; border-left: 8px solid #4CAF50;'><h2 style='color: #81C784; margin:0;'>🟢 【極佳買點】現在是進場好時機！</h2><h4 style='color: #E0E0E0; margin-top:10px; line-height: 1.5;'>大趨勢向上且股價在合理價位，進場風險較低！</h4></div>""", unsafe_allow_html=True)
                elif ma_is_up and bias > 4:
                    st.markdown(f"""<div style='background-color: rgba(255, 193, 7, 0.15); padding: 25px; border-radius: 15px; border-left: 8px solid #FFC107;'><h2 style='color: #FFD54F; margin:0;'>🟡 【觀望一下】很熱門，但別追高！</h2><h4 style='color: #E0E0E0; margin-top:10px; line-height: 1.5;'>股價已高出平均成本 <b>{bias:.1f}%</b>，現在買容易買在最高點，建議等跌下來再考慮。</h4></div>""", unsafe_allow_html=True)
                elif not ma_is_up and latest_close < latest_20ma:
                    st.markdown("""<div style='background-color: rgba(244, 67, 54, 0.15); padding: 25px; border-radius: 15px; border-left: 8px solid #F44336;'><h2 style='color: #E57373; margin:0;'>🔴 【嚴禁買進】趨勢偏弱，千萬別碰！</h2><h4 style='color: #E0E0E0; margin-top:10px; line-height: 1.5;'>股票正在走下坡，買了容易被套牢（接刀子），請保留現金！</h4></div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""<div style='background-color: rgba(158, 158, 158, 0.15); padding: 25px; border-radius: 15px; border-left: 8px solid #9E9E9E;'><h2 style='color: #BDBDBD; margin:0;'>⚪ 【正在盤整】方向不明確，多看少做</h2><h4 style='color: #E0E0E0; margin-top:10px; line-height: 1.5;'>主力可能還在猶豫，建議先放入觀察名單就好。</h4></div>""", unsafe_allow_html=True)

                st.write("") 
                st.write("") 
                
                first_p = df['Close'].iloc[0]
                diff = latest_close - first_p
                roi = (diff / first_p) * 100
                
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.info("💰 最新收盤價")
                    st.metric(label="", value=f"{latest_close:.2f} 元")
                with col_m2:
                    st.warning("🌡️ 目前 RSI 溫度 (情緒)")
                    st.metric(label="", value=f"{df['RSI'].iloc[-1]:.1f}", delta=">70超買，<30超賣", delta_color="off")
                with col_m3:
                    st.success("📈 近半年報酬率")
                    st.metric(label="", value=f"{roi:.2f}%", delta=f"{diff:.2f} 元")
                
                st.divider()
                st.markdown("### 📉 股價走勢與安全通道 (布林通道)")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['布林上軌'], line=dict(color='rgba(255,255,255,0)'), hoverinfo='skip', showlegend=False))
                fig.add_trace(go.Scatter(x=df.index, y=df['布林下軌'], fill='tonexty', fillcolor='rgba(255, 255, 255, 0.1)', line=dict(color='rgba(255,255,255,0)'), name='安全通道邊界', hovertemplate='%{y:.2f}'))
                fig.add_trace(go.Scatter(x=df.index, y=df['60MA'], line=dict(color='#9CCC65', width=2, dash='dash'), name='60MA (季線)', hovertemplate='%{y:.2f}'))
                fig.add_trace(go.Scatter(x=df.index, y=df['20MA'], line=dict(color='#FFCA28', width=2, dash='dot'), name='20MA (月線)', hovertemplate='%{y:.2f}'))
                fig.add_trace(go.Scatter(x=df.index, y=df['5MA'], line=dict(color='#EF5350', width=1.5), name='5MA (周線)', hovertemplate='%{y:.2f}'))
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#42A5F5', width=3), name='當日收盤價', hovertemplate='%{y:.2f}'))

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    hovermode='x unified', 
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    dragmode=False # 🛑 核心優化：禁止手機拖曳縮放，讓網頁可以順暢上下滑動
                )
                # 🛑 核心優化：隱藏右上角的複雜工具列 (displayModeBar: False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                st.markdown("### 🌡️ 市場情緒溫度計 (RSI 指標)")
                st.caption("點擊圖表可查看準確數值。黃線為危險超買區，綠線為超值超賣區。")
                
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#AB47BC', width=2.5), name='RSI 溫度', hovertemplate='RSI: %{y:.1f}'))
                fig_rsi.add_hline(y=70, line_dash="dot", line_color="#EF5350", annotation_text="危險超買區 (70)", annotation_position="top left", annotation_font_color="#EF5350")
                fig_rsi.add_hline(y=30, line_dash="dot", line_color="#81C784", annotation_text="超值超賣區 (30)", annotation_position="bottom left", annotation_font_color="#81C784")
                
                fig_rsi.update_layout(
                    hovermode='x unified',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=10, b=0),
                    yaxis=dict(range=[0, 100]),
                    showlegend=False,
                    dragmode=False # 🛑 核心優化
                )
                st.plotly_chart(fig_rsi, use_container_width=True, config={'displayModeBar': False})

            else:
                st.error("❌ 找不到該股票代號！請確認代號是否輸入正確。")

# ----------------- 分頁 2：市場熱點雷達 -----------------
with tab2:
    st.markdown("### 🔥 今日全台股熱門焦點")
    st.markdown("股市名言：「有量才有價」。右邊的 **成交總額榜** 就是今天全台灣股民都在討論的新聞主角！")
    
    if st.button("📡 一鍵掃描今日台股市場", width="stretch"):
        with st.spinner("正在連線至台灣證券交易所獲取官方資料..."):
            try:
                url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers, timeout=10, verify=False)
                df_all = pd.DataFrame(res.json())
                df_all['TradeVolume'] = pd.to_numeric(df_all['TradeVolume'], errors='coerce')
                df_all['TradeValue'] = pd.to_numeric(df_all['TradeValue'], errors='coerce')
                
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("#### 💰 成交量排行榜 (散戶最愛)")
                    df_vol = df_all.sort_values(by='TradeVolume', ascending=False).head(10)
                    df_show_vol = df_vol[['Code', 'Name', 'ClosingPrice']].copy()
                    df_show_vol['成交量(張)'] = (df_vol['TradeVolume'] / 1000).astype(int)
                    df_show_vol.columns = ['代號', '名稱', '現價', '成交量(張)']
                    st.dataframe(df_show_vol, hide_index=True, use_container_width=True)

                with col_right:
                    st.markdown("#### 📰 成交總額排行榜 (法人與焦點)")
                    df_val = df_all.sort_values(by='TradeValue', ascending=False).head(10)
                    df_show_val = df_val[['Code', 'Name', 'ClosingPrice']].copy()
                    df_show_val['成交總額(億)'] = (df_val['TradeValue'] / 100000000).round(1)
                    df_show_val.columns = ['代號', '名稱', '現價', '成交總額(億)']
                    st.dataframe(df_show_val, hide_index=True, use_container_width=True)
                    
            except Exception as e:
                st.error("官方伺服器連線異常，請稍後再試。")

# ----------------- 分頁 3：存股退休計算機 -----------------
with tab3:
    if 'auto_growth' not in st.session_state:
        st.session_state.auto_growth = 5.0
    if 'auto_yield' not in st.session_state:
        st.session_state.auto_yield = 4.0

    st.markdown("### 💰 真實存股與提早退休計算機")
    st.markdown("想知道存哪一檔股票最划算？先查查它的歷史表現，系統會**自動幫你把數據填進下方的計算機**！")
    
    st.markdown("#### 🔍 第一步：查詢目標股票的歷史表現")
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        target_stock = st.text_input("💡 想存哪一檔？(上市/上櫃皆可)", value="0050", key="tab3_input")
    with col_s2:
        st.write("")
        fetch_btn = st.button("📊 查詢並自動帶入數據", width="stretch", key="tab3_btn")
        
    if fetch_btn:
        with st.spinner(f"正在回測 {target_stock} 過去五年的真實表現..."):
            try:
                t_stock = yf.Ticker(f"{target_stock}.TW")
                hist_5y = t_stock.history(period="5y")
                
                if hist_5y.empty:
                    t_stock = yf.Ticker(f"{target_stock}.TWO")
                    hist_5y = t_stock.history(period="5y")
                
                if not hist_5y.empty:
                    first_p = hist_5y['Close'].iloc[0]
                    last_p = hist_5y['Close'].iloc[-1]
                    years_span = len(hist_5y) / 252 
                    cagr = ((last_p / first_p) ** (1 / years_span)) - 1
                    
                    hist_1y = t_stock.history(period="1y")
                    div_sum = hist_1y['Dividends'].sum() if 'Dividends' in hist_1y.columns else 0
                    div_yield = (div_sum / last_p)
                    
                    cagr_percent = round(cagr * 100, 1)
                    yield_percent = round(div_yield * 100, 1)
                    st.session_state.auto_growth = min(max(cagr_percent, 0.0), 25.0) 
                    st.session_state.auto_yield = min(max(yield_percent, 0.0), 15.0)
                    
                    st.markdown(f"""
                    <div style='background-color: rgba(33, 150, 243, 0.15); padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3; margin-bottom: 20px;'>
                        <h3 style='color: #64B5F6; margin-top: 0;'>✅ 已自動為您帶入 {target_stock} 的歷史數據！</h3>
                        <ul style='color: #E0E0E0; font-size: 16px; line-height: 1.8;'>
                            <li>過去 <b>{years_span:.1f}</b> 年間，股價從 <b>{first_p:.1f}</b> 元成長至 <b>{last_p:.1f}</b> 元。</li>
                            <li>👉 平均年股價成長率：<b style='color:#EF5350;'>{cagr_percent}%</b></li>
                            <li>👉 近一年預估殖利率：<b style='color:#EF5350;'>{yield_percent}%</b></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ 找不到這檔股票的歷史資料，請確認代號是否正確。")
            except Exception as e:
                st.error("獲取資料失敗，請稍後再試。")
                
    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.info("📝 第二步：你的投資計畫")
        monthly_invest = st.number_input("💵 每月準備存多少錢？(元)", min_value=1000, value=10000, step=1000)
        years = st.slider("⏳ 打算持續存幾年？", min_value=1, max_value=40, value=10, step=1)
        
    with col_b:
        st.info("🎯 第三步：帶入上方查到的預估表現")
        capital_growth = st.slider("📈 預估股價年成長率 (%)", min_value=0.0, max_value=25.0, key="auto_growth", step=0.5)
        annual_yield = st.slider("💧 預估年殖利率/領息率 (%)", min_value=0.0, max_value=15.0, key="auto_yield", step=0.5)

    if years > 0:
        total_months = years * 12
        monthly_growth_rate = capital_growth / 100 / 12
        monthly_yield_rate = annual_yield / 100 / 12
        
        calc_data = [{"第幾年": 0, "投入總本金": 0, "股票總市值 (含複利)": 0, "預估該年領息": 0}]
        principal = 0
        total_shares_value = 0 
        
        for m in range(1, total_months + 1):
            principal += monthly_invest
            total_shares_value += monthly_invest
            total_shares_value *= (1 + monthly_growth_rate)
            
            monthly_dividend = total_shares_value * monthly_yield_rate
            total_shares_value += monthly_dividend
            
            if m % 12 == 0:
                current_year = m // 12
                yearly_passive_income = total_shares_value * (annual_yield / 100)
                calc_data.append({
                    "第幾年": current_year, 
                    "投入總本金": round(principal), 
                    "股票總市值 (含複利)": round(total_shares_value),
                    "預估該年領息": round(yearly_passive_income)
                })
        
        df_calc = pd.DataFrame(calc_data).set_index("第幾年")
        final_data = calc_data[-1]
        
        st.divider()
        st.markdown(f"<h3 style='text-align: center; color: #EF5350;'>🎉 {years} 年後的存股成果發表 🎉</h3>", unsafe_allow_html=True)
        st.write("")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.success("💼 你的投入總本金")
            st.metric(label="", value=f"{final_data['投入總本金']:,} 元")
        with col_r2:
            st.warning("🏆 最終股票總市值")
            st.metric(label="", value=f"{final_data['股票總市值 (含複利)']:,} 元")
        with col_r3:
            st.error("✨ 達成每月被動收入")
            monthly_passive = final_data['預估該年領息'] // 12
            st.metric(label="", value=f"{monthly_passive:,} 元 / 月")
        
        st.write("")
        st.markdown("#### 📈 財富雪球成長曲線圖")
        
        fig_retire = go.Figure()
        fig_retire.add_trace(go.Scatter(x=df_calc.index, y=df_calc['投入總本金'], fill='tozeroy', mode='lines', line=dict(color='#42A5F5', width=2), name='投入總本金', hovertemplate='本金: %{y:,.0f} 元'))
        fig_retire.add_trace(go.Scatter(x=df_calc.index, y=df_calc['股票總市值 (含複利)'], fill='tonexty', mode='lines', line=dict(color='#EF5350', width=2), name='總市值(含複利)', hovertemplate='市值: %{y:,.0f} 元'))
        fig_retire.update_layout(
            hovermode='x unified',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(title="存股第幾年"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            dragmode=False # 🛑 核心優化
        )
        st.plotly_chart(fig_retire, use_container_width=True, config={'displayModeBar': False}) # 🛑 核心優化
