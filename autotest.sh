#!/bin/sh

while inotifywait -qq -r -e modify -e create -e move -e delete \
       --exclude '\.sw.?$' tests ggcq
do
	clear
	py.test --log-format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' --cov=ggcq tests
	sleep 1
done
