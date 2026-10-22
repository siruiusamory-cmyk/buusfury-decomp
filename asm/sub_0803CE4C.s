	CODE16
|sub_0803CE4C|
	MOV      r0, #0
	SUB      r0, r6, r0
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803CE62|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
|loc_0803CE62|
	POP      {r3, pc}
|sub_0803CE64|
|unk_0803CE64|
	INCBIN	baserom.gba_0x3ce64_0x3ce66.extracted
