# 🧬 BioStat Studio | 生醫統計分析與客製化繪圖平台

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Seaborn](https://img.shields.io/badge/Visualization-Seaborn%20%7C%20Matplotlib-388E3C.svg)](https://seaborn.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **專為生物醫學研究人員、臨床醫師與生物資訊學家打造的無代碼 / 低代碼統計分析與出版級繪圖工作站。**  
> 支援一鍵上傳 Excel/CSV 檔案，自動完成多群組假說檢定、存活分析與差異表現分析，並可自由微調或直接以 Python 撰寫任何進階視覺化圖表！

---

## 🌟 核心特色功能 (Key Features)

### 1. 📁 智慧數據匯入與剖析 (Data Hub)
- **多格式支援**：支援 `.xlsx`、`.xls`、`.csv`，多工作表 (Sheets) 即時切換選取。
- **自動特徵識別**：自動分類數值型、類別型、時間型與文字標籤欄位。
- **品質診斷**：缺失值比例、異常值預警與樣本分佈快速預覽。
- **內建示範數據**：內建臨床試驗隊列、癌症存活追蹤、基因差異表現三大生醫標準數據集。

### 2. 🧪 專業生醫統計檢定引擎 (Biostat Analysis)
- **常態性與敘述統計**：Mean, SD, SEM, Median, IQR, 偏度, 峰度與 **Shapiro-Wilk 常態性檢定**。
- **兩組差異檢定**：自動評估常態性與變異數齊一性（Levene's test），提供 Student's t、Welch's t、Mann-Whitney U 檢定與 Cohen's d 效果值。
- **多組比較**：單因子變異數分析 (One-way ANOVA)、非參數 Kruskal-Wallis 檢定及 Tukey HSD 事後兩兩比較。
- **類別變項分析**：交叉列聯表 (Contingency Table)、Chi-Square 卡方檢定、Fisher's Exact 費雪精確檢定與勝算比 (Odds Ratio)。
- **相關性矩陣**：Pearson 與 Spearman 相關係數熱度圖與雙尾 p-value 顯著性矩陣。
- **存活分析 (Survival Analysis)**：Kaplan-Meier 累積存活率估計、中位存活時間與 Log-Rank 組間差異檢定。
- **線性迴歸 (Linear Regression)**：多元 OLS 模型擬合、係數顯著性與 95% 信賴區間。

### 3. 🎨 出版級圖表工坊 (Plot Studio)
- **多種生醫專用圖表**：
  - 箱形圖 / 小提琴圖 + 抖動散佈 (Box / Violin + Jitter Strip)
  - Kaplan-Meier 生存曲線 (含 95% CI 陰影與中位存活線)
  - 基因差異表現火山圖 (Volcano Plot，支援閾值標線與頂端顯著基因標註)
  - 相關係數熱圖 (Correlation Heatmap)
  - 散佈圖與線性迴歸擬合 (Scatter + OLS + CI)
  - 均值與誤差條柱狀圖 (Bar + SEM / SD)
  - 機率分佈與核密度圖 (Histogram + KDE)
  - 主成分分析投影圖 (PCA Biplot)
- **頂級視覺客製化**：
  - 內建權威頂級期刊配色：`Nature (NPG)`, `Lancet`, `NEJM`, `JAMA`, `Viridis` 等。
  - 支援畫布大小、字體等級、刻度旋轉與格線自訂。
  - **出版級匯出**：一鍵下載 **300/600 DPI 高解析度 PNG**、**向量格式 SVG** 或 **印刷級 PDF**。
- **重現性程式碼檢視**：每次圖表產出皆自動附帶完整的 Python 腳本，方便放入論文方法學或 Jupyter Notebook 重現。

### 4. 💻 Python 自訂程式碼繪圖實驗室 (Interactive Code Lab)
- **無限自由度**：滿足「利用 Seaborn 及 Matplotlib 做出任何 Python 能做出的圖」的需求！
- 預載當前上傳的 `df`，並引入 `pd`, `np`, `plt`, `sns`, `stats`, `lifelines`。
- **內建進階生醫模板**：
  - 層級分群熱圖 (Hierarchical Clustermap)
  - 多變量矩陣圖 (Seaborn PairGrid / Pairplot)
  - 多分面小提琴圖 (FacetGrid)
  - 均值排序棒棒糖圖 (Lollipop Chart)
  - 3D 空間散佈圖 (3D Scatter Plot)
- 支援線上編輯、即時渲染與成果匯出。

---

## 🚀 快速安裝與本地啟動 (Quick Start)

### 1. 複製專案庫
```bash
git clone https://github.com/<your-username>/biostat-studio.git
cd biostat-studio
```

### 2. 建立並啟動虛擬環境 (建議)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate
```

### 3. 安裝必要相依套件
```bash
pip install -r requirements.txt
```

### 4. 啟動 Web 應用
```bash
streamlit run app.py
```
瀏覽器將自動開啟 `http://localhost:8501`。

---

## 📂 專案檔案結構 (Project Structure)

```text
├── app.py                     # Streamlit 主應用程式與前端使用者介面
├── requirements.txt           # 專案相依 Python 套件清單
├── .gitignore                 # Git 忽略檔案設定
├── .streamlit/
│   └── config.toml            # Streamlit 主題樣式與 250MB 檔案上傳設定
├── modules/
│   ├── __init__.py
│   ├── data_manager.py        # 檔案載入、多工作表讀取、欄位特徵分類與清洗
│   ├── biostats.py            # 統計推論核心 (t檢定、ANOVA、卡方、存活分析、迴歸)
│   ├── plot_builder.py        # 出版級 Matplotlib/Seaborn 繪圖與客製化引擎
│   └── code_sandbox.py        # 自訂代碼執行環境與進階模板
├── sample_data/               # 內建生醫示範 Excel 數據集
│   ├── clinical_trial_data.xlsx
│   ├── cancer_survival_data.xlsx
│   └── gene_expression_volcano.xlsx
└── generate_sample_data.py    # 範例數據生成腳本
```

---

## 🌐 部署至免費雲端 (Deploy to Cloud)

本專案完全相容於 **[Streamlit Community Cloud](https://share.streamlit.io/)**：
1. 將程式碼推送到您的 GitHub 儲存庫。
2. 登入 Streamlit Cloud 並點擊 **"New app"**。
3. 選取您的 GitHub 儲存庫、分支（`main`）以及主程式路徑（`app.py`）。
4. 點擊 **"Deploy!"**，幾秒鐘內即可獲得專屬的免費線上生醫分析網站！

---

## 📜 授權協議 (License)

本專案採用 [MIT License](LICENSE) 開源授權，歡迎學術研究、臨床機構及個人自由使用與二次開發。
