	CODE16
|sub_08033DC0|
|unk_08033DC0|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		BNE      |inc_0x331c0_0x341c0| + 0xbfc
		LDR r0, [pc, #0x120]
		LDR r5, [r0]
		CMP r5, #0
		BEQ      |inc_0x331c0_0x341c0| + 0xbfc
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r6, r0, #0
		SUB r6, #0x20
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r7, r0, #0
		LDR r0, [pc, #0x108]
		SUB r7, #0x20
		LDR r0, [r0]
		BL       |loc_080116FC|
		CMP r0, #0x80
		BLT      |inc_0x331c0_0x341c0| + 0xbfc
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xe0]
		ADD r1, #4
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		ADD r1, r5, #0
		ADD r0, sp, #0x1c
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x24]
		LDR r2, [sp, #0x28]
		ADD r1, r0, r1
		LDR r0, [sp, #0x20]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x30]
		ADD r0, r1, r6
		STR r1, [sp, #4]
		STR r1, [sp, #0x2c]
		LDR r1, [sp, #0x30]
		STR r0, [sp, #4]
		ADD r1, r1, r7
		STR r1, [sp, #8]
		STR r1, [sp, #0x38]
		ADD r3, r4, #0
		STR r0, [sp, #0x34]
		MOV r0, #0
		ADD r1, sp, #0x14
		ADD r2, sp, #0x34
		BL       |inc_0x331c0_0x341c0| + 0xd68
		ADD r1, r0, #0
		LDR r0, [pc, #0x80]
		LDR r0, [r0]
	INCBIN  baserom.gba_0x33e72_0x33e74.extracted
|sub_08033E74|
|unk_08033E74|
	INCBIN	baserom.gba_0x33e74_0x33e78.extracted
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0x70]
	SUB      sp, #0xc
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x6c]
	STR      r1, [sp, #4]
	CMP      r4, #0
	STR      r0, [sp, #8]
	STR      r2, [sp]
	BEQ      |loc_08033E96|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08033E96|
	MOV      r0, sp
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033EAA|
	LDR      r1, [pc, #0x50]
	STR      r1, [r0]
|loc_08033EAA|
	ADD      r5, r0, #0
	MOV      r1, #4
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x3c]
	STR      r0, [sp]
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |loc_08033ED2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08033ED2|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_08033EE8|
|unk_08033EE8|
; cited by 0x08033DCA (a pc-relative load targets 0x08033EEC)
	INCBIN	baserom.gba_0x33ee8_0x33efa.extracted
