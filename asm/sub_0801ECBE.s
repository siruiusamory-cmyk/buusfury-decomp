	CODE16
|sub_0801ECBE|
	LSR      r6, r0, #0x20
	LSR      r4, r5, #0x20
	LSR      r2, r6, #1
	DCW      0xf5a5,0x0803
	LSR      r4, r1, #0xf
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	STMIA    r0!, {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x48]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0801ECFA|
	MOV      r0, #1
	POP      {r4, pc}
|loc_0801ECFA|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r4, pc}
|sub_0801ED02|
|unk_0801ED02|
		MOV r0, #0
		BX       lr
