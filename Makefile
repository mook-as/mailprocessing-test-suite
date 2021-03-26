test:
	docker run --rm mailprocessing-test-suite

build-image: image
	docker build -t mailprocessing-test-suite -f image/Dockerfile .
