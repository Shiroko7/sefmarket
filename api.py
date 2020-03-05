# -*- coding: utf-8 -*- 

import time

# Using graph_objects
import plotly
import plotly.graph_objects as go

#Operaciones con fechas
from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta

#Para leer tablas: excel,csv,html
import pandas as pd
import os

#Para parsear strings
import re

#otras operaciones
import numpy as np
from functools import reduce
import warnings

#Conexión base de datos
#<>dependencia con psycopg2
import sqlalchemy as db
from sqlalchemy import create_engine  
from sqlalchemy import Column, String,DateTime,Integer,Float,Text
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker

d_clp = {
            '3M':0.2458,
            '6M':0.4916,
            '9M':0.7374,
            '12M':0.9832,
            '18M':1.4578,
            '2Y':1.9469,
            '3Y':2.8853,
            '4Y':3.7912,
            '5Y':4.6572,
            '6Y':5.4907,
            '7Y':6.6549,
            '8Y':7.0494,
            '9Y':7.7752,
            '10Y':8.4804,
            '12Y':9.8435,
            '15Y':11.7102,
            '20Y':14.4731,
            '25Y':16.7898,
            '30Y':18.7426,
    }


d_clf = {
            "3M":0.2470,
            "6M":0.4923,
            "9M":0.7415,
            "12M":0.9880,
            "18M":1.4740,
            "2Y":1.9743,
            "3Y":2.9533,
            "4Y":3.9386,
            "5Y":4.9360,
            "6Y":5.9477,
            "7Y":6.9660,
            "8Y":7.9949,
            "9Y":8.9638,
            "10Y":9.9035,
            "12Y":11.8255,
            "15Y":14.6906,
            "20Y":19.3095,
            "25Y":24.3888,
            "30Y":29.2578
}

d_usd = {
            '12M':0.9989,
            '2Y':1.9989,
            '3Y':2.9958,
            '4Y':3.9906,
            '5Y':4.9815,
            '6Y':5.9660,
            '7Y':6.9465,
            '8Y':7.9207,
            '9Y':8.8856,
            '10Y':9.8391,
            '12Y':11.7196,
            '15Y':14.4671,
            '20Y':18.7730,
            '25Y':22.3150,
            '30Y':25.9001
}



# tenor1 <= tenor2 ? 
def leq_date(tenor1,tenor2):
    if tenor1[-1] == 'D':
        if tenor2[-1] == 'D':
            if int(tenor1[0:-1]) <= int(tenor2[0:-1]):
                return True
            else:
                return False
        else:
            return True
        
    elif tenor1[-1] == 'M':
        if tenor2[-1] == 'D':
            return False
            
        elif tenor2[-1] == 'M':
            if int(tenor1[0:-1]) <= int(tenor2[0:-1]):
                return True
            else:
                return False
        else:
            return True
        
    elif tenor1[-1] == 'Y':
        if tenor2[-1] == 'Y':
            if int(tenor1[0:-1]) <= int(tenor2[0:-1]):
                return True
            else:
                return False
        else:
            return False
        

#COMPARAR TENORS

# tenor1 >= tenor2 ? 
def geq_date(tenor1,tenor2):
    if tenor1[-1] == 'D':
        if tenor2[-1] == 'D':
            if int(tenor1[0:-1]) < int(tenor2[0:-1]):
                return False
            else:
                return True
        else:
            return False
        
    elif tenor1[-1] == 'M':
        if tenor2[-1] == 'D':
            return True
            
        elif tenor2[-1] == 'M':
            if int(tenor1[0:-1]) < int(tenor2[0:-1]):
                return False
            else:
                return True
        else:
            return False
        
    elif tenor1[-1] == 'Y':
        if tenor2[-1] == 'Y':
            if int(tenor1[0:-1]) < int(tenor2[0:-1]):
                return False
            else:
                return True
        else:
            return True

def in_date(tenor, tenor_range):
    start,end = tenor_range
    if geq_date(tenor,start) and leq_date(tenor,end):
        return True
    return False

def tenor_sort_3(lista):
    misc =  list()
    days = list()
    months = list()
    years  = list()
    for tenor in lista:
        if tenor[-1] == 'D':
            days.append(tenor)
        elif tenor[-1] == 'M':
            months.append(tenor)
        elif tenor[-1] == 'Y':
            years.append(tenor)
        else:
            misc.append(tenor)
    days = sorted(days,key=lambda k: int(k[0:-1]))
    months = sorted(months,key=lambda k: int(k[0:-1]))
    years = sorted(years,key=lambda k: int(k[0:-1]))

    order = misc+days+months+years
    return order

def tenor_sort_2(df):
    misc =  list()
    days = list()
    months = list()
    years  = list()
    cols = list(df.columns.values)
    #print(df.iterrows())
    for index, row in df.iterrows():
        
        if row['Tenor'][-1] == 'D':
            days.append(row)
        elif row['Tenor'][-1] == 'M':
            months.append(row)
        elif row['Tenor'][-1] == 'Y':
            years.append(row)
        else:
            misc.append(row)
    days = sorted(days,key=lambda k: int(k['Tenor'][0:-1]))
    months = sorted(months,key=lambda k: int(k['Tenor'][0:-1]))
    years = sorted(years,key=lambda k: int(k['Tenor'][0:-1]))

    order = pd.DataFrame(misc+days+months+years, columns=cols)
    return order


#conectarse a la base de datos
#cambiar esto por un log in con input de usuario
database = create_engine('postgres://pyyaxqhbgdrmnl:1473a2885ea9a1b3caf5305cef587aff5a652a9c4c7b7e99b6241c34dd5ffd7b@ec2-3-230-106-126.compute-1.amazonaws.com:5432/dabap8cbpp5m6s')
base = declarative_base()

Session = sessionmaker(database)  
session = Session()

base.metadata.create_all(database)

#ORM entidades de la bd
class NDF_USD_CLP(base):  
    __tablename__ = 'ndf_usd_clp'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)#,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)
    
class CLP_CAM(base):  
    __tablename__ = 'clp_cam'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)#,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)
    
class CLF_CAM(base):  
    __tablename__ = 'clf_cam'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)#,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)
    
class BASIS(base):  
    __tablename__ = 'basis'
    index = Column(Integer, autoincrement=True, primary_key=True)
    Broker = Column(String)#,primary_key=True)
    Tenor = Column(String)
    Date = Column(DateTime)
    Volume = Column(Float)
    Trades = Column(Integer)



#OPERCIONES QUE MODIFICAN LA B
            


#OPERACIONES QUE LEEN DATOS DE LA BASE DE DATOS
def query_by_date(producto,fecha):
    #elegir tabla
    if producto == 'NDF_USD_CLP':
        input_rows = session.query(NDF_USD_CLP).filter(NDF_USD_CLP.Date == fecha)
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
        dict1.update({'Date': row.Date, 'Broker': row.Broker, 'Tenor': row.Tenor,'Trades': row.Trades,'Volume':row.Volume}) 
        rows_list.append(dict1)
    df = pd.DataFrame(rows_list) 
    #cols = ['Date','Broker','Tenor','Trades','Volume']
    #df = df[cols]
    return df


def query_by_daterange(producto,start_date,end_date):
    #elegir tabla
    if producto == 'NDF_USD_CLP':
        input_rows = session.query(NDF_USD_CLP).filter(NDF_USD_CLP.Date.between(start_date,end_date))
    elif producto == 'CLP_CAM':
        input_rows = session.query(CLP_CAM).filter(CLP_CAM.Date.between(start_date,end_date))
    elif producto == 'CLF_CAM':
        input_rows = session.query(CLF_CAM).filter(CLF_CAM.Date.between(start_date,end_date))
    elif producto == 'BASIS':
        input_rows = session.query(BASIS).filter(BASIS.Date.between(start_date,end_date))
    else:
        return None
    data = dict()

    rows_list = []
    for row in input_rows:
        dict1 = {}
        # get input row in dictionary format
        # key = col_name
        dict1.update({'Date': row.Date, 'Broker': row.Broker, 'Tenor': row.Tenor,'Trades': row.Trades,'Volume':row.Volume}) 
        rows_list.append(dict1)
    df = pd.DataFrame(rows_list) 
    #cols = ['Date','Broker','Tenor','Trades','Volume']
    #df = df[cols]
    return df


#FUNCIONES PARA OPERAR DATA
#for df.apply
def p_change(row):
    if row['Volume'] >= 1.0:
        return (row['Volume'] - 1) * 100
    elif row['Volume'] == 0.0:
        return row['Volume']
    else:
        return (1-row['Volume']) * -100

def dv01(row,usd,uf,duration,l):
    try:
        dv01 = l*row['Volume']*duration[row['Tenor']]*uf/usd /10000
    except:
        if row['Tenor'][-1] == 'M':
            d = int(row['Tenor'][0:-1])/12
        else:
            d = int(row['Tenor'][0:-1])
        dv01 = l*row['Volume']*d*uf/usd /10000
    return dv01
    
def volume_to_dv01(df,usd,uf,duration,l=1):
    dv_df = df.copy()
    dv_df['Volume'] = dv_df.apply(lambda row: dv01(row,usd,uf,duration,l),axis=1)
    return dv_df

#MEAN OF DATAFRAME BY TENOR
def mean_value(df):
    df = df.groupby(['Tenor']).mean().reset_index()
    #df = df.rename(columns = {'Volume':'Mean'})
    return df

#SD OF DATAFRAME BY TENOR
def sd_value(df):
    #para cada fecha en el rango [start_date, start_date + 1 día....]
    df = df.groupby(['Tenor']).std().reset_index()
    df = df.rename(columns = {'Volume':'SD'})
    return df

#MAX OF DATAFRAME BY TENOR
def max_value(df):
    #para cada fecha en el rango [start_date, start_date + 1 día....]
    df = df.groupby(['Tenor']).max().reset_index()
    df = df.rename(columns = {'Volume':'Highest'})
    return df    

def percent_diff(df1,df2):
    df = pd.concat([df2,df1],sort = True)
    #reemplazar valores únicos(no en común entre df1 y df2) por cero (diferencia no cuantificable)
    df.loc[df['Tenor'].value_counts()[df['Tenor']].values == 1, 'Volume'] = 0.0
    #dvidir columnas con tenor común
    df = df.groupby(['Tenor']).agg({'Volume': lambda L: reduce(pd.np.dvide, L)}).reset_index()
    #pasar a porcentaje
    df['Volume'] = df.apply(lambda row: p_change(row),axis=1)
    #ordenar cronológicamente
    #renombrar
    df = df.rename(columns = {'Volume':'Pct change'})
    
    df['Pct change'] = pd.Series([round(val, 1) for val in df['Pct change']], index = df.index)
    df['Pct change'] = pd.Series(["{0:.1f}%".format(val) for val in df['Pct change']], index = df.index)
    
    return df

def absolute_diff(df1,df2):
    df1['Volume'] = df1['Volume']* -1
    df = pd.concat([df2,df1],sort = True)
    #reemplazar valores únicos(no en común entre df1 y df2) por cero (diferencia no cuantificable)
    df.loc[df['Tenor'].value_counts()[df['Tenor']].values == 1, 'Volume'] = 0.0
    #restar columnas con tenor común
    df = df.groupby(['Tenor']).agg({'Volume': 'sum'}).reset_index()
    #ordenar cronológicamente
    #renombrar
    df = df.rename(columns = {'Volume':'Abs change'})
    #devolver  df1 al original
    df1['Volume'] = df1['Volume']* -1
    return df

def fill_df(df,start_date,end_date,fill_broker = True):
    #FILL DIAS QUE DEONDE NO SE TRADEA
    business_days = pd.date_range(start=start_date, end=end_date, freq='B')
    cols = list(df.columns.values)
    tenors = df['Tenor'].unique()

    if not fill_broker and 'Broker' in cols:
        brokers = df['Broker'].unique()
        for broker in brokers:
            for tenor in tenors:
                days_traded = df[(df['Tenor'] == tenor) & (df['Broker'] == broker)]['Date'].unique()
                fills = set(business_days.date)-set(days_traded)
                if len(fills) != 0:
                    fills = pd.to_datetime(list(fills))
                    fill = [{**{key:0 for key in cols},**{'Broker':broker,'Tenor':tenor,'Date':i}} for i in fills]
                    df_fill = pd.DataFrame(fill,columns = cols)
                    df = df.append(df_fill,ignore_index=True,verify_integrity=False)
    else:
        time_fill = timedelta(seconds=0)
        for tenor in tenors:
            days_traded = df[df['Tenor']==tenor]['Date'].unique()
            fills = set(business_days.date)-set(days_traded)
            if len(fills) != 0:
                fills = pd.to_datetime(list(fills))
                fill = [{**{key:0 for key in cols},**{'Tenor':tenor,'Date':i}} for i in fills]
                df_fill = pd.DataFrame(fill,columns = cols)
                df = df.append(df_fill,ignore_index=True,verify_integrity=False)
    return df


def daily_change(producto, start_date,end_date):
    df_list = []
    #query!
    df = query_by_daterange(producto,start_date,end_date)
    df = df.groupby(['Tenor','Date']).agg({'Volume': 'sum'}).reset_index()
    return df


################ CREAR INFORME (TABLA) ############
#################B STYLE #################
def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    s = s.apply(lambda x: x.replace(',',''))
    s = s.astype(int)
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]

def color_negative_red(val):
    if float(val) < 0:
        color = 'red'
    elif float(val) > 0:
        color = 'green'
    else:
        color = 'black'
    return 'color: %s' % color

# Set CSS properties for th elements in dataframe
th_props = [
  ('font-size', '15px'),
  ('text-align', 'center'),
  ('font-weight', 'bold'),
  ('color', '#6d6d6d'),
  ('background-color', '#f7f7f9')
  ]

# Set CSS properties for td elements in dataframe
td_props = [
  ('font-size', '12px'),
  ]

# Set table styles
styles = [
  dict(selector="th", props=th_props),
  dict(selector="td", props=td_props)
  ]

def informe_v1(producto,start_date,period,usd,uf=1):
    if start_date == None:
        return None
    #BILLONES CLP
    if producto == 'CLP_CAM':
        duration = d_clp
        uf = 1
        l = 1e9
    #MILES UF
    elif producto == 'CLF_CAM':
        duration = d_clf
        l = 1e3
    #MILLONES USD
    elif producto == 'BASIS':
        duration = d_usd
        uf =1
        l = 1e6
        usd = 1
    else:
        uf = 1
        l = 1

    #crear df con todos los tenors
    cols = ['Tenor','Volume','DV01','SD','Highest','Mean','Days Traded']
    empty_df = pd.DataFrame(columns = cols)
    for i in duration.keys():
        dfi =  pd.DataFrame([[i,0,0,0,0,0,0]],columns = cols)
        empty_df = empty_df.append(dfi)
    
    #calcular fecha desde hoy
    today = date.today()
    shift = timedelta(max(1,(today.weekday() + 6) % 7 - 3))
    today = today - shift
    if period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        today = today - timedelta(days=today.weekday()) - timedelta(days=3)

    #print("Generando tabla...")
    #clear_output(wait=False)
    #cargar data historica y pasar a dv01
    historic_df = daily_change(producto,start_date,today)
    historic_df = historic_df.fillna(0)
        
    #pasar a DV01
    historic_df = volume_to_dv01(historic_df,usd,uf,duration,l)
    
    #date to datetime
    historic_df = historic_df.reset_index(drop=True)
    historic_df.Date = pd.to_datetime(historic_df.Date.fillna(pd.NaT),errors='coerce')
    
    #sacar volumen de DV01 periodical
    if period == 'DAILY':
        periodly_dv = historic_df.groupby('Date').sum().reset_index()
    elif period == 'WEEKLY':
        periodly_dv = historic_df.resample('W-Mon', label='left', on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        periodly_dv = historic_df.resample('M', label='left', on='Date').sum().reset_index()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None
    

    #agregar número de días en que se tranzo
    trades_df = historic_df.groupby(['Tenor']).size().reset_index(name='Days Traded')

    #calcular histric values
    historic_trades = historic_df['Date'].nunique()
    
    #hacer un BIG FILL
    historic_df = fill_df(historic_df,start_date,today)
    
    #date to datetime
    
    historic_df = historic_df.reset_index(drop=True)
    historic_df['Date'] = pd.to_datetime(historic_df['Date'].fillna(pd.NaT),errors='coerce')

    if period == 'DAILY':
        historic_mean = historic_df.groupby('Date').agg({'Volume':'sum'}).reset_index()['Volume'].mean()
    elif period == 'WEEKLY':
        historic_df = historic_df.groupby('Tenor').resample('W',label='left',on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg({'Volume':'sum'}).reset_index()['Volume'].mean()
    elif period == 'MONTHLY':
        historic_df = historic_df.groupby('Tenor').resample("M",label='left',on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg({'Volume':'sum'}).reset_index()['Volume'].mean()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None
    
        
    historic_sd = historic_df['Volume'].std()
    

    #calcular media
    mean_df = mean_value(historic_df)
    #encontrar valor máximo
    max_df = max_value(historic_df)
    max_df = max_df[['Tenor','Highest']]
    #calcular desviación estándar
    sd_df = sd_value(historic_df)
    sd_df = sd_df[['Tenor','SD']]
        
    #cargar data a comparar
    if period == 'DAILY':
        period_volume_df = query_by_date(producto,today)
        if not period_volume_df.empty:
            period_volume_df = period_volume_df.groupby(['Tenor']).agg({'Volume':'sum'}).reset_index()
            period_df = volume_to_dv01(period_volume_df,usd,uf,duration,l)
        else:
            period_volume_df = empty_df[['Tenor','Volume']]
            period_df = empty_df[['Tenor','Volume']]
    elif period == 'WEEKLY':
        #esta definido como días habiles desde hoy
        offset_days = pd.date_range(start=today-timedelta(days=6), end=today, freq='B').date[0]
        period_volume_df = daily_change(producto,offset_days,today)
        if not period_volume_df.empty:
            period_volume_df = period_volume_df.groupby(['Tenor']).agg({'Volume':'sum'}).reset_index()
            period_df = volume_to_dv01(period_volume_df,usd,uf,duration,l)
        else:
            period_volume_df = empty_df[['Tenor','Volume']]
            period_df = empty_df[['Tenor','Volume']]
    elif period == 'MONTHLY':
        #esta definido como días habiles desde hoy
        offset_days = pd.date_range(start=today-timedelta(days=31), end=today, freq='B').date[0]        
        period_volume_df = daily_change(producto,offset_days,today)
        if not period_volume_df.empty:
            period_volume_df = period_volume_df.groupby(['Tenor']).agg({'Volume':'sum'}).reset_index()
            period_df = volume_to_dv01(period_volume_df,usd,uf,duration,l)
        else:
            period_volume_df = empty_df[['Tenor','Volume']]
            period_df = empty_df[['Tenor','Volume']]
    
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None
        
    #renombrar columnas
    period_df = period_df.rename(columns = {'Volume':'DV01'})
    mean_df = mean_df.rename(columns = {'Volume':'Mean'})
    
    #crear tabla
    df = reduce(lambda x, y: pd.merge(x, y, how='outer',on = 'Tenor'), [period_volume_df,period_df,max_df,mean_df,trades_df,sd_df])
    df = pd.concat([df,empty_df],sort=True)
    df = df.groupby(['Tenor']).sum().reset_index()
    df = tenor_sort_2(df)
    df = df.fillna(0)
    #pasar desviación estándar a número de desviaciones estandar
    df['SD'] = (df['DV01'] - df['Mean']) / df['SD']
    df = df.replace(np.inf, 0)
    df = df.replace(-np.inf, 0)
    df = df.fillna(0)
    #Agregar total
    t = {'Tenor':'Total',
         'Volume': df['Volume'].sum(),
         'DV01':df['DV01'].sum(),
         'Highest':periodly_dv['Volume'].max(),
         'Mean':historic_mean,
         'Days Traded':historic_trades,
         'SD':(df['DV01'].sum()-historic_mean)/historic_sd
    }
    total = pd.Series(t)
    df = df.append(total,ignore_index=True)
    
    #formato tabla
    df['Mean'] = pd.Series(["{0:,.0f}".format(val) for val in df['Mean']], index = df.index)
    #df['SD'] = pd.Series([round(val * 2) / 2 for val in df['SD']], index = df.index)
    df['SD'] = pd.Series(["{0:,.1f}".format(val) for val in df['SD']], index = df.index)
    df['Highest'] = pd.Series(["{0:,.0f}".format(val) for val in df['Highest']], index = df.index)
    df['DV01'] = pd.Series(["{0:,.0f}".format(val) for val in df['DV01']], index = df.index)
    df['Volume'] = pd.Series(["{0:,.0f}".format(val) for val in df['Volume']], index = df.index)
    df['Days Traded'] = pd.Series(["{0:,.0f}".format(val) for val in df['Days Traded']], index = df.index)
    df = df[cols]
    df = df.set_index('Tenor')
    #print("Producto: " + producto)
    #print("Start Date: " + str(start_date))
    #print("End Date:" + str(today))
    return df

def informe_ndf(start_date, period):
    if start_date == None:
        return None
        
    #crear df con todos los tenors
    cols = ['Tenor','Volume','SD','Highest','Mean','Days Traded']

    #calcular fecha desde hoy
    today = date.today()
    shift = timedelta(max(1,(today.weekday() + 6) % 7 - 3))
    today = today - shift
    
    if period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        today = today - timedelta(days=today.weekday()) - timedelta(days=3)
        
    #print("Generando tabla...")
    #print("Producto: NDF_USD_CLP")
    #print("Start Date: " + str(start_date))
    #print("End Date:" + str(today))

    #cargar data historica 
    historic_df = daily_change('NDF_USD_CLP',start_date,today)
    historic_df = historic_df.fillna(0)
    
    #date to datetime
    historic_df = historic_df.reset_index(drop=True)
    historic_df.Date = pd.to_datetime(historic_df.Date.fillna(pd.NaT),errors='coerce')
    
    #sacar volumen de DV01 periodical
    if period == 'DAILY':
        periodly_dv = historic_df.groupby('Date').sum().reset_index()
    elif period == 'WEEKLY':
        periodly_dv = historic_df.resample('W-Mon', label='left', on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        periodly_dv = historic_df.resample('M', label='left', on='Date').sum().reset_index()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    #agregar número de días en que se tranzo
    trades_df = historic_df.groupby(['Tenor']).size().reset_index(name='Days Traded')
    
    #calcular histric values
    historic_trades = historic_df['Date'].nunique()
    
    #hacer un BIG FILL
    historic_df = fill_df(historic_df,start_date,today)
    
    #date to datetime
    historic_df = historic_df.reset_index(drop=True)
    historic_df['Date'] = pd.to_datetime(historic_df['Date'].fillna(pd.NaT),errors='coerce')

    if period == 'DAILY':
        historic_mean = historic_df.groupby('Date').agg({'Volume':'sum'}).reset_index()['Volume'].mean()
    
    elif period == 'WEEKLY':
        historic_df = historic_df.groupby('Tenor').resample('W',label='left',on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg({'Volume':'sum'}).reset_index()['Volume'].mean()
    elif period == 'MONTHLY':
        historic_df = historic_df.groupby('Tenor').resample("M",label='left',on='Date').sum().reset_index()
        historic_mean = historic_df.groupby('Date').agg({'Volume':'sum'}).reset_index()['Volume'].mean()
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None
        
    historic_sd = historic_df['Volume'].std()
    
    #calcular media
    mean_df = mean_value(historic_df)
    
    #encontrar valor máximo
    max_df = max_value(historic_df)
    max_df = max_df[['Tenor','Highest']]
    #calcular desviación estándar
    sd_df = sd_value(historic_df)
    sd_df = sd_df[['Tenor','SD']]
    
    #cargar data a comparar
    if period == 'DAILY':
        period_volume_df = query_by_date('NDF_USD_CLP',today)
        period_volume_df = period_volume_df.groupby(['Tenor']).agg({'Volume':'sum'}).reset_index()

    elif period == 'WEEKLY':
        #esta definido como días habiles desde hoy
        offset_days = pd.date_range(start=today-timedelta(days=6), end=today, freq='B').date[0]
        period_volume_df = daily_change('NDF_USD_CLP',offset_days,today)
        period_volume_df = period_volume_df.groupby(['Tenor']).agg({'Volume':'sum'}).reset_index()

    elif period == 'MONTHLY':
        #esta definido como días habiles desde hoy
        offset_days = pd.date_range(start=today-timedelta(days=31), end=today, freq='B').date[0]        
        period_volume_df = daily_change('NDF_USD_CLP',offset_days,today)
        period_volume_df = period_volume_df.groupby(['Tenor']).agg({'Volume':'sum'}).reset_index()
    
    else:
        #print("ERROR: variable 'period' no esta bien definida, opciones disponibles: {DAILY,WEEKLY,MONTHLY}")
        return None

    #renombrar columnas
    
    mean_df = mean_df.rename(columns = {'Volume':'Mean'})
    #crear tabla
    df = reduce(lambda x, y: pd.merge(x, y, how='outer',on = 'Tenor'), [period_volume_df,max_df,mean_df,trades_df,sd_df])

    df = df.groupby(['Tenor']).sum().reset_index()
    df = tenor_sort_2(df)
    df = df.fillna(0)
    #pasar desviación estándar a número de desviaciones estandar
    df['SD'] = (df['Volume'] - df['Mean']) / df['SD']
    df = df.replace(np.inf, 0)
    df = df.replace(-np.inf, 0)
    df = df.fillna(0)
    #Agregar total
    t = {'Tenor':'Total',
         'Volume': df['Volume'].sum(),
         'Highest':periodly_dv['Volume'].max(),
         'Mean':historic_mean,
         'Days Traded':historic_trades,
         'SD':(df['Volume'].sum()-historic_mean)/historic_sd
    }
    total = pd.Series(t)
    df = df.append(total,ignore_index=True)
    #formato tabla
    df['Mean'] = pd.Series(["{0:,.0f}".format(val) for val in df['Mean']], index = df.index)
    #df['Mean'] = df.apply(lambda x: "{:,}".format(x['Mean']), axis=1)
    #df['SD'] = pd.Series([round(val * 2) / 2 for val in df['SD']], index = df.index)
    df['SD'] = pd.Series(["{0:,.1f}".format(val) for val in df['SD']], index = df.index)
    df['Highest'] = pd.Series(["{0:,.0f}".format(val) for val in df['Highest']], index = df.index)
    df['Volume'] = pd.Series(["{0:,.0f}".format(val) for val in df['Volume']], index = df.index)
    df['Days Traded'] = pd.Series(["{0:,.0f}".format(val) for val in df['Days Traded']], index = df.index)
    df = df[cols]
    df = df.set_index('Tenor')
    return df


def informe(producto, start_date, period, usd, uf):
    if producto != 'NDF_USD_CLP':
        df = informe_v1(producto,start_date,period,usd,uf)
    else:
        df = informe_ndf(start_date,period)
    df = df.reset_index(drop=False)
    return df

def values_product(producto,usd,uf):
    #BILLONES CLP
    if producto == 'CLP_CAM':
        duration = d_clp
        l = 1e9
        uf = 1
    #MILES UF
    elif producto == 'CLF_CAM':
        duration = d_clf
        l = 1e3
    #MILLONES USD
    elif producto == 'NDF_USD_CLP':
        duration = None
        l = 1e6
        uf = 1
    #MILLONES USD
    elif producto == 'BASIS':
        duration = d_usd
        l = 1e6
        uf = 1
        usd = 1
    else:
        l = 1
        uf = 1
    return usd,uf,duration,l

def get_historic(producto,start_date,today,period,tenor_range=None,usd=1,uf=1,duration=None,l=1):
    #get data
    start = datetime.now()
    df = query_by_daterange(producto, start_date,today)
    end  = datetime.now()
    #print("query_by_daterange time:", (end-start).seconds)
    
    #usar tenors en rango
    if tenor_range is not None:
        mask = df.apply(lambda row: in_date(row['Tenor'],tenor_range), axis=1)
        df = df[mask]

    #start = datetime.now()
    if producto != "NDF_USD_CLP":
        #pasar a dv01
        df = volume_to_dv01(df,usd,uf,duration,l)
    else:
        df['Volume'] = df['Volume']*l
    #end = datetime.now()
    #print("dv01 time: ", (end-start).seconds)
        
    #start = datetime.now()
    df = fill_df(df,start_date,today)
    #end = datetime.now()
    #print("fill_df time: ", (end-start).seconds)
    
    #date to datetime
    df = df.reset_index(drop=True)
    df['Date'] = pd.to_datetime(df['Date'].fillna(pd.NaT),errors='coerce')
    
    if period == 'DAILY':
        df = df.groupby(['Tenor','Date']).agg({'Volume':'sum'}).reset_index()
    elif period == 'WEEKLY':
        df = df.groupby('Tenor').resample('W',label='left',on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        df = df.groupby('Tenor').resample("M",label='left',on='Date').sum().reset_index()
        
    return df
        
def get_specific(producto,start_date,today,period,tenor_range=None,usd=1,uf=1,duration=None,l=1):
    #cargar data a comparar
    if period == 'DAILY':
        period_df = query_by_date(producto,today)
        if period_df.empty:
            period_df = pd.DataFrame([['0Y',0,today]],columns = ['Tenor','Volume','Date'])
        period_df = fill_df(period_df,today,today)

    elif period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + timedelta(days=-start_date.weekday(), weeks=1)   
        today = today - timedelta(days=start_date.weekday()) - timedelta(days=3)
        
        #esta definido como días habiles desde hoy
        offset_days = pd.date_range(start=today-timedelta(days=6), end=today, freq='B').date[0]
        period_df = query_by_daterange(producto,offset_days,today)
        if period_df.empty:
            period_df = pd.DataFrame([['0Y',0,today]],columns = ['Tenor','Volume','Date'])
        period_df = fill_df(period_df,offset_days,today)

    elif period == 'MONTHLY':
        #esta definido como días habiles desde hoy
        offset_days = pd.date_range(start=today-timedelta(days=31), end=today, freq='B').date[0]        
        period_df = query_by_daterange(producto,offset_days,today)
        if period_df.empty:
            period_df = pd.DataFrame([['0Y',0,today]],columns = ['Tenor','Volume','Date'])
        period_df = fill_df(period_df,offset_days,today)
        
    #usar tenors en rango
    if tenor_range is not None:
        mask = period_df.apply(lambda row: in_date(row['Tenor'],tenor_range), axis=1)
        period_df = period_df[mask]

    if producto != "NDF_USD_CLP":
        #pasar a dv01
        period_df = volume_to_dv01(period_df,usd,uf,duration,l)
    else:
        period_df['Volume'] = period_df['Volume']*l
    period_df = period_df.reset_index(drop=True)
    period_df['Date'] = pd.to_datetime(period_df['Date'].fillna(pd.NaT),errors='coerce')
    return period_df



def box_plot_all(producto,start_date,period,tenor_range=None,usd=1,uf=1,show_total=False):
    #definir today (ayer)
    today = date.today()
    shift = timedelta(max(1,(today.weekday() + 6) % 7 - 3))
    today = today - shift
    
    usd,uf,duration,l = values_product(producto,usd,uf)
    
    #start = datetime.now()
    df = get_historic(producto,start_date,today,period,tenor_range,usd,uf,duration,l)
    #end = datetime.now()
    #print('get_historic time: ',(end-start).seconds)

    #start = datetime.now()
    period_df = get_specific(producto,start_date,today,period,tenor_range,usd,uf,duration,l)
    #end = datetime.now()
    #print('get_specific time: ',(end-start).seconds)


    #start = datetime.now()
    if show_total:
    #Agregar total
        date_list = df['Date'].unique()
        for single_date in date_list:
            t = {'Tenor':'Total',
                 'Volume': df[df['Date']==single_date]['Volume'].sum(),
                 'Date': single_date,
            }
            total = pd.Series(t)
            df = df.append(total,ignore_index=True)
            
        t = {'Broker':'',
             'Tenor':'Total',
             'Volume': period_df['Volume'].sum(),
             'Date': single_date,
             'Trades': period_df['Trades'].sum(),
        }
        total = pd.Series(t)
        period_df = period_df.append(total,ignore_index=True)
    
    #agregar boxplot por tenor
    tenors = df['Tenor'].unique()
    tenors=tenor_sort_3(tenors)
    fig = go.Figure()    
    for tenor in tenors:
        fig.add_trace(go.Box(y=df[df['Tenor']==tenor]['Volume'],name=tenor,boxpoints= False))
        period_value = period_df[period_df['Tenor']==tenor]['Volume'].sum()
        
        #agregar valor de hoy ...
        fig.add_trace(go.Scatter(x=[tenor],
                                 y=[period_value],
                                 mode='markers',
                                 name = str(period)+" value",
                                 showlegend=False,
                                 marker=dict(size=[26],
                                             color=['indianred'],
                                             line=dict(width=1))))


        #visible label tttt
        if producto != 'NDF_USD_CLP':
            image = "{0:.1f} K".format(period_value/1e3)
        else:
            image = "{0:.1f} B".format(period_value/1e9)
        fig.add_trace(go.Scatter(x=[tenor],
                                 y=[period_value],
                                 text=[image],
                                 name = str(period)+" value",
                                 showlegend=False,
                                 mode="text",
                                 textfont=dict(color="white",
                                               size=8,
                                               family="Arail",)))
    
    
    #formatear fecha
    if start_date.year == today.year:
        start_date = start_date.strftime('%d %B')
    else:
        start_date = start_date.strftime('%d %B %Y')
    today = today.strftime('%d %B %Y')

    
    # Add range slider
    fig.update_layout(
        xaxis=go.layout.XAxis(
            rangeslider=dict(
                thickness = 0.01,
                visible=True
            ),
        )
    )
    if producto != 'NDF_USD_CLP':
        fig.update_layout(xaxis={'title': producto},
                          yaxis={'title':'DV01'},
                          title= str(period)+ ' Distribution ' + producto+': '+str(start_date)+' to '+str(today))
    else:
        fig.update_layout(xaxis={'title': producto},
                          yaxis={'title':'Volume'},
                          title= str(period)+ ' Distribution ' + producto+': '+str(start_date)+' to '+str(today))        
    
    #fig.show()
    #end = datetime.now()
    #print('boxploting time: ', (end-start).seconds)
    return fig

def general_graph(producto, tenor, start_date,period,usd=770, uf=1, cumulative = False):
    #definir today (ayer)
    today = date.today()
    shift = timedelta(max(1,(today.weekday() + 6) % 7 - 3))
    today = today - shift
    
    usd,uf,duration,l = values_product(producto,usd,uf)
    
    if period == 'WEEKLY':
        #last_monday = start_date - timedelta(days=start_date.weekday())
        #coming_monday = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        #start_date = min([last_monday,coming_monday], key=lambda x: abs(x - start_date))
        start_date = start_date + timedelta(days=-start_date.weekday(), weeks=1)
        today = today - timedelta(days=today.weekday()) - timedelta(days=3)

    df = daily_change(producto, start_date, today)
    #hacer un BIG FILL
    df = fill_df(df,start_date,today)
    
    #date to datetime
    df = df.reset_index(drop=True)
    df['Date'] = pd.to_datetime(df['Date'].fillna(pd.NaT),errors='coerce')
    if period == 'DAILY':
        df = df.groupby(['Tenor','Date']).agg({'Volume':'sum'}).reset_index()
    elif period == 'WEEKLY':
        df = df.groupby('Tenor').resample('W',label='left',on='Date').sum().reset_index()
    elif period == 'MONTHLY':
        df = df.groupby('Tenor').resample("M",label='left',on='Date').sum().reset_index()

    if producto != 'NDF_USD_CLP':
        #pasar a DV01
        df = volume_to_dv01(df,usd,uf,duration,l)
        df = df.rename(columns = {'Volume':'DV01'})
        
        if tenor == 'All':
            df = df.groupby(['Date']).sum().reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['DV01']
            else:
                y_ = df['DV01'].cumsum()
        else:
            df = df.groupby(['Tenor','Date']).agg({'DV01':'sum'}).reset_index()
            x_ = df[df['Tenor']==tenor]['Date']
            if cumulative == False:
                y_ = df[df['Tenor']==tenor]['DV01']
            else:
                y_ = df[df['Tenor']==tenor]['DV01'].cumsum()  
                
        #crear time series
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_, y=y_,name=tenor))#, name="AAPL Low",line_color='dimgray'))
        
        if cumulative == False:
            #agregar meadia
            fig.add_shape(
                    # Line Horizontal
                    go.layout.Shape(
                        type="line",
                        x0=df['Date'][0],
                        y0=y_.mean(),
                        x1=today,
                        y1=y_.mean(),
                        line=dict(
                            color="darkblue",
                            width=4,
                            dash="dashdot",
                        ),
                ))
        #formatear fecha
        if start_date.year == today.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        today = today.strftime('%d %B %Y')
        fig.update_layout(xaxis={'title':tenor},
                          yaxis={'title':'DV01'})
        
    else:
        df['Volume']=df['Volume']*l
        if tenor == 'All':
            df = df.groupby(['Date']).sum().reset_index()
            x_ = df['Date']
            if cumulative == False:
                y_ = df['Volume']
            else:
                y_ = df['Volume'].cumsum()
        else:
            df = df.groupby(['Tenor','Date']).agg({'Volume':'sum'}).reset_index()
            x_ = df[df['Tenor']==tenor]['Date']
            if cumulative == False:
                y_ = df[df['Tenor']==tenor]['Volume']
            else:
                y_ = df[df['Tenor']==tenor]['Volume'].cumsum()
                
        #crear time series
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_, y=y_,name=tenor))#, name="AAPL Low",line_color='dimgray'))
        if cumulative == False:
            fig.add_shape(
                    # Line Horizontal
                    go.layout.Shape(
                        type="line",
                        x0=df['Date'][0],
                        y0=y_.mean(),
                        x1=today,
                        y1=y_.mean(),
                        line=dict(
                            color="darkblue",
                            width=2,
                            dash="dashdot",
                        ),
                ))

        #formatear fecha
        if start_date.year == today.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        today = today.strftime('%d %B %Y')
        
        fig.update_layout(xaxis={'title':tenor},
                          yaxis={'title':'Volume'})
    fig.update_layout(title=  str(period)+ ' Time Series ' + producto)

    # Add range slider
    fig.update_layout(
        xaxis=go.layout.XAxis(
            rangeslider=dict(
                visible=True
            ),
        )
    )
    
    return fig

def participation_graph(producto, start_date, tenor_range,usd=770, uf=1):
    #definir today (ayer)
    today = date.today()
    shift = timedelta(max(1,(today.weekday() + 6) % 7 - 3))
    today = today - shift
    
    usd,uf,duration,l = values_product(producto,usd,uf)
    
    #cargar data
    df = query_by_daterange(producto, start_date, today)
    df = df.groupby(['Broker','Tenor']).agg({'Volume': 'sum'}).reset_index()
    
    #usar tenors en rango
    mask = df.apply(lambda row: in_date(row['Tenor'],tenor_range), axis=1)
    df = df[mask]
    
    if df.empty:
        #print("No se encontraron transacciones en: " + str(tenor_range))
        return None
    
    #formatear fecha
    if start_date.year == today.year:
        start_date = start_date.strftime('%d %B')
    else:
        start_date = start_date.strftime('%d %B %Y')
    today = today.strftime('%d %B %Y')
    if producto != 'NDF_USD_CLP':
        #pasar a DV01
        df = volume_to_dv01(df,usd,uf,duration,l)
        df = df.rename(columns = {'Volume':'DV01'})
        #agrupar por broker
        df = df.groupby(['Broker']).agg({'DV01': 'sum'}).reset_index()
        #Agregar total
        total_value = df['DV01'].sum()
        t = {'Broker':'Total',
             'DV01': total_value
        }
        total = pd.Series(t)
        df = df.append(total,ignore_index=True)
        #calcular % de participación
        df['Share'] = df['DV01']*100/total_value
        df['Share'] =  pd.Series(["{0:.0f}% market share".format(val) for val in df['Share']], index = df.index)
        fig = go.Figure([go.Bar(x=df['Broker'], y=df['DV01'],
                                hovertext=df['Share'])
                        ])
        fig.update_layout(barmode='stack',
                      xaxis={'title':'Broker','categoryorder':'total descending'},
                      yaxis={'title':'DV01'})
    else:
        #agrupar por broker
        df = df.groupby(['Broker']).agg({'Volume': 'sum'}).reset_index()
        df['Volume']=df['Volume']*l
        #Agregar total
        total_value = df['Volume'].sum()
        t = {'Broker':'Total',
             'Volume': total_value
        }
        total = pd.Series(t)
        df = df.append(total,ignore_index=True)
        #calcular % de participación
        df['Share'] = df['Volume']*100/total_value
        df['Share'] =  pd.Series(["{0:.0f}% market share".format(val) for val in df['Share']], index = df.index)
        fig = go.Figure([go.Bar(x=df['Broker'], y=df['Volume'],
                                hovertext=df['Share'])
                        ])
        fig.update_layout(barmode='stack',
                          xaxis={'title':'Broker','categoryorder':'total descending'},
                          yaxis={'title':'Volume'})
    fig.update_layout(title= producto+' Market Share: '+start_date+' to '+today)
        
    return fig


def participation_graph_by_date(producto, start_date,tenor_range=None,usd=770, uf=1,percent=False):
    #definir today (ayer)
    today = date.today()
    shift = timedelta(max(1,(today.weekday() + 6) % 7 - 3))
    today = today - shift
    
    usd,uf,duration,l = values_product(producto,usd,uf)
    
    df = query_by_daterange(producto, start_date, today)
    #usar tenors en rango
    if tenor_range is not None:
        mask = df.apply(lambda row: in_date(row['Tenor'],tenor_range), axis=1)
        df = df[mask]
    
    if producto != 'NDF_USD_CLP':
        #pasar a DV01
        df = volume_to_dv01(df,usd,uf,duration,l)
        df = df.rename(columns = {'Volume':'DV01'})
        
        df = fill_df(df,start_date,today,False)
        df = df.reset_index(drop=True)
        df['Date'] = pd.to_datetime(df['Date'].fillna(pd.NaT),errors='coerce')
        #Agregar total
        
        brokers = df['Broker'].unique()

        total = df.groupby(['Date']).agg({'DV01':'sum'}).reset_index()['DV01']
        
        fig = go.Figure()
        for broker in brokers:
            df_ = df[df['Broker'] == broker].groupby(['Date']).agg({'DV01':'sum'}).reset_index()
            x_ = df_['Date']
            y_ = df_['DV01'].cumsum()
            z_ = 100*y_/total.cumsum()
            if not percent:
                fig.add_trace(go.Scatter(x=x_, y=y_,
                                        hovertemplate =
                                                        '$%{y:.0f}'+
                                                        '<br>%{x}</br>'+
                                                        '%{text}',
                                                        text = ['{0:.0f}% market share'.format(i) for i in z_],
                                         name=broker))
            else:
                fig.add_trace(go.Scatter(x=x_, y=z_,
                        hovertemplate =
                                        '%{y:.0f}% market share'+
                                        '<br>%{x}</br>'+
                                        '%{text}',
                                        text = ['${0:.0f}'.format(i) for i in y_],
                         name=broker))
                fig.update_yaxes(range=[0, 100])
                
        #formatear fecha
        if start_date.year == today.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        today = today.strftime('%d %B %Y')
        
        fig.update_layout(barmode='stack',
                      xaxis={'title':'Broker','categoryorder':'total descending'},
                      yaxis={'title':'DV01'})
    else:
        #agrupar por broker
        df = fill_df(df,start_date,today,False)
        df = df.reset_index(drop=True)
        df['Date'] = pd.to_datetime(df['Date'].fillna(pd.NaT),errors='coerce')
        df = df.groupby(['Broker','Date']).agg({'Volume': 'sum'}).reset_index()
        df['Volume']=df['Volume']*l        

        total = df.groupby(['Date']).agg({'Volume':'sum'}).reset_index()['Volume']
        
        fig = go.Figure()
        brokers = df['Broker'].unique()
        for broker in brokers:
            df_ = df[df['Broker'] == broker].groupby(['Date']).agg({'Volume':'sum'}).reset_index()
            
            x_ = df_['Date']
            y_ = df_['Volume'].cumsum()
            z_ = 100*y_/total.cumsum()
            if not percent:
                fig.add_trace(go.Scatter(x=x_, y=y_,
                                        hovertemplate =
                                                        '$%{y:.0f}'+
                                                        '<br>%{x}</br>'+
                                                        '%{text}',
                                                        text = ['{0:.0f}% market share'.format(i) for i in z_],
                                         name=broker))
            else:
                fig.add_trace(go.Scatter(x=x_, y=z_,
                        hovertemplate =
                                        '%{y:.0f}% market share'+
                                        '<br>%{x}</br>'+
                                        '%{text}',
                                        text = ['${0:.0f}'.format(i) for i in y_],
                         name=broker))
                fig.update_yaxes(range=[0, 100])
                
        #formatear fecha
        if start_date.year == today.year:
            start_date = start_date.strftime('%d %B')
        else:
            start_date = start_date.strftime('%d %B %Y')
        today = today.strftime('%d %B %Y')
        
        fig.update_layout(barmode='stack',
                      xaxis={'title':'Broker','categoryorder':'total descending'},
                      yaxis={'title':'Volume'})

    fig.update_layout(title= producto+' Market Share: ')
    return fig