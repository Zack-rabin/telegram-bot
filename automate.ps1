# =========================
# AUTOMATED VCPKG + tgbot-cpp SETUP
# =========================

# CONFIGURATION
$VcpkgSource = "$env:USERPROFILE\vcpkg-temp"  # Temporary clone folder
$VcpkgDest   = "C:\vcpkg"                     # Final install folder
$VcpkgRepo   = "https://github.com/microsoft/vcpkg"

# 1. Remove previous temp folder if exists
if (Test-Path $VcpkgSource) {
    Write-Host "Removing existing temporary folder..."
    Remove-Item -Recurse -Force $VcpkgSource
}

# 2. Clone vcpkg repository
Write-Host "Cloning vcpkg from GitHub..."
git clone $VcpkgRepo $VcpkgSource

# 3. Move folder to destination
if (Test-Path $VcpkgDest) {
    Write-Host "Destination folder exists. Removing..."
    Remove-Item -Recurse -Force $VcpkgDest
}
Write-Host "Moving vcpkg to $VcpkgDest..."
Move-Item $VcpkgSource $VcpkgDest

# 4. Bootstrap vcpkg
Write-Host "Bootstrapping vcpkg..."
Push-Location $VcpkgDest
.\bootstrap-vcpkg.bat
Pop-Location

# 5. Integrate vcpkg with CMake
Write-Host "Integrating vcpkg with CMake..."
.\vcpkg integrate install 

# 6. Install tgbot-cpp (x64)
Write-Host "Installing tgbot-cpp (x64)..."
.\vcpkg install tgbot-cpp:x64-windows

Write-Host "✅ vcpkg and tgbot-cpp setup complete!"
