
import pymongo
from AppClasses import Student
STUDENTS_COL = 'students'
SETTINGS_COL = 'settings'

STUDENTS_PHOTOS_DIR = 'students_photos'
DETECTED_FACES_DIR = 'detected_faces'

MAX_CAM_NO = 8

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class DatabaseClient:
    
    def __init__(self):
        self.mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.appDatabase = self.mongoClient["infinity"]
    def checkForStudentExistence(self,studentID):
        databaseQuery = {'ID':studentID}
        return self.appDatabase[STUDENTS_COL].count_documents(databaseQuery) > 0

    def getStudentByID(self,studentID,decodeEmbeddings):
        databaseQuery = {'ID':studentID}
        return Student(self.appDatabase[STUDENTS_COL].find_one(databaseQuery),decodeEmbeddings)
    
    def setSettings(self,name,value):
        if self.appDatabase[SETTINGS_COL].count({'settingsType':name}) == 0:
            self.appDatabase[SETTINGS_COL].insert_one({'settingsType':name,name:value})
        else:
            self.appDatabase[SETTINGS_COL].update_one({'settingsType':name} , {'$set' : {name:value}})
    def getSettings(self,settingsName,default=''):
        if self.appDatabase[SETTINGS_COL].count({'settingsType':settingsName}) > 0:
            return self.appDatabase[SETTINGS_COL].find_one({'settingsType':settingsName})[settingsName]
        else:
            return default

    def deleteStudentByID(self,studentID):
        self.appDatabase[STUDENTS_COL].delete_many({"ID":studentID})

    def insertStudent(self,studentDict):
        self.appDatabase[STUDENTS_COL].insert_one(studentDict)

    def loadStudents(self):
        studentsBuffer = dict()
        students = self.appDatabase[STUDENTS_COL].find()
        for student in students:
            studentsBuffer[student['ID']] = Student(student,True)
        return studentsBuffer

    def updateEmbeddings(self,studentID,embeddingsList,processedPhotos):
        databaseQuery = {'ID':studentID}
        self.appDatabase[STUDENTS_COL].update_one(databaseQuery , {'$set':{
            'embeddingsList':embeddingsList,
            'processedPhotos':processedPhotos
        }})
        
    def getStudentsList(self,pageNo,studentsInPage):
        return self.appDatabase[STUDENTS_COL].find().skip(pageNo*studentsInPage).limit(studentsInPage)
   
    def getMajors(self):
        return ['Electronic Engineering' , 'Electrical Engineering','Mecahnical Engineering']
    def getCollegeYears(self):
        return ['First Year' ,'Second Year','Third Year','Fourth Year','Fifth Year']

    def getCameraColors(self):
        return ['#FF0000' , '#00FF00','#0000FF','#FFF000','#000FFF','#FF00FF','#F0000F','#0FFFF0']
    

    def saveDocument(self,columnName,documentType,value):
        self.appDatabase[columnName].insert_one({'documentType':documentType,documentType:value})
      
    def loadDocument(self,columnName,documentType,default=None):
        if self.appDatabase[columnName].count({'documentdocumentTypeName':documentType}) > 0:
            return self.appDatabase[columnName].find_one({'documentType':documentType})[documentType]
        else:
            return default