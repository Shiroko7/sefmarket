# Using graph_objects
import plotly
import plotly.graph_objects as go

import pandas as pd
import numpy as np

# Operaciones con fechas
import time
from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta

import utils.api as api
import utils.tools as tools


def box_plot_all(producto, start_date, end_date, period, tenor_range=None, usd=1, uf=1, show_total=False):

    usd, uf, duration, l = tools.values_product(producto, usd, uf)

    df = api.get_historic(producto, start_date, end_date, period,
                            tenor_range, usd, uf, duration, l)

    period_df = api.get_specific(
        producto, start_date, end_date, period, tenor_range, usd, uf, duration, l)

    if period == 'WEEKLY':
        start_date = start_date + \
            timedelta(days=-start_date.weekday(), weeks=1)
        end_date = end_date - \
            timedelta(days=end_date.weekday()) - timedelta(days=3)
    if show_total:
        # Agregar total
        date_list = df['Date'].unique()
        for single_date in date_list:
            t = {'Tenor': 'Total',
                 'Volume': df[df['Date'] == single_date]['Volume'].sum(),
                 'Date': single_date,
                 }
            total = pd.Series(t)
            df = df.append(total, ignore_index=True)

        t = {'Broker': '',
             'Tenor': 'Total',
             'Volume': period_df['Volume'].sum(),
             'Date': single_date,
             'Trades': period_df['Trades'].sum(),
             }
        total = pd.Series(t)
        period_df = period_df.append(total, ignore_index=True)

    # agregar boxplot por tenor
    tenors = df['Tenor'].unique()
    tenors = tools.tenor_sort_3(tenors)
    fig = go.Figure()
    for tenor in tenors:
        fig.add_trace(go.Box(y=df[df['Tenor'] == tenor]
                             ['Volume'], name=tenor, boxpoints=False))
        period_value = period_df[period_df['Tenor'] == tenor]['Volume'].sum()

        # agregar valor de hoy ...
        fig.add_trace(go.Scatter(x=[tenor],
                                 y=[period_value],
                                 mode='markers',
                                 name=str(period)+" value",
                                 showlegend=False,
                                 marker=dict(size=[26],
                                             color=['indianred'],
                                             line=dict(width=1))))

        # visible label tttt
        if producto != 'NDF_USD_CLP':
            image = "{0:.1f} K".format(period_value/1e3)
        else:
            image = "{0:.1f} B".format(period_value/1e9)
        fig.add_trace(go.Scatter(x=[tenor],
                                 y=[period_value],
                                 text=[image],
                                 name=str(period)+" value",
                                 showlegend=False,
                                 mode="text",
                                 textfont=dict(color="white",
                                               size=8,
                                               family="Arail",)))

    # formatear fecha
    if start_date.year == end_date.year:
        start_date = start_date.strftime('%d %B')
    else:
        start_date = start_date.strftime('%d %B %Y')
    end_date = end_date.strftime('%d %B %Y')

    if producto != 'NDF_USD_CLP':
        fig.update_layout(xaxis={'title': producto},
                          yaxis={'title': 'DV01'},
                          title=str(period) + ' Distribution ' + producto+': '+str(start_date)+' to '+str(end_date))
    else:
        fig.update_layout(xaxis={'title': producto},
                          yaxis={'title': 'Volume'},
                          title=str(period) + ' Distribution ' + producto+': '+str(start_date)+' to '+str(end_date))

    return fig


def general_graph(producto, tenors, start_date, end_date, period, usd=770, uf=1, cumulative=False, report=False):
    tenors = list({tenor if tenor != '1Y' else '12M' for tenor in tenors})

    usd, uf, duration, l = tools.values_product(producto, usd, uf)

    if period == 'WEEKLY':
        start_date = start_date + \
            timedelta(days=-start_date.weekday(), weeks=1)
        end_date = end_date - \
            timedelta(days=end_date.weekday()) - timedelta(days=3)

    df = api.daily_change(producto, start_date, end_date)

    # date to datetime

    df = df.reset_index(drop=True)
    df['Date'] = pd.to_datetime(df['Date'])
    # hacer un BIG FILL
    df = tools.fill_df(df, start_date, end_date)

    if period == 'DAILY':
        df = df.groupby(['Tenor', 'Date']).agg({'Volume': 'sum'}).reset_index()
    elif period == 'WEEKLY':
        df = df.groupby('Tenor').resample(
            'W', label='left', on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        df = df.groupby('Tenor').resample(
            "M", label='left', on='Date').sum().reset_index()

    if producto != 'NDF_USD_CLP':
        # pasar a DV01
        df = tools.volume_to_dv01(df, usd, uf, duration, l)
        df = df.rename(columns={'Volume': 'DV01'})

        if 'All' in tenors:
            df = df.groupby(['Date']).sum().reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['DV01']
            else:
                y_ = df['DV01'].cumsum()
        else:
            df = df[df['Tenor'].isin(tenors)]
            actual_tenors = df['Tenor'].unique()
            df = df.groupby(['Date']).agg({'DV01': 'sum'}).reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['DV01']
            else:
                y_ = df['DV01'].cumsum()
        if producto == 'CLF_CAM':
            color = 'limegreen'
            tit = 'CLF CAM: Promedio diario de DV01 transado en la última semana'
        elif producto == 'CLP_CAM':
            color = 'royalblue'
            tit = 'CLP CAM: Promedio diario de DV01 transado en la última semana'
        else:
            color = 'darkorchid'
            tit = 'Basis: Promedio diario de DV01 transado en la última semana'
        # crear time series
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_, y=y_, name=' ',
                                 showlegend=False, marker_color=color))

        fig.update_layout(yaxis={'title': 'DV01'})

    else:
        df['Volume'] = df['Volume']*l
        if 'All' in tenors:
            df = df.groupby(['Date']).sum().reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['Volume']
            else:
                y_ = df['Volume'].cumsum()
        else:
            df = df[df['Tenor'].isin(tenors)]
            actual_tenors = df['Tenor'].unique()
            df = df.groupby(['Date']).agg({'Volume': 'sum'}).reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['Volume']
            else:
                y_ = df['Volume'].cumsum()

        # crear time series
        fig = go.Figure()
        # , name="AAPL Low",line_color='dimgray'))
        color = 'crimson'
        fig.add_trace(go.Scatter(x=x_, y=y_, name=' ',
                                 showlegend=False, marker_color=color))

        fig.update_layout(yaxis={'title': 'Volume'})

    if cumulative == False:
        fig.add_shape(
            # Line Horizontal
            go.layout.Shape(
                type="line",
                x0=df['Date'][0],
                y0=y_.mean(),
                x1=end_date,
                y1=y_.mean(),
                line=dict(
                    color=color,
                    width=2,
                    dash="dashdot",
                ),
            ))
        Name = tools.namer(y_.mean())
        fig.add_trace(go.Scatter(x=[df['Date'][1]],
                                 y=[y_.mean()],
                                 name=Name,
                                 mode='markers',
                                 marker=dict(color=[color]),
                                 showlegend=True,))
    # formatear fecha
    if start_date.year == end_date.year:
        start_date = start_date.strftime('%d %B')
    else:
        start_date = start_date.strftime('%d %B %Y')
    end_date = end_date.strftime('%d %B %Y')

    if 'All' in tenors:
        fig.update_layout(title=str(period) +
                          ' Time Series ' + producto + ': All')
    else:
        fig.update_layout(title=str(period) + ' Time Series ' +
                          producto + ': ' + ' + '.join(actual_tenors))

    if producto == 'NDF_USD_CLP':
        fig.update_layout(
            yaxis={'title': 'Volume'}, title='Total transado por día en NDF USD CLP')

    elif report:
        fig.update_layout(
            yaxis={'title': 'DV01'}, title='DV01 total transado por día en '+producto)

    return fig


def participation_graph(producto, start_date, end_date, tenor_range, usd=770, uf=1):

    usd, uf, duration, l = tools.values_product(producto, usd, uf)

    # cargar data
    df = api.query_by_daterange(producto, start_date, end_date)
    df = df.groupby(['Broker', 'Tenor']).agg({'Volume': 'sum'}).reset_index()

    # usar tenors en rango
    mask = df.apply(lambda row: tools.in_date(
        row['Tenor'], tenor_range), axis=1)
    df = df[mask]

    if df.empty:
        #print("No se encontraron transacciones en: " + str(tenor_range))
        return None

    # formatear fecha
    if start_date.year == end_date.year:
        start_date = start_date.strftime('%d %B')
    else:
        start_date = start_date.strftime('%d %B %Y')
    end_date = end_date.strftime('%d %B %Y')
    if producto != 'NDF_USD_CLP':
        # pasar a DV01
        df = tools.volume_to_dv01(df, usd, uf, duration, l)
        df = df.rename(columns={'Volume': 'DV01'})
        # agrupar por broker
        df = df.groupby(['Broker']).agg({'DV01': 'sum'}).reset_index()
        # Agregar total
        total_value = df['DV01'].sum()
        t = {'Broker': 'Total',
             'DV01': total_value
             }
        total = pd.Series(t)
        df = df.append(total, ignore_index=True)
        # calcular % de participación
        df['Share'] = df['DV01']*100/total_value
        df['Share'] = pd.Series(["{0:.0f}% market share".format(
            val) for val in df['Share']], index=df.index)
        fig = go.Figure([go.Bar(x=df['Broker'], y=df['DV01'],
                                hovertext=df['Share'])
                         ])
        fig.update_layout(barmode='stack',
                          xaxis={'title': 'Broker',
                                 'categoryorder': 'total descending'},
                          yaxis={'title': 'DV01'})
    else:
        # agrupar por broker
        df = df.groupby(['Broker']).agg({'Volume': 'sum'}).reset_index()
        df['Volume'] = df['Volume']*l
        # Agregar total
        total_value = df['Volume'].sum()
        t = {'Broker': 'Total',
             'Volume': total_value
             }
        total = pd.Series(t)
        df = df.append(total, ignore_index=True)
        # calcular % de participación
        df['Share'] = df['Volume']*100/total_value
        df['Share'] = pd.Series(["{0:.0f}% market share".format(
            val) for val in df['Share']], index=df.index)
        fig = go.Figure([go.Bar(x=df['Broker'], y=df['Volume'],
                                hovertext=df['Share'])
                         ])
        fig.update_layout(barmode='stack',
                          xaxis={'title': 'Broker',
                                 'categoryorder': 'total descending'},
                          yaxis={'title': 'Volume'})
    fig.update_layout(title=producto+' Market Share: ' +
                      start_date+' to '+end_date)

    return fig


def participation_graph_by_date(producto, start_date, end_date, tenor_range=None, usd=770, uf=1, percent=False):

    usd, uf, duration, l = tools.values_product(producto, usd, uf)

    df = api.query_by_daterange(producto, start_date, end_date)
    # usar tenors en rango
    if tenor_range is not None:
        mask = df.apply(lambda row: tools.in_date(
            row['Tenor'], tenor_range), axis=1)
        df = df[mask]

    if producto != 'NDF_USD_CLP':
        # pasar a DV01
        df = tools.volume_to_dv01(df, usd, uf, duration, l)
        df = df.rename(columns={'Volume': 'DV01'})

        df = df.reset_index(drop=True)
        df['Date'] = pd.to_datetime(df['Date'])

        df = tools.fill_df(df, start_date, end_date)

        # Agregar total

        brokers = df['Broker'].unique()

        total = df.groupby(['Date']).agg({'DV01': 'sum'}).reset_index()['DV01']

        fig = go.Figure()
        for broker in brokers:
            df_ = df[df['Broker'] == broker].groupby(
                ['Date']).agg({'DV01': 'sum'}).reset_index()
            x_ = df_['Date']
            y_ = df_['DV01'].cumsum()
            z_ = 100*y_/total.cumsum()
            if not percent:
                fig.add_trace(go.Scatter(x=x_, y=y_,
                                         hovertemplate='$%{y:.0f}' +
                                         '<br>%{x}</br>' +
                                         '%{text}',
                                         text=['{0:.0f}% market share'.format(
                                             i) for i in z_],
                                         name=broker))
            else:
                fig.add_trace(go.Scatter(x=x_, y=z_,
                                         hovertemplate='%{y:.0f}% market share' +
                                         '<br>%{x}</br>' +
                                         '%{text}',
                                         text=['${0:.0f}'.format(
                                             i) for i in y_],
                                         name=broker))
                fig.update_yaxes(range=[0, 100])

        # formatear fecha
        if start_date.year == end_date.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        end_date = end_date.strftime('%d %B %Y')

        fig.update_layout(barmode='stack',
                          xaxis={'title': 'Broker',
                                 'categoryorder': 'total descending'},
                          yaxis={'title': 'DV01'})
    else:
        # agrupar por broker
        df = df.reset_index(drop=True)
        df['Date'] = pd.to_datetime(df['Date'])

        df = tools.fill_df(df, start_date, end_date)
        # print(df.info())

        df = df.groupby(['Broker', 'Date']).agg(
            {'Volume': 'sum'}).reset_index()
        df['Volume'] = df['Volume']*l

        total = df.groupby(['Date']).agg(
            {'Volume': 'sum'}).reset_index()['Volume']

        fig = go.Figure()
        brokers = df['Broker'].unique()
        for broker in brokers:
            df_ = df[df['Broker'] == broker].groupby(
                ['Date']).agg({'Volume': 'sum'}).reset_index()

            x_ = df_['Date']
            y_ = df_['Volume'].cumsum()
            z_ = 100*y_/total.cumsum()
            if not percent:
                fig.add_trace(go.Scatter(x=x_, y=y_,
                                         hovertemplate='$%{y:.0f}' +
                                         '<br>%{x}</br>' +
                                         '%{text}',
                                         text=['{0:.0f}% market share'.format(
                                             i) for i in z_],
                                         name=broker))
            else:
                fig.add_trace(go.Scatter(x=x_, y=z_,
                                         hovertemplate='%{y:.0f}% market share' +
                                         '<br>%{x}</br>' +
                                         '%{text}',
                                         text=['${0:.0f}'.format(
                                             i) for i in y_],
                                         name=broker))
                fig.update_yaxes(range=[0, 100])

        # formatear fecha
        if start_date.year == end_date.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        end_date = end_date.strftime('%d %B %Y')

        fig.update_layout(barmode='stack',
                          xaxis={'title': 'Broker',
                                 'categoryorder': 'total descending'},
                          yaxis={'title': 'Volume'})

    fig.update_layout(title=producto+' Market Share: ')
    return fig


def tenor_graph(producto, tenors, start_date, end_date, period, usd=770, uf=1, cumulative=False):
    tenors = list({tenor if tenor != '1Y' else '12M' for tenor in tenors})
    usd, uf, duration, l = tools.values_product(producto, usd, uf)

    if period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + \
            timedelta(days=-start_date.weekday(), weeks=1)
        end_date = end_date - \
            timedelta(days=end_date.weekday()) - timedelta(days=3)

    df = api.daily_change(producto, start_date, end_date)

    # date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    # hacer un BIG FILL
    df = tools.fill_df(df, start_date, end_date)

    if period == 'DAILY':
        df = df.groupby(['Tenor', 'Date']).agg({'Volume': 'sum'}).reset_index()
    elif period == 'WEEKLY':
        df = df.groupby('Tenor').resample(
            'W', label='left', on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        df = df.groupby('Tenor').resample(
            "M", label='left', on='Date').sum().reset_index()

    if producto != 'NDF_USD_CLP':
        # pasar a DV01
        df = tools.volume_to_dv01(df, usd, uf, duration, l)
        df = df.rename(columns={'Volume': 'DV01'})

        # crear time series
        fig = go.Figure()
        df_ = df.groupby(['Tenor', 'Date']).agg({'DV01': 'sum'}).reset_index()
        for tenor in tenors:

            x_ = df_[df_['Tenor'] == tenor]['Date']
            if cumulative == False:
                y_ = df_[df_['Tenor'] == tenor]['DV01']
            else:
                y_ = df_[df_['Tenor'] == tenor]['DV01'].cumsum()

            # , name="AAPL Low",line_color='dimgray'))
            fig.add_trace(go.Scatter(x=x_, y=y_, name=tenor))
        if 'All' in tenors:
            df = df.groupby(['Date']).agg({'DV01': 'sum'}).reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['DV01']
            else:
                y_ = df['DV01'].cumsum()
            fig.add_trace(go.Scatter(x=x_, y=y_, name='All'))
        # formatear fecha
        if start_date.year == end_date.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        end_date = end_date.strftime('%d %B %Y')
        fig.update_layout(xaxis={'title': tenor},
                          yaxis={'title': 'DV01'})

    else:
        # crear time series
        fig = go.Figure()
        df_ = df.groupby(['Tenor', 'Date']).agg(
            {'Volume': 'sum'}).reset_index()
        for tenor in tenors:
            x_ = df_[df_['Tenor'] == tenor]['Date']
            if cumulative == False:
                y_ = df_[df_['Tenor'] == tenor]['Volume']
            else:
                y_ = df_[df_['Tenor'] == tenor]['Volume'].cumsum()

            # , name="AAPL Low",line_color='dimgray'))
            fig.add_trace(go.Scatter(x=x_, y=y_, name=tenor))
        if 'All' in tenors:
            df = df.groupby(['Date']).agg({'Volume': 'sum'}).reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['Volume']
            else:
                y_ = df['Volume'].cumsum()
            fig.add_trace(go.Scatter(x=x_, y=y_, name='All'))
        # formatear fecha
        if start_date.year == end_date.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        end_date = end_date.strftime('%d %B %Y')

        fig.update_layout(xaxis={'title': tenor},
                          yaxis={'title': 'Volume'})

    # Add range slider
    # fig.update_layout(
    #    xaxis=go.layout.XAxis(
    #        rangeslider=dict(
    #            visible=True
    #        ),
    #    )
    # )
    fig.update_layout(title=str(period) + ' Time Series ' + producto)
    return fig


def bar_by_tenor(producto, start_date, end_date, tenor_range=None, usd=770, uf=1, show_total=False, report=False):

    usd, uf, duration, l = tools.values_product(producto, usd, uf)

    # cargar data
    df = api.query_by_daterange(producto, start_date, end_date)

    # usar tenors en rango
    if tenor_range is not None:
        mask = df.apply(lambda row: tools.in_date(
            row['Tenor'], tenor_range), axis=1)
        df = df[mask]

    if df.empty:
        print("No se encontraron transacciones en: " + str(tenor_range))
        return None

    # formatear fecha
    if start_date.year == end_date.year:
        start_date = start_date.strftime('%d %B')
    else:
        start_date = start_date.strftime('%d %B %Y')
    end_date = end_date.strftime('%d %B %Y')

    if producto != 'NDF_USD_CLP':
        # pasar a DV01
        df = tools.volume_to_dv01(df, usd, uf, duration, l)
        if show_total:
            # Agregar total
            date_list = df['Date'].unique()
            for single_date in date_list:
                t = {'Tenor': 'Total',
                     'Volume': df[df['Date'] == single_date]['Volume'].sum(),
                     'Date': single_date,
                     }
                df = df.append(pd.Series(t), ignore_index=True)

        df = df.groupby(['Tenor']).agg({'Volume': 'sum'}).reset_index()
        df = df.rename(columns={'Volume': 'DV01'})
        # sort
        df = tools.tenor_sort_2(df)

        if producto == 'CLF_CAM':
            color = 'limegreen'
            tit = 'CLF CAM: Promedio diario de DV01 transado en la última semana'
        elif producto == 'CLP_CAM':
            color = 'royalblue'
            tit = 'CLP CAM: Promedio diario de DV01 transado en la última semana'
        else:
            color = 'darkorchid'
            tit = 'Basis: Promedio diario de DV01 transado en la última semana'

        if (report):
            df['DV01'] = df['DV01']/5
        else:
            tit = 'Accumulated ' + producto+': '+start_date+' to '+end_date

        fig = go.Figure(
            [go.Bar(x=df['Tenor'], y=df['DV01'], marker_color=color)])

        fig.update_layout(barmode='stack',
                          xaxis={'title': 'Tenor'},
                          yaxis={'title': 'DV01'},
                          title=tit)

    else:
        if show_total:
            # Agregar total
            date_list = df['Date'].unique()
            for single_date in date_list:
                t = {'Tenor': 'Total',
                     'Volume': df[df['Date'] == single_date]['Volume'].sum(),
                     'Date': single_date,
                     }
                df = df.append(pd.Series(t), ignore_index=True)
        df = df.groupby(['Tenor']).agg({'Volume': 'sum'}).reset_index()
        df['Volume'] = df['Volume']*l
        color = 'crimson'
        # sort
        if (report):
            df['Volume'] = df['Volume']/5
            tit = 'NDF USD CLP: Promedio diario de DV01 transado en la última semana'
        else:
            tit = 'Accumulated ' + producto+': '+start_date+' to '+end_date
        df = tools.tenor_sort_2(df)
        fig = go.Figure(
            [go.Bar(x=df['Tenor'], y=df['Volume'], marker_color=color)])
        fig.update_layout(barmode='stack',
                          xaxis={'title': 'Tenor'},
                          yaxis={'title': 'Volume'},
                          title=tit)

    return fig


def ndf_index(fecha):
    df = api.query_by_date('NDF_USD_CLP', fecha)
    if df.empty:
        return 0
    else:
        df = df.groupby('Tenor').agg({'Volume': 'sum'}).reset_index()
        df['Volume'] = df['Volume']*1e6
        mask_inf = df.apply(lambda row: tools.in_date(
            row['Tenor'], ('0D', '5D')), axis=1)
        mask_mid = df.apply(lambda row: tools.in_date(
            row['Tenor'], ('6D', '1M')), axis=1)
        mask_sup = df.apply(lambda row: tools.in_date(
            row['Tenor'], ('2M', '9999999999Y')), axis=1)
        n_index = df[mask_mid]['Volume'].sum(
        ) - (df[mask_inf]['Volume'].sum() + df[mask_sup]['Volume'].sum())
        return n_index


def graph_ndf_index(start_date, end_date, cumulative=False):
    business_days = pd.date_range(start=start_date, end=end_date, freq='B')
    n_indexes = list()
    for single_date in business_days:
        n_indexes.append(ndf_index(single_date))
    fig = go.Figure()
    if not cumulative:
        fig.add_trace(go.Scatter(x=business_days, y=n_indexes,
                                 name=' ', showlegend=False))
        fig.add_shape(
            # Line Horizontal
            go.layout.Shape(
                type="line",
                x0=business_days[0],
                y0=sum(n_indexes)/len(n_indexes),
                x1=business_days[-1],
                y1=sum(n_indexes)/len(n_indexes),
                line=dict(
                    color="darkblue",
                    width=4,
                    dash="dashdot",
                ),
            ))
        fig.add_trace(go.Scatter(x=[business_days[1]],
                                 y=[sum(n_indexes)/len(n_indexes)],
                                 name="Mean: " +
                                 "{0:.1f} B".format(
                                     sum(n_indexes)/len(n_indexes)/1e9),
                                 mode='markers',
                                 marker=dict(color=["darkblue"]),
                                 showlegend=True,))
        fig.update_layout(title='NDF INDEX Time Series ')
    else:
        fig.add_trace(go.Scatter(x=business_days, y=pd.Series(
            n_indexes).cumsum(), name=' ', showlegend=False))
        fig.update_layout(title='Accumulated NDF INDEX Time Series ')

    # Add range slider
    # fig.update_layout(
    #    xaxis=go.layout.XAxis(
    #        rangeslider=dict(
    #            visible=True
    #        ),
    #    )
    # )
    fig.update_layout(yaxis={'title': 'Volume'})

    return fig


def table_ndf_index(start_date, end_date):
    cols = ['Date', 'Index', 'Zs', 'Mean']
    business_days = pd.date_range(start=start_date, end=end_date, freq='B')

    df_indexes = pd.DataFrame(columns=cols)
    count = 0
    cum = 0

    count = count + 1
    index = ndf_index(start_date)/1e6
    cum = cum + index
    mean = cum/count
    sd = (((index - mean)**2)/count)**0.5
    zscore = (index - mean)/sd
    row = {'Date': business_days[0],
           'Index': index, 'Mean': mean, 'Zs': zscore}
    df_indexes = df_indexes.append(row, ignore_index=True)

    business_days = business_days[1:]
    for single_date in business_days:
        count = count + 1
        index = ndf_index(single_date)/1e6
        cum = cum + index
        mean = cum/count
        sd = ((((df_indexes['Index'] - mean)**2).sum() +
               (index - mean)**2)/count)**0.5
        zscore = (index - mean)/sd
        row = {'Date': single_date, 'Index': index, 'Mean': mean, 'Zs': zscore}
        df_indexes = df_indexes.append(row, ignore_index=True)
    return df_indexes


def tseries_clf_clp(start_date, end_date, usd=770, uf=1):
    ###################################
    usd, uf, duration, l = tools.values_product('CLF_CAM', usd, uf)

    df_clf = api.daily_change('CLF_CAM', start_date, end_date)
    # date to datetime

    df_clf = df_clf.reset_index(drop=True)
    df_clf['Date'] = pd.to_datetime(df_clf['Date'])
    # hacer un BIG FILL
    df_clf = tools.fill_df(df_clf, start_date, end_date)

    df_clf = df_clf.groupby(['Tenor', 'Date']).agg(
        {'Volume': 'sum'}).reset_index()

    # pasar a DV01
    df_clf = tools.volume_to_dv01(df_clf, usd, uf, duration, l)
    df_clf = df_clf.rename(columns={'Volume': 'DV01'})

    df_clf = df_clf.groupby(['Date']).sum().reset_index()

    ################################
    usd, uf, duration, l = tools.values_product('CLP_CAM', usd, uf)

    df = api.daily_change('CLP_CAM', start_date, end_date)
    # date to datetime

    df = df.reset_index(drop=True)
    df['Date'] = pd.to_datetime(df['Date'])
    # hacer un BIG FILL
    df = tools.fill_df(df, start_date, end_date)

    df = df.groupby(['Tenor', 'Date']).agg({'Volume': 'sum'}).reset_index()

    # pasar a DV01
    df = tools.volume_to_dv01(df, usd, 1, duration, l)
    df = df.rename(columns={'Volume': 'DV01'})

    df = df.groupby(['Date']).sum().reset_index()

    # crear time series
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['DV01'], name='CLP CAM', showlegend=True, marker_color='royalblue'))

    fig.add_trace(go.Scatter(
        x=df_clf['Date'], y=df_clf['DV01'], name='CLF CAM', showlegend=True, marker_color='limegreen'))

    # formatear fecha
    if start_date.year == end_date.year:
        start_date = start_date.strftime('%d %B')
    else:
        start_date = start_date.strftime('%d %B %Y')
    end_date = end_date.strftime('%d %B %Y')

    fig.update_layout(
        yaxis={'title': 'DV01'}, title='DV01 total transado por día en CLPCAM y CLFCAM')

    return fig
