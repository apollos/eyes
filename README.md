# eyes   
"Eyes" is a deeplearning project. It can support real-time object detection and recognizing. It is written by C, CUDA and Python. The project is a personal learning and practice project and there are many codes refered from the other open source projects so please do not use the project in any commercial product, otherwise, you shall be response for any legal, IP and copyright issue.   
   
#How to Build   
Dependency:   
1. OpenCV 2.x    
2. CUDA 7.5     
3. CUDNN 7.5   
   
make all -jn       
   
Note: You can also disable OpenCV, CUDNN and CUDA in make file according to your real environemnt.      
   
#How to Train your Data   
1. Label your images by https://github.com/tzutalin/labelImg   
2. Generate the traing image list and conver the image label from xml to txt by script/labelImgConvert.py   
3. Generate your label image file by modify the class and run label/make_labels.py   
4. Add a configuration file in cfg. You can refer the two example one is 20 categories and the other is 3 categories.      
   a) Adjust batch number to increase or reduce the input image number       
   b) Adjust subdivisions number to adjust the piece size of each batch. If your GPU memory is big enough, you can change it to 2 to get the best performance   
   c) If you adjust classes number, you need also adjust the "output" of the last connect layer. output = side*side*(num*5+classes)   
5. Update the src/classDefine.h according to your new class definition      
6. Update the train.txt file local in src/stream.c (train_images, backup_directory)       
7. rebuild and start the training by eyes stream train  \<your cfg file\>  \<your weight file\>       
8. If the training is interrupted, you can continue the training by identify the last stored weight file           
   
#How to Run detection   
1. Local mode      
   a) For Image, eyes stream test  \<your cfg file\>  \<your weight\>  \<test image full path\>   
   b) For Video, eyes stream demo  \<your cfg file\>  \<your weight\>   
   
2. Remote mode   
   a) For Video:     
      start server part by eyes stream demo  \<your cfg file\>  \<your weight\>  SOCKET:\<PORT\>     
      start client detection result window by python scripts/testStreamClient.py  \<server IP\>  \<server port\>     
      start client capture window by python scripts/testRemoteCam.py \<server IP>  \<server port\> [video to be play]      
      Without the [video to be play], the capture part will open local camera as input source      
     
#Demo weight    
1. For training, you can use the initiated weight for your training http://pan.baidu.com/s/1mhKJ67u        
2. For detection, you can use the trained weight for 20 category demos http://pan.baidu.com/s/1c1btRC       
