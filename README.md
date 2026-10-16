# 🧬 BioStat Studio | 生醫統計分析與客製化繪圖平台

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Seaborn](https://img.shields.io/badge/Visualization-Seaborn%20%7C%20Matplotlib-388E3C.svg)](https://seaborn.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **專為生物醫學研究人員、臨床醫師與生物資訊學家打造的統計決策引導、完整醫學報告與出版級繪圖工作站。**  
> 支援一鍵上傳 Excel/CSV 檔案，提供「智慧統計方法推薦精靈」引導正確選擇統計檢定，自動生成符合國際期刊規範的結構化分析報告；圖表支援完整 X/Y 軸尺度（線性/對數/範圍限制）與全方位文字大小調整！

---

## 🌟 核心特色功能 (Key Features)

### 1. 🎯 智慧統計方法推薦決策精靈 (Statistical Method Advisor)
- **避免生醫統計誤用**：根據研究設計（獨立組別、前後測配對、多因子、二元疾病預後、存活時間追蹤）動態提供決策指引。
- **前提假設嚴格把關**：
  - **常態性檢定** (Shapiro-Wilk) ➔ 判定母數 vs 無母數檢定。
  - **變異數齊一性** (Levene's test) ➔ 判定 Student's t vs Welch's t (自由度修正)。
  - **列聯表期望頻次診斷** ➔ 期望頻次 < 5 時主動警示並推薦 Fisher's Exact Test。
  - **交互作用診斷** ➔ 雙因子變異數分析檢測因子間是否存在統計學交互作用。

### 2. 🧪 專業生醫統計檢定全套工具庫 (11 大統計方法)
1. **常態性與敘述統計**：Mean, SD, SEM, Median, IQR, 偏度, 峰度與 **Shapiro-Wilk 常態性檢定**。
2. **兩組獨立樣本差異檢定**：Student's t、Welch's t、Mann-Whitney U 檢定與 Cohen's d 效果值。
3. **配對樣本前後測檢定 (Paired Samples)**：Paired t-test、Wilcoxon Signed-Rank 符號等級檢定、前後測差值 CI 與配對效果量 Cohen's dz。
4. **多組單因子變異數分析 (One-Way ANOVA)**：ANOVA F 檢定、非參數 Kruskal-Wallis 檢定及 Tukey HSD 事後兩兩比較。
5. **雙因子變異數分析 (Two-Way ANOVA)**：因子 A、因子 B 主效應與 A × B 交互作用檢定。
6. **類別變項分析**：交叉列聯表 (Contingency Table)、Chi-Square 卡方檢定、Fisher's Exact 費雪精確檢定與勝算比 (Odds Ratio)。
7. **相關性矩陣**：Pearson、Spearman、Kendall 相關係數矩陣與雙尾顯著性檢定。
8. **存活分析 (Survival Analysis)**：Kaplan-Meier 累積存活率估計、中位存活時間與 Log-Rank 組間差異檢定。
9. **Cox 比例風險模型 (Cox PH)**：多變項存活迴歸、危險比 (Hazard Ratio, HR)、95% 信賴區間與 C-index 模型鑑別度。
10. **二元邏輯斯迴歸 (Logistic Regression)**：二元臨床預後模型、勝算比 (Odds Ratio, OR)、McFadden's Pseudo-R²。
11. **多元線性迴歸 (Linear Regression OLS)**：多變量 OLS 模型擬合、係數顯著性與 95% 信賴區間。

### 3. 📄 完整生醫統計分析報告產生器 (Structured Clinical Reports)
- 自動產出符合國際醫學期刊（APA / ICMJE / NEJM）格式之結構化分析報告：
  - **研究假說與檢定設計**
  - **前提假設與診斷檢定**（常態性 p 值、齊一性判定）
  - **統計量與效果值結果表**
  - **醫學期刊規範結論解讀 (Narrative Conclusion)**
- 支援一鍵下載完整 Markdown 格式報告或複製至論文方法學/結果章節。

### 4. 🎨 出版級圖表工坊 (全自訂 X/Y 尺度與字級)
- **多種生醫專用圖表**：
  - 箱形圖 / 小提琴圖 + 抖動散佈 (Box / Violin + Jitter Strip)
  - Kaplan-Meier 生存曲線 (含 95% CI 陰影與中位存活線)
  - 基因差異表現火山圖 (Volcano Plot)
  - 相關係數熱圖 (Correlation Heatmap)
  - 散佈圖與線性迴歸擬合 (Scatter + OLS + CI)
  - 均值與誤差條柱狀圖 (Bar + SEM / SD)
  - 機率分佈與核密度圖 (Histogram + KDE)
  - 主成分分析投影圖 (PCA Biplot)
- **全新深度座標軸客製化控制**：
  - **X/Y 軸尺度自由切換**：線性尺度 (Linear) 或 對數尺度 (Log10)。
  - **X/Y 軸數值範圍自訂**：自訂最小值 (Min) 與 最大值 (Max) 放大檢視特徵區間。
  - **全方位文字大小調整**：主標題大小 (10~26 pt)、軸標籤大小 (8~22 pt)、座標刻度文字大小 (6~20 pt)。
  - **刻度標籤旋轉角度**：0°、30°、45°、90° 解決標籤重疊。
  - **頂級期刊配色**：`Nature (NPG)`, `Lancet`, `NEJM`, `JAMA`, `Viridis` 等。
  - **出版級匯出**：一鍵下載 **300/600 DPI 高解析度 PNG**、**向量格式 SVG** 或 **印刷級 PDF**。

### 5. 💻 Python 自訂代碼繪圖實驗室 (Interactive Code Lab)
- 直接在線上 Python 編輯器中對已載入的 `df` 進行任何 Matplotlib / Seaborn 自由繪圖。
- 內建進階生醫模板：層級分群熱圖 (Clustermap)、Pairplot、FacetGrid、Lollipop Chart、3D 散佈圖。

---

## 🚀 快速安裝與本地啟動 (Quick Start)

```bash
# 1. 複製專案庫
git clone https://github.com/jessechan27/biostat-studio.git
cd biostat-studio

# 2. 建立虛擬環境
python -m venv venv
venv\Scripts\activate

# 3. 安裝必要套件
pip install -r requirements.txt

# 4. 啟動 Web 服務
streamlit run app.py
```
瀏覽器將自動開啟 `http://localhost:8501`。

---

## 📜 授權協議 (License)

本專案採用 [MIT License](LICENSE) 開源授權，歡迎學術研究、臨床機構及個人自由使用與二次開發。
