# Where to store the distro’s filesystem
$target = "D:\wsl-hybrid\UbuntuHybrid"
New-Item -ItemType Directory -Path $target -Force | Out-Null

# Import (WSL2)
wsl --import Ubuntu-Hybrid $target "$dl\ubuntu-jammy-wsl-amd64-wsl.rootfs.tar" --version 2

# See it
wsl --list --verbose
