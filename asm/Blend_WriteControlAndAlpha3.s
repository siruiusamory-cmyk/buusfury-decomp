|Blend_WriteControlAndAlpha3|
	CODE16
|unk_08024C98|
		LDR r7, [pc, #0xac]
		MOV r6, #1
		LDR r0, [r7]
		LDR r5, [pc, #0xe4]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x16
		LSR r0, r0, #0x1f
		CMP r0, #0
		BEQ      |loc_08024CD8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x2c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_08024CD8|
		LDR r0, [pc, #0xcc]
		STRB r6, [r4, #6]
		STRH r5, [r0, #0x10]
		LDR r0, [pc, #0x88]
		ADD r7, sp, #4
		ADD r1, r7, #0
		SUB r0, #0xd8
		STR r6, [r4, #8]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LSL r2, r6, #8
		ADD r1, r7, r2
		LDR r0, [pc, #0x94]
		BL       |Thunk_VramCopy|
|loc_08024CD8|
		LDR r7, [pc, #0x6c]
		LDR r0, [r7]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x17
		LSR r0, r0, #0x1f
		BEQ      |loc_08024D16|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x30]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_08024D16|
		MOV r0, #2
		STRB r0, [r4, #6]
		LDR r0, [pc, #0x8c]
		STRH r5, [r0, #0x10]
		LDR r0, [pc, #0x4c]
		ADD r5, sp, #4
		ADD r1, r5, #0
		SUB r0, #0x78
		STR r6, [r4, #8]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r2, #0xff
		ADD r2, #1
		ADD r1, r5, r2
		LDR r0, [pc, #0x5c]
		BL       |Thunk_VramCopy|
|loc_08024D16|
		LDR r0, [r7]
		LDRH r0, [r0, #4]
		LSL r1, r0, #0x1e
		LSR r1, r1, #0x1f
		BNE      |loc_08024D26|
		LSL r0, r0, #0x1d
		LSR r0, r0, #0x1f
		BEQ      |loc_08024D32|
|loc_08024D26|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x1c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
|loc_08024D32|
		LDRB r0, [r4, #5]
		CMP r0, #0x10
		BHS      |loc_08024D40|
		ADD r0, #1
		LDR r1, [pc, #0x54]
		STRB r0, [r4, #5]
		STRB r0, [r1, #2]
|loc_08024D40|
|unk_08024D40|
; cited by 0x08024A8C (a pc-relative load targets 0x08024D44)
		MOV r0, #0
		DCW     0xE7A6
	INCBIN  baserom.gba_0x24d44_0x24d94.extracted
