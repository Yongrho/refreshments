import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
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
    fig.write_html("html/chart_revenue_by_city_with_geo.html")

if __name__ == '__main__':
#    df = pd.read_csv('data/sales1.csv')
    df = pd.read_csv('data/sales.csv')
    df.head()

    chart_revenue_by_city_with_geo(df)
