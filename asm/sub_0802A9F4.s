	CODE16
|sub_0802A9F4|
|unk_0802A9F4|
; cited by 0x0802A83A (a pc-relative load targets 0x0802A9F8)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x2a9f8_0x2aa06.extracted
|sub_0802AA06|
|unk_0802AA06|
	INCBIN	baserom.gba_0x2aa06_0x2aa0a.extracted
	LSL      r1, r0, #0x18
	LDR      r0, [pc, #0x24]
	ADD      r1, #0xff
	LDR      r0, [r0, #4]
	ADD      r1, #0xc1
	STR      r0, [r1, #0x28]
	MOV      r0, #0
	BX       lr
|sub_0802AA1A|
|unk_0802AA1A|
	INCBIN	baserom.gba_0x2aa1a_0x2aa1e.extracted
