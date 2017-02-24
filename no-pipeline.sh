#!/bin/bash 
 
# Python exe for virtualenv /usr/bin/python3
PYTHON_EXE=$(which python3)
# export django settings 
export DJANGO_SETTINGS_MODULE=nexchange.settings_test   
NEW_RELIC_CONFIG_FILE=./newrelic.ini 
 
# change it accordinggly 
VIRTUALENV_ROOT="C:/Users/wuelfhis.asuaje/Documents/virtualenvs" 
VIRTUALENV="nexchange" 
 
# Project ROOT 
PROJECT_ROOT=$(pwd) 
 
# HAck to for my windows version 
NPM_EXEC="C:/Users/wuelfhis.asuaje/Documents/Node/npm.bat" 
# Use this to correct installed NPM 
# NPM_EXEC=$(which npm) 
 
# source path for download repos 
SRC_PATH=$VIRTUALENV_ROOT$VIRTUALENV/SRC 
 
main(){ 
  echo "Starting main process" 
  startCreateVirtualEnv 
  installRequirements 
  installNodeRequirements 
  frontEndTest 
 
  # Validate New Relic config file 
  newrelic-admin validate-config ${NEW_RELIC_CONFIG_FILE} 
 
  # Run static validations 
  bash static-validation.sh 
 
  stopVirtualenv 
 
} 
 
# Need a virtualenv 
# and switch to it 
# uses default python version installed 
function startCreateVirtualEnv(){ 
  echo "Setting Up Virtualenv" $VIRTUALENV 
  cd $VIRTUALENV_ROOT 
  virtualenv $VIRTUALENV -p python3
  # TODO  
  # detect windos or *nix   
  source $VIRTUALENV/bin/activate 
} 
 
function stopVirtualenv(){ 
  echo "Stopping Virtualenv" $VIRTUALENV 
  deactivate 
} 
 
 
# Install python requirements         
function installRequirements(){ 
  echo "Installing python requirements"   
 
  # back to project root 
  cd $PROJECT_ROOT 
 
  pip install -r requirements.txt 
   
  has_krakenex=$(python -c "import importlib; k = importlib.find_loader('krakenex'); print(str(k is not None))") 
  if [ "${has_krakenex}" == "False" ]; then 
    git clone https:/github.com/onitsoft/python3-krakenex.git $SRC_PATH/krakenex 
    cd $SRC_PATH/krakenex 
    python3 setup.py install 
    cd - 
  fi 
  python3 -c "import krakenex; print('import krakenex sucessfully executed')" 
 
  has_uphold=$(python -c "import importlib; k = importlib.find_loader('uphold'); print(str(k is not None))") 
  if [ "${has_uphold}" == "False" ]; then 
    git clone https:/github.com/byrnereese/uphold-sdk-python.git $SRC_PATH/uphold 
    cd $SRC_PATH/uphold 
    python3 setup.py install 
    cd - 
  fi 
  python3 -c "import uphold; print('import uphold sucessfully executed')"   
} 
 
function installNodeRequirements(){ 
  echo "Installing node requirements" 
  $NPM_EXEC install   
  $NPM_EXEC run bower  
 
  # Backend tests 
  coverage erase 
  coverage run --source="." manage.py test -v 3 
  coverage report 
  coverage html -d cover   
} 
 
function frontEndTest(){ 
  echo "FrontEnd" 
  # Frontend tests 
  # export PHANTOMJS_BIN=${WERCKER_SOURCE_DIR}/node_modules/.bin/phantomjs 
  # npm run-script test 
} 
 
 
main  
 
