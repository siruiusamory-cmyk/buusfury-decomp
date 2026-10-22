; PATH-100-005 / R-RAW-001: the census run 0x08752ef0..0x08754910 as LABELED RAW DATA.

	EXPORT	|unk_08752EF0|
|unk_08752EF0|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x752ef0_0x752f8c.extracted
	EXPORT	|unk_08752F8C|
|unk_08752F8C|
; cited by 0x0805196A ldr r0 +0x0

	INCBIN	baserom.gba_0x752f8c_0x753008.extracted
	EXPORT	|unk_08753008|
|unk_08753008|
; cited by 0x0802BC58 ldr r6 +0x0 INDEXED base + register (r1, r1, r2) INDEXED base + register (r0, r0, r7) INDEXED base + register (r5, r0, r1)

	INCBIN	baserom.gba_0x753008_0x753a08.extracted
	EXPORT	|unk_08753A08|
|unk_08753A08|
; cited by 0x0802BC76 ldr r6 +0x0 INDEXED base + register (r1, r1, r2) INDEXED base + register (r0, r0, r7) INDEXED base + register (r5, r0, r1)

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	EXPORT	|unk_08753A10|
|unk_08753A10|
; cited by 0x0802BD9E ldr r0 +0x0

	INCBIN	baserom.gba_0x753a10_0x753a14.extracted
	EXPORT	|unk_08753A14|
|unk_08753A14|
; cited by 0x0802BDCC ldr r2 +0x0

	INCBIN	baserom.gba_0x753a14_0x753a18.extracted
	EXPORT	|unk_08753A18|
|unk_08753A18|
; cited by 0x0805192E ldr r0 +0x0

	INCBIN	baserom.gba_0x753a18_0x7548e8.extracted
	EXPORT	|unk_087548E8|
|unk_087548E8|
; cited by 0x0802C0BA ldr r5 +0x4 INDEXED base + register (r0, r0, r1) INDEXED base + register (r1, r1, r2) ldr r5 +0x0, 0x0802C0E2 INDEXED base + register (r0, r0, r1) INDEXED base + register (r1, r1, r2) INDEXED base + register (r0, r0, r4)


	INCBIN	baserom.gba_0x7548e8_0x754910.extracted
