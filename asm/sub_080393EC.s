	CODE16
|sub_080393EC|
|unk_080393EC|
		LDR r0, [pc, #0x40]
		MOV r1, #1
		STR r0, [r4]
		LSL r1, r1, #9
		ADD r1, r5, r1
		LDR r1, [r1, #4]
		LDR r2, [pc, #0x38]
		MOV r0, #0xff
		LSL r1, r1, #3
		ADD r1, r1, r2
		ADD r0, #0xa1
		LDR r0, [r0, r5]
		SUB r1, #0x40
		LDR r2, [r1, #0x38]
		ASR r0, r0, #8
		ADD r2, r0, r2
		LDR r0, [pc, #0x28]
		STR r2, [r0, #0x10]
		MOV r2, #0xff
		ADD r2, #0xa5
		LDR r2, [r2, r5]
		LDR r1, [r1, #0x3c]
		ASR r2, r2, #8
		ADD r1, r2, r1
		STR r1, [r0, #0x14]
		ADD r1, r5, #0
		DCD     0xFE70F7F4
		STR r0, [r4, #4]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x422a
	INCBIN  baserom.gba_0x3942a_0x3942e.extracted
