
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from api import tseries_clf_clp, bar_by_tenor, general_graph
from datetime import date, timedelta, datetime, time
today = date.today()
shift = timedelta(max(1, (today.weekday() + 6) % 7 - 3))
today = today - shift

start_date = today-timedelta(days=2*30)
end_date = today

usd = 800
uf = 29000


fig = tseries_clf_clp(start_date, end_date, usd, uf)

fig_clp = bar_by_tenor('CLP_CAM', date(2020, 8, 3), date(2020, 8, 7),
                       None, usd, uf, show_total=False, report=True)
fig_clf = bar_by_tenor('CLF_CAM', date(2020, 8, 3), date(2020, 8, 7),
                       None, usd, uf, show_total=False, report=True)


fig_ndf = general_graph('NDF_USD_CLP', ['All'], start_date,
                        end_date, 'DAILY', usd, uf, cumulative=False, report=True)

fig_ndf_tenor = bar_by_tenor('NDF_USD_CLP', date(2020, 8, 3), date(2020, 8, 7),
                             None, usd, uf, show_total=False, report=True)

fig_basis = general_graph('BASIS', ['All'], start_date,
                          end_date, 'DAILY', usd, uf, cumulative=False, report=True)

fig_basis_tenor = bar_by_tenor('BASIS', date(2020, 8, 3), date(2020, 8, 7),
                               None, usd, uf, show_total=False, report=True)


report = html.Div(
    [
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
        html.Div(
            [
                dcc.Loading(
                    id="Rloading-icon-4", children=[html.Div(dcc.Graph(id='Rfig_4', figure=fig_ndf))], type="circle")
            ],
            className="pretty_container", style={'page-break-before': 'always'}),
        html.Div(
            [
                dcc.Loading(
                    id="Rloading-icon-5", children=[html.Div(dcc.Graph(id='Rfig_5', figure=fig_ndf_tenor))], type="circle")
            ],
            className="pretty_container"),

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
    ]
)
