	CODE16
|sub_08029FE6|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802A002|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0802A002|
	POP      {r4, pc}
|sub_0802A004|
|unk_0802A004|
	INCBIN	baserom.gba_0x2a004_0x2a006.extracted
