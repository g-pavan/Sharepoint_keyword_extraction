import time
import logging
import pandas as pd 

from config import site_url, folder_name, relative_url, file_names, username, password
from dataFrame import CustomDataFrmae
from file_handler import FileHandler
from log_utils import setup_logging
from sharepointManager import SharePointFileManager


if __name__ == '__main__':
    setup_logging()
    logging.info('Script Initialized')
    # start_time = time.time()

    file_handler = FileHandler()

    keywords_df = pd.read_excel('keywords.xlsx')

    keywords_df = keywords_df[['Product names', 'diseases', 'pests']]
    keywords_df.fillna('', inplace=True)
    keywords_df = keywords_df.astype(str)
    file_handler.keywords['product'] = keywords_df['Product names'].values.tolist()
    file_handler.keywords['diseases'] = keywords_df['diseases'].values.tolist()
    file_handler.keywords['pests'] = keywords_df['pests'].values.tolist()

    fields = ["Title", "Name", "filetype", "Modified", "Project or Product", "Trail Year", "Country", "Indication", "Crop", "Target", "path", "filesize", "product", "disease", "pests", "category_for_one_page"]

    logging.info('Key words Listed')

    metric_df = CustomDataFrmae()
    metric_fileds = ["Site Name", "Folder Count", "Sub Folder Count", "File Count", "Last Run Timestamp"]

    for metric_filed in metric_fileds:
        metric_df.add_column(metric_filed)
    
    for i in range(len(site_url)):
        logging.info(f'Website -- {site_url[i]}')
        start_time = time.time()

        custom_df = CustomDataFrmae()
        logging.info(f'Created DataFrame for {site_url[i]}')

        for field in fields:
            custom_df.add_column(field) 

        sharepoint = SharePointFileManager(site_url[i], relative_url[i], username=username[i], password=password[i])

        sharepoint.set_fields(fields)

        sharepoint.set_master_df(custom_df)
        sharepoint.set_metric_df(metric_df)
        sharepoint.set_file_handler(file_handler)

        logging.info(f'Started Extraction in {folder_name[i]}')

        sharepoint.get_folder_data(folder_name[i])

        custom_df.master_df['category_for_one_page'] = 'Crop and Trail Summaries'
        sharepoint.write_metrics()

        save_folder_name = site_url[i].split("/")[-2]

        custom_df.save_to_csv(save_folder_name, file_names[i])
        custom_df.save_to_json(save_folder_name, file_names[i])

        metric_df.save_to_csv("metrics", "folder_analysis")

        end_time = time.time()

        elapsed_time = end_time - start_time
        elapsed_time_min = elapsed_time / 60

        logging.info("**************************************************************************")
        logging.info(f'Total execution time of {file_names[i]}: {elapsed_time_min:.2f} minutes')        
        logging.info("**************************************************************************")

    logging.info('Script Completed')
