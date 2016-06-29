# eyes
"Eyes" is a deeplearning project. It can support real-time object detection and recognizing. It is written by C, CUDA and Python

Example:
./eyes stream test cfg/eyes.cfg  ../Data/weights/eyes.weights ../Data/pic/test/ll.jpg
./eyes stream demo cfg/eyes.cfg  ../Data/weights/eyes.weights
./eyes stream demo cfg/eyes.cfg  ../Data/weights/eyes.weights ../Data/video/abc.mov
./eyes stream demo cfg/eyes.cfg  ../Data/weights/eyes.weights SOCKET:PORT

python scripts/testRemoteCam.py eyesServerIP PORT data/723524_535269319829012_2051799405_n.mp4 10