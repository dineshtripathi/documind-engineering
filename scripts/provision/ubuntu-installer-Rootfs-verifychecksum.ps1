# Compute local file hash
$local = (Get-FileHash "$dl\$rootfs" -Algorithm SHA256).Hash.ToLower()

# Read the expected hash line for our file from SHA256SUMS
$expected = (Get-Content "$dl\$sha" | Select-String -Pattern $rootfs).ToString().Split(" ")[0].ToLower()

# Compare
if ($local -ne $expected) {
  throw "SHA256 mismatch! Download may be corrupted."
} else {
  "Checksum OK: $local"
}
