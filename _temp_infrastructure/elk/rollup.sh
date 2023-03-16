#!/bin/bash
set -e

# Available options
declare -a commands=(
  "up"
  "down"
)

# Vars
LOGIN=""
PASSWORD=""
IMAGE_TAG="1.0.1"
IMAGE_NAME="registry.your.space.com/dev/sidecar:${IMAGE_TAG}"
ELK_PASSWORD="admin_pass"

export ELK_PASSWORD
export IMAGE_NAME

# Settings & Deploy Testing Environment
function rollUp() {
  echo """
////////////////////////////////////
/////  prepare to deployment!  /////
////////////////////////////////////
"""
  docker login --username $LOGIN --password $PASSWORD registry.your.space.com
  if [[ $? == 0 ]]; then
    docker network create ST_network || echo Ошибка сеть уже существует
    docker network list
    docker exec kafka /opt/bitnami/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic SidecarToIr || echo Ошибка создания топика
    docker exec kafka /opt/bitnami/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic IrToSidecar || echo Ошибка создания топика
    docker exec kafka /opt/bitnami/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic DPtoIR || echo Ошибка создания топика
    rm -rf log_dir || echo Логи прошлых запусков отсутсвуют
    docker-compose -f docker-compose.sidecar.yml up -d
    until [[ "${DEPLOY_RESULT}" == *"Kafka consumer started"* ]]; do
        docker logs sidecar &> container_logs
        DEPLOY_RESULT=$(cat container_logs)
        echo "PLEASE STAND BY !!"
        sleep 5
    done
    echo "CONTAINER IS READY !!"
    rm -rf container_logs
    docker network inspect ST_network || echo Ошибка проинспектировать сеть не удалось
    echo """
////////////////////////////////////
//////  deployment complete!  //////
////////////////////////////////////
"""
    echo """
////////////////////////////////////
///////  prepare monitoring!  //////
////////////////////////////////////
"""
    docker-compose -f docker-compose.elk.yml up -d
    until [[ "${LOGSTASH}" == *"Successfully started Logstash"* ]]; do
        docker logs logstash &> logstash_logs
        LOGSTASH=$(cat logstash_logs)
        echo "PLEASE STAND BY !!"
        sleep 5
    done
    echo "LOGSTASH IS WORKING !!"
    rm -rf logstash_logs
    docker rmi elk_filebeat:latest || echo Файлбит собирается впервые
    docker-compose -f docker-compose.filebeat.yml up -d
    echo "WAITING FILEBEAT !!"
    sleep 10
    echo """
////////////////////////////////////
//////  monitoring is ready!  //////
////////////////////////////////////
"""
  else
    echo "AUTHENTICATION FAILED !!!"
  fi
}

# Tear Down & CleanUp
function tearDown() {
  echo """
////////////////////////////////////
/////  tear down environment!  /////
////////////////////////////////////
"""
    docker rm -f filebeat
    docker rmi elk_filebeat:latest
    docker-compose -f docker-compose.elk.yml down -v --remove-orphans || echo Ошибка при удалении сервиса
    docker-compose -f docker-compose.sidecar.yml down -v --remove-orphans || echo Ошибка при удалении сервиса
    rm -rf log_dir || echo Логи отсутсвуют
    docker image list
    docker network inspect ST_network || echo Ошибка инспектирования тест-подсети
    docker network list
    echo """
////////////////////////////////////
/////  tear down successful!  //////
////////////////////////////////////
"""
}

##################################################################################
################################  MAIN SCRIPT   ##################################
##################################################################################

if [[ "$1" == "" ]]; then
  echo "Available commands: [ ${commands[*]} ]"
  echo "Enter :"
  read COMMAND
else
  COMMAND="$1"
fi

case "${COMMAND}" in
${commands[0]}) rollUp ;;
${commands[1]}) tearDown ;;
*) echo "Bad command provided! Provide one of: [${commands[*]}]" ;;
esac
