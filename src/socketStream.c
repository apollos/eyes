/*
 * socketStream.c
 *
 *  Created on: May 19, 2016
 *      Author: yu
 */

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

#include "image.h"
#ifdef OPENCV
#include "opencv2/highgui/highgui_c.h"
#include "opencv2/imgproc/imgproc_c.h"
#define IMAGE_LEN_MESSAGE_LEN 16
#define SOCKET_CLIENT_NUM 2
#define SOCKET_IN_STREAM 0
#define SOCKET_OUT_STREAM 1

IplImage* imgShow;
IplImage* imgSend;
//IplImage *dispTmp;
CvMat* img1;
int       is_data_ready = 0;
int         serversock, clientsock[SOCKET_CLIENT_NUM];
int       server_port;

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

static int  quit(char* msg, int retval);

int prepareSocket(int port)
{
    struct sockaddr_in server, peerAddr;
    const int server_port = port;
    socklen_t peerLen;
    char ipAddr[INET_ADDRSTRLEN];
    //sndImgHead imgHead;
    memset(clientsock, 0, sizeof(clientsock));
    int socketIdx = 0;
    /* create image */
	imgShow = cvCreateImageHeader(cvSize(640, 480), IPL_DEPTH_8U, 3);
	cvCreateData(imgShow);
	cvZero(imgShow);

	imgSend = cvCreateImageHeader(cvSize(640, 480), IPL_DEPTH_8U, 3);
	cvCreateData(imgSend);
	cvZero(imgSend);

	/*dispTmp = cvCreateImageHeader(cvSize(640, 480), IPL_DEPTH_8U, 3);
	cvCreateData(dispTmp);
	cvZero(dispTmp);*/

    /* open socket */
    if ((serversock = socket(PF_INET, SOCK_STREAM, 0)) == -1) {
        return quit("socket() failed", 1);
    }

    /* setup server's IP and port */
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(server_port);
    server.sin_addr.s_addr = INADDR_ANY;

    /* bind the socket */
    if (bind(serversock, (const void*)&server, sizeof(server)) == -1) {
        return quit("bind() failed", 1);
    }

    /* wait for connection */
    if (listen(serversock, 10) == -1) {
        return quit("listen() failed.", 1);
    }
    printf("Listening Port: %d\n", server_port);
    while(socketIdx < SOCKET_CLIENT_NUM){
		/* accept a client */
		if ((clientsock[socketIdx] = accept(serversock, NULL, NULL)) == -1) {
			quit("accept() failed", 1);
		}
		getpeername(clientsock[socketIdx],(struct sockaddr *)&peerAddr,&peerLen);
		printf("Get Connection from %s:%d\n", inet_ntop(AF_INET, &peerAddr.sin_addr, ipAddr, sizeof(ipAddr)), ntohs(peerAddr.sin_port));
		socketIdx++;
    }

    return 0;
}


static int quit(char* msg, int retval)
{
    if (retval == 0) {
        fprintf(stdout, "%s - %d", (msg == NULL ? "" : msg), retval);
        fprintf(stdout, "\n");
    } else {
        fprintf(stderr, "%s - %d", (msg == NULL ? "" : msg), retval);
        fprintf(stderr, "\n");
    }
    int idx = 0;
    while(idx < SOCKET_CLIENT_NUM)
    	if (clientsock[idx]) close(clientsock[idx++]);
    if (serversock) close(serversock);
    if (imgShow) cvReleaseImage(&imgShow);
    if (imgSend) cvReleaseImage(&imgSend);
    //if (dispTmp) cvReleaseImage(&dispTmp);
    cvDestroyWindow("stream_Compress");

	return retval;
}
IplImage* get_Iplimage_from_socket()
{
	/* get head data */
	int i = 0, bytes = 0;
	char sockdata[1024*1024*3];
	CvMat tmpMat;
	for (i = 0; i < IMAGE_LEN_MESSAGE_LEN; i += bytes) {
		if ((bytes = recv(clientsock[SOCKET_IN_STREAM], sockdata + i, IMAGE_LEN_MESSAGE_LEN - i, 0)) <= 0) {
			quit("recv failed", bytes);
		}
	}

	int imageSize = atoi((char *)sockdata);
	//printf("Get image Size %d\n", imageSize);

	/* get raw data */
	for (i = 0; i < imageSize; i += bytes) {
		if ((bytes = recv(clientsock[SOCKET_IN_STREAM], sockdata + i, imageSize - i, 0)) <= 0) {
			quit("recv failed", bytes);
		}
	}

	/* convert the received data to OpenCV's IplImage format, thread safe */
	pthread_mutex_lock(&mutex);

	memcpy(imgShow->imageData, sockdata, imageSize);
	imgShow->imageSize= imageSize;
	CvMat *tmpMatptr = cvGetMat( imgShow, &tmpMat, NULL, 0 );
	imgShow = cvDecodeImage(tmpMatptr, CV_LOAD_IMAGE_COLOR);
	is_data_ready = 1;
	pthread_mutex_unlock(&mutex);
	return imgShow;

}
int send_image_socket(const image src)
{
	int x,y,k, bytes = 0;
	image copy = copy_image(src);
	constrain_image(copy);
	if(src.c == 3) rgbgr_image(copy);
	//normalize_image(copy);


	int step = imgSend->widthStep;
	for(y = 0; y < src.h; ++y){
		for(x = 0; x < src.w; ++x){
			for(k= 0; k < src.c; ++k){
				imgSend->imageData[y*step + x*src.c + k] = (unsigned char)(get_pixel(copy,x,y,k)*255);
			}
		}
	}
	free_image(copy);


	int encode_param[3];
	encode_param[0] = CV_IMWRITE_JPEG_QUALITY;
	encode_param[1] = 70;
	encode_param[2] = 0;
	CvMat* img1 = cvEncodeImage(".jpg", imgSend, encode_param);
/*	IplImage* tmpImg = cvCreateImageHeader(cvGetSize(img1), IPL_DEPTH_8U, 3);
	cvCreateData(tmpImg);
	cvGetImage(img1,tmpImg); CV_8UC1*/
	//printf("type %d, step %d, ref %d, rows %d, cols %d [%x %x %x]\n", CV_MAT_TYPE(img1->type), img1->step, *(img1->refcount), img1->rows, img1->cols, img1->data.ptr[0], img1->data.ptr[img1->step-1], img1->data.ptr[img1->step]);

	char dataLenStr[16];
	memset(dataLenStr, 0, sizeof(dataLenStr));
	if (snprintf(dataLenStr, sizeof(dataLenStr), "%d", img1->step) == -1){
		return quit("int to string transfer failed!", -1);
	}


	bytes = send(clientsock[SOCKET_OUT_STREAM], dataLenStr, sizeof(dataLenStr), 0);
	bytes += send(clientsock[SOCKET_OUT_STREAM], img1->data.ptr, img1->step, 0);
	printf("Send image size %d\n", img1->step);
//	cvReleaseImage(&tmpImg);
	cvReleaseMat(&img1);
    return bytes;
}
#else
int prepareSocket()
{
	fprintf(stderr, "stream demo [prepareSocket] needs OpenCV for webcam images.\n");
	return 1;
}
#endif
