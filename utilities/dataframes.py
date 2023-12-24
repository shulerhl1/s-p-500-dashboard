import os
import pandas as pd
import numpy as np
import numpy_financial as npf
from datetime import datetime

def get_recent_file():
    target_directory = os.path.join(os.getcwd(), 'data')

    filename_dict = {}
    for file in os.listdir(target_directory):
        name, ext = os.path.splitext(file)
        try:
            date = datetime.strptime(name.split(' ')[1], '%m.%d.%y')
        except:
            continue
        filename_dict[date] = file

    return os.path.join(target_directory, filename_dict[max(filename_dict)])

def get_decade_list(target_list):
    def get_decade(target_year):
        return target_year - (target_year % 10) + 10
    return range(get_decade(target_list[0]), get_decade(target_list[1]), 10)

def dataframe_filter(value):
    global dff
    dff = df[(df['Date']>=datetime(value[0], 12, 1)) & (df['Year']<=value[1])]
    return dff

def table_returns(value):
    
    # Aggregate data, add cash flow column, and calculate irr
    dfy = dff.groupby('Year', as_index=False).agg(
        {'Earnings': 'last', 'Price-to-Earnings': 'last', 'S&P 500 Index': 'last', 'Dividends': 'last'})
    dfy['Cash Flow'] = np.where(dfy['Year']==value[0], dfy['S&P 500 Index'] * -1, 
        np.where(dfy['Year']==value[1], dfy['S&P 500 Index'] + dfy['Dividends'], dfy['Dividends']))
    n = value[1] - value[0]
    total_return = npf.irr(dfy['Cash Flow'])
    total_multiple = (1 + total_return) ** n - 1

    # New dataframe with just first and last years data; drop dividends and cash flow columns
    dftr = dfy[(dfy['Year']==value[0]) | (dfy['Year']==value[1])]
    dftr = dftr.drop(['Dividends'], axis=1)
    dftr = dftr.drop(['Cash Flow'], axis=1)

    # Transpose, remove the first row, and reset the index
    dftr = dftr.T
    dftr = dftr.iloc[1:]
    dftr = dftr.reset_index()

    # Make and set new headers
    # start_column = f'Start: {value[0]}'
    # end_column = f'End: {value[1]}'
    # dftr.columns = ['Measure', start_column, end_column]
    dftr.columns = ['Measure', 'Start', 'End']

    # Add columns for multiple and cagr
    # dftr['Multiple'] = dftr[end_column] / dftr[start_column]
    dftr['Multiple'] = dftr['End'] / dftr['Start']
    dftr['CAGR'] = dftr['Multiple'] ** (1/n) - 1

    # Add new rows with other return measures
    index_return = dftr.iloc[2]['CAGR']
    dftr.loc[3] = ['Dividends', '', '', '', total_return - index_return]
    dftr.loc[4] = ['Total Return', '', '', total_multiple, total_return]
    
    return dftr


df = pd.read_excel(
    # io=get_recent_file(),
    io=r'http://www.econ.yale.edu/~shiller/data/ie_data.xls',
    sheet_name='Data',
    header=None,
    usecols='A:D',
    skiprows=1040,
    nrows=1000
)

# Add header row, drop labels at the end, and fill missing earnings/dividends
df.columns = ['Date', 'S&P 500 Index', 'Dividends', 'Earnings']
df = df.drop(len(df)-1)
df = df.ffill()

# Convert YYYY.MM format to datetime date
df['Date'] *= 10000
df['Date'] += 1
df['Date'] = pd.to_datetime(df.Date, format='%Y%m%d')

# Add various columns
df['Dividend Yield'] = df['Dividends']/df['S&P 500 Index']
df['Price-to-Earnings'] = df['S&P 500 Index']/df['Earnings']
df['Year'] = df['Date'].dt.year

# Define minimum and maximum years and make list of decades
years = [df['Year'].min(), df['Year'].max()]
decades = get_decade_list(years)

# Initialize the filtered dataframe
dff = df

