import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import os.path
from os import path
import pathlib
import glob

quarters = [('01', '03'), ('04', '06'), ('07', '09'), ('10', '12')]
years = ['2013', '2014', '2015']
menu_index = ['StateName', 'LocationName', 'StoreName', 'SalesManagerName', 'ProductCategoryName', 'ProductName']
columns = ['StateName', 'LocationName', 'StoreName', 'Quarter', 'Revenue', 'Profit']
columns_etc = ['Indicator', 'Quarter', 'Revenue', 'Profit']
columns_revenue_profit = ['Indicator', 'Quarter', 'Revenue_Profit']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv('data/BestRunrefreshmentsales.csv')
df.head()

dict = {}
path = 'data/'
all_files = glob.glob('data/*.csv')
for filename in all_files:
    dfo = pd.read_csv(filename, index_col=None, header=0)
    dict[filename[5:-4]] = dfo

x_time_series_changed = 'null'
y_time_series_changed = 'null'

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-category-column',
                options=[{'label': i, 'value': i} for i in menu_index],
                value='StateName'
            )
        ],style={'width': '49%', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'pointIndex': -1}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'})
])

def get_dataframe_by_quarter(dfObj, category, indicator):
    if category == 'LocationName':
        ddfg = df.loc[df[category] == indicator, ['StateName']]
        stateName = ddfg.iloc[0]['StateName']
        locationName = indicator
        storeName = "NaN"
    elif category == 'StoreName':
        ddfg = df.loc[df[category] == indicator, ['StateName', 'LocationName']]
        stateName = ddfg.iloc[0]['StateName']
        locationName = ddfg.iloc[0]['LocationName']
        storeName = indicator
    else:
        stateName = indicator
        locationName = "NaN"
        storeName = "NaN"

    for year in years:
        i = 1
        for quarter in quarters:
            start_quarter = year + quarter[0]
            end_quarter = year + quarter[1]

            period = df.loc[(df[category] == indicator)
                            & (df['Date'].between(int(start_quarter), int(end_quarter)))]

            col_quarter = 'Q' + str(i) + '/' + str(year)
            dfObj  = dfObj.append({'StateName': stateName,
                                  'LocationName': locationName,
                                  'StoreName': storeName,
                                  'Quarter': col_quarter,
                                  'Revenue': period['OriginalSalesPrice'].sum(),
                                  'Profit': period['GrossMargin'].sum()}, ignore_index=True)
            i = i + 1
    return dfObj

def get_dataframe_etc_by_quarter(dfObj, category, indicator):
    for year in years:
        i = 1
        for quarter in quarters:
            start_quarter = year + quarter[0]
            end_quarter = year + quarter[1]

            period = df.loc[(df[category] == indicator)
                            & (df['Date'].between(int(start_quarter), int(end_quarter)))]

            col_quarter = 'Q' + str(i) + '/' + str(year)
            dfObj  = dfObj.append({'Indicator': indicator,
                                  'Quarter': col_quarter,
                                  'Revenue': period['OriginalSalesPrice'].sum(),
                                  'Profit': period['GrossMargin'].sum()}, ignore_index=True)
            i = i + 1
    return dfObj

def get_revenue_profit_by_indicator(category, indicator, target):
    dfObj = pd.DataFrame(columns=columns_revenue_profit)
    if not dict:
        dff = dict.get('BestRunrefreshmentsales')
    else:
        dff = df

    for year in years:
        i = 1
        for quarter in quarters:
            start_quarter = year + quarter[0]
            end_quarter = year + quarter[1]

            period = dff.loc[(dff[category] == indicator)
                            & (dff['Date'].between(int(start_quarter), int(end_quarter)))]

            col_quarter = 'Q' + str(i) + '/' + str(year)
            dfObj  = dfObj.append({'Indicator': indicator,
                                  'Quarter': col_quarter,
                                  'Revenue_Profit': period[target].sum()}, ignore_index=True)
            i = i + 1
    return dfObj

@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-category-column', 'value')])
def update_graph(category):
    if category == 'SalesManagerName' or category == 'ProductCategoryName' or category == 'ProductName':
        if not dict:
            dff = dict.get(category)
            fig = px.scatter(dff, x=dff.Revenue, y=dff.Profit, animation_frame=dff.Quarter,
                                color=dff.Indicator, hover_name=dff.Indicator)
        else:
            dff = pd.DataFrame(columns=columns_etc)

            available_indicators = df[category].unique()
            for indicator in available_indicators:
                dff = get_dataframe_etc_by_quarter(dff, category, indicator)
            fig = px.scatter(dff, x='Revenue', y='Profit', animation_frame='Quarter',
                                color='Indicator', hover_name='Indicator')
            dff.to_csv(filename)
    else:
        if not dict:
            dff = dict.get(category)
            fig = px.scatter(dff, x=dff.Revenue, y=dff.Profit, animation_frame=dff.Quarter,
                                color=dff.StateName, animation_group=category, hover_name=category)
        else:
            dff = pd.DataFrame(columns=columns)

            available_indicators = df[category].unique()
            for indicator in available_indicators:
                dff = get_dataframe_by_quarter(dff, category, indicator)
            fig = px.scatter(dff, x='Revenue', y='Profit', animation_frame='Quarter',
                                color='StateName', animation_group=category, hover_name=category)
            dff.to_csv(filename)

    fig.update_xaxes(title='Revenue', type='linear') #, range=[-100, dff['Revenue'].max()])
    fig.update_yaxes(title='Profit', type='linear') #, range=[-100, dff['Profit'].max()])
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    return fig

def create_time_series(dff, axis_type, value, indicator):
    fig = px.scatter(dff, x='Quarter', y='Revenue_Profit')
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(title=value, type='linear' if axis_type == 'Linear' else 'log')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=indicator)
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-category-column', 'value'),
     dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])
def update_y_timeseries(category, hoverData):
    global y_time_series_changed

    if y_time_series_changed != category or hoverData['points'][0]['pointIndex'] == -1:
        available_indicators = df[category].unique()
        indicator = available_indicators[0]
        y_time_series_changed = category
    else:
        indicator = hoverData['points'][0]['hovertext']

    dff = get_revenue_profit_by_indicator(category, indicator, 'GrossMargin')
    return create_time_series(dff, 'linear', 'Profit', indicator)

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-category-column', 'value'),
     dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])
def update_x_timeseries(category, hoverData):
    global x_time_series_changed

    if x_time_series_changed != category or hoverData['points'][0]['pointIndex'] == -1:
        available_indicators = df[category].unique()
        indicator = available_indicators[0]
        x_time_series_changed = category
    else:
        indicator = hoverData['points'][0]['hovertext']

    dff = get_revenue_profit_by_indicator(category, indicator, 'OriginalSalesPrice')
    return create_time_series(dff, 'linear', 'Revenue', indicator)

if __name__ == '__main__':
    app.run_server(debug=True)

#<iframe width="900" height="600" frameborder="0" scrolling="no"
#	src="https://nameless-forest-96407.herokuapp.com/"></iframe>