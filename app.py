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
    page_title="BioStat Studio | 生醫統計分析與客製化繪圖平台",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished scientific styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 50%, #0D9488 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 6px 6px 0 0;
        padding: 0 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: white !important;
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
    st.image("https://img.shields.io/badge/BioStat_Studio-v1.0.0-blue?style=for-the-badge&logo=python", use_container_width=True)
    st.header("📂 數據匯入中心")
    
    data_source = st.radio("資料來源", ["上傳自己的 Excel / CSV", "載入生醫範例資料庫"], index=1)
    
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
                st.success(f"成功載入: {df_name}")
            except Exception as e:
                st.error(f"讀取失敗: {e}")
    else:
        sample_options = {
            "臨床試驗隊列 (Clinical Trial Cohort)": "sample_data/clinical_trial_data.xlsx",
            "癌症存活追蹤數據 (Cancer Survival)": "sample_data/cancer_survival_data.xlsx",
            "基因差異表現 (Gene Expression Volcano)": "sample_data/gene_expression_volcano.xlsx"
        }
        selected_sample = st.selectbox("選擇生醫示範數據", list(sample_options.keys()))
        sample_path = sample_options[selected_sample]
        if os.path.exists(sample_path):
            df_name = os.path.basename(sample_path)
            uploaded_df = pd.read_excel(sample_path)
            st.info(f"已啟用範例數據集：`{selected_sample}`")
        else:
            st.warning("範例檔案建構中...")

    if uploaded_df is not None:
        st.session_state.df = uploaded_df
        st.session_state.df_name = df_name

    st.markdown("---")
    st.markdown("### 🛠️ 支援核心工具")
    st.caption("• **Seaborn & Matplotlib** 出版級繪圖\n• **SciPy & Statsmodels** 生統檢定\n• **Lifelines** Kaplan-Meier 存活分析\n• 300/600 DPI 高解析 & 向量 SVG/PDF 匯出")

# Main Header
st.markdown('<div class="main-header">🧬 BioStat Studio 生物統計分析與客製化繪圖平台</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">整合 Excel 數據剖析、醫學統計推論檢定、出版級 Seaborn/Matplotlib 視覺化與 Python 即時繪圖實驗室</div>', unsafe_allow_html=True)

# Main Navigation Tabs
tab_data, tab_stats, tab_plots, tab_code, tab_export = st.tabs([
    "📁 1. 數據管理 (Data Hub)",
    "🧪 2. 生物統計分析 (Biostats)",
    "🎨 3. 視覺化圖表工坊 (Plot Studio)",
    "💻 4. 自訂代碼繪圖 (Python Code Lab)",
    "📦 5. 匯出與 GitHub 發佈 (Export & GitHub)"
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
# TAB 2: 生物統計分析 (Biostats)
# ==============================================================================
with tab_stats:
    st.subheader("🧪 生物統計分析與假設檢定")
    stat_task = st.selectbox("選擇統計分析項目", [
        "1. 敘述性統計與常態性檢定 (Descriptive Statistics & Shapiro-Wilk)",
        "2. 兩組獨立樣本差異檢定 (Two-Group: Student's t / Welch's t / Mann-Whitney U)",
        "3. 多組單因子變異數分析 (Multi-Group: One-way ANOVA & Kruskal-Wallis)",
        "4. 類別變項交叉列聯表 (Contingency: Chi-square / Fisher's Exact / OR)",
        "5. 相關係數分析矩陣 (Correlation Matrix: Pearson / Spearman)",
        "6. Kaplan-Meier 存活分析與 Log-Rank 檢定 (Survival Analysis)",
        "7. 多元線性迴歸分析 (Linear Regression OLS)"
    ])
    
    st.markdown("---")
    
    # 1. 敘述統計
    if "1. 敘述性統計" in stat_task:
        st.markdown("##### 📌 數值變項敘述性統計 (Mean, SD, Median, IQR, Shapiro-Wilk 常態性檢定)")
        selected_num_cols = st.multiselect("選取要分析的數值欄位", numeric_cols, default=numeric_cols[:min(5, len(numeric_cols))])
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
        st.markdown("##### 📌 兩組差異檢定 (自動 Levene 齊一性檢定、t-test、Mann-Whitney U 與 Cohen's d)")
        c1, c2, c3 = st.columns(3)
        with c1:
            val_col = st.selectbox("分析數值變項 (Y)", numeric_cols)
        with c2:
            two_group_candidates = [c for c in categorical_cols if df[c].dropna().nunique() == 2]
            fallback_cats = categorical_cols if categorical_cols else all_cols
            grp_col = st.selectbox("分組變項 (恰好 2 組)", two_group_candidates if two_group_candidates else fallback_cats)
        with c3:
            method_choice = st.selectbox("指定檢定方法", ["auto", "student_t", "welch_t", "mann_whitney"])
            
        if st.button("🚀 執行兩組檢定", type="primary"):
            try:
                res = bs.two_group_comparison(df, val_col, grp_col, method_choice)
                
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("檢定方法", res['檢定方法'])
                c_b.metric("檢定統計量", f"{res['統計量']:.4f}")
                p_disp = f"{res['p值']:.4e}" if res['p值'] < 0.001 else f"{res['p值']:.4f}"
                c_c.metric("p 值 (顯著性)", p_disp, delta="顯著 (p<0.05)" if res['顯著性 (p < 0.05)'] else "未達顯著", delta_color="normal" if res['顯著性 (p < 0.05)'] else "inverse")
                
                st.markdown("##### 📊 組別平均值與統計指標比較")
                comp_table = pd.DataFrame([
                    {"組別": res['組別 1 名稱'], "樣本數 N": res['組別 1 樣本數'], "Mean ± SD": f"{res['組別 1 平均值']} ± {res['組別 1 標準差']}", "Median (IQR)": f"{res['組別 1 中位數']} ({res['組別 1 IQR']})"},
                    {"組別": res['組別 2 名稱'], "樣本數 N": res['組別 2 樣本數'], "Mean ± SD": f"{res['組別 2 平均值']} ± {res['組別 2 標準差']}", "Median (IQR)": f"{res['組別 2 中位數']} ({res['組別 2 IQR']})"}
                ])
                st.table(comp_table)
                
                st.markdown(f"""
                - **平均差異 (95% CI)**: `{res['平均差值']} [{res['95% 信賴區間下限']}, {res['95% 信賴區間上限']}]`
                - **效果值 (Cohen's d)**: `{res['Cohen d 效果值']}`
                - **變異數齊一性 (Levene's p)**: `{res['Levene 檢定 p值']}` ({'齊一' if res['變異數齊一'] else '不齊一'})
                """)
            except Exception as e:
                st.error(f"檢定過程出錯: {e}")

    # 3. 多組 ANOVA
    elif "3. 多組單因子" in stat_task:
        st.markdown("##### 📌 多組比較 (One-way ANOVA、Kruskal-Wallis 與 Tukey HSD 事後多重比較)")
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
                
                st.markdown(f"**非參數 Kruskal-Wallis H**: `{res['Kruskal-Wallis H 值']:.4f}` (p = `{res['Kruskal-Wallis p 值']:.4e}`)")
                
                if res['Tukey HSD 事後檢定'] is not None and not res['Tukey HSD 事後檢定'].empty:
                    st.markdown("##### 🔍 Tukey HSD 事後兩兩檢定 (Pairwise Comparisons)")
                    st.dataframe(res['Tukey HSD 事後檢定'], use_container_width=True)
            except Exception as e:
                st.error(f"分析失敗: {e}")

    # 4. 列聯表卡方
    elif "4. 類別變項" in stat_task:
        st.markdown("##### 📌 列聯表與卡方檢定 (Chi-square / Fisher's Exact / OR)")
        c1, c2 = st.columns(2)
        with c1:
            r_col = st.selectbox("橫列變項 (Row Variable)", categorical_cols if categorical_cols else all_cols, key="chi_row")
        with c2:
            c_col = st.selectbox("直欄變項 (Column Variable)", [c for c in (categorical_cols if categorical_cols else all_cols) if c != r_col], key="chi_col")
            
        if st.button("🚀 執行卡方檢定", type="primary"):
            try:
                res = bs.contingency_analysis(df, r_col, c_col)
                st.markdown("##### 📊 交叉次數列聯表 (Observed Frequencies)")
                st.dataframe(res['觀察頻次列聯表'], use_container_width=True)
                
                ca, cb, cc = st.columns(3)
                ca.metric("卡方值 (Chi-Square)", f"{res['卡方統計量']:.4f}")
                cb.metric("自由度 (df)", res['自由度'])
                p_txt = f"{res['卡方 p 值']:.4e}" if res['卡方 p 值'] < 0.001 else f"{res['卡方 p 值']:.4f}"
                cc.metric("卡方 p 值", p_txt, delta="關聯顯著 (p<0.05)" if res['顯著性 (p < 0.05)'] else "無顯著關聯")
                
                if res.get('Fisher Exact p 值') is not None:
                    st.info(f"💡 2x2 列聯表費雪精確檢定 (Fisher's Exact p): `{res['Fisher Exact p 值']:.4e}` | 勝算比 (Odds Ratio): `{res['Odds Ratio']}`")
            except Exception as e:
                st.error(f"檢定出錯: {e}")

    # 5. 相關矩陣
    elif "5. 相關係數" in stat_task:
        st.markdown("##### 📌 相關分析 (Pearson / Spearman 矩陣與雙尾 p-value)")
        c1, c2 = st.columns([1, 3])
        with c1:
            corr_m = st.radio("相關係數類型", ["pearson", "spearman"])
        with c2:
            corr_cols = st.multiselect("選取相關分析欄位", numeric_cols, default=numeric_cols[:min(6, len(numeric_cols))])
            
        if len(corr_cols) >= 2:
            r_df, p_df, n_df = bs.correlation_matrix(df, corr_cols, corr_m)
            st.markdown("##### 相關係數矩陣 (r)")
            st.dataframe(r_df.style.background_gradient(cmap='coolwarm', vmin=-1, vmax=1).format("{:.3f}"), use_container_width=True)
            st.markdown("##### 雙尾檢定 p 值矩陣")
            st.dataframe(p_df.style.format("{:.4e}"), use_container_width=True)
        else:
            st.warning("請選取至少 2 個數值欄位。")

    # 6. 生存分析
    elif "6. Kaplan-Meier" in stat_task:
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

    # 7. 線性迴歸
    elif "7. 多元線性迴歸" in stat_task:
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
    st.subheader("🎨 出版級生醫視覺化圖表工坊")
    
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
        # Dynamic variable selectors
        if "Box / Violin" in plot_type:
            pt_mode = st.radio("繪製子型態", ["Boxplot + Jitter", "Violin Plot", "Strip Plot Only"], horizontal=True)
            px = st.selectbox("X 軸 (分組類別)", categorical_cols if categorical_cols else all_cols)
            py = st.selectbox("Y 軸 (分析數值)", numeric_cols)
            phue = st.selectbox("次分組 (Hue, 選填)", [None] + categorical_cols)
        elif "Survival Curve" in plot_type:
            ptime = st.selectbox("時間變項 (Time)", numeric_cols, key="plot_surv_time")
            pevt = st.selectbox("事件變項 (Event: 1=發生, 0=設限)", numeric_cols if numeric_cols else all_cols, key="plot_surv_evt")
            pgrp = st.selectbox("分組變項 (選填)", [None] + categorical_cols, key="plot_surv_grp")
            pci = st.checkbox("顯示 95% 信賴區間", value=True)
            pmed = st.checkbox("標註中位存活時間虛線", value=True)
        elif "Volcano Plot" in plot_type:
            pfc = st.selectbox("Log2 Fold Change 欄位", numeric_cols, index=0)
            ppval = st.selectbox("P-value 欄位", [c for c in numeric_cols if c != pfc], index=0)
            gene_candidates = [c for c in all_cols if c not in [pfc, ppval]]
            pgene = st.selectbox("基因/特徵標籤欄位 (選填)", [None] + gene_candidates)
            fc_th = st.number_input("Log2 FC 顯著閾值", value=1.0, step=0.1)
            pval_th = st.number_input("P-value 顯著閾值", value=0.05, step=0.01)
        elif "Correlation Heatmap" in plot_type:
            p_corr_cols = st.multiselect("選取熱圖欄位 (≥2)", numeric_cols, default=numeric_cols[:min(7, len(numeric_cols))])
            p_corr_m = st.selectbox("相關方法", ["pearson", "spearman"])
            p_annot = st.checkbox("標註相關係數數值", value=True)
        elif "Scatter + OLS Fit" in plot_type:
            ps_x = st.selectbox("X 軸數值欄位", numeric_cols, index=0)
            ps_y = st.selectbox("Y 軸數值欄位", [c for c in numeric_cols if c != ps_x], index=0)
            ps_hue = st.selectbox("顏色分類 (Hue, 選填)", [None] + categorical_cols)
            ps_ci = st.checkbox("顯示 95% 迴歸信賴區間", value=True)
        elif "Bar + SEM/SD" in plot_type:
            pb_x = st.selectbox("X 軸 (類別)", categorical_cols if categorical_cols else all_cols)
            pb_y = st.selectbox("Y 軸 (數值)", numeric_cols)
            pb_hue = st.selectbox("次分組 (Hue, 選填)", [None] + categorical_cols)
            pb_err = st.radio("誤差條類型", ["se (標準誤 SEM)", "sd (標準差 SD)"])
        elif "Histogram + KDE" in plot_type:
            ph_col = st.selectbox("數值欄位", numeric_cols)
            ph_hue = st.selectbox("分組疊加 (Hue, 選填)", [None] + categorical_cols)
            ph_bins = st.slider("組數 (Bins)", 10, 60, 25)
            ph_kde = st.checkbox("顯示核密度估計 (KDE 曲線)", value=True)
        elif "PCA Biplot" in plot_type:
            pca_features = st.multiselect("選取 PCA 特徵欄位 (≥2)", numeric_cols, default=numeric_cols[:min(8, len(numeric_cols))])
            pca_label = st.selectbox("標籤著色欄位 (選填)", [None] + categorical_cols)

        st.markdown("#### 3. 🎨 視覺美學客製化")
        with st.expander("展開圖表版面與調色設定", expanded=True):
            palette_opt = st.selectbox("科學期刊調色盤 (Palette)", list(pb.PALETTES.keys()), index=0)
            fig_w = st.slider("畫布寬度 (Width)", 4.0, 16.0, 8.0, step=0.5)
            fig_h = st.slider("畫布高度 (Height)", 3.0, 12.0, 6.0, step=0.5)
            fig_dpi = st.select_slider("匯出解析度 (DPI)", options=[100, 150, 300, 600], value=300)
            custom_title = st.text_input("自訂圖表主標題 (選填)", "")
            custom_xlabel = st.text_input("自訂 X 軸標籤 (選填)", "")
            custom_ylabel = st.text_input("自訂 Y 軸標籤 (選填)", "")

    # Right Column: Plot Rendering and Code Display
    with col_view:
        st.markdown("#### 🖼️ 即時渲染圖表 (Live Preview)")
        fig, generated_code = None, ""
        
        try:
            figsize = (fig_w, fig_h)
            if "Box / Violin" in plot_type:
                fig, generated_code = pb.create_group_distribution_plot(
                    df, px, py, phue, plot_type=pt_mode, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, title=custom_title,
                    xlabel=custom_xlabel, ylabel=custom_ylabel
                )
            elif "Survival Curve" in plot_type:
                fig, generated_code = pb.create_survival_plot(
                    df, ptime, pevt, pgrp, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, title=custom_title or "Kaplan-Meier Survival Analysis",
                    show_ci=pci, show_median=pmed
                )
            elif "Volcano Plot" in plot_type:
                fig, generated_code = pb.create_volcano_plot(
                    df, pfc, ppval, pgene, fc_threshold=fc_th, pval_threshold=pval_th,
                    palette_name=palette_opt, figsize=figsize, dpi=fig_dpi,
                    title=custom_title or "Volcano Plot (Differential Expression)"
                )
            elif "Correlation Heatmap" in plot_type:
                if len(p_corr_cols) >= 2:
                    fig, generated_code = pb.create_correlation_heatmap(
                        df, p_corr_cols, method=p_corr_m, palette_name=palette_opt,
                        figsize=figsize, dpi=fig_dpi, annot=p_annot,
                        title=custom_title or "Correlation Heatmap"
                    )
                else:
                    st.warning("相關熱圖需要選取至少 2 個數值欄位。")
            elif "Scatter + OLS Fit" in plot_type:
                fig, generated_code = pb.create_scatter_regression_plot(
                    df, ps_x, ps_y, ps_hue, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, show_ci=ps_ci,
                    title=custom_title or f"{ps_y} vs {ps_x}"
                )
            elif "Bar + SEM/SD" in plot_type:
                err_param = "se" if "se" in pb_err else "sd"
                fig, generated_code = pb.create_bar_error_plot(
                    df, pb_x, pb_y, pb_hue, errorbar=err_param, palette_name=palette_opt,
                    figsize=figsize, dpi=fig_dpi, title=custom_title or f"{pb_y} by {pb_x}"
                )
            elif "Histogram + KDE" in plot_type:
                fig, generated_code = pb.create_distribution_plot(
                    df, ph_col, ph_hue, bins=ph_bins, show_kde=ph_kde,
                    palette_name=palette_opt, figsize=figsize, dpi=fig_dpi,
                    title=custom_title or f"Distribution of {ph_col}"
                )
            elif "PCA Biplot" in plot_type:
                if len(pca_features) >= 2:
                    fig, generated_code = pb.create_pca_plot(
                        df, pca_features, pca_label, palette_name=palette_opt,
                        figsize=figsize, dpi=fig_dpi, title=custom_title or "PCA Projection"
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
    st.subheader("📦 專案匯出與 GitHub 開源發佈指南")
    
    col_ex1, col_ex2 = st.columns(2)
    
    with col_ex1:
        st.markdown("#### 1. 數據與清洗結果匯出")
        st.write("您可以下載當前已載入並整理完畢的資料集：")
        
        # Buffer to excel
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='BioStat_Data')
        excel_buf.seek(0)
        
        st.download_button(
            "📥 下載處理後數據 (Excel .xlsx)",
            excel_buf.getvalue(),
            f"processed_{st.session_state.df_name or 'biostat_data.xlsx'}",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_ex2:
        st.markdown("#### 2. 本地啟動與開發")
        st.code("""# 在終端機執行此命令即可本地啟動此網站：
streamlit run app.py
""", language="bash")

    st.markdown("---")
    st.markdown("#### 3. 🚀 發佈至 GitHub Repository 步驟指南")
    st.markdown("""
    在您當前專案資料夾 (`c:\\Users\\james\\Downloads\\test2`)，執行以下 Git 命令即可推送到您的 GitHub 儲存庫：
    """)
    
    st.code("""# 1. 初始化 Git 倉庫
git init

# 2. 將所有檔案加入暫存區
git add .

# 3. 提交首次版本
git commit -m "feat: initial commit of BioStat Studio web app"

# 4. 建立 main 分支
git branch -M main

# 5. 連接您的遠端 GitHub 倉庫 (請將 <your-username>/<repo-name> 換成您的 GitHub 專案網址)
git remote add origin https://github.com/<your-username>/<repo-name>.git

# 6. 推送至 GitHub
git push -u origin main
""", language="bash")
    
    st.info("💡 **免費雲端部署建議**：上傳至 GitHub 後，您可以直接前往 [Streamlit Community Cloud](https://share.streamlit.io/) 點擊 'Deploy an app'，選取您的 GitHub 儲存庫與 `app.py`，即可一鍵免費獲得全公開的生醫統計分析雲端網站！")
