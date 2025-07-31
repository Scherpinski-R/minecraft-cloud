# minecraft-cloud
Project to create and mantain a Minecraft server on Google Cloud (GCP)

# How to run

## Clone the repository
```
git clone https://github.com/Scherpinski-R/minecraft-cloud.git
```

## Create Resources
```
terraform init
```
```
terraform plan mc-plan
```
```
terraform apply mc-plan
```

## SSH on new Instance
- get ip from https://console.cloud.google.com/compute/instances
- ssh from gcp console
  
## Setup Credentials
- change .env file to match your mod provider credentials

## Get the server up and running

```
docker compose up -d
```

## Allow your friends IP
- manually throught firewall
- using cloud functions

# Have Fun!

