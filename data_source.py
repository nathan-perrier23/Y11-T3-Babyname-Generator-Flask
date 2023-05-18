from pathlib import Path
import pandas as pd

class DataSource:
    def __init__(self):
        pass
        
    def retrieve_graph_data(self):
        source_files = sorted(Path("data/years").glob("*.txt"))
        dataframes = []
        for file in source_files:
            df = pd.read_csv(file, header=None, names=["name", "sex", "n"])
            df["year"] = int(file.stem.replace("yob", ""))
            dataframes.append(df) 
        return pd.concat(dataframes)
        
    def get_graph_data(self, name):  
        graph_data = self.retrieve_graph_data()
        graph_data = graph_data.groupby(["name"], as_index=False)
        graph_data = graph_data.get_group(name) 
        graph_data_dict = {}
        for n, year in zip(graph_data['n'], graph_data['year']):
            graph_data_dict[year] = n
        return graph_data_dict
    
    def retrieve_name_data(self, gender, names): 
        return pd.read_csv(('data/'+gender+'.csv'), header=None, names=names, low_memory=False)
    
    def get_name_data(self, name, file_gender, names=['rank','name','alt_spellings','n_sum','n_percent','year_min','year_max','year_pop','biblical','palindrome','phones','first_letter','stresses','syllables','alliteration_first','unisex']):
        name_data_dict = {}
        name_data = self.retrieve_name_data(file_gender, names)
        try: 
            name_data = name_data.groupby(["name"], as_index=False)
            name_data = name_data.get_group(name)
        except:
            name_data = name_data.groupby(["alt_spelling"], as_index=False)
            name_data = name_data.get_group(name)
        graph_name = list(name_data['name'])[0] #? weird
        try: graph_data_dict = self.get_graph_data(graph_name) 
        except: graph_data_dict = None 
        for h_name in names: 
            data = list(name_data[h_name])
            name_data_dict[h_name] = data[0] #issue?
        return name_data_dict, graph_data_dict
    
    def get_data(self, name, gender):
        try:
            try: return self.get_name_data(name.capitalize(), gender)
            except: return self.get_name_data(name.capitalize(), 'boys')
        except Exception as e: print(e)
    