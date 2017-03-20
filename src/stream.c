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

#define FRAMES 3

#ifdef OPENCV
#include "opencv2/highgui/highgui_c.h"
#include "opencv2/imgproc/imgproc_c.h"
image get_image_from_stream(CvCapture *cap);

static char **demo_names;
static image **demo_alphabet;
static int demo_classes;

static float **probs;
static box *boxes;
static network net;
static image in   ;
static image in_s ;
static image det  ;
static image det_s;
static image disp = {0};
static CvCapture * cap;
static float demo_thresh = 0;
static float demo_hier_thresh = .5;

static float *predictions[FRAMES];
static int demo_index = 0;
static image images[FRAMES];
static float *avg;

void *fetch_data_zmq(void *dealer)
{
	zmq_msg_t message;
	zmq_msg_init (&message);
	zmq_msg_recv (&message, dealer,0);//, ZMQ_NOBLOCK);

	//  Process the message frame

	int size = zmq_msg_size(&message);
	char *string = malloc(size + 1);
	memcpy(string, zmq_msg_data(&message), size);
	int nextFrame = 0;
	zmq_msg_close (&message);
	printf("Raw data len %d ", size);
	string[size] = 0;


	/*image im = ipl_to_image(src);
	rgbgr_image(im);

    in_s = resize_image(im, net.w, net.h);*/
    return 0;
}

void *detect_data_zmq(void *ptr)
{
    float nms = .4;

    layer l = net.layers[net.n-1];
    float *X = det_s.data;
    float *prediction = network_predict(net, X);

    memcpy(predictions[demo_index], prediction, l.outputs*sizeof(float));
    mean_arrays(predictions, FRAMES, l.outputs, avg);
    l.output = avg;

    free_image(det_s);
    if(l.type == DETECTION){
        get_detection_boxes(l, 1, 1, demo_thresh, probs, boxes, 0);
    } else if (l.type == REGION){
        get_region_boxes(l, 1, 1, demo_thresh, probs, boxes, 0, 0, demo_hier_thresh);
    } else {
        error("Last layer must produce detections\n");
    }
    if (nms > 0) do_nms(boxes, probs, l.w*l.h*l.n, l.classes, nms);
    printf("\033[2J");
    printf("\033[1;1H");
    printf("Objects:\n\n");

    images[demo_index] = det;
    det = images[(demo_index + FRAMES/2 + 1)%FRAMES];
    demo_index = (demo_index + 1)%FRAMES;

    draw_detections(det, l.w*l.h*l.n, demo_thresh, boxes, probs, demo_names, demo_alphabet, demo_classes);

    return 0;
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

    avg = (float *) calloc(l.outputs, sizeof(float));
    for(j = 0; j < FRAMES; ++j) predictions[j] = (float *) calloc(l.outputs, sizeof(float));
    for(j = 0; j < FRAMES; ++j) images[j] = make_image(1,1,3);

    boxes = (box *)calloc(l.w*l.h*l.n, sizeof(box));
    probs = (float **)calloc(l.w*l.h*l.n, sizeof(float *));
    for(j = 0; j < l.w*l.h*l.n; ++j) probs[j] = (float *)calloc(l.classes, sizeof(float));

    det = in;
    det_s = in_s;


    disp = det;

    int count = 0;
    cvNamedWindow("Stream", CV_WINDOW_NORMAL);
	cvMoveWindow("Stream", 0, 0);
	cvResizeWindow("Stream", 1352, 1013);

    while(1){
        ++count;
        if(1){
        	fetch_data_zmq(dealer);
        	//detect_in_thread(0);

            //show_image(disp, "Stream");
            //int c = cvWaitKey(1);
            //if (c == 'q')
            //	break;

            //free_image(disp);
            disp  = det;

            det   = in;
            det_s = in_s;
        }
    }
    //zctx_destroy (&ctx);
}
#else
void stream(int gpu_id, char *cfgfile, char *weightfile, const char *ip_addr, const int port, char **names, int classes, float hier_thresh, float thresh)
{
    fprintf(stderr, "Demo needs OpenCV for webcam images.\n");
}
#endif

