; PATH-100-009 / R-RAW-001: the census run 0x08757b58..0x087581cc as LABELED RAW DATA.

	EXPORT	|unk_08757B58|
|unk_08757B58|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x757b58_0x757b5c.extracted
	EXPORT	|unk_08757B5C|
|unk_08757B5C|
; cited by 0x080301A0, 0x080301B8

	INCBIN	baserom.gba_0x757b5c_0x757b64.extracted
	EXPORT	|unk_08757B64|
|unk_08757B64|
; cited by 0x08052086 ldr r0 +0x0

	INCBIN	baserom.gba_0x757b64_0x757ee8.extracted
	EXPORT	|unk_08757EE8|
|unk_08757EE8|
; cited by 0x0803029E INDEXED ldrh [r7 + reg] INDEXED base + register (r2, r2, r7) INDEXED base + register (r0, r0, r1)

	INCBIN  build\endrom\endrom_00757EE8_00758190.bin
	EXPORT	|unk_08758190|
|unk_08758190|
; cited by 0x080303C6 ldr r5 +0x0, 0x080303DE ldr r5 +0x0

	INCBIN	baserom.gba_0x758190_0x758194.extracted
	EXPORT	|unk_08758194|
|unk_08758194|
; cited by 0x0803045A ldr r6 +0x0, 0x080304A2

	INCBIN	baserom.gba_0x758194_0x7581c8.extracted
	EXPORT	|unk_087581C8|
|unk_087581C8|
; cited by 0x0803053A ldr r0 +0x0


	INCBIN	baserom.gba_0x7581c8_0x7581cc.extracted
