_mp() {
    docker-compose -f .docker-compose.yml run --rm --service-ports mailpile "$@"
}

mp-setup() {
    docker volume rm mailpile_data
    _mp setup
    _mp --www=0.0.0.0:33411
}

mp() {
    echo "http://127.0.0.1:33411"
    _mp "$@"
}
