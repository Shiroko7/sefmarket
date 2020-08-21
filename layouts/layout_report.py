
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from utils.plots import tseries_clf_clp, bar_by_tenor, general_graph, graph_ndf_index
from datetime import date, timedelta, datetime, time
today = date.today()
shift = timedelta(max(1, (today.weekday() + 6) % 7 - 3))
today = today - shift

start_date = today-timedelta(days=2*30)
end_date = today

start_week = date(2020, 8, 10)
end_week = date(2020, 8, 14)

usd = 800
uf = 29000


fig = tseries_clf_clp(start_date, end_date, usd, uf)

fig_clp = bar_by_tenor('CLP_CAM', start_week, end_week,
                       None, usd, uf, show_total=False, report=True)
fig_clf = bar_by_tenor('CLF_CAM', start_week, end_week,
                       None, usd, uf, show_total=False, report=True)


fig_basis = general_graph('BASIS', ['All'], start_date,
                          end_date, 'DAILY', usd, uf, cumulative=False, report=True)

fig_basis_tenor = bar_by_tenor('BASIS', start_week, end_week,
                               None, usd, uf, show_total=False, report=True)

fig_ndf = general_graph('NDF_USD_CLP', ['All'], start_date,
                        end_date, 'DAILY', usd, uf, cumulative=False, report=True)

fig_ndf_tenor = bar_by_tenor('NDF_USD_CLP', start_week, end_week,
                             None, usd, uf, show_total=False, report=True)

fig_ndf_index = graph_ndf_index(
    start_date, end_date, cumulative=False, report=True)

report = html.Div(
    [
        # PAGE 1
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2('DV01 Transado Mercado Local'),
                                html.H6(str(end_date)),
                            ], className='twelve columns', style={'textAlign': 'center'}
                        )
                    ], id='header', className='row',
                ),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-1", children=[html.Div(dcc.Graph(id='Rfig_1', figure=fig))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-2", children=[html.Div(dcc.Graph(id='Rfig_2', figure=fig_clp))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-3", children=[html.Div(dcc.Graph(id='Rfig_3', figure=fig_clf))], type="circle")
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
                            id="Rloading-icon-6", children=[html.Div(dcc.Graph(id='Rfig_6', figure=fig_basis))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-7", children=[html.Div(dcc.Graph(id='Rfig_7', figure=fig_basis_tenor))], type="circle")
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
                            id="Rloading-icon-4", children=[html.Div(dcc.Graph(id='Rfig_4', figure=fig_ndf))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-5", children=[html.Div(dcc.Graph(id='Rfig_5', figure=fig_ndf_tenor))], type="circle")
                    ],
                    className="pretty_container"),
                html.Div(
                    [
                        dcc.Loading(
                            id="Rloading-icon-6", children=[html.Div(dcc.Graph(id='Rfig_6', figure=fig_ndf_index))], type="circle")
                    ],
                    className="pretty_container"),

                html.Div(
                    [
                        html.Div([html.Img(src='assets/Banco_de_Chile_Logo.png',
                                           style={'height': '24px', 'width': '144px'}),
                                  html.P('Este archivo es confidencial y destinado únicamente para uso interno.', style={'textAlign': 'right', 'fontStyle': 'italic'
                                                                                                                         }), ], className='twelve columns')
                    ],
                    className="foot row",
                ),
            ], className='Parent'
        )
    ]

)
