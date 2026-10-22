	CODE16
|sub_0801D68C|
|unk_0801D68C|
		LDR r0, [pc, #0x2d0]
		MOV r1, #0
		STMIA r5!, {r0, r1}
		SUB r5, #8
		ADD r4, r5, #0
		ADD r4, #0xff
		ADD r4, #1
		MOV r0, #0
		STR r0, [r4, #0xc]
		STR r0, [r4, #8]
		STR r0, [r4, #0x10]
		LDR r0, [pc, #0x2c0]
		ADD r7, r4, #0
		STR r0, [r5]
		MOV r0, #0
		ADD r7, #0x50
		STR r0, [r7]
		LDR r0, [pc, #0x2a8]
		STR r6, [r4, #0x14]
		LDR r0, [r0, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r6, r0, r1
		ADD r0, r6, #0
		BL       |loc_08013C66|
		ADD r0, r6, #0
		ADD r0, #0x4c
		LDRH r0, [r0]
		STR r0, [r4, #0x28]
		STR r0, [r4, #0x18]
		ADD r0, r6, #0
		ADD r0, #0x4e
		LDRH r0, [r0]
		STR r0, [r4, #0x2c]
		STR r0, [r4, #0x1c]
		ADD r0, r6, #0
		ADD r0, #0x50
		LDRH r0, [r0]
		STR r0, [r4, #0x30]
		STR r0, [r4, #0x20]
		ADD r0, r6, #0
		ADD r0, #0x54
		LDRH r0, [r0]
		STR r0, [r4, #0x34]
		STR r0, [r4, #0x24]
		MOV r0, #0
		LDR r1, [pc, #0x264]
		STR r0, [r4, #0x3c]
		LDR r1, [r1, #0xc]
		ADD r1, #0xe4
		LDR r2, [r1]
		CMP r2, #0
		BLE      |loc_0801D74C|
|loc_0801D700|
		LSL r2, r0, #2
		ADD r2, r2, r1
		ADD r2, #4
		LDR r3, [r2]
		LSL r6, r3, #4
		MOV ip, r3
		MOV r3, #0x2c
		LSR r6, r6, #4
		MUL r3, r6
		LDR r6, [pc, #0x254]
		ADD r3, r3, r6
		LDRB r3, [r3, #0x14]
		LDR r6, [r4, #0x14]
		CMP r3, r6
		BNE      |loc_0801D744|
		LDR r6, [pc, #0x238]
		MOV r3, ip
		LDR r6, [r6, #0xc]
		LSR r3, r3, #0x1c
		LDRB r6, [r6]
		SUB r3, #1
		CMP r3, r6
		BNE      |loc_0801D732|
		LDR r3, [r7]
		STR r3, [r4, #0x3c]
|loc_0801D732|
		LDR r3, [r7]
		ADD r6, r3, #1
		LSL r3, r3, #3
		ADD r3, r3, r7
		STR r6, [r7]
		LDR r2, [r2]
		ADD r3, #4
		STR r0, [r3, #4]
		STR r2, [r3]
|loc_0801D744|
		LDR r2, [r1]
		ADD r0, #1
		CMP r2, r0
		BGT      |loc_0801D700|
|loc_0801D74C|
		LDR r0, [r4, #0x3c]
		SUB r0, #2
		STR r0, [r4, #0x38]
		BPL      |loc_0801D758|
		MOV r0, #0
		STR r0, [r4, #0x38]
|loc_0801D758|
		ADD r0, r5, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x1206
		ADD r0, r5, #0
		DCW     0xE793
	INCBIN  baserom.gba_0x1d762_0x1d790.extracted
