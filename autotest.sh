#!/bin/sh

while inotifywait -qq -r -e modify -e create -e move -e delete \
       --exclude '\.sw.?$' tests ggcq
do
	clear
	py.test --cov=ggcq tests
	sleep 1
done
