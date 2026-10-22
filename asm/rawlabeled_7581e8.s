; PATH-100-009 / R-RAW-001: the census run 0x087581e8..0x0875916c as LABELED RAW DATA.

	EXPORT	|unk_087581E8|
|unk_087581E8|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x7581e8_0x7581ec.extracted
	EXPORT	|unk_087581EC|
|unk_087581EC|
; cited by 0x0805271E ldr r0 +0x4

	DCD	|unk_03003300|
	DCD	|unk_03001C4C|
	EXPORT	|unk_087581F4|
|unk_087581F4|
; cited by 0x08030A0C, 0x08030A54 ldr r1 +0x0

	INCBIN	baserom.gba_0x7581f4_0x7581fc.extracted
	EXPORT	|unk_087581FC|
|unk_087581FC|
; cited by 0x08030AE0 INDEXED ldrb [r0 + reg] INDEXED base + register (r1, r1, r2) INDEXED base + register (r1, r0, r1), 0x08030AF0 INDEXED base + register (r1, r1, r2) INDEXED base + register (r1, r0, r1)

	INCBIN	baserom.gba_0x7581fc_0x7585ec.extracted
	EXPORT	|unk_087585EC|
|unk_087585EC|
; cited by 0x080FB3F6

	INCBIN	baserom.gba_0x7585ec_0x759154.extracted
	EXPORT	|unk_08759154|
|unk_08759154|
; cited by 0x08030F62 ldr r0 +0xc, 0x08030F86 ldr r0 +0xc


	DCD	|unk_03003300|
	DCD	|unk_03001C4C|
	DCD	|unk_03001068|
	DCD	|unk_030019A4|
	DCD	|unk_03001A68|
	DCD	|unk_0806EE6C|
