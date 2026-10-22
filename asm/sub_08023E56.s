	CODE16
|sub_08023E56|
|unk_08023E56|
		LDR r1, [r5, #0x38]
		LSR r2, r1, #0x1f
		ADD r2, r2, r1
		ASR r2, r2, #1
		ADD r2, #8
		CMP r2, r0
		BLE      |loc_08023E6E|
		ADD r1, r4, #0
		ADD r0, r5, #0
		BL       |loc_08023DBA|
		B        |loc_08023E54|
|loc_08023E6E|
		ADD r2, r1, #0
		ADD r2, #8
		CMP r0, r2
		BGE      |loc_08023EA2|
		LDR r3, [r4, #0x50]
		MOV r2, #2
		LDR r3, [r3]
		CMP r3, #4
		BNE      |loc_08023E8A|
		SUB r0, r0, r1
		ADD r0, #8
		LSL r0, r0, #0x1c
		LSR r2, r0, #0x1f
		ADD r2, #2
|loc_08023E8A|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r3, [r1, #0x30]
		ADD r3, r3, r1
		MOV r1, #0xe
		BL       |inc_0x046118_0x049114| + 0x98e
		ADD r1, r4, #0
		ADD r0, r5, #0
		BL       |loc_08023DBA|
		B        |loc_08023E54|
|loc_08023EA2|
		CMP r2, r0
		BNE      |loc_08023EC4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x30]
		ADD r3, r2, r1
		MOV r2, #0
		MOV r1, #0xe
		BL       |inc_0x046118_0x049114| + 0x98e
		ADD r5, #0x20
		ADD r4, #0xff
		ADD r4, #1
		ADD r4, #0x78
		LDMIA r5!, {r0, r1}
		STMIA r4!, {r0, r1}
		B        |loc_08023E54|
|loc_08023EC4|
		ADD r1, #0x10
		CMP r0, r1
		BLT      |loc_08023E54|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x40]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
	INCBIN  baserom.gba_0x23ee0_0x23ee2.extracted
|sub_08023EE2|
|unk_08023EE2|
	INCBIN	baserom.gba_0x23ee2_0x23ee6.extracted
	ADD      r0, #0x38
	LDMIA    r0!, {r0, r1}
	ADD      r0, #0x10
	CMP      r1, r0
	BLT      |sub_08023EF4|
	MOV      r0, #1
	BX       lr
