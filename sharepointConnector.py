from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

class SharePointConnection:
    _instance = None

    def __new__(cls, site_url, username=None, password=None, client_id=None, client_secret=None):
        if cls._instance is None:
            cls._instance = super(SharePointConnection, cls).__new__(cls)
            cls._instance.site_url = site_url
            cls._instance.username = username
            cls._instance.password = password
            cls._instance.client_id = client_id
            cls._instance.client_secret = client_secret
            cls._instance.ctx = cls._instance._connect_to_sharepoint()
        
        return cls._instance.ctx 
    
    def _connect_to_sharepoint(self):
        if self.username and self.password:
            user_credentials = UserCredential(self.username, self.password)
            ctx = ClientContext(self.site_url).with_credentials(user_credentials)
        elif self.client_id and self.client_context:
            client_credentials = ClientCredential(self.client_id, self.client_secret)
            ctx = ClientContext(self.site_url).with_credentials(client_credentials)
        else:
            raise ValueError("Provider either username and password or client ID and secret.")
        
        return ctx