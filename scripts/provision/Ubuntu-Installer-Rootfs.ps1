# Pick a folder
$dl = "C:\Users\DineshTripathi\Downloads"
New-Item -ItemType Directory -Path $dl -Force | Out-Null

# Files/URLs
$base = "https://cloud-images.ubuntu.com/wsl/releases/22.04/20240304"
$rootfs = "ubuntu-jammy-wsl-amd64-wsl.rootfs.tar.gz"
$sha = "SHA256SUMS"

# Download
Invoke-WebRequest -Uri "$base/$rootfs" -OutFile "$dl\$rootfs"
Invoke-WebRequest -Uri "$base/$sha"     -OutFile "$dl\$sha"
