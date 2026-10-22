	CODE16
|sub_0802C6B0|
|unk_0802C6B0|
		LDR r0, [pc, #0xcc]
		STR r0, [r4]
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r5, r0, #1
		MOV r0, #0xff
		ADD r0, #1
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r1, r0, #0
		ADD r1, #0x40
		LSL r1, r1, #0x18
		LDR r2, [pc, #0xb8]
		LSR r1, r1, #0x16
		LDR r1, [r2, r1]
		LSL r0, r0, #0x18
		MUL r1, r5
		ASR r1, r1, #0xa
		STR r1, [r4, #4]
		LSR r0, r0, #0x16
		LDR r0, [r2, r0]
		MUL r0, r5
		ASR r0, r0, #0xa
		STR r0, [r4, #8]
		MOV r0, #0
		STR r0, [r4, #0xc]
		STR r0, [r4, #0x10]
		ADD r0, r4, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xb62
