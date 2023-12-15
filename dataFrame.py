import pandas as pd 
import json
import os
import logging

class CustomDataFrmae:
    def __init__(self):
        self.master_df = pd.DataFrame()
    
    def add_column(self, col_name):
        self.master_df[col_name] = None
    
    def add_row(self, row_data):
        self.master_df = self.master_df._append(row_data, ignore_index=True)
    
    def get_cols(self):
        return list(self.master_df.columns)

    def save_to_csv(self, folder_name, file_name):
        file_name += '.csv'
        logging.info(f'Saving to CSV with {file_name}')

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            logging.info(f'Folder {folder_name} created.')
        
        file_path = os.path.join(folder_name, file_name)
        self.master_df.to_csv(file_path, index=False)

        logging.info(f'DataFrame saved to {file_path}')

    def save_to_json(self, folder_name, file_name):
        file_name += '.json'
        logging.info(f'Saving to JSON with {file_name}')

        df_copy = self.master_df.where(pd.notna(self.master_df), None)

        json_data_str = df_copy.to_json(orient='records', default_handler=str, indent=4)

        json_data = json.loads(json_data_str)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            logging.info(f"Folder {folder_name} created.")
        
        file_path = os.path.join(folder_name, file_name)

        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        
        logging.info(f"DataFrame saved to {file_path}")
        