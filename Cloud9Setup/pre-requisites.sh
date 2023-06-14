#!/bin/bash -x
. /home/ec2-user/.nvm/nvm.sh

# Install python3.9. See: https://tecadmin.net/install-python-3-9-on-amazon-linux/
sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel 
wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz 
sudo tar xzf Python-3.9.16.tgz
cd Python-3.9.16 
sudo ./configure --enable-optimizations 
sudo make altinstall 
cd ..
rm Python-3.9.16.tgz
sudo alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.9 1
sudo alternatives --set python3 /usr/local/bin/python3.9

# Uninstall default aws cli and Install aws cli version-2.9.5
sudo pip2 uninstall awscli -y

echo "Installing aws cli version-2.9.5"
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.9.5.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm awscliv2.zip
rm -rf aws
sudo alternatives --install /usr/bin/aws aws /usr/local/bin/aws 1
sudo alternatives --set aws /usr/local/bin/aws

# Install sam cli 
echo "Installing sam cli version 1.82.0"
wget https://github.com/aws/aws-sam-cli/releases/download/v1.82.0/aws-sam-cli-linux-x86_64.zip
# wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install
if [ $? -ne 0 ]; then
	echo "Sam cli is already present, so deleting existing version"
	sudo rm /usr/local/bin/sam
	sudo rm -rf /usr/local/aws-sam-cli
	echp "Now installing sam cli version 1.33.0"
	sudo ./sam-installation/install    
fi
rm aws-sam-cli-linux-x86_64.zip
rm -rf sam-installation

# Install git-remote-codecommit version 1.16
echo "Installing git-remote-codecommit version 1.16"
python3 -m pip install git-remote-codecommit==1.16

# Install node v14.18.1
echo "Installing node v14.18.1"
nvm deactivate
nvm uninstall node
nvm install v16.20.0
nvm use v16.20.0
nvm alias default v16.20.0

# Install cdk cli version 2.32.1
# echo "Installing cdk cli version 2.32.1"
# npm uninstall -g aws-cdk
# npm install -g aws-cdk@2.32.1

# Install jq version 1.5
sudo yum -y install jq-1.5

#Install pylint version 2.15.8
python3 -m pip install pylint==2.15.8
