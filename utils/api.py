# -*- coding: utf-8 -*-
import utils.tools as tools

# Operaciones con fechas
import time
from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta

# Para leer tablas: excel,csv,html
import pandas as pd
import os


# otras operaciones
import numpy as np
from functools import reduce
import warnings

# Conexión base de datos
# <>dependencia con psycopg2
import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Conectar engine://user:password@host:port/database
database = create_engine(
    'postgres://hgoturfocpwsgw:a084e1d36517cf703d2d9590df5c2f7a345340d857dfb54b5ebed9712856d610@ec2-35-174-88-65.compute-1.amazonaws.com:5432/dfun38lejd4e')
base = declarative_base()

Session = sessionmaker(database)
session = Session()

base.metadata.create_all(database)

# resumenes for bd
# funciones que no operan directamente con la BD


def product_scale(row):
    # BILLONES CLP
    if str(row['Name']) == 'CLP_CAM':
        l = 1e9
    # MILES UF
    elif str(row['Name']) == 'CLF_CAM':
        l = 1e3
    # MILLONES USD
    elif str(row['Name']) == 'NDF_USD_CLP':
        l = 1e6
    # MILLONES USD
    elif str(row['Name']) == 'BASIS':
        l = 1e6
    else:
        l = 1
    return int(row['Volume'])/l
# CLP CAM


def resumen_for_BD(fecha=None):
    if fecha == None:
        return

    # LATAM
    latam_resumen = tools.latam_proc(fecha)
    latam_resumen['Broker'] = 'LatAmSEF'
    latam_resumen = latam_resumen[[
        'Broker', 'Name', 'Tenor', 'Trades', 'Volume']]

    # TRADITION
    tradition_resumen = tools.tradition_proc(fecha)
    tradition_resumen['Broker'] = 'TraditionSEF'
    tradition_resumen = tradition_resumen[[
        'Broker', 'Name', 'Tenor', 'Trades', 'Volume']]

    # TULLETT
    tullett_resumen = tools.tullett_proc(fecha)
    tullett_resumen = tullett_resumen[[
        'Broker', 'Name', 'Tenor', 'Trades', 'Volume']]

    # GFI
    gfi_resumen = tools.gfi_proc(fecha)
    gfi_resumen['Broker'] = 'GFI'
    gfi_resumen = gfi_resumen[['Broker', 'Tenor', 'Name', 'Trades', 'Volume']]

    # BgC
    bgc_resumen = tools.bgc_proc(fecha)
    bgc_resumen['Broker'] = 'BGC'
    bgc_resumen = bgc_resumen[['Broker', 'Tenor', 'Name', 'Trades', 'Volume']]

    resumen = pd.concat([latam_resumen, tradition_resumen,
                         tullett_resumen, gfi_resumen, bgc_resumen], sort=False)

    resumen = resumen[~resumen.Tenor.str.contains("-")]
    resumen = resumen[~resumen.Tenor.str.contains("NONE")]

    if not resumen.empty:
        resumen['Volume'] = resumen.apply(
            lambda row: product_scale(row), axis=1)
        resumen['Date'] = fecha

    return resumen


# ORM entidades de la bd
class NDF_USD_CLP(base):
    __tablename__ = 'ndf_usd_clp'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)  # ,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)


class CLP_CAM(base):
    __tablename__ = 'clp_cam'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)  # ,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)


class CLF_CAM(base):
    __tablename__ = 'clf_cam'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)  # ,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)


class BASIS(base):
    __tablename__ = 'basis'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)  # ,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)


# OPERCIONES QUE MODIFICAN LA B
# OPERCIONES QUE MODIFICAN LA BD

# delete rows by date
def delete_by_date(fecha):

    input_rows = session.query(NDF_USD_CLP).filter(
        NDF_USD_CLP.Date == fecha).delete()

    input_rows = session.query(CLP_CAM).filter(CLP_CAM.Date == fecha).delete()

    input_rows = session.query(CLF_CAM).filter(CLF_CAM.Date == fecha).delete()

    input_rows = session.query(BASIS).filter(BASIS.Date == fecha).delete()

    session.commit()

# UPLOAD DAILY DATA


def pd_to_sql(date):
    # IMPORTANTE: CADA UPLOAD DE UN DÍA PRIMERO BOTA LO QUE YA ESTA, PARA NO DUPLICAR DATA
    delete_by_date(date)

    df = resumen_for_BD(date)
    if df.empty:
        print("No se registraron datos: ", date)
        return None

    ndf_usd_clp = df[df['Name'] == 'NDF_USD_CLP']
    ndf_usd_clp = ndf_usd_clp[['Broker', 'Tenor', 'Trades', 'Volume', 'Date']]
    if not ndf_usd_clp.empty:
        ndf_usd_clp.to_sql("ndf_usd_clp",
                           database,
                           if_exists='append',
                           schema='public',
                           index=False,
                           chunksize=500,
                           dtype={"Broker": Text,
                                  "Date": DateTime,
                                  "Tenor": Text,
                                  "Trades": Integer,
                                  "Volume": Float}
                           )

    clp_cam = df[df['Name'] == 'CLP_CAM']
    clp_cam = clp_cam[['Broker', 'Tenor', 'Trades', 'Volume', 'Date']]
    if not clp_cam.empty:
        clp_cam.to_sql("clp_cam",
                       database,
                       if_exists='append',
                       schema='public',
                       index=False,
                       chunksize=500,
                       dtype={"Broker": Text,
                              "Date": DateTime,
                              "Tenor": Text,
                              "Trades": Integer,
                              "Volume": Float}
                       )

    clf_cam = df[df['Name'] == 'CLF_CAM']
    clf_cam = clf_cam[['Broker', 'Tenor', 'Trades', 'Volume', 'Date']]
    if not clf_cam.empty:
        clf_cam.to_sql("clf_cam",
                       database,
                       if_exists='append',
                       schema='public',
                       index=False,
                       chunksize=500,
                       dtype={"Broker": Text,
                              "Date": DateTime,
                              "Tenor": Text,
                              "Trades": Integer,
                              "Volume": Float}
                       )

    basis = df[df['Name'] == 'BASIS']
    basis = basis[['Broker', 'Tenor', 'Trades', 'Volume', 'Date']]

    if not basis.empty:
        basis.to_sql("basis",
                     database,
                     if_exists='append',
                     schema='public',
                     index=False,
                     chunksize=500,
                     dtype={"Broker": Text,
                            "Date": DateTime,
                            "Tenor": Text,
                            "Trades": Integer,
                            "Volume": Float}
                     )

    session.commit()

# UPLOAD DATA BY DATE RANGE


def upload_range(start_date, end_date):
    day_count = (end_date - start_date).days + 1
    # para cada fecha en el rango [start_date, start_date + 1 día....]
    business_days = pd.date_range(
        start=start_date, end=end_date, freq='B').date
    for single_date in business_days:
        try:
            pd_to_sql(single_date)
        except Exception as e:
            print("Error: " + str(single_date) + " | "+str(e))

    session.commit()
# DELETE (<<<CAREFUL) DATA BY DATE RANGE


def delete_range(start_date, end_date):
    day_count = (end_date - start_date).days + 1
    # para cada fecha en el rango [start_date, start_date + 1 día....]
    business_days = pd.date_range(
        start=start_date, end=end_date, freq='B').date
    for single_date in business_days:

        try:
            delete_by_date(single_date)
            print('Deleted: ' + str(single_date))
        except Exception as e:
            print("Error: " + str(single_date) + ' | ' + str(e))
    session.commit()


# OPERACIONES QUE LEEN DATOS DE LA BASE DE DATOS
def query_by_date(producto, fecha):
    # elegir tabla
    if producto == 'NDF_USD_CLP':
        input_rows = session.query(NDF_USD_CLP).filter(
            NDF_USD_CLP.Date == fecha)
    elif producto == 'CLP_CAM':
        input_rows = session.query(CLP_CAM).filter(CLP_CAM.Date == fecha)
    elif producto == 'CLF_CAM':
        input_rows = session.query(CLF_CAM).filter(CLF_CAM.Date == fecha)
    elif producto == 'BASIS':
        input_rows = session.query(BASIS).filter(BASIS.Date == fecha)
    else:
        return None
    data = dict()

    rows_list = []
    for row in input_rows:
        dict1 = {}
        # get input row in dictionary format
        # key = col_name
        dict1.update({'Date': row.Date, 'Broker': row.Broker,
                      'Tenor': row.Tenor, 'Trades': row.Trades, 'Volume': row.Volume})
        rows_list.append(dict1)
    df = pd.DataFrame(rows_list)
    #cols = ['Date','Broker','Tenor','Trades','Volume']
    #df = df[cols]
    return df


def query_by_daterange(producto, start_date, end_date):
    # elegir tabla
    if producto == 'NDF_USD_CLP':
        input_rows = session.query(NDF_USD_CLP).filter(
            NDF_USD_CLP.Date.between(start_date, end_date))
    elif producto == 'CLP_CAM':
        input_rows = session.query(CLP_CAM).filter(
            CLP_CAM.Date.between(start_date, end_date))
    elif producto == 'CLF_CAM':
        input_rows = session.query(CLF_CAM).filter(
            CLF_CAM.Date.between(start_date, end_date))
    elif producto == 'BASIS':
        input_rows = session.query(BASIS).filter(
            BASIS.Date.between(start_date, end_date))
    else:
        return None
    data = dict()

    rows_list = []
    for row in input_rows:
        dict1 = {}
        # get input row in dictionary format
        # key = col_name
        dict1.update({'Date': row.Date, 'Broker': row.Broker,
                      'Tenor': row.Tenor, 'Trades': row.Trades, 'Volume': row.Volume})
        rows_list.append(dict1)
    df = pd.DataFrame(rows_list)
    #cols = ['Date','Broker','Tenor','Trades','Volume']
    #df = df[cols]
    return df


# derivados de querys


def daily_change(producto, start_date, end_date):
    df_list = []
    # query!
    df = query_by_daterange(producto, start_date, end_date)
    df = df.groupby(['Tenor', 'Date']).agg({'Volume': 'sum'}).reset_index()
    return df


################ CREAR INFORME (TABLA) ############


def informe_v1(producto, start_date, end_date, period, usd, uf=1):
    if start_date == None:
        return None
    # BILLONES CLP
    if producto == 'CLP_CAM':
        duration = tools.d_clp
        uf = 1
        l = 1e9
    # MILES UF
    elif producto == 'CLF_CAM':
        duration = tools.d_clf
        l = 1e3
    # MILLONES USD
    elif producto == 'BASIS':
        duration = tools.d_usd
        uf = 1
        l = 1e6
        usd = 1
    else:
        uf = 1
        l = 1

    # crear df con todos los tenors
    cols = ['Tenor', 'Volume', 'DV01', 'SD',
            'Mean', 'Highest', 'Days Traded', 'Percent']
    empty_df = pd.DataFrame(columns=cols)
    for i in duration.keys():
        dfi = pd.DataFrame([[i, 0, 0, 0, 0, 0, 0, 0]], columns=cols)
        empty_df = empty_df.append(dfi)

    if period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + \
            timedelta(days=-start_date.weekday(), weeks=1)
        end_date = end_date - \
            timedelta(days=end_date.weekday()) - timedelta(days=3)

    #print("Generando tabla...")
    # clear_output(wait=False)
    # cargar data historica y pasar a dv01
    historic_df = daily_change(producto, start_date, end_date)
    historic_df = historic_df.fillna(0)

    # pasar a DV01
    historic_df = tools.volume_to_dv01(historic_df, usd, uf, duration, l)

    # date to datetime
    historic_df = historic_df.reset_index(drop=True)
    historic_df.Date = pd.to_datetime(historic_df.Date)

    # sacar volumen de DV01 periodical
    if period == 'DAILY':
        periodly_dv = historic_df.groupby('Date').sum().reset_index()
    elif period == 'WEEKLY':
        periodly_dv = historic_df.resample(
            'W-Mon', label='left', on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        periodly_dv = historic_df.resample(
            'M', label='left', on='Date').sum().reset_index()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    # agregar número de días en que se tranzo
    trades_df = historic_df.groupby(
        ['Tenor']).size().reset_index(name='Days Traded')

    # calcular histric values
    historic_trades = historic_df['Date'].nunique()

    # date to datetime
    historic_df = historic_df.reset_index(drop=True)
    historic_df['Date'] = pd.to_datetime(historic_df['Date'])

    # hacer un BIG FILL
    historic_df = tools.fill_df(historic_df, start_date, end_date)

    if period == 'DAILY':
        historic_mean = historic_df.groupby('Date').agg(
            {'Volume': 'sum'}).reset_index()['Volume'].mean()
    elif period == 'WEEKLY':
        historic_df = historic_df.groupby('Tenor').resample(
            'W', label='left', on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg(
            {'Volume': 'sum'}).reset_index()['Volume'].mean()
    elif period == 'MONTHLY':
        historic_df = historic_df.groupby('Tenor').resample(
            "M", label='left', on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg(
            {'Volume': 'sum'}).reset_index()['Volume'].mean()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    historic_sd = historic_df['Volume'].std()

    # calcular media
    mean_df = tools.mean_value(historic_df)
    # encontrar valor máximo
    max_df = tools.max_value(historic_df)
    max_df = max_df[['Tenor', 'Highest']]
    # calcular desviación estándar
    sd_df = tools.sd_value(historic_df)
    sd_df = sd_df[['Tenor', 'SD']]

    # cargar data a comparar
    if period == 'DAILY':
        period_volume_df = query_by_date(producto, end_date)
        if not period_volume_df.empty:
            period_volume_df = period_volume_df.groupby(
                ['Tenor']).agg({'Volume': 'sum'}).reset_index()
            period_df = tools.volume_to_dv01(
                period_volume_df, usd, uf, duration, l)
        else:
            period_volume_df = empty_df[['Tenor', 'Volume']]
            period_df = empty_df[['Tenor', 'Volume']]
    elif period == 'WEEKLY':
        # esta definido como días habiles desde hoy
        offset_days = pd.date_range(
            start=end_date-timedelta(days=6), end=end_date, freq='B').date[0]
        period_volume_df = daily_change(producto, offset_days, end_date)
        if not period_volume_df.empty:
            period_volume_df = period_volume_df.groupby(
                ['Tenor']).agg({'Volume': 'sum'}).reset_index()
            period_df = tools.volume_to_dv01(
                period_volume_df, usd, uf, duration, l)
        else:
            period_volume_df = empty_df[['Tenor', 'Volume']]
            period_df = empty_df[['Tenor', 'Volume']]
    elif period == 'MONTHLY':
        # esta definido como días habiles desde hoy
        offset_days = pd.date_range(
            start=end_date-timedelta(days=31), end=end_date, freq='B').date[0]
        period_volume_df = daily_change(producto, offset_days, end_date)
        if not period_volume_df.empty:
            period_volume_df = period_volume_df.groupby(
                ['Tenor']).agg({'Volume': 'sum'}).reset_index()
            period_df = tools.volume_to_dv01(
                period_volume_df, usd, uf, duration, l)
        else:
            period_volume_df = empty_df[['Tenor', 'Volume']]
            period_df = empty_df[['Tenor', 'Volume']]

    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    # renombrar columnas
    period_df = period_df.rename(columns={'Volume': 'DV01'})
    mean_df = mean_df.rename(columns={'Volume': 'Mean'})

    # crear tabla
    df = reduce(lambda x, y: pd.merge(x, y, how='outer', on='Tenor'), [
                period_volume_df, period_df, max_df, mean_df, trades_df, sd_df])
    df = pd.concat([df, empty_df], sort=True)
    df = df.groupby(['Tenor']).sum().reset_index()
    df = tools.tenor_sort_2(df)
    df = df.fillna(0)
    # pasar desviación estándar a número de desviaciones estandar
    df['SD'] = (df['DV01'] - df['Mean']) / df['SD']
    df = df.replace(np.inf, 0)
    df = df.replace(-np.inf, 0)
    df = df.fillna(0)
    # Agregar total
    t = {'Tenor': 'Total',
         'Volume': df['Volume'].sum(),
         'DV01': df['DV01'].sum(),
         'Highest': periodly_dv['Volume'].max(),
         'Mean': historic_mean,
         'Days Traded': historic_trades,
         'SD': (df['DV01'].sum()-historic_mean)/historic_sd
         }
    total = pd.Series(t)
    df = df.append(total, ignore_index=True)
    df['Percent'] = df['Days Traded']/historic_trades
    df['Percent'] = pd.Series(["{0:,.2f}".format(val)
                               for val in df['Percent']], index=df.index)
    # formato tabla
    df['Mean'] = pd.Series(["{0:,.0f}".format(val)
                            for val in df['Mean']], index=df.index)
    #df['SD'] = pd.Series([round(val * 2) / 2 for val in df['SD']], index = df.index)
    df['SD'] = pd.Series(["{0:,.1f}".format(val)
                          for val in df['SD']], index=df.index)
    df['Highest'] = pd.Series(["{0:,.0f}".format(val)
                               for val in df['Highest']], index=df.index)
    df['DV01'] = pd.Series(["{0:,.0f}".format(val)
                            for val in df['DV01']], index=df.index)
    df['Volume'] = pd.Series(["{0:,.0f}".format(val)
                              for val in df['Volume']], index=df.index)
    df['Days Traded'] = pd.Series(
        ["{0:,.0f}".format(val) for val in df['Days Traded']], index=df.index)
    df = df[cols]
    df = df.set_index('Tenor')
    #print("Producto: " + producto)
    #print("Start Date: " + str(start_date))
    #print("End Date:" + str(today))
    return df


def informe_ndf(start_date, end_date, period):
    if start_date == None:
        return None

    # crear df con todos los tenors
    cols = ['Tenor', 'Volume', 'SD', 'Mean',
            'Highest', 'Days Traded', 'Percent']

    if period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + \
            timedelta(days=-start_date.weekday(), weeks=1)
        end_date = end_date - \
            timedelta(days=end_date.weekday()) - timedelta(days=3)

    #print("Generando tabla...")
    #print("Producto: NDF_USD_CLP")
    #print("Start Date: " + str(start_date))
    #print("End Date:" + str(today))

    # cargar data historica
    historic_df = daily_change('NDF_USD_CLP', start_date, end_date)
    historic_df = historic_df.fillna(0)

    # date to datetime
    historic_df = historic_df.reset_index(drop=True)
    historic_df.Date = pd.to_datetime(historic_df.Date)

    # sacar volumen de DV01 periodical
    if period == 'DAILY':
        periodly_dv = historic_df.groupby('Date').sum().reset_index()
    elif period == 'WEEKLY':
        periodly_dv = historic_df.resample(
            'W-Mon', label='left', on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        periodly_dv = historic_df.resample(
            'M', label='left', on='Date').sum().reset_index()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    # agregar número de días en que se tranzo
    trades_df = historic_df.groupby(
        ['Tenor']).size().reset_index(name='Days Traded')

    # calcular histric values
    historic_trades = historic_df['Date'].nunique()

    # date to datetime
    historic_df = historic_df.reset_index(drop=True)
    historic_df['Date'] = pd.to_datetime(historic_df['Date'])

    # hacer un BIG FILL
    historic_df = tools.fill_df(historic_df, start_date, end_date)

    if period == 'DAILY':
        historic_mean = historic_df.groupby('Date').agg(
            {'Volume': 'sum'}).reset_index()['Volume'].mean()

    elif period == 'WEEKLY':
        historic_df = historic_df.groupby('Tenor').resample(
            'W', label='left', on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg(
            {'Volume': 'sum'}).reset_index()['Volume'].mean()
    elif period == 'MONTHLY':
        historic_df = historic_df.groupby('Tenor').resample(
            "M", label='left', on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg(
            {'Volume': 'sum'}).reset_index()['Volume'].mean()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    historic_sd = historic_df['Volume'].std()

    # calcular media
    mean_df = tools.mean_value(historic_df)

    # encontrar valor máximo
    max_df = tools.max_value(historic_df)
    max_df = max_df[['Tenor', 'Highest']]
    # calcular desviación estándar
    sd_df = tools.sd_value(historic_df)
    sd_df = sd_df[['Tenor', 'SD']]

    # cargar data a comparar
    if period == 'DAILY':
        period_volume_df = query_by_date('NDF_USD_CLP', end_date)
        period_volume_df = period_volume_df.groupby(
            ['Tenor']).agg({'Volume': 'sum'}).reset_index()

    elif period == 'WEEKLY':
        # esta definido como días habiles desde hoy
        offset_days = pd.date_range(
            start=end_date-timedelta(days=6), end=end_date, freq='B').date[0]
        period_volume_df = daily_change('NDF_USD_CLP', offset_days, end_date)
        period_volume_df = period_volume_df.groupby(
            ['Tenor']).agg({'Volume': 'sum'}).reset_index()

    elif period == 'MONTHLY':
        # esta definido como días habiles desde hoy
        offset_days = pd.date_range(
            start=end_date-timedelta(days=31), end=end_date, freq='B').date[0]
        period_volume_df = daily_change('NDF_USD_CLP', offset_days, end_date)
        period_volume_df = period_volume_df.groupby(
            ['Tenor']).agg({'Volume': 'sum'}).reset_index()

    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    # renombrar columnas

    mean_df = mean_df.rename(columns={'Volume': 'Mean'})
    # crear tabla
    df = reduce(lambda x, y: pd.merge(x, y, how='outer', on='Tenor'), [
                period_volume_df, max_df, mean_df, trades_df, sd_df])

    df = df.groupby(['Tenor']).sum().reset_index()
    df = tools.tenor_sort_2(df)
    df = df.fillna(0)
    # pasar desviación estándar a número de desviaciones estandar
    df['SD'] = (df['Volume'] - df['Mean']) / df['SD']
    df = df.replace(np.inf, 0)
    df = df.replace(-np.inf, 0)
    df = df.fillna(0)
    # Agregar total
    t = {'Tenor': 'Total',
         'Volume': df['Volume'].sum(),
         'Highest': periodly_dv['Volume'].max(),
         'Mean': historic_mean,
         'Days Traded': historic_trades,
         'SD': (df['Volume'].sum()-historic_mean)/historic_sd
         }
    total = pd.Series(t)
    df = df.append(total, ignore_index=True)
    # formato tabla
    df['Percent'] = df['Days Traded']/historic_trades
    df['Percent'] = pd.Series(["{0:,.2f}".format(val)
                               for val in df['Percent']], index=df.index)
    df['Mean'] = pd.Series(["{0:,.0f}".format(val)
                            for val in df['Mean']], index=df.index)
    #df['Mean'] = df.apply(lambda x: "{:,}".format(x['Mean']), axis=1)
    #df['SD'] = pd.Series([round(val * 2) / 2 for val in df['SD']], index = df.index)
    df['SD'] = pd.Series(["{0:,.1f}".format(val)
                          for val in df['SD']], index=df.index)
    df['Highest'] = pd.Series(["{0:,.0f}".format(val)
                               for val in df['Highest']], index=df.index)
    df['Volume'] = pd.Series(["{0:,.0f}".format(val)
                              for val in df['Volume']], index=df.index)
    df['Days Traded'] = pd.Series(
        ["{0:,.0f}".format(val) for val in df['Days Traded']], index=df.index)

    df = df[cols]
    df = df.set_index('Tenor')
    return df


def informe(producto, start_date, end_date, period, usd, uf):
    if producto != 'NDF_USD_CLP':
        df = informe_v1(producto, start_date, end_date, period, usd, uf)
    else:
        df = informe_ndf(start_date, end_date, period)
    df = df.rename(columns={'SD': 'Zs', 'Days Traded': 'Trades'})
    df = df.reset_index(drop=False)
    return df


def get_historic(producto, start_date, end_date, period, tenor_range=None, usd=1, uf=1, duration=None, l=1):
    # get data
    start = datetime.now()
    df = query_by_daterange(producto, start_date, end_date)
    end = datetime.now()
    #print("query_by_daterange time:", (end-start).seconds)

    # usar tenors en rango
    if tenor_range is not None:
        mask = df.apply(lambda row: tools.in_date(
            row['Tenor'], tenor_range), axis=1)
        df = df[mask]

    #start = datetime.now()
    if producto != "NDF_USD_CLP":
        # pasar a dv01
        df = tools.volume_to_dv01(df, usd, uf, duration, l)
    else:
        df['Volume'] = df['Volume']*l

    # date to datetime
    df = df.reset_index(drop=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df = tools.fill_df(df, start_date, end_date)

    if period == 'DAILY':
        df = df.groupby(['Tenor', 'Date']).agg({'Volume': 'sum'}).reset_index()
    elif period == 'WEEKLY':
        df = df.groupby('Tenor').resample(
            'W', label='left', on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        df = df.groupby('Tenor').resample(
            "M", label='left', on='Date').sum().reset_index()

    return df


def get_specific(producto, start_date, end_date, period, tenor_range=None, usd=1, uf=1, duration=None, l=1):
    # cargar data a comparar
    if period == 'DAILY':
        period_df = query_by_date(producto, end_date)
        if period_df.empty:
            period_df = pd.DataFrame([['0Y', 0, end_date]], columns=[
                                     'Tenor', 'Volume', 'Date'])
        period_df = period_df.reset_index(drop=True)
        period_df['Date'] = pd.to_datetime(period_df['Date'])
        period_df = tools.fill_df(period_df, end_date, end_date)

    elif period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + \
            timedelta(days=-start_date.weekday(), weeks=1)
        end_date = end_date - \
            timedelta(days=start_date.weekday()) - timedelta(days=3)

        # esta definido como días habiles desde hoy
        offset_days = pd.date_range(
            start=end_date-timedelta(days=6), end=end_date, freq='B').date[0]
        period_df = query_by_daterange(producto, offset_days, end_date)
        if period_df.empty:
            period_df = pd.DataFrame([['0Y', 0, end_date]], columns=[
                                     'Tenor', 'Volume', 'Date'])
        period_df = period_df.reset_index(drop=True)
        period_df['Date'] = pd.to_datetime(period_df['Date'])
        period_df = tools.fill_df(period_df, offset_days, end_date)

    elif period == 'MONTHLY':
        # esta definido como días habiles desde hoy
        offset_days = pd.date_range(
            start=end_date-timedelta(days=31), end=end_date, freq='B').date[0]
        period_df = query_by_daterange(producto, offset_days, end_date)
        if period_df.empty:
            period_df = pd.DataFrame([['0Y', 0, end_date]], columns=[
                                     'Tenor', 'Volume', 'Date'])
        period_df = period_df.reset_index(drop=True)
        period_df['Date'] = pd.to_datetime(period_df['Date'])
        period_df = tools.fill_df(period_df, offset_days, end_date)

    # usar tenors en rango
    if tenor_range is not None:
        mask = period_df.apply(lambda row: tools.in_date(
            row['Tenor'], tenor_range), axis=1)
        period_df = period_df[mask]

    if producto != "NDF_USD_CLP":
        # pasar a dv01
        period_df = tools.volume_to_dv01(period_df, usd, uf, duration, l)
    else:
        period_df['Volume'] = period_df['Volume']*l

    return period_df
