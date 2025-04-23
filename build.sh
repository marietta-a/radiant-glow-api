#!/bin/bash
# Install Python 3.13.3
PYTHON_VERSION=3.13.3
wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
tar -xzf Python-${PYTHON_VERSION}.tgz
cd Python-${PYTHON_VERSION}
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall
cd ..

# Install dependencies
python3.13 -m pip install --upgrade pip
python3.13 -m pip install -r requirements.txt