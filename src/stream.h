#ifndef STREAM
#define STREAM

#include "image.h"
void stream(int gpu_id, char *cfgfile, char *weightfile, const char *ip_addr, const int port, char **names, int classes, float hier_thresh, float thresh);

#endif
