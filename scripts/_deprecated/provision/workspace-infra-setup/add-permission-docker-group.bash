# 1) Add your user to 'docker' group
getent group docker >/dev/null || sudo groupadd docker
sudo usermod -aG docker "$USER"

# 2) Apply new group in this shell (no logout needed)
newgrp docker <<'EOS'
docker version
EOS
