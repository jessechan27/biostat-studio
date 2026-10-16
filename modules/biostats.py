import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from typing import Dict, Any, List, Optional, Tuple

# ==============================================================================
# 1. 敘述性統計與常態性檢定
# ==============================================================================
def calculate_descriptive_stats(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Calculate comprehensive biostatistical descriptive metrics for selected numeric columns."""
    records = []
    for col in columns:
        s = df[col].dropna()
        n = len(s)
        if n == 0:
            continue

        mean_val = float(s.mean())
        std_val = float(s.std(ddof=1)) if n > 1 else 0.0
        sem_val = float(std_val / np.sqrt(n)) if n > 0 else 0.0
        median_val = float(s.median())
        q25 = float(s.quantile(0.25))
        q75 = float(s.quantile(0.75))
        iqr_val = q75 - q25
        min_val = float(s.min())
        max_val = float(s.max())
        skew_val = float(s.skew()) if n > 2 else 0.0
        kurt_val = float(s.kurt()) if n > 3 else 0.0

        # Shapiro-Wilk Normality test (recommended for n <= 5000)
        norm_p = np.nan
        norm_verdict = "N/A"
        if 3 <= n <= 5000:
            try:
                stat, p = stats.shapiro(s)
                norm_p = p
                norm_verdict = "常態分佈 (p ≥ 0.05)" if p >= 0.05 else "非常態/偏態 (p < 0.05)"
            except Exception:
                pass

        records.append({
            '變項名稱': col,
            '樣本數 (N)': n,
            '平均值 (Mean)': round(mean_val, 3),
            '標準差 (SD)': round(std_val, 3),
            '標準誤 (SEM)': round(sem_val, 3),
            '中位數 (Median)': round(median_val, 3),
            '第一四分位數 (Q1)': round(q25, 3),
            '第三四分位數 (Q3)': round(q75, 3),
            '四分位距 (IQR)': round(iqr_val, 3),
            '極小值 (Min)': round(min_val, 3),
            '極大值 (Max)': round(max_val, 3),
            '偏度 (Skewness)': round(skew_val, 3),
            '峰度 (Kurtosis)': round(kurt_val, 3),
            '常態檢定 p 值': f"{norm_p:.4e}" if not np.isnan(norm_p) else "N/A",
            '分佈檢定結論': norm_verdict
        })

    return pd.DataFrame(records)

# ==============================================================================
# 2. 兩組獨立樣本比較 (Independent Two Groups)
# ==============================================================================
def two_group_comparison(df: pd.DataFrame, value_col: str, group_col: str, test_method: str = "auto") -> Dict[str, Any]:
    """Perform two-group hypothesis testing (Student's t, Welch's t, Mann-Whitney U) with full diagnostics."""
    sub_df = df[[value_col, group_col]].dropna()
    groups = sub_df[group_col].unique()

    if len(groups) != 2:
        raise ValueError(f"分組變項必須恰好有 2 個組別，目前偵測到 {len(groups)} 個組別：{list(groups)}")

    g1_label, g2_label = str(groups[0]), str(groups[1])
    g1_vals = sub_df[sub_df[group_col] == groups[0]][value_col].values
    g2_vals = sub_df[sub_df[group_col] == groups[1]][value_col].values

    n1, n2 = len(g1_vals), len(g2_vals)
    if n1 < 2 or n2 < 2:
        raise ValueError("兩組樣本數皆須至少為 2 筆數據。")

    m1, s1 = float(np.mean(g1_vals)), float(np.std(g1_vals, ddof=1))
    m2, s2 = float(np.mean(g2_vals)), float(np.std(g2_vals, ddof=1))
    med1, iqr1 = float(np.median(g1_vals)), float(np.percentile(g1_vals, 75) - np.percentile(g1_vals, 25))
    med2, iqr2 = float(np.median(g2_vals)), float(np.percentile(g2_vals, 75) - np.percentile(g2_vals, 25))

    # Levene's test for equality of variances
    levene_stat, levene_p = stats.levene(g1_vals, g2_vals)
    equal_var = levene_p >= 0.05

    # Normality
    shapiro_g1 = stats.shapiro(g1_vals).pvalue if 3 <= n1 <= 5000 else np.nan
    shapiro_g2 = stats.shapiro(g2_vals).pvalue if 3 <= n2 <= 5000 else np.nan
    is_normal = (np.isnan(shapiro_g1) or shapiro_g1 >= 0.05) and (np.isnan(shapiro_g2) or shapiro_g2 >= 0.05)

    # Effect size (Cohen's d)
    pooled_sd = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    cohen_d = (m1 - m2) / pooled_sd if pooled_sd > 0 else 0.0

    # Mean difference and 95% CI
    mean_diff = m1 - m2
    se_diff = np.sqrt(s1**2 / n1 + s2**2 / n2)
    dof_welch = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1)) if se_diff > 0 else 1
    t_crit = stats.t.ppf(0.975, df=dof_welch)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    # Select method
    selected_method = test_method
    if test_method == "auto":
        if is_normal and equal_var:
            selected_method = "student_t"
        elif is_normal and not equal_var:
            selected_method = "welch_t"
        else:
            selected_method = "mann_whitney"

    stat_val, p_val = 0.0, 1.0
    method_name = ""
    advisor_reason = ""

    if selected_method == "student_t":
        stat_val, p_val = stats.ttest_ind(g1_vals, g2_vals, equal_var=True)
        method_name = "學生氏獨立樣本 t 檢定 (Student's t-test)"
        advisor_reason = "兩組皆符合常態分佈假設且通過 Levene 變異數齊一性檢定 (p ≥ 0.05)。"
    elif selected_method == "welch_t":
        stat_val, p_val = stats.ttest_ind(g1_vals, g2_vals, equal_var=False)
        method_name = "韋爾奇 t 檢定 (Welch's t-test, 變異數不齊一)"
        advisor_reason = "資料符合常態性但未通過 Levene 變異數齊一性檢定 (p < 0.05)，使用 Welch 自由度修正。"
    elif selected_method == "mann_whitney":
        stat_val, p_val = stats.mannwhitneyu(g1_vals, g2_vals, alternative='two-sided')
        method_name = "曼-惠特尼 U 檢定 (Mann-Whitney U Test, 無母數)"
        advisor_reason = "至少一組不符合常態分佈假設 (p < 0.05)，依據生醫統計規範推薦無母數檢定。"

    return {
        '檢定方法': method_name,
        '統計方法代碼': selected_method,
        '推薦依據': advisor_reason,
        '統計量': float(stat_val),
        'p值': float(p_val),
        '顯著性 (p < 0.05)': bool(p_val < 0.05),
        '組別 1 名稱': g1_label,
        '組別 1 樣本數': n1,
        '組別 1 平均值': round(m1, 3),
        '組別 1 標準差': round(s1, 3),
        '組別 1 中位數': round(med1, 3),
        '組別 1 IQR': round(iqr1, 3),
        '組別 1 常態 p值': shapiro_g1,
        '組別 2 名稱': g2_label,
        '組別 2 樣本數': n2,
        '組別 2 平均值': round(m2, 3),
        '組別 2 標準差': round(s2, 3),
        '組別 2 中位數': round(med2, 3),
        '組別 2 IQR': round(iqr2, 3),
        '組別 2 常態 p值': shapiro_g2,
        '平均差值': round(mean_diff, 3),
        '95% 信賴區間下限': round(ci_lower, 3),
        '95% 信賴區間上限': round(ci_upper, 3),
        'Cohen d 效果值': round(cohen_d, 3),
        'Levene 檢定統計量': round(levene_stat, 4),
        'Levene 檢定 p值': round(levene_p, 4),
        '變異數齊一': bool(equal_var),
        '符合常態性': bool(is_normal)
    }

# ==============================================================================
# 3. 配對樣本比較 (Paired Samples Comparison: Pre vs Post)
# ==============================================================================
def paired_samples_comparison(df: pd.DataFrame, pre_col: str, post_col: str, test_method: str = "auto") -> Dict[str, Any]:
    """Perform paired samples hypothesis testing (Paired t-test vs Wilcoxon Signed-Rank)."""
    sub_df = df[[pre_col, post_col]].dropna()
    n = len(sub_df)
    if n < 3:
        raise ValueError("配對樣本需至少包含 3 筆完整的前後測數據。")

    pre_vals = sub_df[pre_col].values
    post_vals = sub_df[post_col].values
    diff = post_vals - pre_vals

    mean_pre, sd_pre = float(np.mean(pre_vals)), float(np.std(pre_vals, ddof=1))
    mean_post, sd_post = float(np.mean(post_vals)), float(np.std(post_vals, ddof=1))
    mean_diff, sd_diff = float(np.mean(diff)), float(np.std(diff, ddof=1))
    med_diff = float(np.median(diff))

    # Normality of difference
    diff_shapiro_stat, diff_shapiro_p = stats.shapiro(diff) if n <= 5000 else (np.nan, np.nan)
    is_normal = np.isnan(diff_shapiro_p) or diff_shapiro_p >= 0.05

    # Paired Cohen's dz
    cohen_dz = mean_diff / sd_diff if sd_diff > 0 else 0.0

    # 95% CI of mean difference
    se_diff = sd_diff / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=n - 1)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    # Select method
    selected_method = test_method
    if test_method == "auto":
        selected_method = "paired_t" if is_normal else "wilcoxon"

    stat_val, p_val = 0.0, 1.0
    method_name = ""
    advisor_reason = ""

    if selected_method == "paired_t":
        stat_val, p_val = stats.ttest_rel(post_vals, pre_vals)
        method_name = "配對樣本 t 檢定 (Paired Samples t-test)"
        advisor_reason = "前後測差值符合常態分佈假設 (Shapiro-Wilk p ≥ 0.05)。"
    else:
        stat_val, p_val = stats.wilcoxon(post_vals, pre_vals)
        method_name = "威爾卡森符號等級檢定 (Wilcoxon Signed-Rank Test, 配對無母數)"
        advisor_reason = "前後測差值不符合常態分佈 (Shapiro-Wilk p < 0.05)，推薦採用無母數配對檢定。"

    return {
        '檢定方法': method_name,
        '統計方法代碼': selected_method,
        '推薦依據': advisor_reason,
        '統計量': float(stat_val),
        'p值': float(p_val),
        '顯著性 (p < 0.05)': bool(p_val < 0.05),
        '配對樣本數 (N)': n,
        '前測變項': pre_col,
        '後測變項': post_col,
        '前測 Mean ± SD': f"{mean_pre:.3f} ± {sd_pre:.3f}",
        '後測 Mean ± SD': f"{mean_post:.3f} ± {sd_post:.3f}",
        '平均差值 (Post - Pre)': round(mean_diff, 3),
        '差值標準差': round(sd_diff, 3),
        '差值中位數': round(med_diff, 3),
        '差值 95% 信賴區間': f"[{ci_lower:.3f}, {ci_upper:.3f}]",
        '配對效果值 (Cohen dz)': round(cohen_dz, 3),
        '差值常態性檢定 p值': diff_shapiro_p,
        '差值符合常態性': is_normal
    }

# ==============================================================================
# 4. 多組單因子比較 (One-Way ANOVA & Kruskal-Wallis)
# ==============================================================================
def multi_group_comparison(df: pd.DataFrame, value_col: str, group_col: str) -> Dict[str, Any]:
    """Perform One-way ANOVA, Kruskal-Wallis, and post-hoc Tukey HSD test."""
    sub_df = df[[value_col, group_col]].dropna()
    groups = sub_df[group_col].unique()

    if len(groups) < 2:
        raise ValueError(f"分組變項至少需有 2 組以上，目前只有 {len(groups)} 組。")

    group_data = [sub_df[sub_df[group_col] == g][value_col].values for g in groups]

    # One-way ANOVA
    f_stat, anova_p = stats.f_oneway(*group_data)

    # Kruskal-Wallis
    h_stat, kw_p = stats.kruskal(*group_data)

    # Group summary
    grp_summary = []
    for g in groups:
        vals = sub_df[sub_df[group_col] == g][value_col].values
        n_g = len(vals)
        grp_summary.append({
            '組別': str(g),
            '樣本數 (N)': n_g,
            '平均值 (Mean)': round(float(np.mean(vals)), 3) if n_g > 0 else 0,
            '標準差 (SD)': round(float(np.std(vals, ddof=1)), 3) if n_g > 1 else 0,
            '中位數 (Median)': round(float(np.median(vals)), 3) if n_g > 0 else 0,
            '四分位距 (IQR)': round(float(np.percentile(vals, 75) - np.percentile(vals, 25)), 3) if n_g > 0 else 0
        })
    summary_df = pd.DataFrame(grp_summary)

    # Tukey HSD Post-hoc
    tukey_df = None
    if anova_p < 0.05 and len(groups) > 2:
        try:
            tukey = pairwise_tukeyhsd(endog=sub_df[value_col], groups=sub_df[group_col], alpha=0.05)
            tukey_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
            tukey_df.columns = ['組別 1', '組別 2', '平均差值', 'p 值', '95% CI 下限', '95% CI 上限', '顯著拒絕虛無假設']
        except Exception:
            pass

    return {
        '組別數': len(groups),
        'ANOVA F 值': float(f_stat),
        'ANOVA p 值': float(anova_p),
        'ANOVA 顯著性 (p < 0.05)': bool(anova_p < 0.05),
        'Kruskal-Wallis H 值': float(h_stat),
        'Kruskal-Wallis p 值': float(kw_p),
        '各組摘要': summary_df,
        'Tukey HSD 事後檢定': tukey_df
    }

# ==============================================================================
# 5. 雙因子變異數分析 (Two-Way ANOVA with Interaction)
# ==============================================================================
def two_way_anova(df: pd.DataFrame, value_col: str, factor1_col: str, factor2_col: str) -> Dict[str, Any]:
    """Perform Two-Way ANOVA assessing main effects and interaction effect."""
    sub_df = df[[value_col, factor1_col, factor2_col]].dropna()
    formula = f"Q('{value_col}') ~ C(Q('{factor1_col}')) + C(Q('{factor2_col}')) + C(Q('{factor1_col}')):C(Q('{factor2_col}'))"
    model = smf.ols(formula, data=sub_df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    # Rename indices for clean presentation
    display_table = pd.DataFrame({
        '自由度 (df)': anova_table['df'].astype(int),
        '平方和 (Sum Sq)': anova_table['sum_sq'].round(3),
        '均方 (Mean Sq)': (anova_table['sum_sq'] / anova_table['df']).round(3),
        'F 檢定值': anova_table['F'].round(4),
        'p 值': [f"{p:.4e}" if p < 0.001 else f"{p:.4f}" for p in anova_table['PR(>F)']],
        '顯著性 (p < 0.05)': anova_table['PR(>F)'] < 0.05
    })
    
    # Map index names
    index_map = {
        f"C(Q('{factor1_col}'))": f"主效應: {factor1_col}",
        f"C(Q('{factor2_col}'))": f"主效應: {factor2_col}",
        f"C(Q('{factor1_col}')):C(Q('{factor2_col}'))": f"交互作用: {factor1_col} × {factor2_col}",
        "Residual": "殘差 (Residual)"
    }
    display_table.index = [index_map.get(idx, idx) for idx in display_table.index]

    return {
        'anova_table': display_table,
        'r_squared': round(model.rsquared, 4),
        'f1_name': factor1_col,
        'f2_name': factor2_col
    }

# ==============================================================================
# 6. 類別變項列聯表 (Chi-Square, Fisher's Exact, Odds Ratio)
# ==============================================================================
def contingency_analysis(df: pd.DataFrame, row_col: str, col_col: str) -> Dict[str, Any]:
    """Perform Contingency Table analysis with Chi-Square, Fisher's Exact, and Odds Ratio."""
    sub_df = df[[row_col, col_col]].dropna()
    contingency = pd.crosstab(sub_df[row_col], sub_df[col_col])

    chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
    min_expected = np.min(expected)

    fisher_p = None
    odds_ratio = None
    if contingency.shape == (2, 2):
        try:
            res_fisher = stats.fisher_exact(contingency)
            odds_ratio = float(res_fisher[0])
            fisher_p = float(res_fisher[1])
        except Exception:
            pass

    advisor_note = ""
    if min_expected < 5:
        advisor_note = "⚠️ 警告：列聯表中有格子期望頻次小於 5，傳統卡方檢定可能失準，強烈建議採納 Fisher's Exact Test 結果。"
    else:
        advisor_note = "✅ 所有格子期望頻次均 ≥ 5，卡方檢定適法性良好。"

    return {
        '觀察頻次列聯表': contingency,
        '期望頻次矩陣': pd.DataFrame(expected, index=contingency.index, columns=contingency.columns).round(2),
        '卡方統計量': float(chi2),
        '自由度': int(dof),
        '卡方 p 值': float(p_val),
        '顯著性 (p < 0.05)': bool(p_val < 0.05),
        '最小期望頻次': float(min_expected),
        '適法性診斷': advisor_note,
        'Fisher Exact p 值': fisher_p,
        'Odds Ratio': round(odds_ratio, 3) if odds_ratio is not None else None
    }

# ==============================================================================
# 7. 相關係數分析矩陣 (Correlation Analysis)
# ==============================================================================
def correlation_matrix(df: pd.DataFrame, columns: List[str], method: str = 'pearson') -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Calculate correlation matrix, p-values matrix, and pairwise summary table."""
    sub_df = df[columns].dropna()
    n_cols = len(columns)
    corr_matrix = np.zeros((n_cols, n_cols))
    p_matrix = np.zeros((n_cols, n_cols))

    pairs = []
    for i in range(n_cols):
        for j in range(n_cols):
            if i == j:
                corr_matrix[i, j] = 1.0
                p_matrix[i, j] = 0.0
            else:
                x, y = sub_df[columns[i]], sub_df[columns[j]]
                if method == 'pearson':
                    r, p = stats.pearsonr(x, y)
                elif method == 'spearman':
                    r, p = stats.spearmanr(x, y)
                else:
                    r, p = stats.kendalltau(x, y)
                corr_matrix[i, j] = r
                p_matrix[i, j] = p
                if i < j:
                    pairs.append({
                        '變項 1': columns[i],
                        '變項 2': columns[j],
                        '相關係數 (r)': round(r, 3),
                        'p 值': f"{p:.4e}" if p < 0.001 else f"{p:.4f}",
                        '顯著性 (p < 0.05)': p < 0.05,
                        '相關強度': "強相關" if abs(r) >= 0.7 else ("中等相關" if abs(r) >= 0.4 else "微弱相關")
                    })

    corr_df = pd.DataFrame(corr_matrix, index=columns, columns=columns)
    p_df = pd.DataFrame(p_matrix, index=columns, columns=columns)
    pairs_df = pd.DataFrame(pairs).sort_values(by='相關係數 (r)', key=abs, ascending=False).reset_index(drop=True)
    return corr_df, p_df, pairs_df

# ==============================================================================
# 8. Kaplan-Meier 存活分析與 Log-Rank 檢定
# ==============================================================================
def fit_survival_analysis(df: pd.DataFrame, duration_col: str, event_col: str, group_col: Optional[str] = None) -> Dict[str, Any]:
    """Kaplan-Meier survival estimation and log-rank test."""
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test

    sub_df = df[[duration_col, event_col] + ([group_col] if group_col else [])].dropna()
    sub_df[event_col] = pd.to_numeric(sub_df[event_col], errors='coerce').fillna(0).astype(int)

    kmf = KaplanMeierFitter()
    total_n = len(sub_df)
    events_n = int(sub_df[event_col].sum())
    censored_pct = round((1 - events_n / total_n) * 100, 1) if total_n > 0 else 0.0

    medians = {}
    logrank_stat = None
    logrank_p = None

    if not group_col:
        kmf.fit(sub_df[duration_col], event_observed=sub_df[event_col], label='Overall')
        medians['Overall'] = round(kmf.median_survival_time_, 2)
    else:
        unique_groups = sub_df[group_col].unique()
        for g in unique_groups:
            g_data = sub_df[sub_df[group_col] == g]
            kmf_g = KaplanMeierFitter()
            kmf_g.fit(g_data[duration_col], event_observed=g_data[event_col], label=str(g))
            medians[str(g)] = round(kmf_g.median_survival_time_, 2)

        if len(unique_groups) == 2:
            g1_data = sub_df[sub_df[group_col] == unique_groups[0]]
            g2_data = sub_df[sub_df[group_col] == unique_groups[1]]
            lr = logrank_test(g1_data[duration_col], g2_data[duration_col],
                              event_observed_A=g1_data[event_col], event_observed_B=g2_data[event_col])
            logrank_stat = round(lr.test_statistic, 4)
            logrank_p = lr.p_value

    return {
        '樣本總數': total_n,
        '事件發生數': events_n,
        '設限比例 (%)': censored_pct,
        '中位存活時間': medians,
        'Log-Rank 統計量': logrank_stat,
        'Log-Rank p 值': logrank_p
    }

# ==============================================================================
# 9. Cox 比例風險模型 (Cox Proportional Hazards Regression)
# ==============================================================================
def fit_cox_ph(df: pd.DataFrame, duration_col: str, event_col: str, covariate_cols: List[str]) -> Dict[str, Any]:
    """Fit Cox Proportional Hazards Model and compute Hazard Ratios with 95% CIs."""
    from lifelines import CoxPHFitter
    
    sub_df = df[[duration_col, event_col] + covariate_cols].dropna()
    sub_df[event_col] = pd.to_numeric(sub_df[event_col], errors='coerce').fillna(0).astype(int)

    # One-hot encode any string/categorical covariates
    sub_df = pd.get_dummies(sub_df, drop_first=True)

    cph = CoxPHFitter()
    cph.fit(sub_df, duration_col=duration_col, event_col=event_col)

    summary_df = cph.summary.copy()
    coef_table = pd.DataFrame({
        '變項 (Covariate)': summary_df.index,
        '危險比 (Hazard Ratio, exp(coef))': summary_df['exp(coef)'].round(3),
        '95% CI 下限': summary_df['exp(coef) lower 95%'].round(3),
        '95% CI 上限': summary_df['exp(coef) upper 95%'].round(3),
        'z 統計量': summary_df['z'].round(3),
        'p 值 (p-value)': [f"{p:.4e}" if p < 0.001 else f"{p:.4f}" for p in summary_df['p']],
        '統計顯著性 (p < 0.05)': summary_df['p'] < 0.05
    }).reset_index(drop=True)

    return {
        'c_index': round(cph.concordance_index_, 3),
        'log_likelihood': round(cph.log_likelihood_, 2),
        'aic': round(cph.AIC_partial_, 2),
        'coef_table': coef_table,
        'n_obs': len(sub_df),
        'n_events': int(sub_df[event_col].sum())
    }

# ==============================================================================
# 10. 二元邏輯斯迴歸分析 (Binary Logistic Regression)
# ==============================================================================
def fit_logistic_regression(df: pd.DataFrame, y_col: str, x_cols: List[str]) -> Dict[str, Any]:
    """Fit Binary Logistic Regression model, reporting Odds Ratios (OR) and 95% CI."""
    sub_df = df[[y_col] + x_cols].dropna()
    y = sub_df[y_col]
    
    # Ensure binary outcome
    unique_y = y.unique()
    if len(unique_y) != 2:
        raise ValueError(f"邏輯斯迴歸的應變項 (Y) 必須是二元類別 (恰好 2 個相異值)，目前偵測到: {list(unique_y)}")

    # Convert to 0 and 1 if not already
    if set(unique_y) != {0, 1}:
        y = (y == unique_y[1]).astype(int)

    X = pd.get_dummies(sub_df[x_cols], drop_first=True)
    X_const = sm.add_constant(X)

    logit_mod = sm.Logit(y, X_const).fit(disp=False)
    
    params = logit_mod.params
    conf = logit_mod.conf_int()
    odds_ratios = np.exp(params)
    or_lower = np.exp(conf[0])
    or_upper = np.exp(conf[1])

    coef_df = pd.DataFrame({
        '變項名稱': params.index,
        '迴歸係數 (Beta)': params.round(4),
        '標準誤 (SE)': logit_mod.bse.round(4),
        '勝算比 (Odds Ratio)': odds_ratios.round(3),
        'OR 95% CI 下限': or_lower.round(3),
        'OR 95% CI 上限': or_upper.round(3),
        'z 統計量': logit_mod.tvalues.round(3),
        'p 值': [f"{p:.4e}" if p < 0.001 else f"{p:.4f}" for p in logit_mod.pvalues],
        '顯著性 (p < 0.05)': logit_mod.pvalues < 0.05
    }).reset_index(drop=True)

    return {
        'pseudo_r2': round(logit_mod.prsquared, 4),
        'll_ratio_p': logit_mod.llr_pvalue,
        'coef_table': coef_df,
        'n_obs': int(logit_mod.nobs)
    }

# ==============================================================================
# 11. 多元線性迴歸分析 (OLS Linear Regression)
# ==============================================================================
def fit_linear_regression(df: pd.DataFrame, y_col: str, x_cols: List[str]) -> Dict[str, Any]:
    """Fit OLS linear regression and return formatted diagnostics."""
    sub_df = df[[y_col] + x_cols].dropna()
    X = pd.get_dummies(sub_df[x_cols], drop_first=True)
    X_const = sm.add_constant(X)
    y = sub_df[y_col]

    model = sm.OLS(y, X_const).fit()

    coef_df = pd.DataFrame({
        '變項名稱': model.params.index,
        '係數 (Estimate)': model.params.round(4),
        '標準誤 (Std.Error)': model.bse.round(4),
        't 檢定值 (t-Stat)': model.tvalues.round(4),
        'p 值 (P>|t|)': [f"{p:.4e}" if p < 0.0001 else f"{p:.4f}" for p in model.pvalues],
        '95% CI 下限': model.conf_int()[0].round(4),
        '95% CI 上限': model.conf_int()[1].round(4),
        '顯著性 (p < 0.05)': model.pvalues < 0.05
    }).reset_index(drop=True)

    return {
        'R平方 (R2)': round(model.rsquared, 4),
        '調整後 R平方': round(model.rsquared_adj, 4),
        'F 檢定統計量': round(model.fvalue, 4),
        'F 檢定 p 值': model.f_pvalue,
        '係數表': coef_df,
        '樣本數': int(model.nobs)
    }

# ==============================================================================
# 12. 智慧統計方法推薦決策精靈 (Statistical Method Advisor)
# ==============================================================================
def advise_statistical_method(goal: str, sample_size: int, is_normal: bool = True,
                              equal_var: bool = True, paired: bool = False,
                              num_groups: int = 2, min_expected_count: float = 10.0) -> Dict[str, Any]:
    """Provide rule-based statistical decision advising for biomedical research."""
    rec = {}
    if goal == "two_group":
        if paired:
            if is_normal:
                rec['primary'] = "配對樣本 t 檢定 (Paired Samples t-test)"
                rec['rationale'] = "配對前後測差值符合常態分佈假設。"
                rec['alternative'] = "威爾卡森符號等級檢定 (Wilcoxon Signed-Rank Test)"
            else:
                rec['primary'] = "威爾卡森符號等級檢定 (Wilcoxon Signed-Rank Test)"
                rec['rationale'] = "前後測差值不符合常態分佈，應使用無母數配對檢定。"
                rec['alternative'] = "無 (建議維持無母數分析)"
        else:
            if is_normal and equal_var:
                rec['primary'] = "學生氏獨立樣本 t 檢定 (Student's t-test)"
                rec['rationale'] = "符合母數分析假設：兩組皆常態分佈且變異數齊一。"
                rec['alternative'] = "曼-惠特尼 U 檢定 (Mann-Whitney U Test)"
            elif is_normal and not equal_var:
                rec['primary'] = "韋爾奇 t 檢定 (Welch's t-test)"
                rec['rationale'] = "資料符合常態性但變異數不齊一，以 Welch 自由度修正避免型一錯誤膨脹。"
                rec['alternative'] = "曼-惠特尼 U 檢定 (Mann-Whitney U Test)"
            else:
                rec['primary'] = "曼-惠特尼 U 檢定 (Mann-Whitney U Test)"
                rec['rationale'] = "至少一組嚴重偏離常態分佈，醫學統計規範建議採無母數檢定。"
                rec['alternative'] = "Welch's t-test (若樣本數極大 n>100 可考量中央極限定理)"

    elif goal == "multi_group":
        if is_normal and equal_var:
            rec['primary'] = "單因子變異數分析 (One-way ANOVA) + Tukey HSD 事後檢定"
            rec['rationale'] = "各組均符合常態性且變異數齊一，ANOVA 能有效控制多重比較族誤差率。"
            rec['alternative'] = "Kruskal-Wallis 檢定"
        else:
            rec['primary'] = "克魯斯卡-沃利斯檢定 (Kruskal-Wallis Test, 無母數 ANOVA)"
            rec['rationale'] = "資料偏離常態性或變異數不齊一，應避免使用傳統 ANOVA。"
            rec['alternative'] = "Welch's ANOVA (若僅變異數不齊一但常態)"

    elif goal == "contingency":
        if min_expected_count < 5:
            rec['primary'] = "費雪精確檢定 (Fisher's Exact Test)"
            rec['rationale'] = "列聯表中有格子期望次數 < 5，卡方漸近分佈失準，必須使用精確檢定。"
            rec['alternative'] = "葉氏連續性校正卡方檢定 (Yates' correction)"
        else:
            rec['primary'] = "皮爾森卡方獨立性檢定 (Pearson's Chi-Square Test)"
            rec['rationale'] = "所有格子期望頻次均 ≥ 5，卡方檢定適法性良好。"
            rec['alternative'] = "Fisher's Exact Test"

    elif goal == "survival":
        rec['primary'] = "Kaplan-Meier 存活分析 + Log-Rank 檢定 (單變項) / Cox PH 模型 (多變項)"
        rec['rationale'] = "生物醫學存活追蹤數據帶有設限 (Censored)，必須採用時間至事件 (Time-to-Event) 統計模型。"
        rec['alternative'] = "Wilcoxon-Breslow-Gehan 檢定 (若強調早期存活差異)"

    return rec

# ==============================================================================
# 13. 專業結構化醫學統計分析報告產生器 (Comprehensive Statistical Report)
# ==============================================================================
def generate_clinical_report(task_type: str, results: Dict[str, Any], title: str = "") -> str:
    """Generate publication-ready structured statistical narrative reports in Markdown/HTML format."""
    lines = []
    lines.append(f"# 📋 生物醫學統計分析報告：{title or task_type}")
    lines.append(f"**分析日期**：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("---")

    if task_type == "two_group":
        lines.append("### 一、 分析研究假說與方法")
        lines.append(f"- **應變數 (數值)**：分析組別間之平均差異")
        lines.append(f"- **採用統計檢定**：`{results['檢定方法']}`")
        lines.append(f"- **統計方法決策依據**：{results['推薦依據']}")
        lines.append("")
        lines.append("### 二、 前提假設與診斷檢定")
        lines.append(f"- **常態性假設**：組別 1 Shapiro-Wilk p = `{results['組別 1 常態 p值']}`，組別 2 p = `{results['組別 2 常態 p值']}`（結論：{'符合常態性' if results['符合常態性'] else '非常態/偏態'}）")
        lines.append(f"- **變異數齊一性 (Levene's Test)**：F = `{results['Levene 檢定統計量']}`，p = `{results['Levene 檢定 p值']}`（結論：{'變異數齊一' if results['變異數齊一'] else '變異數不齊一'}）")
        lines.append("")
        lines.append("### 三、 統計量與效果值結果")
        lines.append(f"| 組別 | 樣本數 (N) | 平均值 ± 標準差 (Mean ± SD) | 中位數 (IQR) |")
        lines.append(f"| :--- | :--- | :--- | :--- |")
        lines.append(f"| {results['組別 1 名稱']} | {results['組別 1 樣本數']} | {results['組別 1 平均值']} ± {results['組別 1 標準差']} | {results['組別 1 中位數']} ({results['組別 1 IQR']}) |")
        lines.append(f"| {results['組別 2 名稱']} | {results['組別 2 樣本數']} | {results['組別 2 平均值']} ± {results['組別 2 標準差']} | {results['組別 2 中位數']} ({results['組別 2 IQR']}) |")
        lines.append("")
        lines.append(f"- **統計檢定值**：`{results['統計量']:.4f}`")
        lines.append(f"- **雙尾 p 值**：`{results['p值']:.4e}` ({'達統計顯著水準 p < 0.05' if results['顯著性 (p < 0.05)'] else '未達統計顯著水準 p ≥ 0.05'})")
        lines.append(f"- **兩組平均差值 (95% CI)**：`{results['平均差值']} [{results['95% 信賴區間下限']}, {results['95% 信賴區間上限']}]`")
        lines.append(f"- **效果值 (Cohen's d)**：`{results['Cohen d 效果值']}`")
        lines.append("")
        lines.append("### 四、 醫學期刊規範結論解讀 (Conclusion)")
        sig_text = "存在顯著統計學差異" if results['顯著性 (p < 0.05)'] else "未發現統計學顯著差異"
        lines.append(f"> 根據 **{results['檢定方法']}** 分析，{results['組別 1 名稱']} 與 {results['組別 2 名稱']} 之間 **{sig_text}**（統計量 = {results['統計量']:.3f}, p = {results['p值']:.4e}）。兩組平均差值為 {results['平均差值']} (95% CI [{results['95% 信賴區間下限']}, {results['95% 信賴區間上限']}]，標準化效果值 Cohen's d = {results['Cohen d 效果值']}）。")

    elif task_type == "paired":
        lines.append("### 一、 前後測配對分析研究假說")
        lines.append(f"- **前測變項**：`{results['前測變項']}` | **後測變項**：`{results['後測變項']}` (N = {results['配對樣本數 (N)']})")
        lines.append(f"- **採用檢定方法**：`{results['檢定方法']}`")
        lines.append(f"- **方法依據**：{results['推薦依據']}")
        lines.append("")
        lines.append("### 二、 前後測數值比較與差值分佈")
        lines.append(f"- **前測數值**：{results['前測 Mean ± SD']}")
        lines.append(f"- **後測數值**：{results['後測 Mean ± SD']}")
        lines.append(f"- **平均差值 (Post - Pre)**：`{results['平均差值 (Post - Pre)']} ± {results['差值標準差']}` (95% CI: `{results['差值 95% 信賴區間']}`)")
        lines.append(f"- **差值常態性檢定**：Shapiro-Wilk p = `{results['差值常態性檢定 p值']}`")
        lines.append(f"- **統計量與 p 值**：統計值 = `{results['統計量']:.4f}`，p = `{results['p值']:.4e}`")
        lines.append(f"- **配對效果值 (Cohen's dz)**：`{results['配對效果值 (Cohen dz)']}`")
        lines.append("")
        lines.append("### 三、 醫學期刊規範結論解讀 (Conclusion)")
        sig_text = "具有高度統計顯著性變化" if results['顯著性 (p < 0.05)'] else "前後未觀察到顯著差異"
        lines.append(f"> 經由 **{results['檢定方法']}** 評估，受試者於治療後 **{sig_text}**（平均差值 = {results['平均差值 (Post - Pre)']}, 95% CI {results['差值 95% 信賴區間']}, 檢定統計值 = {results['統計量']:.3f}, p = {results['p值']:.4e}, 配對效果量 dz = {results['配對效果值 (Cohen dz)']}）。")

    return "\n".join(lines)
