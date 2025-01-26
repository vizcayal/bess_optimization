import pandas as pd

def date_to_timezone(dataset, col_name, timezone = 'US/Central'):
    ''' 
    given a dataset, and a column (col_name) with datetime values,
    convert it to timezone.
    '''
    dataset[col_name] = pd.to_datetime(dataset[col_name])
        
    dataset = dataset.set_index(col_name).tz_localize(timezone, ambiguous='infer')
    dataset = dataset.reset_index()
    return dataset