#!/bin/bash
#while true; do cansend kcan4 24B#$(hexdump -n7 -e '7/1 "%02X"' /dev/urandom)11; sleep 0.01; done

while true; do
  random_bytes=$(hexdump -n7 -e '7/1 "%02X"' /dev/urandom)
  fuzzed_frame="${random_bytes}11"
  cansend kcan4 24B#${fuzzed_frame}  
  sleep 0.01
done
