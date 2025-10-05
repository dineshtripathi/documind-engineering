sudo apt-get update -y
sudo apt-get install -y build-essential git curl wget unzip jq pkg-config ca-certificates libssl-dev software-properties-common

wget -q https://packages.microsoft.com/config/ubuntu/$(. /etc/os-release; echo $VERSION_ID)/packages-microsoft-prod.deb -O /tmp/msprod.deb
sudo dpkg -i /tmp/msprod.deb
sudo apt-get update -y
sudo apt-get install -y dotnet-sdk-8.0
dotnet --info
