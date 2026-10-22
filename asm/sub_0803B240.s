	CODE16
|sub_0803B240|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [pc, #0x90]
	SUB      sp, #0x28
	MOV      r0, #0
	STRB     r0, [r1]
	ADD      r1, r4, #0
	ADD      r0, sp, #8
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x14]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r1, r1, #1
	ASR      r0, r0, #1
	STR      r1, [sp]
	STR      r1, [sp, #0x18]
	ADD      r1, #2
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x1c]
	SUB      r0, #0x11
	STR      r0, [sp, #4]
	STR      r1, [sp]
	STR      r1, [sp, #0x20]
	STR      r0, [sp, #0x24]
	ADD      r2, r4, #0
	MOV      r0, #0
	ADD      r1, sp, #0x20
	BL       |loc_0803AEA8|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x54]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x28
	POP      {r4, pc}
	LDR      r0, [pc, #0x40]
	LDRB     r0, [r0]
	CMP      r0, #3
	BEQ      |loc_0803B2A0|
	CMP      r0, #1
	BNE      |sub_0803B2A4|
|loc_0803B2A0|
	MOV      r0, #1
	BX       lr
