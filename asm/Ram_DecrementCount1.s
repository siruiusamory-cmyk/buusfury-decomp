	CODE16
|Ram_DecrementCount1|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	LDR      r1, [pc, #0xfc]
	ADD      r5, r0, #0
	LDR      r0, [r1, #4]
	MOV      r2, #0
	SUB      r0, #1
	STR      r0, [r1, #4]
	LDR      r0, [pc, #0xf4]
	MOV      r1, #0x10
	LDR      r0, [r0]
	BL       |loc_08011C0C|
	CMP      r4, #0
	BEQ      |loc_080124F6|
	ADD      r0, r5, #0
	BL       |GBARam_Free|
|loc_080124F6|
	POP      {r3, r4, r5, pc}
