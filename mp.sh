_mp() {
    docker-compose -f .docker-compose.yml run --rm --service-ports mailpile "$@"
}

mp() {
    if [ "$1" = "setup" ]; then
        shift
        docker volume rm mailpile_data
        if [ "$?" != 0 ]; then
            return "$?"
        fi
        _mp setup
        _mp --www=0.0.0.0:33411
    fi

    echo "http://127.0.0.1:33411"
    _mp "$@"
}
