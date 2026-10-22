	CODE16
|sub_080287EE|
|unk_080287EE|
		LDR r1, [pc, #0x1d0]
		MOV r6, #1
		LDR r1, [r1, #8]
		ADD r1, #0x80
		CMP r0, #0
		DCW     0xD064
		LDR r0, [r4, #0x4c]
		CMP r0, #0
		DCW     0xD061
		LDR r0, [r4, #0x40]
		LDR r2, [r4, #0x38]
		LDR r3, [r4, #0x3c]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x34]
		ADD r2, r3, #0
		STR r3, [sp, #0x38]
		LDR r3, [r4, #0x20]
		ADD r7, sp, #8
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x34]
		ADD r2, r3, r2
		STR r2, [sp, #0x38]
		LDR r5, [sp, #0x38]
		ADD r2, r0, #0
		LDR r0, [r4, #0x4c]
		ADD r3, sp, #0
		STR r0, [sp, #0x28]
		LDR r0, [r4, #0x44]
		STRB r0, [r3, #0x1c]
		LDR r0, [pc, #0x1a4]
		STR r0, [sp, #0x24]
		MOV r0, #0
		STR r0, [sp, #0x20]
		STRB r0, [r3, #8]
		ADD r3, r2, #0
		ADD r0, r7, #4
		ADD r7, r5, #0
		SUB r7, #8
		SUB r3, #8
		ADD r2, #8
		ADD r5, #8
		STR r4, [sp, #0x38]
		STR r5, [sp, #0x18]
		STR r2, [sp, #0x14]
		STR r3, [sp, #0xc]
		STR r7, [sp, #0x10]
		LDR r1, [r1, #0x2c]
		LDR r5, [pc, #0x16c]
		BL       |loc_08009324|
		CMP r0, #0
		DCW     0xD047
		ADD r2, sp, #8
		MOV r1, #0
		LDR r0, [r5]
		BL       |loc_08011C0C|
		CMP r0, #0
		DCW     0xD026
		MOV r0, #0x36
		BL       |inc_0x0158_0x143f2|
		LDR r5, [pc, #0x164]
		ADD r1, r0, #0
		LDR r0, [r5]
		BL       |loc_0800EDF8|
		LDR r5, [r5]
		MOV r0, #4
		DCW     0xF014
		DCW     0xFE9B
		CMP r0, #0
		BEQ      |loc_0802888A|
		LDR r1, [pc, #0x154]
		STR r1, [r0]
|loc_0802888A|
		ADD r7, r0, #0
		MOV r1, #0
		ADD r0, r5, #0
		BL       |Record_SelectIndexed|
		ADD r1, r7, #0
		ADD r0, r5, #0
		BL       |loc_0800ED18|
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0x2348
		DCW     0xE000
|loc_080288A4|
|unk_080288A4|
; cited by 0x080286F2 (a pc-relative load targets 0x080289BC)
		B        |loc_08028962|
		LDR r5, [pc, #0x130]
		LDR r1, [r5]
		STRB r0, [r1, #0x11]
		MOV r0, #0xff
		LDR r1, [pc, #0x130]
		ADD r0, #0x2d
		STR r0, [r1]
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
		LDR r0, [r4, #0x40]
		CMP r0, #0x40
		BGE      |loc_080288C6|
		ADD r0, #4
		STR r0, [r4, #0x40]
		B        |loc_080288DE|
		B        |loc_080288F0|
|loc_080288C6|
		LDR r0, [r4, #0x38]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #4]
		STR r0, [sp]
		LDR r2, [r4, #0x20]
		ADD r0, r2, r0
		STR r0, [r4, #0x20]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
|loc_080288DE|
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		CMP r0, #0xf0
		BLE      |loc_08028962|
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
|loc_080288F0|
		LDR r0, [r4, #0x40]
		LDR r2, [r4, #0x38]
		LDR r3, [r4, #0x3c]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x34]
		ADD r2, r3, #0
		STR r3, [sp, #0x38]
		LDR r3, [r4, #0x20]
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x34]
		ADD r2, r3, r2
		ADD r3, r0, #0
		ADD r0, #8
		ADD r5, r2, #0
		SUB r5, #8
		SUB r3, #8
		STR r2, [sp, #0x38]
		ADD r2, #8
		STR r0, [sp, #0x34]
		STR r2, [sp, #0x38]
		STR r3, [sp, #0x2c]
		STR r5, [sp, #0x30]
		LDR r1, [r1, #0x2c]
		ADD r0, sp, #0x2c
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_08028932|
		STRB r6, [r4, #0x10]
		B        |loc_08028962|
|loc_08028932|
		LDR r0, [r4, #0x40]
		CMP r0, #0x40
		BGE      |loc_0802893E|
		ADD r0, #4
		STR r0, [r4, #0x40]
		B        |loc_08028956|
|loc_0802893E|
		LDR r0, [r4, #0x38]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #0x28]
		STR r0, [sp, #0x24]
		LDR r2, [r4, #0x20]
		ADD r0, r2, r0
		STR r0, [r4, #0x20]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
|loc_08028956|
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		CMP r0, #0xf0
		BLE      |loc_08028962|
		STRB r6, [r4, #0x10]
