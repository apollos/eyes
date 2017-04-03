# eyes   
"Eyes" is a deeplearning project. It can support real-time object detection and recognizing. It is written by C, CUDA and Python. The project is a personal learning and practice project and there are many codes refered from the other open source projects so please do not use the project in any commercial product, otherwise, you shall be response for any legal, IP and copyright issue.   
   
#How to Build   
Dependency:   
1. OpenCV 2.x    
2. CUDA 7.5/8.0   
3. CUDNN 5.1
   
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
   a) For Image, eyes detector test  \<your cfg data\> \<your cfg file\>  \<your weight\>  \<test image full path\>   
   b) For Video, eyes detector demo  \<your cfg data\> \<your cfg file\>  \<your weight\>   
   
2. Remote mode   
   a) Start zmq Broker: script/zmq_broker.py
   
   b) Start eyes: eyes detector stream \<your cfg data\> \<your cfg file\>  \<your weight\> 
   
   c) Start zmq video in: script/zmq_video_in.py -t broker_ip -p port -i client_id
                          You can also use -l to specify the video path or remote IP Cam: http://ip:port/video?dummy=param.mjpg    
                          
   d) Start zmq video reciver: script/zmq_video_out.py -t broker_ip -p port -i client_id
     
#Demo weight    
1. For training, you can use the initiated weight for your training http://pan.baidu.com/s/1mhKJ67u        
2. For detection, you can use the trained weight for 20 category demos http://pan.baidu.com/s/1c1btRC     
3. For detection, you can use the trained weight for 80 category demos https://pan.baidu.com/s/1o7VIuYu
