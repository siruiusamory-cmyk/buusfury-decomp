	CODE16
|sub_0800B7B0|
	ADD      r1, r0, r1
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x2234
	LDR      r0, [r6]
	MOV      r3, #0x88
	ADD      r1, r0, #0
	ADD      r1, #8
	STR      r1, [r6]
	LDR      r1, [pc, #0x58]
	STR      r1, [r0]
	LDR      r2, [r4, #0x14]
	LDR      r2, [r2, #0x28]
	SUB      r2, r3, r2
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x18
	ORR      r1, r2
	STR      r1, [r0]
	LDRH     r1, [r4, #0xc]
	LDR      r2, [r0, #4]
	LSR      r2, r2, #0xa
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x16
	LSL      r2, r2, #0xa
	ORR      r1, r2
	MOV      r2, #3
	LSL      r2, r2, #0xa
	BIC      r1, r2
	MOV      r2, #1
	LSL      r2, r2, #0xa
	ADD      r1, r1, r2
	STR      r1, [r0, #4]
	ADD      sp, #0xc
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
|loc_0800B7F6|
	DCW      0x0000
	DCW      0x1c90,0x0807,0x0000,0x0601,0x44d8,0x0871,0x2000,0x405c
	DCW      0x9680,0x0804,0xb4d8,0x0804,0xf70d
|loc_0800B812|
	LSR      r3, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	LSL      r5, r0, #0x11
	LSL      r0, r0, #0
	STR      r0, [r0]
	STRH     r0, [r1]
	CMP      r1, #3
	BLT      |sub_0800B828|
	MOV      r0, #2
	BX       lr
