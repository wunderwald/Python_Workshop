import seaborn as sns
import numpy as np
import pandas as pd
def lineplot(arr):
    df = pd.DataFrame({
        "x": np.arange(len(arr)),
        "y": arr
    })
    sns.lineplot(data=df, x="x", y="y")