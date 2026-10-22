; PATH-100-005 / R-RAW-001: the census run 0x086fc260..0x086fda00 as LABELED RAW DATA.

	EXPORT	|unk_086FC260|
|unk_086FC260|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x6fc260_0x6fccc0.extracted
	EXPORT	|unk_086FCCC0|
|unk_086FCCC0|
; cited by 0x080183EA ldr r4 +0x0, 0x08018482 ldr r4 +0x0 ldr r4 +0x4

	DCD	|unk_03001C4C|
	DCD	|unk_0300197C|
	EXPORT	|unk_086FCCC8|
|unk_086FCCC8|
; cited by 0x080184E6 ldr r0 +0x0 INDEXED base + register (r0, r0, r1), 0x08018514 ldr r0 +0x0 INDEXED base + register (r0, r0, r1), 0x08018572 ldr r0 +0x0 ldr r7 +0x0, 0x08018580 ldr r0 +0x0 ldr r7 +0x0 (+6 more sites)

	INCBIN	baserom.gba_0x6fccc8_0x6fd9d0.extracted
	EXPORT	|unk_086FD9D0|
|unk_086FD9D0|
; cited by 0x0804E8E4


	INCBIN	baserom.gba_0x6fd9d0_0x6fda00.extracted
