	CODE16
|loc_08009B12|
	PUSH     {r4, r5, lr}
	LDR      r3, [pc, #0x204]
	ADD      r4, r0, #0
	ADD      sp, r3
	MOV      r3, #0
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0, #4]
	ADD      r5, sp, #4
	LSL      r1, r1, #2
	ADD      r0, r0, r1
	LDR      r1, [r0, #4]
	ADD      r1, #4
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620|
	LDR      r0, [r4, #4]
	LDRB     r1, [r0, #1]
	LDRH     r0, [r0, #2]
	LSL      r2, r1, #6
	MOV      r1, #3
	LSL      r1, r1, #0x19
	LSL      r0, r0, #6
	ADD      r0, r0, r1
	ADD      r1, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r3, [pc, #0x1d8]
	ADD      sp, r3
	POP      {r4, r5, pc}
|sub_08009B4C|
|unk_08009B4C|
	INCBIN	baserom.gba_0x9b4c_0x9b80.extracted
