	CODE16
|sub_0803F5EC|
|unk_0803F5EC|
		LDR r0, [r2]
		LSL r1, r1, #1
		LDRH r1, [r0, r1]
		LSL r1, r1, #1
		ADD r0, r1, r0
		LDRH r5, [r0]
		ADD r0, #2
		STR r0, [sp, #0x130]
|loc_0803F5FC|
|unk_0803F5FC|
		LDR r0, [r6, #4]
		LDR r1, [r6]
		STR r0, [sp, #0x124]
		ADD r0, r5, #1
		ADD r0, r1, r0
		STR r0, [sp, #0x128]
		LDR r0, [sp, #0x124]
		ADD r2, r4, #0
		ADD r0, #0x11
		STR r0, [sp, #0x12c]
		STR r1, [sp, #0x120]
		ADD r1, sp, #0x120
		ADD r0, sp, #0x110
		ADD r2, #0x10
		BL       |inc_0x049120_0x055620| + 0xa130
		LDR r0, [sp, #0x110]
		LDR r1, [sp, #0x118]
		CMP r0, r1
		DCW     0xDA68
		LDR r0, [sp, #0x114]
		LDR r1, [sp, #0x11c]
		CMP r0, r1
		DCW     0xDA64
		LDR r0, [sp, #0x118]
		LDR r1, [sp, #0x110]
		SUB r1, r0, r1
		STR r1, [sp, #0x10c]
		LDR r1, [sp, #0x114]
		LDR r0, [sp, #0x11c]
		LDR r2, [r6, #4]
		SUB r0, r0, r1
		LSL r7, r0
		SUB r7, #1
		STR r7, [sp, #0x104]
		MOV r7, #0
		SUB r2, r1, r2
		MOV r0, #0
		CMP r5, #0
		STR r2, [sp, #0x108]
		STR r7, [sp, #4]
		BLE      |loc_0803F66A|
|loc_0803F650|
		LDR r2, [sp, #0x130]
		LSL r1, r0, #1
		LDRH r1, [r2, r1]
		LSL r2, r0, #2
		ADD r3, sp, #0x84
		STR r1, [r3, r2]
		ADD r3, sp, #4
		ADD r2, r2, r3
		LSL r1, r1, #1
		ADD r0, #1
		CMP r0, r5
		STR r1, [r2, #4]
		BLT      |loc_0803F650|
|loc_0803F66A|
		LSL r0, r0, #2
		ADD r1, sp, #0x84
		STR r7, [r1, r0]
		LDR r2, [sp, #0x110]
		LDR r0, [r6]
		ADD r3, sp, #4
		SUB r2, r2, r0
		LSL r2, r2, #2
		ADD r2, r2, r3
		STR r2, [sp]
		LDR r2, [sp, #0x114]
		LDR r3, [r4, #0x28]
		LSL r0, r0, #2
		MUL r2, r3
		LDR r3, [r4, #0x24]
		ADD r2, r2, r3
		LDR r3, [sp, #0x110]
		ADD r7, r2, r3
		LSL r2, r3, #2
		ADD r1, r2, r1
		SUB r0, r1, r0
		MOV lr, r0
		MOV r0, #0
		LDR r1, [sp, #0x10c]
		MOV ip, r0
		CMP r1, #0
		DCW     0xDD2A
|loc_0803F6A0|
|unk_0803F6A0|
		MOV r1, lr
		LDMIA r1!, {r0}
		LDR r2, [sp, #0x108]
		MOV lr, r1
		LSR r0, r2
		LDR r2, [sp, #0x104]
		AND r0, r2
		LDR r2, [sp]
		LDMIA r2!, {r1}
		STR r2, [sp]
		LDR r2, [sp, #0x108]
		LSR r1, r2
		DCW     0xE000
|loc_0803F6BA|
|unk_0803F6BA|
		DCW     0xE020
		LDR r2, [sp, #0x104]
		AND r1, r2
		ADD r2, r7, #0
		ADD r3, r0, #0
		ORR r3, r1
		DCW     0xD00F
