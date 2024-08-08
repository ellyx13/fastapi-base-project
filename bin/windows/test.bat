docker compose -f docker-compose-test.yml build
docker compose -f docker-compose-test.yml up --abort-on-container-exit
docker compose -f docker-compose-test.yml down -v
