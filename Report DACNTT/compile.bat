@echo off
chcp 65001 >nul
:: MiKTeX: ban cai cho mot user, cai cho moi user, hoac xelatex tren PATH
set MIKTEX=%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64
if not exist "%MIKTEX%\xelatex.exe" set MIKTEX=%ProgramFiles%\MiKTeX\miktex\bin\x64
if not exist "%MIKTEX%\xelatex.exe" for %%I in (xelatex.exe) do set MIKTEX=%%~dp$PATH:I
set TARGET=main
if not "%1"=="" set TARGET=%1

cd /d "%~dp0"

echo [1/4] XeLaTeX pass 1...
"%MIKTEX%\xelatex.exe" -synctex=1 -interaction=nonstopmode %TARGET%.tex
if errorlevel 1 goto fail

echo [2/4] Biber...
"%MIKTEX%\biber.exe" %TARGET%

echo [3/4] XeLaTeX pass 2...
"%MIKTEX%\xelatex.exe" -synctex=1 -interaction=nonstopmode %TARGET%.tex
if errorlevel 1 goto fail

echo [4/4] XeLaTeX pass 3 (danh so tai lieu tham khao theo nhom)...
"%MIKTEX%\xelatex.exe" -synctex=1 -interaction=nonstopmode %TARGET%.tex
if errorlevel 1 goto fail

echo Done! %TARGET%.pdf
start "" "%~dp0%TARGET%.pdf"
goto end

:fail
echo ERROR! Check %TARGET%.log
:end
