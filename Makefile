test:
	docker run --rm $${SRC:+-v $${SRC}:/src:ro} mailprocessing-test-suite

build-image: image
	docker build -t mailprocessing-test-suite -f image/Dockerfile .
