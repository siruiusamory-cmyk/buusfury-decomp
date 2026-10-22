	CODE16
|sub_0803F754|
|unk_0803F754|
		LDR r0, [r2]
		LSL r1, r1, #1
		LDRH r1, [r0, r1]
		LSL r1, r1, #1
		ADD r0, r1, r0
		LDRH r5, [r0]
		ADD r0, #2
		STR r0, [sp, #0x130]
|loc_0803F764|
|unk_0803F764|
		LDR r0, [r6]
		LDR r1, [r6, #4]
		SUB r0, #1
		STR r0, [sp, #0x120]
		STR r1, [sp, #0x124]
		LDR r1, [sp, #0x120]
		ADD r0, r5, #2
		ADD r0, r1, r0
		STR r0, [sp, #0x128]
		LDR r0, [sp, #0x124]
		ADD r2, r4, #0
		ADD r0, #0x11
		STR r0, [sp, #0x12c]
		ADD r0, sp, #0x110
		ADD r2, #0x10
		ADD r1, sp, #0x120
		BL       |inc_0x049120_0x055620| + 0xa130
		LDR r0, [sp, #0x110]
		LDR r1, [sp, #0x118]
		CMP r0, r1
		DCW     0xDA71
		LDR r0, [sp, #0x114]
		LDR r1, [sp, #0x11c]
		CMP r0, r1
		DCW     0xDA6D
		LDR r0, [sp, #0x118]
		LDR r1, [sp, #0x110]
		SUB r2, r0, r1
		LDR r0, [sp, #0x11c]
		LDR r1, [sp, #0x114]
		STR r2, [sp, #0x10c]
		SUB r0, r0, r1
		LDR r2, [r6, #4]
		LSL r7, r0
		SUB r2, r1, r2
		MOV r1, #0
		SUB r7, #1
		STR r7, [sp, #0x104]
		STR r2, [sp, #0x108]
		MOV r0, #0
		CMP r5, #0
		STR r1, [sp, #8]
		STR r1, [sp, #4]
		BLE      |loc_0803F7EC|
|loc_0803F7BE|
		LDR r2, [sp, #0x130]
		LSL r1, r0, #1
		LDRH r1, [r2, r1]
		LSL r2, r0, #2
		ADD r3, sp, #0x84
		STR r1, [r3, r2]
		ADD r7, sp, #4
		LDR r3, [r7, r2]
		ADD r7, sp, #4
		ORR r3, r1
		STR r3, [r7, r2]
		LSR r3, r1, #1
		LSL r7, r1, #1
		ORR r3, r7
		ADD r7, sp, #4
		ADD r2, r2, r7
		LDR r7, [r2, #4]
		STR r1, [r2, #8]
		ORR r3, r7
		ADD r0, #1
		CMP r0, r5
		STR r3, [r2, #4]
		BLT      |loc_0803F7BE|
|loc_0803F7EC|
		MOV r1, #0
		LSL r0, r0, #2
		ADD r2, sp, #0x84
		STR r1, [r2, r0]
		LDR r0, [sp, #0x110]
		LDR r1, [r6]
		ADD r3, sp, #4
		SUB r1, r0, r1
		LSL r0, r1, #2
		ADD r3, r0, r3
		MOV lr, r0
		ADD lr, r2
		LDR r0, [sp, #0x114]
		STR r3, [sp]
		LDR r2, [r4, #0x28]
		MUL r0, r2
		LDR r2, [r4, #0x24]
		ADD r0, r0, r2
		LDR r2, [sp, #0x110]
		ADD r7, r0, r2
		MOV r0, #0
		CMP r1, #0
		DCW     0xDB07
		MOV r0, lr
		LDR r0, [r0]
		DCW     0xE000
|loc_0803F820|
|unk_0803F820|
		DCW     0xE039
		LDR r2, [sp, #0x108]
		LSR r0, r2
		LDR r2, [sp, #0x104]
		AND r0, r2
		MOV r1, #0
		LDR r2, [sp, #0x10c]
		MOV ip, r1
		CMP r2, #0
		BLE      |loc_0803F874|
