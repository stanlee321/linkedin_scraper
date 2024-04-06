# Ensure the 'json_column' is actually stringified JSON and convert it if necessary
from typing import List
import pandas as pd

def create_profile_df(data_list: List[dict], data_column: str = 'data'):
    
    df = pd.DataFrame(data_list)
    
    expanded_df = pd.DataFrame()

    # Iterate over each row in the original DataFrame
    for index, row in df.iterrows():
        # Normalize the list of dictionaries and create a DataFrame
        row_df = pd.json_normalize(row[data_column])
        # Add the 'page' value to this new DataFrame
        row_df['page'] = row['page']
        # Append the new DataFrame to the expanded DataFrame
        expanded_df = pd.concat([expanded_df, row_df], ignore_index=True)
    
    # Drop Empty rows if profile_link is empty
    # expanded_df.dropna(subset=['name','profile_url'], inplace=True)
    expanded_df = expanded_df[~(expanded_df['name'] == '') & ~(expanded_df['profile_url'] == '') ]
    return expanded_df