	CODE16
|loc_08009108|
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LSL      r2, r1, #2
	LDR      r0, [r0, #0x14]
	LDR      r0, [r0, r2]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xe0]
	LDR      r0, [r0, #0x14]
	BL       |List_Append|
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r0, [r0, #4]
	ADD      r5, r2, #0
	ADD      r6, r3, #0
	LDR      r0, [r0, #0x14]
	LSL      r2, r1, #2
	LDR      r0, [r0, r2]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r0]
	ADD      r4, r0, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r5]
	MOV      r0, #0xff
	ADD      r0, #0xa1
	LSL      r1, r1, #8
	STR      r1, [r0, r4]
	LDR      r1, [r5, #4]
	ADD      r0, #4
	LSL      r1, r1, #8
	STR      r1, [r0, r4]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x98]
	STRB     r6, [r4, #0x10]
	LDR      r0, [r0, #0x14]
	ADD      r1, r4, #0
	BL       |List_Append|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
