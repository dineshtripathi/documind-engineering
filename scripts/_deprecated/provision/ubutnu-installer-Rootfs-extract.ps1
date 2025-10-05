# target folder banado
New-Item -ItemType Directory -Path "D:\wsl-hybrid\UbuntuHybrid" -Force | Out-Null

# import karo (source is in C:, target is D:)
wsl --import Ubuntu-Hybrid "D:\wsl-hybrid\UbuntuHybrid" "C:\Users\DineshTripathi\Downloads\ubuntu-jammy-wsl-amd64-wsl.rootfs.tar.gz" --version 2
