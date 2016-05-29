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
#ifdef OPENCV
#include "opencv2/highgui/highgui_c.h"
#include "opencv2/imgproc/imgproc_c.h"
#define IMAGE_LEN_MESSAGE_LEN 16


IplImage* imgShow;
CvMat* img1;
int       is_data_ready = 0;
int         serversock, clientsock;
int       server_port;
#define IMAGE_LEN_MESSAGE_LEN 16

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

static int  quit(char* msg, int retval);

int prepareSocket()
{
    struct sockaddr_in server, peerAddr;
    const int server_port = 9119;
    socklen_t peerLen;
    char ipAddr[INET_ADDRSTRLEN];
    //sndImgHead imgHead;

    /* create image */
	imgShow = cvCreateImageHeader(cvSize(640, 480), IPL_DEPTH_8U, 3);
	cvCreateData(imgShow);
	cvZero(imgShow);

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
    /* accept a client */
    if ((clientsock = accept(serversock, NULL, NULL)) == -1) {
        quit("accept() failed", 1);
    }
    getpeername(clientsock,(struct sockaddr *)&peerAddr,&peerLen);
    printf("Get Connection from %s:%d\n", inet_ntop(AF_INET, &peerAddr.sin_addr, ipAddr, sizeof(ipAddr)), ntohs(peerAddr.sin_port));
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

    if (clientsock) close(clientsock);
    if (serversock) close(serversock);
    if (imgShow) cvReleaseImage(&imgShow);
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
		if ((bytes = recv(clientsock, sockdata + i, IMAGE_LEN_MESSAGE_LEN - i, 0)) <= 0) {
			quit("recv failed", bytes);
		}
	}

	int imageSize = atoi((char *)sockdata);
	//printf("Get image Size %d\n", imageSize);

	/* get raw data */
	for (i = 0; i < imageSize; i += bytes) {
		if ((bytes = recv(clientsock, sockdata + i, imageSize - i, 0)) <= 0) {
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

#else
int prepareSocket()
{
	fprintf(stderr, "stream demo [prepareSocket] needs OpenCV for webcam images.\n");
	return 1;
}
#endif
