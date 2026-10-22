	CODE16
|sub_08030A0C|
|unk_08030A0C|
		LDR r1, [pc, #0x94]
		ADD r0, r4, #0
		BL       |inc_0x301c0_0x311c0| + 0x38
		LDR r0, [pc, #0x90]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0x24]
		STR r0, [r4, #0x2c]
		MOV r0, #0x29
		LSL r0, r0, #4
		MUL r0, r5
		ASR r0, r0, #8
		STR r0, [r4, #0x28]
		ADD r0, r4, #0
		B        |inc_0x301c0_0x311c0| + 0x84a
		LDR r1, [r0, #0x2c]
		CMP r1, #0
		BEQ      |inc_0x301c0_0x311c0| + 0x888
		LDR r1, [pc, #0x78]
		LDR r1, [r1, #4]
		LSL r1, r1, #0x1d
		BPL      |sub_08030A42|
		LDR r1, [r0, #0x24]
		ASR r1, r1, #8
		STR r1, [r0, #0x1c]
		B        |inc_0x301c0_0x311c0| + 0x888
