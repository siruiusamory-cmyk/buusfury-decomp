	CODE16
|sub_08036E2A|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x24]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4cc4
	LDR      r1, [r4, #8]
	LDR      r2, [r4, #0xc]
	LDR      r0, [r5, #4]
	LSL      r1, r1, #0xa
	LSL      r2, r2, #0xa
	STMIA    r0!, {r1, r2}
	LDR      r1, [r4, #0x10]
	SUB      r0, #8
	LSL      r1, r1, #0xa
	STR      r1, [r0, #8]
	LDR      r0, [r5, #4]
	BL       |sub_0802ed98|
	POP      {r3, r4, r5, pc}
|loc_08036E52|
	DCW      0x0000
	DCW      0xf7f4,0x0875,0xe762,0x3bb7,0xf9db
|loc_08036E5E|
	TST      r2, r4
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x74]
	ADD      r3, r2, r1
	MOV      r2, #0
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98e
	MOV      r0, #1
	POP      {r3, pc}
|sub_08036E76|
|unk_08036E76|
		LDR r0, [pc, #0x28]
		BX       lr
