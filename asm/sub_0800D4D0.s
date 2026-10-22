	CODE16
|sub_0800D4D0|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x54]
	ADD      r6, r1, #0
	STR      r0, [r5]
	LDR      r0, [r5, #0x4c]
	LDR      r4, [r0, #8]
	LDRB     r0, [r4]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_0800D504|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x44]
	CMP      r0, r1
	BEQ      |loc_0800D504|
	MOV      r3, #2
	LDR      r0, [pc, #0x28]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0]
	BL       |loc_0801142A|
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_0800D504|
	MOV      r1, #0
	ADD      r0, r5, #0
	BL       |sub_0800D9F0|
	CMP      r6, #0
	BEQ      |loc_0800D516|
	ADD      r0, r5, #0
	BL       |GBARam_Free|
|loc_0800D516|
	POP      {r4, r5, r6, pc}
|sub_0800D518|
|unk_0800D518|
; cited by 0x0800D2B0 (a pc-relative load targets 0x0800D518)
	INCBIN  baserom.gba_0xd518_0xd538.extracted
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [r0, #0x40]
		SUB sp, #0x3c
		CMP r0, #0
		BNE      |loc_0800D62C|
		LDR r1, [r4, #0x60]
		LDR r2, [r4, #0x68]
		LDR r0, [r4, #0x6c]
		ADD r1, r1, r2
		LDR r2, [r4, #0x64]
		STR r1, [sp, #0x24]
		ADD r0, r2, r0
		STR r0, [sp, #0x28]
		ADD r0, r1, #0
		LDR r1, [sp, #0x28]
		STR r0, [sp, #0x34]
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x38]
		LDR r1, [sp, #0x34]
		STR r0, [sp, #0x2c]
		ASR r2, r1, #8
		LDR r1, [sp, #0x38]
		STR r2, [sp, #0x14]
		ASR r1, r1, #8
		STR r1, [sp, #0x18]
		STR r1, [sp, #0x20]
		STR r2, [sp, #0x1c]
		LDR r1, [r4, #0x70]
		ADD r0, r4, #0
		ADD r0, #0x70
		ADD r1, r1, r2
		LDR r2, [r0, #4]
		LDR r3, [sp, #0x20]
		STR r1, [sp, #4]
		ADD r2, r2, r3
		STR r2, [sp, #8]
		ADD r0, #8
		LDR r3, [r0]
		LDR r7, [sp, #0x1c]
		LDR r0, [r0, #4]
		ADD r3, r3, r7
		LDR r7, [sp, #0x20]
		STR r3, [sp, #4]
		ADD r0, r0, r7
		STR r0, [sp, #8]
		ADD r0, r3, #0
		LDR r3, [sp, #8]
		STR r1, [sp, #0xc]
		ADD r1, sp, #0xc
		STR r0, [sp, #0x14]
		ADD r0, r1, #0
		STR r2, [sp, #0x10]
		STR r3, [sp, #0x18]
		LDMIA r0!, {r0, r1, r2, r3}
		ADD r7, sp, #0x24
		STMIA r7!, {r0, r1, r2, r3}
		LDR r0, [pc, #0x2cc]
		ADD r5, r4, #0
		ADD r5, #0x60
		LDR r0, [r0, #0xc]
		ADD r6, r5, #4
		ADD r0, #0x80
		LDR r1, [r0, #0x28]
		ADD r0, sp, #0x24
		BL       |loc_08009324|
		MOV r7, #1
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0xd4dc
		LDR r0, [sp, #0x34]
		ADD r2, sp, #0x1c
		STR r0, [r5]
		LDR r0, [sp, #0x38]
		STR r0, [r6]
		LDR r0, [sp, #0x34]
		ASR r1, r0, #8
		LDR r0, [sp, #0x38]
		STR r1, [sp, #0x14]
		ASR r0, r0, #8
		STR r1, [sp, #0x1c]
		ADD r1, r2, #0
		STR r0, [sp, #0x18]
		STR r0, [sp, #0x20]
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xd98e
		ADD r0, r4, #0
		ADD r0, #0x18
		ADD r1, r0, #0
		LDR r2, [r4, #0x18]
		LDR r3, [r4, #0x20]
		ADD r1, #8
		LDR r0, [r4, #0x1c]
		LDR r1, [r1, #4]
		ADD r2, r2, r3
		ADD r0, r0, r1
		STR r0, [sp, #0x10]
		ASR r0, r0, #1
		ASR r1, r2, #1
		STR r0, [sp, #0x10]
		STR r0, [sp, #0x18]
		ADD r0, r1, #0
		STR r2, [sp, #0xc]
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x14]
		LDR r1, [r4, #0x24]
		SUB r0, #8
		STR r0, [r4, #0x50]
		SUB r1, #6
		STR r1, [r4, #0x54]
		LDR r0, [r4, #0x3c]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0xd4dc
		LDR r1, [sp, #0x24]
		LDR r2, [sp, #0x28]
		ADD r5, sp, #0x2c
		SUB r1, #0xf
		LDMIA r5!, {r3, r5}
		STRH r1, [r0, #4]
		SUB r2, #7
		B        |sub_0800D62E|
|loc_0800D62C|
		B        |loc_0800D666|
