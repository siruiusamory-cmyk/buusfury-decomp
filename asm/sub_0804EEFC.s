	CODE16
|sub_0804EEFC|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EF1A|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0xc]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0x10]
	STR      r2, [r0]
	STR      r1, [r0, #0x14]
|loc_0804EF1A|
	POP      {r4, pc}
|sub_0804EF1C|
|unk_0804EF1C|
	INCBIN	baserom.gba_0x4ef1c_0x4ef1e.extracted
|sub_0804EF1E|
	DCW      0x0804
