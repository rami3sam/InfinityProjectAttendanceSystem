
import pymongo
from AppClasses import Student
STUDENTS_COL = 'students'
SETTINGS_COL = 'settings'
SHARED_COL = 'shared'
LECTURES_COL = 'lectures'
LECTURE_TAG = 'lecture'
ATTENDANCE_COL = 'attendance'
ATTENDANCE_TAG = 'ATTENDANCE'
STUDENTS_PHOTOS_DIR = 'students_photos'
DETECTED_FACES_DIR = 'detected_faces'
FPS = 24
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
    
    def getTimePeriod(self):
        return 60

    def getPeriodThreshold(self):
        return 10

    def setSettings(self,name,value):
        if self.appDatabase[SETTINGS_COL].count_documents({'settingsType':name}) == 0:
            self.appDatabase[SETTINGS_COL].insert_one({'settingsType':name,name:value})
        else:
            self.appDatabase[SETTINGS_COL].update_one({'settingsType':name} , {'$set' : {name:value}})
    def getSettings(self,settingsName,default=''):
        if self.appDatabase[SETTINGS_COL].count_documents({'settingsType':settingsName}) > 0:
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

    def getDays(self):
        return ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday',"Saturday"]

    def getCameraColors(self):
        return ['#FF0000' , '#00FF00','#0000FF','#FFF000','#000FFF','#FF00FF','#F0000F','#0FFFF0']
    

    def saveDocument(self,columnName,documentType,value):
        self.appDatabase[columnName].insert_one({'documentType':documentType,**value})
    
    def prepareSelectionCriteria(self,selectionCritera,documentType):
        if selectionCritera == None:
            selectionCritera = dict({'documentType' : documentType})
        elif '$and' in selectionCritera:
            selectionCritera['$and'].append({'documentType' : documentType})
        elif '$or' in selectionCritera:
            selectionCritera['$and'] = [selectionCritera, {'documentType' : documentType}]
        return selectionCritera

    def updateDocument(self,columnName,documentType,selectionCritera,updateQuery):
        selectionCritera = self.prepareSelectionCriteria(selectionCritera,documentType)

        if self.appDatabase[columnName].count_documents({'documentType':documentType}):
            self.appDatabase[columnName].update_one({'documentType':documentType,**selectionCritera},updateQuery)
            return True
        else:
            return False

    def deleteDocument(self,columnName,documentType,selectionCritera=None):
        selectionCritera = self.prepareSelectionCriteria(selectionCritera,documentType)

        if self.appDatabase[columnName].count_documents(selectionCritera) > 0:
            self.appDatabase[columnName].delete_one(selectionCritera)
      
    def loadDocument(self,columnName,documentType,selectionCritera=None,default=None):
        selectionCritera = self.prepareSelectionCriteria(selectionCritera,documentType)

        if self.appDatabase[columnName].count_documents(selectionCritera) > 0:
            return self.appDatabase[columnName].find_one(selectionCritera)
        else:
            return default

    def loadDocuments(self,columnName,documentType,selectionCritera=None,default=None):
        selectionCritera = self.prepareSelectionCriteria(selectionCritera,documentType)

        if self.appDatabase[columnName].count_documents(selectionCritera) > 0:
            return self.appDatabase[columnName].find(selectionCritera)
        else:
            return default
    
    def getDistinctValues(self,columnName,documentType,field,selectionCritera=None):
        selectionCritera = self.prepareSelectionCriteria(selectionCritera,documentType)
        return self.appDatabase[columnName].distinct(field,selectionCritera)

    def getNextSequenceNumber(self,sequenceName):
        sequenceDocument = self.appDatabase['counters'].find_one_and_update(filter={'_id':sequenceName},
        update={'$inc': {'sequence_value' : 1}},upsert=True )
        if sequenceDocument is None:
            return 0
        return sequenceDocument['sequence_value']