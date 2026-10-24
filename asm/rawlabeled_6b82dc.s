; PATH-100-006 / R-RAW-001: the census run 0x086b82dc..0x086b880c as LABELED RAW DATA.

	EXPORT	|unk_086B82DC|
|unk_086B82DC|
; cited by 0x08016FC6 ldr r1 +0x4 INDEXED base + register (r0, r1, r0), 0x0801707A ldr r3 +0x0 ldr r5 +0x4 INDEXED base + register (r5, r5, r4), 0x080170D2 ldr r0 +0x0

	DCD	|g_KeyState|
	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	DCD	|unk_03001068|
	EXPORT	|unk_086B82EC|
|unk_086B82EC|
; cited by 0x0802E8FC INDEXED base + register (r0, r0, r1)

	INCBIN	baserom.gba_0x6b82ec_0x6b87fc.extracted
	EXPORT	|unk_086B87FC|
|unk_086B87FC|
; cited by 0x08017194 ldr r2 +0xc, 0x080171D8 ldr r6 +0x8, 0x08017370 ldr r7 +0xc


	DCD	|g_KeyState|
	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	DCD	|unk_03001068|
