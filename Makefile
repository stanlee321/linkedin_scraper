build:
	@echo "Building..."
	docker buildx build --platform linux/amd64 -t stanlee321/linkend_selenium:latest --load -f ./Dockerfile .
	docker buildx build --platform linux/amd64 --no-cache -t stanlee321/linkend_selenium:latest --load -f ./Dockerfile.new . 
tag:
	docker tag ippb/linkend_selenium stanlee321/linkend_selenium:latest
push:
	docker push stanlee321/linkend_selenium:latest
run:
	@echo "Running..."
	docker run -it --rm stanlee321/linkend_selenium:latest