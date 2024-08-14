# This file contains methods for getting all of the data used in the model
import datetime
import io
import os

import numpy as np
import requests
from bs4 import BeautifulSoup
from fredapi import Fred
import pandas as pd
import warnings
from dotenv import load_dotenv
warnings.filterwarnings('ignore')


load_dotenv()
fred_api_key = os.getenv('FREDapiKey')
fred = Fred(api_key=fred_api_key)

recession_starts = ['1960-04-01', '1969-12-01', '1973-11-01', '1980-01-01', '1981-07-01',
                    '1990-07-01', '2001-03-01', '2007-12-01', '2020-02-01']
recession_ends = ['1961-02-01', '1970-11-01', '1975-03-01', '1980-07-01', '1982-11-01',
                  '1991-03-01', '2001-11-01', '2009-06-01', '2020-04-01']


def get_using_dates():
    return pd.DataFrame(data=pd.date_range('1965-01-01', datetime.datetime.today().strftime("%Y-%m-%d"),
                                           freq='MS').strftime("%Y-%m-%d").tolist(), columns=['date'])


def get_unemp_table():
    unemp = fred.get_series('UNRATE')
    unemp = pd.DataFrame(unemp).reset_index()
    unemp.columns = ['date', 'un_rate']
    unemp.date = unemp.date.astype(str)
    unemp = unemp[unemp['date'] >= '1965-01-01'].reset_index(drop=True)
    unemp['12_mo_unemp_change'] = 0.
    for i in range(12, len(unemp)):
        change = (unemp.at[i, 'un_rate'] - unemp.at[i - 12, 'un_rate'])
        unemp.at[i, '12_mo_unemp_change'] = change
    unemp = unemp[unemp['date'] >= '1968-01-01'].reset_index(drop=True)
    print('Unemp Table Most Recent: ', unemp.iloc[-1]['date'])
    unemp = unemp.merge(get_using_dates(), how='right', on='date')
    unemp['12_mo_unemp_change'] = unemp['12_mo_unemp_change'].fillna(method='bfill').fillna(method='ffill')
    unemp['un_rate'] = unemp['un_rate'].fillna(method='bfill').fillna(method='ffill')
    return unemp


def get_mhp_table():
    mhp = fred.get_series('MSPUS')
    mhp = pd.DataFrame(mhp).reset_index()
    mhp.columns = ['date', 'median_household_price']
    mhp.date = mhp.date.astype(str)
    mhp = mhp.merge(get_using_dates(), how='right', on='date')
    mhp.median_household_price = mhp.median_household_price.fillna(method='pad')
    mhp['pct_house_change_year'] = 0.
    mhp['housing_climb_change'] = 0.
    for i in range(12, len(mhp)):
        pct_change = ((mhp.at[i, 'median_household_price'] -
                       mhp.at[i - 12, 'median_household_price']) /
                      mhp.at[i - 12, 'median_household_price']) * 100
        mhp.at[i, 'pct_house_change_year'] = pct_change

        value_change = (mhp.at[i, 'pct_house_change_year'] - mhp.at[i - 12, 'pct_house_change_year'])
        mhp.at[i, 'housing_climb_change'] = value_change

    mhp = mhp[mhp['date'] >= '1968-01-01'].reset_index(drop=True)
    print('MHP Table Most Recent: ', mhp.iloc[-1]['date'])
    return mhp


def get_cpi_table():
    latest_date = datetime.datetime.today() - datetime.timedelta(1)
    ld_string = latest_date.strftime('%Y-%m-%d')
    if datetime.datetime.today().month != 1:
        latest_month = datetime.datetime(datetime.datetime.today().year,
                                         datetime.datetime.today().month - 1, 1)
    else:
        latest_month = datetime.datetime(datetime.datetime.today().year - 1,
                                         12, 1)
    lm_string = latest_month.strftime('%Y-%m-%d')
    cpi = requests.get('https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&' +
                       'chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&heigh' +
                       't=389&mode=fred&recession_bars=on&txtcolor=%23444444&ts=10&tts=10&' +
                       'width=536&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&sh' +
                       'ow_tooltip=yes&id=CPIAUCSL,CPILFESL&scale=left,left&cosd=1960-01-0' +
                       '1,1960-01-01&coed=' + lm_string + ',' + lm_string + '&line_color=%' +
                       '234572a7,%23aa4643&link_values=false,false&line_style=solid,solid&' +
                       'mark_type=none,none&mw=1,1&lw=2,2&ost=-99999,-99999&oet=99999,9999' +
                       '9&mma=0,0&fml=a,a&fq=Monthly,Monthly&fam=avg,avg&fgst=lin,lin&fgsn' +
                       'd=2009-06-01,2009-06-01&line_index=1,2&transformation=pc1,pc1&vint' +
                       'age_date=' + ld_string + ',' + ld_string + '&revision_date=' +
                       ld_string + ',' + ld_string + '&nd=1947-01-01,1957-01-01')
    cpi = pd.read_csv(io.StringIO(cpi.content.decode('utf-8')))
    cpi.columns = ['date', 'cpi_change_all', 'cpi_change_less_food_and_energy']
    cpi['36_mo_cpi_change_all'] = 0.
    for i in range(36, len(cpi)):
        change = (cpi.at[i, 'cpi_change_all'] - cpi.at[i - 36, 'cpi_change_all'])
        cpi.at[i, '36_mo_cpi_change_all'] = change

    cpi = cpi[cpi['date'] >= '1968-01-01'].reset_index(drop=True)
    print('CPI Table Most Recent: ', cpi.iloc[-1]['date'])
    cpi = cpi.merge(get_using_dates(), how='right', on='date')
    cpi['36_mo_cpi_change_all'] = cpi['36_mo_cpi_change_all'].fillna(method='bfill').fillna(method='ffill')
    cpi['cpi_change_all'] = cpi['cpi_change_all'].fillna(method='bfill').fillna(method='ffill')
    cpi['cpi_change_less_food_and_energy'] = cpi['cpi_change_less_food_and_energy'].fillna(method='bfill').fillna(method='ffill')
    return cpi


def get_sp_table():
    url = 'https://www.multpl.com/s-p-500-historical-prices/table/by-month'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find(id='datatable')

    sp = pd.DataFrame(columns=['date', 'average_sp_price'])

    dt = table.find_all('tr')
    for i in range(2, len(dt)):
        info = dt[i].find_all('td')
        date = info[0].text
        date = datetime.datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')
        price = info[1].text.replace('\n', '').replace(',', '')
        sp = sp.append({'date': date, 'average_sp_price': float(price)}, ignore_index=True)

    sp['pct_monthly_sp_change'] = 0.
    sp['pct_bimonthly_sp_change'] = 0.
    sp = sp[sp['date'] >= '1967-01-01']
    sp = sp.sort_values('date').reset_index(drop=True)
    for i in range(2, len(sp)):
        monthly_pct_change = ((sp.at[i, 'average_sp_price'] -
                               sp.at[i - 1, 'average_sp_price']) /
                              sp.at[i - 1, 'average_sp_price']) * 100
        sp.at[i, 'pct_monthly_sp_change'] = monthly_pct_change

        bi_pct_change = ((sp.at[i, 'average_sp_price'] -
                          sp.at[i - 2, 'average_sp_price']) /
                         sp.at[i - 2, 'average_sp_price']) * 100
        sp.at[i, 'pct_bimonthly_sp_change'] = bi_pct_change

    sp = sp[sp['date'] >= '1968-01-01'].reset_index(drop=True)
    print('S&P Table Most Recent: ', sp.iloc[-1]['date'])
    return sp


def get_yield_table():
    yield_ten = fred.get_series('DGS10')
    yield_ten = pd.DataFrame(yield_ten).reset_index()
    yield_ten.columns = ['date', 'ten_yr_yield']
    yield_ten.date = [pd.to_datetime(x).strftime('%Y-%m-%d') for x in yield_ten.date.values]
    yield_ten = yield_ten.merge(get_using_dates(), how='outer', on='date').sort_values('date')
    yield_ten.ten_yr_yield = yield_ten.ten_yr_yield.fillna(method='bfill').fillna(method='ffill')
    rows = [(x, y) for x, y
            in zip(yield_ten.date.values, yield_ten.ten_yr_yield.values) if
            (x.split('-')[2] == '01')]
    yield_ten = pd.DataFrame(data=rows, columns=['date', 'ten_yr_yield'])

    # 1 Year Yield
    yield_one = fred.get_series('DGS1')
    yield_one = pd.DataFrame(yield_one).reset_index()
    yield_one.columns = ['date', 'one_yr_yield']
    yield_one.date = [pd.to_datetime(x).strftime('%Y-%m-%d') for x in yield_one.date.values]
    yield_one = yield_one.merge(get_using_dates(), how='outer', on='date').sort_values('date')
    yield_one.one_yr_yield = yield_one.one_yr_yield.fillna(method='bfill').fillna(method='ffill')
    rows = [(x, y) for x, y
            in zip(yield_one.date.values, yield_one.one_yr_yield.values) if
            (x.split('-')[2] == '01')]
    yield_one = pd.DataFrame(data=rows, columns=['date', 'one_yr_yield'])

    total_yield = yield_ten.merge(yield_one, how='inner', on='date')
    total_yield['yield_diff'] = total_yield['ten_yr_yield'] - total_yield['one_yr_yield']
    total_yield['yield_below_zero'] = (total_yield['yield_diff'] < 0).astype(int)
    print('Yield Table Most Recent: ', total_yield.iloc[-1]['date'])
    return total_yield


# returns the number of years from the given date since the last recession
# returns 0 if date is during a recession
# returns NaN if given date is before the earliest recorded recesssion in the data
def yearsSinceRecession(date):
    if date < recession_starts[0]:
        return float('NaN')
    days_since_list = []
    for i in range(len(recession_ends)):
        days_since = (datetime.datetime.strptime(date, '%Y-%m-%d') -
                      datetime.datetime.strptime(recession_ends[i], '%Y-%m-%d')).days
        days_since_list.append(days_since)
    min_days = min(d for d in days_since_list if d > 0)
    min_days_idx = days_since_list.index(min_days)
    if min_days_idx == len(recession_starts) - 1:
        return min_days / 365
    elif date >= recession_starts[min_days_idx + 1]:
        return 0
    else:
        return min_days / 365


# returns the number of years from the given date until the next recession
# returns 0 if date is in a recession
# returns nan if date is after the latest recession
def yearsUntilRecession(date):
    days_until_list = []
    for i in range(len(recession_starts)):
        days_until = (datetime.datetime.strptime(recession_starts[i], '%Y-%m-%d') -
                      datetime.datetime.strptime(date, '%Y-%m-%d')).days
        days_until_list.append(days_until)
    try:
        min_days = min(d for d in days_until_list if d >= 0)
    except ValueError:
        if date <= recession_ends[-1]:
            return 0
        return float('NaN')
    min_days_idx = days_until_list.index(min_days)
    if (min_days_idx != 0) & (date <= recession_ends[min_days_idx - 1]):
        return 0
    else:
        return min_days / 365


# returns 1 if there is a recession in the next year, or if there is currently a recession
# returns NaN if one year from the listed date is in the future
# returns 0 otherwise
def recessionInNextYear(date):
    if yearsSinceRecession(date) == 0:
        return 1

    split_date = date.split('-')
    one_year_later = str(int(split_date[0]) + 1) + '-' + split_date[1] + '-' + split_date[2]
    if one_year_later > datetime.datetime.today().strftime('%Y-%m-%d'):
        return float('NaN')
    possible_matches = [d for d in recession_starts if d >= date]
    possible_matches = [d for d in possible_matches if d <= one_year_later]
    return float(len(possible_matches) > 0)


def inRecession(date):
    for i in range(len(recession_starts)):
        if (date <= recession_ends[i]) & (date >= recession_starts[i]):
            return 1
    return 0


def get_total_table():
    YSRVect = np.vectorize(yearsSinceRecession)
    YURVect = np.vectorize(yearsUntilRecession)
    RINYVect = np.vectorize(recessionInNextYear)
    IRVect = np.vectorize(inRecession)

    total_data = get_unemp_table().merge(get_mhp_table(), how='inner', on='date')
    total_data = total_data.merge(get_cpi_table(), how='inner', on='date')
    total_data = total_data.merge(get_sp_table(), how='left', on='date')
    total_data = total_data.merge(get_yield_table(), how='inner', on='date')

    total_data['years_since_recession'] = YSRVect(total_data.date.values)
    total_data['years_until_recession'] = YURVect(total_data.date.values)
    total_data['recession_in_next_year'] = RINYVect(total_data.date.values)
    total_data['in_recession'] = IRVect(total_data.date.values)
    return total_data


if __name__ == "__main__":
    total_data = get_total_table()
    total_data.to_csv('mysite/CodeBase/Data/total_data.csv')
