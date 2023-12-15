import os
import logging
from datetime import datetime

def setup_logging(environment='dev'):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d_%H-%M-%S'

    log_directory = 'logs'
    os.makedirs(log_directory, exist_ok=True)

    timestamp = datetime.now().strftime(date_format)
    file_name = f'{environment}_{timestamp}.log'

    log_file = os.path.join(log_directory, file_name)
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format, datefmt=date_format)

    if environment == 'dev':
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        logging.getLogger().addHandler(console_handler)