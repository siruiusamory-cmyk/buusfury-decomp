	CODE16
|sub_08025C66|
|unk_08025C66|
		LDR r1, [sp, #0x10]
		CMP r1, #0
		BGE      |loc_08025C94|
		MOV r7, #0
		CMP r5, #0
		BLE      |loc_08025CD4|
		LDR r0, [sp, #8]
		LSL r2, r0, #1
		LSL r1, r6, #1
		STR r1, [sp, #0x20]
		STR r2, [sp, #0x24]
|loc_08025C7C|
		LSL r0, r7, #6
		LDR r1, [sp, #0x20]
		ADD r0, r0, r4
		ADD r0, r0, r1
		MOV r1, #0
		LDR r2, [sp, #0x24]
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025C7C|
		B        |loc_08025CD4|
|loc_08025C94|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #0xd
		ADD r0, r0, r1
		LDR r1, [sp, #0x10]
		MOV r7, #0
		LSL r1, r1, #6
		ADD r0, r0, r1
		LDR r1, [pc, #0x150]
		ADD r1, r0, r1
		STR r1, [sp, #4]
		CMP r5, #0
		BLE      |loc_08025CD4|
		LDR r0, [sp, #8]
		LSL r0, r0, #1
		LSL r2, r6, #1
		STR r2, [sp, #0x18]
		STR r0, [sp, #0x1c]
|loc_08025CB8|
		LDR r1, [sp, #4]
		LSL r0, r7, #8
		LDR r2, [sp, #0x18]
		ADD r0, r0, r1
		ADD r1, r0, r2
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r0, r0, r2
		LDR r2, [sp, #0x1c]
		BL       |Thunk_PaletteCopy|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025CB8|
|loc_08025CD4|
		CMP r6, #0
		BEQ      |loc_08025C62|
		LDR r1, [sp, #0x10]
		CMP r1, #3
		BLT      |loc_08025CFA|
		MOV r7, #0
		CMP r5, #0
		BLE      |loc_08025C62|
		LSL r6, r6, #1
|loc_08025CE6|
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r2, r6, #0
		MOV r1, #0
		BL       |sub_08049168|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025CE6|
		B        |loc_08025C62|
|loc_08025CFA|
		MOV r7, #0
		CMP r5, #0
		BLE      |loc_08025C62|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #0xd
		ADD r0, r0, r1
		LDR r1, [sp, #0x10]
		LSL r1, r1, #6
		ADD r1, r0, r1
		LDR r0, [pc, #0xec]
		ADD r1, r1, r0
		STR r1, [sp, #0x14]
		LSL r6, r6, #1
|loc_08025D16|
		LDR r1, [sp, #0x14]
		LSL r0, r7, #8
		ADD r1, r0, r1
		LSL r0, r7, #6
		ADD r0, r0, r4
		ADD r2, r6, #0
		BL       |Thunk_PaletteCopy|
		ADD r7, #1
		CMP r7, r5
		BLT      |loc_08025D16|
		B        |loc_08025C62|
