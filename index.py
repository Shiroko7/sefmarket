
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from app import server

import callbacks

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/dash':
        from layouts.layout_dash import dash
        return dash
    elif pathname == '/report':
        from layouts.layout_report import report
        return report
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
