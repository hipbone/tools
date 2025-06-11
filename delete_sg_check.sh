#!/bin/bash

paths='
/home/hipbone/src/iep-git/iep-gcp-projects
/home/hipbone/src/iep-git/iep-terraform
'

file="./data"

for path in $paths
do
    for ip in `awk '{for(i=1;i<=NF;i++)print $i}' $file`
    do
        ack $ip $path
    done
done
