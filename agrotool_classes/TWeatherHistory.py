import numpy as np
import pandas as pd


class TWeatherHistory():
    def __init__(self):
        self.df = pd.DataFrame(
            {
                "Date": np.empty(0),
                "T": np.empty(0),
                "Rad": np.empty(0),
                "Prec": np.empty(0),
                "SumSnow": np.empty(0),
            }
        )

    def append_frame(self, new_frame_dict):
        self.df = self.df.append(pd.DataFrame(new_frame_dict))
