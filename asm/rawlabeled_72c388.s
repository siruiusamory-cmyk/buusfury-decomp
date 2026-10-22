; PATH-100-005 / R-RAW-001: the census run 0x0872c388..0x087315e8 as LABELED RAW DATA.

	EXPORT	|unk_0872C388|
|unk_0872C388|
; cited by 0x080244BE ldr r0 +0x0

	INCBIN	baserom.gba_0x72c388_0x72c38c.extracted
	EXPORT	|unk_0872C38C|
|unk_0872C38C|
; cited by 0x08024602 ldr r5 +0x0 ldr r5 +0x4, 0x0802464A ldr r0 +0x0, 0x08024666 ldr r5 +0x0 ldr r5 +0x4

	DCD	|unk_03004A8C|
	DCD	|unk_03002F58|
	EXPORT	|unk_0872C394|
|unk_0872C394|
; cited by 0x0802497C ldr r5 +0x0 INDEXED base + register (r0, r0, r1), 0x080249E4 ldr r4 +0x0

	INCBIN	baserom.gba_0x72c394_0x72c3b8.extracted
	EXPORT	|unk_0872C3B8|
|unk_0872C3B8|
; cited by 0x080249AA

	INCBIN	baserom.gba_0x72c3b8_0x72c461.extracted
	EXPORT	|unk_0872C461|
|unk_0872C461|
; cited by 0x083CC164 strh r1 +0x24 INDEXED base + register (r0, r0, r1)

	INCBIN	baserom.gba_0x72c461_0x72d6b8.extracted
	EXPORT	|unk_0872D6B8|
|unk_0872D6B8|
; cited by 0x0802472C INDEXED base + register (r0, r0, r1) INDEXED ldr [r6 + reg] INDEXED base + register (r1, r5, r6) INDEXED ldrsh [r5 + reg]

	INCBIN	baserom.gba_0x72d6b8_0x7315a8.extracted
	EXPORT	|unk_087315A8|
|unk_087315A8|
; cited by 0x0801BF76 INDEXED base + register (r2, r0, r1)

	INCBIN	baserom.gba_0x7315a8_0x7315d8.extracted
	EXPORT	|unk_087315D8|
|unk_087315D8|
; cited by 0x08024D98 ldr r0 +0xc INDEXED ldr [r6 + reg], 0x08024E44 ldr r0 +0x8 INDEXED base + register (r0, r0, r1)


	DCD	|unk_03003300|
	DCD	|unk_03001C4C|
	DCD	|unk_03001068|
	DCD	|unk_0806E050|
