# -*- coding: utf-8 -*- 

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html
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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(children=
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H2('SEF Market Data Activity',),
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
                            dcc.Dropdown(
                                id='fecha',
                                options=[
                                    {'label': 'Desde 01 Enero', 'value': date(2020,1,3)},
                                    {'label': '1 Semana', 'value': today-timedelta(days=7)},
                                    {'label': '1 Mes', 'value': today-timedelta(days=30)},
                                ],
                                value=date(2020,1,3),             
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label('USD',className="control_label"),
                                            dcc.Input(id='usd', value='800', type='number', className = "dcc_control"),
                                        ],style={"width":"49%"}
                                    ),
                                    html.Div(
                                        [
                                            html.Label('UF',className="control_label"),
                                            dcc.Input(id='uf', value='28000', type='number', className = "dcc_control"),
                                        ],style={"width":"49%"}
                                    )
                                ], className = 'row'
                            ),
                        ], className = "pretty_container"),
                    dash_table.DataTable(
                        id='table',
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
                                    'column_id': 'SD',
                                    'filter_query': '{SD} > 0.0'
                                },
                                'color': 'green',
                            },
                            {
                                'if': {
                                    'column_id': 'SD',
                                    'filter_query': '{SD} < 0.0'
                                },
                                'color': 'red',
                            },
                        ]
                    ),
                ],className="four columns"
            ),

            html.Div(
                [
                html.Div(
                    [
                        html.P(
                            children = 'Filtrar por rango de tenors:',
                            #className="control_label",
                            id = 'tenor_slider_output_1',
                        ),

                        dcc.RangeSlider(
                            id='tenor_slider_1',
                            #className="dcc_control",
                            min=0,
                            max=71,
                            value=[0,71],
                            allowCross=False
                        ),
                        dcc.Checklist(
                            id='show_total',
                            options=[
                                {'label': 'Mostrar total', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Graph(id='fig_1'),
                    ],
                    className="pretty_container"),
                    
                html.Div(
                    [
                        dcc.Checklist(
                            id='cumulative_2',
                            options=[
                                {'label': 'Mostrar acumulado', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.Graph(id='fig_2')
                    ],
                    className="pretty_container")
                ],className="eight columns")
        ], className='row'),

        html.Div(
            [
                html.Div(
                [
                        html.P(
                            children = 'Filtrar por rango de tenors:',
                            #className="control_label",
                            id = 'tenor_slider_output_3',
                        ),

                        dcc.RangeSlider(
                            id='tenor_slider_3',
                            #className="dcc_control",
                            min=0,
                            max=71,
                            value=[0,71],
                            allowCross=False
                        ),
                    dcc.Graph(id='fig_3')
                ],className="pretty_container five columns"),
                html.Div(
                [
                        html.P(
                            children = 'Filtrar por rango de tenors:',
                            #className="control_label",
                            id = 'tenor_slider_output_4',
                        ),
                        dcc.Checklist(
                            id='porcentaje_4',
                            options=[
                                {'label': 'Mostrar porcentaje', 'value': 'True'}
                            ],
                            className="dcc_control"
                        ),
                        dcc.RangeSlider(
                            id='tenor_slider_4',
                            #className="dcc_control",
                            min=0,
                            max=71,
                            value=[0,71],
                            allowCross=False
                        ),
                    dcc.Graph(id='fig_4')
                ],className="pretty_container seven columns"),

            ],
            className='row'
        )
])

@app.callback(
    Output('tenor_slider_output_1', 'children'),
    [Input('tenor_slider_1', 'value')])
def update_output(value):
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]],a[value[1]])

@app.callback(
    Output('tenor_slider_output_3', 'children'),
    [Input('tenor_slider_3', 'value')])
def update_output(value):
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]],a[value[1]])

@app.callback(
    Output('tenor_slider_output_4', 'children'),
    [Input('tenor_slider_4', 'value')])
def update_output(value):
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]],a[value[1]])


@app.callback(
    Output(component_id='fig_1', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='fecha', component_property='value'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_1', component_property='value'),
     Input(component_id='show_total', component_property='value')],
)
def update_graph_1(producto,periodo,fecha, usd, uf,tenor_slider_1,show_total):
    usd = int(usd)
    uf = int(uf)
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    tenors = (a[tenor_slider_1[0]],a[tenor_slider_1[1]])
    #print("start:" + str(producto))
    flag = False
    if show_total is not None:
        if len(show_total)!=0:
            flag = True
        
    #start = time.time()
    fig = api.box_plot_all(producto=producto,start_date=fecha,period=periodo,tenor_range=tenors,usd=usd,uf=uf,show_total=flag)
    #end = time.time()
    
    #print("overall time: " + str(producto), end - start)

    return fig

@app.callback(
    Output(component_id='fig_2', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='fecha', component_property='value'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='cumulative_2', component_property='value')]
)
def update_graph_2(producto,periodo,fecha, usd, uf,cumulative_2):
    usd = int(usd)
    uf = int(uf)
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    #print("start:" + str(producto))
    flag = False
    if cumulative_2 is not None:
        if len(cumulative_2)!=0:
            flag = True

    start = time.time()
    fig = api.general_graph(producto=producto, tenor='All', start_date=fecha,period=periodo,usd=usd, uf=uf, cumulative = flag)
    end = time.time()
    
    #print("overall time: " + str(producto), end - start)

    return fig

@app.callback(
    Output(component_id='fig_3', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='fecha', component_property='value'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_3', component_property='value')],
     
)
def update_graph_3(producto,fecha, usd, uf,tenor_slider_3):
    usd = int(usd)
    uf = int(uf)
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    tenor_slider_3 = (a[tenor_slider_3[0]],a[tenor_slider_3[1]])
    #print("start:" + str(producto))

    #start = time.time()
    fig = api.participation_graph(producto=producto, start_date=fecha, tenor_range=tenor_slider_3,usd=usd, uf=uf)
    #end = time.time()
    
    #print("overall time: " + str(producto), end - start)

    return fig


@app.callback(
    Output(component_id='fig_4', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='fecha', component_property='value'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_4',component_property='value'),
     Input(component_id='porcentaje_4',component_property='value'),]
)
def update_graph_4(producto,fecha, usd, uf, tenor_slider_4,porcentaje_4):
    usd = int(usd)
    uf = int(uf)
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    tenor_slider_4 =  (a[tenor_slider_4[0]],a[tenor_slider_4[1]])
    flag = False
    if porcentaje_4 is not None:
        if len(porcentaje_4) != 0:
            flag = True
    #print("start:" + str(producto))

    #start = time.time()
    fig = api.participation_graph_by_date(producto=producto, start_date=fecha,tenor_range=tenor_slider_4,usd=usd, uf=uf,percent=flag)
    #end = time.time()

    #print("overall time: " + str(producto), end - start)

    return fig

@app.callback(
    [Output(component_id='table', component_property='data'),
    Output(component_id='table', component_property='columns'),
    Output(component_id='table', component_property='style_data_conditional')],
    [Input(component_id='producto', component_property='value'),
     Input(component_id='fecha', component_property='value'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value')],
    [State(component_id='table', component_property='style_data_conditional')]
)
def update_table(producto,fecha, usd, uf, styles):
    usd = int(usd)
    uf = int(uf)
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    df = api.informe(producto = producto, start_date = date(2020,1,3), period = 'DAILY', usd = usd, uf = uf)
    cols = [{"name": i, "id": i} for i in list(df.columns)]
    df = df.to_dict('records')

    max_value = max(df, key=lambda val: val.get('Highest'))

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