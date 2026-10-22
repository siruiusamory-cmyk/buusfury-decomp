	CODE16
|sub_08023F32|
|unk_08023F32|
		CMP r0, #4
		BHS      |loc_08023F3C|
		MOV r0, #0
		STRB r0, [r1, #0x11]
		DCW     0xE7F8
|loc_08023F3C|
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1e
		STRB r0, [r1, #0x11]
		BNE      |loc_08023F48|
		MOV r0, #2
		STRB r0, [r1, #0x11]
|loc_08023F48|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r2}
		LDR r0, [r0]
		ASR r2, r2, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r2, #0
		STR r2, [sp, #4]
		LDR r2, [sp, #8]
		STR r0, [sp, #0xc]
		STR r2, [sp, #0x10]
		LDRB r0, [r1, #0x10]
		LDR r2, [pc, #0xc4]
		LSL r0, r0, #3
		ADD r0, r0, r2
		LDR r2, [sp, #0xc]
		LDR r3, [r0]
		ADD r2, r2, r3
		LDR r3, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r2, [sp, #4]
		ADD r0, r3, r0
		STR r0, [sp, #8]
		ADD r0, r2, #0
		LDR r2, [sp, #8]
		STR r0, [sp, #0x14]
		ADD r0, sp, #0x14
		STR r2, [sp, #0x18]
	INCBIN  baserom.gba_0x23f84_0x23f86.extracted
|sub_08023F86|
|unk_08023F86|
	INCBIN	baserom.gba_0x23f86_0x23f8a.extracted
	LDR      r0, [pc, #0xa0]
	PUSH     {r4, lr}
	MOV      r1, #0xbd
	LDR      r2, [pc, #0x9c]
	LSL      r1, r1, #2
	SUB      r0, #4
	LDR      r0, [r0]
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x98]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xba8
	POP      {r4, pc}
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0x8c]
	SUB      sp, #0xc
	MOV      r5, #0
	LDR      r0, [r0]
	ADD      r4, r1, #0
	LDR      r2, [pc, #0x84]
	ADD      r1, r5, #0
	CMP      r4, #0
	STR      r5, [sp, #4]
	STR      r0, [sp, #8]
	STR      r2, [sp]
	BEQ      |loc_08023FC8|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08023FC8|
	MOV      r0, sp
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x68]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x4c]
	MOV      r1, #0xbd
	LDR      r2, [pc, #0x4c]
	LSL      r1, r1, #2
	SUB      r0, #4
	LDR      r0, [r0]
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x44]
	MOV      r2, #0x40
	ADD      r3, r5, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [pc, #0x48]
	STR      r0, [sp]
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |loc_0802400E|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802400E|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x28]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08024020|
	MOV      r0, #0
|loc_08024020|
	SUB      r0, r2, r0
	BX       lr
	LDR      r0, [pc, #0x18]
	ADD      r0, #4
	BX       lr
	LSL      r0, r0, #0
	STMIA    r3!, {r3, r4, r6}
	LSR      r2, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xa8
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BL       |loc_08024120|
	ADD      r4, #0xff
	ADD      r4, #0x11
	MOV      r0, #0xff
	ADD      r0, #0x35
	LDRB     r7, [r4, #0xc]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080240A8|
	LDR      r0, [pc, #0xa8]
	ADD      r5, r4, #0
	STR      r0, [r4]
	MOV      r0, #0xff
	ADD      r0, #0x15
	STRB     r7, [r0, r4]
	ADD      r5, #0xff
	MOV      r6, #0
	ADD      r5, #1
	STR      r6, [r5, #0x1c]
	STR      r6, [r5, #0x20]
	MVN      r1, r6
	ADD      r0, r4, #0
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x7c]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x7c]
	STR      r6, [r0]
	LDR      r0, [pc, #0x7c]
	STR      r6, [r0]
	LDR      r0, [pc, #0x7c]
	STR      r0, [r4]
	MOV      r0, #0xff
	ADD      r0, #0x31
	STR      r6, [r5, #0x2c]
	STRB     r7, [r0, r4]
|loc_080240A8|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	LDR      r1, [pc, #0x5c]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	CMP      r1, #0
	BEQ      |sub_080240DA|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r2, [r1, #0x18]
	ADD      r2, #1
	STR      r2, [r1, #0x18]
	CMP      r2, #0xa
	BLE      |sub_080240DA|
	BL       |inc_0x03d784_0x041118| + 0x29fe
	MOV      r0, #2
	POP      {r3, pc}
