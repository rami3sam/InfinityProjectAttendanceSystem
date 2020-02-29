from AppClasses import Student
import os
import DatabaseClient
import shutil
collegeYear = "Fifth Year"
admissionYear = "2014"
studentMajor = "Electronic Engineering"
studentID = 10000
directoryPath = '/home/rami3sam/Database pics'
if __name__ == '__main__':
    databaseClient = DatabaseClient.DatabaseClient()
    for (dirpath, dirnames, filenames) in os.walk(directoryPath):
        for directory in dirnames:
            lastImageIndex = 0
            for (_,_,pictureNames) in os.walk(os.path.join(dirpath,directory)):
                pictureIndex  = 0 
                for pictureName in pictureNames:
                    
                    if DatabaseClient.allowed_file((pictureName)):
                        imageFilepathSrc = os.path.join(directoryPath,directory,pictureName)
                        studentFolder = os.path.join(DatabaseClient.STUDENTS_PHOTOS_DIR,str(studentID))
                        imageFilepathDest = os.path.join(DatabaseClient.STUDENTS_PHOTOS_DIR,str(studentID),f'{lastImageIndex:04d}.jpg')
                        os.makedirs(studentFolder,exist_ok=True)
                        shutil.copyfile(imageFilepathSrc,imageFilepathDest)
                        lastImageIndex+=1
                break

            student = Student()

            student.ID = studentID
            student.name = directory
            student.major = studentMajor
            student.collegeYear = collegeYear
            student.admissionYear = admissionYear
            student.lastImageIndex = lastImageIndex

            studentDict = student.getStudentAsDict()
            databaseClient.insertStudent(studentDict)
            studentID+=1
        print('added the following students:')
        print(','.join(dirnames))
        break