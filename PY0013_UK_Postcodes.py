import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from shapely.geometry import Point # Shapely for converting latitude/longtitude to geometry
import geopandas as gpd # To create GeodataFrame
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
from sklearn.cluster import AgglomerativeClustering
from sklearn.utils import shuffle
import scipy.cluster.hierarchy as shc
from datetime import date
import os
import logging
import logging.config

class DataCategoriser():
    df_all = pd.DataFrame
    df_postcodes = pd.DataFrame
    data_scaled = None
    cluster = None

    def __init__(self):
        paths = self._create_folders()
        logging.basicConfig(filename='./logs/execution.log',
                            filemode='w',
                            level=logging.INFO,
                            format='%(asctime)s:%(levelname)s:%(message)s')
        logging.info('Constructor checked folder: {}'.format(paths[0]))
        logging.info('Constructor checked folder: {}'.format(paths[1]))

    def _create_folders(self):
        log_path = "./logs/"
        out_path = "./outputs/"
        log_path = self._check_create(log_path)
        out_path = self._check_create(out_path)
        return [log_path, out_path]

    @staticmethod
    def _check_create(folder):
        directory = os.path.dirname(folder)
        try:
            os.stat(directory)
            return 'Existed: {}'.format(directory)
        except:
            os.mkdir(directory)
            return 'Created: {}'.format(directory)

    def load_data(self):
        # Import dataframe with all postcodes of UK and fix index to integers:
        url = 'https://www.doogal.co.uk/files/postcodes.zip'
        self.df_all = pd.read_csv(url, compression='zip', sep=',', usecols = ['Postcode', 'Latitude', 'Longitude','Country'])
        logging.info('Raw data loaded from: {}'.format(url))
        return self._crop_and_shuffle()

    def _crop_and_shuffle(self):
        #### TESTING EDINBURGH SET OF POSCODES ####
        df_edinburgh = self.df_all[self.df_all['Postcode'].str.startswith('EH')]
        df_edinburgh.drop_duplicates(subset=['Latitude', 'Longitude'], keep=False, inplace=True)
        df_edinburgh = shuffle(df_edinburgh)
        self.df_postcodes = df_edinburgh.head(25)
        logging.info('Data has been sliced & shuffled')
        return self.df_postcodes

    def create_geometry(self):
        # creating a geometry column
        geometry = [Point(xy) for xy in zip(self.df_postcodes['Longitude'], self.df_postcodes['Latitude'])]

        # Coordinate reference system : WGS84
        crs = {'init': 'epsg:4326'}

        # Creating a Geographic data frame
        gdf = gpd.GeoDataFrame(self.df_postcodes, crs=crs, geometry=geometry)
        gdf_list = gdf['geometry'].to_list()
        points_array = np.array([[p.x, p.y] for p in gdf_list])
        self.data_scaled = normalize(points_array)
        logging.info('Geometry points generated from Longitude / Latitude coordinates')

    def chart_dendrogram(self):
        # Generate Dendrogram to choose cluster's size:
        plt.figure(figsize=(10, 7))
        plt.title("Dendrograms")
        dend = shc.dendrogram(shc.linkage(self.data_scaled, method='ward'), show_contracted=True, show_leaf_counts=True)
        filename = self._get_filename('_Dendrogram')
        plt.savefig(filename, format="png", dpi=200)
        plt.show()
        logging.info('Dedrogram figure saved to: {}'.format(filename))

    def create_cluster(self):
        # Generate the final cluster:
        self.cluster = AgglomerativeClustering(n_clusters=4, affinity='euclidean', linkage='ward')
        self.cluster.fit_predict(self.data_scaled)
        #cluster.fit(data_scaled)
        plt.figure()
        plt.scatter(self.data_scaled[:, 0], self.data_scaled[:, 1], c=self.cluster.labels_, s=2)
        filename = self._get_filename('_Chart_A')
        plt.savefig(filename, format="png", dpi=200)
        logging.info('Cluster figure saved to: {}'.format(filename))

    def output_cluster(self):
        #Assing cluster categorisations to dataframe:
        self.df_postcodes['cluster'] = self.cluster.labels_
        filename = self._get_filename('postcode_analysis.xlsx')
        with pd.ExcelWriter(filename) as writer:
            self.df_postcodes.to_excel(writer, sheet_name='raw_data')
        logging.info('Outputs saved to: {}'.format(filename))

    def chart_output(self):
        plt.scatter(x=self.df_postcodes['Longitude'], y=self.df_postcodes['Latitude'], c=self.df_postcodes['cluster'], s=2)
        filename = self._get_filename('_Chart_B')
        plt.savefig(filename, format="png", dpi=200)
        logging.info('Dataframe chart geometry saved to: {}'.format(filename))

    def _get_filename(self, iv_addition):
        return str('./outputs/' + str(date.today().strftime('%Y%m%d')) + iv_addition )

def main():
    o_postcodes = DataCategoriser()
    o_postcodes.load_data()
    o_postcodes.create_geometry()
    o_postcodes.chart_dendrogram()
    o_postcodes.create_cluster()
    o_postcodes.output_cluster()
    o_postcodes.chart_output()

if __name__ == '__main__':
    main()