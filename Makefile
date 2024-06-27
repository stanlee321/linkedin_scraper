build:
	@echo "Building..."
	docker buildx build --platform linux/amd64 -t ippb/linkend_selenium:latest --load -f ./Dockerfile .

run:
	@echo "Running..."
	docker run -it --rm ippb/linkend_selenium:latest