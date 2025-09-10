#!/bin/bash
  
for i in `awk '{ for(i=1; i<=NF; i++) print $i}' iplist`
do
    grep ${i} /var/named/slaves/* | grep -v "/var/named/slaves/svsv.me"
done

