	CODE16
|loc_08005228|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x30
	SUB      sp, #0x24
	BL       |GBARam_Malloc|
	MOV      r7, #0
	MVN      r7, r7
	ADD      r5, r0, #0
	CMP      r0, #0
	LDR      r6, [pc, #0x1e4]
	BEQ      |loc_0800526A|
	MOV      r1, #0
	STR      r1, [sp, #0x18]
	MOV      r2, #1
	STR      r2, [sp, #0x1c]
	MOV      r1, #1
	MOV      r2, #0x78
	STR      r2, [sp, #0x10]
|unk_0800524E|
	INCBIN	baserom.gba_0x524e_0x5250.extracted
	STR      r2, [sp, #4]
	STR      r1, [sp, #0xc]
	STR      r1, [sp]
	MOV      r0, #0x78
	STR      r0, [sp, #0x14]
	ADD      r1, r4, #0
	MOV      r2, #0
	MOV      r3, #1
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	BL       |loc_080060A8|
	STR      r6, [r5]
|loc_0800526A|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BEQ      |loc_080052A8|
	MOV      r2, #1
	MOV      r1, #1
	STR      r1, [sp, #0x18]
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x78
	MOV      r1, #2
	STR      r2, [sp, #0x10]
	SUB      r2, r1, #3
	STR      r1, [sp, #0xc]
	MOV      r1, #0
	STR      r1, [sp]
	STR      r2, [sp, #4]
	MOV      r0, #0x86
	STR      r0, [sp, #0x14]
	MOV      r2, #1
	ADD      r1, r4, #0
	MOV      r3, #0
	ADD      r0, r5, #0
	STR      r7, [sp, #8]
	BL       |loc_080060A8|
	STR      r6, [r5]
|loc_080052A8|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0xe16
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800664E|
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x154]
	LDR      r0, [pc, #0x15c]
	SUB      r1, #8
	LDR      r1, [r1]
	MOV      r6, #0
	ADD      r5, r1, r0
	MOV      r0, #0xff
	ADD      r0, #0x21
	CMP      r2, #0
	LDR      r7, [pc, #0x154]
	LDR      r4, [pc, #0x150]
	BEQ      |sub_08005332|
	CMP      r2, #1
	BNE      |loc_08005362|
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800531E|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STR      r6, [r0, #4]
	STR      r7, [r0]
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	MOV      r2, #0xff
	LDR      r3, [pc, #0x138]
	ADD      r2, #0x15
	STR      r6, [r1, #0x10]
	STR      r3, [r2, r0]
	LDR      r2, [pc, #0x134]
	LDR      r3, [pc, #0x134]
	STR      r2, [r0]
	ADD      r2, #0x38
	STR      r2, [r1, #0x14]
	LDRB     r2, [r3]
	ADD      r1, #0x18
	STRB     r2, [r1]
	LDRB     r2, [r3, #1]
	STRB     r2, [r1, #1]
	LDRB     r2, [r3, #2]
	STRB     r2, [r1, #2]
	LDRB     r2, [r3, #3]
	STRB     r2, [r1, #3]
|loc_0800531E|
	BL       |inc_0x03d784_0x041118| + 0xcc
	ADD      r1, r4, #0
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08005332|
|unk_08005332|
		DCW     0xF038
		DCW     0xF941
		CMP r0, #0
		BEQ      |loc_0800534E|
		ADD r1, r0, #0
		ADD r1, #0xff
		STR r6, [r0, #4]
		STR r7, [r0]
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0xf4]
		STR r1, [r0]
|loc_0800534E|
		BL       |inc_0x03d784_0x041118| + 0xcc
		ADD r1, r4, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x51d8
|loc_08005362|
|unk_08005362|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x51d8
		MOV r0, #0
		BX       lr
