	CODE16
|sub_0803937C|
|unk_0803937C|
		LDR r0, [pc, #0x44]
		MOV r2, #1
		STR r0, [r4]
		LSL r2, r2, #9
		ADD r2, r5, r2
		LDR r0, [pc, #0x40]
		LDR r2, [r2, #4]
		LDR r3, [pc, #0x40]
		LDR r1, [r0]
		MOV r0, #0xff
		LSL r2, r2, #3
		ADD r2, r2, r3
		ADD r0, #0xa1
		LDR r0, [r0, r1]
		SUB r2, #0x40
		LDR r3, [r2, #0x38]
		ASR r0, r0, #8
		ADD r3, r0, r3
		LDR r0, [pc, #0x2c]
		ADD r1, #0xff
		ADD r1, #0xa5
		STR r3, [r0, #0x10]
		LDR r1, [r1]
		LDR r2, [r2, #0x3c]
		ASR r1, r1, #8
		ADD r1, r1, r2
		STR r1, [r0, #0x14]
		ADD r1, r5, #0
		DCD     0xFEA6F7F4
		STR r0, [r4, #4]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x41ba
	INCBIN  baserom.gba_0x393be_0x393c2.extracted
