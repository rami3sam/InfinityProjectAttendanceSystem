
class Student:
    def __init__(self,name):
        self.name = name   
        self.embeddingsList = []
        self.processedPhotos = []

class Embeddings:
    def __init__(self,filename='',embeddings=None):
        self.filename=filename
        self.embeddings=embeddings

