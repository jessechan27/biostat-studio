import sys
import io
import traceback
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, Any, Tuple, Optional

# Pre-defined advanced scientific visualization templates
CODE_TEMPLATES = {
    "Seaborn Clustermap (層級分群熱圖)": """# 層級分群熱圖 (Hierarchical Clustermap)
# 請確認 df 含有數值型變項
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:8]
sub_df = df[numeric_cols].dropna()

# 繪製分群熱圖 (z-score 標準化)
g = sns.clustermap(sub_df, standard_scale=1, cmap="vlag", figsize=(8, 8), dendrogram_ratio=(.15, .15), cbar_pos=(0.02, 0.8, 0.04, 0.18))
g.fig.suptitle("Hierarchical Clustermap (Z-Score Standardized)", y=1.02, fontsize=14, fontweight='bold')
fig = g.fig
""",

    "Seaborn PairGrid / Pairplot (多變量矩陣圖)": """# 多變量散佈與密度矩陣 (Pairplot)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:4]
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
hue_col = cat_cols[0] if len(cat_cols) > 0 else None

g = sns.pairplot(df.dropna(subset=numeric_cols), vars=numeric_cols, hue=hue_col, palette="tab10", diag_kind="kde", corner=True)
g.fig.suptitle("Multivariate Pairwise Distribution", y=1.02, fontsize=14, fontweight='bold')
fig = g.fig
""",

    "FacetGrid 多分面小提琴圖 (FacetGrid Multi-panel)": """# 多分面小提琴與分佈圖 (FacetGrid)
num_col = df.select_dtypes(include=[np.number]).columns.tolist()[0]
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
group_col = cat_cols[0] if len(cat_cols) > 0 else None

fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
if group_col:
    sns.violinplot(data=df, x=group_col, y=num_col, palette="Set2", inner="box", ax=ax)
    sns.stripplot(data=df, x=group_col, y=num_col, color="black", alpha=0.4, jitter=0.2, ax=ax)
else:
    sns.violinplot(data=df, y=num_col, color="#4DBBD5", ax=ax)

ax.set_title(f"Distribution of {num_col}", fontsize=14, fontweight='bold', pad=10)
plt.tight_layout()
""",

    "Lollipop Chart (棒棒糖圖 - 適合均值排名)": """# 棒棒糖圖 (Lollipop Chart) - 適合多組別均值比較
cat_col = df.select_dtypes(include=['object', 'category']).columns.tolist()[0]
num_col = df.select_dtypes(include=[np.number]).columns.tolist()[0]

summary = df.groupby(cat_col)[num_col].mean().reset_index().sort_values(num_col)

fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
ax.hlines(y=summary[cat_col], xmin=0, xmax=summary[num_col], color='#00468B', alpha=0.7, linewidth=2)
ax.scatter(summary[num_col], summary[cat_col], color='#ED0000', s=100, alpha=1, zorder=3)

ax.set_title(f"Mean {num_col} by {cat_col}", fontsize=13, fontweight='bold')
ax.set_xlabel(f"Average {num_col}")
ax.grid(axis='x', linestyle='--', alpha=0.5)
sns.despine(top=True, right=True)
plt.tight_layout()
""",

    "3D 散佈圖 (Matplotlib 3D Scatter)": """# 3D 散佈圖 (3D Scatter Plot)
from mpl_toolkits.mplot3d import Axes3D
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if len(num_cols) >= 3:
    x_c, y_c, z_c = num_cols[0], num_cols[1], num_cols[2]
    fig = plt.figure(figsize=(8, 6), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(df[x_c], df[y_c], df[z_c], c=df[z_c], cmap='viridis', s=45, alpha=0.8, edgecolors='w')
    ax.set_xlabel(x_c)
    ax.set_ylabel(y_c)
    ax.set_zlabel(z_c)
    ax.set_title(f"3D Scatter: {x_c} vs {y_c} vs {z_c}", fontsize=13, fontweight='bold')
    fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=8, label=z_c)
    plt.tight_layout()
else:
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, "需要至少 3 個數值欄位", ha='center')
"""
}

def execute_user_plot_code(code_str: str, df: pd.DataFrame) -> Tuple[Optional[plt.Figure], str, Optional[str]]:
    """Execute custom user Python script in an isolated namespace and return the generated Figure, stdout, and error."""
    # Reset current matplotlib figure
    plt.close('all')
    
    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture
    
    env_namespace = {
        'pd': pd,
        'np': np,
        'plt': plt,
        'sns': sns,
        'stats': stats,
        'df': df.copy(),
        'fig': None
    }
    
    try:
        import lifelines
        env_namespace['lifelines'] = lifelines
    except ImportError:
        pass

    error_msg = None
    fig = None
    
    try:
        exec(code_str, env_namespace)
        
        # Check if user assigned `fig` variable
        if env_namespace.get('fig') is not None and isinstance(env_namespace['fig'], plt.Figure):
            fig = env_namespace['fig']
        else:
            # Otherwise grab current active figure
            fig = plt.gcf()
            if not fig.axes:
                # No axes plotted
                fig = None
    except Exception as e:
        error_msg = traceback.format_exc()
    finally:
        sys.stdout = old_stdout

    captured_out = stdout_capture.getvalue()
    return fig, captured_out, error_msg
