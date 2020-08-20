# -*- coding: utf-8 -*-
import dash
import dash_table

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server
