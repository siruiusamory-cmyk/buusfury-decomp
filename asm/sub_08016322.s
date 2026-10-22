	CODE16
|sub_08016322|
|unk_08016322|
		LDR r0, [pc, #0x194]
		LDR r5, [pc, #0x194]
		STR r0, [r4]
		MOV r0, #0x40
		STRH r0, [r4, #0xe]
		LDR r0, [r5]
		MOV r1, #0x40
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08016348|
		MOV r1, #0x40
		LDR r0, [r5]
		BL       |sub_08011732|
		MOV r1, #0x40
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_08016348|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x174]
		LDR r1, [pc, #0x16c]
		STR r0, [r4]
		STR r6, [r4, #0x10]
		STR r7, [r4, #0x14]
		LDR r0, [sp, #8]
		ADD r1, #4
		LSL r0, r0, #2
		LDR r5, [r1, r0]
		LDR r0, [r5, #4]
		ASR r1, r0, #0x1f
		LSR r1, r1, #0x1a
		ADD r0, r1, r0
		ASR r0, r0, #6
		STR r0, [r4, #0x1c]
		LDR r0, [r5, #4]
		DCW     0xF027
		DCW     0xF925
		ADD r1, r0, #0
		STR r0, [r4, #0x24]
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r0, #0
		STR r0, [r4, #0x18]
		MVN r0, r0
		STR r0, [r4, #0x20]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0xf2c
