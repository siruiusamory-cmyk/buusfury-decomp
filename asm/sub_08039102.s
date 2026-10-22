	CODE16
|sub_08039102|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803911E|
	LDR      r1, [pc, #0x14]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0803911E|
	POP      {r4, pc}
|sub_08039120|
|unk_08039120|
	INCBIN	baserom.gba_0x39120_0x39122.extracted
