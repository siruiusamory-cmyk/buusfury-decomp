	CODE16
|sub_0802136C|
|unk_0802136C|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r0, #8]
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		DCW     0xE7F3
|loc_08021380|
|unk_08021380|
		LDR r3, [r4, #0x20]
		LDR r6, [r4, #0x4c]
		ADD r3, r3, r6
		STR r3, [r4, #0x20]
		LDR r2, [r4, #0x50]
		LDR r3, [r4, #0x24]
		ADD r2, r3, r2
		STR r2, [r4, #0x24]
		LDR r2, [r4, #0x50]
		STR r1, [r4, #0x40]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		ADD r2, #0x20
		STR r2, [r4, #0x50]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r0, #4]
		LSL r1, r1, #2
		ADD r0, r0, r1
		ADD r0, #0xc
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [r4, #0x58]
		SUB r0, #0x20
		STR r0, [r4, #0x58]
		LDR r1, [r4, #0x54]
		ADD r0, r1, r0
		STR r0, [r4, #0x54]
		DCW     0xD5D4
		MOV r6, #0
		CMP r5, #0
		BEQ      |loc_08021424|
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r5, sp
		ADD r7, r5, #4
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x1b0]
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #0x5c]
		LDRH r0, [r0]
		STR r0, [sp, #0x18]
		ADD r0, r4, #0
		ADD r0, #0x28
		LDMIA r0!, {r0, r1, r2, r3}
		STMIA r7!, {r0, r1, r2, r3}
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		ADD r0, #0xff
		ADD r0, #0xc1
		LDR r0, [r0, #0x10]
		ADD r2, r5, #0
		LDR r5, [pc, #0x178]
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		LDR r0, [r5, #4]
		MOV r1, #0
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_08021424|
		LDR r5, [r5]
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		LDR r1, [pc, #0x160]
		ADD r0, r3, r0
		LSL r0, r0, #2
		SUB r1, #0x24
		ADD r1, r0, r1
		LDR r0, [pc, #0x158]
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08021424|
		MOV r0, #1
		STR r0, [r4, #0x48]
		STR r6, [r4, #0x40]
		DCW     0xE79D
|loc_0802142C|
|unk_0802142C|
		B        |loc_0802142E|
|loc_0802142E|
		STR r1, [r4, #0x40]
		LSL r1, r1, #0x1b
		LSR r1, r1, #0x1e
		CMP r1, #3
		LDR r0, [r0, #4]
		BNE      |loc_08021440|
		ADD r0, #0xc
		STR r0, [r4, #0x18]
		B        |loc_0802144A|
|loc_08021440|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
|loc_0802144A|
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		DCW     0xE78A
