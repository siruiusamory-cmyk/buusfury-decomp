	CODE16
|sub_08027424|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802743A|
	LDR      r1, [pc, #0x4c]
	STR      r1, [r0]
	MOV      r1, #0
	STRB     r1, [r0, #4]
|loc_0802743A|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xec28
	MOV      r0, #0x28
|loc_08027444|
	STRB     r0, [r4, #8]
	POP      {r4, pc}
|loc_08027448|
	PUSH     {r3, lr}
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0xec4e
	POP      {r3, pc}
|loc_08027454|
	ADD      r0, #0xff
	ADD      r0, #0x81
	LDR      r0, [r0, #0xc]
	LDR      r0, [r0]
	BX       lr
|loc_0802745E|
	ADD      r0, #0xff
	ADD      r0, #0x81
	LDR      r0, [r0, #0xc]
	LDR      r0, [r0, #4]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [pc, #0xc]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, pc}
	LSL      r0, r0, #0
	BCC      |loc_08027378|
	LSR      r4, r6, #1
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	LDMIA    r6!, {r3, r4, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0xe0
	LSR      r4, r0, #0x20
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	PUSH     {r3, lr}
	LDRB     r1, [r2, #4]
	ADD      r1, #1
	STRB     r1, [r2, #4]
	LSL      r1, r1, #0x1b
	LSR      r1, r1, #0x1d
	LDR      r2, [pc, #0x18]
	LSL      r1, r1, #2
	LDR      r1, [r2, r1]
	LDR      r2, [r0, #0x38]
	CMP      r2, r1
	BEQ      |loc_080274A4|
	BL       |inc_0x0158_0x143f2| + 0xed74
|loc_080274A4|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	LSL      r0, r0, #0
	BCC      |loc_08027574|
	LSR      r4, r6, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_080274D0|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080274D0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
