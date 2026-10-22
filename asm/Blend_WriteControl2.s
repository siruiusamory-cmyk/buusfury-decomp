	CODE16
|Blend_WriteControl2|
	LSL      r0, r0, #0
	STR      r4, [r3, #0x1c]
	LSR      r5, r0, #0x20
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	STR      r6, [sp, #0x3f0]
	LSR      r4, r0, #0x20
	LSL      r0, r0, #8
	LSL      r0, r0, #0x14
	ADD      r0, r2, r4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0x3d0]
	SUB      sp, #0x10
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r5, #1
	LSL      r5, r5, #0x1a
	MOV      r4, #0
	STRH     r4, [r5]
	STRH     r4, [r5, #0x10]
	STRH     r4, [r5, #0x12]
	STRH     r4, [r5, #0x14]
	STRH     r4, [r5, #0x16]
	STRH     r4, [r5, #0x18]
	STRH     r4, [r5, #0x1a]
	STRH     r4, [r5, #0x1c]
	LDR      r0, [pc, #0x3a8]
	STRH     r4, [r5, #0x1e]
	STRH     r4, [r0, #0x10]
	ADD      r0, r6, #0
	BL       |sub_08005740|
	LDR      r0, [pc, #0x3a0]
	MOV      r1, #0
	STRH     r0, [r5, #0xa]
	MOV      r0, #0x49
	LSL      r0, r0, #6
	STRH     r0, [r5]
	MOV      r0, #3
	LSL      r0, r0, #0x19
	LDR      r2, [pc, #0x394]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #8]
	MOV      r0, #0x14
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	MOV      r2, #1
	STR      r4, [sp]
	STR      r4, [sp, #4]
	LDR      r1, [pc, #0x380]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LSR      r2, r5, #0x11
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x378]
	BL       |inc_0x049120_0x055620| + 0x24
	LSR      r2, r5, #0x11
	LDR      r1, [pc, #0x370]
	LDR      r0, [pc, #0x35c]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	BL       |loc_080058C6|
	MOV      r0, #0
	POP      {r3, pc}
	PUSH     {r4, lr}
	SUB      sp, #0x10
	ADD      r4, r0, #0
	BL       |sub_08005740|
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r2, #6
	ADD      r1, r4, #0
	MOV      r3, #8
	MOV      r0, #0
	BL       |loc_08013E64|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r2, #8
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #7
	STR      r0, [sp, #4]
	MOV      r2, #7
	ADD      r1, r4, #0
	MOV      r3, #0xd0
	MOV      r0, #0
	BL       |loc_08013E64|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	LDRH     r0, [r2]
	MOV      r1, #0x41
	LSL      r1, r1, #6
	ORR      r0, r1
	STRH     r0, [r2]
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_08005ABE|
|unk_08005ABE|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		CMP r2, #8
		SUB sp, #0xc
		BHS      |loc_08005AD2|
		DCW     0xA302
		ADD r3, r3, r2
		LDRH r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
|loc_08005AD2|
		B        |loc_08005E36|
	INCBIN  baserom.gba_0x5ad4_0x5bc0.extracted
		LDR r0, [pc, #0x214]
		MOV r1, #0x10
		STR r0, [r4]
		LSL r0, r1, #6
		ADD r0, r4, r0
		STR r1, [r0, #8]
		STR r5, [r0, #4]
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x11c
		MOV r0, #4
		DCW     0xF037
		DCW     0xFCEF
		CMP r0, #0
		BEQ      |loc_08005BE2|
		LDR r1, [pc, #0x1fc]
		STR r1, [r0]
|loc_08005BE2|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r1, #0x45
		LDR r0, [r6, #0x10]
		LSL r1, r1, #5
		ADD r0, r0, r1
		LDRB r1, [r0, #2]
		LDR r0, [r6, #0x10]
		LDR r2, [pc, #0x1ec]
		STR r1, [sp]
		ADD r3, r0, r2
		MOV r2, #1
		B        |loc_08005BFE|
	INCBIN  baserom.gba_0x5bfc_0x5bfe.extracted
