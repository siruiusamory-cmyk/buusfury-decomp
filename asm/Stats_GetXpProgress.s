	CODE16
|Stats_GetXpProgress|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x24]
	ADD      r5, r1, #0
	LDR      r6, [pc, #0x2c0]
	MOV      r1, #9
	LSL      r1, r1, #6
	ADD      r1, r6, r1
	LDR      r1, [r1, #0x18]
	CMP      r0, r1
	BCC      |loc_08013658|
	ADD      r0, r5, #0
	POP      {r4, r5, r6, pc}
|loc_08013658|
	ADD      r0, r4, #0
	BL       |Stats_GetLevel|
	LDR      r1, [r4, #0x24]
	LSL      r0, r0, #2
	ADD      r2, r0, r6
	SUB      r2, #0xff
	SUB      r2, #1
	LDR      r0, [r2, #0x38]
	LDR      r2, [r2, #0x3c]
	SUB      r1, r1, r0
	SUB      r0, r2, r0
	MUL      r1, r5
	BL       |inc_0x046118_0x049114| + 0xe18
	POP      {r4, r5, r6, pc}
