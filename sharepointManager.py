import io
import logging
from datetime import datetime
from tika import parser
from sharepointConnector import SharePointConnection
from office365.sharepoint.files.file import File

class SharePointFileManager():
    def __init__(self, site_url, relative_url, username=None, password=None, client_id=None, client_secret=None):
        self.site_url = site_url
        self.ctx = SharePointConnection(site_url, username, password, client_id, client_secret)
        self.relative_url = relative_url

        self.library_name = None
        self.folder_name = None
        self.folder_ctx = None
        
        self.master_df = None
        self.metric_df = None
        self.file_handler = None
        
        self.support_files = set(['pptx', 'ppt', 'docx', 'csv', 'pptm', 'folder'])
        self.fields = None

        self.skipped_folders = set(['forms', 'sharepoint quick guide', 'publishedlinks', 'published links', 'images'])

        self.folder_count = 0
        self.files_count = 0
        self.sub_folder_count = 0

    def set_master_df(self, customDF):
        self.master_df = customDF
    
    def set_metric_df(self, metric_df):
        self.metric_df = metric_df
    
    def set_file_handler(self, file_handler):
        self.file_handler = file_handler
    
    def set_fields(self, fields):
        self.fields = fields
    
    def set_folder_ctx(self, library_name='', folder_name='', folder_url=None):
        try:
            if folder_url is None:
                self.library_name = library_name
                self.folder_name = self.folder_name
                url = f'/{self.relative_url}/{library_name}/{folder_name}'
                self.folder_ctx = self.ctx.web.get_folder_by_server_relative_url(url)
            else:
                # self.folder_ctx = self.ctx.web.get_folder_by_server_relative_url(folder_url).expand(["Versions", "ListItemAllFields"])
                self.folder_ctx = self.ctx.web.get_folder_by_server_relative_url(folder_url)
        except Exception as e:
            logging.error(f"Error setting folder context: {str(e)}")
    
    def get_files(self):
        try:
            files = self.folder_ctx.files
            self.ctx.load(files)
            self.ctx.execute_query()
            return [file for file in files]
        except Exception as e:
            logging.error(f"Error getting files: {str(e)}")
    
    def get_folders(self):
        try:
            folders = self.folder_ctx.folders
            self.ctx.load(folders)
            self.ctx.execute_query()
            return [folder for folder in folders]
        except Exception as e:
            logging.error(f"Error getting folders: {str(e)}")

    def get_properties(self, item_properties):
        properties = {}

        for prop in item_properties:
            properties[prop] = item_properties.get(prop, None)
        
        return properties

    def get_properties_by_field(self, item_properties, prop_name):
        return item_properties.get(prop_name, None)

    def read_file_data(self, file_type, file_url):
        res = {'product':'',
               'disease':'',
               'pests':''
               }

        if file_type not in self.support_files:
            return res

        response= File.open_binary(self.ctx, file_url)

        bytes_file_obj = io.BytesIO()
        bytes_file_obj.write(response.content)
        bytes_file_obj.seek(0)

        if bytes_file_obj is not None:
            data = parser.from_buffer(bytes_file_obj)

            # key = []

            if data['content'] is not None:
                # s = data['content'].strip().replace('\n', '')
                # words = nltk.word_tokenize(s)
                # words = [w.lower() for w in words]

                # for col in self.file_handler.keywords:
                #     key = []
                #     for k in self.file_handler.keywords[col]:
                #         k = str(k)
                #         if k.lower() in str(s.lower()):
                #             key.append(k)
                #             # logging.info("'{%s}' found in this file."%k)
                    
                #     a = list(set(key))
                #     a = ", ".join(a)
                #     res[col] = a
                self.file_handler.set_data(data['content'])
                self.file_handler.refrine_data()
                
                for col in self.file_handler.keywords:
                    res[col] = self.file_handler.find_matched_keywords(self.file_handler.keywords[col])
                
                # print('**************************')
                # print(res)
                # print('**************************')
        
        return res
    
    def get_extension(self, name):
        if name is None:
            return ""

        return name.split('.')[-1]

    def get_file_data(self, file):
        # file_type = file.properties['Name'].split('.')[-1]
        
        logging.info(f"filename : {file.properties.get('Name', None)}")
        self.files_count += 1
        file_type = self.get_extension(self.get_properties_by_field(file.properties, 'Name'))

        if(file_type == 'aspx'):
            return 
        
        file_url = file.properties['ServerRelativeUrl']

        # file_items = file.listItemAllFields
        # self.ctx.load(file_items)
        # self.ctx.execute_query()

        file_data = {
            'Title' : self.get_properties_by_field(file.properties, 'Title'),
            'Name' : self.get_properties_by_field(file.properties, 'Name'),
            'filetype' : file_type,
            # 'Modified' : self.get_properties_by_field(file_items.properties, 'Modified'),
            # 'Project or Product' : self.get_properties_by_field(file_items.properties, 'Trail_x0020_Year'),
            # 'Trail Year' : self.get_properties_by_field(file_items.properties, 'Trail_x0020_Year'),
            # 'Country' : self.get_properties_by_field(file_items.properties, 'Country'),
            # 'Indication' : self.get_properties_by_field(file_items.properties, 'Indication'),
            # 'Crop' : self.get_properties_by_field(file_items.properties, 'Crop'),
            # 'Target' : self.get_properties_by_field(file_items.properties, 'Target'),
            'filesize' : self.get_properties_by_field(file.properties, 'Length')
        }

        if file.properties['LinkingUri'] is not None:
            file_data['path'] = file.properties['LinkingUri']
        else:
            file_data['path'] = "https://wallero.sharepoint.com" + file_url
        
        keywords_dict = self.read_file_data(file_data['filetype'], file_url)

        for key, value in keywords_dict.items():
            file_data[key] = value
        
        self.master_df.add_row(file_data)
    
    def get_folder_data(self, folder_url):
        self.set_folder_ctx(folder_url=folder_url)
        
        logging.info("==============================================================================")
        logging.info(f"Folder {folder_url}")

        files = self.get_files()

        for file in files:
            self.get_file_data(file)
        
        folders = self.get_folders()

        self.sub_folder_count += len(folders)

        for folder in folders:
            folder_name = self.get_properties_by_field(folder.properties, 'Name')

            if folder_name.lower() in self.skipped_folders:
                continue

            try:
                folder_url = folder.properties['ServerRelativeUrl']
                # folder_items = folder.list_item_all_fields
                # self.ctx.load(folder_items)
                # self.ctx.execute_query()

                folder_data = {
                    'Title' : self.get_properties_by_field(folder.properties, 'Title'),
                    'Name' : folder_name,
                    'filetype' : 'Folder',
                    # 'Modified': self.get_properties_by_field(folder_items.properties, 'Modified'),
                    # 'Project or Product' : self.get_properties_by_field(folder_items.properties, 'Project_x0020_or_x0020_Product'),
                    # 'Trail Year' : self.get_properties_by_field(folder_items.properties, 'Trail_x0020_Year'),
                    # 'Country' : self.get_properties_by_field(folder_items.properties, 'Country'),
                    # 'Indication' : self.get_properties_by_field(folder_items.properties, 'Indication'),
                    # 'Crop' : self.get_properties_by_field(folder_items.properties, 'Crop'),
                    # 'Target' : self.get_properties_by_field(folder_items.properties, 'Target'),
                    # 'Comments' : self.get_properties_by_field(folder_items.properties['Comments']),
                    'path' : "https://wallero.sharepoint.com" + folder_url
                }

                self.master_df.add_row(folder_data)
                self.get_folder_data(folder_url)
            
            except Exception as e:
                logging.error(f"Error occured while reading folder: {e}")
        
        self.folder_count = len(folders)

        logging.info("==============================================================================")


    def write_metrics(self):
        row_data = {
            "Site Name" : self.site_url,
            "Folder Count" : self.folder_count,
            "Sub Folder Count" : max(self.sub_folder_count-self.folder_count, 0),
            "File Count" : self.files_count,
            "Last Run Timestamp" : datetime.now()
        }

        self.metric_df.add_row(row_data)