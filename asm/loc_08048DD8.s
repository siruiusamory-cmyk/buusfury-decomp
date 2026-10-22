	CODE16
|loc_08048DD8|
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048DE6|
|unk_08048DE6|
	INCBIN	baserom.gba_0x48de6_0x48dea.extracted
