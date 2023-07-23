import pandas as pd
import geojson

# ------------------- Data ------------------- #
# load population data
populations = pd.read_csv('Data/Auxiliary/poblaciones.csv', sep=',')
def population_normalizer(df_):
    for i, province in populations.iterrows():
        name = province['provincia']
        # wherever the province name appears in the 'provincia_destino' column, divide 'viajeros' by the population of that province
        df_.loc[df_['provincia_destino'] == name, 'viajeros'] = df_.loc[df_['provincia_destino'] == name, 'viajeros'] / province['poblacion']
    return df_

# get the geojson file for argentina's provinces. contains the geometry of each province
arg_provinces_geometry = geojson.load(open('Data/Auxiliary/arg_provincias.geojson'))
for i, province in enumerate(arg_provinces_geometry['features']):
    # reduce the number of datapoints in province['geometry']['coordinates'] to 5% of the original
    n_points = len(province['geometry']['coordinates'][0])
    p = int(n_points/max(1, n_points * 0.1))
    arg_provinces_geometry['features'][i]['geometry']['coordinates'] = [province['geometry']['coordinates'][0][::p]]
    # change the id of each province to its name, which will allow us to use the name directly as a location in the choropleth
    arg_provinces_geometry['features'][i]['id'] = province['properties']['name']

# ----------- Interprovincial Travel ----------- #
df = pd.read_csv('Data/viajes_origen_destino_mes.csv', sep=',')
# make a unique int id for each date, to use in the slider
datesvalues = {}
for i, date in enumerate(df['mes_inicio'].unique()):
    datesvalues[i] = date
    
# ---------- Beneficiaries ---------- #
df_beneficiaries = pd.read_csv('Data/personas_beneficiarias.csv', sep=',')
# df_beneficiaries contains the columns provincia,tramo_edad,genero,personas_beneficiarias,edicion
# provincia, tramo_edad, genero, edicion are categorical variables. condense the rows where only edicion is different
# by summing the values of personas_beneficiarias
df_beneficiaries = df_beneficiaries.groupby(['provincia', 'tramo_edad', 'genero']).sum().reset_index()