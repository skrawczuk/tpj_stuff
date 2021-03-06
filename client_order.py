from history import update_history_sheet
from datetime import datetime
import numpy as np
import pandas as pd
import argparse


def per_client(order_sheet, dish_names): 
    with open('per_client.txt', 'w') as fo: 
        for _, row in order_sheet.iterrows():
            fo.write('{}\n'.format(row['name']))

            for dish in dish_names: 
                if not pd.isnull(row[dish]):
                    if isinstance(row[dish], float):
                        row[dish] = int(row[dish])
                    fo.write('• {} - {}\n'.format(dish, row[dish]))
            if not pd.isnull(row['Comments + Special Requests']):
                fo.write(row['Comments + Special Requests'])
                fo.write('\n')
            fo.write('\n')


def per_dish_client(order_sheet, dish_names):
    with open('per_dish_clients.txt', 'w') as fo:
        for dish in dish_names:
            fo.write('• {}: \n'.format(dish))
            for _, row in order_sheet[['name', dish]].dropna().iterrows():
                if isinstance(row[dish], float):
                    row[dish] = int(row[dish])
                fo.write('   - {}: {}\n'.format(row['name'], row[dish]))
            fo.write('\n')


def per_dish_count(order_sheet, dish_names):
    dish_count_df = pd.DataFrame()
    with open('per_dish_counts.txt', 'w') as fo:
        for dish in dish_names:
            dish_df = pd.DataFrame()
            try:
                dish_df.loc[:, 'count'] = order_sheet[dish].dropna().apply(
                    lambda x: max([float(i) for i in str(x).replace(' servings', '').split(',') if i.replace('.', '').isnumeric()]))
            except ValueError:
                print(f'\n\n\nHi chef, please check the CSV for missing amounts for: \n- {dish} \n\n\n')
                break

            modifier_filter = lambda x: ', '.join([i.lower() for i in str(x).split(', ') if ''.join([s for s in i if s.isalnum()]).replace(' ', '').isalpha()])

            dish_df.loc[:, 'modifier'] = order_sheet[dish].dropna().apply(modifier_filter)
            dish_df.replace('', 'unmodified', inplace=True)

            if not dish_df.empty:
                dish_subcounts = dish_df.groupby('modifier').apply(lambda x: x['count'].sum()).astype(int)
                dish_count = dish_subcounts.sum()
            else:
                dish_subcounts = {}
                dish_count = 0

            dish_count_df[dish] = [dish_count]

            fo.write('• {}: {}\n'.format(dish, dish_count))
            for mod, ct in dish_subcounts.items():
                fo.write('   - {}: {}\n'.format(mod, ct))
            fo.write('\n')
    return dish_count_df


if __name__ == '__main__':
    argc = argparse.ArgumentParser(description='csv input path')
    argc.add_argument('-i', '--input_path', type=str)
    argc.add_argument('-p', '--history_path', type=str)

    argp = argc.parse_args()
    
    input_path = argp.input_path
    history_path = argp.history_path

    order_sheet = pd.read_csv(input_path)
    order_sheet = order_sheet.loc[:, ~order_sheet.columns.str.contains('^Unnamed')]

    date = datetime.strptime(order_sheet['Submitted At'][0][:12], '%b %d, %Y')

    for k, v in order_sheet.items():
        order_sheet.loc[order_sheet[k].astype(str).str.startswith('novalue'), k] = np.nan

    order_sheet['name'] = order_sheet['First Name'] + ' ' + order_sheet['Last Name']

    INFO_COLS = ['name', 'First Name', 'Last Name', 'Phone', 'Email Address', 'Email',
                 'Address for Delivery', 'Address', 'Comments + Special Requests',
                 'Payment Received', 'Payer Name', 'Payer Address', 'Payer Email',
                 'Total Payment', 'Quantity', 'Street Address', 'City', 'State / Province',
                 'Zip / Country', 'Purchase Details', 'Purchase Type', 'Confirmation Code',
                 'Memo', 'Locale', 'Submission Source', 'Submitted At']
    dish_names = [col for col in order_sheet if col not in INFO_COLS and not col.endswith('.1')]

    per_client(order_sheet, dish_names)
    per_dish_client(order_sheet, dish_names)
    dish_count_df = per_dish_count(order_sheet, dish_names)
    update_history_sheet(history_path, dish_count_df, date)
