mp() {
    echo "http://127.0.0.1:33411"
    docker-compose -f .docker-compose.yml run --rm --service-ports mailpile
}
