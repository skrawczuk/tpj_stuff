import pandas as pd
import os


def update_history_sheet(history_path, dish_count_df, date):
    if os.path.isfile(history_path):
        history_sheet = pd.read_csv(history_path, index_col=0)
        history_sheet.columns = pd.to_datetime(history_sheet.columns)
        history_sheet = history_sheet.T
        history_sheet.index.name = 'date'
    else:
        history_sheet = pd.DataFrame()

    dish_count_df.columns = list(map(dish_parser, dish_count_df.columns.tolist()))
    dish_count_df['date'] = date
    dish_count_df = dish_count_df.set_index('date')

    history_sheet = history_sheet.append(dish_count_df)
    history_sheet = history_sheet.sort_values(by='date')
    history_sheet.T.to_csv(history_path)


def dish_parser(name):
    stripped_name = name.lower().split('~')[0].strip()
    stripped_name = stripped_name.split('…')[0].strip()
    stripped_name = stripped_name.replace('*', '').strip()

    return stripped_name

