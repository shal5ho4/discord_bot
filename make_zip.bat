@echo off
setlocal

set "DEST_DIR=lambda_package"
set "ZIP_FILE=lambda_package.zip"

if not exist "%DEST_DIR%" (
    mkdir "%DEST_DIR%"
)

copy /Y *.py "%DEST_DIR%\" >nul
if exist ".env" (
    copy /Y ".env" "%DEST_DIR%\" >nul
)

powershell -Command "Compress-Archive -Path '%DEST_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force"

echo Packaging complete: %ZIP_FILE%
powershell -Command "Get-Content '%ZIP_FILE%' | Out-Null; Add-Type -AssemblyName 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::OpenRead('%ZIP_FILE%').Entries | ForEach-Object { $_.FullName }"
endlocal