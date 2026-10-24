	CODE16
|loc_080042FC|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r1, #0
	LDR      r2, [pc, #0x22c]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r4, #0
	MOV      r6, #0x9f
	LDR      r7, [pc, #0x224]
	LSL      r6, r6, #3
|loc_08004310|
	LSL      r0, r4, #3
	ADD      r0, r0, r4
	LSL      r0, r0, #1
	ADD      r1, r0, r7
	MOV      r0, #0x68
	MUL      r0, r4
	ADD      r0, r0, r5
	ADD      r0, r0, r6
	BL       |Stats_LoadRecord|
	ADD      r4, #1
	CMP      r4, #9
	BLT      |loc_08004310|
	POP      {r3, r4, r5, r6, r7, pc}
