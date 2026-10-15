import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from typing import Dict, Any, List, Optional, Tuple

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
                norm_verdict = "常態分佈 (p ≥ 0.05)" if p >= 0.05 else "偏態 / 非常態 (p < 0.05)"
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

def two_group_comparison(df: pd.DataFrame, value_col: str, group_col: str, test_method: str = "auto") -> Dict[str, Any]:
    """Perform two-group hypothesis testing (Student's t, Welch's t, Mann-Whitney U)."""
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

    # Effect size (Cohen's d)
    pooled_sd = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    cohen_d = (m1 - m2) / pooled_sd if pooled_sd > 0 else 0.0

    # Mean difference and 95% CI
    mean_diff = m1 - m2
    se_diff = np.sqrt(s1**2 / n1 + s2**2 / n2)
    # Welch-Satterthwaite df
    dof_welch = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1)) if se_diff > 0 else 1
    t_crit = stats.t.ppf(0.975, df=dof_welch)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    # Tests calculation
    t_stat_stu, t_p_stu = stats.ttest_ind(g1_vals, g2_vals, equal_var=True)
    t_stat_welch, t_p_welch = stats.ttest_ind(g1_vals, g2_vals, equal_var=False)
    mwu_stat, mwu_p = stats.mannwhitneyu(g1_vals, g2_vals, alternative='two-sided')

    # Selected test
    if test_method == "t_student":
        chosen_name = "獨立樣本 t 檢定 (Student's t-test, 等變異數)"
        stat_val, p_val = t_stat_stu, t_p_stu
    elif test_method == "t_welch":
        chosen_name = "韋爾奇 t 檢定 (Welch's t-test, 異變異數)"
        stat_val, p_val = t_stat_welch, t_p_welch
    elif test_method == "mann_whitney":
        chosen_name = "曼-惠特尼 U 無母數檢定 (Mann-Whitney U test)"
        stat_val, p_val = mwu_stat, mwu_p
    else: # auto
        is_normal = (np.isnan(shapiro_g1) or shapiro_g1 >= 0.05) and (np.isnan(shapiro_g2) or shapiro_g2 >= 0.05)
        if not is_normal:
            chosen_name = "曼-惠特尼 U 檢定 (自動推薦：數據偏離常態分佈)"
            stat_val, p_val = mwu_stat, mwu_p
        elif equal_var:
            chosen_name = "學生 t 檢定 (自動推薦：常態且變異數齊一)"
            stat_val, p_val = t_stat_stu, t_p_stu
        else:
            chosen_name = "韋爾奇 t 檢定 (自動推薦：常態但變異數不齊)"
            stat_val, p_val = t_stat_welch, t_p_welch

    summary_df = pd.DataFrame([
        {'組別': g1_label, 'N': n1, 'Mean': round(m1, 3), 'SD': round(s1, 3), 'Median': round(med1, 3), 'IQR': round(iqr1, 3), '常態檢定 p': f"{shapiro_g1:.4f}" if not np.isnan(shapiro_g1) else "N/A"},
        {'組別': g2_label, 'N': n2, 'Mean': round(m2, 3), 'SD': round(s2, 3), 'Median': round(med2, 3), 'IQR': round(iqr2, 3), '常態檢定 p': f"{shapiro_g2:.4f}" if not np.isnan(shapiro_g2) else "N/A"}
    ])

    results = {
        'group1': g1_label,
        'group2': g2_label,
        'summary_table': summary_df,
        'levene_p': levene_p,
        'equal_variance': equal_var,
        'chosen_test': chosen_name,
        'statistic': round(stat_val, 4),
        'p_value': p_val,
        'cohen_d': round(cohen_d, 4),
        'mean_difference': round(mean_diff, 4),
        'ci_95': (round(ci_lower, 4), round(ci_upper, 4)),
        'all_tests': {
            "Student's t-test": {'stat': t_stat_stu, 'p': t_p_stu},
            "Welch's t-test": {'stat': t_stat_welch, 'p': t_p_welch},
            "Mann-Whitney U": {'stat': mwu_stat, 'p': mwu_p}
        }
    }
    return results

def multi_group_comparison(df: pd.DataFrame, value_col: str, group_col: str) -> Dict[str, Any]:
    """Perform ANOVA and Kruskal-Wallis testing with Tukey HSD post-hoc."""
    sub_df = df[[value_col, group_col]].dropna()
    groups = sub_df[group_col].unique()

    if len(groups) < 3:
        raise ValueError(f"多組比較至少需要 3 個組別，目前偵測到 {len(groups)} 個組別。請使用兩組比較。")

    group_data = [sub_df[sub_df[group_col] == g][value_col].values for g in groups]

    # Group summaries
    group_summaries = []
    for g, vals in zip(groups, group_data):
        group_summaries.append({
            '組別': str(g),
            '樣本數 (N)': len(vals),
            '平均值 (Mean)': round(float(np.mean(vals)), 3),
            '標準差 (SD)': round(float(np.std(vals, ddof=1)), 3),
            '中位數 (Median)': round(float(np.median(vals)), 3),
            '四分位距 (IQR)': round(float(np.percentile(vals, 75) - np.percentile(vals, 25)), 3)
        })
    summary_df = pd.DataFrame(group_summaries)

    # One-Way ANOVA
    f_stat, anova_p = stats.f_oneway(*group_data)

    # Kruskal-Wallis H test
    kw_stat, kw_p = stats.kruskal(*group_data)

    # Levene test
    levene_stat, levene_p = stats.levene(*group_data)

    # Tukey HSD Post-hoc
    tukey = pairwise_tukeyhsd(endog=sub_df[value_col], groups=sub_df[group_col].astype(str), alpha=0.05)
    tukey_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
    tukey_df = tukey_df.rename(columns={
        'group1': '組別 1',
        'group2': '組別 2',
        'meandiff': '平均值差異',
        'p-adj': '調整後 p 值',
        'lower': '95% CI 下限',
        'upper': '95% CI 上限',
        'reject': '顯著差異 (p<0.05)'
    })

    return {
        'summary_table': summary_df,
        'anova_f': round(f_stat, 4),
        'anova_p': anova_p,
        'kruskal_h': round(kw_stat, 4),
        'kruskal_p': kw_p,
        'levene_p': levene_p,
        'tukey_posthoc': tukey_df
    }

def contingency_analysis(df: pd.DataFrame, row_col: str, col_col: str) -> Dict[str, Any]:
    """Perform Chi-Square, Fisher's Exact test, Odds Ratio and Relative Risk."""
    sub_df = df[[row_col, col_col]].dropna()
    crosstab_counts = pd.crosstab(sub_df[row_col], sub_df[col_col])
    crosstab_pct = pd.crosstab(sub_df[row_col], sub_df[col_col], normalize='index') * 100

    # Chi-Square Test
    chi2, p_val, dof, expected = stats.chi2_contingency(crosstab_counts)

    # Cramér's V
    n = crosstab_counts.sum().sum()
    min_dim = min(crosstab_counts.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0.0

    result = {
        'crosstab_counts': crosstab_counts,
        'crosstab_pct': crosstab_pct.round(1),
        'chi2_stat': round(chi2, 4),
        'chi2_p': p_val,
        'dof': dof,
        'cramers_v': round(cramers_v, 4),
        'is_2x2': crosstab_counts.shape == (2, 2)
    }

    # If 2x2 table, compute Fisher's exact, Odds Ratio & Relative Risk
    if crosstab_counts.shape == (2, 2):
        odds_ratio, fisher_p = stats.fisher_exact(crosstab_counts)
        a = crosstab_counts.iloc[0, 0]
        b = crosstab_counts.iloc[0, 1]
        c = crosstab_counts.iloc[1, 0]
        d = crosstab_counts.iloc[1, 1]

        # 95% CI for OR (Woolf's formula)
        if a > 0 and b > 0 and c > 0 and d > 0:
            log_or = np.log(odds_ratio)
            se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d)
            or_ci_lower = np.exp(log_or - 1.96 * se_log_or)
            or_ci_upper = np.exp(log_or + 1.96 * se_log_or)
        else:
            or_ci_lower, or_ci_upper = np.nan, np.nan

        # Relative Risk (RR)
        risk1 = a / (a + b) if (a + b) > 0 else 0
        risk2 = c / (c + d) if (c + d) > 0 else 0
        rr = risk1 / risk2 if risk2 > 0 else np.nan

        result.update({
            'fisher_p': fisher_p,
            'odds_ratio': round(odds_ratio, 4),
            'or_ci_95': (round(or_ci_lower, 4), round(or_ci_upper, 4)) if not np.isnan(or_ci_lower) else None,
            'relative_risk': round(rr, 4) if not np.isnan(rr) else None
        })

    return result

def correlation_matrix(df: pd.DataFrame, columns: List[str], method: str = 'pearson') -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Calculate correlation coefficient matrix, p-value matrix, and ranked pairs."""
    sub_df = df[columns].dropna()
    corr_df = sub_df.corr(method=method)

    p_matrix = pd.DataFrame(np.zeros(corr_df.shape), index=corr_df.index, columns=corr_df.columns)
    pairs = []

    for i in range(len(columns)):
        for j in range(len(columns)):
            if i == j:
                p_matrix.iloc[i, j] = 0.0
            else:
                x = sub_df[columns[i]]
                y = sub_df[columns[j]]
                if method == 'pearson':
                    _, p = stats.pearsonr(x, y)
                elif method == 'spearman':
                    _, p = stats.spearmanr(x, y)
                else:
                    _, p = stats.kendalltau(x, y)
                p_matrix.iloc[i, j] = p

                if i < j:
                    r_val = corr_df.iloc[i, j]
                    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
                    pairs.append({
                        '變數 1': columns[i],
                        '變數 2': columns[j],
                        '相關係數 (r)': round(r_val, 4),
                        'p 值': f"{p:.4e}" if p < 0.0001 else round(p, 4),
                        '顯著性': sig,
                        '強度解釋': ('極強' if abs(r_val)>=0.8 else ('強' if abs(r_val)>=0.6 else ('中等' if abs(r_val)>=0.4 else ('弱' if abs(r_val)>=0.2 else '極弱/無相關'))))
                    })

    pairs_df = pd.DataFrame(pairs).sort_values(by='相關係數 (r)', key=abs, ascending=False).reset_index(drop=True)
    return corr_df, p_matrix, pairs_df

def fit_survival_analysis(df: pd.DataFrame, duration_col: str, event_col: str, group_col: Optional[str] = None) -> Dict[str, Any]:
    """Kaplan-Meier survival estimation, log-rank test, and median survival."""
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test

    sub_df = df[[duration_col, event_col] + ([group_col] if group_col else [])].dropna()
    sub_df[event_col] = pd.to_numeric(sub_df[event_col], errors='coerce').fillna(0).astype(int)

    kmf = KaplanMeierFitter()
    results = {}

    if not group_col:
        kmf.fit(sub_df[duration_col], event_observed=sub_df[event_col], label='Overall Cohort')
        median_time = kmf.median_survival_time_
        results['overall_median'] = median_time
        results['groups'] = {'Overall': {'median': median_time, 'events': int(sub_df[event_col].sum()), 'total': len(sub_df)}}
    else:
        group_results = {}
        unique_groups = sub_df[group_col].unique()
        for g in unique_groups:
            g_data = sub_df[sub_df[group_col] == g]
            kmf_g = KaplanMeierFitter()
            kmf_g.fit(g_data[duration_col], event_observed=g_data[event_col], label=str(g))
            group_results[str(g)] = {
                'median': kmf_g.median_survival_time_,
                'events': int(g_data[event_col].sum()),
                'total': len(g_data)
            }
        results['groups'] = group_results

        # Log-rank test between first 2 groups (or pairwise)
        if len(unique_groups) == 2:
            g1_data = sub_df[sub_df[group_col] == unique_groups[0]]
            g2_data = sub_df[sub_df[group_col] == unique_groups[1]]
            lr = logrank_test(g1_data[duration_col], g2_data[duration_col],
                              event_observed_A=g1_data[event_col], event_observed_B=g2_data[event_col])
            results['logrank_stat'] = round(lr.test_statistic, 4)
            results['logrank_p'] = lr.p_value

    return results

def fit_linear_regression(df: pd.DataFrame, y_col: str, x_cols: List[str]) -> Dict[str, Any]:
    """Fit OLS linear regression and return formatted diagnostics."""
    sub_df = df[[y_col] + x_cols].dropna()
    X = sub_df[x_cols]
    X_const = sm.add_constant(X)
    y = sub_df[y_col]

    model = sm.OLS(y, X_const).fit()

    coef_df = pd.DataFrame({
        '係數 (Estimate)': model.params.round(4),
        '標準誤 (Std.Error)': model.bse.round(4),
        't 檢定值 (t-Stat)': model.tvalues.round(4),
        'p 值 (P>|t|)': [f"{p:.4e}" if p < 0.0001 else round(p, 4) for p in model.pvalues],
        '95% CI 下限': model.conf_int()[0].round(4),
        '95% CI 上限': model.conf_int()[1].round(4)
    })

    return {
        'r_squared': round(model.rsquared, 4),
        'adj_r_squared': round(model.rsquared_adj, 4),
        'f_statistic': round(model.fvalue, 4),
        'f_pvalue': model.f_pvalue,
        'coef_table': coef_df,
        'n_obs': int(model.nobs)
    }
