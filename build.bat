@echo off

mkdir build

echo ::: Building tools :::
cmake -B tools/compress/build -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXE_LINKER_FLAGS="/SAFESEH:NO" -A Win32 tools/compress
cmake --build tools/compress/build

echo ::: Decoding and re-encoding images :::
python tools\assets\generate_assets.py extract --rom baserom.gba
if errorlevel 1 exit /b 1
python tools\assets\generate_assets.py build --rom baserom.gba
if errorlevel 1 exit /b 1

echo ::: Including missing pieces :::
call tools\incbin.bat baserom.gba 0x0158 0x3d4d0
call tools\incbin.bat baserom.gba 0x03d5b8 0x03d63c
call tools\incbin.bat baserom.gba 0x03d63c 0x03d730
call tools\incbin.bat baserom.gba 0x03d740 0x03d784
call tools\incbin.bat baserom.gba 0x03d784 0x049114
call tools\incbin.bat baserom.gba 0x049120 0x055620
call tools\incbin.bat baserom.gba 0x06d4e0 0x071758
call tools\incbin.bat baserom.gba 0x071c90 0x3be3d4
call tools\incbin.bat baserom.gba 0x3c33f8 0x7b89a8
call tools\incbin.bat baserom.gba 0x7b89a8 0x800000

echo ::: Compiling source files :::
armcpp		-c src/color_transforms.cpp -o build/color_transforms.o
armcpp		-c src/strings.cpp -o build/strings.o

echo ::: Building ASM files :::
armasm		asm/buu.s -o build/buu.o
armasm		asm/GBARam.s -o build/GBARam.o
armasm		asm/ewram.s -o build/ewram.o
armasm		asm/iwram.s -o build/iwram.o
armasm		asm/rest_of_the_game.s -o build/rest_of_the_game.o

echo ::: Linking ^& Building image :::
armlink		build/GBARam.o build/color_transforms.o build/strings.o build/buu.o build/rest_of_the_game.o build/ewram.o build/iwram.o -noremove -scatter scatter.ld -o build/buu.axf
fromelf    	build/buu.axf -bin -o build/output
ren build\output\ROM_START image.gba
move build\output\image.gba image.gba

echo ::: Comparing Images :::
call tools\sha1.bat image.gba

rmdir /S /Q build