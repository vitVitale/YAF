#!/usr/bin/env bash
set -e

# Available options
declare -a commands=(
  "rollUp"
  "updateDB"
  "insertData"
  "dropAll"
  "clean"
)

# Vars
LOGIN=""
PASSWORD=""


# prepare DB
function rollUp() {
  if [[ "$LOGIN" == "" || "$PASSWORD" == "" ]]; then
    echo "Enter registry login & password:"
    read LOGIN
    read PASSWORD
  else
    echo 'registry credentials were setup in file!'
  fi
  echo """
////////////////////////////////////
/////  prepare to deployment!  /////
////////////////////////////////////
"""
  docker login --username $LOGIN --password $PASSWORD registry.your.space.com
  if [[ $? == 0 ]]; then
    docker network create ST_network || echo Ошибка сеть уже существует
    docker network list
    docker-compose -f docker-compose.db.yml up -d
    sleep 10
    echo """
////////////////////////////////////
//////  deployment complete!  //////
////////////////////////////////////
"""
  else
    echo "AUTHENTICATION FAILED !!!"
  fi
}

# Update Schema
function updateDB() {
  echo """
////////////////////////////////////
//////////  update DB  /////////////
////////////////////////////////////
"""
  cd migrations_tools
    liquibase/liquibase \
    --driver=org.postgresql.Driver \
    --classpath=postgresql-42.2.8.jar \
    --changeLogFile="../changelogs/changelog-master.yml" \
    --url="jdbc:postgresql://127.0.0.1:5432/postgres?currentSchema=data_pipe_cache" \
    --username=postgres \
    --password=admin \
    update
  cd ../
  echo """
////////////////////////////////////
////////  update complete!  ////////
////////////////////////////////////
"""
}

# Insert Data from csv
function insertData() {
  echo """
////////////////////////////////////
//////////  load data!  ////////////
////////////////////////////////////
"""
#  python3 -V
#  python3 -m venv env
#  source ./env/bin/activate
#  pip3 install --no-cache-dir -r requirements.txt
  cd restore_data
  python3 database.py
  cd ../
  echo """
////////////////////////////////////
///////  load data complete!  //////
////////////////////////////////////
"""
}

# Drop Schema
function dropAll() {
  echo """
////////////////////////////////////
////////////  drop DB  /////////////
////////////////////////////////////
"""
  cd migrations_tools
    liquibase/liquibase \
    --driver=org.postgresql.Driver \
    --classpath=postgresql-42.2.8.jar \
    --changeLogFile="../changelogs/changelog-master.yml" \
    --url="jdbc:postgresql://127.0.0.1:5432/postgres?currentSchema=data_pipe_cache" \
    --username=postgres \
    --password=admin \
    dropAll
  cd ../
  echo """
////////////////////////////////////
////////  drop successful!  ////////
////////////////////////////////////
"""
}

# Tear Down & CleanUp
function clean() {
  echo """
////////////////////////////////////
/////  starts clean processes!  ////
////////////////////////////////////
"""
  docker-compose -f docker-compose.db.yml down -v --remove-orphans || echo Ошибка при удалении сервиса
  rm -f ${PWD}/reWorkTest.csv
  echo """
////////////////////////////////////
/////  clean up successful!  ///////
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
${commands[1]}) updateDB ;;
${commands[2]}) insertData ;;
${commands[3]}) dropAll ;;
${commands[4]}) clean ;;
*) echo "Bad command provided! Provide one of: [${commands[*]}]" ;;
esac
