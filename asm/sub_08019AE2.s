	CODE16
|sub_08019AE2|
	LSL      r0, r0, #0
	PUSH     {r2, r4, r6}
	LSR      r4, r0, #0x20
	ADD      r7, #0xc
	LSR      r1, r6, #1
	LDR      r4, [sp, #0x100]
	LSR      r1, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r7, #0xcc
	LSR      r1, r6, #1
	STRH     r0, [r5, #4]
	LSR      r3, r5, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x200]
	LDR      r6, [pc, #0x204]
	STR      r0, [r4]
	STRH     r1, [r4, #0xe]
	ADD      r5, r1, #0
	ADD      r7, r2, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x110f4
	ADD      r3, r0, #1
	BNE      |loc_08019B2E|
	ADD      r1, r5, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r1, r5, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x110f4
|loc_08019B2E|
	STRH     r0, [r4, #0xc]
	LDR      r0, [pc, #0x1e0]
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r4, #0x14]
	STR      r7, [r4, #0x1c]
	CMP      r7, #0
	BEQ      |loc_08019B4A|
	LDRB     r0, [r7, #0x10]
	ADD      r7, #0xff
	ADD      r7, #0xc1
	STRB     r0, [r4, #0x10]
	LDR      r0, [r7, #0x10]
	STRB     r0, [r4, #0x11]
|loc_08019B4A|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08019B4E|
	PUSH     {r4, r5}
	LDR      r1, [r0, #0x20]
	MOV      r3, #0
	ASR      r2, r1, #8
	LDR      r1, [r0, #0x18]
	LDRSB    r4, [r1, r3]
	MOV      r3, #1
	SUB      r4, r2, r4
	STR      r4, [r0, #0x28]
	LDR      r2, [r0, #0x24]
	LDRSB    r5, [r1, r3]
	ASR      r2, r2, #8
	SUB      r5, r2, r5
	STR      r5, [r0, #0x2c]
	LDRB     r3, [r1, #2]
	LDRB     r1, [r1, #3]
	ADD      r3, r4, r3
	ADD      r1, r5, r1
	STR      r1, [r0, #0x34]
	STR      r2, [r0, #4]
	STR      r3, [r0, #0x30]
	POP      {r4, r5}
	BX       lr
	LDR      r1, [pc, #0x190]
	LDR      r2, [pc, #0x198]
	LDR      r1, [r1, #4]
	LDR      r2, [r2]
	ADD      r1, #0x18
	CMP      r2, #0
	BEQ      |loc_08019B8E|
	MOV      r0, #1
	BX       lr
|loc_08019B8E|
	LDRB     r2, [r0, #0x10]
	CMP      r2, #0
	BEQ      |loc_08019BAC|
	CMP      r2, #1
	BEQ      |sub_08019BBC|
	CMP      r2, #2
	BEQ      |sub_08019BCC|
	CMP      r2, #3
	BNE      |loc_08019BE0|
	LDR      r0, [r0, #0x28]
	LDR      r1, [r1, #8]
	CMP      r0, r1
	BGE      |loc_08019BDC|
	MOV      r0, #1
	BX       lr
|loc_08019BAC|
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r1, #0xc]
	CMP      r0, r1
	BGE      |sub_08019BB8|
	MOV      r0, #1
	BX       lr
