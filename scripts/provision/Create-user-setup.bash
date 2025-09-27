# === 0) Variables (change if you want a different username) ===
NEW_USER="dinesh"

# === 1) Create user + set password + grant sudo ===
id -u "$NEW_USER" >/dev/null 2>&1 || adduser "$NEW_USER"
usermod -aG sudo "$NEW_USER"

# === 2) Require password for sudo (safer than NOPASSWD) ===
# Ensure the default policy is passworded sudo
if ! grep -q '^%sudo\s\+ALL=(ALL:ALL)\s\+ALL' /etc/sudoers; then
  echo '%sudo   ALL=(ALL:ALL) ALL' >> /etc/sudoers
fi

# === 3) Make your user the default WSL user ===
# (This makes new shells land as the new user instead of root)
if [ -f /etc/wsl.conf ]; then
  # Update or add [user] default
  awk -v u="$NEW_USER" '
    BEGIN{found_user=0; found_default=0}
    /^\[user\]/{found_user=1; print; next}
    found_user==1 && /^default=/{print "default=" u; found_default=1; next}
    {print}
    END{
      if(found_user==0){print "[user]"; print "default=" u}
      else if(found_default==0){print "default=" u}
    }' /etc/wsl.conf > /etc/wsl.conf.new && mv /etc/wsl.conf.new /etc/wsl.conf
else
  printf "[user]\ndefault=%s\n" "$NEW_USER" > /etc/wsl.conf
fi

# === 4) Lock direct root login (no password) ===
passwd -l root

# === 5) Basic hygiene ===
# Quiet daily MOTD for root; new user will get normal MOTD
touch /root/.hushlogin

# Make sure sudo is installed (usually is on Ubuntu rootfs)
apt-get update -y && apt-get install -y sudo

echo "✅ Safe setup complete. Now exit and restart the distro:"
echo "   exit"
echo "   (in Windows PowerShell)  wsl --terminate Ubuntu-Hybrid"
echo "   (then)                   wsl -d Ubuntu-Hybrid"
