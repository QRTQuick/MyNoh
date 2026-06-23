$ErrorActionPreference = "Stop"
$AppName = "Mynoh"
$Version = if ($env:VERSION) { $env:VERSION } else { "0.1.0" }
python scripts/build.py
New-Item -ItemType Directory -Force -Path packaging | Out-Null
Compress-Archive -Path "dist/$AppName/*" -DestinationPath "packaging/$AppName-$Version-windows-portable.zip" -Force
# Optional MSI when WiX Toolset is installed. Extend Product.wxs for branded production installers.
if (Get-Command candle.exe -ErrorAction SilentlyContinue) {
  Write-Host "WiX detected. Add packaging/Product.wxs to produce MSI."
}
Copy-Item "dist/$AppName/$AppName.exe" "packaging/$AppName-$Version.exe" -ErrorAction SilentlyContinue
