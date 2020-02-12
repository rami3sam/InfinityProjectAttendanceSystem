
STUDENTS_PHOTOS_DIR = 'students_photos'
DETECTED_FACES_DIR = 'detected_faces'



ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])



def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
