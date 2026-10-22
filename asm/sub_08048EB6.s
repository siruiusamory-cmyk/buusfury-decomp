	CODE16
|sub_08048EB6|
	LSR      r4, r0, #0x20
	ADD      r4, #0x90
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048ECA|
|unk_08048ECA|
; cited by 0x08048EBC (a pc-relative load targets 0x08048ECC)
	INCBIN	baserom.gba_0x48eca_0x48f54.extracted
|loc_08048F54|
|unk_08048F54|
; cited by 0x08048E34 (a pc-relative load targets 0x08048FF8)
	INCBIN	baserom.gba_0x48f54_0x49010.extracted
|loc_08049010|
|unk_08049010|
; cited by 0x08048ED0 (a pc-relative load targets 0x080490A4)
	INCBIN	baserom.gba_0x49010_0x49114.extracted
