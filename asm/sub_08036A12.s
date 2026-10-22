	CODE16
|sub_08036A12|
	LSR      r5, r6, #1
	SUB      sp, #0
	LSR      r4, r0, #0x20
	ADD      r5, sp, #0xe0
	LSR      r4, r0, #0x20
	PUSH     {r4, r5}
	LDR      r1, [r0, #0x38]
	MOV      r3, #0
	LDRSB    r4, [r1, r3]
	LDR      r2, [r0, #0x10]
	MOV      r3, #1
	SUB      r2, r2, r4
	STR      r2, [r0, #0x20]
	LDRSB    r5, [r1, r3]
	LDR      r4, [r0, #0x14]
	SUB      r4, r4, r5
	STR      r4, [r0, #0x24]
	LDRB     r3, [r1, #2]
	LDRB     r1, [r1, #3]
	ADD      r2, r2, r3
	ADD      r1, r4, r1
	STR      r1, [r0, #0x2c]
	STR      r2, [r0, #0x28]
	POP      {r4, r5}
	BX       lr
