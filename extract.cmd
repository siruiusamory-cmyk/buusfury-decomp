@echo off
setlocal
set "ROOT=%~dp0"
python "%ROOT%tools\extract\extract.py" --rom "%ROOT%baserom.gba" --sha1-file "%ROOT%baserom.sha1" --build "%ROOT%build"
if errorlevel 1 exit /b 1
python "%ROOT%tools\assets\generate_assets.py" extract --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\generated"
if errorlevel 1 exit /b 1
python "%ROOT%tools\tilebank\generate_tilebank.py" extract --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\tilebank" --manifest "%ROOT%tools\tilebank\tilebank_manifest.csv"
if errorlevel 1 exit /b 1
python "%ROOT%tools\mapcontainer\generate_mapcontainer.py" extract --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\mapcontainer" --records "%ROOT%assets\maprecords"
if errorlevel 1 exit /b 1
python "%ROOT%tools\mapcontainer\generate_mapcontainer.py" extract --block sprite --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\spritecontainer"
if errorlevel 1 exit /b 1
python "%ROOT%tools\mapcontainer\generate_mapcontainer.py" extract --block endrom --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\endrom" --records "%ROOT%assets\endromrecords"
if errorlevel 1 exit /b 1
python "%ROOT%tools\mapcontainer\generate_mapcontainer.py" extract --block spritedefs --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\spritedefs" --records "%ROOT%assets\spriterecords"
if errorlevel 1 exit /b 1
python "%ROOT%tools\mapcontainer\generate_mapcontainer.py" extract --block assetdir --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\assetdir" --records "%ROOT%assets\assetdirrecords"
if errorlevel 1 exit /b 1
python "%ROOT%tools\structured\generate_structured.py" extract --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\structured"
if errorlevel 1 exit /b 1
python "%ROOT%tools\research\opcode_stream.py" build --rom "%ROOT%baserom.gba" --out-dir "%ROOT%build\opcode"
if errorlevel 1 exit /b 1
python "%ROOT%tools\research\generate_jcalg1.py" --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\jcalg1" --out-dir "%ROOT%build\jcalg1"
if errorlevel 1 exit /b 1
python "%ROOT%tools\mapcontainer\generate_assetdir3.py" extract --rom "%ROOT%baserom.gba" --payloads "%ROOT%assets\assetdir3"
python "%ROOT%tools\research\rawlabeled.py" --extract --rom "%ROOT%baserom.gba"
if errorlevel 1 exit /b 1
echo extract done
