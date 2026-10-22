	CODE16
|sub_0802BC40|
|unk_0802BC40|
		MOV r1, #0
		MOV r2, #0xff
|loc_0802BC44|
		ADD r3, r0, r1
		ADD r1, #1
		CMP r1, #5
		STRB r2, [r3, #0x10]
		BLT      |loc_0802BC44|
		LDRH r0, [r0, #0xc]
		LDR r1, [pc, #0x14]
		MOV r2, #1
		LSL r0, r0, #5
		ADD r0, r0, r1
		LDR r1, [pc, #0x10]
		LSL r2, r2, #0xa
		BL       |Thunk_VramCopy|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xf2
|loc_0802BC64|
|unk_0802BC64|
; cited by 0x0802BC50 (a pc-relative load targets 0x0802BC68)
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xf2
		DCD     VRAM + 0x10000
		DCD     0x08753008
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r1, #0
		MOV r1, #0x87
		LDR r6, [pc, #0xc0]
		LDR r2, [pc, #0xc0]
		LSL r1, r1, #2
		ADD r5, r0, #0
		LDR r0, [r6]
		ADD r1, r1, r2
		LDR r7, [pc, #0xbc]
		MOV r2, #0x40
		MOV r3, #0
		ADD r0, r0, r7
		SUB sp, #0x1c
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r4, [r4, #4]
		LDR r0, [r4, #0x14]
		LDR r1, [r0]
		LDR r2, [r1, #0x14]
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		STR r0, [r5, #0x10]
		CMP r0, #0
		BEQ      |loc_0802BCAA|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xf3e4
|loc_0802BCAA|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x30]
		ADD r3, r2, r1
		MOV r2, #1
		MOV r1, #0xd
		BL       |inc_0x042118_0x049114| + 0x498e
		LDR r0, [r5, #0xc]
		CMP r0, #0
		BGE      |sub_0802BCCE|
		NEG r0, r0
		MOV r3, #0x2c
		LDR r1, [pc, #0x7c]
		MUL r0, r3
		ADD r5, r0, r1
		ADD r5, #4
		B        |inc_0x2bb4c_0x2d1c0| + 0x18c
