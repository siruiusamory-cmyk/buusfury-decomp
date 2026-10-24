; PATH-100-006 / R-RAW-001: the census run 0x08732350..0x08732384 as LABELED RAW DATA.

	EXPORT	|unk_08732350|
|unk_08732350|
; cited by 0x080250DE ldm r0 +0x0 INDEXED base + register (r0, sp, r0)

	INCBIN	baserom.gba_0x732350_0x732360.extracted
	EXPORT	|unk_08732360|
|unk_08732360|
; cited by 0x08025D48 ldr r3 +0x0 INDEXED base + register (r2, r0, r2) ldr r4 +0x0

	DCD	|g_KeyState|
	DCD	|unk_03001C4C|
	DCD	|unk_03001068|
	DCD	|unk_030019A4|
	DCD	|unk_0300197C|
	EXPORT	|unk_08732374|
|unk_08732374|
; cited by 0x08025E7C ldr r0 +0x8 INDEXED base + register (r1, r1, r2) ldr r0 +0xc INDEXED ldr [r1 + reg], 0x08025F26 ldr r1 +0xc INDEXED ldr [r1 + reg], 0x08025FAE ldr r5 +0x0, 0x0802604C ldr r6 +0x4 INDEXED base + register (r6, sp, r6) INDEXED base + register (r0, sp, r0) (+2 more sites)


	DCD	|g_KeyState|
	DCD	|unk_03001C4C|
	DCD	|unk_03001068|
	DCD	|unk_0806EE6C|
