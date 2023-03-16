#!/bin/bash

#BUILD_REPORT="Yes"
#FLAKY_RERUN="0"
#TEST_MODEL="ALL"
#TAGS="not (beta_v3 or delta_v2)"
#THREADS="4"

if [ -z "${THREADS}" ] || [ "${THREADS}" = "0" ]; then
  NUM=""
else
  NUM="-n=${THREADS}"
fi

if [ -z "${JIRA_PROJECT}" ] || [ -z "${JIRA_USER}" ] || [ -z "${JIRA_PASS}" ]; then
  JIRA="NO"
else
  JIRA="YES"
fi

if [ -z "${BUILD_REPORT}" ] || [ $(echo "${BUILD_REPORT}" | tr '[:upper:]' '[:lower:]') = "yes" ]; then
  ALLURE_PLUGIN="--alluredir=../../test_model/allure-result"
  isAllureNeeded=true
elif [ $(echo "${BUILD_REPORT}" | tr '[:upper:]' '[:lower:]') = "results_only" ]; then
  ALLURE_PLUGIN="--alluredir=../../test_model/allure-result"
  isAllureNeeded=false
else
  ALLURE_PLUGIN=""
  isAllureNeeded=false
fi

echo """
////////////////////////////////////
//////////  run tests!  ////////////
////////////////////////////////////"""
echo """
FEATURES: ${TEST_MODEL}
TAGS: ${TAGS}
PARALLEL: ${THREADS}
BUILD_REPORT: ${isAllureNeeded}
JIRA_ENABLE: ${JIRA}"""
cd yaffat/app
if [ -z "${NUM}" ]; then
  echo "ONLY TEST RUN"
  python -m pytest -m "${TAGS}" ${ALLURE_PLUGIN} tests.py::TestRunner::test_ --no-header --no-summary
else
  echo "TEST RUN WITH PRE-POST ACTIONS"
  python -m pytest ${ALLURE_PLUGIN} tests.py::TestRunner::tests_before_all --no-header --no-summary
  python -m pytest -m "${TAGS}" ${NUM} ${ALLURE_PLUGIN} tests.py::TestRunner::test_ --no-header --no-summary
  python -m pytest ${ALLURE_PLUGIN} tests.py::TestRunner::tests_after_all --no-header --no-summary
fi
cd ../../
if [ ${isAllureNeeded} = true ]; then
  allure-2.13.9/bin/allure generate test_model/allure-result --clean -o test_model/allure-report
  chmod -R 777 test_model/allure-report
fi
chmod -R 777 test_model/allure-result || echo "NO ALLURE RESULTS !"
if [ "${JIRA}" = "YES" ]; then
  cd yaffat/app && python3 test_cycle.py "$JIRA_PROJECT" "$JIRA_USER" "$JIRA_PASS"
fi
echo """
////////////////////////////////////
/////////////  done!  //////////////
////////////////////////////////////
"""
