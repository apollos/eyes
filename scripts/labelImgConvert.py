import os, sys
from os import walk, getcwd
from PIL import Image
import re
import xml.etree.ElementTree as ET

sets=['songyu'] #['stopsign', 'stopsign', 'yieldsign'] 

classes = ["stop sign", "yield sign", "song yu"]


def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)
    
def convert_annotation(targetPath, image_folder, imageFile):
    p = re.compile('\..+$')
    image_id = p.sub("", imageFile)
    inFilePath = '%s/%s/annotations/%s.xml'%(targetPath, image_folder, image_id)
    if not os.path.exists(inFilePath):
        print "label file %s is not existed." % (inFilePath)
        return
    in_file = open(inFilePath)
    out_file = open('%s/%s/labels/%s.txt'%(targetPath, image_folder, image_id), 'w')

    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


if __name__ == "__main__":
    if len(sys.argv) !=2:
        print("Usage: python labelImgConvert.py <data path>")
        exit(-1)

    targetPath = sys.argv[1]
    if not os.path.exists(targetPath) or not os.path.isdir(targetPath):
        print("Path %s is not right!" % targetPath)
        exit(-1)    
    
    for image_folder in sets:
        imgPath = '%s/%s/images' % (targetPath, image_folder)
        labelPath = '%s/%s/labels' % (targetPath, image_folder)

        list_file = open('%s/%s_train.txt'%(targetPath, image_folder), 'w')
        if not os.path.exists(imgPath):
            print ("Path %s is not existed." % (imgPath))
            continue
        if not os.path.exists(labelPath):
            os.makedirs(labelPath)
        cmd = "cd %s && find './' " % (imgPath)
        fileList = os.popen(cmd).read().replace("./", "").split('\n')        
        for imageFile in fileList:
            if imageFile == "":
                continue
            list_file.write('%s/%s\n'%(imgPath, imageFile))
            convert_annotation(targetPath, image_folder, imageFile)
        list_file.close()

    

