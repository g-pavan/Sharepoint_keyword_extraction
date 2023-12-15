import re

class FileHandler:
    def __init__(self) -> None:
        self.keywords = {}
        self.data = None
    
    def set_data(self, data):
        self.data = data
    
    def flush_data(self):
        self.data = None
    
    def refrine_data(self):
        self.data = re.sub(r'[^\w\s]', ' ', self.data)
        self.data = re.sub(r'\s+', ' ', self.data)
        self.data = self.data.strip().lower()

    def find_matched_keywords(self, keywords):
        if(self.data is None):
            raise Exception('Data is not available')
        
        matched_keywords = set()

        for keyword in keywords:
            keyword = keyword.lower()
            if not keyword.strip():
                continue

            keyword = re.sub(r'[^\w\s]', ' ', keyword)
            keyword = re.sub(r'\s+', ' ', keyword)
            keyword = keyword.strip().lower()

            matches = re.findall(keyword, self.data, re.IGNORECASE)
            matched_keywords.update(matches)
        
        matched_keywords = ', '.join(matched_keywords)

        return matched_keywords