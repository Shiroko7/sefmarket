# Para parsear strings

import re

# Operaciones con fechas
import time
from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta

# otras operaciones
import pandas as pd
import numpy as np
from functools import reduce
import warnings


# definir today (ayer)
today = date.today()
shift = timedelta(max(1, (today.weekday() + 6) % 7 - 3))
today = today - shift

d_clp = {
    '3M': 0.2458,
    '6M': 0.4916,
    '9M': 0.7374,
    '12M': 0.9832,
    '18M': 1.4578,
    '2Y': 1.9469,
    '3Y': 2.8853,
    '4Y': 3.7912,
    '5Y': 4.6572,
    '6Y': 5.4907,
    '7Y': 6.6549,
    '8Y': 7.0494,
    '9Y': 7.7752,
    '10Y': 8.4804,
    '12Y': 9.8435,
    '15Y': 11.7102,
    '20Y': 14.4731,
    '25Y': 16.7898,
    '30Y': 18.7426,
}


d_clf = {
    "3M": 0.2470,
    "6M": 0.4923,
    "9M": 0.7415,
    "12M": 0.9880,
    "18M": 1.4740,
    "2Y": 1.9743,
    "3Y": 2.9533,
    "4Y": 3.9386,
    "5Y": 4.9360,
    "6Y": 5.9477,
    "7Y": 6.9660,
    "8Y": 7.9949,
    "9Y": 8.9638,
    "10Y": 9.9035,
    "12Y": 11.8255,
    "15Y": 14.6906,
    "20Y": 19.3095,
    "25Y": 24.3888,
    "30Y": 29.2578
}

d_usd = {
    '12M': 0.9989,
    '2Y': 1.9989,
    '3Y': 2.9958,
    '4Y': 3.9906,
    '5Y': 4.9815,
    '6Y': 5.9660,
    '7Y': 6.9465,
    '8Y': 7.9207,
    '9Y': 8.8856,
    '10Y': 9.8391,
    '12Y': 11.7196,
    '15Y': 14.4671,
    '20Y': 18.7730,
    '25Y': 22.3150,
    '30Y': 25.9001
}
# displayer de tablas by side


def display_side_by_side(*args):
    html_str = ''
    for df in args:
        html_str += df.to_html()
    display_html(html_str.replace(
        'table', 'table style="display:inline"'), raw=True)

# formatear fechas


def f_date(days, weeks, months, years):
    days = int(days)
    weeks = int(weeks)
    months = int(months)
    years = int(years)
    ############# MES >= 30 días #############
    MONTH = 29
    ############# AÑO >= 365 días #############
    YEAR = 365
    ############# mes anterior o siguiente >< 15 días #############
    delta = 15
    # only days
    if weeks == 0 and months == 0 and years == 0:
        # truncar a años
        if days > YEAR:
            y = days//YEAR
            if y == 1:
                tenor = '12M'
                return tenor
            else:
                tenor = str(y) + 'Y'
                return tenor
        # aproximar a la cantidad de meses más cercana
        elif days > MONTH:
            if days % MONTH > delta:
                tenor = str(days//MONTH+1) + 'M'
                return tenor
            else:
                tenor = str(days//MONTH) + 'M'
                return tenor
        else:
            tenor = str(days) + 'D'
            return tenor
    # only weeks
    elif days == 0 and weeks != 0 and months == 0 and years == 0:
        # aproximar a meses
        if weeks >= 4:
            if weeks % 4 > 2:
                tenor = str(weeks//4+1) + 'M'
                return tenor
            else:
                tenor = str(weeks//4) + 'M'
                return tenor
        # pasar a días
        else:
            tenor = str(weeks*7) + 'D'
            return tenor

    # only months
    elif days == 0 and weeks == 0 and months != 0 and years == 0:
        # producto en años
        if months % 12 == 0:
            y = months // 12
            if y == 1:
                tenor = '12M'
                return tenor
            else:
                tenor = str(months // 12) + 'Y'
                return tenor
        elif months > 24:
            tenor = str((months + 12 // 2) // 12) + 'Y'
            return tenor
        # producto en meses o años y medio
        else:
            tenor = str(months) + 'M'
            return tenor
    # only years
    elif days == 0 and weeks == 0 and months == 0 and years != 0:
        if years == 1:
            tenor = '12M'
            return tenor
        else:
            tenor = str(years) + 'Y'
            return tenor
    # Years and months
    elif years != 0 and months != 0:
        tenor = str(years * 12 + months) + 'M'
        return tenor
    # Yeards and days
    elif years != 0 and days != 0:
        if years == 1:
            tenor = '12M'
            return tenor
        else:
            tenor = str(years) + 'Y'
            return tenor
    # Months and days
    elif days != 0 and months != 0:
        # mes más cercano
        if days > delta:
            tenor = str(months+1) + 'M'
            return tenor
        else:
            tenor = str(months) + 'M'
            return tenor
    # Years, months and days
    elif days != 0 and months != 0 and years != 0:
        tenor = str(years * 12 + months) + 'M'
    return "NO MATCH"


# tenor1 <= tenor2 ?
def leq_date(tenor1, tenor2):
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


# COMPARAR TENORS

# tenor1 >= tenor2 ?
def geq_date(tenor1, tenor2):
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
    start, end = tenor_range
    if geq_date(tenor, start) and leq_date(tenor, end):
        return True
    return False


# rules latam
def latam_parser_tenor(row):

    # Expresiones regulares para identificar la fecha
    # NDF USD CLP
    reg1 = re.compile("(FX_NDF_USD-CLP_)(\d+.)")
    # CLP CAMARA
    reg2 = re.compile("(IRS_FF_CLP_([^\s]*_)?)(\d+.)")
    # CLF CAMARA
    reg3 = re.compile("(IRS_CCY_CLF-CLP_)(\d+.)")

    token = str(row["Internal_Prod_ID"])

    # NDF USD CLP
    if reg1.match(token) is not None:
        tenor = reg1.match(token).groups()[1]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # CLP CAMARA
    if reg2.match(token) is not None:
        tenor = reg2.match(token).groups()[2]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor

    # CLF CAMARA
    if reg3.match(token) is not None:
        tenor = reg3.match(token).groups()[1]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # warnings.warn('No se pudo leer TENOR de LatAmSEF '+str(row['Trade_Date']))
    return "NONE"


def latam_parser_ID(row):
    # NDF USD-CLP
    if (row["Asset_Class"] == "FX") & (row["Tran_Type"] == "USDCLP"):
        return "NDF_USD_CLP"

    # CLP CAM
    if (row["Asset_Class"] == "IR") & (row["Traded_Currency"] == "CLP"):
        return "CLP_CAM"

    # CLF CAM
    if (row["Asset_Class"] == "IR") & (row["Traded_Currency"] == "CLF"):
        return "CLF_CAM"
    # warnings.warn('No se pudo leer PRODUCTO de LatAmSEF ' + str(row['Trade_Date']))
    return "NONE"


def latam_proc(fecha):
    fecha_x = "".join(str(fecha).split("-"))
    token = "assets/LatAmSEF_MarketActivityData_{0}.csv".format(fecha_x)

    # parsear como dataframe
    try:
        df = pd.read_csv(token, sep=",")
    except Exception as e:
        # si no existe el archivo crear un dataframe vacio
        # dataframe.columns.values
        print(e)
        df = pd.DataFrame(columns=['SEF_DCM_Name',
                                   'SEF_DCM_LEI',
                                   'Trade_Date',
                                   'Effective_Date',
                                   'Internal_Prod_ID',
                                   'Internal_Prod_Des',
                                   'Name',
                                   'Tenor',
                                   'Asset_Class',
                                   'Base_Prod',
                                   'Sub_Prod',
                                   'Tran_Type',
                                   'Contract_Type',
                                   'Curr_Code',
                                   'DCO_Name',
                                   'DCO_LEI',
                                   'First_Price',
                                   'High_Price',
                                   'Low_Price',
                                   'Last_Price',
                                   'Traded_Currency',
                                   'Volume',
                                   'Notional_USD',
                                   'Trades'])
        return df
    # rellenar NaNs con strings vacios para evitar problemas
    df = df.fillna(" ")
    # filtro df = df[condiciones]
    df = df[
        ((df["Asset_Class"] == "FX") & (df["Tran_Type"] == "USDCLP")) |
        ((df["Asset_Class"] == "IR") & (df["Traded_Currency"] == "CLP")) |
        ((df["Asset_Class"] == "IR") & (df["Traded_Currency"] == "CLF"))
    ]

    if not df.empty:
        # Agregar nueva columna con nombres de los productos
        df["Name"] = df.apply(lambda row: latam_parser_ID(row), axis=1)
        # crear nueva columna con plazo
        df["Tenor"] = df.apply(lambda row: latam_parser_tenor(row), axis=1)
    else:
        df["Name"] = None
        df["Tenor"] = None

    # ordenar columnas
    cols = df.columns.tolist()
    cols.insert(cols.index("Internal_Prod_Des")+1, cols.pop(-1))
    cols.insert(cols.index("Internal_Prod_Des")+1, cols.pop(-1))
    # ordenar columnas
    df = df[cols]
    # rename Notional_Traded_Currency
    df = df.rename(columns={'Notional_Traded_Currency': 'Volume'})
    df["Trades"] = 1
    # df = df.groupby(['Name','Tenor']).agg({'Trades':'sum','Volume':'sum'}).reset_index()
    return df


# tradition


def tradition_parser_tenor(row):
    # Expresiones regulares para identificar la fecha
    # NDF USD CLP
    reg1 = re.compile("(\d+.|..)([^\s]*_USDCLP_NDF)")
    # CLP CAMARA
    reg2 = re.compile("(\d+.)([^\s]*_IRS_[^\s]+_CLICP(_.+)?)")
    # CLF CAMARA
    reg3 = re.compile("(\d+.)([^\s]*_BSW_[^\s]+_CLFUF_[^\s]+_CLICP)")
    # BASIS
    reg4 = re.compile("(\d+.)([^\s]*_BSW_[^\s]+_USDLIBOR_[^\s]+_CLICP)")

    token = str(row["Internal_Prod_ID"])

    # NDF USD CLP
    if reg1.match(token) is not None:
        tenor = reg1.match(token).groups()[0]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            try:
                n = int(n)
                tenor = f_date(n, 0, 0, 0)
            except:
                pass
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        elif tenor[-1] == 'N':
            if n == 'T':
                tenor = '1D'
            elif n == 'O':
                tenor = '1D'
            elif n == 'S':
                tenor = '2D'
        return tenor
    # CLP CAMARA
    elif reg2.match(token) is not None:
        tenor = reg2.match(token).groups()[0]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # CLF CAMARA
    elif reg3.match(token) is not None:
        tenor = reg3.match(token).groups()[0]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # BASIS
    elif reg4.match(token) is not None:
        tenor = reg4.match(token).groups()[0]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # OPTIONS:
    if(str(row['Base_Prod']) == 'NDO'):
        reg0 = re.compile("(\d+.|..)([\s\S]+)")
        token = str(row["Internal_Prod_Des"])
        if reg0.match(token) is not None:
            tenor = reg0.match(token).groups()[0]
            n = tenor[0:-1]
            if tenor[-1] == "D":
                try:
                    n = int(n)
                    tenor = f_date(n, 0, 0, 0)
                except:
                    pass
            elif tenor[-1] == "W":
                tenor = f_date(0, n, 0, 0)
            elif tenor[-1] == "M":
                tenor = f_date(0, 0, n, 0)
            elif tenor[-1] == "Y":
                tenor = f_date(0, 0, 0, n)
            return tenor
    # warnings.warn('No se pudo leer TENOR de TraditionSEF ' +
    #              str(row['Trade_Date']))
    return "NONE"


def tradition_parser_ID(row):
    # NDF USD-CLP
    if (row['Asset_Class'] == 'FX') & (row["Base_Prod"] == 'NDF') & (row["Curr_Code"] == 'USD'):
        return "NDF_USD_CLP"
    # OPTIONS
    elif (row['Asset_Class'] == 'FX') & (row["Base_Prod"] == 'NDO') & (row["Curr_Code"] == 'USD'):
        return "NDO_USD_CLP"
    # CLP CAM
    elif (row['Asset_Class'] == 'IR') & (row["Curr_Code"] == 'CLP'):
        return "CLP_CAM"

    # CLF CAM
    elif (row['Asset_Class'] == 'IR') & (row["Curr_Code"] == 'CLF'):
        return "CLF_CAM"

    # BASIS
    elif (row['Asset_Class'] == 'IR') & (row["Curr_Code"] == 'USD'):
        return "BASIS"
    # warnings.warn('No se pudo leer PRODUCTO de TraditionSEF ' +
    #              str(row['Trade_Date']))
    return "NONE"


def tradition_proc(fecha):
    # rescartar nombre del archivo
    fecha_x = "".join(str(fecha).split("-"))
    token = "assets/SEF16_MKTDATA_TFSU_{0}.csv".format(fecha_x)
    try:
        # parsar como dataframe
        df = pd.read_csv(token, sep="|")
    except Exception as e:
        # si no existe el archivo crear dataframe vacio
        # dataframe.columns.values
        print(e)
        df = pd.DataFrame(columns=['SEF_DCM_Name',
                                   'SEF_DCM_LEI',
                                   'Trade_Date',
                                   'Effective_Date',
                                   'Internal_Prod_ID',
                                   'Internal_Prod_Des',
                                   'Name',
                                   'Tenor',
                                   'Asset_Class',
                                   'Base_Prod',
                                   'Sub_Prod',
                                   'Tran_Type',
                                   'Contract_Type',
                                   'Curr_Code',
                                   'Setl_Method',
                                   'UPI',
                                   'Block_Flag',
                                   'Option_Flag',
                                   'DCO_Name',
                                   'DCO_LEI',
                                   'Premium_Volatility_Other_Flag',
                                   'First_Price',
                                   'High_Price',
                                   'Low_Price',
                                   'Last_Price',
                                   'Traded_Currency',
                                   'Notional_Traded_Currency_DA',
                                   'Volume',
                                   'Total_Notional_USD_DA',
                                   'Cleared_Notional_USD_DA',
                                   'Un_Cleared_Notional_USD_DA',
                                   'Total_Notional_USD_NDA',
                                   'Cleared_Notional_USD_NDA',
                                   'Un_Cleared_Notional_USD_NDA',
                                   'Trades',
                                   'Cleared_Trade_Count',
                                   'Un_Cleared_Trade_Count'])
        return df
    # rellenar NaNs con strings vacios para evitar problemas
    df = df.fillna(" ")
    # filtro df = df[condiciones]
    df = df[
        ((df['Asset_Class'] == "FX") & (df["Tran_Type"] == "USDCLP")) |
        ((df['Asset_Class'] == "IR") &
         (df["Internal_Prod_ID"].str.contains("CLICP")))
    ]

    if not df.empty:
        # Agregar nueva columna con nombres de los productos
        df["Name"] = df.apply(lambda row: tradition_parser_ID(row), axis=1)
        # crear nueva columna con plazo
        df["Tenor"] = df.apply(lambda row: tradition_parser_tenor(row), axis=1)
    else:
        df["Name"] = None
        df["Tenor"] = None

    # ordenar columnas
    cols = df.columns.tolist()
    cols.insert(cols.index("Internal_Prod_Des")+1, cols.pop(-1))
    cols.insert(cols.index("Internal_Prod_Des")+1, cols.pop(-1))
    # ordenar columnas
    df = df[cols]
    # rename Notional_Traded_Currency_NDA
    df = df.rename(columns={'Notional_Traded_Currency_NDA': 'Volume'})
    # rename Total_Trade_Count
    df = df.rename(columns={'Total_Trade_Count': 'Trades'})

    return df


# prebon

def tullett_parser_tenor(row):
    # Expresiones regulares para identificar la fecha
    # NDF USD CLP
    reg1 = re.compile("(\d+D|\d+M)(_NDF_USD_CLP_NDF)")
    reg2 = re.compile("(NDF_USD_CLP_)(\d+D|\d+M)")
    reg2x = re.compile("(USDCLP)(\d\d\d\d\d\d\d\d)([\S]*)")

    # CLP CAMARA
    reg3 = re.compile("(CLP_NDS_[^\s]+_USD_TNA_0X)(\d+)")
    regx = re.compile("(CLP\.)(\d+.)(\.[^\s]+_)(\d\d\d\d\d\d\d\d)")
    # CLF CAMARA
    reg4 = re.compile("(IRS_CLF_[^\s]+_CLP_CAMA_0X)(\d+)")
    # BASIS
    reg5 = re.compile("(IRS_USD_[^\s]+_CLP_CAMA_0X)(\d+)")
    # opciones (\d+.)([^\s]*_USD_CLP_[^\s]+_FXO)
    token = str(row["Tradeable Instrument"])

    # NDF USD CLP
    if reg1.match(token) is not None:
        tenor = reg1.match(token).groups()[0]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor

    if reg2.match(token) is not None:
        tenor = reg2.match(token).groups()[1]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    if reg2x.match(token) is not None:
        tenor = reg2x.match(token).groups()[1]
        X = pd.to_datetime(row["Batch Date"], format="%Y-%m-%d")
        Y = pd.to_datetime(tenor, format="%Y%m%d")
        Z = relativedelta(Y, X)
        tenor = f_date(Z.days, 0, Z.months, Z.years)
        return tenor
    # CLP CAMARA
    if reg3.match(token) is not None:
        tenor = reg3.match(token).groups()[1]
        tenor = f_date(0, 0, tenor, 0)
        return tenor

    if regx.match(token) is not None:
        tenor = regx.match(token).groups()[1]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # CLF CAMARA
    if reg4.match(token) is not None:
        tenor = reg4.match(token).groups()[1]
        tenor = f_date(0, 0, tenor, 0)
        return tenor
    # BASIS
    if reg5.match(token) is not None:
        tenor = reg5.match(token).groups()[1]
        tenor = f_date(0, 0, tenor, 0)
        return tenor
    # warnings.warn('No se pudo leer TENOR de tullett prebon ' +
    #              str(row['Batch Date']))
    return "NONE"


def tullett_parser_ID(row):
    # Expresiones regulares para identificar la fecha
    reg1 = re.compile("(\d+D|\d+M)(_NDF_USD_CLP_NDF)")
    reg2 = re.compile("(NDF_USD_CLP_)(\d+D|\d+M)")
    reg2x = re.compile("(USDCLP)(\d\d\d\d\d\d\d\d)([\S]*)")
    reg3 = re.compile("(CLP_NDS_[^\s]+_USD_TNA_0X)(\d+)")
    regx = re.compile("(CLP\.)(\d+.)(\.[^\s]+_)(\d\d\d\d\d\d\d\d)")
    reg4 = re.compile("(IRS_CLF_[^\s]+_CLP_CAMA_0X)(\d+)")
    reg5 = re.compile("(IRS_USD_[^\s]+_CLP_CAMA_0X)(\d+)")

    token = str(row["Tradeable Instrument"])

    # NDF USD CLP
    if reg1.match(token) is not None:
        return "NDF_USD_CLP"
    if reg2.match(token) is not None:
        return "NDF_USD_CLP"
    if reg2x.match(token) is not None:
        return "NDF_USD_CLP"
    # CLP CAMARA
    if reg3.match(token) is not None:
        return "CLP_CAM"
    if regx.match(token) is not None:
        return "CLP_CAM"
    # CLF CAMARA
    if reg4.match(token) is not None:
        return "CLF_CAM"
    # BASIS
    if reg5.match(token) is not None:
        return "BASIS"
    # warnings.warn('No se pudo leer PRODUCTO de tullett prebon ' +
    #              str(row['Batch Date']))
    return "NONE"


def tullett_parser_broker(row):
    # otros
    reg1 = re.compile("(\d+D|\d+M)(_NDF_USD_CLP_NDF)")
    # xp
    reg2x = re.compile("(USDCLP)(\d\d\d\d\d\d\d\d)([\S]*)")
    # icap
    reg2 = re.compile("(NDF_USD_CLP_)(\d+D|\d+M)")
    # icap
    reg3 = re.compile("(CLP_NDS_[^\s]+_USD_TNA_0X)(\d+)")
    # otros
    regx = re.compile("(CLP\.)(\d+.)(\.[^\s]+_)(\d\d\d\d\d\d\d\d)")
    # icap
    reg4 = re.compile("(IRS_CLF_[^\s]+_CLP_CAMA_0X)(\d+)")
    reg5 = re.compile("(IRS_USD_[^\s]+_CLP_CAMA_0X)(\d+)")

    token = str(row["Tradeable Instrument"])

    # NDF USD CLP
    if reg2.match(token) is not None:
        return "ICAP"
    if reg1.match(token) is not None:
        return "Otros"
    if reg2x.match(token) is not None:
        return "XP"
    # CLP CAMARA
    if reg3.match(token) is not None:
        return "ICAP"
    if regx.match(token) is not None:
        return "Otros"
    # CLF CAMARA
    if reg4.match(token) is not None:
        return "ICAP"
    # BASIS
    if reg5.match(token) is not None:
        return "ICAP"
    # warnings.warn('No se pudo leer BROKER de tullett prebon ' +
    #              str(row['Batch Date']))
    return "NONE"


def tullett_proc(fecha):
    fecha_x = "".join(str(fecha).split("-"))
    token = "assets/TULLETT_PREBON_MKTDATA_{0}.aspx".format(fecha_x)
    try:
        # leer archivo como string
        data = open(token, 'r',).read()
        # parsar como dataframe
        df = pd.read_html(data, header=0)[0]
    except Exception as e:
        print(e)
        # si no existe el archivo crear dataframe vacio
        df = pd.DataFrame(columns=['Batch Date',
                                   'Asset Class',
                                   'Tradeable Instrument',
                                   'Description', 'Name',
                                   'Tenor',
                                   'Broker',
                                   'Opening Price',
                                   'Trade High',
                                   'TradeLow',
                                   'Closing Price',
                                   'Trades',
                                   'Volume']
                          )
        return df

    # rellenar NaNs con strings vacios para evitar problemas
    df = df.fillna(" ")

    # filtro filas df = df[condiciones]
    df = df[df['Tradeable Instrument'].str.contains('CLP')]

    if not df.empty:
        # Agregar nombres
        df["Name"] = df.apply(lambda row: tullett_parser_ID(row), axis=1)
        # crear nueva columna con plazo
        df["Tenor"] = df.apply(lambda row: tullett_parser_tenor(row), axis=1)
        # segregar el resto de ICAP
        df["Broker"] = df.apply(lambda row: tullett_parser_broker(row), axis=1)
    else:
        df["Name"] = None
        df["Tenor"] = None
        df["Broker"] = None
    # ordenar columnas
    cols = df.columns.tolist()
    cols.insert(cols.index("Description")+1, cols.pop(-1))
    cols.insert(cols.index("Description")+1, cols.pop(-1))
    cols.insert(cols.index("Description")+1, cols.pop(-1))
    # ordenar columnas
    df = df[cols]
    # rename Total Notional Value
    df = df.rename(columns={'Total Notional Value': 'Volume'})
    # rename Num of Trades
    df = df.rename(columns={'Num of Trades': 'Trades'})
    return df


def gfi_parser_tenor(row):
    # Expresiones regulares para identificar la fecha
    # NDF USD CLP
    reg1 = re.compile(
        "(USDCLP NDF )(\d\d(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d\d\d\d)( [^\s]+)*")
    reg2 = re.compile(
        "(USDCLP NDF )(\d\d-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-\d\d)(\([^\s]+\) [^\s]+)*")
    # CLP CAMARA
    reg3 = re.compile(
        "(CLP/CAMARA Interest Rate Swap  CLP/CAMARA )((\d+.)( \d+.)?( \d+.)?)")
    # CLF CAMARA
    reg4 = re.compile(
        "(UF/CAMARA Interest Rate Cross Currency  UF/CAMARA )((\d+.)( \d+.)?( \d+.)?)")
    # BASIS
    reg5 = re.compile("(USD CLP Basis Swap )((\d+.)( \d+.)?( \d+.)?)")

    token = row["Contract Description"]

    # NDF
    if reg1.match(token) is not None:
        X = row["Date"]
        Y = pd.to_datetime(reg1.match(token).groups()[1], format="%d%b%Y")
        Z = relativedelta(Y, X)
        tenor = f_date(Z.days, 0, Z.months, Z.years)
        return tenor

    elif reg2.match(token) is not None:
        X = row["Date"]
        Y = pd.to_datetime(reg2.match(token).groups()[1], format="%d-%b-%y")
        Z = relativedelta(Y, X)
        tenor = f_date(Z.days, 0, Z.months, Z.years)
        return tenor
    # CLP CAM
    if reg3.match(token) is not None:
        tenor = reg3.match(token).groups()[1]
        if (reg3.match(token).groups()[2] is not None) and (reg3.match(token).groups()[3] is not None):
            years = reg3.match(token).groups()[2][0:-1]
            months = reg3.match(token).groups()[3][0:-1]
            tenor = f_date(0, 0, months, years)
        else:
            n = tenor[0:-1]
            if tenor[-1] == "D":
                tenor = f_date(n, 0, 0, 0)
            elif tenor[-1] == "W":
                tenor = f_date(0, n, 0, 0)
            elif tenor[-1] == "M":
                tenor = f_date(0, 0, n, 0)
            elif tenor[-1] == "Y":
                tenor = f_date(0, 0, 0, n)
        return tenor
    # CLF CAM
    if reg4.match(token) is not None:
        tenor = reg4.match(token).groups()[1]
        if (reg4.match(token).groups()[2] is not None) and (reg4.match(token).groups()[3] is not None):
            years = reg4.match(token).groups()[2][0:-1]
            months = reg4.match(token).groups()[3][0:-1]
            tenor = f_date(0, 0, months, years)
        else:
            n = tenor[0:-1]
            if tenor[-1] == "D":
                tenor = f_date(n, 0, 0, 0)
            elif tenor[-1] == "W":
                tenor = f_date(0, n, 0, 0)
            elif tenor[-1] == "M":
                tenor = f_date(0, 0, n, 0)
            elif tenor[-1] == "Y":
                tenor = f_date(0, 0, 0, n)
        return tenor
    # BASIS
    if reg5.match(token) is not None:
        tenor = reg5.match(token).groups()[1]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # warnings.warn('No se pudo leer TENOR de GFI ' + str(row['Date']))
    return "NONE"


# gfi

def gfi_parser_ID(row):
    # NDF USD CLP
    if (row['Asset Class'] == 'FX') & (row['Currency'] == 'USD'):
        return "NDF_USD_CLP"
    # CLP CAM
    elif (row['Asset Class'] == 'Interest Rate') & (row['Currency'] == "CLP"):
        return "CLP_CAM"
    # CLF CAM
    elif (row['Asset Class'] == 'Interest Rate') & (row['Currency'] == "CLF"):
        return "CLF_CAM"
    # BASIS
    elif (row['Asset Class'] == 'Interest Rate') & (row['Currency'] == 'USD'):
        return "BASIS"
    # warnings.warn('No se pudo leer PRODUCTO de GFI '+str(row['Date']))
    return "NONE"


# Reading an excel file using Python
def gfi_proc(fecha):
    token = "assets/{0}_daily_trade_data.xls".format(str(fecha))
    try:
        import xlrd
        import os
        # open book
        # EN CASO DE QUE CAMBIE EL HEADER
        # > import os: borrar parámetro logfile para ver errors
        # > import xlrd: buscar por casilla
        wb = xlrd.open_workbook(token, logfile=open(os.devnull, 'w'))
        # sheet = wb.sheet_by_index(0)
        # buscar pivote (donde comienza la tabla)
        # for i in range(10):
        #    for j in range(10):
        #        if (sheet.cell_value(i, j) == "Asset Class"):
        #            pivote = (i,j)
        #            print(pivote)
        #            break
        df = pd.read_excel(wb, sheet_name='SEFTrades', header=4, engine='xlrd')
    except Exception as e:
        print(e)
        df = pd.DataFrame(columns=['Date',
                                   'Asset Class',
                                   'Contract Description',
                                   'Name',
                                   'Tenor',
                                   'Open',
                                   'Low',
                                   'High',
                                   'Close',
                                   'Block',
                                   'Volume',
                                   'Currency',
                                   'Trades']
                          )
        return df

    # rellenar NaNs con strings vacios para evitar problemas
    df = df.fillna(" ")
    # filtro df = df[condiciones]
    df = df[
        ((df['Asset Class'] == 'FX') & (df['Contract Description'].str.match('USDCLP NDF'))) |
        ((df['Asset Class'] == 'Interest Rate') & (df['Contract Description'].str.match('CLP/CAMARA')) & (df['Currency'] == "CLP")) |
        ((df['Asset Class'] == 'Interest Rate') & (df['Contract Description'].str.match('UF/CAMARA')) & (df['Currency'] == "CLF")) |
        ((df['Asset Class'] == 'Interest Rate') &
         (df['Contract Description'].str.match('USD CLP')))
    ]
    if not df.empty:
        # Agregar fecha del día para poder realizar calculos de duración
        df['Date'] = '{0}'.format(str(fecha))
        df['Date'] = pd.to_datetime(df['Date'])
        # Agergar nombre
        df["Name"] = df.apply(lambda row: gfi_parser_ID(row), axis=1)
        # Agregar plazo
        df["Tenor"] = df.apply(lambda row: gfi_parser_tenor(row), axis=1)
    else:
        df["Date"] = None
        df["Name"] = None
        df["Tenor"] = None

    # ordenar columnas
    cols = df.columns.tolist()
    cols.insert(cols.index("Contract Description")+1, cols.pop(-1))
    cols.insert(cols.index("Contract Description")+1, cols.pop(-1))
    cols.insert(cols.index("Asset Class"), cols.pop(-1))
    # ordenar columnas
    df = df[cols]

    df['Trades'] = 1
    # df = df.groupby(['Name','Tenor']).agg({'Trades':'sum','Volume':'sum'}).reset_index()

    return df


def bgc_parser_tenor(row):
    # Expresiones regulares para identificar la fecha
    # NDF USD CLP
    reg1 = re.compile(
        "(USDCLP NDF )(\d\d-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-\d\d)((\([^\s]+\))* .*)")
    # CLP CAM y CLF CAM
    reg2 = re.compile("(\d+.)( .+ CLP-TNA.+)")
    # BASIS
    reg3 = re.compile("(\d+.)( .+ USD-LIBOR.+CLP-TNA.+)")

    token = str(row["Instrument Description"])

    # NDF
    if reg1.match(token) is not None:
        X = row[' Trade Date']
        Y = pd.to_datetime(reg1.match(token).groups()[1], format="%d-%b-%y")
        Z = relativedelta(Y, X)
        tenor = f_date(Z.days, 0, Z.months, Z.years)
        return tenor

    # CLP CAM CLF CAM
    if reg2.match(token) is not None:
        tenor = reg2.match(token).groups()[0]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor

    # BASIS
    if reg3.match(token) is not None:
        tenor = reg3.match(token).groups()[0]
        n = tenor[0:-1]
        if tenor[-1] == "D":
            tenor = f_date(n, 0, 0, 0)
        elif tenor[-1] == "W":
            tenor = f_date(0, n, 0, 0)
        elif tenor[-1] == "M":
            tenor = f_date(0, 0, n, 0)
        elif tenor[-1] == "Y":
            tenor = f_date(0, 0, 0, n)
        return tenor
    # warnings.warn('No se pudo leer TENOR de BGC ' + str(row['Trade Date']))
    return "NONE"


def bgc_parser_ID(row):
    # NDF USD CLP
    if (row['Asset Class'] == 'CU') & (row['CCY'] == 'USD'):
        return "NDF_USD_CLP"
    # CLP CAM
    elif (row['Asset Class'] == 'IR') & (row['CCY'] == "CLP"):
        return "CLP_CAM"
    # CLF CAM
    elif (row['Asset Class'] == 'IR') & (row['CCY'] == "CLF"):
        return "CLF_CAM"
    # BASIS
    elif (row['Asset Class'] == 'IR') & (row['CCY'] == 'USD'):
        return "BASIS"
    # warnings.warn('No se pudo leer PRODUCTO de BGC ' + str(row['Trade Date']))
    return "NONE"

# Reading an excel file using Python


def bgc_proc(fecha):
    fecha_x = "".join(str(fecha).split("-"))
    token = "assets/DailyAct_{0}-001.xls".format(fecha_x)
    try:
        import xlrd
        import os
        # open book
        # EN CASO DE QUE CAMBIE EL HEADER
        # > import os: borrar parámetro logfile para ver errors
        # > import xlrd: buscar por casilla
        wb = xlrd.open_workbook(token, logfile=open(os.devnull, 'w'))
        # sheet = wb.sheet_by_index(0)
        # buscar pivote (donde comienza la tabla)
        # for i in range(10):
        #    for j in range(10):
        #        if (sheet.cell_value(i, j) == " Trade Date"):
        #            pivote = (i,j)
        #            print(pivote)
        #            break

        df = pd.read_excel(wb, sheet_name='Report1', header=6, engine='xlrd')
    except Exception as e:
        print(e)
        # si no existe el archivo retornar dataframe vacio
        df = pd.DataFrame(columns=[' Trade Date',
                                   'Volume',
                                   'Asset Class',
                                   'CCY',
                                   'Instrument Description',
                                   'Name',
                                   'Tenor',
                                   'Open Price',
                                   'Open Type',
                                   'High Price',
                                   'High Type',
                                   'Low Price',
                                   'Low Type',
                                   'Close Price',
                                   'Close Type',
                                   'Block Volume',
                                   'EDRP Vol',
                                   'Trades']
                          )
        return df

    # rellenar NaNs con strings vacios para evitar problemas
    df = df.fillna(" ")
    # filtro df = df[condiciones]
    df = df[
        ((df['Instrument Description'].str.match('USDCLP NDF'))) |
        ((df['Asset Class'] == 'IR') & (df['CCY'] == "CLP")) |
        ((df['Asset Class'] == 'IR') & (df['CCY'] == "CLF")) |
        (
            (df['Asset Class'] == 'IR') &
            (
                (df['Instrument Description'].str.contains('USD-LIBOR')) &
                (df['Instrument Description'].str.contains('CLP-TNA'))
            )
        )
    ]

    # agregar formato
    df[' Trade Date'] = pd.to_datetime(df[' Trade Date'])
    if not df.empty:
        # Agergar nombre
        df["Name"] = df.apply(lambda row: bgc_parser_ID(row), axis=1)
        # Agregar plazo
        df["Tenor"] = df.apply(lambda row: bgc_parser_tenor(row), axis=1)
    else:
        df["Name"] = None
        df["Tenor"] = None

    # ordenar columnas
    cols = df.columns.tolist()
    cols.insert(cols.index("Instrument Description")+1, cols.pop(-1))
    cols.insert(cols.index("Instrument Description")+1, cols.pop(-1))
    cols.insert(cols.index("Asset Class"), cols.pop(-1))
    # ordenar columnas
    df = df[cols]
    # rename Total Volume
    df = df.rename(columns={'Total Volume': 'Volume'})

    df['Trades'] = 1
    # df = df.groupby(['Name','Tenor']).agg({'Trades':'sum','Volume':'sum'}).reset_index()
    return df


# tenors sort

def tenor_sort(df, detalle):
    if not detalle:
        elements = list(zip(df['Tenor'], df['Volume']))
        days = list()
        months = list()
        years = list()
        for tenor, volume in elements:
            if tenor[-1] == 'D':
                days.append((tenor, volume))
            if tenor[-1] == 'M':
                months.append((tenor, volume))
            if tenor[-1] == 'Y':
                years.append((tenor, volume))
        days = sorted(days, key=lambda k: int(k[0][0:-1]))
        months = sorted(months, key=lambda k: int(k[0][0:-1]))
        years = sorted(years, key=lambda k: int(k[0][0:-1]))

        order = pd.DataFrame(days + months + years,
                             columns=['Tenor', 'Volume'])
        return order
    else:
        elements = list(zip(df['Broker'], df['Tenor'],
                            df['Trades'], df['Volume']))
        days = list()
        months = list()
        years = list()
        for broker, tenor, trades, volume in elements:
            if tenor[-1] == 'D':
                days.append((broker, tenor, trades, volume))
            if tenor[-1] == 'M':
                months.append((broker, tenor, trades, volume))
            if tenor[-1] == 'Y':
                years.append((broker, tenor, trades, volume))
        days = sorted(days, key=lambda k: int(k[1][0:-1]))
        months = sorted(months, key=lambda k: int(k[1][0:-1]))
        years = sorted(years, key=lambda k: int(k[1][0:-1]))

        order = pd.DataFrame(days + months + years,
                             columns=['Broker', 'Tenor', 'Trades', 'Volume'])
        return order


def tenor_sort_2(df):
    misc = list()
    days = list()
    months = list()
    years = list()
    cols = list(df.columns.values)
    for index, row in df.iterrows():
        if row['Tenor'][-1] == 'D':
            days.append(row)
        elif row['Tenor'][-1] == 'M':
            months.append(row)
        elif row['Tenor'][-1] == 'Y':
            years.append(row)
        else:
            misc.append(row)
    days = sorted(days, key=lambda k: int(k['Tenor'][0:-1]))
    months = sorted(months, key=lambda k: int(k['Tenor'][0:-1]))
    years = sorted(years, key=lambda k: int(k['Tenor'][0:-1]))

    order = pd.DataFrame(misc+days+months+years, columns=cols)
    return order


def tenor_sort_3(lista):
    misc = list()
    days = list()
    months = list()
    years = list()
    for tenor in lista:
        if tenor[-1] == 'D':
            days.append(tenor)
        elif tenor[-1] == 'M':
            months.append(tenor)
        elif tenor[-1] == 'Y':
            years.append(tenor)
        else:
            misc.append(tenor)
    days = sorted(days, key=lambda k: int(k[0:-1]))
    months = sorted(months, key=lambda k: int(k[0:-1]))
    years = sorted(years, key=lambda k: int(k[0:-1]))

    order = misc+days+months+years
    return order

# resumen

# CLP CAM


def resumen(producto, detalle=True, fecha=None):
    if fecha == None:
        return
    # BILLONES CLP
    if producto == 'CLP_CAM':
        l = 1e9
    # MILES UF
    elif producto == 'CLF_CAM':
        l = 1e3
    # MILLONES USD
    elif producto == 'NDF_USD_CLP':
        l = 1e6
    # MILLONES USD
    elif producto == 'BASIS':
        l = 1e6
    else:
        l = 1
    # display = '<font size="5">{0}</font>'.format(producto)
    # display_html(display, raw=True)

    # LATAM
    latam_resumen = latam_proc(fecha)
    latam_resumen = latam_resumen[latam_resumen['Name'] == producto]
    latam_resumen['Broker'] = 'LatAmSEF'
    latam_resumen = latam_resumen[['Broker', 'Tenor', 'Trades', 'Volume']]

    # TRADITION
    tradition_resumen = tradition_proc(fecha)
    tradition_resumen = tradition_resumen[tradition_resumen['Name'] == producto]
    tradition_resumen['Broker'] = 'TraditionSEF'
    tradition_resumen = tradition_resumen[[
        'Broker', 'Tenor', 'Trades', 'Volume']]

    # TULLETT
    tullett_resumen = tullett_proc(fecha)
    tullett_resumen = tullett_resumen[tullett_resumen['Name'] == producto]
    tullett_resumen = tullett_resumen[['Broker', 'Tenor', 'Trades', 'Volume']]

    # GFI
    gfi_resumen = gfi_proc(fecha)
    gfi_resumen = gfi_resumen[gfi_resumen['Name'] == producto]
    gfi_resumen['Broker'] = 'GFI'
    gfi_resumen = gfi_resumen[['Broker', 'Tenor', 'Trades', 'Volume']]

    # BgC
    bgc_resumen = bgc_proc(fecha)
    bgc_resumen = bgc_resumen[bgc_resumen['Name'] == producto]
    bgc_resumen['Broker'] = 'BGC'
    bgc_resumen = bgc_resumen[['Broker', 'Tenor', 'Trades', 'Volume']]

    resumen = pd.concat([latam_resumen, tradition_resumen,
                         tullett_resumen, gfi_resumen, bgc_resumen], sort=False)

    if not detalle:
        resumen = resumen.groupby(['Tenor']).agg(
            {'Volume': 'sum'}).reset_index()

    # else:
    #    resumen = tenor_sort(resumen, detalle)

    resumen['Volume'] = resumen['Volume'].apply(lambda x: x/l)
    resumen['Date'] = fecha
    # ordenar columnas
    # cols = resumen.columns.tolist()
    # cols.insert(0, cols.pop(-1))
    # ordenar columnas
    # resumen = resumen[cols]
    return resumen


# FUNCIONES PARA OPERAR DATA
# for df.apply
def p_change(row):
    if row['Volume'] >= 1.0:
        return (row['Volume'] - 1) * 100
    elif row['Volume'] == 0.0:
        return row['Volume']
    else:
        return (1-row['Volume']) * -100


def dv01(row, usd, uf, duration, l):
    try:
        dv01 = l*row['Volume']*duration[row['Tenor']]*uf/usd / 10000
    except:
        if row['Tenor'][-1] == 'M':
            d = int(row['Tenor'][0:-1])/12
        else:
            d = int(row['Tenor'][0:-1])
        dv01 = l*row['Volume']*d*uf/usd / 10000
    return dv01


def volume_to_dv01(df, usd, uf, duration, l=1):
    dv_df = df.copy()
    dv_df['Volume'] = dv_df.apply(
        lambda row: dv01(row, usd, uf, duration, l), axis=1)
    return dv_df

# MEAN OF DATAFRAME BY TENOR


def mean_value(df):
    df = df.groupby(['Tenor']).mean().reset_index()
    # df = df.rename(columns = {'Volume':'Mean'})
    return df

# SD OF DATAFRAME BY TENOR


def sd_value(df):
    # para cada fecha en el rango [start_date, start_date + 1 día....]
    df = df.groupby(['Tenor']).std().reset_index()
    df = df.rename(columns={'Volume': 'SD'})
    return df

# MAX OF DATAFRAME BY TENOR


def max_value(df):
    # para cada fecha en el rango [start_date, start_date + 1 día....]
    df = df.groupby(['Tenor']).max().reset_index()
    df = df.rename(columns={'Volume': 'Highest'})
    return df


def percent_diff(df1, df2):
    df = pd.concat([df2, df1], sort=True)
    # reemplazar valores únicos(no en común entre df1 y df2) por cero (diferencia no cuantificable)
    df.loc[df['Tenor'].value_counts()[df['Tenor']].values == 1, 'Volume'] = 0.0
    # dvidir columnas con tenor común
    df = df.groupby(['Tenor']).agg(
        {'Volume': lambda L: reduce(pd.np.dvide, L)}).reset_index()
    # pasar a porcentaje
    df['Volume'] = df.apply(lambda row: p_change(row), axis=1)
    # ordenar cronológicamente
    # renombrar
    df = df.rename(columns={'Volume': 'Pct change'})

    df['Pct change'] = pd.Series([round(val, 1)
                                  for val in df['Pct change']], index=df.index)
    df['Pct change'] = pd.Series(
        ["{0:.1f}%".format(val) for val in df['Pct change']], index=df.index)

    return df


def absolute_diff(df1, df2):
    df1['Volume'] = df1['Volume'] * -1
    df = pd.concat([df2, df1], sort=True)
    # reemplazar valores únicos(no en común entre df1 y df2) por cero (diferencia no cuantificable)
    df.loc[df['Tenor'].value_counts()[df['Tenor']].values == 1, 'Volume'] = 0.0
    # restar columnas con tenor común
    df = df.groupby(['Tenor']).agg({'Volume': 'sum'}).reset_index()
    # ordenar cronológicamente
    # renombrar
    df = df.rename(columns={'Volume': 'Abs change'})
    # devolver  df1 al original
    df1['Volume'] = df1['Volume'] * -1
    return df


def fill_df(df, start_date, end_date):
    # FILL DIAS QUE DEONDE NO SE TRADEA
    business_days = pd.date_range(start=start_date, end=end_date, freq='B')
    cols = list(df.columns.values)
    tenors = df['Tenor'].unique()

    if 'Broker' in cols:
        brokers = df['Broker'].unique()
        for broker in brokers:
            for tenor in tenors:
                days_traded = df[(df['Tenor'] == tenor) & (
                    df['Broker'] == broker)]['Date'].unique()
                fills = set(business_days.date)-set(days_traded)
                if len(fills) != 0:
                    fill = [{**{key: 0 for key in cols}, **{'Broker': broker,
                                                            'Tenor': tenor, 'Date': i}} for i in fills]
                    df_fill = pd.DataFrame(fill, columns=cols)
                    df_fill['Date'] = pd.to_datetime(df_fill['Date'])
                    df = df.append(df_fill, ignore_index=True,
                                   verify_integrity=False)
    else:
        time_fill = timedelta(seconds=0)
        for tenor in tenors:
            days_traded = df[df['Tenor'] == tenor]['Date'].unique()
            fills = set(business_days.date)-set(days_traded)
            if len(fills) != 0:
                fill = [{**{key: 0 for key in cols}, **{'Broker': '',
                                                        'Tenor': tenor, 'Date': i}} for i in fills]
                df_fill = pd.DataFrame(fill, columns=cols)
                df_fill['Date'] = pd.to_datetime(df_fill['Date'])
                df = df.append(df_fill, ignore_index=True,
                               verify_integrity=False)
    return df


def namer(value):
    if value > 1e9:
        return "Promedio: " + "{0:.1f} B".format(value/1e9)
    elif value > 1e3:
        return "Promedio: " + "{0:.0f} K".format(value/1e3)
    else:
        return "Promedio: " + "{0:.0f}".format(value)


def values_product(producto, usd, uf):
    # BILLONES CLP
    if producto == 'CLP_CAM':
        duration = d_clp
        l = 1e9
        uf = 1
    # MILES UF
    elif producto == 'CLF_CAM':
        duration = d_clf
        l = 1e3
    # MILLONES USD
    elif producto == 'NDF_USD_CLP':
        duration = None
        l = 1e6
        uf = 1
    # MILLONES USD
    elif producto == 'BASIS':
        duration = d_usd
        l = 1e6
        uf = 1
        usd = 1
    else:
        l = 1
        uf = 1
    return usd, uf, duration, l


#################B STYLE #################
def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    s = s.apply(lambda x: x.replace(',', ''))
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


def oddness(row):
    if row.name % 2 != 0:
        return ['background-color: #f2f2f2' for i in range(len(row))]
    else:
        return ['background-color: #fafafa' for i in range(len(row))]


# Set CSS properties for th elements in dataframe
th_props = [
    ('font-size', '25px'),
    ('text-align', 'center'),
    ('font-weight', 'bold'),
    ('color', '#6d6d6d'),
    ('background-color', '#f2f2f2')
]

# Set CSS properties for td elements in dataframe
td_props = [
    ('font-size', '20px')
]

# Set table styles
styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props)
]


def ticks_gen(df_max):
    mag = int(np.log10(df_max))
    top = int(round(df_max, -mag))

    _, steps = min([(top % i, i) for i in range(3, 10)], key=lambda x: x[0])

    ticks = [int(top*i/steps) for i in range(steps+1)]

    return ticks, max(df_max+top/(4*steps), top + top/(4*steps))
