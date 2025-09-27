# EXAMPLE: if /var/run/docker.sock exists
export DOCKER_HOST=unix:///var/run/docker.sock
# or if /mnt/wsl/shared-docker/docker.sock exists
# export DOCKER_HOST=unix:///mnt/wsl/shared-docker/docker.sock
# or if /run/desktop/docker.sock exists
# export DOCKER_HOST=unix:///run/desktop/docker.sock

# persist it:
grep -q DOCKER_HOST ~/.bashrc || echo 'export DOCKER_HOST='"$DOCKER_HOST" >> ~/.bashrc
