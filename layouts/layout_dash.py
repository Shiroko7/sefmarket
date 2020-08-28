
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from datetime import date, timedelta, datetime, time
today = date.today()
shift = timedelta(max(1, (today.weekday() + 6) % 7 - 3))
today = today - shift


options = [str(i)+'D' for i in range(0, 30)] + [str(i) +
                                                'M' for i in range(1, 13)] + [str(i)+'Y' for i in range(1, 31)]
a = {i: options[i] for i in range(len(options))}
b = [{'label': options[i], 'value': options[i]}
     for i in range(len(options))] + [{'label': 'All', 'value': 'All'}]


#import json
#import dash_dangerously_set_inner_html


# should really not be here
# VALID_USERNAME_PASSWORD_PAIRS = {
#    'bancochile': 'bancochile'
# }
# external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
#               "https://codepen.io/bcd/pen/YaXojL.js"]

# auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS
# )

dash = html.Div(children=[
    # html.Div(
    #    [
    #        dbc.Button("Exportar a PDF", id="open", style={
    #            'position': "absolute", 'top': '-40', 'right': '0'}),
    #        dbc.Modal(
    #            [
    #                dbc.ModalHeader("Exportar a PDF"),
    #                dbc.ModalBody(
    #                    [
    #                        html.A(['Generate PDF'], id="pdf-button",
    #                               className="button no-print print", style={'margin': '0 auto'}),
    #                        dcc.Loading(children=[html.Div(children=[html.A(['Download PDF'], id="download-pdf-button", href='NONE',
    #                                                                        download='report.pdf', className="button no-print print", hidden=True)], id='pdf-div', style={'margin': '0 auto'})]),
    #                        html.P("Puede demorar varios minutos."),
    #                        html.P(
    #                            "Por favor no cierre mientras se este cargando.")
    #                    ], id='modal-body'
    #                ),
    #                dbc.ModalFooter(
    #                    dbc.Button("Close", id="close",
    #                               className="ml-auto")
    #                ),
    #            ],
    #            id="modal",
    #        ),
    #    ]
    # ),
    html.Div(
        [
            html.Div(
                [
                    html.H2('SEF Market Data Activity',),
                    html.H6('Versión 3.1.0', className='no-print'),
                ], className='twelve columns', style={'text-align': 'center'}
            )
        ], id='header', className='row',
    ),
    html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Link('Reporte semanal', href='/report'),
                            html.Label(
                                'Producto', className="control_label"),
                            dcc.Dropdown(
                                id='producto',
                                options=[
                                    {'label': 'NDF USD-CLP',
                                     'value': 'NDF_USD_CLP'},
                                    {'label': 'CLP CAMARA',
                                     'value': 'CLP_CAM'},
                                    {'label': 'UF CAMARA', 'value': 'CLF_CAM'},
                                    {'label': 'BASIS SWAP', 'value': 'BASIS'}
                                ],
                                clearable=False,
                                value='CLP_CAM',
                            ),
                            html.Label(
                                'Periodo', className="control_label"),
                            dcc.Dropdown(
                                id='periodo',
                                options=[
                                    {'label': 'Diario', 'value': 'DAILY'},
                                    {'label': 'Semanal', 'value': 'WEEKLY'},
                                    #{'label': 'Mensual', 'value': 'MONTHLY'},
                                ],
                                clearable=False,
                                value='DAILY',
                            ),
                            html.Label('Seleccionar rango de data',
                                       className="control_label"),
                            dcc.DatePickerRange(
                                id='daterange',
                                first_day_of_week=1,
                                min_date_allowed=datetime(2020, 1, 3),
                                max_date_allowed=today+timedelta(days=1),
                                initial_visible_month=today,
                                start_date=datetime(2020, 1, 3),
                                end_date=today,
                                display_format='Do MMM, YY',
                            ),
                        ], className="pretty_container no-print"),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label('USD'),
                                    html.Label('UF')
                                ], style={'margin': '10px'}
                            ),

                            html.Div(
                                [
                                    dcc.Input(id='usd', value='750', type='number', style={
                                        'text-align': 'right', 'margin-right': '2000px'}),
                                    dcc.Input(id='uf', value='28663', type='number', style={
                                        'text-align': 'right'})
                                ], style={'margin-left': '20px'}
                            ),
                        ], className="row pretty_container no-print"
                    ),
                    dcc.Loading(
                        [
                            dash_table.DataTable(
                                id='table',
                                style_table={
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
                        ],
                        id="loading-icon-0", type="dot"
                    ),
                ], className="four columns"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                children='Filtrar por rango de tenors:',
                                id='tenor_slider_output_1',
                                className="no-print"
                            ),

                            dcc.RangeSlider(
                                id='tenor_slider_1',
                                min=0,
                                max=71,
                                value=[0, 71],
                                marks={
                                    0: {'label': '0D'},
                                    30: {'label': '1M'},
                                    41: {'label': '12M'},
                                    46: {'label': '5Y'},
                                    51: {'label': '10Y'},
                                    61: {'label': '20Y'},
                                    71: {'label': '30Y'},
                                },
                                allowCross=False,
                                className="no-print"
                            ),
                            dcc.Checklist(
                                id='show_total',
                                options=[
                                    {'label': '  Mostrar total', 'value': 'True'}
                                ],
                                className="dcc_control no-print"
                            ),
                            dcc.Loading(
                                id="loading-icon-1", children=[html.Div(dcc.Graph(id='fig_1'))], type="circle")
                        ],
                        className="pretty_container"),
                    html.Div(
                        [
                            html.P(
                                children='Filtrar por rango de tenors:',
                                id='tenor_slider_output_6',
                                className='no-print'
                            ),
                            dcc.RangeSlider(
                                id='tenor_slider_6',
                                min=0,
                                max=71,
                                value=[0, 71],
                                marks={
                                    0: {'label': '0D'},
                                    30: {'label': '1M'},
                                    41: {'label': '12M'},
                                    46: {'label': '5Y'},
                                    51: {'label': '10Y'},
                                    61: {'label': '20Y'},
                                    71: {'label': '30Y'},
                                },
                                allowCross=False,
                                className="no-print"
                            ),
                            dcc.Checklist(
                                id='show_total_6',
                                options=[
                                    {'label': '  Mostrar total', 'value': 'True'}
                                ],
                                className="dcc_control no-print"
                            ),
                            dcc.Loading(
                                id="loading-icon-6", children=[html.Div(dcc.Graph(id='fig_6'))], type="circle")
                        ],
                        className="pretty_container"),
                    html.Div([
                        html.Div(
                            [
                                dcc.Checklist(
                                    id='show_total_7',
                                    options=[
                                        {'label': '  Mostrar acumulado',
                                         'value': 'True'}
                                    ],
                                    className="dcc_control no-print"
                                ),
                                dcc.Loading(
                                    id="loading-icon-7", children=[dcc.Graph(id='fig_7')], type="circle"),
                            ], className="pretty_container"
                        )
                    ], id='div_7'),
                    html.Div(
                        [
                            dcc.Loading(
                                id="loading-icon-8", children=[dash_table.DataTable(id='table_2')], type="dot")
                        ], id='div_8'
                    )
                ], className="eight columns")
        ], className='row page'),
    html.Div(
        [
            html.Div(
                [
                    dcc.Dropdown(
                        id='dropdown_6',
                        options=b,
                        value=['All'],
                        multi=True,
                        className="no-print"
                    ),
                    dcc.Checklist(
                        id='cumulative_2',
                        options=[
                            {'label': ' Mostrar acumulado', 'value': 'True'}
                        ],
                        className="dcc_control no-print"
                    ),
                    dcc.Loading(
                        id="loading-icon-2", children=[html.Div(dcc.Graph(id='fig_2'))], type="circle")
                ],
                className="pretty_container six columns"),
            html.Div(
                [
                    dcc.Dropdown(
                        id='dropdown_5',
                        options=b,
                        value=['1M', '12M', '5Y', 'All'],
                        multi=True,
                        className="no-print"
                    ),
                    dcc.Checklist(
                        id='cumulative_5',
                        options=[
                            {'label': ' Mostrar acumulado', 'value': 'True'}
                        ],
                        className="dcc_control no-print"
                    ),
                    dcc.Loading(
                        id="loading-icon-5", children=[html.Div(dcc.Graph(id='fig_5'))], type="circle")
                ],
                className="pretty_container six columns"),
        ],
        className='row',
    ),
    html.Div(
        [
            html.Div(
                [
                    html.P(
                        children='Filtrar por rango de tenors:',
                        id='tenor_slider_output_3',
                        className="no-print",
                    ),

                    dcc.RangeSlider(
                        id='tenor_slider_3',
                        min=0,
                        max=71,
                        value=[0, 71],
                        marks={
                            0: {'label': '0D'},
                            30: {'label': '1M'},
                            41: {'label': '12M'},
                            46: {'label': '5Y'},
                            51: {'label': '10Y'},
                            61: {'label': '20Y'},
                            71: {'label': '30Y'},
                        },
                        allowCross=False,
                        className="no-print"
                    ),
                    dcc.Loading(
                        id="loading-icon-3", children=[html.Div(dcc.Graph(id='fig_3'))], type="circle")
                ], className="pretty_container five columns"),
            html.Div(
                [
                    html.P(
                        children='Filtrar por rango de tenors:',
                        id='tenor_slider_output_4',
                        className='no-print'
                    ),
                    dcc.RangeSlider(
                        id='tenor_slider_4',
                        min=0,
                        max=71,
                        value=[0, 71],
                        marks={
                            0: {'label': '0D'},
                            30: {'label': '1M'},
                            41: {'label': '12M'},
                            46: {'label': '5Y'},
                            51: {'label': '10Y'},
                            61: {'label': '20Y'},
                            71: {'label': '30Y'},
                        },
                        allowCross=False,
                        className="no-print"
                    ),
                    dcc.Checklist(
                        id='porcentaje_4',
                        options=[
                            {'label': ' Mostrar porcentaje', 'value': 'True'}
                        ],
                        className="dcc_control no-print"
                    ),
                    dcc.Loading(
                        id="loading-icon-4", children=[html.Div(dcc.Graph(id='fig_4'))], type="circle")
                ], className="pretty_container seven columns"),
        ],
        className='row page',
    ),
]  # ,id="mainContainer",style={"display": "flex","flex-direction": "column"}
)
