	CODE16
|sub_0803DA78|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r2, #0
	CMP      r0, #0
	BNE      |loc_0803DA8C|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803DAAA|
|loc_0803DA8C|
	ADD      r6, r0, #0
	ADD      r6, #0x10
	LDMIA    r4!, {r1, r2, r3}
	STMIA    r6!, {r1, r2, r3}
	LDMIA    r4!, {r3}
	MOV      r1, #0
	STMIA    r6!, {r3}
	STR      r5, [r0, #0xc]
	STRB     r1, [r0]
	STRB     r1, [r0, #1]
	SUB      r4, #0x10
	LDMIA    r4!, {r1, r2}
	STR      r1, [r0, #4]
	ADD      r2, #0xc
	STR      r2, [r0, #8]
|loc_0803DAAA|
	POP      {r4, r5, r6, pc}
|sub_0803DAAC|
|unk_0803DAAC|
	INCBIN	baserom.gba_0x3daac_0x3dab6.extracted
