# -*- coding: utf-8 -*-
import utils.plots as plots
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
    'postgres://ywbhjstvlwwguj:4169cd9bb75716133a084e53deb4481699ec6cdc5c2d253af098ffb00fc77457@ec2-18-211-48-247.compute-1.amazonaws.com:5432/dc69t4t9dl57ao')
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
        resumen['Volume'] = tools.resumen.apply(
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

    df = tools.resumen_for_BD(date)
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
