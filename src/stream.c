#include "network.h"
#include "detection_layer.h"
#include "region_layer.h"
#include "cost_layer.h"
#include "utils.h"
#include "parser.h"
#include "box.h"
#include "image.h"
#include "stream.h"
#include <sys/time.h>
#include "zmq.h"

#ifdef OPENCV
#include "opencv2/highgui/highgui_c.h"
#include "opencv2/imgproc/imgproc_c.h"
image get_image_from_raw_data(IplImage* src);

static char **demo_names;
static image **demo_alphabet;
static int demo_classes;

static float **probs;
static box *boxes;
static network net;
static image in   ;
static image det  ;
static float demo_thresh = 0;
static float demo_hier_thresh = .5;

image get_Iplimage_from_raw_data(IplImage* imgShow, unsigned char* raw_data, int data_len)
{
	CvMat tmpMat;
	memcpy(imgShow->imageData, raw_data, data_len);
	imgShow->imageSize= data_len;
	CvMat *tmpMatptr = cvGetMat( imgShow, &tmpMat, NULL, 0 );
	imgShow = cvDecodeImage(tmpMatptr, CV_LOAD_IMAGE_COLOR);
	in = get_image_from_raw_data(imgShow);
	return in;
}

image fetch_data_zmq(void *dealer, IplImage* imgShow)
{
	int more = 0;
	unsigned char rcv_buf[1024*768*3];
	int len = 0;
	size_t opt_size = sizeof (len);
	unsigned char* raw_data_pos = NULL;

	do{
		int rc = zmq_recv (dealer, rcv_buf+len, sizeof(rcv_buf) - len,0);//, ZMQ_NOBLOCK);
		assert (rc != -1);
		if (more == 0){ //first come, it is identity
			raw_data_pos = rcv_buf+len+rc;
		}
		len += rc;
		rc = zmq_getsockopt (dealer, ZMQ_RCVMORE, &more, &opt_size);
		assert (rc == 0);

	}while(more);
	return get_Iplimage_from_raw_data(imgShow, raw_data_pos, len - (raw_data_pos - rcv_buf));
}

image detect_data_zmq(image in)
{

    layer l = net.layers[net.n-1];

    if(l.type == DETECTION){
        get_detection_boxes(l, 1, 1, demo_thresh, probs, boxes, 0);
    } else if (l.type == REGION){
        get_region_boxes(l, 1, 1, demo_thresh, probs, boxes, 0, 0, demo_hier_thresh);
    } else {
        error("Last layer must produce detections\n");
    }

    draw_detections(det, l.w*l.h*l.n, demo_thresh, boxes, probs, demo_names, demo_alphabet, demo_classes);

    return det;
}

void stream(int gpu_id, char *cfgfile, char *weightfile, const char *ip_addr, const int port, char **names, int classes, float hier_thresh, float thresh)
{
    //skip = frame_skip;
    image **alphabet = load_alphabet();
    demo_names = names;
    demo_alphabet = alphabet;
    demo_classes = classes;
    demo_thresh = thresh;
    demo_hier_thresh = hier_thresh;
    printf("Stream\n");
    net = parse_network_cfg(cfgfile);
    if(weightfile){
        load_weights(&net, weightfile);
    }
    set_batch_network(&net, 1);

    srand(2222222);

    void *ctx   = zmq_ctx_new();
	void *dealer = zmq_socket(ctx,ZMQ_DEALER);
	char identity [20];
	snprintf (identity, sizeof(identity), "GPU-BROKER-%02d", gpu_id);

	char address [100];
	snprintf (address, sizeof(address), "tcp://%s:%d", ip_addr, port);
	zmq_setsockopt (dealer, ZMQ_IDENTITY, &identity, sizeof(identity));
	int rc = zmq_connect(dealer,address);
	assert(rc == 0);

    layer l = net.layers[net.n-1];
    int j;

    boxes = (box *)calloc(l.w*l.h*l.n, sizeof(box));
    probs = (float **)calloc(l.w*l.h*l.n, sizeof(float *));
    for(j = 0; j < l.w*l.h*l.n; ++j) probs[j] = (float *)calloc(l.classes, sizeof(float));

    int count = 0;
    cvNamedWindow("Stream", CV_WINDOW_NORMAL);
	cvMoveWindow("Stream", 0, 0);
	cvResizeWindow("Stream", 1352, 1013);
	int picH=480;
	int picW=640;
	IplImage* imgShow = cvCreateImageHeader(cvSize(picW, picH), IPL_DEPTH_8U, 3);
	cvCreateData(imgShow);
	cvZero(imgShow);

    while(1){
        ++count;
        if(1){
        	fetch_data_zmq(dealer,imgShow);
        	detect_data_zmq(in);

            show_image(det, "Stream");
            int c = cvWaitKey(1);
            if (c == 'q')
            	break;

            free_image(in);
            free_image(det);
        }
    }
}
#else
void stream(int gpu_id, char *cfgfile, char *weightfile, const char *ip_addr, const int port, char **names, int classes, float hier_thresh, float thresh)
{
    fprintf(stderr, "Demo needs OpenCV for webcam images.\n");
}
#endif

