# Operaciones con fechas
from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import BDay
# Descargar de la web
import urllib.request
from urllib.request import urlopen
# Descomprimir zip
import zipfile

import utils.api

# LatAmSEF


def latam_dl(fecha):
    if fecha == None:
        return
    # parseo de la fecha
    fecha_x = "".join(str(fecha).split("-"))
    #token: añomesdia
    token = "LatAmSEF_MarketActivityData_{0}.csv".format(fecha_x)
    url = "http://latamsef.com/market-data/" + token

    # actual download
    try:
        urllib.request.urlretrieve(url, 'assets/'+token)

        out = "LatAmSEF {0} descargado con éxito".format(str(fecha))
    except:
        try:
            # descargar comprimido y descomprimir
            fecha_x = str(fecha.year) + str(fecha.month).zfill(2)
            token = "LatAmSEF_MarketActivityData_{0}.zip".format(fecha_x)

            url = "http://latamsef.com/market-data/" + token

            urllib.request.urlretrieve(url, 'assets/'+token)

            # descomprimir carpeta principal
            with zipfile.ZipFile('assets/'+token, 'r') as zip_ref:
                zip_ref.extractall()
            out = "LatAmSEF {0} descargado con éxito".format(str(fecha))
        except:
            try:
                # descargar comprimido y descomprimir
                fecha_x = str(fecha.year)
                token = "LatAmSEF_MarketActivityData_{0}.zip".format(fecha_x)
                url = "http://latamsef.com/market-data/" + token

                urllib.request.urlretrieve(url, 'assets/'+token)

                # descomprimir carpeta principal
                with zipfile.ZipFile('assets/'+token, 'r') as zip_ref:
                    zip_ref.extractall()
                # descomprimir cada mes
                rango = ['0'+str(i) for i in range(1, 10)] + ['11', '12']
                for i in rango:
                    token = "LatAmSEF_MarketActivityData_{0}".format(
                        fecha)+i+".zip"
                    with zipfile.ZipFile('assets/'+token, 'r') as zip_ref:
                        zip_ref.extractall()

                out = "LatAmSEF {0} descargado con éxito".format(str(fecha_x))
            except:

                out = "Warning: LatAmSEF {0} no se encuentra disponible".format(
                    str(fecha))
    print(out)

# TraditionSEF


def tradition_dl(fecha):
    if fecha == None:
        return
    # parseo de la fecha
    fecha_x = "".join(str(fecha).split("-"))
    #token: añomesdia
    token = "SEF16_MKTDATA_TFSU_{0}.csv".format(fecha_x)
    url = "http://www.traditionsef.com/dailyactivity/" + token

    # actual download
    try:
        urllib.request.urlretrieve(url, 'assets/'+token)

        out = "TraditionSEF {0} descargado con éxito".format(str(fecha))
    except:
        out = "Warning: TraditionSEF {0} no se encuentra disponible".format(
            str(fecha))
    # print(out)

# tullet prebon


def tullett_dl(fecha):
    if fecha == None:
        return
    fecha_x = "".join(str(fecha).split("-"))
    url = "https://www.tullettprebon.com/swap-execution-facility/daily-activity-summary.aspx"
    # custom token añomesdia
    token = "TULLETT_PREBON_MKTDATA_{0}.aspx".format(fecha_x)

    # actual download
    try:
        urllib.request.urlretrieve(url, 'assets/'+token)

        out = "tullet prebon {0} descargado con éxito".format(str(fecha))
    except:
        out = "Warning: tullett {0} no se pudo descargar".format(str(fecha))
    print(out)

# GFI


def gfi_dl(fecha):
    if fecha == None:
        return
    # parseo de la fecha
    fecha_x = str(fecha)
    #token: año-mes-dia
    token = "{0}_daily_trade_data.xls".format(fecha_x)
    url = "http://www.gfigroup.com/doc/sef/marketdata/" + token

    # actual download
    try:
        urllib.request.urlretrieve(url, 'assets/'+token)

        out = "GFI {0} descargado con éxito".format(str(fecha))

    except:
        out = "Warning: GFI {0} no se encuentra disponible".format(
            str(fecha_x))
    print(out)

# BGC


def bgc_dl(fecha):
    if fecha == None:
        return
    # parseo de la fecha
    fecha_x = "".join(str(fecha).split("-"))
    #token: año-mes-dia
    token = "DailyAct_{0}-001.xls".format(fecha_x)
    url = "http://dailyactprod.bgcsef.com/SEF/DailyAct/" + token

    # actual download
    try:
        urllib.request.urlretrieve(url, 'assets/'+token)

        out = "BGC {0} descargado con éxito".format(str(fecha))

    except:
        out = "Warning: BGC {0} no se encuentra disponible".format(
            str(fecha_x))
    print(out)


def daily_download(bol=True):
    # Descargas del dia anterior
    today = date.today()
    shift = timedelta(max(1, (today.weekday() + 6) % 7 - 3))
    today = today - shift
    if bol:
        # downloads
        latam_dl(today)
        tradition_dl(today)
        tullett_dl(today)
        gfi_dl(today)
        bgc_dl(today)
        print('Descarga terminada')


def daily_upload(bol=True):
    today = date.today()
    shift = timedelta(max(1, (today.weekday() + 6) % 7 - 3))
    today = today - shift
    if bol:
        try:
            api.pd_to_sql(today)
            print('Upload terminado')
        except:
            print('Error inesperado en función pd_to_sql()')
