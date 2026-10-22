@echo off
setlocal
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
if "%ADS%"=="" set "ADS=%~dp0..\toolchains\ads12-build805"
set "PATH=%ADS%\Bin;%PATH%"
set "ARMHOME=%ADS%"
set "ARMINC=%ADS%\Include"
set "ARMLIB=%ADS%\Lib"
cd /d "%ROOT%"
if not exist build mkdir build
echo === incbin slices ===
call tools\incbin.bat baserom.gba 0x3bbbb0 0x3bbe70
call tools\incbin.bat baserom.gba 0x7594ec 0x7594f0
call tools\incbin.bat baserom.gba 0x759510 0x759620
call tools\incbin.bat baserom.gba 0x759680 0x75a0e9
call tools\incbin.bat baserom.gba 0x75a22f 0x75a2a0
call tools\incbin.bat baserom.gba 0x75a6a8 0x75a6dc
call tools\incbin.bat baserom.gba 0x2b8bc8 0x2b8bf4
call tools\incbin.bat baserom.gba 0x2b8c38 0x2b9bb0
call tools\incbin.bat baserom.gba 0x3352 0x3354
call tools\incbin.bat baserom.gba 0x4092 0x4094
call tools\incbin.bat baserom.gba 0x45c2 0x45c4
call tools\incbin.bat baserom.gba 0x4810 0x4812
call tools\incbin.bat baserom.gba 0x4ae4 0x4ae6
call tools\incbin.bat baserom.gba 0x5bfc 0x5bfe
call tools\incbin.bat baserom.gba 0x5c3e 0x5c40
call tools\incbin.bat baserom.gba 0x6092 0x6094
call tools\incbin.bat baserom.gba 0x628c 0x628e
call tools\incbin.bat baserom.gba 0x6aa8 0x6aaa
call tools\incbin.bat baserom.gba 0x6ff4 0x6ffa
call tools\incbin.bat baserom.gba 0x73b6 0x73b8
call tools\incbin.bat baserom.gba 0x73bc 0x73be
call tools\incbin.bat baserom.gba 0x74ba 0x74bc
call tools\incbin.bat baserom.gba 0x74c0 0x74c2
call tools\incbin.bat baserom.gba 0x774e 0x7752
call tools\incbin.bat baserom.gba 0x7a18 0x7a1a
call tools\incbin.bat baserom.gba 0x7d5c 0x7d5e
call tools\incbin.bat baserom.gba 0x8486 0x84a6
call tools\incbin.bat baserom.gba 0x86b2 0x86b4
call tools\incbin.bat baserom.gba 0x9018 0x9022
call tools\incbin.bat baserom.gba 0x98f8 0x98fa
call tools\incbin.bat baserom.gba 0xa4e0 0xa4e2
call tools\incbin.bat baserom.gba 0xa520 0xa522
call tools\incbin.bat baserom.gba 0xa78c 0xa78e
call tools\incbin.bat baserom.gba 0xa9b0 0xa9b8
call tools\incbin.bat baserom.gba 0xad7a 0xad82
call tools\incbin.bat baserom.gba 0xb096 0xb0a8
call tools\incbin.bat baserom.gba 0xbc46 0xbc5a
call tools\incbin.bat baserom.gba 0xc274 0xc276
call tools\incbin.bat baserom.gba 0xc42c 0xc42e
call tools\incbin.bat baserom.gba 0xcb00 0xcb02
call tools\incbin.bat baserom.gba 0xcdd8 0xcde2
call tools\incbin.bat baserom.gba 0xcee4 0xcef2
call tools\incbin.bat baserom.gba 0xd1a8 0xd1b2
call tools\incbin.bat baserom.gba 0xd876 0xd892
call tools\incbin.bat baserom.gba 0xde14 0xde16
call tools\incbin.bat baserom.gba 0x14754 0x14770
call tools\incbin.bat baserom.gba 0x15e80 0x15e94
call tools\incbin.bat baserom.gba 0x178c0 0x178c2
call tools\incbin.bat baserom.gba 0x17964 0x17966
call tools\incbin.bat baserom.gba 0x17bda 0x17be0
call tools\incbin.bat baserom.gba 0x17be4 0x17be8
call tools\incbin.bat baserom.gba 0x17bec 0x17bf2
call tools\incbin.bat baserom.gba 0x18786 0x187a2
call tools\incbin.bat baserom.gba 0x1a578 0x1a590
call tools\incbin.bat baserom.gba 0x1c6a4 0x1c6c6
call tools\incbin.bat baserom.gba 0x1cb32 0x1cb34
call tools\incbin.bat baserom.gba 0x1cb7c 0x1cb86
call tools\incbin.bat baserom.gba 0x1d762 0x1d790
call tools\incbin.bat baserom.gba 0x1d958 0x1d95a
call tools\incbin.bat baserom.gba 0x1e13c 0x1e13e
call tools\incbin.bat baserom.gba 0x1fb38 0x1fb3a
call tools\incbin.bat baserom.gba 0x1ff40 0x1ff4e
call tools\incbin.bat baserom.gba 0x20530 0x2054a
call tools\incbin.bat baserom.gba 0x21052 0x2105a
call tools\incbin.bat baserom.gba 0x21166 0x2116e
call tools\incbin.bat baserom.gba 0x2125e 0x2126a
call tools\incbin.bat baserom.gba 0x21828 0x21832
call tools\incbin.bat baserom.gba 0x21870 0x21872
call tools\incbin.bat baserom.gba 0x21bb4 0x21bb6
call tools\incbin.bat baserom.gba 0x220c2 0x220d8
call tools\incbin.bat baserom.gba 0x228fa 0x228fc
call tools\incbin.bat baserom.gba 0x22900 0x22902
call tools\incbin.bat baserom.gba 0x23b2a 0x23b50
call tools\incbin.bat baserom.gba 0x23b52 0x23c1c
call tools\incbin.bat baserom.gba 0x23ee0 0x23ee2
call tools\incbin.bat baserom.gba 0x23f84 0x23f86
call tools\incbin.bat baserom.gba 0x242d6 0x242e2
call tools\incbin.bat baserom.gba 0x243e6 0x243e8
call tools\incbin.bat baserom.gba 0x24556 0x2455e
call tools\incbin.bat baserom.gba 0x2bdbc 0x2bdbe
call tools\incbin.bat baserom.gba 0x2c058 0x2c066
call tools\incbin.bat baserom.gba 0x2c77a 0x2c782
call tools\incbin.bat baserom.gba 0x2e638 0x2e63c
call tools\incbin.bat baserom.gba 0x2e644 0x2e654
call tools\incbin.bat baserom.gba 0x304dc 0x304de
call tools\incbin.bat baserom.gba 0x3383a 0x33862
call tools\incbin.bat baserom.gba 0x34280 0x34294
call tools\incbin.bat baserom.gba 0x34816 0x3481c
call tools\incbin.bat baserom.gba 0x35e34 0x35e38
call tools\incbin.bat baserom.gba 0x35e82 0x35e86
call tools\incbin.bat baserom.gba 0x36968 0x3696e
call tools\incbin.bat baserom.gba 0x3722e 0x37238
call tools\incbin.bat baserom.gba 0x37254 0x3725a
call tools\incbin.bat baserom.gba 0x37478 0x3747e
call tools\incbin.bat baserom.gba 0x3747e 0x37480
call tools\incbin.bat baserom.gba 0x37568 0x3756a
call tools\incbin.bat baserom.gba 0x3764a 0x3764c
call tools\incbin.bat baserom.gba 0x378da 0x378dc
call tools\incbin.bat baserom.gba 0x379b4 0x379b6
call tools\incbin.bat baserom.gba 0x37b2e 0x37b32
call tools\incbin.bat baserom.gba 0x37e26 0x37e28
call tools\incbin.bat baserom.gba 0x383ca 0x383d2
call tools\incbin.bat baserom.gba 0x383d2 0x383d4
call tools\incbin.bat baserom.gba 0x387d2 0x387d6
call tools\incbin.bat baserom.gba 0x38ad0 0x38ad2
call tools\incbin.bat baserom.gba 0x38dd8 0x38de2
call tools\incbin.bat baserom.gba 0x393be 0x393c2
call tools\incbin.bat baserom.gba 0x3942a 0x3942e
call tools\incbin.bat baserom.gba 0x3973e 0x3974a
call tools\incbin.bat baserom.gba 0x398c4 0x398ca
call tools\incbin.bat baserom.gba 0x3dd32 0x3dd34
call tools\incbin.bat baserom.gba 0x3f36c 0x3f36e
call tools\incbin.bat baserom.gba 0x413a4 0x413a8
call tools\incbin.bat baserom.gba 0x413d6 0x413d8
call tools\incbin.bat baserom.gba 0x413dc 0x413e0
call tools\incbin.bat baserom.gba 0x4165c 0x4168c
call tools\incbin.bat baserom.gba 0x41786 0x417ac
call tools\incbin.bat baserom.gba 0x41afc 0x41b00
call tools\incbin.bat baserom.gba 0x4256c 0x42592
call tools\incbin.bat baserom.gba 0x42594 0x425b0
call tools\incbin.bat baserom.gba 0x47fae 0x47fb0
call tools\incbin.bat baserom.gba 0x4802e 0x48034
call tools\incbin.bat baserom.gba 0xf1e8 0xf1f8
call tools\incbin.bat baserom.gba 0xf4b0 0xf4b2
call tools\incbin.bat baserom.gba 0x10dd8 0x10dda
call tools\incbin.bat baserom.gba 0x110d0 0x110d2
call tools\incbin.bat baserom.gba 0x11552 0x1155a
call tools\incbin.bat baserom.gba 0x1218c 0x1218e
call tools\incbin.bat baserom.gba 0x123c4 0x123de
call tools\incbin.bat baserom.gba 0x12fa4 0x12fa6
call tools\incbin.bat baserom.gba 0x131b4 0x131b6
call tools\incbin.bat baserom.gba 0x13b94 0x13b96
call tools\incbin.bat baserom.gba 0x195a4 0x195a6
call tools\incbin.bat baserom.gba 0x19d0c 0x19d1e
call tools\incbin.bat baserom.gba 0x1a23a 0x1a2aa
call tools\incbin.bat baserom.gba 0x1a30e 0x1a322
call tools\incbin.bat baserom.gba 0x1a354 0x1a356
call tools\incbin.bat baserom.gba 0x1a3b0 0x1a3b2
call tools\incbin.bat baserom.gba 0x1b22e 0x1b23c
call tools\incbin.bat baserom.gba 0x1b4ce 0x1b4ec
call tools\incbin.bat baserom.gba 0x1b7fe 0x1b800
call tools\incbin.bat baserom.gba 0x1b810 0x1b814
call tools\incbin.bat baserom.gba 0x1ba7e 0x1ba84
call tools\incbin.bat baserom.gba 0x1ba88 0x1ba8c
call tools\incbin.bat baserom.gba 0x1bdb6 0x1bdbc
call tools\incbin.bat baserom.gba 0x1bdc0 0x1bdc4
call tools\incbin.bat baserom.gba 0x1bdc8 0x1bdcc
call tools\incbin.bat baserom.gba 0x20a76 0x20a7c
call tools\incbin.bat baserom.gba 0x20a94 0x20aa4
call tools\incbin.bat baserom.gba 0x24d44 0x24d94
call tools\incbin.bat baserom.gba 0x25288 0x2528a
call tools\incbin.bat baserom.gba 0x25ad4 0x25adc
call tools\incbin.bat baserom.gba 0x25ae4 0x25af0
call tools\incbin.bat baserom.gba 0x25af8 0x25afa
call tools\incbin.bat baserom.gba 0x26582 0x26584
call tools\incbin.bat baserom.gba 0x266d2 0x266d4
call tools\incbin.bat baserom.gba 0x26802 0x26804
call tools\incbin.bat baserom.gba 0x2737a 0x2737c
call tools\incbin.bat baserom.gba 0x27692 0x2769e
call tools\incbin.bat baserom.gba 0x27926 0x27932
call tools\incbin.bat baserom.gba 0x27d90 0x27d92
call tools\incbin.bat baserom.gba 0x286b6 0x286b8
call tools\incbin.bat baserom.gba 0x286bc 0x286d2
call tools\incbin.bat baserom.gba 0x289ba 0x289de
call tools\incbin.bat baserom.gba 0x28bfa 0x28c02
call tools\incbin.bat baserom.gba 0x28c02 0x28c04
call tools\incbin.bat baserom.gba 0x2900a 0x2900e
call tools\incbin.bat baserom.gba 0x2995e 0x29962
call tools\incbin.bat baserom.gba 0x2a098 0x2a09a
call tools\incbin.bat baserom.gba 0x2a580 0x2a5a2
call tools\incbin.bat baserom.gba 0x2a7ac 0x2a7b2
call tools\incbin.bat baserom.gba 0x2a9f8 0x2aa06
call tools\incbin.bat baserom.gba 0x2aac4 0x2aac6
call tools\incbin.bat baserom.gba 0x2c8fa 0x2c8fe
call tools\incbin.bat baserom.gba 0x2cd76 0x2cd78
call tools\incbin.bat baserom.gba 0x2cde0 0x2cde4
call tools\incbin.bat baserom.gba 0x2d166 0x2d168
call tools\incbin.bat baserom.gba 0x2d76c 0x2d78c
call tools\incbin.bat baserom.gba 0x2d798 0x2d79c
call tools\incbin.bat baserom.gba 0x2de08 0x2de1c
call tools\incbin.bat baserom.gba 0x2e036 0x2e040
call tools\incbin.bat baserom.gba 0x2e09e 0x2e0a8
call tools\incbin.bat baserom.gba 0x2ed7c 0x2ed98
call tools\incbin.bat baserom.gba 0x2fb9c 0x2fc2c
call tools\incbin.bat baserom.gba 0x2ff10 0x2ff1c
call tools\incbin.bat baserom.gba 0x30b12 0x30b14
call tools\incbin.bat baserom.gba 0x30ef4 0x30ef8
call tools\incbin.bat baserom.gba 0x30efc 0x30f04
call tools\incbin.bat baserom.gba 0x30f08 0x30f0c
call tools\incbin.bat baserom.gba 0x32d40 0x32d44
call tools\incbin.bat baserom.gba 0x32dc4 0x32dc8
call tools\incbin.bat baserom.gba 0x33d60 0x33d66
call tools\incbin.bat baserom.gba 0x33e72 0x33e74
call tools\incbin.bat baserom.gba 0x349e8 0x349f8
call tools\incbin.bat baserom.gba 0x34ce2 0x34cf8
call tools\incbin.bat baserom.gba 0x36d66 0x36d82
call tools\incbin.bat baserom.gba 0x37898 0x3789a
call tools\incbin.bat baserom.gba 0x39f08 0x39f16
call tools\incbin.bat baserom.gba 0x3a7ee 0x3a7f2
call tools\incbin.bat baserom.gba 0x3ac58 0x3ac5c
call tools\incbin.bat baserom.gba 0x3c0a8 0x3c0b6
call tools\incbin.bat baserom.gba 0x3c1d8 0x3c1da
call tools\incbin.bat baserom.gba 0x3d0ec 0x3d0ee
call tools\incbin.bat baserom.gba 0x3e368 0x3e36a
call tools\incbin.bat baserom.gba 0x40f7c 0x40f7e
call tools\incbin.bat baserom.gba 0x41df4 0x41df8
call tools\incbin.bat baserom.gba 0x4208a 0x420b0
call tools\incbin.bat baserom.gba 0x425b4 0x425f0
call tools\incbin.bat baserom.gba 0x425f2 0x42604
call tools\incbin.bat baserom.gba 0x4260a 0x42638
call tools\incbin.bat baserom.gba 0x4263c 0x4269c
call tools\incbin.bat baserom.gba 0x4269e 0x426c4
call tools\incbin.bat baserom.gba 0x42d2a 0x42d72
call tools\incbin.bat baserom.gba 0x42faa 0x42fac
call tools\incbin.bat baserom.gba 0x42fb8 0x42fbc
call tools\incbin.bat baserom.gba 0x4ed94 0x4ed96
call tools\incbin.bat baserom.gba 0x4ee58 0x4ee5a
call tools\incbin.bat baserom.gba 0x4f02e 0x4f032
call tools\incbin.bat baserom.gba 0x4f05e 0x4f060
call tools\incbin.bat baserom.gba 0x4f99c 0x4f99e
call tools\incbin.bat baserom.gba 0x5ad4 0x5bc0
call tools\incbin.bat baserom.gba 0x5c6e 0x5e36
call tools\incbin.bat baserom.gba 0x7770 0x7774
call tools\incbin.bat baserom.gba 0xa26e 0xa272
call tools\incbin.bat baserom.gba 0xa418 0xa41a
call tools\incbin.bat baserom.gba 0xd518 0xd538
call tools\incbin.bat baserom.gba 0xf624 0xf62c
call tools\incbin.bat baserom.gba 0x10576 0x10582
call tools\incbin.bat baserom.gba 0x12d0a 0x12d0c
call tools\incbin.bat baserom.gba 0x13fbe 0x13fc0
call tools\incbin.bat baserom.gba 0x16996 0x16998
call tools\incbin.bat baserom.gba 0x16a92 0x16aa8
call tools\incbin.bat baserom.gba 0x16b66 0x16c58
call tools\incbin.bat baserom.gba 0x18392 0x18394
call tools\incbin.bat baserom.gba 0x1dce8 0x1dd72
call tools\incbin.bat baserom.gba 0x1dda2 0x1ddec
call tools\incbin.bat baserom.gba 0x1ddee 0x1df7e
call tools\incbin.bat baserom.gba 0x1f05e 0x1f06a
call tools\incbin.bat baserom.gba 0x1f346 0x1f364
call tools\incbin.bat baserom.gba 0x1f790 0x1f792
call tools\incbin.bat baserom.gba 0x2079c 0x2079e
call tools\incbin.bat baserom.gba 0x20da0 0x20dac
call tools\incbin.bat baserom.gba 0x20eea 0x20eec
call tools\incbin.bat baserom.gba 0x2105a 0x2105c
call tools\incbin.bat baserom.gba 0x21832 0x21834
call tools\incbin.bat baserom.gba 0x23088 0x2309c
call tools\incbin.bat baserom.gba 0x2312a 0x2312c
call tools\incbin.bat baserom.gba 0x23482 0x23484
call tools\incbin.bat baserom.gba 0x23490 0x234dc
call tools\incbin.bat baserom.gba 0x23c7c 0x23cb8
call tools\incbin.bat baserom.gba 0x24976 0x24978
call tools\incbin.bat baserom.gba 0x255a8 0x255aa
call tools\incbin.bat baserom.gba 0x28eba 0x28ebc
call tools\incbin.bat baserom.gba 0x292d8 0x292e0
call tools\incbin.bat baserom.gba 0x2a236 0x2a238
call tools\incbin.bat baserom.gba 0x2a7b2 0x2a7b4
call tools\incbin.bat baserom.gba 0x2c1d0 0x2c1dc
call tools\incbin.bat baserom.gba 0x338fc 0x33908
call tools\incbin.bat baserom.gba 0x33b86 0x33b88
call tools\incbin.bat baserom.gba 0x358a2 0x358a4
call tools\incbin.bat baserom.gba 0x36d82 0x36d84
call tools\incbin.bat baserom.gba 0x38180 0x38192
call tools\incbin.bat baserom.gba 0x382be 0x382c0
call tools\incbin.bat baserom.gba 0x3870a 0x3870c
call tools\incbin.bat baserom.gba 0x38a82 0x38a84
call tools\incbin.bat baserom.gba 0x3ac4c 0x3ac54
call tools\incbin.bat baserom.gba 0x3bf0e 0x3bf28
call tools\incbin.bat baserom.gba 0x3c4d8 0x3c4dc
call tools\incbin.bat baserom.gba 0x4e4da 0x4e4dc
call tools\incbin.bat baserom.gba 0x4e4de 0x4e4e0
call tools\incbin.bat baserom.gba 0x4e4e2 0x4e4e4
call tools\incbin.bat baserom.gba 0x4e4e6 0x4e4e8
call tools\incbin.bat baserom.gba 0x4e4ea 0x4e4ec
call tools\incbin.bat baserom.gba 0x4e4ee 0x4e4f0
call tools\incbin.bat baserom.gba 0x4e4f2 0x4e4f4
call tools\incbin.bat baserom.gba 0x4e4f6 0x4e4f8
call tools\incbin.bat baserom.gba 0x4e4fa 0x4e4fc
call tools\incbin.bat baserom.gba 0x4e4fe 0x4e500
call tools\incbin.bat baserom.gba 0x4e502 0x4e504
call tools\incbin.bat baserom.gba 0x4e506 0x4e508
call tools\incbin.bat baserom.gba 0x4e51e 0x4e520
call tools\incbin.bat baserom.gba 0x4e522 0x4e524
call tools\incbin.bat baserom.gba 0x4e546 0x4e548
call tools\incbin.bat baserom.gba 0x4e54a 0x4e54c
call tools\incbin.bat baserom.gba 0x4ec02 0x4ec04
call tools\incbin.bat baserom.gba 0x4ec06 0x4ec08
call tools\incbin.bat baserom.gba 0x4ec1e 0x4ec20
call tools\incbin.bat baserom.gba 0x4ec9a 0x4ec9c
call tools\incbin.bat baserom.gba 0x4ecbe 0x4ecc0
call tools\incbin.bat baserom.gba 0x4ece2 0x4ece4
call tools\incbin.bat baserom.gba 0x4ecf6 0x4ecf8
call tools\incbin.bat baserom.gba 0x4f076 0x4f078
call tools\incbin.bat baserom.gba 0x4f09e 0x4f0a0
call tools\incbin.bat baserom.gba 0x4f0a2 0x4f0a4
call tools\incbin.bat baserom.gba 0x4f0c2 0x4f0c4
call tools\incbin.bat baserom.gba 0x4f0de 0x4f0e0
call tools\incbin.bat baserom.gba 0x4f116 0x4f118
call tools\incbin.bat baserom.gba 0x4f15e 0x4f160
call tools\incbin.bat baserom.gba 0x4f162 0x4f164
call tools\incbin.bat baserom.gba 0x4f172 0x4f174
call tools\incbin.bat baserom.gba 0x4f176 0x4f178
call tools\incbin.bat baserom.gba 0x4f186 0x4f188
call tools\incbin.bat baserom.gba 0x4f19e 0x4f1a0
call tools\incbin.bat baserom.gba 0x4f1a2 0x4f1a4
call tools\incbin.bat baserom.gba 0x4f1a6 0x4f1a8
call tools\incbin.bat baserom.gba 0x4f1aa 0x4f1ac
call tools\incbin.bat baserom.gba 0x4f1ae 0x4f1b0
call tools\incbin.bat baserom.gba 0x4f1b2 0x4f1b4
call tools\incbin.bat baserom.gba 0x4f1ea 0x4f1ec
call tools\incbin.bat baserom.gba 0x4f1ee 0x4f1f0
call tools\incbin.bat baserom.gba 0x4f1f2 0x4f1f4
call tools\incbin.bat baserom.gba 0x4f1f6 0x4f1f8
call tools\incbin.bat baserom.gba 0x4f1fa 0x4f1fc
call tools\incbin.bat baserom.gba 0x4f1fe 0x4f200
call tools\incbin.bat baserom.gba 0x4f202 0x4f204
call tools\incbin.bat baserom.gba 0x4f206 0x4f208
call tools\incbin.bat baserom.gba 0x4f20a 0x4f20c
call tools\incbin.bat baserom.gba 0x4f282 0x4f284
call tools\incbin.bat baserom.gba 0x4f292 0x4f294
call tools\incbin.bat baserom.gba 0x4f296 0x4f298
call tools\incbin.bat baserom.gba 0x4f29a 0x4f29c
call tools\incbin.bat baserom.gba 0x4f2ba 0x4f2bc
call tools\incbin.bat baserom.gba 0x4f2ca 0x4f2cc
call tools\incbin.bat baserom.gba 0x4f2ce 0x4f2d0
call tools\incbin.bat baserom.gba 0x4f2de 0x4f2e0
call tools\incbin.bat baserom.gba 0x4f2e2 0x4f2e4
call tools\incbin.bat baserom.gba 0x4f2e6 0x4f2e8
call tools\incbin.bat baserom.gba 0x4f30e 0x4f310
call tools\incbin.bat baserom.gba 0x4f31e 0x4f320
call tools\incbin.bat baserom.gba 0x4f322 0x4f324
call tools\incbin.bat baserom.gba 0x4f36e 0x4f370
call tools\incbin.bat baserom.gba 0x4f37e 0x4f380
call tools\incbin.bat baserom.gba 0x4f382 0x4f384
call tools\incbin.bat baserom.gba 0x4f386 0x4f388
call tools\incbin.bat baserom.gba 0x4f38a 0x4f38c
call tools\incbin.bat baserom.gba 0x4f39a 0x4f39c
call tools\incbin.bat baserom.gba 0x4f3aa 0x4f3ac
call tools\incbin.bat baserom.gba 0x4f3ae 0x4f3b0
call tools\incbin.bat baserom.gba 0x4f412 0x4f414
call tools\incbin.bat baserom.gba 0x4f44a 0x4f44c
call tools\incbin.bat baserom.gba 0x4f44e 0x4f450
call tools\incbin.bat baserom.gba 0x4f452 0x4f454
call tools\incbin.bat baserom.gba 0x4f456 0x4f458
call tools\incbin.bat baserom.gba 0x4f48a 0x4f48c
call tools\incbin.bat baserom.gba 0x4f49a 0x4f49c
call tools\incbin.bat baserom.gba 0x4f4c2 0x4f4c4
call tools\incbin.bat baserom.gba 0x4f51a 0x4f51c
call tools\incbin.bat baserom.gba 0x4f51e 0x4f520
call tools\incbin.bat baserom.gba 0x4f522 0x4f524
call tools\incbin.bat baserom.gba 0x4f526 0x4f528
call tools\incbin.bat baserom.gba 0x4f52a 0x4f52c
call tools\incbin.bat baserom.gba 0x4f52e 0x4f530
call tools\incbin.bat baserom.gba 0x4f532 0x4f534
call tools\incbin.bat baserom.gba 0x4f536 0x4f538
call tools\incbin.bat baserom.gba 0x4f556 0x4f558
call tools\incbin.bat baserom.gba 0x4f596 0x4f598
call tools\incbin.bat baserom.gba 0x4f5e2 0x4f5e4
call tools\incbin.bat baserom.gba 0x4f672 0x4f674
call tools\incbin.bat baserom.gba 0x4fcb6 0x4fcb8
call tools\incbin.bat baserom.gba 0x4fcba 0x4fcbc
call tools\incbin.bat baserom.gba 0x4fcbe 0x4fcc0
call tools\incbin.bat baserom.gba 0x4fcc2 0x4fcc4
call tools\incbin.bat baserom.gba 0x4fcc6 0x4fcc8
call tools\incbin.bat baserom.gba 0x4fcda 0x4fcdc
call tools\incbin.bat baserom.gba 0x4fcde 0x4fce0
call tools\incbin.bat baserom.gba 0x4fdca 0x4fdcc
call tools\incbin.bat baserom.gba 0x4fdce 0x4fdd0
call tools\incbin.bat baserom.gba 0x4fdd2 0x4fdd4
call tools\incbin.bat baserom.gba 0x4fdd6 0x4fdd8
call tools\incbin.bat baserom.gba 0x4fdda 0x4fddc
call tools\incbin.bat baserom.gba 0x4fdde 0x4fde0
call tools\incbin.bat baserom.gba 0x4fde2 0x4fde4
call tools\incbin.bat baserom.gba 0x4fe72 0x4fe74
call tools\incbin.bat baserom.gba 0x4fe76 0x4fe78
call tools\incbin.bat baserom.gba 0x4fe7a 0x4fe7c
call tools\incbin.bat baserom.gba 0x4fe9a 0x4fe9c
call tools\incbin.bat baserom.gba 0x4fed6 0x4fedc
call tools\incbin.bat baserom.gba 0x501de 0x501e0
call tools\incbin.bat baserom.gba 0x145bc 0x14666
call tools\incbin.bat baserom.gba 0x14668 0x146b2
call tools\incbin.bat baserom.gba 0x14744 0x14748
call tools\incbin.bat baserom.gba 0x1474c 0x14750
call tools\incbin.bat baserom.gba 0x14c34 0x14c5c
call tools\incbin.bat baserom.gba 0x1ab6e 0x1ab7c
call tools\incbin.bat baserom.gba 0x2ad34 0x2ad48
call tools\incbin.bat baserom.gba 0x2ad4c 0x2ad58
call tools\incbin.bat baserom.gba 0x2ae18 0x2ae20
call tools\incbin.bat baserom.gba 0x2aeaa 0x2aeb0
call tools\incbin.bat baserom.gba 0x2aef8 0x2af04
call tools\incbin.bat baserom.gba 0x2b1fc 0x2b20c
call tools\incbin.bat baserom.gba 0x2b210 0x2b214
call tools\incbin.bat baserom.gba 0x2b3b4 0x2b3c0
call tools\incbin.bat baserom.gba 0x2b3c4 0x2b3d0
call tools\incbin.bat baserom.gba 0x2b5ce 0x2b5d4
call tools\incbin.bat baserom.gba 0x2b6e4 0x2b6f8
call tools\incbin.bat baserom.gba 0x2b6fc 0x2b708
call tools\incbin.bat baserom.gba 0x2b89c 0x2b8ac
call tools\incbin.bat baserom.gba 0x2b8b0 0x2b8f0
call tools\incbin.bat baserom.gba 0x2b974 0x2b97c
call tools\incbin.bat baserom.gba 0x2d1cc 0x2d1e8
call tools\incbin.bat baserom.gba 0x2d318 0x2d324
call tools\incbin.bat baserom.gba 0x2d3ba 0x2d3bc
call tools\incbin.bat baserom.gba 0x2d49e 0x2d4a4
call tools\incbin.bat baserom.gba 0x2d4ac 0x2d4b0
call tools\incbin.bat baserom.gba 0x2d64c 0x2d650
call tools\incbin.bat baserom.gba 0x2db6a 0x2db6c
call tools\incbin.bat baserom.gba 0x2de66 0x2de7c
call tools\incbin.bat baserom.gba 0x2df32 0x2df38
call tools\incbin.bat baserom.gba 0x2df40 0x2df44
call tools\incbin.bat baserom.gba 0x2dfca 0x2dfd0
call tools\incbin.bat baserom.gba 0x2dfd4 0x2dfd8
call tools\incbin.bat baserom.gba 0x2e254 0x2e270
call tools\incbin.bat baserom.gba 0x2e274 0x2e278
call tools\incbin.bat baserom.gba 0x2e33a 0x2e348
call tools\incbin.bat baserom.gba 0x2e6a6 0x2e6a8
call tools\incbin.bat baserom.gba 0x2e812 0x2e83c
call tools\incbin.bat baserom.gba 0x2f21a 0x2f224
call tools\incbin.bat baserom.gba 0x2f708 0x2f710
call tools\incbin.bat baserom.gba 0x2f714 0x2f724
call tools\incbin.bat baserom.gba 0x2f742 0x2f74c
call tools\incbin.bat baserom.gba 0x2fc34 0x2fc52
call tools\incbin.bat baserom.gba 0x2ff06 0x2ff0c
call tools\incbin.bat baserom.gba 0x2ff96 0x2ffa0
call tools\incbin.bat baserom.gba 0x3018d 0x301b8
call tools\incbin.bat baserom.gba 0x314c0 0x314dc
call tools\incbin.bat baserom.gba 0x315a4 0x315a8
call tools\incbin.bat baserom.gba 0x315ac 0x315b0
call tools\incbin.bat baserom.gba 0x31832 0x3185c
call tools\incbin.bat baserom.gba 0x31e6a 0x31e6c
call tools\incbin.bat baserom.gba 0x321a2 0x321d0
call tools\incbin.bat baserom.gba 0x327ca 0x327d0
call tools\incbin.bat baserom.gba 0x327d4 0x327e0
call tools\incbin.bat baserom.gba 0x3281c 0x32824
call tools\incbin.bat baserom.gba 0x32d2a 0x32d30
call tools\incbin.bat baserom.gba 0x34330 0x34334
call tools\incbin.bat baserom.gba 0x3455c 0x3456c
call tools\incbin.bat baserom.gba 0x34aa4 0x34aac
call tools\incbin.bat baserom.gba 0x34ba6 0x34bb8
call tools\incbin.bat baserom.gba 0x34bbc 0x34bc0
call tools\incbin.bat baserom.gba 0x34ec0 0x34ec8
call tools\incbin.bat baserom.gba 0x34ed4 0x34ed8
call tools\incbin.bat baserom.gba 0x41828 0x41864
call tools\incbin.bat baserom.gba 0x10f26 0x10f40
call tools\incbin.bat baserom.gba 0x10ffc 0x11014
call tools\incbin.bat baserom.gba 0x12b58 0x12b5a
call tools\incbin.bat baserom.gba 0x1a460 0x1a576
call tools\incbin.bat baserom.gba 0x1a594 0x1a624
call tools\incbin.bat baserom.gba 0x2b7e0 0x2b7e4
call tools\incbin.bat baserom.gba 0x2d63e 0x2d640
call tools\incbin.bat baserom.gba 0x2f5d6 0x2f5e8
call tools\incbin.bat baserom.gba 0x2f92a 0x2f940
call tools\incbin.bat baserom.gba 0x2ff50 0x2ff56
call tools\incbin.bat baserom.gba 0x2ffd8 0x2ffde
call tools\incbin.bat baserom.gba 0x2ffee 0x30000
call tools\incbin.bat baserom.gba 0x3123a 0x31258
call tools\incbin.bat baserom.gba 0x32b8e 0x32b94
call tools\incbin.bat baserom.gba 0x343a2 0x343a4
call tools\incbin.bat baserom.gba 0x41cb4 0x41ce4
call tools\incbin.bat baserom.gba 0x3724f2 0x372574
call tools\incbin.bat baserom.gba 0x37259c 0x3725c0
call tools\incbin.bat baserom.gba 0x42118 0x4212c
call tools\incbin.bat baserom.gba 0x42168 0x42170
echo === compiling source files ===
python "%ROOT%\tools\assets\generate_assets.py" build --rom "%ROOT%\baserom.gba"
if errorlevel 1 exit /b 1
armcpp -c src/color_transforms.cpp -o build/color_transforms.o
echo armcpp_color_transforms_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -Otime -apcs /nointerwork src/sub_0801C62C.c -o build/sub_0801C62C.o
echo tcpp_sub_0801C62C_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -Otime -apcs /nointerwork src/sub_0801C634.c -o build/sub_0801C634.o
echo tcpp_sub_0801C634_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -apcs /interwork src/sub_08043860.c -o build/sub_08043860.o
echo tcpp_sub_08043860_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -Otime -apcs /nointerwork src/sub_0802B960.c -o build/sub_0802B960.o
echo tcpp_sub_0802B960_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -Otime -apcs /nointerwork src/sub_0803431C.c -o build/sub_0803431C.o
echo tcpp_sub_0803431C_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -apcs /interwork src/sub_08045598.c -o build/sub_08045598.o
echo tcpp_sub_08045598_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -apcs /interwork src/sub_08045658.c -o build/sub_08045658.o
echo tcpp_sub_08045658_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -Otime -apcs /nointerwork src/sub_0803E44C.c -o build/sub_0803E44C.o
echo tcpp_sub_0803E44C_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -Otime -apcs /nointerwork src/sub_0803E4A0.c -o build/sub_0803E4A0.o
echo tcpp_sub_0803E4A0_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -apcs /nointerwork src/sub_0802AD88.c -o build/sub_0802AD88.o
echo tcpp_sub_0802AD88_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -apcs /interwork src/sub_08046124.c -o build/sub_08046124.o
echo tcpp_sub_08046124_exit=%ERRORLEVEL%
tcpp -c -cpu ARM7TDMI -Iinclude -O2 -apcs /interwork src/sub_080461F8.c -o build/sub_080461F8.o
echo tcpp_sub_080461F8_exit=%ERRORLEVEL%
echo === building asm files ===
armasm asm/buu.s -o build/buu.o
echo armasm_buu_exit=%ERRORLEVEL%
armasm asm/GBARam.s -o build/GBARam.o
echo armasm_gbaram_exit=%ERRORLEVEL%
armasm asm/ewram.s -o build/ewram.o
echo armasm_ewram_exit=%ERRORLEVEL%
armasm asm/iwram.s -o build/iwram.o
echo armasm_iwram_exit=%ERRORLEVEL%
echo === generating sections ===
python "%ROOT%\tools\gate\emit_all.py"
if errorlevel 1 exit /b 1
echo === compiling generated source ===
armcpp -c build/strings.cpp -o build/strings.o
echo armcpp_strings_exit=%ERRORLEVEL%
armasm asm/rest_of_the_game.s -o build/rest_of_the_game.o
echo armasm_rest_exit=%ERRORLEVEL%
echo === linking and converting ===
armlink build/GBARam.o build/color_transforms.o build/strings.o build/buu.o build/sub_0801C62C.o build/sub_0801C634.o build/sub_08043860.o build/sub_0802B960.o build/sub_0803431C.o build/sub_08045598.o build/sub_08045658.o build/sub_0803E44C.o build/sub_0803E4A0.o build/sub_0802AD88.o build/sub_08046124.o build/sub_080461F8.o build/rest_of_the_game.o build/ewram.o build/iwram.o -noremove -scatter scatter.ld -map -symbols -o build/buu.axf 2> build\buu.map
echo armlink_exit=%ERRORLEVEL%
if errorlevel 1 findstr /i /c:"error:" build\buu.map
fromelf build/buu.axf -bin -o build/output
echo fromelf_exit=%ERRORLEVEL%
python "%ROOT%\tools\symbols\generate_symbols.py"
echo symbols_exit=%ERRORLEVEL%
dir /b build\output
echo DONE
