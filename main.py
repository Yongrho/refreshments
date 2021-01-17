import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

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
    quarter = 1
    year = 2013
    columns = ['Quarter','Revenue', 'Profit']
    dfObj = pd.DataFrame(columns=columns)
    for i in range(12):
        if quarter == 1:
            start_month = '01'
            end_month = '03'
        elif quarter == 2:
            start_month = '04'
            end_month = '06'
        elif quarter == 3:
            start_month = '07'
            end_month = '09'
        else:
            start_month = '10'
            end_month = '12'
        start_quarter = str(year) + start_month
        end_quarter = str(year) + end_month

        period = df[(df['Date'] >= int(start_quarter)) & (df['Date'] <= int(end_quarter))]
        revenue = period['OriginalSalesPrice'].sum()
        profit = period['GrossMargin'].sum()

        col_quarter = 'Q' + str(quarter) + '/' + str(year)
        dfObj = dfObj.append({'Quarter': col_quarter, 'Revenue': revenue, 'Profit': profit}, ignore_index=True)
        if quarter == 4:
            quarter = 1
            year += 1
        else:
            quarter += 1
    print(dfObj)

    fig = px.line(dfObj, x="Quarter", y=dfObj.columns,
                  hover_data={"Quarter": "|%B %s, %Y"},
                  title='custom tick labels with ticklabelmode="period"')
    fig.update_xaxes(
        dtick="Q1",
        tickformat="%b\n%Y",
        ticklabelmode="period")
    fig.show()

def chart_overall_revenue_profit_by_month(df):
    s = 2013
    e = 2016
    month_format = ['01','02','03','04','05','06','07','08','09','10','11','12']
    columns = ['Month', 'Revenue', 'Profit']
    dfObj = pd.DataFrame(columns=columns)
    for year in range(s, e):
        print (year)
        for month in range(1, 13):
            year_month = str(year) + month_format[month - 1]
            period = df[(df['Date'] == int(year_month))]
            revenue = period['OriginalSalesPrice'].sum()
            profit = period['GrossMargin'].sum()

            month_col = str(year) + '-' + str(month)
            dfObj = dfObj.append({'Month': month_col, 'Revenue': revenue, 'Profit': profit}, ignore_index=True)
    print(dfObj)
    fig = px.line(dfObj, x="Month", y=dfObj.columns,
                  hover_data={"Month": "|%B, %Y"},
                  title='custom tick labels with ticklabelmode="period"')
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y",
        ticklabelmode="period")
    fig.update_layout(hovermode="x", width=1000, height=500)
    fig.show()

if __name__ == '__main__':
#    df = pd.read_csv('data/sales1.csv')
    df = pd.read_csv('data/BestRunrefreshmentsales.csv')
    df.head()

#    chart_revenue_by_city_with_geo(df)
#    chart_overall_revenue_profit_by_quarter(df)
#    chart_overall_revenue_profit_by_month(df)

