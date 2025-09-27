# create your user
adduser dinesh
usermod -aG sudo dinesh

# make 'dinesh' the default WSL user
printf "[user]\ndefault=dinesh\n" | tee /etc/wsl.conf

# optional: stop the daily login message
touch /root/.hushlogin

# exit to Windows and restart the distro to apply default user
exit
