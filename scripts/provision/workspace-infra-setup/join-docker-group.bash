# create group if missing
getent group docker >/dev/null || sudo groupadd docker

# add your user
sudo usermod -aG docker $USER

# apply group without logging out
newgrp docker <<'EOS'
docker version
EOS

### Note: You may still need to log out and back in for some apps to pick up the group change
docker context ls
docker ps
echo "✅ You are now in the 'docker' group. If you see permission errors, please log out and back in."