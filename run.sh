#!/bin/bash

echo "Creating experiment set-up"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed. Please install Docker first."
  exit 1
fi

# Check if the user has permissions to run Docker
if ! docker info &> /dev/null; then
  echo "Docker is installed, but you do not have the necessary permissions to run it."
  echo "Make sure your user is part of the 'docker' group or run the script with sudo."
  exit 1
fi

# Define containers to stop and remove
containers=("modsecurity-flask1" "modsecurity-flask2" "modsecurity-flask3" "modsecurity-flask4" "modsecurity-flask5")

# Stop specified containers
echo "Stopping specified containers..."
for container in "${containers[@]}"; do
  if docker ps -q -f name="^${container}$" &> /dev/null; then
    echo "Stopping container: $container"
    docker stop "$container"
  else
    echo "Container $container is not running or does not exist."
  fi
done

# Remove specified containers
echo "Removing specified containers..."
for container in "${containers[@]}"; do
  if docker ps -a -q -f name="^${container}$" &> /dev/null; then
    echo "Removing container: $container"
    docker rm "$container"
  else
    echo "Container $container does not exist."
  fi
done

# Remove specified images
echo "Removing specified images..."
for image in "${containers[@]}"; do
  if docker images -q "$image" &> /dev/null; then
    echo "Removing image: $image"
    docker rmi "$image"
  else
    echo "Image $image does not exist."
  fi
done

echo "Operation completed."

# Directory of the script
script_dir="$(dirname "$0")"

file1="check_signatures.py"
file2="app.py"

echo "Creating images"

sed -i "s/^own_id = .*/own_id = 1/" "$script_dir/$file1"
sed -i "s/^own_id = .*/own_id = 1/" "$script_dir/$file2"

docker build -t modsecurity-flask1 .

sed -i "s/^own_id = .*/own_id = 2/" "$script_dir/$file1"
sed -i "s/^own_id = .*/own_id = 2/" "$script_dir/$file2"

docker build -t modsecurity-flask2 .

sed -i "s/^own_id = .*/own_id = 3/" "$script_dir/$file1"
sed -i "s/^own_id = .*/own_id = 3/" "$script_dir/$file2"

docker build -t modsecurity-flask3 .

sed -i "s/^own_id = .*/own_id = 4/" "$script_dir/$file1"
sed -i "s/^own_id = .*/own_id = 4/" "$script_dir/$file2"

docker build -t modsecurity-flask4 .

sed -i "s/^own_id = .*/own_id = 5/" "$script_dir/$file1"
sed -i "s/^own_id = .*/own_id = 5/" "$script_dir/$file2"

docker build -t modsecurity-flask5 .

echo "Images created"

echo "Starting containers"

docker run -d -p 8080:80 --name modsecurity-flask1 modsecurity-flask1

docker run -d -p 8081:80 --name modsecurity-flask2 modsecurity-flask2

docker run -d -p 8082:80 --name modsecurity-flask3 modsecurity-flask3

docker run -d -p 8083:80 --name modsecurity-flask4 modsecurity-flask4

docker run -d -p 8084:80 --name modsecurity-flask5 modsecurity-flask5

echo "Containers started and ready"

echo "Set-up ready"
