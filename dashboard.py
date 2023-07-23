"""

    An interactive dashboard for the Argentina Previaje program.
    Built using the Dash framework.
    
    Author: Martín Famá 
    © 2023 Martín Famá. All rights reserved.

"""
import pandas as pd
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from data import *

app = dash.Dash(__name__)
app.title = 'Previaje Argentina'
app._favicon = ('arg.ico')

app.layout = html.Div([
    
    html.H1("Argentina Previaje Dashboard", style={'text-align': 'center'}),
    # set title 'Argentina Previaje Dashboard' using a font 
    
    # slider for the date
    # a strange format, but i chose it because:
    # 1. Dash doesn't have a Date Picker where you can reduce the options to only year and month
    # 2. Since we only have 24 months of data, it fits pretty nicely in the screen
    dcc.Slider(0, len(datesvalues)-1,
               step=1,
               id='date_slider',
               marks=datesvalues,
               value=0,),
    
    # make a tickbox that controls whether data will be normalized by population or not
    dcc.Checklist([dict(label='Normalizar por población', value='normalize')],
                  value=[],
                  id='normalize_checkbox',),
    
    # this div containes two graphs:
    # 1. The choroopleth of the number of travelers going _to_ province
    # 2. A scatterplot of the number of travelers going from province _to_ province
    html.Div(id='graphs', children=[
        dcc.Graph(id='choropleth_viajeros', figure={},
                style={'margin': 'auto', 'width': '30%', 'height': '100vh', 'display': 'inline-block'}),
        dcc.Graph(id='cross_province', figure={},
                    style={'margin': 'auto', 'width': '70%', 'height': '100vh', 'display': 'inline-block'})
        ]),

    # insert text which describes the data table below
    html.H3("Beneficiarios del programa", style={'text-align': 'center'}),
    html.P("La siguiente tabla contiene los datos de los viajeros que viajaron (en el rango total del programa). \
            Muestra, para cada provincia, la cantidad de personas que se beneficiaron del programa, \
            separados por género y por rango etario.", style={'text-align': 'center'}),

    dash.dash_table.DataTable(
        id='beneficiaries_table',
        columns=[{"name": i, "id": i} for i in df_beneficiaries.columns],
        data=df_beneficiaries.to_dict('records'),
        style_cell={'textAlign': 'left'},
        style_as_list_view=True)

])

# the app callback modifies both graphs according to the date selected in the slider
@app.callback(
    [Output(component_id='choropleth_viajeros', component_property='figure'),
     Output(component_id='cross_province', component_property='figure')],
    [Input(component_id='date_slider', component_property='value'),
     Input(component_id='normalize_checkbox', component_property='value')])
def update_graph(date, normalize):
    
    # --- data --- #
    cmap = 'Teal'
    # select the data for the date selected in the slider
    dff = df[df['mes_inicio'] == datesvalues[date]]
    if 'normalize' in normalize:
        # normalize by population
        dff = population_normalizer(dff)
        # change colormap to differentiate between absolute and normalized values
        cmap = 'Purp'
    # group by province of destination and sum the number of travelers
    provinces_viajeros_df = dff.groupby('provincia_destino').sum().reset_index()
    # ------------------- #
    
    # --- graphs --- #
    fig_choropleth = px.choropleth(
        data_frame = provinces_viajeros_df, geojson=arg_provinces_geometry,
        locations='provincia_destino', color='viajeros',
        color_continuous_scale=cmap,
        scope='south america')
    fig_choropleth.update_geos(fitbounds="locations")
    
    fig_cross_province = px.scatter(
        data_frame = dff, x='provincia_origen', y='provincia_destino', size='viajeros',
        color='viajeros', color_continuous_scale=cmap,
        labels={'provincia_origen': 'Provincia de origen', 'provincia_destino': 'Provincia de destino'},)
    
    
    return [fig_choropleth, fig_cross_province]
        
if __name__ == '__main__':
    app.run_server(debug=True)
                     