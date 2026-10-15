import sys
import io
import traceback
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, Any

def execute_custom_python_code(code_str: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Safely execute user-provided Python Seaborn/Matplotlib code in an isolated scope.
    Captures stdout, output figure (fig), and any exceptions.
    """
    # Clear any previous matplotlib state
    plt.close('all')

    # Setup execution environment
    stdout_capture = io.StringIO()
    original_stdout = sys.stdout

    local_scope = {
        'df': df.copy(),
        'pd': pd,
        'np': np,
        'plt': plt,
        'sns': sns,
        'matplotlib': matplotlib,
        'fig': None,
        'ax': None
    }

    # Pre-populate optional libraries if available
    try:
        import scipy
        from scipy import stats
        local_scope['scipy'] = scipy
        local_scope['stats'] = stats
    except ImportError:
        pass

    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
        local_scope['sm'] = sm
        local_scope['smf'] = smf
    except ImportError:
        pass

    try:
        import lifelines
        local_scope['lifelines'] = lifelines
    except ImportError:
        pass

    try:
        import sklearn
        local_scope['sklearn'] = sklearn
    except ImportError:
        pass

    success = False
    fig_result = None
    error_msg = None

    try:
        sys.stdout = stdout_capture
        # Execute script
        exec(code_str, local_scope, local_scope)

        # Retrieve figure
        if 'fig' in local_scope and isinstance(local_scope['fig'], plt.Figure):
            fig_result = local_scope['fig']
        else:
            # Fallback to current figure if user called plt.plot / sns directly without fig, ax
            fig_result = plt.gcf()

        # Check if the figure has any content/axes
        if fig_result and len(fig_result.axes) == 0:
            # No axes was created
            pass

        success = True
    except Exception as e:
        error_msg = traceback.format_exc()
        success = False
    finally:
        sys.stdout = original_stdout

    captured_output = stdout_capture.getvalue()

    return {
        'success': success,
        'figure': fig_result,
        'output': captured_output,
        'error': error_msg
    }
