import os
import io
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Modules
import modules.data_manager as dm
import modules.biostats as bs
import modules.plot_builder as pb
import modules.code_sandbox as cs

# Page Configuration
st.set_page_config(
    page_title="Super Xstat // 頂尖黑科技生物統計分析平台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech Tesla / SpaceX Dark Sci-Fi Aesthetic CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Typography & Deep Dark Sci-Fi Canvas */
    html, body, [class*="css"] {
        font-family: 'Rajdhani', 'Inter', 'Microsoft JhengHei', sans-serif;
        color: #E2E8F0;
    }

    /* Top HUD Cockpit Container */
    .hud-box {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(7, 10, 19, 0.95) 100%);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-left: 5px solid #00F0FF;
        border-radius: 6px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.08), inset 0 0 20px rgba(0, 240, 255, 0.02);
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
    }
    .hud-box::after {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 120px;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 240, 255, 0.05));
        pointer-events: none;
    }
    .hud-topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Orbitron', monospace;
        font-size: 0.8rem;
        letter-spacing: 2px;
        color: #94A3B8;
        margin-bottom: 8px;
    }
    .hud-badge-spacex {
        background: rgba(0, 240, 255, 0.12);
        border: 1px solid rgba(0, 240, 255, 0.4);
        color: #00F0FF;
        padding: 3px 10px;
        border-radius: 3px;
        font-weight: 700;
    }
    .hud-status {
        color: #00FF66;
        font-weight: 600;
        display: flex;
        align-items: center;
    }
    @keyframes pulse-beacon {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 10px #00FF66; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }
    .pulsing-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        background-color: #00FF66;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse-beacon 1.8s infinite ease-in-out;
    }
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.7rem;
        font-weight: 900;
        letter-spacing: 3.5px;
        background: linear-gradient(135deg, #FFFFFF 0%, #A5F3FC 40%, #00F0FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 240, 255, 0.35);
        margin: 2px 0 6px 0;
    }
    .accent-x {
        color: #E82127 !important;
        -webkit-text-fill-color: #E82127 !important;
        text-shadow: 0 0 25px rgba(232, 33, 39, 0.9);
        display: inline-block;
        transform: scale(1.08);
    }
    .hud-subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.15rem;
        color: #94A3B8;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 14px;
    }
    .hud-stats-bar {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        border-top: 1px solid rgba(0, 240, 255, 0.15);
        padding-top: 12px;
        font-family: 'Orbitron', monospace;
        font-size: 0.75rem;
    }
    .hud-stat-item {
        background: rgba(10, 15, 26, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 5px 12px;
        border-radius: 3px;
        display: flex;
        gap: 8px;
    }
    .hud-lbl { color: #64748B; }
    .hud-val { color: #00F0FF; font-weight: 700; }

    /* SpaceX Starship Angular Glass Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(10, 15, 26, 0.85);
        border: 1px solid rgba(0, 240, 255, 0.22);
        border-radius: 6px;
        padding: 6px;
        gap: 6px;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.5);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Orbitron', 'Rajdhani', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.2px !important;
        color: #94A3B8 !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 4px !important;
        padding: 8px 16px !important;
        transition: all 0.25s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00F0FF !important;
        background: rgba(0, 240, 255, 0.08) !important;
        border-color: rgba(0, 240, 255, 0.3) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, rgba(0, 240, 255, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
        color: #00F0FF !important;
        border: 1px solid rgba(0, 240, 255, 0.6) !important;
        border-bottom: 3px solid #00F0FF !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.3) !important;
    }

    /* Sci-Fi Metric HUD Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(8, 12, 22, 0.95) 100%) !important;
        border: 1px solid rgba(0, 240, 255, 0.22) !important;
        border-radius: 6px !important;
        padding: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 0 15px rgba(0, 240, 255, 0.02) !important;
        backdrop-filter: blur(10px) !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(0, 240, 255, 0.5) !important;
        transform: translateY(-2px);
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #94A3B8 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        color: #00F0FF !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.45) !important;
    }

    /* Tesla Cybertruck & SpaceX Action Buttons */
    button[kind="primary"] {
        background: linear-gradient(90deg, #E82127 0%, #FF1E40 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 30, 64, 0.6) !important;
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1.8px !important;
        font-weight: 700 !important;
        border-radius: 4px !important;
        box-shadow: 0 0 20px rgba(232, 33, 39, 0.45) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(90deg, #FF1E40 0%, #00F0FF 100%) !important;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.7) !important;
        border-color: #00F0FF !important;
        color: #07090E !important;
        transform: translateY(-1.5px);
    }
    button[kind="secondary"] {
        background: rgba(15, 23, 42, 0.8) !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        border-radius: 4px !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(0, 240, 255, 0.15) !important;
        border-color: #00F0FF !important;
        color: #00F0FF !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.35) !important;
    }

    /* High-Tech Containers & Dataframes */
    .stExpander {
        background: rgba(13, 19, 33, 0.75) !important;
        border: 1px solid rgba(0, 240, 255, 0.22) !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3) !important;
    }
    [data-testid="stSidebar"] {
        background-color: #080C14 !important;
        border-right: 1px solid rgba(0, 240, 255, 0.18) !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_name' not in st.session_state:
    st.session_state.df_name = ""
if 'active_code' not in st.session_state:
    st.session_state.active_code = ""

# Sidebar: Data Source & Selection
with st.sidebar:
    st.image("https://img.shields.io/badge/SUPER_XSTAT-v3.0_QUANTUM-00F0FF?style=for-the-badge&logo=spacex&logoColor=white", use_container_width=True)
    st.header("⚡ 數據匯入中心 // DATA DOCK")
    
    data_source = st.radio("資料來源", ["上傳自己的 Excel / CSV", "載入生醫示範數據庫"], index=1)
    
    uploaded_df = None
    df_name = ""
    
    if data_source == "上傳自己的 Excel / CSV":
        uploaded_file = st.file_uploader("選擇 Excel (.xlsx, .xls) 或 CSV 檔案", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            df_name = uploaded_file.name
            sheet_names = dm.get_excel_sheet_names(uploaded_file)
            selected_sheet = 0
            if sheet_names and len(sheet_names) > 1:
                selected_sheet = st.selectbox("選擇工作表 (Sheet)", sheet_names)
            try:
                uploaded_df = dm.load_data(uploaded_file, sheet_name=selected_sheet)
                st.success(f"資料載入成功: {df_name}")
            except Exception as e:
                st.error(f"讀取失敗: {e}")
    else:
        sample_options = {
            "植物生長試驗 (anova plant growth.xlsx)": "sample_data/anova_plant_growth.xlsx",
            "臨床試驗隊列 (Clinical Trial Cohort)": "sample_data/clinical_trial_data.xlsx",
            "癌症存活追蹤數據 (Cancer Survival)": "sample_data/cancer_survival_data.xlsx",
            "基因差異表現 (Gene Expression Volcano)": "sample_data/gene_expression_volcano.xlsx"
        }
        selected_sample = st.selectbox("選擇生醫示範數據", list(sample_options.keys()), index=0)
        sample_path = sample_options[selected_sample]
        if os.path.exists(sample_path):
            df_name = os.path.basename(sample_path)
            uploaded_df = pd.read_excel(sample_path)
            st.info(f"已啟用數據矩陣：`{selected_sample}`")
        else:
            st.warning("範例檔案建構中...")

    if uploaded_df is not None:
        st.session_state.df = uploaded_df
        st.session_state.df_name = df_name

    st.markdown("---")
    st.markdown("### 🛠️ 量子運算模組")
    st.caption("• **自動推論決策精靈** 智慧引導適法統計\n• **結構化分析報告** 自動產出期刊醫學結論\n• **全自訂 X/Y 尺度** 線性/對數/數值範圍\n• **文字標籤與字級控制** 支援文字刻度與傾斜旋轉\n• **Tesla/SpaceX 出版級匯出** 300/600 DPI & 向量 SVG/PDF")

# Main Header - Tesla / SpaceX Cockpit HUD Banner
st.markdown("""
<div class="hud-box">
  <div class="hud-topline">
    <span class="hud-badge-spacex">SPACEX // TESLA INFERENCE ENGINE</span>
    <span class="hud-status"><span class="pulsing-dot"></span>SYS_CORE: OPERATIONAL</span>
    <span>ENCRYPTION: 512-BIT QUANTUM // LATENCY: 0.42ms</span>
  </div>
  <div class="hud-title">SUPER <span class="accent-x">X</span>STAT</div>
  <div class="hud-subtitle">AEROSPACE-GRADE BIOSTATISTICAL INTELLIGENCE & HIGH-PRECISION VISUALIZATION PLATFORM</div>
  <div class="hud-stats-bar">
    <div class="hud-stat-item"><span class="hud-lbl">FLIGHT_COMPUTER</span><span class="hud-val">STARSHIP_BIO_v3.0</span></div>
    <div class="hud-stat-item"><span class="hud-lbl">INFERENCE_CORE</span><span class="hud-val">QUANTUM GAUSSIAN</span></div>
    <div class="hud-stat-item"><span class="hud-lbl">VECTOR_ENGINE</span><span class="hud-val">SEABORN // MATPLOTLIB ACCELERATED</span></div>
    <div class="hud-stat-item"><span class="hud-lbl">TELEMETRY_LINK</span><span class="hud-val">STARLINK ACTIVE</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_data, tab_stats, tab_plots, tab_code, tab_export = st.tabs([
    "⚡ 01 // DATA MATRIX (數據矩陣)",
    "🔮 02 // STATISTICAL CORE (推論運算核心)",
    "🚀 03 // SPECTRUM STUDIO (高精圖表工坊)",
    "💻 04 // NEURAL CODE LAB (自主程式實驗室)",
    "🛰️ 05 // MISSION CONTROL (指令與發佈中心)"
])

# Guard condition if no data is loaded
if st.session_state.df is None:
    for tab in [tab_data, tab_stats, tab_plots, tab_code, tab_export]:
        with tab:
            st.info("請於左側面板上傳 Excel/CSV 檔案或選取內建示範數據，以啟動分析模組。")
    st.stop()

df = st.session_state.df
col_info = dm.classify_columns(df)
numeric_cols = col_info['numeric']
categorical_cols = col_info['categorical']
all_cols = list(df.columns)

# ==============================================================================
# TAB 1: 數據管理 (Data Hub)
# ==============================================================================
with tab_data:
    st.subheader(f"📊 當前數據集摘要：`{st.session_state.df_name}`")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("總樣本數 (Rows)", f"{len(df):,}")
    m2.metric("總變項數 (Columns)", f"{len(df.columns):,}")
    m3.metric("數值型變項 (Numeric)", f"{len(numeric_cols)}")
    m4.metric("類別/分組變項 (Categorical)", f"{len(categorical_cols)}")
    
    st.markdown("#### 🔍 數據表格預覽")
    st.dataframe(df.head(100), use_container_width=True)
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 📋 變項欄位屬性分類")
        info_records = []
        for col in df.columns:
            dtype_str = "數值型 (Numeric)" if col in numeric_cols else ("類別型 (Categorical)" if col in categorical_cols else "其他文字/日期")
            n_unique = df[col].nunique()
            n_missing = df[col].isna().sum()
            info_records.append({
                "變項名稱": col,
                "數據型態": dtype_str,
                "非重覆值數 (Unique)": n_unique,
                "缺失值個數 (Missing)": n_missing,
                "缺失比例 (%)": f"{(n_missing/len(df)*100):.1f}%"
            })
        st.dataframe(pd.DataFrame(info_records), use_container_width=True, height=280)
        
    with c2:
        st.markdown("#### 🩺 數據品質與缺失值檢測")
        missing_summary = dm.get_missing_summary(df)
        if not missing_summary.empty:
            st.dataframe(missing_summary, use_container_width=True, height=280)
        else:
            st.success("✅ 數據完整無缺漏，所有欄位均無缺失值！")

# ==============================================================================
# TAB 2: 生物統計分析與完整報告 (Biostats)
# ==============================================================================
with tab_stats:
    # 智慧統計決策推薦精靈
    with st.expander("🎯 智慧統計方法推薦決策精靈 (Statistical Method Advisor) — 點擊展開引導", expanded=False):
        st.markdown("""
        生醫研究中，正確使用統計方法至關重要。請選擇您的**研究分析目的**，系統將提供正規國際期刊認可的最佳統計檢定建議與適法性條件：
        """)
        ad_col1, ad_col2 = st.columns(2)
        with ad_col1:
            ad_goal = st.selectbox("您的研究目標是什麼？", [
                "比較兩組獨立樣本差異 (例如：治療組 vs 對照組)",
                "前後測配對樣本比較 (例如：同批患者用藥前 vs 用藥後)",
                "比較三組以上多組樣本差異 (例如：安慰劑 vs 低劑量 vs 高劑量)",
                "分析兩類別變項之關聯性 (例如：用藥組別與不良反應發生率)",
                "分析病患存活時間與風險因子 (帶有 Censored 追蹤數據)",
                "二元臨床預後預測 (例如：治療反應 有效 vs 無效)"
            ])
        with ad_col2:
            st.markdown("##### 📌 統計學指引與前提條件")
            if "兩組獨立" in ad_goal:
                st.info("""
                - **黃金標準**：若兩組皆符合**常態分佈**且**變異數齊一** ➔ **Student's t-test**。
                - **變異數不齊一**：若常態但變異數不齊 (Levene's p < 0.05) ➔ **Welch's t-test** (自由度修正)。
                - **偏態/非常態**：若偏離常態 (Shapiro-Wilk p < 0.05) ➔ **Mann-Whitney U 檢定** (無母數)。
                """)
            elif "前後測配對" in ad_goal:
                st.info("""
                - **黃金標準**：若前後測**差值符合常態分佈** ➔ **Paired t-test** (配對 t 檢定)。
                - **偏態/非常態**：若差值不符常態 ➔ **Wilcoxon Signed-Rank Test** (符號等級檢定)。
                """)
            elif "三組以上" in ad_goal:
                st.info("""
                - **黃金標準**：符合常態與齊一 ➔ **One-way ANOVA** + **Tukey HSD 事後檢定**。
                - **雙因子交互作用**：探討兩種因子 (如藥物×性別) ➔ **Two-way ANOVA**。
                - **偏態/非常態**：偏態分佈 ➔ **Kruskal-Wallis 檢定**。
                """)
            elif "類別變項" in ad_goal:
                st.info("""
                - **格子期望值 ≥ 5** ➔ **皮爾森卡方檢定 (Chi-Square Test)**。
                - **任一格子期望值 < 5** ➔ 必須採用 **費雪精確檢定 (Fisher's Exact Test)**。
                """)
            elif "存活時間" in ad_goal:
                st.info("""
                - **單變項曲線與組別比較** ➔ **Kaplan-Meier 估計量 + Log-Rank 檢定**。
                - **多變項風險因子校正** ➔ **Cox 比例風險模型 (Cox PH)** 計算 Hazard Ratio (HR)。
                """)
            elif "二元臨床預後" in ad_goal:
                st.info("""
                - **二元疾病預測** ➔ **二元邏輯斯迴歸 (Logistic Regression)** 計算勝算比 (Odds Ratio, OR)。
                """)

    st.markdown("---")
    
    stat_task = st.selectbox("選擇統計分析方法", [
        "1. 敘述性統計與常態性檢定 (Descriptive Statistics & Shapiro-Wilk)",
        "2. 兩組獨立樣本差異檢定 (Two-Group: Student's t / Welch's t / Mann-Whitney U)",
        "3. 配對樣本前後測檢定 (Paired Samples: Paired t / Wilcoxon Signed-Rank) ⭐",
        "4. 多組單因子變異數分析 (Multi-Group: One-way ANOVA & Kruskal-Wallis)",
        "5. 雙因子變異數分析 (Two-way ANOVA with Interaction A*B) ⭐",
        "6. 類別變項交叉列聯表 (Contingency: Chi-square / Fisher's Exact / Odds Ratio)",
        "7. 相關係數分析矩陣 (Correlation Matrix: Pearson / Spearman / Kendall)",
        "8. Kaplan-Meier 存活分析與 Log-Rank 檢定 (Survival Analysis)",
        "9. Cox 比例風險迴歸模型 (Cox Proportional Hazards Regression) ⭐",
        "10. 二元邏輯斯迴歸分析 (Binary Logistic Regression: Odds Ratios) ⭐",
        "11. 多元線性迴歸分析 (Linear Regression OLS)"
    ])
    
    st.markdown("---")
    
    # 1. 敘述統計
    if "1. 敘述性統計" in stat_task:
        st.markdown("##### 📌 數值變項敘述性統計與常態性檢定 (Mean, SD, Median, IQR, Shapiro-Wilk)")
        selected_num_cols = st.multiselect("選取要分析的數值欄位", numeric_cols, default=numeric_cols[:min(6, len(numeric_cols))])
        if selected_num_cols:
            desc_df = bs.calculate_descriptive_stats(df, selected_num_cols)
            st.dataframe(desc_df, use_container_width=True)
            
            # Export CSV
            csv_data = desc_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下載敘述統計結果 (CSV)", csv_data, "descriptive_stats.csv", "text/csv")
        else:
            st.warning("請至少選取一個數值型變項。")
            
    # 2. 兩組比較
    elif "2. 兩組獨立樣本" in stat_task:
        st.markdown("##### 📌 兩組差異檢定 (自動判定常態性與 Levene 齊一性，推薦 Student's / Welch's / Mann-Whitney)")
        c1, c2, c3 = st.columns(3)
        with c1:
            val_col = st.selectbox("分析數值變項 (Y)", numeric_cols)
        with c2:
            two_group_candidates = [c for c in categorical_cols if df[c].dropna().nunique() == 2]
            fallback_cats = categorical_cols if categorical_cols else all_cols
            grp_col = st.selectbox("分組變項 (恰好 2 組)", two_group_candidates if two_group_candidates else fallback_cats)
        with c3:
            method_choice = st.selectbox("檢定方法", ["auto (依檢定假設自動推薦)", "student_t", "welch_t", "mann_whitney"])
            
        if st.button("🚀 執行兩組檢定並產出報告", type="primary"):
            try:
                res = bs.two_group_comparison(df, val_col, grp_col, method_choice.split()[0])
                
                st.info(f"💡 **統計方法適法性診斷**：採用 `{res['檢定方法']}`。理由：{res['推薦依據']}")
                
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("檢定方法", res['檢定方法'])
                c_b.metric("檢定統計量", f"{res['統計量']:.4f}")
                p_disp = f"{res['p值']:.4e}" if res['p值'] < 0.001 else f"{res['p值']:.4f}"
                c_c.metric("p 值 (顯著性)", p_disp, delta="顯著 (p<0.05)" if res['顯著性 (p < 0.05)'] else "未達顯著", delta_color="normal" if res['顯著性 (p < 0.05)'] else "inverse")
                
                st.markdown("##### 📊 組別平均值與統計指標比較")
                comp_table = pd.DataFrame([
                    {"組別": res['組別 1 名稱'], "樣本數 N": res['組別 1 樣本數'], "Mean ± SD": f"{res['組別 1 平均值']} ± {res['組別 1 標準差']}", "Median (IQR)": f"{res['組別 1 中位數']} ({res['組別 1 IQR']})", "Shapiro 常態 p值": res['組別 1 常態 p值']},
                    {"組別": res['組別 2 名稱'], "樣本數 N": res['組別 2 樣本數'], "Mean ± SD": f"{res['組別 2 平均值']} ± {res['組別 2 標準差']}", "Median (IQR)": f"{res['組別 2 中位數']} ({res['組別 2 IQR']})", "Shapiro 常態 p值": res['組別 2 常態 p值']}
                ])
                st.table(comp_table)
                
                st.markdown(f"""
                - **平均差異 (95% CI)**: `{res['平均差值']} [{res['95% 信賴區間下限']}, {res['95% 信賴區間上限']}]`
                - **效果值 (Cohen's d)**: `{res['Cohen d 效果值']}`
                - **變異數齊一性 (Levene's p)**: `{res['Levene 檢定 p值']}` ({'齊一' if res['變異數齊一'] else '不齊一'})
                """)
                
                # Full Clinical Report
                rep_md = bs.generate_clinical_report("two_group", res, f"{val_col} 在 {grp_col} 間之組別差異")
                with st.expander("📄 查看完整醫學統計分析報告 (Structured Clinical Report)", expanded=True):
                    st.markdown(rep_md)
                    st.download_button("📥 下載完整分析報告 (Markdown 格式)", rep_md.encode('utf-8'), f"Report_TwoGroup_{val_col}.md", "text/markdown")
            except Exception as e:
                st.error(f"檢定過程出錯: {e}")

    # 3. 配對樣本前後測
    elif "3. 配對樣本前後測" in stat_task:
        st.markdown("##### 📌 配對樣本檢定 (前後測配對 t-test / 威爾卡森符號等級檢定 Wilcoxon)")
        c1, c2, c3 = st.columns(3)
        with c1:
            pre_c = st.selectbox("前測數值變項 (Pre)", numeric_cols, index=0)
        with c2:
            post_c = st.selectbox("後測數值變項 (Post)", [c for c in numeric_cols if c != pre_c], index=0)
        with c3:
            p_method = st.selectbox("檢定方法", ["auto (自動依差值常態性判定)", "paired_t", "wilcoxon"])
            
        if st.button("🚀 執行前後測配對檢定", type="primary"):
            try:
                p_res = bs.paired_samples_comparison(df, pre_c, post_c, p_method.split()[0])
                st.info(f"💡 **適法性引導**：採用 `{p_res['檢定方法']}`。理由：{p_res['推薦依據']}")
                
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("配對樣本數", f"{p_res['配對樣本數 (N)']} 筆")
                c_b.metric("平均差值 (Post - Pre)", f"{p_res['平均差值 (Post - Pre)']}")
                p_disp = f"{p_res['p值']:.4e}" if p_res['p值'] < 0.001 else f"{p_res['p值']:.4f}"
                c_c.metric("檢定 p 值", p_disp, delta="顯著差異 (p<0.05)" if p_res['顯著性 (p < 0.05)'] else "無顯著差異")
                
                st.markdown(f"""
                - **前測 Baseline**: `{p_res['前測 Mean ± SD']}` | **後測 Post**: `{p_res['後測 Mean ± SD']}`
                - **差值 95% 信賴區間**: `{p_res['差值 95% 信賴區間']}`
                - **配對效果值 (Cohen dz)**: `{p_res['配對效果值 (Cohen dz)']}`
                - **差值常態性檢定 (Shapiro-Wilk p)**: `{p_res['差值常態性檢定 p值']}`
                """)
                
                p_rep = bs.generate_clinical_report("paired", p_res, f"{pre_c} 與 {post_c} 前後測配對檢定")
                with st.expander("📄 查看完整配對檢定醫學報告", expanded=True):
                    st.markdown(p_rep)
                    st.download_button("📥 下載配對分析報告", p_rep.encode('utf-8'), f"Report_Paired_{pre_c}_{post_c}.md", "text/markdown")
            except Exception as e:
                st.error(f"配對檢定出錯: {e}")

    # 4. 多組 ANOVA
    elif "4. 多組單因子" in stat_task:
        st.markdown("##### 📌 多組單因子比較 (One-way ANOVA、Kruskal-Wallis 與 Tukey HSD 事後多重比較)")
        c1, c2 = st.columns(2)
        with c1:
            val_col = st.selectbox("分析數值變項 (Y)", numeric_cols, key="anova_val")
        with c2:
            grp_col = st.selectbox("分組變項 (≥2 組)", categorical_cols if categorical_cols else all_cols, key="anova_grp")
            
        if st.button("🚀 執行多組變異數分析", type="primary"):
            try:
                res = bs.multi_group_comparison(df, val_col, grp_col)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("組別數量", f"{res['組別數']} 組")
                c_b.metric("ANOVA F 統計量", f"{res['ANOVA F 值']:.4f}")
                p_disp = f"{res['ANOVA p 值']:.4e}" if res['ANOVA p 值'] < 0.001 else f"{res['ANOVA p 值']:.4f}"
                c_c.metric("ANOVA p 值", p_disp, delta="組間有顯著差異" if res['ANOVA 顯著性 (p < 0.05)'] else "無顯著差異")
                
                st.markdown("##### 📊 各組數值統計摘要")
                st.dataframe(res['各組摘要'], use_container_width=True)
                st.markdown(f"**非參數 Kruskal-Wallis H**: `{res['Kruskal-Wallis H 值']:.4f}` (p = `{res['Kruskal-Wallis p 值']:.4e}`)")
                
                if res['Tukey HSD 事後檢定'] is not None and not res['Tukey HSD 事後檢定'].empty:
                    st.markdown("##### 🔍 Tukey HSD 事後兩兩檢定 (Pairwise Comparisons)")
                    st.dataframe(res['Tukey HSD 事後檢定'], use_container_width=True)
            except Exception as e:
                st.error(f"分析失敗: {e}")

    # 5. 雙因子變異數分析 (Two-Way ANOVA)
    elif "5. 雙因子變異數分析" in stat_task:
        st.markdown("##### 📌 雙因子變異數分析 (Two-Way ANOVA：分析因子 A、因子 B 與交互作用 A × B)")
        c1, c2, c3 = st.columns(3)
        with c1:
            y_col_2w = st.selectbox("數值應變項 (Y)", numeric_cols, key="2w_y")
        with c2:
            f1_col = st.selectbox("自變項因子 1 (Factor A)", categorical_cols if categorical_cols else all_cols, key="2w_f1")
        with c3:
            f2_col = st.selectbox("自變項因子 2 (Factor B)", [c for c in (categorical_cols if categorical_cols else all_cols) if c != f1_col], key="2w_f2")
            
        if st.button("🚀 執行雙因子 ANOVA", type="primary"):
            try:
                res_2w = bs.two_way_anova(df, y_col_2w, f1_col, f2_col)
                st.metric("模型決定係數 (R²)", f"{res_2w['r_squared']:.4f}")
                st.markdown("##### 📋 雙因子 ANOVA 變異數分析表")
                st.dataframe(res_2w['anova_table'], use_container_width=True)
                
                # Check interaction significance
                inter_idx = f"交互作用: {f1_col} × {f2_col}"
                if inter_idx in res_2w['anova_table'].index:
                    is_inter_sig = res_2w['anova_table'].loc[inter_idx, '顯著性 (p < 0.05)']
                    if is_inter_sig:
                        st.warning(f"💡 觀察到 `{f1_col}` 與 `{f2_col}` 之間存在統計學**顯著交互作用** (p < 0.05)，表示因子 A 的效果會隨著因子 B 的組別而改變！")
                    else:
                        st.success(f"✅ 交互作用未達顯著水準 (p ≥ 0.05)，可分別檢驗兩因子的獨立主效應。")
            except Exception as e:
                st.error(f"雙因子分析出錯: {e}")

    # 6. 列聯表卡方
    elif "6. 類別變項" in stat_task:
        st.markdown("##### 📌 列聯表與卡方檢定 (Chi-square / Fisher's Exact / Odds Ratio)")
        c1, c2 = st.columns(2)
        with c1:
            r_col = st.selectbox("橫列變項 (Row Variable)", categorical_cols if categorical_cols else all_cols, key="chi_row")
        with c2:
            c_col = st.selectbox("直欄變項 (Column Variable)", [c for c in (categorical_cols if categorical_cols else all_cols) if c != r_col], key="chi_col")
            
        if st.button("🚀 執行卡方檢定", type="primary"):
            try:
                res = bs.contingency_analysis(df, r_col, c_col)
                st.info(f"💡 {res['適法性診斷']}")
                
                st.markdown("##### 📊 交叉次數列聯表 (Observed Frequencies)")
                st.dataframe(res['觀察頻次列聯表'], use_container_width=True)
                
                ca, cb, cc = st.columns(3)
                ca.metric("卡方值 (Chi-Square)", f"{res['卡方統計量']:.4f}")
                cb.metric("自由度 (df)", res['自由度'])
                p_txt = f"{res['卡方 p 值']:.4e}" if res['卡方 p 值'] < 0.001 else f"{res['卡方 p 值']:.4f}"
                cc.metric("卡方 p 值", p_txt, delta="關聯顯著 (p<0.05)" if res['顯著性 (p < 0.05)'] else "無顯著關聯")
                
                if res.get('Fisher Exact p 值') is not None:
                    st.success(f"💡 2x2 列聯表費雪精確檢定 (Fisher's Exact p): `{res['Fisher Exact p 值']:.4e}` | 勝算比 (Odds Ratio): `{res['Odds Ratio']}`")
            except Exception as e:
                st.error(f"檢定出錯: {e}")

    # 7. 相關矩陣
    elif "7. 相關係數" in stat_task:
        st.markdown("##### 📌 相關分析 (Pearson / Spearman 矩陣與雙尾 p-value)")
        c1, c2 = st.columns([1, 3])
        with c1:
            corr_m = st.radio("相關係數類型", ["pearson", "spearman", "kendall"])
        with c2:
            corr_cols = st.multiselect("選取相關分析欄位", numeric_cols, default=numeric_cols[:min(6, len(numeric_cols))])
            
        if len(corr_cols) >= 2:
            r_df, p_df, pairs_df = bs.correlation_matrix(df, corr_cols, corr_m)
            st.markdown("##### 相關係數矩陣 (r)")
            st.dataframe(r_df.style.background_gradient(cmap='coolwarm', vmin=-1, vmax=1).format("{:.3f}"), use_container_width=True)
            st.markdown("##### 兩兩顯著相關排序表")
            st.dataframe(pairs_df, use_container_width=True)
        else:
            st.warning("請選取至少 2 個數值欄位。")

    # 8. 生存分析
    elif "8. Kaplan-Meier" in stat_task:
        st.markdown("##### 📌 生存分析 (Kaplan-Meier 估計量與 Log-Rank 檢定)")
        c1, c2, c3 = st.columns(3)
        with c1:
            t_col = st.selectbox("存活時間變項 (Time)", numeric_cols, key="surv_time")
        with c2:
            e_col = st.selectbox("事件狀態變項 (Event: 1=發生, 0=設限)", numeric_cols if numeric_cols else all_cols, key="surv_evt")
        with c3:
            g_col = st.selectbox("分組比較變項 (選填)", [None] + categorical_cols, key="surv_grp")
            
        if st.button("🚀 擬合 Kaplan-Meier 存活模型", type="primary"):
            try:
                surv_res = bs.fit_survival_analysis(df, t_col, e_col, g_col)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("總樣本數", surv_res['樣本總數'])
                c_b.metric("事件發生數 (Events)", surv_res['事件發生數'])
                c_c.metric("設限比例 (Censored %)", f"{surv_res['設限比例 (%)']}%")
                
                st.markdown("##### ⏱️ 各組中位存活時間 (Median Survival)")
                st.table(pd.DataFrame(list(surv_res['中位存活時間'].items()), columns=['組別', '中位存活時間']))
                
                if surv_res.get('Log-Rank p 值') is not None:
                    st.success(f"Log-Rank 組間差異檢定統計量: `{surv_res['Log-Rank 統計量']:.4f}` | p-value: `{surv_res['Log-Rank p 值']:.4e}`")
            except Exception as e:
                st.error(f"存活分析錯誤: {e}")

    # 9. Cox 比例風險模型
    elif "9. Cox 比例風險" in stat_task:
        st.markdown("##### 📌 Cox 比例風險迴歸模型 (計算各風險因子之 Hazard Ratio, 95% CI 與 Wald 檢定)")
        c1, c2, c3 = st.columns(3)
        with c1:
            cx_t = st.selectbox("存活時間 (Time)", numeric_cols, key="cox_t")
        with c2:
            cx_e = st.selectbox("事件狀態 (Event: 1/0)", numeric_cols if numeric_cols else all_cols, key="cox_e")
        with c3:
            candidate_covs = [c for c in all_cols if c not in [cx_t, cx_e]]
            cx_covs = st.multiselect("共變量危險因子 (Covariates)", candidate_covs, default=candidate_covs[:min(4, len(candidate_covs))])
            
        if cx_covs and st.button("🚀 擬合 Cox PH 模型", type="primary"):
            try:
                cox_res = bs.fit_cox_ph(df, cx_t, cx_e, cx_covs)
                c1, c2, c3 = st.columns(3)
                c1.metric("C-Index (模型鑑別力)", f"{cox_res['c_index']:.3f}")
                c2.metric("有效樣本數 / 事件數", f"{cox_res['n_obs']} / {cox_res['n_events']}")
                c3.metric("對數概似值 (Log-Likelihood)", f"{cox_res['log_likelihood']}")
                
                st.markdown("##### 📋 Cox 危害比 (Hazard Ratio) 與 95% 信賴區間")
                st.dataframe(cox_res['coef_table'], use_container_width=True)
            except Exception as e:
                st.error(f"Cox 模型擬合出錯: {e}")

    # 10. 二元邏輯斯迴歸
    elif "10. 二元邏輯斯" in stat_task:
        st.markdown("##### 📌 二元邏輯斯迴歸分析 (Binary Logistic Regression：計算勝算比 Odds Ratio 與 95% CI)")
        c1, c2 = st.columns([1, 2])
        with c1:
            two_val_cols = [c for c in all_cols if df[c].dropna().nunique() == 2]
            log_y = st.selectbox("二元應變項 (Y, 2種狀態)", two_val_cols if two_val_cols else all_cols, key="log_y")
        with c2:
            log_xs = st.multiselect("預測變項 (X)", [c for c in all_cols if c != log_y], default=[c for c in numeric_cols if c != log_y][:min(3, len(numeric_cols))])
            
        if log_xs and st.button("🚀 擬合邏輯斯迴歸模型", type="primary"):
            try:
                log_res = bs.fit_logistic_regression(df, log_y, log_xs)
                st.metric("McFadden's Pseudo R²", f"{log_res['pseudo_r2']:.4f}")
                st.markdown("##### 📋 邏輯斯迴歸係數與勝算比 (Odds Ratio) 表")
                st.dataframe(log_res['coef_table'], use_container_width=True)
            except Exception as e:
                st.error(f"邏輯斯迴歸出錯: {e}")

    # 11. 線性迴歸
    elif "11. 多元線性" in stat_task:
        st.markdown("##### 📌 多元線性迴歸分析 (OLS Regression)")
        c1, c2 = st.columns([1, 2])
        with c1:
            y_col = st.selectbox("應變項 (Dependent Variable Y)", numeric_cols, key="reg_y")
        with c2:
            x_cols = st.multiselect("自變項 (Independent Variables X)", [c for c in numeric_cols if c != y_col], default=[c for c in numeric_cols if c != y_col][:min(3, len(numeric_cols)-1)])
            
        if x_cols and st.button("🚀 執行 OLS 迴歸擬合", type="primary"):
            try:
                reg_res = bs.fit_linear_regression(df, y_col, x_cols)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("決定係數 R²", f"{reg_res['R平方 (R2)']:.4f}")
                c_b.metric("調整後 R²", f"{reg_res['調整後 R平方']:.4f}")
                c_c.metric("模型 F 檢定 p 值", f"{reg_res['F 檢定 p 值']:.4e}")
                
                st.markdown("##### 📋 迴歸係數表與 95% 信賴區間")
                st.dataframe(reg_res['係數表'], use_container_width=True)
            except Exception as e:
                st.error(f"迴歸擬合錯誤: {e}")

# ==============================================================================
# TAB 3: 視覺化圖表工坊 (Plot Studio)
# ==============================================================================
with tab_plots:
    st.subheader("🎨 出版級生醫視覺化圖表工坊 (全自訂 X/Y 尺度與字級)")
    
    col_ctrl, col_view = st.columns([1.1, 2.2])
    
    with col_ctrl:
        st.markdown("#### 1. 選擇圖表類型")
        plot_type = st.selectbox("圖表類別", [
            "箱形圖 / 小提琴圖 + 抖動散佈 (Box / Violin + Jitter)",
            "Kaplan-Meier 生存曲線 (Survival Curve)",
            "差異表現火山圖 (Volcano Plot)",
            "相關係數熱圖 (Correlation Heatmap)",
            "散佈圖與線性迴歸 (Scatter + OLS Fit)",
            "均值與誤差條柱狀圖 (Bar + SEM/SD)",
            "機率分佈與密度圖 (Histogram + KDE)",
            "主成分分析投影 (PCA Biplot)"
        ])
        
        st.markdown("#### 2. 變項配置")
        if "Box / Violin" in plot_type:
            pt_mode = st.radio("繪製子型態", ["Boxplot + Jitter", "Violin Plot", "Strip Plot Only"], horizontal=True)
            default_cat_idx = all_cols.index(categorical_cols[0]) if categorical_cols else 0
            px = st.selectbox("X 軸 (類別 / 文字欄位)", all_cols, index=default_cat_idx)
            py = st.selectbox("Y 軸 (分析數值)", numeric_cols if numeric_cols else all_cols)
            phue = st.selectbox("次分組 (Hue, 選填)", [None] + categorical_cols)
            is_current_x_numeric = pd.api.types.is_numeric_dtype(df[px])
        elif "Survival Curve" in plot_type:
            ptime = st.selectbox("時間變項 (Time)", numeric_cols, key="plot_surv_time")
            pevt = st.selectbox("事件變項 (Event: 1=發生, 0=設限)", numeric_cols if numeric_cols else all_cols, key="plot_surv_evt")
            pgrp = st.selectbox("分組變項 (選填)", [None] + categorical_cols, key="plot_surv_grp")
            pci = st.checkbox("顯示 95% 信賴區間", value=True)
            pmed = st.checkbox("標註中位存活時間虛線", value=True)
            is_current_x_numeric = True
        elif "Volcano Plot" in plot_type:
            pfc = st.selectbox("Log2 Fold Change 欄位", numeric_cols, index=0)
            ppval = st.selectbox("P-value 欄位", [c for c in numeric_cols if c != pfc], index=0)
            gene_candidates = [c for c in all_cols if c not in [pfc, ppval]]
            pgene = st.selectbox("基因/特徵標籤欄位 (選填)", [None] + gene_candidates)
            fc_th = st.number_input("Log2 FC 顯著閾值", value=1.0, step=0.1)
            pval_th = st.number_input("P-value 顯著閾值", value=0.05, step=0.01)
            is_current_x_numeric = True
        elif "Correlation Heatmap" in plot_type:
            p_corr_cols = st.multiselect("選取熱圖欄位 (≥2)", numeric_cols, default=numeric_cols[:min(7, len(numeric_cols))])
            p_corr_m = st.selectbox("相關方法", ["pearson", "spearman"])
            p_annot = st.checkbox("標註相關係數數值", value=True)
            is_current_x_numeric = False
        elif "Scatter + OLS Fit" in plot_type:
            ps_x = st.selectbox("X 軸欄位 (數值或類別文字)", all_cols, index=0)
            ps_y = st.selectbox("Y 軸數值欄位", [c for c in numeric_cols if c != ps_x], index=0)
            ps_hue = st.selectbox("顏色分類 (Hue, 選填)", [None] + categorical_cols)
            ps_ci = st.checkbox("顯示 95% 迴歸信賴區間", value=True)
            is_current_x_numeric = pd.api.types.is_numeric_dtype(df[ps_x])
        elif "Bar + SEM/SD" in plot_type:
            default_cat_idx = all_cols.index(categorical_cols[0]) if categorical_cols else 0
            pb_x = st.selectbox("X 軸 (類別 / 文字欄位)", all_cols, index=default_cat_idx)
            pb_y = st.selectbox("Y 軸 (數值)", numeric_cols if numeric_cols else all_cols)
            pb_hue = st.selectbox("次分組 (Hue, 選填)", [None] + categorical_cols)
            pb_err = st.radio("誤差條類型", ["se (標準誤 SEM)", "sd (標準差 SD)"])
            is_current_x_numeric = pd.api.types.is_numeric_dtype(df[pb_x])
        elif "Histogram + KDE" in plot_type:
            ph_col = st.selectbox("分析欄位 (數值型分佈 或 文字型計數)", all_cols)
            ph_hue = st.selectbox("分組疊加 (Hue, 選填)", [None] + categorical_cols)
            ph_bins = st.slider("組數 (Bins)", 10, 60, 25)
            ph_kde = st.checkbox("顯示核密度估計 (KDE 曲線)", value=True)
            is_current_x_numeric = pd.api.types.is_numeric_dtype(df[ph_col])
        elif "PCA Biplot" in plot_type:
            pca_features = st.multiselect("選取 PCA 特徵欄位 (≥2)", numeric_cols, default=numeric_cols[:min(8, len(numeric_cols))])
            pca_label = st.selectbox("標籤著色欄位 (選填)", [None] + categorical_cols)
            is_current_x_numeric = True

        st.markdown("#### 3. 🎨 視覺美學與座標軸客製化")
        
        with st.expander("📐 座標軸尺度與數值範圍 (X/Y Scale & Limits)", expanded=True):
            col_sc1, col_sc2 = st.columns(2)
            with col_sc1:
                if not is_current_x_numeric:
                    st.info("🏷️ **X 軸文字模式**：當前 X 軸為文字標籤，系統已自動確保文字完整呈現。對數尺度與自訂範圍僅適用於連續數值軸。")
                    x_scale_val = "linear"
                    x_custom_lim = False
                    x_min, x_max = None, None
                else:
                    x_scale_opt = st.selectbox("X 軸尺度 (Scale)", ["linear (線性)", "log (對數 Log10)"])
                    x_scale_val = "log" if "log" in x_scale_opt else "linear"
                    x_custom_lim = st.checkbox("自訂 X 軸數值範圍", value=False)
                    x_min, x_max = None, None
                    if x_custom_lim:
                        x_c1, x_c2 = st.columns(2)
                        x_min = x_c1.number_input("X 軸最小值", value=0.0)
                        x_max = x_c2.number_input("X 軸最大值", value=100.0)
            with col_sc2:
                y_scale_opt = st.selectbox("Y 軸尺度 (Scale)", ["linear (線性)", "log (對數 Log10)"])
                y_scale_val = "log" if "log" in y_scale_opt else "linear"
                y_custom_lim = st.checkbox("自訂 Y 軸數值範圍", value=False)
                y_min, y_max = None, None
                if y_custom_lim:
                    y_c1, y_c2 = st.columns(2)
                    y_min = y_c1.number_input("Y 軸最小值", value=0.0)
                    y_max = y_c2.number_input("Y 軸最大值", value=100.0)

        with st.expander("🔤 座標文字大小與標籤 (Font Sizes & Labels)", expanded=True):
            custom_title = st.text_input("自訂圖表主標題", "")
            title_fsize = st.slider("標題文字大小 (Title Font Size)", 10, 26, 14)
            
            c_lbl1, c_lbl2 = st.columns(2)
            custom_xlabel = c_lbl1.text_input("自訂 X 軸標籤", "")
            custom_ylabel = c_lbl2.text_input("自訂 Y 軸標籤", "")
            label_fsize = st.slider("軸標籤文字大小 (Label Font Size)", 8, 22, 12)
            
            c_tk1, c_tk2 = st.columns(2)
            tick_fsize = c_tk1.slider("刻度文字大小 (Tick Font Size)", 6, 20, 10)
            # Default rotation 30 if X is text to prevent overlap
            default_rot_idx = 1 if not is_current_x_numeric else 0
            tick_rot = c_tk2.selectbox("X 軸文字旋轉角度", [0, 30, 45, 90], index=default_rot_idx, help="若文字標籤較長，推薦選取 30° 或 45° 避免重疊")
            show_grid_opt = st.checkbox("顯示網格輔助線 (Grid)", value=True)

        with st.expander("📏 畫布尺寸與頂級期刊配色", expanded=False):
            palette_opt = st.selectbox("科學期刊調色盤 (Palette)", list(pb.PALETTES.keys()), index=0)
            fig_w = st.slider("畫布寬度 (Width)", 4.0, 16.0, 8.0, step=0.5)
            fig_h = st.slider("畫布高度 (Height)", 3.0, 12.0, 6.0, step=0.5)
            fig_dpi = st.select_slider("匯出解析度 (DPI)", options=[100, 150, 300, 600], value=300)

    # Right Column: Plot Rendering and Code Display
    with col_view:
        st.markdown("#### 🖼️ 即時渲染圖表 (Live Preview)")
        fig, generated_code = None, ""
        
        try:
            figsize = (fig_w, fig_h)
            xlim_param = (x_min, x_max) if x_custom_lim else None
            ylim_param = (y_min, y_max) if y_custom_lim else None

            if "Box / Violin" in plot_type:
                fig, generated_code = pb.create_group_distribution_plot(
                    df, px, py, phue, plot_type=pt_mode, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, title=custom_title,
                    xlabel=custom_xlabel, ylabel=custom_ylabel,
                    title_fontsize=title_fsize, label_fontsize=label_fsize,
                    xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                    tick_rotation=tick_rot, show_grid=show_grid_opt,
                    xlim=xlim_param, ylim=ylim_param,
                    xscale=x_scale_val, yscale=y_scale_val
                )
            elif "Survival Curve" in plot_type:
                fig, generated_code = pb.create_survival_plot(
                    df, ptime, pevt, pgrp, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, title=custom_title or "Kaplan-Meier Survival Analysis",
                    xlabel=custom_xlabel, ylabel=custom_ylabel,
                    title_fontsize=title_fsize, label_fontsize=label_fsize,
                    xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                    tick_rotation=tick_rot, show_grid=show_grid_opt,
                    xlim=xlim_param, ylim=ylim_param,
                    xscale=x_scale_val, yscale=y_scale_val,
                    show_ci=pci, show_median=pmed
                )
            elif "Volcano Plot" in plot_type:
                fig, generated_code = pb.create_volcano_plot(
                    df, pfc, ppval, pgene, fc_threshold=fc_th, pval_threshold=pval_th,
                    palette_name=palette_opt, figsize=figsize, dpi=fig_dpi,
                    title=custom_title or "Volcano Plot (Differential Expression)",
                    xlabel=custom_xlabel, ylabel=custom_ylabel,
                    title_fontsize=title_fsize, label_fontsize=label_fsize,
                    xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                    tick_rotation=tick_rot, show_grid=show_grid_opt,
                    xlim=xlim_param, ylim=ylim_param,
                    xscale=x_scale_val, yscale=y_scale_val
                )
            elif "Correlation Heatmap" in plot_type:
                if len(p_corr_cols) >= 2:
                    fig, generated_code = pb.create_correlation_heatmap(
                        df, p_corr_cols, method=p_corr_m, palette_name=palette_opt,
                        figsize=figsize, dpi=fig_dpi, annot=p_annot,
                        title=custom_title or "Correlation Heatmap",
                        title_fontsize=title_fsize,
                        xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                        tick_rotation=tick_rot if tick_rot != 0 else 45
                    )
                else:
                    st.warning("相關熱圖需要選取至少 2 個數值欄位。")
            elif "Scatter + OLS Fit" in plot_type:
                fig, generated_code = pb.create_scatter_regression_plot(
                    df, ps_x, ps_y, ps_hue, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, show_ci=ps_ci,
                    title=custom_title or f"{ps_y} vs {ps_x}",
                    xlabel=custom_xlabel, ylabel=custom_ylabel,
                    title_fontsize=title_fsize, label_fontsize=label_fsize,
                    xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                    tick_rotation=tick_rot, show_grid=show_grid_opt,
                    xlim=xlim_param, ylim=ylim_param,
                    xscale=x_scale_val, yscale=y_scale_val
                )
            elif "Bar + SEM/SD" in plot_type:
                err_param = "se" if "se" in pb_err else "sd"
                fig, generated_code = pb.create_bar_error_plot(
                    df, pb_x, pb_y, pb_hue, errorbar=err_param, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, title=custom_title or f"{pb_y} by {pb_x}",
                    xlabel=custom_xlabel, ylabel=custom_ylabel,
                    title_fontsize=title_fsize, label_fontsize=label_fsize,
                    xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                    tick_rotation=tick_rot, show_grid=show_grid_opt,
                    xlim=xlim_param, ylim=ylim_param,
                    xscale=x_scale_val, yscale=y_scale_val
                )
            elif "Histogram + KDE" in plot_type:
                fig, generated_code = pb.create_distribution_plot(
                    df, ph_col, ph_hue, bins=ph_bins, show_kde=ph_kde,
                    palette_name=palette_opt, figsize=figsize, dpi=fig_dpi,
                    title=custom_title or f"Distribution of {ph_col}",
                    xlabel=custom_xlabel, ylabel=custom_ylabel,
                    title_fontsize=title_fsize, label_fontsize=label_fsize,
                    xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                    tick_rotation=tick_rot, show_grid=show_grid_opt,
                    xlim=xlim_param, ylim=ylim_param,
                    xscale=x_scale_val, yscale=y_scale_val
                )
            elif "PCA Biplot" in plot_type:
                if len(pca_features) >= 2:
                    fig, generated_code = pb.create_pca_plot(
                        df, pca_features, pca_label, palette_name=palette_opt,
                        figsize=figsize, dpi=fig_dpi, title=custom_title or "PCA Projection",
                        xlabel=custom_xlabel, ylabel=custom_ylabel,
                        title_fontsize=title_fsize, label_fontsize=label_fsize,
                        xtick_fontsize=tick_fsize, ytick_fontsize=tick_fsize,
                        tick_rotation=tick_rot, show_grid=show_grid_opt,
                        xlim=xlim_param, ylim=ylim_param,
                        xscale=x_scale_val, yscale=y_scale_val
                    )
                else:
                    st.warning("PCA 降維投影需要至少 2 個數值變項。")
                    
            if fig is not None:
                st.pyplot(fig)
                
                # High Resolution & Vector Export
                d1, d2, d3, d4 = st.columns(4)
                png_bytes = pb.fig_to_bytes(fig, format='png', dpi=fig_dpi)
                svg_bytes = pb.fig_to_bytes(fig, format='svg', dpi=fig_dpi)
                pdf_bytes = pb.fig_to_bytes(fig, format='pdf', dpi=fig_dpi)
                
                d1.download_button("💾 下載 PNG (高畫質)", png_bytes, "biostat_plot.png", "image/png", use_container_width=True)
                d2.download_button("📐 下載 SVG (向量格式)", svg_bytes, "biostat_plot.svg", "image/svg+xml", use_container_width=True)
                d3.download_button("📄 下載 PDF (出版規格)", pdf_bytes, "biostat_plot.pdf", "application/pdf", use_container_width=True)
                
                if d4.button("⚡ 傳送至 Code Lab 編輯", use_container_width=True):
                    st.session_state.active_code = generated_code
                    st.success("已成功載入程式碼至「4. 自訂代碼繪圖」分頁！")

                # Code Accordion
                with st.expander("查看此圖表的完整 Python 重現程式碼 (Reproducible Code)", expanded=False):
                    st.code(generated_code, language="python")
                    
        except Exception as e:
            st.error(f"繪圖生成失敗: {e}")

# ==============================================================================
# TAB 4: 自訂代碼繪圖 (Python Code Lab)
# ==============================================================================
with tab_code:
    st.subheader("💻 Python 自訂程式碼繪圖實驗室 (Interactive Code Lab)")
    st.markdown("""
    本環境直接掛載當前上傳數據集 `df`，並預載 `pd`, `np`, `plt`, `sns`, `stats`, `lifelines`。
    您可以**撰寫或微調任何 Python 支援的圖表**（如 3D 散佈圖、分群熱圖 Clustermap、Pairplot、FacetGrid 或特定軸線標註），即時點擊執行並匯出成果！
    """)
    
    col_preset, col_btn = st.columns([2, 1])
    with col_preset:
        preset_name = st.selectbox("💡 快速載入進階生醫圖表模板", ["-- 選擇模板代碼 --"] + list(cs.CODE_TEMPLATES.keys()))
        if preset_name != "-- 選擇模板代碼 --":
            if st.button("套用所選模板至編輯區"):
                st.session_state.active_code = cs.CODE_TEMPLATES[preset_name]
                st.rerun()
                
    initial_code = st.session_state.active_code if st.session_state.active_code else cs.CODE_TEMPLATES["Seaborn Clustermap (層級分群熱圖)"]
    user_code = st.text_area("Python 繪圖程式碼編輯區", value=initial_code, height=280)
    
    if st.button("🚀 執行程式碼並繪圖 (Execute Code)", type="primary"):
        st.session_state.active_code = user_code
        with st.spinner("正在執行 Python 繪圖腳本..."):
            custom_fig, console_out, err_msg = cs.execute_user_plot_code(user_code, df)
            
            if err_msg:
                st.error("執行程式碼時發生例外錯誤：")
                st.code(err_msg, language="python")
            else:
                if console_out:
                    st.markdown("##### 🖥️ 標準輸出 (Stdout)")
                    st.text(console_out)
                    
                if custom_fig is not None:
                    st.markdown("##### 🖼️ 執行繪圖成果")
                    st.pyplot(custom_fig)
                    
                    c1, c2 = st.columns(2)
                    c_png = pb.fig_to_bytes(custom_fig, 'png', dpi=300)
                    c_pdf = pb.fig_to_bytes(custom_fig, 'pdf', dpi=300)
                    c1.download_button("💾 下載自訂圖表 (PNG 300 DPI)", c_png, "custom_plot.png", "image/png", use_container_width=True)
                    c2.download_button("📄 下載自訂圖表 (PDF 格式)", c_pdf, "custom_plot.pdf", "application/pdf", use_container_width=True)
                else:
                    st.warning("程式執行完成，但未偵測到生成的 matplotlib Figure。請確認腳本有使用 `plt.plot()` 或將圖表存入 `fig` 變數。")

# ==============================================================================
# TAB 5: 匯出與 GitHub 發佈 (Export & GitHub)
# ==============================================================================
with tab_export:
    st.subheader("🛰️ MISSION CONTROL // 數據匯出與 GITHUB 遠端控制")
    
    col_ex1, col_ex2 = st.columns(2)
    
    with col_ex1:
        st.markdown("#### 1. 數據矩陣全量匯出 (DATA EXPORT)")
        st.write("下載當前經由 Super Xstat 解析與校正之完整資料集：")
        
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Super_Xstat_Data')
        excel_buf.seek(0)
        
        st.download_button(
            "📥 下載處理後數據 (Excel .xlsx)",
            excel_buf.getvalue(),
            f"super_xstat_{st.session_state.df_name or 'matrix.xlsx'}",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_ex2:
        st.markdown("#### 2. 本地終端機快速啟動")
        st.code("""# 於專案目錄執行啟動 Super Xstat 本地伺服器：
streamlit run app.py
""", language="bash")

    st.markdown("---")
    st.markdown("#### 3. 🚀 GITHUB TELEMETRY // 遠端推送同步")
    st.markdown("""
    本專案已綁定遠端 GitHub 儲存庫 **[https://github.com/jessechan27/biostat-studio.git](https://github.com/jessechan27/biostat-studio.git)**。
    執行以下指令即可將最新黑科技版 Super Xstat 同步至雲端：
    """)
    
    st.code("""git add .
git commit -m "feat: transform frontend into Super Xstat Tesla/SpaceX dark tech style"
git push origin main
""", language="bash")
    
    st.info("💡 **一鍵免費雲端上線 (Streamlit Cloud)**：前往 share.streamlit.io 點擊 'Deploy an app'，連結 `jessechan27/biostat-studio` 與 `app.py`，即可將 Super Xstat 部署為全球可存取的頂級黑科技雲端網站！")
