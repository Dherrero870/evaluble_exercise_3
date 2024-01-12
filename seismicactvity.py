#Importamos todas las librerías que vamos a utilizar tanto paralos datos como para visualizar gráficas y mapas
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import numpy as np

# Descargamos los datos desde un enlace de csv previamente buscado que nos da una hoja de excel de donde sacaremos algunos datos
url = "https://digital.csic.es/bitstream/10261/284662/3/GEoREST_induced_seismicity_database_v20.11.2022.csv"
data = pd.read_csv(url, encoding='latin-1')


# Mostrar las primeras filas del conjunto de datos
print(data.head())

# Información general sobre el conjunto de datos
print(data.info())

# Estadísticas descriptivas de las columnas numéricas
print(data.describe())

# Visualizar la distribución de frecuencia de actividades sísmicas según los diferentes paises del mundo
plt.figure(figsize=(10, 6))
plt.hist(data['country'], bins=20, color='skyblue', edgecolor='black')
plt.title('Distribución de Frecuencia Sísmica según diferentes paises')
plt.xlabel('País')
plt.ylabel('Frecuencia')
plt.show()

# Visualizar la relación entre país y profundidad de las actividades sísmicas
plt.figure(figsize=(10, 6))
plt.scatter(data['country'],data['location'], data['seism_depth_max'], alpha=0.5, color='orange')
plt.title('Relación entre País y Profundidad Sísmica')
plt.xlabel('País y Localización')
plt.ylabel('Profundidad (km)')
plt.show()

# Eliminar filas con valores NaN en latitud y longitud (LOs NaN son datos no numéricos que aperecen y hace que se haya errores, por lo que complica la resolución del mapa)
data = data.dropna(subset=['latitude', 'longitude'])

# Crear un GeoDataFrame para trabajar con datos geoespaciales
gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))

while True:
    # Solicitar al usuario que ingrese el nombre del país
    country_name = input("Ingrese el nombre del país para visualizar en el mapa (en inglés): ")

    # Obtener límites del país
    country_boundaries = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    try:
        country_geometry = country_boundaries[country_boundaries['name'].str.lower() == country_name.lower()]['geometry'].iloc[0]
    except IndexError:
        print(f"No se encontraron límites para el país {country_name}. Intente nuevamente.")
        continue

    # Crear un mapa centrado en el país
    mymap = folium.Map(location=[country_geometry.centroid.y, country_geometry.centroid.x], zoom_start=6)

    # Añadir un grupo de marcadores al mapa usando MarkerCluster
    marker_cluster = MarkerCluster().add_to(mymap)

    # Añadir marcadores solo para filas sin NaN en latitud y longitud dentro de los límites del país
    for idx, row in gdf[gdf.geometry.within(country_geometry)].dropna(subset=['latitude', 'longitude']).iterrows():
        folium.Marker([row['latitude'], row['longitude']],
                      popup=f"Profundidad: {row['seism_depth_max']} m").add_to(marker_cluster)

    # Guardar el mapa como un archivo HTML
    mymap.save(f'seismic_map_{country_name}.html')

    # Abrir el mapa en el navegador predeterminado
    import webbrowser
    webbrowser.open(f'seismic_map_{country_name}.html')
    break
