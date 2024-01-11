import pandas as pd
import folium
from folium import Choropleth
from folium.plugins import HeatMap
from datetime import datetime
import matplotlib.pyplot as plt

class SeismicAnalyzer:
    def __init__(self, seismic_data, region_data):
        self.seismic_data = seismic_data
        self.region_data = region_data
        self.data = None  # Almacenar los datos procesados aquí
        self.alert_threshold = 5.0  # Magnitud a partir de la cual se emiten alertas

    def load_data(self):
        # Implementa la carga de datos desde un archivo o fuente de datos
        # Asegúrate de manejar errores de lectura de archivos y formateo de datos
        # Ejemplo (puedes ajustarlo según el formato real de tus datos):
        self.data = pd.read_csv("https://digital.csic.es/bitstream/10261/284662/3/GEoREST_induced_seismicity_database_v20.11.2022.csv", encoding='ISO-8859-1')

    def visualize_data(self):
        # Implementa la visualización de los datos sísmicos
        plt.plot(self.data['date'], self.data['magnitude'], marker='o')
        plt.xlabel('Fecha')
        plt.ylabel('Magnitud')
        plt.title('Actividad Sísmica a lo largo del tiempo')
        plt.show()

    def plot_seismic_map(self):
        # Implementa un mapa de calor (HeatMap) para visualizar la actividad sísmica en un mapa
        m = folium.Map(location=[self.data['latitude'].mean(), self.data['longitude'].mean()], zoom_start=2)
        heat_data = [[point[1], point[0]] for point in zip(self.data['latitude'], self.data['longitude'], self.data['magnitude'])]
        HeatMap(heat_data).add_to(m)
        m.save("seismic_map.html")

    def analyze_trends(self):
        # Implementa el análisis estadístico para identificar tendencias
        # Utiliza numpy para cálculos estadísticos
        mean_magnitude = self.data['magnitude'].mean()
        std_dev = self.data['magnitude'].std()

        # Visualizar tendencias en un gráfico
        plt.plot(self.data['date'], self.data['magnitude'], marker='o', label='Magnitud')
        plt.axhline(y=mean_magnitude, color='r', linestyle='--', label='Media de Magnitud')
        plt.fill_between(self.data['date'], mean_magnitude - std_dev, mean_magnitude + std_dev, color='gray', alpha=0.2, label='Desviación Estándar')
        plt.xlabel('Fecha')
        plt.ylabel('Magnitud')
        plt.title('Tendencias de Magnitud Sísmica')
        plt.legend()
        plt.show()

    def plot_seismic_risk_map(self):
        # Implementa un mapa de riesgo de actividad sísmica basado en densidad de puntos y variaciones de magnitud
        m = folium.Map(location=[self.data['latitude'].mean(), self.data['longitude'].mean()], zoom_start=2)
        
        # Ajusta el radio del Kernel Density Estimation (KDE) según tus necesidades
        radius = 15
        
        heat_data = self.data[['latitude', 'longitude', 'magnitude']].dropna().values
        m.add_child(HeatMap(heat_data, radius=radius))

        # Agregar capa de riesgo sísmico modelado para diferentes regiones
        for _, region in self.region_data.iterrows():
            Choropleth(
                geo_data=region['geojson'],  # Archivo GeoJSON que describe los límites de la región
                data=None,  # Datos asociados al GeoJSON (pueden incluir métricas de riesgo)
                columns=None,  # Columnas del DataFrame correspondientes a los datos
                key_on='feature.id',
                fill_color='YlOrRd',  # Esquema de colores (puedes ajustar según tus necesidades)
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='Seismic Risk'
            ).add_to(m)

        m.save("seismic_risk_map.html")

    def calculate_probabilities(self, region_name, start_date, end_date):
        # Calcular la probabilidad de una nueva actividad sísmica en una región y período de tiempo específicos
        region_data = self.data[(self.data['latitude'] >= self.region_data.loc[region_name, 'latitude_min']) &
                                (self.data['latitude'] <= self.region_data.loc[region_name, 'latitude_max']) &
                                (self.data['longitude'] >= self.region_data.loc[region_name, 'longitude_min']) &
                                (self.data['longitude'] <= self.region_data.loc[region_name, 'longitude_max']) &
                                (self.data['date'] >= start_date) &
                                (self.data['date'] <= end_date)]

        total_events = len(region_data)
        if total_events == 0:
            return 0  # No hay eventos sísmicos en el período y la región especificados
        else:
            # Calcular la probabilidad como la frecuencia de eventos dividida por la duración del período
            duration_days = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
            probability = total_events / duration_days
            return probability

def main():
    # Crear instancia del analizador sísmico
    seismic_data = pd.read_csv("https://digital.csic.es/bitstream/10261/284662/3/GEoREST_induced_seismicity_database_v20.11.2022.csv", encoding='ISO-8859-1')

    # Datos de la región, incluyendo el GeoJSON que describe los límites de cada región
    region_data = pd.DataFrame({
        'region_name': ['Region A', 'Region B'],  # Nombres de las regiones
        'latitude_min': [0, 10],  # Límites de latitud para cada región
        'latitude_max': [10, 20],
        'longitude_min': [0, 10],  # Límites de longitud para cada región
        'longitude_max': [10, 20],
        'geojson': ['path/to/region_a.geojson', 'path/to/region_b.geojson']  # Rutas a los archivos GeoJSON
    })

    analyzer = SeismicAnalyzer(seismic_data, region_data)

    # Ejecutar funciones de análisis
    analyzer.load_data()
    analyzer.visualize_data()
    analyzer.plot_seismic_map()
    analyzer.analyze_trends()
    analyzer.plot_seismic_risk_map()

    # Calcular la probabilidad de una nueva actividad sísmica en una región y período de tiempo específicos
    region_name = 'Region A'
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    probability = analyzer.calculate_probabilities(region_name, start_date, end_date)
    print(f"La probabilidad de actividad sísmica en {region_name} entre {start_date} y {end_date} es: {probability}")

if __name__ == "__main__":
    main()
