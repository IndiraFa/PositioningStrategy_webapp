import numpy as np
import pandas as pd
from pathlib import Path

''' Lecteur '''
# Créer un code permet de ouvrir les csv, 
# donner les métadonnées et les 5 premières lignes 
# class reader -> getinfos, getdata
DATADIR = Path('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit Big Data/dataset')
class Reader:
    def __init__(self, path):
        self.path = path
        self.data = pd.read_csv(self.path)
        self.info = self.getinfos()
    
    def getinfos(self):
        print('---Infos globales---')
        print(self.data.info())
        print('Nombre de lignes:', self.data.shape[0])
        print('Nombre de colonnes:', self.data.shape[1])
        print('5 premiers lignes de données:', self.data.head())
        return 0
 
def main():
    listdatafiles = Path(DATADIR).rglob('*.csv')
    for file in listdatafiles:
        reader = Reader(file)
        reader.getinfos()
        print('---***---')
        print('---***---')

if __name__ == "__main__":
    main()