	CODE16
|sub_080198E4|
|unk_080198E4|
		MOV r0, #0x10
		STR r0, [r4, #0x4c]
		STR r5, [r4, #0x54]
		STR r7, [r4, #0x18]
|loc_080198EC|
|unk_080198EC|
		LDR r0, [r4, #0x4c]
		CMP r0, #0
		BEQ      |loc_08019902|
		SUB r0, #1
		STR r0, [r4, #0x4c]
		BNE      |inc_0x153f2_0x1a3f2| + 0x44ee
		ADD r1, r4, #0
		LDR r0, [r6, #4]
		BL       |loc_08011944|
|loc_08019900|
		B        |inc_0x153f2_0x1a3f2| + 0x44ee
|loc_08019902|
		LDR r1, [r4, #0x20]
		LDR r2, [r4, #0x40]
		ADD r1, r1, r2
		STR r1, [r4, #0x20]
		LDR r0, [r4, #0x44]
		LDR r1, [r4, #0x24]
		ADD r0, r1, r0
		STR r0, [r4, #0x24]
		LDR r0, [r4, #0x48]
		ADD r0, #1
		ASR r1, r0, #3
		CMP r1, #3
		STR r0, [r4, #0x48]
		BLE      |loc_08019924|
		LSL r1, r1, #0x1f
		LSR r1, r1, #0x1f
		ADD r1, #2
|loc_08019924|
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r4, #0x50]
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x478a
		CMP r0, #0
		BNE      |loc_0801994A|
		ADD r1, r4, #0
		LDR r0, [r6, #4]
		BL       |loc_08011944|
		B        |inc_0x153f2_0x1a3f2| + 0x44ee
|loc_0801994A|
		LDR r6, [pc, #0x1a0]
		ADD r0, r4, #0
		SUB r6, #0xc
		LDR r1, [r6, #8]
		ADD r0, #0x28
		ADD r6, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_0801996A|
		MOV r0, #0x10
		STR r0, [r4, #0x4c]
		STR r7, [r4, #0x18]
		B        |inc_0x153f2_0x1a3f2| + 0x44ee
|loc_0801996A|
		LDR r0, [sp, #0x38]
		CMP r0, #0
		BEQ      |inc_0x153f2_0x1a3f2| + 0x44ee
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |inc_0x153f2_0x1a3f2| + 0x44ee
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x178]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r6!, {r1, r2, r3, r6}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r6}
		LDRB r0, [r4, #0x11]
		ADD r3, sp, #0
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		LDR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |loc_080199AC|
		LDR r0, [r4, #0x60]
		CMP r0, #0
		BEQ      |loc_080199AC|
		ADD r0, #0xff
		ADD r0, #0xc1
		STR r5, [r0, #0xc]
|loc_080199AC|
		LDR r6, [pc, #0x13c]
		ADD r2, r7, #0
		MOV r1, #0
		SUB r6, #0xc
		LDR r0, [r6, #4]
		BL       |loc_08011C70|
		MOV r7, #1
		CMP r0, #0
		BEQ      |loc_080199E2|
		LDR r6, [r6]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x120]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x11c]
		ADD r3, r5, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		STR r7, [r4, #0x54]
|loc_080199E2|
		LDR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |loc_08019900|
		LDR r0, [r4, #0x60]
		CMP r0, #0
		BEQ      |loc_08019900|
		ADD r0, #0xff
		ADD r0, #0xc1
		STR r7, [r0, #0xc]
		B        |inc_0x153f2_0x1a3f2| + 0x44ee
