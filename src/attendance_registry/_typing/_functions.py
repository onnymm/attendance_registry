from typing import Callable
import pandas as pd

ColumnAssignation = dict[str, Callable[[pd.DataFrame], pd.Series]]
