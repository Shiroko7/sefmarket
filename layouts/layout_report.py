
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from datetime import date

report = html.Div(
    [
        # PAGE 1
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2('Reporte CFTC'),
                                html.H6(date.today()),
                            ], className='twelve columns', style={'textAlign': 'center'}
                        )
                    ], id='header', className='row',
                ),
                html.Label('USD', className='no-print'),
                dcc.Input(id='usd_resumen', value='800', type='number', style={
                    'text-align': 'right', 'margin-right': '2000px'}, className='no-print'),
                html.Label('UF', className='no-print'),
                dcc.Input(id='uf_resumen', value='29000', type='number', style={
                    'text-align': 'right'}, className='no-print'),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-1", children=[html.Div(dcc.Graph(id='Rfig_1'))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-2", children=[html.Div(dcc.Graph(id='Rfig_2'))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-3", children=[html.Div(dcc.Graph(id='Rfig_3'))], type="circle")
                    ],
                    className="pretty_container"),

            ], className='Parent'
        ),

        # PAGE 2
        html.Div(
            [
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-6", children=[html.Div(dcc.Graph(id='Rfig_4'))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-7", children=[html.Div(dcc.Graph(id='Rfig_5'))], type="circle")
                    ],
                    className="pretty_container"),


            ], className='Parent'
        ),

        # PAGE 3
        html.Div(
            [
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-4", children=[html.Div(dcc.Graph(id='Rfig_6'))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-5", children=[html.Div(dcc.Graph(id='Rfig_7'))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-6", children=[html.Div(dcc.Graph(id='Rfig_8'))], type="circle")
                    ],
                    className="pretty_container"),

                html.Div(
                    [
                        html.Div([
                                  html.Div([html.P('Fuente: CFTC')],
                                           className='Fuente'),
                                  html.P('Este archivo es confidencial y destinado únicamente para uso interno.', style={'textAlign': 'right', 'fontStyle': 'italic'
                                                                                                                         }), ], className='twelve columns')
                    ],
                    className="foot row",
                ),
            ], className='Parent'
        )
    ]

)
