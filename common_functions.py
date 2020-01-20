import PIL
import os
import pickle
import re
def detectFace(mtcnn,image,filename):
    aligned ,_ = mtcnn(image,return_prob=True,save_path=filename);
    boxes,prob = mtcnn.detect(image)
    if boxes is not None:
         print('Faces detected: {} with probability: {} '.format(len(boxes) , prob))
    else:
        print("no faces detected")
    return boxes,aligned
all_embeddings = dict()
def loadEmbeddings():
    for (dirpath, dirnames, filenames) in os.walk("students_photos"):
        if re.match(r'^students_photos/\w*$',dirpath):
            embeddingsPath = os.path.join(dirpath ,'embeddings')
            with open(embeddingsPath,'rb') as embeddingsFile:
                student_id = dirpath
                student_embedding = pickle.load(embeddingsFile)
                all_embeddings[student_id] = student_embedding