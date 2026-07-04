#!/bin/bash

# -----------------------------------------------------------------------------
#                           NOTES
# At some point, I need to either clean this script up or rewrite it with a tool
# like `click` in Python or `commander` in Node.js.
# -----------------------------------------------------------------------------

DATABASE_CONTAINER_NAME="pg_database"
# DATABASE_HOST="0.0.0.0"
DATABASE_HOST="pg_database"
DATABASE_NAME="aoam_property_plan"
TEST_DATABASE_NAME="test_aoam_property_plan"
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS
PSQL_CONNECTION="postgresql://postgres:example@pg_database:5432"
LAST_RETURN_STATUS_CODE=$?


getDatabaseContainerID() {
    docker ps -qf name=$DATABASE_CONTAINER_NAME
}

getDatabaseHost() {
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(getDatabaseContainerID)
}


# If you do not want that output, use...
# -- `>/dev/null` to suppress stdout
# -- `2>/dev/null` to suppress stderr
# -- `&>/dev/null` to suppress both

dbIsNotReady() {
    pg_isready -h $DATABASE_HOST > /dev/null 2>&1;
    return $(( $? == 0 ? 1 : 0 ));  # Flip the exit code: return 1 if ready, 0 if not ready
}

isDbReady() {
    # docker compose up -d pg_database 1> /dev/null &
    echo ""
    echo "======================================================================================"
    echo "Starting ready loop..."
    echo "======================================================================================"
    echo ""
    while dbIsNotReady; do
        echo "Is DB ready? $(dbIsNotReady && echo 'FALSE' || echo 'TRUE')"
        echo "Waiting for database to be ready..."
        # TODO: this falls over if there's not container yet
        echo "Container ID: $(getDatabaseContainerID)"
        echo "Database Host: $(getDatabaseHost)"
        sleep 2
    done
}

dbExists() {
    # Q: Is this a common practice for predicate functions in bash? Or is there some other common practice?
    local db_name="${1:-$DATABASE_NAME}"
    psql $PSQL_CONNECTION -l | grep "\b$db_name\b" | wc -l
}

dropDatabase() {
    echo ""
    echo "======================================================================================"
    echo "Dropping $DATABASE_NAME database..."
    echo "======================================================================================"
    echo ""
    docker compose exec pg_database \
        psql $PSQL_CONNECTION \
        -c "DROP DATABASE IF EXISTS $DATABASE_NAME"
}

dropTestDatabase() {
    echo ""
    echo "======================================================================================"
    echo "Dropping $TEST_DATABASE_NAME database..."
    echo "======================================================================================"
    echo ""
    docker compose exec pg_database \
        psql $PSQL_CONNECTION \
        -c "DROP DATABASE IF EXISTS $TEST_DATABASE_NAME"
}

createDatabase() {
    if [[ $* == "-d" ]]; then # drop flag included
        dropDatabase
    fi

    docker compose exec pg_database \
        psql $PSQL_CONNECTION \
        -f "/opt/scripts/db/init_db.sql"

    docker compose run --rm backend-scripts scripts/db/initialize.py
}

createTestDatabase() {
    if [[ $* == "-d" ]]; then # drop flag included
        dropTestDatabase
    fi

    docker compose exec pg_database \
        psql $PSQL_CONNECTION \
        -f "/opt/scripts/db/init_test_db.sql"

    docker compose run \
        -e DATABASE_NAME=$TEST_DATABASE_NAME \
        -e ENV=test \
        --rm backend-scripts scripts/db/initialize.py
}

initDatabase() {
    isDbReady

    # `$(dbExists)` returns number of results so 0 results === DB does not exist/can't be found
    if [[ $* == "-d" || $(dbExists) -ne 0 ]]; then
        echo ""
        echo "======================================================================================"
        echo "Creating $DATABASE_NAME database..."
        echo "======================================================================================"
        echo ""
        createDatabase
    else
        echo ""
        echo "======================================================================================"
        echo "$DATABASE_NAME already exists :]"
        echo "======================================================================================"
        echo ""
    fi
}

initTestDatabase() {
    isDbReady

    if [[ $* == "-d" || $(dbExists $TEST_DATABASE_NAME) -ne 0 ]]; then
        echo ""
        echo "======================================================================================"
        echo "Creating $TEST_DATABASE_NAME database..."
        echo "======================================================================================"
        echo ""
        createTestDatabase
    else
        echo ""
        echo "======================================================================================"
        echo "$TEST_DATABASE_NAME already exists :]"
        echo "======================================================================================"
        echo ""
    fi
}

backendPublishBase() {
    docker buildx build \
        -f backend/Dockerfile.release \
        -t "${DOCKER_USERNAME}/aoam-backend-base:latest" \
        --target backend-release-base \
        --push .
        # --platform linux/amd64,linux/arm64 \
}

backendPublishApp() {
    docker buildx build \
        -f backend/Dockerfile.release \
        -t "${DOCKER_USERNAME}/aoam-backend-app:latest" \
        --target backend-release-app \
        --push .
        # --platform linux/amd64,linux/arm64 \
}

backendPublishMigrations() {
    docker buildx build \
        -f backend/Dockerfile.release \
        -t "${DOCKER_USERNAME}/aoam-backend-migrations:latest" \
        --target backend-release-migrations \
        --push .
        # --platform linux/amd64,linux/arm64 \
}

backendPublishScripts() {
    docker buildx build \
        -f backend/Dockerfile.release \
        -t "${DOCKER_USERNAME}/aoam-backend-scripts:latest" \
        --target backend-release-scripts \
        --push .
        # --platform linux/amd64,linux/arm64 \
}

backendPublishTest() {
    docker buildx build \
        -f backend/Dockerfile.release \
        -t "${DOCKER_USERNAME}/aoam-backend-test:latest" \
        --target backend-release-test \
        --push .
        # --platform linux/amd64,linux/arm64 \
}

frontendPublishBase() {
    docker buildx build \
        -f frontend/Dockerfile.release \
        -t "${DOCKER_USERNAME}/aoam-frontend-base:latest" \
        --target frontend-release-base \
        --push .
        # --platform linux/amd64,linux/arm64 \
}

frontendPublishApp() {
    docker buildx build \
        -f frontend/Dockerfile.release \
        -t "${DOCKER_USERNAME}/aoam-frontend-app:latest" \
        --target frontend-release-app \
        --push .
        # --platform linux/amd64,linux/arm64 \
}

# frontendPublishTest() {
#     docker buildx build \
#         -f frontend/Dockerfile.release \
#         -t "${DOCKER_USERNAME}/aoam-frontend-test:latest" \
#         --target frontend-release-test \
#         --push .
#         # --platform linux/amd64,linux/arm64 \
# }

scriptController() {
    if [ "$1" == "dcr-alembic" ]; then
        # echo "before: $@"
        shift
        # echo "after: $@"
        # docker compose run --build --rm --remove-orphans backend-migrations revision --autogenerate -m
        docker compose run \
            --build \
            --rm \
            --remove-orphans \
            backend-migrations revision --autogenerate -m "$@"
        # TODO: fix this :]
        # while getopts "m" arg; do
        #     echo "m arg: ${arg}"
        #     case ${arg} in
        #         m)
        #             echo "m: ${OPTARG}"
        #             docker compose run --rm backend-migrations revision --autogenerate -m "'${OPTARG}'"
        #             exit 0
        #             ;;
        #     esac
        # done
    elif [ "$1" == "db" ]; then
        echo ""
        echo "======================================================================================"
        echo "db case"
        echo "======================================================================================"
        echo ""
        if [ "$2" == "drop" ]; then
            dropDatabase
        elif [ "$2" == "drop-test" ]; then
            dropTestDatabase
        # elif [ "$2" == "sandbox" ]; then
        #     docker compose run --rm backend-scripts scripts/db/sandbox.py
        # elif [ "$2" == "stash" ]; then
        #     docker compose run --rm backend-scripts scripts/db/stash_db.py
        # elif [ "$2" == "pop" ]; then
        #     docker compose run --rm backend-scripts scripts/db/pop_db.py
        elif [ "$2" == "up-head" ]; then
            docker compose run --rm backend-migrations upgrade head
        elif [ "$2" == "down-1" ]; then
            docker compose run --rm backend-migrations downgrade -1
        elif [ "$2" == "init" ]; then
            echo ""
            echo "======================================================================================"
            echo "Initializing $DATABASE_NAME database..."
            echo "======================================================================================"
            echo ""
            initDatabase
        elif [ "$2" == "create" ]; then
            echo ""
            echo "======================================================================================"
            echo "Creating $DATABASE_NAME database..."
            echo "======================================================================================"
            echo ""
            createDatabase
        elif [ "$2" == "init-test" ]; then
            echo ""
            echo "======================================================================================"
            echo "Initializing test_$DATABASE_NAME database..."
            echo "======================================================================================"
            echo ""
            initTestDatabase
        elif [ "$2" == "create-test" ]; then
            echo ""
            echo "======================================================================================"
            echo "Creating test_$DATABASE_NAME database..."
            echo "======================================================================================"
            echo ""
            createTestDatabase
        elif [ "$2" == "seed" ]; then
            if [ "$3" == "stocks" ]; then
                echo ""
                echo "======================================================================================"
                echo "Seeding stocks data..."
                echo "======================================================================================"
                echo ""
                seedStocks
            else
                echo ""
                echo "======================================================================================"
                echo "Seeding database..."
                echo "======================================================================================"
                echo ""
                seedDatabase
            fi
        elif [ "$2" == "testing" ]; then
            echo ""
            echo "======================================================================================"
            echo "testing..."
            echo "======================================================================================"
            echo ""
            if [[ $(dbExists) -ne 0 ]]; then
                echo "dbExists? FALSE"
            else
                echo "dbExists? TRUE"
            fi
        fi
    elif [ "$1" == "test" ]; then
        if [ "$2" == "backend" ]; then
            echo ""
            echo "======================================================================================"
            echo "Running backend tests! :D"
            echo "======================================================================================"
            echo ""
            docker compose run --rm --remove-orphans backend-test  # "'${@:3}'"
        fi
    elif [ "$1" == "clean" ]; then
        echo ""
        echo "======================================================================================"
        echo "clean case"
        echo "======================================================================================"
        echo ""
        if [ "$2" == "docker" ]; then
            cleanDocker
        fi
    elif [ "$1" == "docker" ]; then
        echo ""
        echo "======================================================================================"
        echo "docker case"
        echo "======================================================================================"
        echo ""
        if [ "$2" == "publish" ]; then
            printf '%s\n' "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

            if [ "$3" == "app" ]; then
                backendPublishBase
                backendPublishApp
                backendPublishScripts
                frontendPublishBase
                frontendPublishApp

            elif [ "$3" == "backend" ]; then
                if [ "$4" == "all" ]; then
                    backendPublishBase
                    backendPublishApp
                    backendPublishMigrations
                    backendPublishScripts
                    backendPublishTest
                elif [ "$4" == "base" ]; then
                    backendPublishBase
                elif [ "$4" == "app" ]; then
                    backendPublishApp
                elif [ "$4" == "migrations" ]; then
                    backendPublishMigrations
                elif [ "$4" == "scripts" ]; then
                    backendPublishScripts
                elif [ "$4" == "test" ]; then
                    backendPublishTest
                fi
            elif [ "$3" == "frontend" ]; then
              if [ "$4" == "all" ]; then
                frontendPublishBase
                frontendPublishApp
                # frontendPublishTest
              elif [ "$4" == "base" ]; then
                frontendPublishBase
              elif [ "$4" == "app" ]; then
                frontendPublishApp
              # elif [ "$4" == "test" ]; then
              #   frontendPublishTest
              fi
            elif [ "$3" == "pg" ]; then
                docker buildx build \
                    -f postgres/Dockerfile \
                    -t "${DOCKER_USERNAME}/aoam-postgres:latest" \
                    --push postgres
            fi
        fi
    elif [ "$1" == "reset-backend" ]; then
        docker compose down && \
        docker compose build pg_database backend --no-cache && \
        docker compose up -d pg_database backend
    fi
}

scriptController $@
