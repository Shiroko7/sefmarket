# -*- coding: utf-8 -*- 

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
#import json
#import numpy as np
#mport dash_dangerously_set_inner_html
from dash.dependencies import Input, Output, State

import pandas as pd
import api
from datetime import date, timedelta, datetime, time

import time


#definir today (ayer)
today = date.today()
shift = timedelta(max(1,(today.weekday() + 6) % 7 - 3))
today = today - shift

options = [str(i)+'D' for i in range(0,30)] + [str(i)+'M' for i in range(1,13)] +  [str(i)+'Y' for i in range(1,31)]
a = {i:options[i] for i in range(len(options))}
b = [{'label': options[i], 'value': options[i]} for i in range(len(options))] + [{'label':'All','value':'All'}]

app = dash.Dash(__name__)
server = app.server


app.layout = html.Div(children=
    [#html.Div(id='options', style={'display': 'none'}),
        html.Div(
            [
                html.Div(
                    [
                        html.H2('SEF Market Data Activity',),
                        html.H6('Versión Alpha 1.2.4',),
                    ],className='twelve columns',style = {'text-align': 'center'}
                )
            ],id='header',className='row',
        ),
        html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Label('Producto',className="control_label"),
                            dcc.Dropdown(
                                id='producto',
                                options=[
                                    {'label': 'NDF USD-CLP', 'value': 'NDF_USD_CLP'},
                                    {'label': 'CLP CAMARA', 'value': 'CLP_CAM'},
                                    {'label': 'UF CAMARA', 'value': 'CLF_CAM'},
                                    {'label': 'BASIS SWAP', 'value': 'BASIS'}
                                ],
                                value='CLP_CAM',             
                            ),                        
                            html.Label('Periodo',className="control_label"),
                            dcc.Dropdown(
                                id='periodo',
                                options=[
                                    {'label': 'Diario', 'value': 'DAILY'},
                                    {'label': 'Semanal', 'value': 'WEEKLY'},
                                    #{'label': 'Mensual', 'value': 'MONTHLY'},
                                ],
                                value='DAILY',             
                            ),
                            html.Label('Fecha de inicio',className="control_label"),
                            dcc.DatePickerSingle(
                                id='start_date',
                                min_date_allowed=datetime(2020, 1, 3),
                                max_date_allowed=today,
                                initial_visible_month=today,
                                date=datetime(2020, 1, 3),
                                display_format='Do MMM, YY'
                            ),
                            html.Label('Fecha de termino',className="control_label"),
                            dcc.DatePickerSingle(
                                id='end_date',
                                min_date_allowed=datetime(2020, 1, 3),
                                max_date_allowed=today,
                                initial_visible_month=today,
                                date=today,
                                display_format='Do MMM, YY'
                            ),
                        ], className = "pretty_container"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([html.Label('USD'),dcc.Input(id='usd', value='850', type='number',style={'text-align':'right'})]),
                                    html.Div([html.Label('UF'),dcc.Input(id='uf', value='28500', type='number',style={'text-align':'right'})]),
                                ], className = 'pretty_container', 
                            )

                        ],className="row"
                    ),
                            
                    dash_table.DataTable(
                            id='table',
                            style_table = {
                                'box-sizing': 'border-box',
                                'overflowX': 'scroll'
                            },
                            style_header={
                                'fontWeight': 'bold',
                                'textAlign': 'center'
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': 'Tenor'},
                                    'textAlign': 'left'
                                }
                            ],
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(251, 251, 251)'
                                },
                                {
                                    'if': {
                                        'column_id': 'Zs',
                                        'filter_query': '{Zs} > 0.0'
                                    },
                                    'color': 'green',
                                },
                                {
                                    'if': {
                                        'column_id': 'Zs',
                                        'filter_query': '{Zs} < 0.0'
                                    },
                                    'color': 'red',
                                },
                            ],
                            merge_duplicate_headers=True,
                        ),
                ],className="four columns"
            ),

            html.Div(
                [
                html.Div(
                    [
                        html.P(
                            children = 'Filtrar por rango de tenors:',
                            id = 'tenor_slider_output_1',
                        ),

                        dcc.RangeSlider(
                            id='tenor_slider_1',
                            min = 0,
                            max = 71,
                            value = [0,71],
                            marks = {
                                    0 :{'label': '0D'},
                                    30:{'label': '1M'},
                                    41:{'label': '12M'},
                                    46:{'label': '5Y'},
                                    51:{'label': '10Y'},
                                    61:{'label': '20Y'},
                                    71:{'label': '30Y'},
                                },
                            allowCross=False
                        ),
                        dcc.Checklist(
                            id='show_total',
                            options=[
                                {'label': '  Mostrar total', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Loading(id = "loading-icon-1", children=[html.Div(dcc.Graph(id='fig_1'))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        html.P(
                            children = 'Filtrar por rango de tenors:',
                            id = 'tenor_slider_output_6',
                        ),
                        dcc.RangeSlider(
                            id='tenor_slider_6',
                            min = 0,
                            max = 71,
                            value = [0,71],
                            marks = {
                                    0 :{'label': '0D'},
                                    30:{'label': '1M'},
                                    41:{'label': '12M'},
                                    46:{'label': '5Y'},
                                    51:{'label': '10Y'},
                                    61:{'label': '20Y'},
                                    71:{'label': '30Y'},
                                },
                            allowCross=False
                        ),
                        dcc.Checklist(
                            id='show_total_6',
                            options=[
                                {'label': '  Mostrar total', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Loading(id = "loading-icon-6", children=[html.Div(dcc.Graph(id='fig_6'))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div( [
                    html.Div(
                        [
                        dcc.Checklist(
                            id='show_total_7',
                            options=[
                                {'label': '  Mostrar acumulado', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Loading(id = "loading-icon-7", children=[dcc.Graph(id='fig_7')], type="circle"),
                        ],className="pretty_container"
                    )
                ],id='div_7')
                ],className="eight columns")
        ], className='row'),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id='dropdown_6',
                            options=b,
                            value=['1M', '12M','5Y'],
                            multi=True
                        ), 
                        dcc.Checklist(
                            id='cumulative_2',
                            options=[
                                {'label': ' Mostrar acumulado', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Loading(id = "loading-icon-2", children=[html.Div(dcc.Graph(id='fig_2'))], type="circle")
                    ],
                    className="pretty_container six columns"),
                html.Div(
                    [
                        dcc.Dropdown(
                            id='dropdown_5',
                            options=b,
                            value=['1M', '12M','5Y'],
                            multi=True
                        ), 
                        dcc.Checklist(
                            id='cumulative_5',
                            options=[
                                {'label': ' Mostrar acumulado', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Loading(id = "loading-icon-5", children=[html.Div(dcc.Graph(id='fig_5'))], type="circle")
                    ],
                    className="pretty_container six columns"),
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                [
                        html.P(
                            children = 'Filtrar por rango de tenors:',
                            id = 'tenor_slider_output_3',
                        ),

                        dcc.RangeSlider(
                            id='tenor_slider_3',
                            min = 0,
                            max = 71,
                            value = [0,71],
                            marks = {
                                    0 :{'label': '0D'},
                                    30:{'label': '1M'},
                                    41:{'label': '12M'},
                                    46:{'label': '5Y'},
                                    51:{'label': '10Y'},
                                    61:{'label': '20Y'},
                                    71:{'label': '30Y'},
                                },
                            allowCross=False
                        ),
                    dcc.Loading(id = "loading-icon-3", children=[html.Div(dcc.Graph(id='fig_3'))], type="circle")
                ],className="pretty_container five columns"),
                html.Div(
                [
                        html.P(
                            children = 'Filtrar por rango de tenors:',
                            id = 'tenor_slider_output_4',
                        ),
                        dcc.RangeSlider(
                            id='tenor_slider_4',
                            min = 0,
                            max = 71,
                            value = [0,71],
                            marks = {
                                    0 :{'label': '0D'},
                                    30:{'label': '1M'},
                                    41:{'label': '12M'},
                                    46:{'label': '5Y'},
                                    51:{'label': '10Y'},
                                    61:{'label': '20Y'},
                                    71:{'label': '30Y'},
                                },
                            allowCross=False
                        ),
                        dcc.Checklist(
                            id='porcentaje_4',
                            options=[
                                {'label': ' Mostrar porcentaje', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                    dcc.Loading(id = "loading-icon-4", children=[html.Div(dcc.Graph(id='fig_4'))], type="circle")
                ],className="pretty_container seven columns"),

            ],
            className='row'
        ),
],id="mainContainer",style={"display": "flex","flex-direction": "column"}
)
 
#@app.callback(Output('options', 'children'), [Input('producto', 'value')])
#def load_tenors(producto):
#    hidden_df = api.query_by_daterange(producto,date(2020,1,3),today)
#    options = hidden_df['Tenor'].unique()
#    options = api.tenor_sort_3(options)
#    return json.dumps(options)

@app.callback(
    Output('tenor_slider_output_1', 'children'),
    [Input('tenor_slider_1', 'value'),
    #Input('options','children')
    ])
def update_output(value):#,options):
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]],a[value[1]])

@app.callback(
    Output('tenor_slider_output_3', 'children'),
    [Input('tenor_slider_3', 'value'),
    #Input('options','children')
    ])
def update_output(value):#,options):
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]],a[value[1]])

@app.callback(
    Output('tenor_slider_output_4', 'children'),
    [Input('tenor_slider_4', 'value'),
    #Input('options','children')
    ])
def update_output(value):#,options):
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]],a[value[1]])

@app.callback(
    Output('tenor_slider_output_6', 'children'),
    [Input('tenor_slider_6', 'value'),
    #Input('options','children')
    ])
def update_output(value):#,options):
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]],a[value[1]])


#@app.callback(
#    [Output('tenor_slider_1','min'),
#     Output('tenor_slider_1','max'),
#     Output('tenor_slider_1','value'),
#     Output('tenor_slider_3','min'),
#     Output('tenor_slider_3','max'),
#     Output('tenor_slider_3','value'),
#     Output('tenor_slider_4','min'),
#     Output('tenor_slider_4','max'),
#     Output('tenor_slider_4','value'),
#     Output('tenor_slider_6','min'),
#     Output('tenor_slider_6','max'),
#     Output('tenor_slider_6','value')],
#    [Input('options','children')]
#)
#
#def update_rangesliders(options):
#    options = json.loads(options)
#    a = {i:options[i] for i in range(len(options))}
#    return 0,len(a)-1,[0,len(a)-1],0,len(a)-1,[0,len(a)-1],0,len(a)-1,[0,len(a)-1],0,len(a)-1,[0,len(a)-1]

#@app.callback(
#    [Output('dropdown_5','options'),
#    Output('dropdown_5','value')],
#    [Input('options','children')]
#)
#
#def update_dropdown_5(options):
#    #options = json.loads(options)
#    #b = [{'label': options[i], 'value': options[i]} for i in range(len(options))]
#    return b,[b[0]['value'],b[-1]['value']]

#@app.callback(Output("loading-icon-1", "children"))
#@app.callback(Output("loading-icon-2", "children"))
#@app.callback(Output("loading-icon-3", "children"))
#@app.callback(Output("loading-icon-4", "children"))
#@app.callback(Output("loading-icon-6", "children"))
#@app.callback(Output("loading-icon-7", "children"))


@app.callback(
    Output(component_id='fig_1', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='start_date', component_property='date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_1', component_property='value'),
     Input(component_id='show_total', component_property='value'),
     #Input(component_id='options',component_property='children')
     ],
)
def update_graph_1(producto,periodo,start_date, usd, uf,tenor_slider_1,show_total):#options):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    tenors = (a[tenor_slider_1[0]],a[tenor_slider_1[1]])
    #print("start:" + str(producto))
    flag = False
    if show_total is not None:
        if len(show_total)!=0:
            flag = True
        
    #start = time.time()
    fig = api.box_plot_all(producto=producto,start_date=start_date,period=periodo,tenor_range=tenors,usd=usd,uf=uf,show_total=flag)
    #end = time.time()
    
    #print("overall time: " + str(producto), end - start)

    return fig

@app.callback(
    Output(component_id='fig_2', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='start_date', component_property='date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='cumulative_2', component_property='value'),
    Input(component_id='dropdown_6', component_property='value')]
)
def update_graph_2(producto,periodo,start_date, usd, uf,cumulative_2,tenors):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    flag = False
    if cumulative_2 is not None:
        if len(cumulative_2)!=0:
            flag = True

    fig = api.general_graph(producto=producto, tenors=tenors, start_date=start_date,period=periodo,usd=usd, uf=uf, cumulative = flag)

    return fig

@app.callback(
    Output(component_id='fig_3', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='start_date', component_property='date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_3', component_property='value'),
     #Input(component_id='options',component_property='children')
     ],
     
)
def update_graph_3(producto,start_date, usd, uf,tenor_slider_3):#,options):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    tenor_slider_3 = (a[tenor_slider_3[0]],a[tenor_slider_3[1]])
    fig = api.participation_graph(producto=producto, start_date=start_date, tenor_range=tenor_slider_3,usd=usd, uf=uf)

    return fig


@app.callback(
    Output(component_id='fig_4', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='start_date', component_property='date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_4',component_property='value'),
     Input(component_id='porcentaje_4',component_property='value'),
     #Input(component_id='options',component_property='children')
     ]
)
def update_graph_4(producto,start_date, usd, uf, tenor_slider_4,porcentaje_4):#,options):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    tenor_slider_4 =  (a[tenor_slider_4[0]],a[tenor_slider_4[1]])
    flag = False
    if porcentaje_4 is not None:
        if len(porcentaje_4) != 0:
            flag = True
    fig = api.participation_graph_by_date(producto=producto, start_date=start_date,tenor_range=tenor_slider_4,usd=usd, uf=uf,percent=flag)

    return fig

@app.callback(
    Output(component_id='fig_5', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='start_date', component_property='date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='cumulative_5', component_property='value'),
     Input(component_id='dropdown_5', component_property='value')]
)
def update_graph_5(producto,periodo,start_date, usd, uf,cumulative_5,dropdown_5):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    #print("start:" + str(producto))
    flag = False
    if cumulative_5 is not None:
        if len(cumulative_5)!=0:
            flag = True
    fig = api.tenor_graph(producto=producto, tenors=dropdown_5,start_date=start_date,period=periodo,usd=usd, uf=uf, cumulative = flag)

    return fig

@app.callback(
    Output(component_id='fig_6', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='start_date', component_property='date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_6', component_property='value'),
    Input(component_id='show_total_6', component_property='value'),
    #Input(component_id='options',component_property='children')
    ],
)
def update_graph_6(producto,start_date, usd, uf,tenor_slider_6,show_total_6):#,options):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    #options = json.loads(options)
    #a = {i:options[i] for i in range(len(options))}
    tenors = (a[tenor_slider_6[0]],a[tenor_slider_6[1]])
    flag = False
    if show_total_6 is not None:
        if len(show_total_6)!=0:
            flag = True
    fig = api.bar_by_tenor(producto=producto,start_date=start_date,tenor_range=tenors,usd=usd,uf=uf,show_total=flag)
    return fig

@app.callback(
    Output('div_7','children'),    
    [Input('producto','value'),
    Input('start_date','date')]
)

def upgrade_div_7(producto,start_date):
    if producto == 'NDF_USD_CLP':
        start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
        fig = api.graph_ndf_index(start_date)
        return   [
                    html.Div(
                        [
                        dcc.Checklist(
                            id='show_total_7',
                            options=[
                                {'label': '  Mostrar acumulado', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Loading(id = "loading-icon-7", children=[dcc.Graph(id='fig_7',figure=fig)], type="circle"),
                        ],className="pretty_container"
                    )
                ]
        return []


@app.callback(
    Output('fig_7','figure'),
    [Input('producto','value'),
    Input('start_date','date'),
    Input('show_total_7','value')]
)
def upgrade_graph_7(producto,start_date,show_total_7):
    if producto  == 'NDF_USD_CLP':
        flag = False
        if show_total_7 is not None:
            if len(show_total_7)!=0:
                flag = True
        start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
        fig = api.graph_ndf_index(start_date,flag)
        return fig
    else:
        return {}
        
@app.callback(
    [Output(component_id='table', component_property='data'),
    Output(component_id='table', component_property='columns'),
    Output(component_id='table', component_property='style_data_conditional')],
    [Input(component_id='producto', component_property='value'),
     Input(component_id='start_date', component_property='date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value')],
    [State(component_id='table', component_property='style_data_conditional')]
)
def update_table(producto,start_date, usd, uf, styles):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    df = api.informe(producto = producto, start_date = start_date, period = 'DAILY', usd = usd, uf = uf)
    if producto != 'NDF_USD_CLP':
        cols = [
                {"name": ['','Tenor'], 'id':"Tenor"},
                {"name": ['Actual','Volume'], 'id':"Volume"},
                {"name": ['Actual','DV01'], 'id':"DV01"},
                {"name": ['Actual','Zs'], 'id':"Zs"},
                {"name": ['Historic','Mean'], 'id':'Mean'},
                {"name": ['Historic','Highest'], 'id':"Highest"},
                {"name": ['Days Traded','Count'], 'id':'Trades'},
                {"name": ['Days Traded','%'], 'id':"Percent"},
        ]
    else:
        cols = [
                {"name": ['','Tenor'], 'id':"Tenor"},
                {"name": ['Actual','Volume'], 'id':"Volume"},
                {"name": ['Actual','Zs'], 'id':"Zs"},
                {"name": ['Historic','Mean'], 'id':'Mean'},
                {"name": ['Historic','Highest'], 'id':"Highest"},
                {"name": ['Days Traded','Count'], 'id':'Trades'},
                {"name": ['Days Traded','%'], 'id':"Percent"},
        ]

    df = df.to_dict('records')
    
    max_value = max(df, key=lambda val: int(val.get('Highest').replace(',','')) if val.get('Tenor') != 'Total' else 0)

    styles.append({
        'if': {
            'column_id': 'Highest',
            'filter_query': '{{{}}} eq {}'.format('Highest', max_value.get('Highest'))
        },
        'backgroundColor': 'yellow'
    })
    return df,cols, styles


if __name__ == '__main__':
    app.run_server(debug=True)