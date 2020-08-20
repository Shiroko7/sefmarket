from app import app
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import dash_html_components as html

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import numpy as np

import utils.plots as plots
import utils.tools as tools

import plotly.io
from datetime import date, timedelta, datetime, time


import base64
import chart_studio.plotly as py

import time
import os

# para generar pdfs
from xhtml2pdf import pisa             # import python module
import pdfkit


options = [str(i)+'D' for i in range(0, 30)] + [str(i) +
                                                'M' for i in range(1, 13)] + [str(i)+'Y' for i in range(1, 31)]
a = {i: options[i] for i in range(len(options))}
b = [{'label': options[i], 'value': options[i]}
     for i in range(len(options))] + [{'label': 'All', 'value': 'All'}]

STATIC_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'static')


@app.callback(
    Output('tenor_slider_output_1', 'children'),
    [Input('tenor_slider_1', 'value')]
)
def update_output(value):
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]], a[value[1]])


@app.callback(
    Output('tenor_slider_output_3', 'children'),
    [Input('tenor_slider_3', 'value')]
)
def update_output(value):
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]], a[value[1]])


@app.callback(
    Output('tenor_slider_output_4', 'children'),
    [Input('tenor_slider_4', 'value')]
)
def update_output(value):
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]], a[value[1]])


@app.callback(
    Output('tenor_slider_output_6', 'children'),
    [Input('tenor_slider_6', 'value'), ]
)
def update_output(value):
    return 'Filtrar por rango de tenors: {}-{}'.format(a[value[0]], a[value[1]])


@app.callback(
    Output(component_id='fig_1', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='daterange', component_property='start_date'),
     Input(component_id='daterange', component_property='end_date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_1', component_property='value'),
     Input(component_id='show_total', component_property='value'),
     ],
)
# options):
def update_graph_1(producto, periodo, start_date, end_date, usd, uf, tenor_slider_1, show_total):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
    tenors = (a[tenor_slider_1[0]], a[tenor_slider_1[1]])
    flag = False
    if show_total is not None:
        if len(show_total) != 0:
            flag = True

    fig = plots.box_plot_all(producto=producto, start_date=start_date, end_date=end_date,
                             period=periodo, tenor_range=tenors, usd=usd, uf=uf, show_total=flag)

    return fig


@app.callback(
    Output(component_id='fig_2', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='daterange', component_property='start_date'),
     Input(component_id='daterange', component_property='end_date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='cumulative_2', component_property='value'),
     Input(component_id='dropdown_6', component_property='value')]
)
def update_graph_2(producto, periodo, start_date, end_date, usd, uf, cumulative_2, tenors):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
    flag = False
    if cumulative_2 is not None:
        if len(cumulative_2) != 0:
            flag = True

    fig = plots.general_graph(producto=producto, tenors=tenors, start_date=start_date,
                              end_date=end_date, period=periodo, usd=usd, uf=uf, cumulative=flag)

    return fig


@app.callback(
    Output(component_id='fig_3', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='daterange', component_property='start_date'),
     Input(component_id='daterange', component_property='end_date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_3', component_property='value'),
     ],

)
def update_graph_3(producto, start_date, end_date, usd, uf, tenor_slider_3):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
    tenors_3 = (a[tenor_slider_3[0]], a[tenor_slider_3[1]])
    fig = plots.participation_graph(producto=producto, start_date=start_date,
                                    end_date=end_date, tenor_range=tenors_3, usd=usd, uf=uf)

    return fig


@app.callback(
    Output(component_id='fig_4', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='daterange', component_property='start_date'),
     Input(component_id='daterange', component_property='end_date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_4', component_property='value'),
     Input(component_id='porcentaje_4', component_property='value'),
     ]
)
def update_graph_4(producto, start_date, end_date, usd, uf, tenor_slider_4, porcentaje_4):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
    tenors_4 = (a[tenor_slider_4[0]], a[tenor_slider_4[1]])
    flag = False
    if porcentaje_4 is not None:
        if len(porcentaje_4) != 0:
            flag = True
    fig = plots.participation_graph_by_date(
        producto=producto, start_date=start_date, end_date=end_date, tenor_range=tenors_4, usd=usd, uf=uf, percent=flag)

    return fig


@app.callback(
    Output(component_id='fig_5', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='daterange', component_property='start_date'),
     Input(component_id='daterange', component_property='end_date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='cumulative_5', component_property='value'),
     Input(component_id='dropdown_5', component_property='value')]
)
def update_graph_5(producto, periodo, start_date, end_date, usd, uf, cumulative_5, dropdown_5):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
    flag = False
    if cumulative_5 is not None:
        if len(cumulative_5) != 0:
            flag = True
    fig = plots.tenor_graph(producto=producto, tenors=dropdown_5, start_date=start_date,
                            end_date=end_date, period=periodo, usd=usd, uf=uf, cumulative=flag)

    return fig


@app.callback(
    Output(component_id='fig_6', component_property='figure'),
    [Input(component_id='producto', component_property='value'),
     Input(component_id='daterange', component_property='start_date'),
     Input(component_id='daterange', component_property='end_date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value'),
     Input(component_id='tenor_slider_6', component_property='value'),
     Input(component_id='show_total_6', component_property='value'),
     ],
)
def update_graph_6(producto, start_date, end_date, usd, uf, tenor_slider_6, show_total_6):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
    tenors_6 = (a[tenor_slider_6[0]], a[tenor_slider_6[1]])
    flag = False
    if show_total_6 is not None:
        if len(show_total_6) != 0:
            flag = True
    fig = plots.bar_by_tenor(producto=producto, start_date=start_date,
                             end_date=end_date, tenor_range=tenors_6, usd=usd, uf=uf, show_total=flag)
    return fig


@app.callback(
    Output('div_7', 'children'),
    [Input('producto', 'value'),
     Input('daterange', 'start_date'),
     Input('daterange', 'end_date')]
)
def upgrade_div_7(producto, start_date, end_date):
    if producto == 'NDF_USD_CLP':
        start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
        end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
        fig = plots.graph_ndf_index(start_date, end_date)
        return [
            html.Div(
                [
                    dcc.Checklist(
                        id='show_total_7',
                        options=[
                            {'label': '  Mostrar acumulado', 'value': 'True'}
                        ],
                        className="dcc_control"
                    ),
                    dcc.Loading(
                        id="loading-icon-7", children=[dcc.Graph(id='fig_7', figure=fig)], type="circle"),
                ], className="pretty_container"
            )
        ]
    else:
        return [html.Div(id='show_total_7')]


@app.callback(
    Output('fig_7', 'figure'),
    [Input('producto', 'value'),
     Input('daterange', 'start_date'),
     Input('daterange', 'end_date'),
     Input('show_total_7', 'value')]
)
def upgrade_graph_7(producto, start_date, end_date, show_total_7):
    if producto == 'NDF_USD_CLP':
        flag = False
        if show_total_7 is not None:
            if len(show_total_7) != 0:
                flag = True
        start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
        end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
        fig = plots.graph_ndf_index(start_date, end_date, flag)
        return fig
    else:
        return {}


@app.callback(
    [Output(component_id='table', component_property='data'),
     Output(component_id='table', component_property='columns'),
     Output(component_id='table', component_property='style_data_conditional')],
    [Input(component_id='producto', component_property='value'),
     Input(component_id='periodo', component_property='value'),
     Input(component_id='daterange', component_property='start_date'),
     Input(component_id='daterange', component_property='end_date'),
     Input(component_id='usd', component_property='value'),
     Input(component_id='uf', component_property='value')],
    [State(component_id='table', component_property='style_data_conditional')]
)
def update_table(producto, period, start_date, end_date, usd, uf, styles):
    usd = int(usd)
    uf = int(uf)
    start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
    df = tools.informe(producto=producto, start_date=start_date,
                       end_date=end_date, period=period, usd=usd, uf=uf)
    if producto != 'NDF_USD_CLP':
        cols = [
            {"name": ['', 'Tenor'], 'id':"Tenor"},
            {"name": ['Actual', 'Volume'], 'id':"Volume"},
            {"name": ['Actual', 'DV01'], 'id':"DV01"},
            {"name": ['Actual', 'Zs'], 'id':"Zs"},
            {"name": ['Historic', 'Mean'], 'id':'Mean'},
            {"name": ['Historic', 'Highest'], 'id':"Highest"},
            {"name": ['Days Traded', 'Count'], 'id':'Trades'},
            {"name": ['Days Traded', '%'], 'id':"Percent"},
        ]
    else:
        cols = [
            {"name": ['', 'Tenor'], 'id':"Tenor"},
            {"name": ['Actual', 'Volume'], 'id':"Volume"},
            {"name": ['Actual', 'Zs'], 'id':"Zs"},
            {"name": ['Historic', 'Mean'], 'id':'Mean'},
            {"name": ['Historic', 'Highest'], 'id':"Highest"},
            {"name": ['Days Traded', 'Count'], 'id':'Trades'},
            {"name": ['Days Traded', '%'], 'id':"Percent"},
        ]

    df = df.to_dict('records')

    max_value = max(df, key=lambda val: int(val.get('Highest').replace(
        ',', '')) if val.get('Tenor') != 'Total' else 0)

    styles.append({
        'if': {
            'column_id': 'Highest',
            'filter_query': '{{{}}} eq {}'.format('Highest', max_value.get('Highest'))
        },
        'backgroundColor': 'yellow'
    })
    return df, cols, styles


@app.callback(
    Output('div_8', 'children'),
    [Input('producto', 'value'),
     Input('daterange', 'start_date'),
     Input('daterange', 'end_date')]
)
def load_table_2(producto, start_date, end_date):
    if producto == 'NDF_USD_CLP':
        start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
        end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
        df = plots.table_ndf_index(start_date=start_date, end_date=end_date)
        df = df.iloc[::-1]
        df = df.fillna(0.0)
        df['Zs'] = pd.Series(["{0:,.1f}".format(val)
                              for val in df['Zs']], index=df.index)
        df['Index'] = pd.Series(["{0:,.0f}".format(val)
                                 for val in df['Index']], index=df.index)
        df['Mean'] = pd.Series(["{0:,.0f}".format(val)
                                for val in df['Mean']], index=df.index)
        df['Date'] = df['Date'].astype(str)
        df['Date'] = df.apply(lambda x: x['Date'][0:10], axis=1)

        cols = [{'name': i, 'id': i} for i in list(df.columns)]
        df = df.to_dict('records')
        return [
            html.Div(
                [
                    dcc.Loading(id="loading-icon-8", children=[
                        dash_table.DataTable(id='table_2',
                                             data=df,
                                             columns=cols,
                                             style_table={
                                                 'box-sizing': 'border-box',
                                                 'overflowX': 'scroll'
                                             },
                                             style_header={
                                                 'fontWeight': 'bold',
                                                 'textAlign': 'center',
                                                 'padding-right': '0',
                                             },
                                             style_cell_conditional=[
                                                 {
                                                     'if': {'column_id': 'Date'},
                                                     'textAlign': 'center'
                                                 },
                                                 {
                                                     'if': {'column_id': 'Index'},
                                                     'textAlign': 'right',
                                                     'padding-right': '8%',
                                                 },
                                                 {
                                                     'if': {'column_id': 'Zs'},
                                                     'textAlign': 'center'
                                                 },
                                                 {
                                                     'if': {'column_id': 'Mean'},
                                                     'textAlign': 'right',
                                                     'padding-right': '8%',
                                                 },

                                             ],
                                             style_header_conditional=[
                                                 {
                                                     'if': {'column_id': 'Index'},
                                                     'textAlign': 'center',
                                                     'padding-right': '0',
                                                 },
                                                 {
                                                     'if': {'column_id': 'Mean'},
                                                     'textAlign': 'center',
                                                     'padding-right': '0',
                                                 },
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
                                             page_size=10,
                                             )
                    ], type="dot")
                ], id='div_8'
            )
        ]
    else:
        return [html.Div([])]


@app.callback(
    Output('table_2', 'data'),
    [Input('producto', 'value'),
     Input('daterange', 'start_date'),
     Input('daterange', 'end_date')]
)
def update_table_2(producto, start_date, end_date):
    if producto == 'NDF_USD_CLP':
        start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
        end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
        df = plots.table_ndf_index(start_date=start_date, end_date=end_date)
        df = df.iloc[::-1]
        df = df.fillna(0.0)
        df['Zs'] = pd.Series(["{0:,.1f}".format(val)
                              for val in df['Zs']], index=df.index)
        df['Index'] = pd.Series(["{0:,.0f}".format(val)
                                 for val in df['Index']], index=df.index)
        df['Mean'] = pd.Series(["{0:,.0f}".format(val)
                                for val in df['Mean']], index=df.index)
        df['Date'] = df['Date'].astype(str)
        df['Date'] = df.apply(lambda x: x['Date'][0:10], axis=1)

        df = df.to_dict('records')
        return df
    else:
        return []


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output('pdf-div', 'children'),
    [Input('pdf-button', 'n_clicks')],
    [
        State('table', 'data'),
        State('producto', 'value'),
        State('periodo', 'value'),
        State('daterange', 'start_date'),
        State('daterange', 'end_date'),
        State('usd', 'value'),
        State('uf', 'value'),
        State('tenor_slider_1', 'value'),
        State('show_total', 'value'),
        State(component_id='cumulative_2', component_property='value'),
        State(component_id='dropdown_6', component_property='value'),
        State(component_id='tenor_slider_3', component_property='value'),
        State(component_id='tenor_slider_4', component_property='value'),
        State(component_id='porcentaje_4', component_property='value'),
        State(component_id='cumulative_5', component_property='value'),
        State(component_id='dropdown_5', component_property='value'),
        State(component_id='tenor_slider_6', component_property='value'),
        State(component_id='show_total_6', component_property='value'),
        State('show_total_7', 'value')
    ]
)
def print_pdf(n_clicks, table, producto, periodo, start_date, end_date, usd, uf, tenor_slider_1, show_total, cumulative_2, dropdown_6, tenor_slider_3, tenor_slider_4, porcentaje_4, cumulative_5, dropdown_5, tenor_slider_6, show_total_6, show_total_7):
    if n_clicks is not None:
        request_id = str(time.time()).replace('.', '')

        usd = int(usd)
        uf = int(uf)
        start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
        end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')

        tenors_1 = (a[tenor_slider_1[0]], a[tenor_slider_1[1]])
        tenors_3 = (a[tenor_slider_3[0]], a[tenor_slider_3[1]])
        tenors_4 = (a[tenor_slider_4[0]], a[tenor_slider_4[1]])
        tenors_6 = (a[tenor_slider_6[0]], a[tenor_slider_6[1]])

        flag_show_total = False
        if show_total is not None:
            if len(show_total) != 0:
                flag_show_total = True

        flag_cumulative_2 = False
        if cumulative_2 is not None:
            if len(cumulative_2) != 0:
                flag_cumulative_2 = True
        flag_porcentaje_4 = False
        if porcentaje_4 is not None:
            if len(porcentaje_4) != 0:
                flag_porcentaje_4 = True
        flag_cumulative_5 = False
        if cumulative_5 is not None:
            if len(cumulative_5) != 0:
                flag_cumulative_5 = True
        flag_show_total_6 = False
        if show_total_6 is not None:
            if len(show_total_6) != 0:
                flag_show_total_6 = True

        width = 1200
        height = 800
        df = pd.DataFrame.from_dict(table)
        u = df.index.get_level_values(0)
        if producto != 'NDF_USD_CLP':
            # resumen
            df = df.style.\
                applymap(tools.color_negative_red, subset=pd.IndexSlice[:, ['Zs']]).\
                apply(tools.oddness, axis=1).\
                apply(tools.highlight_max, subset=pd.IndexSlice[u[:-1], ['Highest']], axis=0).\
                set_table_styles(tools.styles).\
                set_properties(**{'width': '150px'}).\
                set_properties(subset=["DV01", "Highest", "Mean", "Percent", "Zs"], **{'text-align': 'center'}).\
                set_properties(subset=["Trades", "Volume"], **{'text-align': 'right', 'padding-right': '80px', }).\
                set_properties(subset=["Tenor"], **{'text-align': 'left', 'padding-left': '82px'}).\
                hide_index()
            # figuras
            fig_1 = plots.box_plot_all(producto=producto, start_date=start_date, end_date=end_date,
                                       period=periodo, tenor_range=tenors_1, usd=usd, uf=uf, show_total=flag_show_total)
            fig_1.write_image("assets/fig_1_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_2 = plots.general_graph(producto=producto, tenors=dropdown_6, start_date=start_date,
                                        end_date=end_date, period=periodo, usd=usd, uf=uf, cumulative=flag_cumulative_2)
            fig_2.write_image("assets/fig_2_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_3 = plots.participation_graph(
                producto=producto, start_date=start_date, end_date=end_date, tenor_range=tenors_3, usd=usd, uf=uf)
            fig_3.write_image("assets/fig_3_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_4 = plots.participation_graph_by_date(
                producto=producto, start_date=start_date, end_date=end_date, tenor_range=tenors_4, usd=usd, uf=uf, percent=flag_porcentaje_4)
            fig_4.write_image("assets/fig_4_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_5 = plots.tenor_graph(producto=producto, tenors=dropdown_5, start_date=start_date,
                                      end_date=end_date, period=periodo, usd=usd, uf=uf, cumulative=flag_cumulative_5)
            fig_5.write_image("assets/fig_5_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_6 = plots.bar_by_tenor(producto=producto, start_date=start_date, end_date=end_date,
                                       tenor_range=tenors_6, usd=usd, uf=uf, show_total=flag_show_total_6)
            fig_6.write_image("assets/fig_6_"+request_id+".png",
                              width=width, height=height, scale=2)

            images = ["fig_1_"+request_id+".png", "fig_6_"+request_id+".png", "fig_2_"+request_id +
                      ".png", "fig_5_"+request_id+".png", "fig_3_"+request_id+".png", "fig_4_"+request_id+".png"]

        else:
            flag_show_total_7 = False
            if show_total_7 is not None:
                if len(show_total_7) != 0:
                    flag_show_total_7 = True
            # resumen
            df = df.style.\
                applymap(tools.color_negative_red, subset=pd.IndexSlice[:, ['Zs']]).\
                apply(tools.oddness, axis=1).\
                apply(tools.highlight_max, subset=pd.IndexSlice[u[:-1], ['Highest']], axis=0).\
                set_table_styles(tools.styles).\
                set_properties(**{'width': '150px'}).\
                set_properties(subset=["Highest", "Mean", "Percent", "Zs"], **{'text-align': 'center'}).\
                set_properties(subset=["Trades", "Volume"], **{'text-align': 'right', 'padding-right': '80px', }).\
                set_properties(subset=["Tenor"], **{'text-align': 'left', 'padding-left': '82px'}).\
                hide_index()

            # table 2

            df_2 = plots.table_ndf_index(
                start_date=start_date, end_date=end_date)
            df_2 = df_2.iloc[::-1]
            df_2 = df_2.iloc[:7]
            df_2 = df_2.fillna(0.0)
            df_2['Zs'] = pd.Series(["{0:,.1f}".format(val)
                                    for val in df_2['Zs']], index=df_2.index)
            df_2['Index'] = pd.Series(
                ["{0:,.0f}".format(val) for val in df_2['Index']], index=df_2.index)
            df_2['Mean'] = pd.Series(
                ["{0:,.0f}".format(val) for val in df_2['Mean']], index=df_2.index)
            df_2['Date'] = df_2['Date'].astype(str)
            df_2['Date'] = df_2.apply(lambda x: x['Date'][0:10], axis=1)
            df_2 = df_2.style.\
                applymap(tools.color_negative_red, subset=pd.IndexSlice[:, ['Zs']]).\
                apply(tools.oddness, axis=1).\
                set_table_styles(tools.styles).\
                set_properties(**{'width': '300px'}).\
                set_properties(subset=["Date", "Zs"], **{'text-align': 'center'}).\
                set_properties(
                    subset=["Index", "Mean"], **{'text-align': 'right', 'padding-right': '150px'})

            # figuras
            fig_1 = plots.box_plot_all(producto=producto, start_date=start_date, end_date=end_date,
                                       period=periodo, tenor_range=tenors_1, usd=usd, uf=uf, show_total=flag_show_total)
            fig_1.write_image("assets/fig_1_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_2 = plots.general_graph(producto=producto, tenors=dropdown_6, start_date=start_date,
                                        end_date=end_date, period=periodo, usd=usd, uf=uf, cumulative=flag_cumulative_2)
            fig_2.write_image("assets/fig_2_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_3 = plots.participation_graph(
                producto=producto, start_date=start_date, end_date=end_date, tenor_range=tenors_3, usd=usd, uf=uf)
            fig_3.write_image("assets/fig_3_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_4 = plots.participation_graph_by_date(
                producto=producto, start_date=start_date, end_date=end_date, tenor_range=tenors_4, usd=usd, uf=uf, percent=flag_porcentaje_4)
            fig_4.write_image("assets/fig_4_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_5 = plots.tenor_graph(producto=producto, tenors=dropdown_5, start_date=start_date,
                                      end_date=end_date, period=periodo, usd=usd, uf=uf, cumulative=flag_cumulative_5)
            fig_5.write_image("assets/fig_5_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_6 = plots.bar_by_tenor(producto=producto, start_date=start_date, end_date=end_date,
                                       tenor_range=tenors_6, usd=usd, uf=uf, show_total=flag_show_total_6)
            fig_6.write_image("assets/fig_6_"+request_id+".png",
                              width=width, height=height, scale=2)

            fig_7 = plots.graph_ndf_index(
                start_date=start_date, end_date=end_date, cumulative=flag_show_total_7)
            fig_7.write_image("assets/fig_7_"+request_id+".png",
                              width=width, height=height, scale=2)

            images = ["fig_1_"+request_id+".png", "fig_6_"+request_id+".png", "fig_7_"+request_id+".png", "fig_2_" +
                      request_id+".png", "fig_5_"+request_id+".png", "fig_3_"+request_id+".png", "fig_4_"+request_id+".png"]

        template = (''
                    '<img style="width: {width}; height: {height}" src="{image}">'
                    '<br>'
                    '<hr>'
                    '')
        # plots.go.figure(fig_1).write_image("fig1.png")

        #images = [base64.b64encode(py.image.get(i, width=width, height=height)).decode('utf-8') for i in figures]
        # print(df.render())
        htmlref = "assets/report_"+request_id+".html"
        fileref = "assets/report_"+request_id+".pdf"
        f = open(htmlref, "w")
        # '<!DOCTYPE html>' +
        f.write(
            "<h2 style='color: rgb(50, 50, 50); font-family: Open Sans;'>SEF Market Data Activity</h2>")
        report_html = df.render().replace(': ;', '')
        f.write(report_html)
        for image in images:
            test = template
            test = test.format(image=image, width=width, height=height)
            f.write(test)
            if image[0:5] == "fig_7":
                f.write(df_2.render().replace(': ;', ''))

        f.close()

        #convert_html_to_pdf(report_html, 'report-2.pdf')
        pdfkit.from_file(htmlref, fileref, options={
                         "enable-local-file-access": ""})

        # delete temp files
        for image in images:
            tok = "assets/"+image
            os.remove(tok)
        os.remove(htmlref)
        return [html.A(['Download PDF'], id="download-pdf-button", href=fileref, download='report.pdf', className="button no-print print", hidden=False)]

    else:
        return []


@app.callback(
    Output('modal-body', 'children'),
    [Input('close', 'n_clicks')]
)
def close_modal(n_clicks):
    if n_clicks is not None:
        for filename in os.listdir('assets/'):
            if filename.endswith(".pdf"):
                os.remove('assets/'+filename)

    return [
        html.A(['Generate PDF'], id="pdf-button",
               className="button no-print print", style={'margin': '0 auto'}),
        dcc.Loading(children=[html.Div(children=[html.A(['Download PDF'], id="download-pdf-button", href='NONE',
                                                        download='report.pdf', className="button no-print print", hidden=True)], id='pdf-div', style={'margin': '0 auto'})]),
        html.P("Puede demorar un par de minutos."),
        html.P("Por favor no cierre mientras se este cargando.")
    ]
