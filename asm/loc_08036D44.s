	CODE16
|loc_08036D44|
|unk_08036D44|
; cited by 0x08036A5C (a pc-relative load targets 0x08036D68)
		CMP r7, #0
		BEQ      |loc_08036D4A|
		MOV r4, #0
|loc_08036D4A|
		ADD r2, r4, #0
		ADD r0, r6, #0
		LDR r1, [r5, #0x28]
		BL       |loc_08009930|
		ADD r2, r4, #0
		ADD r0, sp, #0xc
		LDR r1, [r5, #0x30]
		BL       |loc_08009930|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1af2
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1af2
	INCBIN  baserom.gba_0x36d66_0x36d82.extracted
|sub_08036D82|
|unk_08036D82|
	INCBIN  baserom.gba_0x36d82_0x36d84.extracted
		PUSH {r4, r5, r6, lr}
	LDR      r5, [pc, #0xcc]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4cc4
	LDR      r0, [r5, #4]
	LDR      r2, [r4, #8]
	ADD      r6, r0, #0
	LSL      r2, r2, #0xa
	STR      r2, [r0, #8]
	LDR      r0, [r4, #8]
	ADD      r6, #0x10
	BL       |inc_0x049120_0x055620| + 0xb9bc
	LDR      r1, [pc, #0xb4]
	BL       |inc_0x049120_0x055620| + 0xba1c
	BL       |inc_0x049120_0x055620| + 0xb894
	BL       |inc_0x049120_0x055620| + 0x78
	BL       |inc_0x049120_0x055620| + 0xa1c8
	LDR      r1, [pc, #0xa4]
	BL       |inc_0x049120_0x055620| + 0xba1c
	MOV      r1, #0x89
	LSL      r1, r1, #0x17
	BL       |inc_0x049120_0x055620| + 0xba1c
	BL       |inc_0x049120_0x055620| + 0xb944
	MOV      r1, #0x11
	LSL      r1, r1, #0xa
	ADD      r0, r0, r1
	STR      r0, [r6]
	LDR      r0, [r5, #4]
	BL       |sub_0802ed98|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x78]
	ADD      r5, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4cc4
	LDR      r1, [r5, #8]
	LDR      r0, [r4, #4]
	LSL      r1, r1, #0xa
	STR      r1, [r0, #0xc]
	LDR      r0, [r4, #4]
	BL       |sub_0802ed98|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x5c]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4cc4
	LDR      r0, [r5, #4]
	ADD      r0, #0x80
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_08036E1E|
	LDR      r1, [r4, #8]
	LDR      r0, [r5, #4]
	LDR      r2, [r4, #0xc]
	LSL      r1, r1, #0xa
	STMIA    r0!, {r1}
	LSL      r2, r2, #0xa
	STR      r2, [r0]
	LDR      r0, [r5, #4]
	BL       |sub_0802ed98|
	POP      {r3, r4, r5, pc}
