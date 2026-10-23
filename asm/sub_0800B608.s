	CODE16
|sub_0800B608|
|unk_0800B608|
		LDR r0, [pc, #0x1fc]
		MOV r6, #1
		LSL r6, r6, #9
		LDR r5, [pc, #0x1e8]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5, #8]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0800B630|
		ADD r1, r6, #0
		LDR r0, [r5, #8]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5, #8]
		BL       |loc_0801124C|
|loc_0800B630|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x1d8]
		MOV r2, #0x10
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0x18
		MOV r1, #0x20
		ADD r6, r0, #0
		BL       |loc_0803F540|
		MOV r0, #0
		MVN r0, r0
		STR r0, [r4, #0x10]
		STR r7, [r4, #0x14]
		LDR r0, [r5, #0x14]
		MOV r1, #1
		STR r0, [r4, #0x24]
		MOV r0, #2
		STRB r0, [r4, #0x1b]
		STRB r1, [r6, #2]
		LDR r1, [pc, #0x1b4]
		MOV r0, #0
		STR r1, [r6, #0x20]
		STRB r0, [r4, #0x18]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xb4ae
|sub_0800B664|
	DCW      0x4a64
