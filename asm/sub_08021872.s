	CODE16
|sub_08021872|
	LSR      r2, r6, #1
	LDR      r2, [pc, #0x33c]
	MOV      r0, #0
	STRB     r0, [r2]
	LDR      r1, [pc, #0x33c]
	STRB     r0, [r2, #1]
	LDR      r3, [r1, #0x10]
	STRH     r0, [r3, #2]
	LDR      r3, [r1, #0x10]
	STRH     r0, [r3, #4]
	LDR      r3, [r1, #0x10]
	STRH     r0, [r3, #6]
	LDR      r3, [r1, #0x10]
	ADD      r3, #0xff
	ADD      r3, #0x81
	STRH     r0, [r3, #0xc]
	LDR      r3, [r1, #0x14]
	STRH     r0, [r3, #2]
	LDR      r3, [r1, #0x14]
	STRH     r0, [r3, #4]
	LDR      r3, [r1, #0x14]
	STRH     r0, [r3, #6]
	LDR      r1, [r1, #0x14]
	ADD      r1, #0xff
	ADD      r1, #0x81
	STRH     r0, [r1, #0xc]
	MOV      r0, #1
	STR      r0, [r2, #8]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	LDR      r0, [pc, #0x300]
	MOV      r6, #1
	MOV      r4, #0
	LSL      r6, r6, #9
	SUB      sp, #0x14
	STR      r4, [r0, #8]
	ADD      r2, r6, #0
	MOV      r1, #0
	LDR      r0, [pc, #0x2f8]
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r2, r6, #0
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	LSL      r5, r6, #0x11
	STRH     r4, [r5]
	STRH     r4, [r5, #0x10]
	STRH     r4, [r5, #0x12]
	STRH     r4, [r5, #0x14]
	STRH     r4, [r5, #0x16]
	STRH     r4, [r5, #0x18]
	STRH     r4, [r5, #0x1a]
	STRH     r4, [r5, #0x1c]
	LDR      r0, [pc, #0x2d8]
	STRH     r4, [r5, #0x1e]
	STRH     r0, [r5, #0xa]
	MOV      r1, #0
	LSL      r0, r0, #0x19
	LDR      r2, [pc, #0x2d4]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, #0x14
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	MOV      r2, #1
	STR      r4, [sp, #4]
	STR      r4, [sp, #8]
	LDR      r1, [pc, #0x2c0]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LSR      r2, r5, #0x11
	MOV      r0, #5
	LSL      r0, r0, #0x18
	STRH     r6, [r5]
	LDR      r1, [pc, #0x2b8]
	BL       |inc_0x049120_0x055620| + 0x24
	LSR      r2, r5, #0x11
	LDR      r1, [pc, #0x2b0]
	LDR      r0, [pc, #0x29c]
	BL       |inc_0x049120_0x055620| + 0x24
	LDR      r0, [pc, #0x2ac]
	STRH     r4, [r0, #0x10]
	ADD      r0, r7, #0
	BEQ      |loc_08021936|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08021936|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_0802193A|
|unk_0802193A|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r1, [pc, #0x294]
		MOV r0, #0
		SUB sp, #0xec
		STR r0, [r1]
		LDR r1, [pc, #0x290]
		ADD r5, r4, #4
		ADD r6, r5, #4
		STR r0, [r1]
		B        |loc_08021B98|
