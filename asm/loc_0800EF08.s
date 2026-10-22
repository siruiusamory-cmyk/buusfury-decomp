	CODE16
|loc_0800EF08|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
	LDRB     r2, [r0, #0x11]
	LDR      r1, [r0, #0x50]
	LSL      r2, r2, #4
	ADD      r1, r1, r2
	LDRB     r2, [r0, #0x10]
	LSL      r2, r2, #2
	ADD      r1, r1, r2
	LDR      r1, [r1, #4]
	STR      r1, [r0, #0x54]
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x81
	ADD      r2, r1, #0
	SUB      r2, #0x80
	LDR      r3, [r2, #0x78]
	LDR      r2, [r2, #0x7c]
	STR      r2, [r1, #8]
	STR      r3, [r1, #4]
	MOV      r1, #1
	STR      r1, [r0, #0x60]
	STR      r1, [r0, #0x64]
	MOV      r0, #1
	BX       lr
	PUSH     {r4}
	LDRB     r3, [r1, #0x11]
	LDR      r2, [r1, #0x50]
	LDR      r4, [r1, #0x58]
	LSL      r3, r3, #4
	ADD      r2, r2, r3
	LDRB     r3, [r1, #0x10]
	LDRB     r4, [r4, #8]
	LSL      r3, r3, #2
	ADD      r2, r2, r3
	LDR      r3, [r2, #4]
	LDR      r2, [r1, #0x6c]
	LDR      r1, [r1, #0x70]
	ADD      r2, r2, r4
	ADD      r4, r3, #0
	MOV      r3, #5
	LDRSB    r4, [r4, r3]
	SUB      r2, #8
	ADD      r1, r1, r4
	STR      r1, [r0, #4]
	STR      r2, [r0]
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x254]
	ADD      r4, r0, #0
	ADD      sp, r3
	MOV      r2, #0
	STR      r2, [sp, #0x24]
	LDR      r0, [pc, #0x244]
	MOV      r3, #1
	SUB      r0, #8
	LDR      r0, [r0, #4]
	LSL      r3, r3, #0xc
	ADD      r3, sp
	ADD      r0, #0x80
	STR      r0, [r3, #0x40]
	ADD      r2, r4, #0
	ADD      r5, r1, #0
	LDR      r1, [r0, #0x10]
	ADD      r2, #0xff
	ADD      r2, #0x81
	STR      r2, [r3, #0x3c]
	CMP      r1, #0
	LDR      r0, [pc, #0x230]
	BEQ      |loc_0800F02C|
	LDR      r1, [r5, #8]
	CMP      r1, #0x10
	BLT      |Math_Divide3|
	MOV      r0, #0
	LDR      r3, [pc, #0x228]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
