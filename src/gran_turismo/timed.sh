#!/bin/bash

ulimit -n 3000 # increase to avoid "out of file descriptors" error

/usr/bin/time --format "Memory usage: %MKB\tTime: %e seconds\tCPU usage: %P" "$@"
