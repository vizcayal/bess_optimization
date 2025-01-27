import pandas as pd

def date_to_timezone(dataset: pd.DataFrame, col_name: str, timezone: str = 'US/Central') -> pd.DataFrame:
    """
    Converts a datetime column in a dataset to a specified timezone.

    Parameters:
    dataset: The dataset containing the datetime column to be converted.
    col_name: The name of the column with datetime values to be processed.
    timezone: The timezone to localize the datetime values to. Default is 'US/Central'.

    Returns: A DataFrame with the datetime column localized to the specified timezone.
    zone.
    """
    # Check the column is datetime 
    dataset[col_name] = pd.to_datetime(dataset[col_name])

    # Set col_name as the index and localize to the timezone
    dataset = dataset.set_index(col_name).tz_localize(timezone, ambiguous='infer')

    # Reset index back to normal column
    dataset = dataset.reset_index()

    return dataset