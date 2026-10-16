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
        return [pal[i % len(pal)] for i in range(n_colors)]
    else:
        return sns.color_palette(pal, n_colors).as_hex()

def setup_matplotlib_style(theme: str = "whitegrid", font_scale: float = 1.0, font_family: str = "sans-serif"):
    """Configure matplotlib/seaborn aesthetic style with multi-language and CJK font support."""
    sns.set_theme(style=theme, font=font_family, font_scale=font_scale)
    # Ensure Chinese and Unicode text glyphs display properly without tofu boxes
    plt.rcParams['font.sans-serif'] = [
        'Microsoft JhengHei', 'Microsoft YaHei', 'PingFang TC', 'SimHei',
        'Arial Unicode MS', 'DejaVu Sans', 'Arial', 'sans-serif'
    ]
    plt.rcParams['axes.unicode_minus'] = False

def apply_plot_customizations(ax, fig, title: str = "", xlabel: str = "", ylabel: str = "",
                               title_fontsize: int = 14, label_fontsize: int = 12,
                               xtick_fontsize: int = 10, ytick_fontsize: int = 10,
                               tick_rotation: int = 0, show_grid: bool = True,
                               despine: bool = True,
                               xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                               ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                               xscale: str = 'linear', yscale: str = 'linear',
                               is_x_categorical: bool = False):
    """Apply comprehensive title, label, scale limits, tick sizes, and axis scaling customizations with text x-axis support."""
    if title:
        ax.set_title(title, fontsize=title_fontsize, pad=12, fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=label_fontsize, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=label_fontsize, labelpad=8)
    
    # Scale adjustment: Only apply log scale if NOT categorical
    if not is_x_categorical and xscale == 'log':
        try:
            ax.set_xscale('log')
        except Exception:
            pass

    if yscale in ['linear', 'log']:
        try:
            ax.set_yscale(yscale)
        except Exception:
            pass

    # Axis Limits: Only apply xlim if X is continuous numeric
    if not is_x_categorical and xlim is not None:
        xmin, xmax = xlim
        if xmin is not None and xmax is not None and xmin < xmax:
            ax.set_xlim(xmin, xmax)
        elif xmin is not None:
            ax.set_xlim(left=xmin)
        elif xmax is not None:
            ax.set_xlim(right=xmax)

    if ylim is not None:
        ymin, ymax = ylim
        if ymin is not None and ymax is not None and ymin < ymax:
            ax.set_ylim(ymin, ymax)
        elif ymin is not None:
            ax.set_ylim(bottom=ymin)
        elif ymax is not None:
            ax.set_ylim(top=ymax)

    # Tick formatting & font sizes for text X-axis
    if tick_rotation != 0:
        plt.setp(ax.get_xticklabels(), rotation=tick_rotation,
                 ha='right' if tick_rotation > 0 else 'center',
                 rotation_mode='anchor',
                 fontsize=xtick_fontsize, visible=True)
    else:
        plt.setp(ax.get_xticklabels(), rotation=0, ha='center',
                 fontsize=xtick_fontsize, visible=True)

    plt.setp(ax.get_yticklabels(), fontsize=ytick_fontsize, visible=True)
    
    ax.grid(show_grid, linestyle='--', alpha=0.5)
    if despine:
        sns.despine(ax=ax, top=True, right=True)
        
    try:
        fig.tight_layout()
    except Exception:
        pass

def generate_customization_code_lines(title: str, xlabel: str, ylabel: str,
                                      title_fontsize: int, label_fontsize: int,
                                      xtick_fontsize: int, ytick_fontsize: int,
                                      tick_rotation: int, show_grid: bool,
                                      xlim: Optional[Tuple[Optional[float], Optional[float]]],
                                      ylim: Optional[Tuple[Optional[float], Optional[float]]],
                                      xscale: str, yscale: str,
                                      is_x_categorical: bool = False) -> List[str]:
    """Helper to generate Python snippet for reproducibility."""
    lines = []
    if title:
        lines.append(f"plt.title({repr(title)}, fontsize={title_fontsize}, fontweight='bold')")
    if xlabel:
        lines.append(f"plt.xlabel({repr(xlabel)}, fontsize={label_fontsize})")
    if ylabel:
        lines.append(f"plt.ylabel({repr(ylabel)}, fontsize={label_fontsize})")
    if not is_x_categorical and xscale == 'log':
        lines.append("plt.xscale('log')")
    if yscale == 'log':
        lines.append("plt.yscale('log')")
    if not is_x_categorical and xlim and (xlim[0] is not None or xlim[1] is not None):
        lines.append(f"plt.xlim({xlim[0]}, {xlim[1]})")
    if ylim and (ylim[0] is not None or ylim[1] is not None):
        lines.append(f"plt.ylim({ylim[0]}, {ylim[1]})")
    if tick_rotation != 0:
        lines.append(f"plt.xticks(rotation={tick_rotation}, ha='right', fontsize={xtick_fontsize})")
    else:
        lines.append(f"plt.xticks(rotation=0, ha='center', fontsize={xtick_fontsize})")
    lines.append(f"plt.yticks(fontsize={ytick_fontsize})")
    lines.append(f"plt.grid({show_grid}, linestyle='--', alpha=0.5)")
    lines.append("plt.tight_layout()")
    lines.append("plt.show()")
    return lines

def fig_to_bytes(fig, format: str = 'png', dpi: int = 300) -> bytes:
    """Convert a Matplotlib figure into bytes for downloading."""
    buf = io.BytesIO()
    fig.savefig(buf, format=format, dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()

# ==============================================================================
# 1. Boxplot / Violin + Jitter Plot (Group Comparison with Text X-axis)
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
                                   title_fontsize: int = 14,
                                   label_fontsize: int = 12,
                                   xtick_fontsize: int = 10,
                                   ytick_fontsize: int = 10,
                                   tick_rotation: int = 0,
                                   show_grid: bool = True,
                                   xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                                   ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                                   xscale: str = 'linear',
                                   yscale: str = 'linear',
                                   box_alpha: float = 0.8,
                                   jitter_alpha: float = 0.6,
                                   jitter_size: float = 5.0,
                                   show_points: bool = True) -> Tuple[plt.Figure, str]:
    """Generate Boxplot, Violin, or Strip plot with text X-axis group comparisons."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    colors = get_color_list(palette_name)
    sub_df = df.dropna(subset=[x_col, y_col] + ([hue_col] if hue_col else [])).copy()
    # Explicitly ensure X is treated as string text
    sub_df[x_col] = sub_df[x_col].astype(str)
    
    code_lines = [
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "",
        f"plt.figure(figsize={figsize}, dpi={dpi})",
        f"sub_df = df.dropna(subset=['{x_col}', '{y_col}']).copy()",
        f"sub_df['{x_col}'] = sub_df['{x_col}'].astype(str)"
    ]

    if "Boxplot" in plot_type:
        if hue_col:
            sns.boxplot(data=sub_df, x=x_col, y=y_col, hue=hue_col,
                        palette=colors, ax=ax, boxprops=dict(alpha=box_alpha),
                        fliersize=0 if show_points else 3)
            code_lines.append(f"sns.boxplot(data=sub_df, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, palette='{palette_name}', boxprops=dict(alpha={box_alpha}))")
        else:
            sns.boxplot(data=sub_df, x=x_col, y=y_col, hue=x_col,
                        palette=colors, ax=ax, legend=False, boxprops=dict(alpha=box_alpha),
                        fliersize=0 if show_points else 3)
            code_lines.append(f"sns.boxplot(data=sub_df, x='{x_col}', y='{y_col}', hue='{x_col}', palette='{palette_name}', legend=False, boxprops=dict(alpha={box_alpha}))")
    elif "Violin" in plot_type:
        if hue_col:
            sns.violinplot(data=sub_df, x=x_col, y=y_col, hue=hue_col,
                           palette=colors, ax=ax, cut=0, inner="quartile",
                           alpha=box_alpha)
            code_lines.append(f"sns.violinplot(data=sub_df, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, palette='{palette_name}', cut=0, inner='quartile')")
        else:
            sns.violinplot(data=sub_df, x=x_col, y=y_col, hue=x_col,
                           palette=colors, ax=ax, cut=0, inner="quartile",
                           legend=False, alpha=box_alpha)
            code_lines.append(f"sns.violinplot(data=sub_df, x='{x_col}', y='{y_col}', hue='{x_col}', palette='{palette_name}', legend=False, cut=0, inner='quartile')")
    
    if show_points and ("Jitter" in plot_type or plot_type == "Strip Plot Only"):
        if hue_col:
            sns.stripplot(data=sub_df, x=x_col, y=y_col, hue=hue_col,
                          palette=colors, ax=ax, jitter=0.25, size=jitter_size, alpha=jitter_alpha,
                          dodge=True)
            code_lines.append(f"sns.stripplot(data=sub_df, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, jitter=0.25, size={jitter_size}, alpha={jitter_alpha}, dodge=True)")
        else:
            sns.stripplot(data=sub_df, x=x_col, y=y_col, color='#222222',
                          ax=ax, jitter=0.25, size=jitter_size, alpha=jitter_alpha)
            code_lines.append(f"sns.stripplot(data=sub_df, x='{x_col}', y='{y_col}', color='#222222', jitter=0.25, size={jitter_size}, alpha={jitter_alpha})")

    apply_plot_customizations(ax, fig, title=title or f"{y_col} across {x_col}",
                              xlabel=xlabel or x_col, ylabel=ylabel or y_col,
                              title_fontsize=title_fontsize, label_fontsize=label_fontsize,
                              xtick_fontsize=xtick_fontsize, ytick_fontsize=ytick_fontsize,
                              tick_rotation=tick_rotation, show_grid=show_grid,
                              xlim=None, ylim=ylim, xscale='linear', yscale=yscale,
                              is_x_categorical=True)
    
    code_lines.extend(generate_customization_code_lines(
        title or f"{y_col} across {x_col}", xlabel or x_col, ylabel or y_col,
        title_fontsize, label_fontsize, xtick_fontsize, ytick_fontsize,
        tick_rotation, show_grid, None, ylim, 'linear', yscale, is_x_categorical=True
    ))
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
                         xlabel: str = "",
                         ylabel: str = "",
                         title_fontsize: int = 14,
                         label_fontsize: int = 12,
                         xtick_fontsize: int = 10,
                         ytick_fontsize: int = 10,
                         tick_rotation: int = 0,
                         show_grid: bool = True,
                         xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                         ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                         xscale: str = 'linear',
                         yscale: str = 'linear',
                         show_ci: bool = True,
                         show_median: bool = True) -> Tuple[plt.Figure, str]:
    """Generate publication-ready Kaplan-Meier survival curves using lifelines."""
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test
    
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    
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
        final_title = (title or "Kaplan-Meier Survival Analysis") + p_val_text
    else:
        kmf.fit(sub_df[time_col], sub_df[event_col], label=f"All Patients (N={len(sub_df)})")
        kmf.plot_survival_function(ax=ax, ci_show=show_ci, color=colors[0], linewidth=2.2)
        final_title = title or "Kaplan-Meier Survival Analysis"
    
    apply_plot_customizations(ax, fig, title=final_title,
                              xlabel=xlabel or f"Time ({time_col})",
                              ylabel=ylabel or "Cumulative Survival Probability",
                              title_fontsize=title_fontsize, label_fontsize=label_fontsize,
                              xtick_fontsize=xtick_fontsize, ytick_fontsize=ytick_fontsize,
                              tick_rotation=tick_rotation, show_grid=show_grid,
                              xlim=xlim, ylim=ylim if ylim else (-0.02, 1.05),
                              xscale=xscale, yscale=yscale,
                              is_x_categorical=False)
    
    code_lines = [
        "import matplotlib.pyplot as plt",
        "from lifelines import KaplanMeierFitter",
        f"plt.figure(figsize={figsize}, dpi={dpi})",
        f"sub_df = df.dropna(subset=['{time_col}', '{event_col}'])",
        "kmf = KaplanMeierFitter()",
        "# Loop through groups and plot survival curves"
    ]
    code_lines.extend(generate_customization_code_lines(
        final_title, xlabel or f"Time ({time_col})", ylabel or "Cumulative Survival Probability",
        title_fontsize, label_fontsize, xtick_fontsize, ytick_fontsize,
        tick_rotation, show_grid, xlim, ylim, xscale, yscale, is_x_categorical=False
    ))
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
                        xlabel: str = "",
                        ylabel: str = "",
                        title_fontsize: int = 14,
                        label_fontsize: int = 12,
                        xtick_fontsize: int = 10,
                        ytick_fontsize: int = 10,
                        tick_rotation: int = 0,
                        show_grid: bool = True,
                        xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                        ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                        xscale: str = 'linear',
                        yscale: str = 'linear',
                        top_genes: int = 8) -> Tuple[plt.Figure, str]:
    """Generate high-impact genomics Volcano Plot with threshold lines and gene labels."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    sub = df.dropna(subset=[log2fc_col, pval_col]).copy()
    sub[pval_col] = sub[pval_col].replace(0, 1e-300)
    sub['neg_log10_p'] = -np.log10(sub[pval_col])
    
    conditions = [
        (sub[log2fc_col] >= fc_threshold) & (sub[pval_col] < pval_threshold),
        (sub[log2fc_col] <= -fc_threshold) & (sub[pval_col] < pval_threshold)
    ]
    sub['regulation'] = np.select(conditions, ['Up-regulated', 'Down-regulated'], default='Not Significant')
    
    palette_map = {
        'Up-regulated': '#E64B35',
        'Down-regulated': '#3C5488',
        'Not Significant': '#BCBDC0'
    }
    
    sns.scatterplot(data=sub, x=log2fc_col, y='neg_log10_p', hue='regulation',
                    palette=palette_map, alpha=0.75, s=35, ax=ax, edgecolor='none')
    
    neg_p_thresh = -np.log10(pval_threshold)
    ax.axhline(neg_p_thresh, color='#555555', linestyle='--', linewidth=1.0, alpha=0.7)
    ax.axvline(fc_threshold, color='#555555', linestyle='--', linewidth=1.0, alpha=0.7)
    ax.axvline(-fc_threshold, color='#555555', linestyle='--', linewidth=1.0, alpha=0.7)
    
    if gene_col and gene_col in sub.columns and top_genes > 0:
        sig_genes = sub[sub['regulation'] != 'Not Significant'].sort_values('neg_log10_p', ascending=False).head(top_genes)
        for _, row in sig_genes.iterrows():
            ax.annotate(str(row[gene_col]),
                        (row[log2fc_col], row['neg_log10_p']),
                        xytext=(4, 4), textcoords='offset points',
                        fontsize=8, fontweight='bold', alpha=0.9)
    
    n_up = (sub['regulation'] == 'Up-regulated').sum()
    n_down = (sub['regulation'] == 'Down-regulated').sum()
    final_title = f"{title or 'Volcano Plot'}\n(Up: {n_up}, Down: {n_down})"
    
    apply_plot_customizations(ax, fig, title=final_title,
                              xlabel=xlabel or f"Log2 Fold Change ({log2fc_col})",
                              ylabel=ylabel or f"-Log10 P-value ({pval_col})",
                              title_fontsize=title_fontsize, label_fontsize=label_fontsize,
                              xtick_fontsize=xtick_fontsize, ytick_fontsize=ytick_fontsize,
                              tick_rotation=tick_rotation, show_grid=show_grid,
                              xlim=xlim, ylim=ylim, xscale=xscale, yscale=yscale,
                              is_x_categorical=False)
    ax.legend(title="", frameon=True, loc='upper right')
    
    code_lines = [
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        f"plt.figure(figsize={figsize}, dpi={dpi})"
    ]
    code_lines.extend(generate_customization_code_lines(
        final_title, xlabel or f"Log2 Fold Change ({log2fc_col})", ylabel or f"-Log10 P-value ({pval_col})",
        title_fontsize, label_fontsize, xtick_fontsize, ytick_fontsize,
        tick_rotation, show_grid, xlim, ylim, xscale, yscale, is_x_categorical=False
    ))
    return fig, "\n".join(code_lines)

# ==============================================================================
# 4. Correlation Heatmap
# ==============================================================================
def create_correlation_heatmap(df: pd.DataFrame, columns: List[str],
                               method: str = "pearson",
                               palette_name: str = "Coolwarm",
                               figsize: Tuple[float, float] = (8.0, 7.0),
                               dpi: int = 300,
                               annot: bool = True,
                               title: str = "Correlation Heatmap",
                               title_fontsize: int = 14,
                               xtick_fontsize: int = 10,
                               ytick_fontsize: int = 10,
                               tick_rotation: int = 45) -> Tuple[plt.Figure, str]:
    """Generate correlation matrix heatmap with annotated coefficients and text labels."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    corr = df[columns].corr(method=method)
    cmap = "coolwarm" if palette_name == "Coolwarm" else (palette_name if isinstance(PALETTES.get(palette_name), str) else "vlag")
    
    sns.heatmap(corr, annot=annot, fmt=".2f", cmap=cmap, vmin=-1, vmax=1,
                center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title(f"{title} ({method.capitalize()})", fontsize=title_fontsize, fontweight='bold', pad=12)
    plt.setp(ax.get_xticklabels(), rotation=tick_rotation, ha='right', rotation_mode='anchor', fontsize=xtick_fontsize)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=ytick_fontsize)
    fig.tight_layout()
    
    code = f"""import matplotlib.pyplot as plt
import seaborn as sns

cols = {repr(columns)}
corr = df[cols].corr(method='{method}')
plt.figure(figsize={figsize}, dpi={dpi})
sns.heatmap(corr, annot={annot}, fmt='.2f', cmap='{cmap}', vmin=-1, vmax=1, center=0, square=True, linewidths=0.5)
plt.title('{title} ({method.capitalize()})', fontsize={title_fontsize}, fontweight='bold')
plt.xticks(rotation={tick_rotation}, ha='right', fontsize={xtick_fontsize})
plt.yticks(fontsize={ytick_fontsize})
plt.tight_layout()
plt.show()"""
    return fig, code

# ==============================================================================
# 5. Scatter Plot with Regression (or Categorical Strip Plot if X is Text)
# ==============================================================================
def create_scatter_regression_plot(df: pd.DataFrame, x_col: str, y_col: str,
                                   hue_col: Optional[str] = None,
                                   palette_name: str = "Nature (NPG)",
                                   figsize: Tuple[float, float] = (8.0, 6.0),
                                   dpi: int = 300,
                                   title: str = "",
                                   xlabel: str = "",
                                   ylabel: str = "",
                                   title_fontsize: int = 14,
                                   label_fontsize: int = 12,
                                   xtick_fontsize: int = 10,
                                   ytick_fontsize: int = 10,
                                   tick_rotation: int = 0,
                                   show_grid: bool = True,
                                   xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                                   ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                                   xscale: str = 'linear',
                                   yscale: str = 'linear',
                                   show_ci: bool = True) -> Tuple[plt.Figure, str]:
    """Generate scatter plot with OLS linear regression fit, or categorical scatter if X is text."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    sub = df.dropna(subset=[x_col, y_col] + ([hue_col] if hue_col else [])).copy()
    
    is_x_numeric = pd.api.types.is_numeric_dtype(sub[x_col])
    
    code_lines = [
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        f"plt.figure(figsize={figsize}, dpi={dpi})"
    ]

    if is_x_numeric:
        if hue_col:
            sns.scatterplot(data=sub, x=x_col, y=y_col, hue=hue_col, palette=colors, ax=ax, alpha=0.7, s=40)
            sns.regplot(data=sub, x=x_col, y=y_col, scatter=False, ax=ax, color='#333333', ci=95 if show_ci else None,
                        line_kws={'linewidth': 1.8, 'linestyle': '--'})
        else:
            sns.regplot(data=sub, x=x_col, y=y_col, ax=ax, color=colors[0], ci=95 if show_ci else None,
                        scatter_kws={'alpha': 0.7, 's': 40}, line_kws={'linewidth': 2.0})
        code_lines.append(f"sns.regplot(data=df, x='{x_col}', y='{y_col}', ci={95 if show_ci else 'None'})")
    else:
        # Categorical text on X axis
        sub[x_col] = sub[x_col].astype(str)
        sns.stripplot(data=sub, x=x_col, y=y_col, hue=hue_col, palette=colors, ax=ax, alpha=0.7, size=6, jitter=0.25)
        # Add mean line per category
        means = sub.groupby(x_col)[y_col].mean()
        ax.scatter(range(len(means)), means.values, color='#E64B35', marker='D', s=50, zorder=5, label='Category Mean')
        code_lines.append(f"sns.stripplot(data=sub, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, jitter=0.25)")
        
    apply_plot_customizations(ax, fig, title=title or f"{y_col} vs {x_col}",
                              xlabel=xlabel or x_col, ylabel=ylabel or y_col,
                              title_fontsize=title_fontsize, label_fontsize=label_fontsize,
                              xtick_fontsize=xtick_fontsize, ytick_fontsize=ytick_fontsize,
                              tick_rotation=tick_rotation, show_grid=show_grid,
                              xlim=None if not is_x_numeric else xlim, ylim=ylim,
                              xscale='linear' if not is_x_numeric else xscale, yscale=yscale,
                              is_x_categorical=not is_x_numeric)
    
    code_lines.extend(generate_customization_code_lines(
        title or f"{y_col} vs {x_col}", xlabel or x_col, ylabel or y_col,
        title_fontsize, label_fontsize, xtick_fontsize, ytick_fontsize,
        tick_rotation, show_grid, None if not is_x_numeric else xlim, ylim,
        'linear' if not is_x_numeric else xscale, yscale, is_x_categorical=not is_x_numeric
    ))
    return fig, "\n".join(code_lines)

# ==============================================================================
# 6. Bar Plot with Error Bars (Mean ± SEM / SD with Text X-axis)
# ==============================================================================
def create_bar_error_plot(df: pd.DataFrame, x_col: str, y_col: str,
                          hue_col: Optional[str] = None,
                          errorbar: str = "se",
                          palette_name: str = "Nature (NPG)",
                          figsize: Tuple[float, float] = (8.0, 6.0),
                          dpi: int = 300,
                          title: str = "",
                          xlabel: str = "",
                          ylabel: str = "",
                          title_fontsize: int = 14,
                          label_fontsize: int = 12,
                          xtick_fontsize: int = 10,
                          ytick_fontsize: int = 10,
                          tick_rotation: int = 0,
                          show_grid: bool = True,
                          xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                          ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                          xscale: str = 'linear',
                          yscale: str = 'linear') -> Tuple[plt.Figure, str]:
    """Generate scientific bar chart with error bars and clear text labels on X-axis."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    sub = df.dropna(subset=[x_col, y_col] + ([hue_col] if hue_col else [])).copy()
    sub[x_col] = sub[x_col].astype(str)
    
    if hue_col:
        sns.barplot(data=sub, x=x_col, y=y_col, hue=hue_col, palette=colors,
                    errorbar=errorbar, capsize=0.15, err_kws={'linewidth': 1.5}, ax=ax, alpha=0.9)
    else:
        sns.barplot(data=sub, x=x_col, y=y_col, hue=x_col, palette=colors, legend=False,
                    errorbar=errorbar, capsize=0.15, err_kws={'linewidth': 1.5}, ax=ax, alpha=0.9)
    
    eb_label = "Mean ± SEM" if errorbar == "se" else "Mean ± SD"
    apply_plot_customizations(ax, fig, title=title or f"{y_col} by {x_col} ({eb_label})",
                              xlabel=xlabel or x_col, ylabel=ylabel or f"{y_col} ({eb_label})",
                              title_fontsize=title_fontsize, label_fontsize=label_fontsize,
                              xtick_fontsize=xtick_fontsize, ytick_fontsize=ytick_fontsize,
                              tick_rotation=tick_rotation, show_grid=show_grid,
                              xlim=None, ylim=ylim, xscale='linear', yscale=yscale,
                              is_x_categorical=True)
    
    code_lines = [
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        f"plt.figure(figsize={figsize}, dpi={dpi})",
        f"sub = df.copy(); sub['{x_col}'] = sub['{x_col}'].astype(str)",
        f"sns.barplot(data=sub, x='{x_col}', y='{y_col}', hue={repr(hue_col)}, errorbar='{errorbar}', capsize=0.15)"
    ]
    code_lines.extend(generate_customization_code_lines(
        title or f"{y_col} by {x_col}", xlabel or x_col, ylabel or f"{y_col} ({eb_label})",
        title_fontsize, label_fontsize, xtick_fontsize, ytick_fontsize,
        tick_rotation, show_grid, None, ylim, 'linear', yscale, is_x_categorical=True
    ))
    return fig, "\n".join(code_lines)

# ==============================================================================
# 7. Distribution / Histogram & KDE (Supports Text/Categorical or Numeric X-axis)
# ==============================================================================
def create_distribution_plot(df: pd.DataFrame, col: str,
                             hue_col: Optional[str] = None,
                             bins: int = 25,
                             show_kde: bool = True,
                             palette_name: str = "Nature (NPG)",
                             figsize: Tuple[float, float] = (8.0, 5.5),
                             dpi: int = 300,
                             title: str = "",
                             xlabel: str = "",
                             ylabel: str = "",
                             title_fontsize: int = 14,
                             label_fontsize: int = 12,
                             xtick_fontsize: int = 10,
                             ytick_fontsize: int = 10,
                             tick_rotation: int = 0,
                             show_grid: bool = True,
                             xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                             ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                             xscale: str = 'linear',
                             yscale: str = 'linear') -> Tuple[plt.Figure, str]:
    """Generate distribution histogram for numeric data, or frequency bar plot for text/categorical data."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    colors = get_color_list(palette_name)
    sub = df.dropna(subset=[col] + ([hue_col] if hue_col else [])).copy()
    
    is_numeric = pd.api.types.is_numeric_dtype(sub[col])
    
    code_lines = [
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        f"plt.figure(figsize={figsize}, dpi={dpi})"
    ]

    if is_numeric:
        sns.histplot(data=sub, x=col, hue=hue_col, bins=bins, kde=show_kde,
                     palette=colors, ax=ax, alpha=0.6, stat="density", common_norm=False)
        code_lines.append(f"sns.histplot(data=df, x='{col}', hue={repr(hue_col)}, bins={bins}, kde={show_kde}, stat='density')")
    else:
        # Category count plot showing text labels on X
        sub[col] = sub[col].astype(str)
        sns.countplot(data=sub, x=col, hue=hue_col, palette=colors, ax=ax, alpha=0.85)
        # annotate counts
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f"{int(height)}", (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=xtick_fontsize, xytext=(0, 3),
                            textcoords='offset points')
        code_lines.append(f"sub['{col}'] = sub['{col}'].astype(str)")
        code_lines.append(f"sns.countplot(data=sub, x='{col}', hue={repr(hue_col)})")
    
    apply_plot_customizations(ax, fig, title=title or f"Distribution of {col}",
                              xlabel=xlabel or col, ylabel=ylabel or ("Density" if is_numeric else "Count (頻次)"),
                              title_fontsize=title_fontsize, label_fontsize=label_fontsize,
                              xtick_fontsize=xtick_fontsize, ytick_fontsize=ytick_fontsize,
                              tick_rotation=tick_rotation, show_grid=show_grid,
                              xlim=None if not is_numeric else xlim, ylim=ylim,
                              xscale='linear' if not is_numeric else xscale, yscale=yscale,
                              is_x_categorical=not is_numeric)
    
    code_lines.extend(generate_customization_code_lines(
        title or f"Distribution of {col}", xlabel or col, ylabel or ("Density" if is_numeric else "Count"),
        title_fontsize, label_fontsize, xtick_fontsize, ytick_fontsize,
        tick_rotation, show_grid, None if not is_numeric else xlim, ylim,
        'linear' if not is_numeric else xscale, yscale, is_x_categorical=not is_numeric
    ))
    return fig, "\n".join(code_lines)

# ==============================================================================
# 8. PCA Biplot (Unsupervised Clustering)
# ==============================================================================
def create_pca_plot(df: pd.DataFrame, feature_cols: List[str],
                    label_col: Optional[str] = None,
                    palette_name: str = "Nature (NPG)",
                    figsize: Tuple[float, float] = (8.0, 6.0),
                    dpi: int = 300,
                    title: str = "PCA Projection",
                    xlabel: str = "",
                    ylabel: str = "",
                    title_fontsize: int = 14,
                    label_fontsize: int = 12,
                    xtick_fontsize: int = 10,
                    ytick_fontsize: int = 10,
                    tick_rotation: int = 0,
                    show_grid: bool = True,
                    xlim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                    ylim: Optional[Tuple[Optional[float], Optional[float]]] = None,
                    xscale: str = 'linear',
                    yscale: str = 'linear') -> Tuple[plt.Figure, str]:
    """Perform PCA and generate 2D score plot with explained variance ratios."""
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    sub = df[feature_cols + ([label_col] if label_col else [])].dropna()
    X = sub[feature_cols].values
    X_std = (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-9)
    
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
    
    apply_plot_customizations(ax, fig, title=title,
                              xlabel=xlabel or f"PC1 ({ratios[0]:.1f}% variance)",
                              ylabel=ylabel or f"PC2 ({ratios[1]:.1f}% variance)",
                              title_fontsize=title_fontsize, label_fontsize=label_fontsize,
                              xtick_fontsize=xtick_fontsize, ytick_fontsize=ytick_fontsize,
                              tick_rotation=tick_rotation, show_grid=show_grid,
                              xlim=xlim, ylim=ylim, xscale=xscale, yscale=yscale,
                              is_x_categorical=False)
    
    code_lines = [
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        f"plt.figure(figsize={figsize}, dpi={dpi})"
    ]
    code_lines.extend(generate_customization_code_lines(
        title, xlabel or f"PC1 ({ratios[0]:.1f}% variance)", ylabel or f"PC2 ({ratios[1]:.1f}% variance)",
        title_fontsize, label_fontsize, xtick_fontsize, ytick_fontsize,
        tick_rotation, show_grid, xlim, ylim, xscale, yscale, is_x_categorical=False
    ))
    return fig, "\n".join(code_lines)
