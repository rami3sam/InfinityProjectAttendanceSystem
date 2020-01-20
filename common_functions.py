import PIL
def detectFace(mtcnn,image,filename):
    aligned ,_ = mtcnn(image,return_prob=True,save_path=filename);
    boxes,prob = mtcnn.detect(image)
    if boxes is not None:
         print('Faces detected: ',len(boxes) ,',with probabilities :' ,prob)
    else:
        print("no faces detected")
    return boxes,aligned