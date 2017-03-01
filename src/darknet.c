#include <time.h>
#include <stdlib.h>
#include <stdio.h>

#include "parser.h"
#include "utils.h"
#include "cuda.h"
#include "blas.h"
#include "connected_layer.h"

#ifdef OPENCV
#include "opencv2/highgui/highgui_c.h"
#endif

extern void run_detector(int argc, char **argv);

int main(int argc, char **argv)
{
    if(argc < 2){
        fprintf(stderr, "usage: %s <function>\n", argv[0]);
        return 0;
    }
    gpu_index = find_int_arg(argc, argv, "-i", 0);
    if(find_arg(argc, argv, "-nogpu")) {
        gpu_index = -1;
    }

#ifndef GPU
    gpu_index = -1;
#else
    if(gpu_index >= 0){
        cuda_set_device(gpu_index);
    }
#endif

    if (0 == strcmp(argv[1], "detector")){
        run_detector(argc, argv);
    } else {
        fprintf(stderr, "Not an option: %s\n", argv[1]);
    }
    return 0;
}

