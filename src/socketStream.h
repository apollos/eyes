#ifndef SOCKETSTREAM_H
#define SOCKETSTREAM_H
int prepareSocket(int port);
IplImage* get_Iplimage_from_socket();
int send_image_socket(const image disp);

typedef struct hndshkMessType
{
    char msg[3];
    int height;
    int width;
    int channel;
}hndshkMess;
#endif

