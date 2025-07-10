build:
	docker build -t server-image ./server
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart: down build up
