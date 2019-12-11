import pandas as pd
import json


def get_df_from_json(json_file):
    with open(json_file) as json_data:
        json_data = json.load(json_data)
    weatherDf = pd.DataFrame(json_data["Weather"])
    return weatherDf
