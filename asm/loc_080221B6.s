	CODE16
|loc_080221B6|
|unk_080221B6|
		LSL r3, r0, #3
		SUB r3, r3, r0
		LSL r3, r3, #2
		ADD r3, lr
		ADD r3, #4
		LDR r6, [r3]
		CMP r1, r6
		BLT      |loc_0802228E|
		LDR r6, [r3, #8]
		CMP r1, r6
		BGE      |loc_0802228E|
		LDR r6, [r2, #4]
		LDR r7, [r3, #4]
		CMP r6, r7
		BLT      |loc_0802228E|
		LDR r7, [r3, #0xc]
		CMP r6, r7
		BGE      |loc_0802228E|
		LDR r6, [r3, #0x10]
		CMP r6, #0
		BNE      |loc_0802228E|
		MOV r0, #1
		STR r0, [r3, #0x10]
		MOV r0, #0xff
		ADD r0, #0xd1
		LDR r0, [r0, r4]
		LDR r2, [r0]
		ADD r6, r2, #1
		STR r6, [r0]
		LSL r2, r2, #3
		ADD r0, r2, r0
		LDR r1, [r3, #0x18]
		ADD r0, #4
		LDR r2, [r3, #0x14]
		STR r1, [r0, #4]
		STR r2, [r0]
		ADD r0, r3, #0
		LDR r2, [r3]
		LDR r6, [r3, #8]
		LDR r3, [r3, #4]
		ADD r0, #8
		LDR r0, [r0, #4]
		ADD r2, r2, r6
		STR r2, [sp, #4]
		ASR r2, r2, #1
		ADD r0, r3, r0
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		MOV r0, #0
		STR r2, [sp, #4]
		STR r2, [sp, #0xc]
		ADD r1, sp, #0xc
		BL       |loc_080222E0|
		ADD r6, r0, #0
		BL       |sub_08022368|
		LDR r7, [pc, #0xac]
		ADD r1, r6, #0
		LDR r0, [r7, #4]
		BL       |List_Append|
		LDR r0, [r5]
		ADD r1, r0, #1
		LSL r0, r0, #2
		ADD r0, r0, r5
		STR r1, [r5]
		STR r6, [r0, #4]
		LDR r0, [r4, #4]
		SUB r0, #1
		STR r0, [r4, #4]
		BNE      |loc_0802227C|
		LDR r2, [r5]
		CMP r2, #0
		BLE      |loc_08022262|
		LDR r3, [r4, #8]
|loc_08022252|
		LSL r1, r0, #2
		ADD r1, r1, r5
		LDR r1, [r1, #4]
		CMP r1, r3
		BEQ      |loc_08022266|
		ADD r0, #1
		CMP r2, r0
		BGT      |loc_08022252|
|loc_08022262|
		MOV r0, #0
		MVN r0, r0
|loc_08022266|
		LDR r1, [r5]
		SUB r1, #1
		STR r1, [r5]
		SUB r1, r1, r0
		BEQ      |loc_08022284|
		LSL r0, r0, #2
		ADD r0, r0, r5
		LSL r2, r1, #2
		ADD r1, r0, #0
		ADD r1, #8
		B        |loc_0802227E|
|loc_0802227C|
		DCW     0xE00B
|loc_0802227E|
		ADD r0, #4
		BL       |Thunk_VramCopy|
|loc_08022284|
		LDR r1, [r4, #8]
		LDR r0, [r7, #4]
		BL       |loc_08011944|
		DCW     0xE003
|loc_0802228E|
		B        |sub_08022290|
