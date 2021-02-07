import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

years = ['2013', '2014', '2015']
quarters = [('01', '03'), ('04', '06'), ('07', '09'), ('10', '12')]
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

def chart_revenue_by_city_with_geo(df):
    df.set_index('LocationName', inplace=True)
    sum_by_city = df.groupby(level='LocationName')['OriginalSalesPrice'].sum().reset_index()
    longitude_by_city = df.groupby(level='LocationName')['Longitude'].mean().reset_index()
    latitude_by_city = df.groupby(level='LocationName')['Latitude'].mean().reset_index()
    merge_by_city = sum_by_city.merge(longitude_by_city)
    merge_by_city = merge_by_city.merge(latitude_by_city)
    revenue_by_city = merge_by_city.sort_values('OriginalSalesPrice', ascending=False)

    revenue_by_city['text'] = revenue_by_city['LocationName'] + '<br>Sales ' + (revenue_by_city['OriginalSalesPrice']).astype(str) + ' dollars'
    limits = [(0, 3), (4, 10), (11, 20), (21, 50), (50, 3000)]
    colors = ["royalblue", "crimson", "lightseagreen", "orange", "lightgrey"]
    scale = 100000

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        df_sub = revenue_by_city[lim[0]:lim[1]]

        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=df_sub['Longitude'],
            lat=df_sub['Latitude'],
            text=df_sub['text'],
            marker=dict(
                size=df_sub['OriginalSalesPrice'] / scale,
                color=colors[i],
                line_color='rgb(40,40,40)',
                line_width=0.5,
                sizemode='area'
            ),
            name='{0} - {1}'.format(lim[0], lim[1])))

    fig.update_layout(
        title_text='2013-2015 revenue in the west coast cities of the US <br>(Click legend to toggle traces)',
        showlegend=True,
        geo=dict(
            scope='usa',
            landcolor='rgb(217, 217, 217)',
        )
    )
    fig.write_html("chart/chart_revenue_by_city_with_geo.html")

def chart_overall_revenue_profit_by_quarter(df):
    columns = ['Quarter','Revenue', 'Profit']
    dff = pd.DataFrame(columns=columns)

    for year in years:
        i = 1
        for quarter in quarters:
            start_quarter = year + quarter[0]
            end_quarter = year + quarter[1]

            period = df[(df['Date'] >= int(start_quarter)) & (df['Date'] <= int(end_quarter))]

            col_quarter = 'Q' + str(i) + '/' + str(year)
            dff = dff.append({'Quarter': col_quarter,
                              'Revenue': period['OriginalSalesPrice'].sum(),
                              'Profit': period['GrossMargin'].sum()}, ignore_index=True)
            i = i + 1

    fig = px.line(dff, x="Quarter", y=dff.columns,
                  title='The revenue and profit from 2013 to 2015 by quater')

    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_yaxes(title='Revenue-Profit')
    fig.update_layout(width=1000, height=500, hovermode='x unified', legend_title='Legend')
#    fig.show()
    fig.write_html("chart/chart_revenue_profit_by_quarter.html")

def chart_overall_revenue_profit_by_month(df):
    columns = ['Month', 'Revenue', 'Profit']
    ddf = pd.DataFrame(columns=columns)

    for year in years:
        for month in months:
            year_month = year + month
            period = df[(df['Date'] == int(year_month))]

            month_col = year + '-' + month
            ddf = ddf.append({'Month': month_col,
                              'Revenue': period['OriginalSalesPrice'].sum(),
                              'Profit': period['GrossMargin'].sum()}, ignore_index=True)

    fig = px.line(ddf, x='Month', y=ddf.columns,
                  hover_data={"Month": "|%B, %Y"},
                  title='The revenue and profit from 2013 to 2015 by month')

    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y", ticklabelmode="period")
    fig.update_yaxes(title='Revenue-Profit')
    fig.update_layout(width=1000, height=500, hovermode="x", legend_title='Legend')
#    fig.show()
    fig.write_html("chart/chart_revenue_profit_by_month.html")


if __name__ == '__main__':
    df = pd.read_csv('data/BestRunrefreshmentsales.csv')
    df.head()

#   chart_revenue_by_city_with_geo(df)
    chart_overall_revenue_profit_by_quarter(df)
    chart_overall_revenue_profit_by_month(df)