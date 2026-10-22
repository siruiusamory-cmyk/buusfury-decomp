	CODE16
|loc_080400EE|
	PUSH     {r4, r5, r6, r7}
	LDR      r6, [pc, #0x12c]
	LDR      r5, [pc, #0x12c]
	MOV      r7, #0
	MOV      r1, #0
	LDR      r2, [pc, #0x13c]
	ADD      r6, #0xc
	ADD      r5, #0x18
|loc_080400FE|
	LSL      r4, r1, #1
	STRH     r7, [r6, r4]
	MOV      r0, #0
|loc_08040104|
	LSL      r3, r0, #2
	ADD      r3, r3, r5
	ADD      r0, #1
	CMP      r0, #2
	STRH     r2, [r3, r4]
	BLT      |loc_08040104|
	ADD      r1, #1
	CMP      r1, #2
	BLT      |loc_080400FE|
	POP      {r4, r5, r6, r7}
	BX       lr
	LDR      r0, [pc, #0x108]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	LDR      r1, [pc, #0xf8]
	ADD      r1, #0xc
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LDR      r0, [pc, #0xf0]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	LDR      r3, [pc, #0xe8]
	LDR      r1, [r0]
	ADD      r3, #0x18
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	LDR      r1, [pc, #0xdc]
	LDR      r1, [r1, #0x10]
	LSL      r1, r1, #2
	ADD      r1, r1, r3
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
