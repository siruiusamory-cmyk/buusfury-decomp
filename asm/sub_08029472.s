	CODE16
|sub_08029472|
|unk_08029472|
		LDR r0, [r4, #0x40]
		LDR r1, [r4, #0x44]
		ORR r0, r1
		BEQ      |loc_0802946E|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x478a
		CMP r0, #0
		BNE      |loc_0802948E|
		ADD r1, r4, #0
		LDR r0, [r7, #4]
		BL       |loc_08011944|
		B        |loc_0802946E|
|loc_0802948E|
		LDR r7, [pc, #0x134]
		ADD r0, r4, #0
		SUB r7, #0xc
		LDR r1, [r7, #8]
		ADD r0, #0x28
		ADD r7, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_080294B6|
		MOV r0, #0x10
		STR r0, [r4, #0x4c]
		LDR r0, [pc, #0x124]
		STR r0, [r4, #0x54]
		MOV r0, #0
		STR r0, [r5]
		STR r0, [r6]
		B        |loc_0802946E|
|loc_080294B6|
		LDR r0, [sp, #0x38]
		CMP r0, #0
		BEQ      |loc_0802946E|
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |loc_0802946E|
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x104]
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #0x50]
		STR r0, [sp, #0x18]
		ADD r0, sp, #4
		LDMIA r7!, {r1, r2, r3, r7}
		STMIA r0!, {r1, r2, r3, r7}
		LDRB r0, [r4, #0x11]
		LDR r7, [pc, #0xe4]
		ADD r3, sp, #0
		STRB r0, [r3]
		MOV r1, #0
		SUB r7, #0xc
		STR r4, [sp, #0x30]
		LDR r0, [r7, #4]
		MOV r2, sp
		BL       |loc_08011C70|
		CMP r0, #0
		BEQ      |loc_0802946E|
		LDR r7, [r7]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0xd4]
		LSL r0, r0, #2
		ADD r1, r0, r1
		ADD r0, r7, #0
		LDR r7, [pc, #0xc0]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r0, r7
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0x10
		STR r0, [r4, #0x4c]
		LDR r0, [pc, #0xb4]
		MOV r3, #0
		STR r0, [r4, #0x54]
		STR r3, [r5]
		STR r3, [r6]
		B        |loc_0802946E|
