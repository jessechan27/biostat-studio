import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional, Tuple

# Scientific and journal color palettes
PALETTES = {
    "Nature (NPG)": ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4", "#91D1C2", "#DC0000", "#7E6148"],
    "Lancet": ["#00468B", "#ED0000", "#42B540", "#0099B4", "#925E9F", "#FDAF91", "#AD002A", "#ADB6B6"],
    "NEJM": ["#BC3C29", "#0072B5", "#E18727", "#20854E", "#7876B1", "#6F99AD", "#FFDC91", "#EE4C97"],
    "JAMA": ["#374E55", "#DF8F44", "#00A1D5", "#B24745", "#79AF97", "#6A6599", "#80796B"],
    "Viridis": "viridis",
    "Plasma": "plasma",
    "Mako": "mako",
    "Rocket": "rocket",
    "Set2 (Clean)": "Set2",
    "Dark2 (Contrasting)": "Dark2",
    "Pastel1": "Pastel1",
    "Spectral": "Spectral",
    "Coolwarm": "coolwarm"
}

def get_color_list(palette_name: str, n_colors: int = 8) -> List[str]:
    """Retrieve color hex codes for a given palette name."""
    pal = PALETTES.get(palette_name, "Set2")
    if isinstance(pal, list):
        if n_colors <= len(pal):
            return pal[:n_colors]
        # cycle if needed
        return [pal[i % len(pal)] for i in range(n_colors)]
    else:
        return sns.color_palette(pal, n_colors).as_hex()

def setup_matplotlib_style(theme: str = "whitegrid", font_scale: float = 1.0, font_family: str = "sans-serif"):
    """Configure matplotlib/seaborn aesthetic style."""
    sns.set_theme(style=theme, font=font_family, font_scale=font_scale)
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'Microsoft JhengHei', 'SimHei', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

def apply_plot_customizations(ax, fig, title: str = "", xlabel: str = "", ylabel: str = "",
                               title_fontsize: int = 14, label_fontsize: int = 12,
                               tick_rotation: int = 0, show_grid: bool = True,
                               despine: bool = True):
    """Apply standard title, label, tick, and spine customizations."""
    if title:
        ax.set_title(title, fontsize=title_fontsize, pad=12, fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=label_fontsize, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=label_fontsize, labelpad=8)
    
    if tick_rotation != 0:
        ax.tick_params(axis='x', rotation=tick_rotation)
    
    ax.grid(show_grid, linestyle='--', alpha=0.5)
    if despine:
        sns.despine(ax=ax, top=True, right=True)
    fig.tight_layout()

def fig_to_bytes(fig, format: str = 'png', dpi: int = 300) -> bytes:
    """Convert a Matplotlib figure into bytes for downloading."""
    buf = io.BytesIO()
    fig.savefig(buf, format=format, dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()

# ==============================================================================
# 1. Boxplot / Violin + Jitter Plot (Group Comparison)
# ==============================================================================
def create_group_distribution_plot(df: pd.DataFrame, x_col: str, y_col: str,
                                   hue_col: Optional[str] = None,
                                   plot_type: str = "Boxplot + Jitter",
                                   palette_name: str = "Nature (NPG)",
                                   figsize: Tuple[float, float] = (8.0, 6.0),
                                   dpi: int = 300,
                                   title: str = "",
                                   xlabel: str = "",
                                   ylabel: str = "",
                                   box_alpha: float = 0.8,
                                   jitter_alpha: float = 0.6,
                                   jitter_size: float = 5.0,
                                   show_points: bool = True) -> Tuple[plt.Figure, str]:
    """Generate Boxplot, Violin, or Strip plot with group comparisons."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    colors = get_color_list(palette_name)
    sub_df = df.dropna(subset=[x_col, y_col] + ([hue_col] if hue_col else []))
    
    code_lines = [
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "",
        "plt.figure(figsize=" + str(figsize) + ", dpi=" + str(dpi) + ")",
        f"sub_df = df.dropna(subset=['{x_col}', '{y_col}'])"
    ]

    if "Boxplot" in plot_type:
        sns.boxplot(data=sub_df, x=x_col, y=y_col, hue=hue_col,
                    palette=colors, ax=ax, boxprops=dict(alpha=box_alpha),
                    fliersize=0 if show_points else 3)
        code_lines.append(f"sns.boxplot(data=sub_df, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, palette='{palette_name}', boxprops=dict(alpha={box_alpha}))")
    elif "Violin" in plot_type:
        sns.violinplot(data=sub_df, x=x_col, y=y_col, hue=hue_col,
                       palette=colors, ax=ax, cut=0, inner="quartile",
                       alpha=box_alpha)
        code_lines.append(f"sns.violinplot(data=sub_df, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, palette='{palette_name}', cut=0, inner='quartile')")
    
    if show_points and ("Jitter" in plot_type or plot_type == "Strip Plot Only"):
        sns.stripplot(data=sub_df, x=x_col, y=y_col, hue=hue_col,
                      palette=['#222222'] if not hue_col else colors,
                      ax=ax, jitter=0.25, size=jitter_size, alpha=jitter_alpha,
                      dodge=True if hue_col else False)
        code_lines.append(f"sns.stripplot(data=sub_df, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, jitter=0.25, size={jitter_size}, alpha={jitter_alpha}, dodge={bool(hue_col)})")

    apply_plot_customizations(ax, fig, title=title or f"{y_col} across {x_col}",
                              xlabel=xlabel or x_col, ylabel=ylabel or y_col)
    
    code_lines.extend([
        f"plt.title('{title or f'{y_col} across {x_col}'}', fontsize=14, fontweight='bold')",
        f"plt.xlabel('{xlabel or x_col}')",
        f"plt.ylabel('{ylabel or y_col}')",
        "plt.tight_layout()",
        "plt.show()"
    ])
    
    return fig, "\n".join(code_lines)

# ==============================================================================
# 2. Kaplan-Meier Survival Curve
# ==============================================================================
def create_survival_plot(df: pd.DataFrame, time_col: str, event_col: str,
                         group_col: Optional[str] = None,
                         palette_name: str = "Nature (NPG)",
                         figsize: Tuple[float, float] = (8.5, 6.0),
                         dpi: int = 300,
                         title: str = "Kaplan-Meier Survival Analysis",
                         show_ci: bool = True,
                         show_median: bool = True) -> Tuple[plt.Figure, str]:
    """Generate publication-ready Kaplan-Meier survival curves using lifelines."""
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test
    
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    
    code_lines = [
        "import matplotlib.pyplot as plt",
        "from lifelines import KaplanMeierFitter",
        "from lifelines.statistics import logrank_test",
        "",
        "plt.figure(figsize=" + str(figsize) + ", dpi=" + str(dpi) + ")",
        f"sub_df = df.dropna(subset=['{time_col}', '{event_col}'])"
    ]
    
    sub_df = df.dropna(subset=[time_col, event_col])
    kmf = KaplanMeierFitter()
    
    if group_col and group_col in df.columns:
        groups = sub_df[group_col].unique()
        p_val_text = ""
        if len(groups) == 2:
            g1, g2 = groups[0], groups[1]
            d1 = sub_df[sub_df[group_col] == g1]
            d2 = sub_df[sub_df[group_col] == g2]
            lr = logrank_test(d1[time_col], d2[time_col], d1[event_col], d2[event_col])
            p_val_text = f" (Log-Rank p = {lr.p_value:.4f})" if lr.p_value >= 0.0001 else " (Log-Rank p < 0.0001)"

        for i, grp in enumerate(groups):
            grp_data = sub_df[sub_df[group_col] == grp]
            col = colors[i % len(colors)]
            kmf.fit(grp_data[time_col], grp_data[event_col], label=f"{grp} (N={len(grp_data)})")
            kmf.plot_survival_function(ax=ax, ci_show=show_ci, color=col, linewidth=2.0)
            if show_median and not np.isnan(kmf.median_survival_time_):
                med = kmf.median_survival_time_
                if not np.isinf(med):
                    ax.axvline(med, color=col, linestyle=':', alpha=0.6)
        
        ax.set_title(title + p_val_text, fontsize=13, fontweight='bold')
    else:
        kmf.fit(sub_df[time_col], sub_df[event_col], label=f"All Patients (N={len(sub_df)})")
        kmf.plot_survival_function(ax=ax, ci_show=show_ci, color=colors[0], linewidth=2.2)
        ax.set_title(title, fontsize=13, fontweight='bold')
    
    ax.set_xlabel(f"Time ({time_col})", fontsize=12)
    ax.set_ylabel("Cumulative Survival Probability", fontsize=12)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, linestyle='--', alpha=0.4)
    sns.despine(ax=ax)
    fig.tight_layout()
    
    code_lines.extend([
        "kmf = KaplanMeierFitter()",
        "# Loop through groups and plot survival curves",
        "plt.title('Kaplan-Meier Survival Curves')",
        f"plt.xlabel('Time ({time_col})')",
        "plt.ylabel('Survival Probability')",
        "plt.tight_layout()",
        "plt.show()"
    ])
    
    return fig, "\n".join(code_lines)

# ==============================================================================
# 3. Volcano Plot (Genomics / Differential Expression)
# ==============================================================================
def create_volcano_plot(df: pd.DataFrame, log2fc_col: str, pval_col: str,
                        gene_col: Optional[str] = None,
                        fc_threshold: float = 1.0,
                        pval_threshold: float = 0.05,
                        palette_name: str = "Nature (NPG)",
                        figsize: Tuple[float, float] = (8.5, 6.5),
                        dpi: int = 300,
                        title: str = "Volcano Plot (Differential Expression)",
                        top_genes: int = 8) -> Tuple[plt.Figure, str]:
    """Generate high-impact genomics Volcano Plot with threshold lines and gene labels."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    sub = df.dropna(subset=[log2fc_col, pval_col]).copy()
    # Avoid log(0)
    sub[pval_col] = sub[pval_col].replace(0, 1e-300)
    sub['neg_log10_p'] = -np.log10(sub[pval_col])
    
    # Classification
    conditions = [
        (sub[log2fc_col] >= fc_threshold) & (sub[pval_col] < pval_threshold),
        (sub[log2fc_col] <= -fc_threshold) & (sub[pval_col] < pval_threshold)
    ]
    sub['regulation'] = np.select(conditions, ['Up-regulated', 'Down-regulated'], default='Not Significant')
    
    palette_map = {
        'Up-regulated': '#E64B35',     # Red
        'Down-regulated': '#3C5488',   # Blue
        'Not Significant': '#BCBDC0'   # Gray
    }
    
    sns.scatterplot(data=sub, x=log2fc_col, y='neg_log10_p', hue='regulation',
                    palette=palette_map, alpha=0.75, s=35, ax=ax, edgecolor='none')
    
    # Threshold dashed lines
    neg_p_thresh = -np.log10(pval_threshold)
    ax.axhline(neg_p_thresh, color='#555555', linestyle='--', linewidth=1.0, alpha=0.7)
    ax.axvline(fc_threshold, color='#555555', linestyle='--', linewidth=1.0, alpha=0.7)
    ax.axvline(-fc_threshold, color='#555555', linestyle='--', linewidth=1.0, alpha=0.7)
    
    # Text annotation for top significant genes
    if gene_col and gene_col in sub.columns and top_genes > 0:
        sig_genes = sub[sub['regulation'] != 'Not Significant'].sort_values('neg_log10_p', ascending=False).head(top_genes)
        for _, row in sig_genes.iterrows():
            ax.annotate(str(row[gene_col]),
                        (row[log2fc_col], row['neg_log10_p']),
                        xytext=(4, 4), textcoords='offset points',
                        fontsize=8, fontweight='bold', alpha=0.9)
    
    n_up = (sub['regulation'] == 'Up-regulated').sum()
    n_down = (sub['regulation'] == 'Down-regulated').sum()
    ax.set_title(f"{title}\n(Up: {n_up}, Down: {n_down})", fontsize=13, fontweight='bold')
    ax.set_xlabel(f"Log2 Fold Change ({log2fc_col})", fontsize=11)
    ax.set_ylabel(f"-Log10 P-value ({pval_col})", fontsize=11)
    ax.legend(title="", frameon=True, loc='upper right')
    sns.despine(ax=ax)
    fig.tight_layout()
    
    code = f"""import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sub = df.dropna(subset=['{log2fc_col}', '{pval_col}']).copy()
sub['neg_log10_p'] = -np.log10(sub['{pval_col}'].replace(0, 1e-300))
sub['regulation'] = np.select([
    (sub['{log2fc_col}'] >= {fc_threshold}) & (sub['{pval_col}'] < {pval_threshold}),
    (sub['{log2fc_col}'] <= -{fc_threshold}) & (sub['{pval_col}'] < {pval_threshold})
], ['Up-regulated', 'Down-regulated'], default='Not Significant')

plt.figure(figsize={figsize}, dpi={dpi})
sns.scatterplot(data=sub, x='{log2fc_col}', y='neg_log10_p', hue='regulation',
                palette={{'Up-regulated': '#E64B35', 'Down-regulated': '#3C5488', 'Not Significant': '#BCBDC0'}},
                alpha=0.8, s=35)
plt.axhline(-np.log10({pval_threshold}), color='gray', linestyle='--')
plt.axvline({fc_threshold}, color='gray', linestyle='--')
plt.axvline(-{fc_threshold}, color='gray', linestyle='--')
plt.title('{title}', fontsize=14, fontweight='bold')
plt.xlabel('Log2 Fold Change')
plt.ylabel('-Log10 P-value')
plt.tight_layout()
plt.show()"""
    
    return fig, code

# ==============================================================================
# 4. Correlation Heatmap
# ==============================================================================
def create_correlation_heatmap(df: pd.DataFrame, columns: List[str],
                               method: str = "pearson",
                               palette_name: str = "Coolwarm",
                               figsize: Tuple[float, float] = (8.0, 7.0),
                               dpi: int = 300,
                               annot: bool = True,
                               title: str = "Correlation Heatmap") -> Tuple[plt.Figure, str]:
    """Generate correlation matrix heatmap with annotated coefficients."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    corr = df[columns].corr(method=method)
    cmap = "coolwarm" if palette_name == "Coolwarm" else (palette_name if isinstance(PALETTES.get(palette_name), str) else "vlag")
    
    sns.heatmap(corr, annot=annot, fmt=".2f", cmap=cmap, vmin=-1, vmax=1,
                center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title(f"{title} ({method.capitalize()})", fontsize=13, fontweight='bold', pad=12)
    fig.tight_layout()
    
    code = f"""import matplotlib.pyplot as plt
import seaborn as sns

cols = {repr(columns)}
corr = df[cols].corr(method='{method}')
plt.figure(figsize={figsize}, dpi={dpi})
sns.heatmap(corr, annot={annot}, fmt='.2f', cmap='{cmap}', vmin=-1, vmax=1, center=0, square=True, linewidths=0.5)
plt.title('{title} ({method.capitalize()})', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()"""
    return fig, code

# ==============================================================================
# 5. Scatter Plot with Regression and Confidence Intervals
# ==============================================================================
def create_scatter_regression_plot(df: pd.DataFrame, x_col: str, y_col: str,
                                   hue_col: Optional[str] = None,
                                   palette_name: str = "Nature (NPG)",
                                   figsize: Tuple[float, float] = (8.0, 6.0),
                                   dpi: int = 300,
                                   show_ci: bool = True,
                                   title: str = "") -> Tuple[plt.Figure, str]:
    """Generate scatter plot with OLS linear regression fit and confidence interval."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    sub = df.dropna(subset=[x_col, y_col] + ([hue_col] if hue_col else []))
    
    if hue_col:
        sns.scatterplot(data=sub, x=x_col, y=y_col, hue=hue_col, palette=colors, ax=ax, alpha=0.7, s=40)
        # fit overall regression line
        sns.regplot(data=sub, x=x_col, y=y_col, scatter=False, ax=ax, color='#333333', ci=95 if show_ci else None,
                    line_kws={'linewidth': 1.8, 'linestyle': '--'})
    else:
        sns.regplot(data=sub, x=x_col, y=y_col, ax=ax, color=colors[0], ci=95 if show_ci else None,
                    scatter_kws={'alpha': 0.7, 's': 40}, line_kws={'linewidth': 2.0})
        
    apply_plot_customizations(ax, fig, title=title or f"{y_col} vs {x_col}",
                              xlabel=x_col, ylabel=y_col)
    
    code = f"""import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize={figsize}, dpi={dpi})
sns.regplot(data=df, x='{x_col}', y='{y_col}', ci={95 if show_ci else 'None'})
plt.title('{title or f"{y_col} vs {x_col}"}', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()"""
    return fig, code

# ==============================================================================
# 6. Bar Plot with Error Bars (Mean ± SEM / SD)
# ==============================================================================
def create_bar_error_plot(df: pd.DataFrame, x_col: str, y_col: str,
                          hue_col: Optional[str] = None,
                          errorbar: str = "se",
                          palette_name: str = "Nature (NPG)",
                          figsize: Tuple[float, float] = (8.0, 6.0),
                          dpi: int = 300,
                          title: str = "") -> Tuple[plt.Figure, str]:
    """Generate scientific bar chart with error bars (Standard Error or SD)."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    
    sns.barplot(data=df, x=x_col, y=y_col, hue=hue_col, palette=colors,
                errorbar=errorbar, capsize=0.15, err_kws={'linewidth': 1.5}, ax=ax, alpha=0.9)
    
    eb_label = "Mean ± SEM" if errorbar == "se" else "Mean ± SD"
    apply_plot_customizations(ax, fig, title=title or f"{y_col} by {x_col} ({eb_label})",
                              xlabel=x_col, ylabel=f"{y_col} ({eb_label})")
    
    code = f"""import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize={figsize}, dpi={dpi})
sns.barplot(data=df, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, errorbar='{errorbar}', capsize=0.15)
plt.title('{title or f"{y_col} by {x_col}"}', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()"""
    return fig, code

# ==============================================================================
# 7. Distribution / Histogram & KDE
# ==============================================================================
def create_distribution_plot(df: pd.DataFrame, col: str,
                             hue_col: Optional[str] = None,
                             bins: int = 25,
                             show_kde: bool = True,
                             palette_name: str = "Nature (NPG)",
                             figsize: Tuple[float, float] = (8.0, 5.5),
                             dpi: int = 300,
                             title: str = "") -> Tuple[plt.Figure, str]:
    """Generate distribution histogram and Kernel Density Estimation."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    
    sns.histplot(data=df, x=col, hue=hue_col, bins=bins, kde=show_kde,
                 palette=colors, ax=ax, alpha=0.6, stat="density", common_norm=False)
    
    apply_plot_customizations(ax, fig, title=title or f"Distribution of {col}",
                              xlabel=col, ylabel="Density")
    
    code = f"""import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize={figsize}, dpi={dpi})
sns.histplot(data=df, x='{col}', hue={repr(hue_col)}, bins={bins}, kde={show_kde}, stat='density', common_norm=False)
plt.title('{title or f"Distribution of {col}"}', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()"""
    return fig, code

# ==============================================================================
# 8. PCA Biplot (Unsupervised Clustering)
# ==============================================================================
def create_pca_plot(df: pd.DataFrame, feature_cols: List[str],
                    label_col: Optional[str] = None,
                    palette_name: str = "Nature (NPG)",
                    figsize: Tuple[float, float] = (8.0, 6.0),
                    dpi: int = 300,
                    title: str = "PCA Projection") -> Tuple[plt.Figure, str]:
    """Perform PCA and generate 2D score plot with explained variance ratios."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # Standardize data
    sub = df[feature_cols + ([label_col] if label_col else [])].dropna()
    X = sub[feature_cols].values
    X_std = (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-9)
    
    # SVD for PCA
    U, S, Vt = np.linalg.svd(X_std, full_matrices=False)
    PCs = np.dot(X_std, Vt.T[:, :2])
    explained_variance = (S**2) / (len(X_std) - 1)
    total_var = np.sum(explained_variance)
    ratios = (explained_variance / total_var)[:2] * 100
    
    sub['PC1'] = PCs[:, 0]
    sub['PC2'] = PCs[:, 1]
    
    colors = get_color_list(palette_name)
    sns.scatterplot(data=sub, x='PC1', y='PC2', hue=label_col, palette=colors if label_col else None,
                    s=50, alpha=0.8, ax=ax)
    
    ax.set_xlabel(f"PC1 ({ratios[0]:.1f}% variance)", fontsize=12)
    ax.set_ylabel(f"PC2 ({ratios[1]:.1f}% variance)", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.4)
    sns.despine(ax=ax)
    fig.tight_layout()
    
    code = f"""import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sub = df[{repr(feature_cols)}].dropna()
X = sub.values
X_std = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
U, S, Vt = np.linalg.svd(X_std, full_matrices=False)
PCs = np.dot(X_std, Vt.T[:, :2])
sub['PC1'] = PCs[:, 0]
sub['PC2'] = PCs[:, 1]

plt.figure(figsize={figsize}, dpi={dpi})
sns.scatterplot(data=sub, x='PC1', y='PC2', hue={repr(label_col)}, s=50, alpha=0.8)
plt.title('{title}', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()"""
    return fig, code
