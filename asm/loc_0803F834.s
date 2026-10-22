	CODE16
|loc_0803F834|
|unk_0803F834|
		LDR r1, [sp]
		ADD r1, #4
		STR r1, [sp]
		LDR r1, [r1]
		LDR r2, [sp, #0x108]
		LSR r1, r2
		LDR r2, [sp, #0x104]
		AND r1, r2
		ADD r2, r7, #0
		ADD r3, r0, #0
		ORR r3, r1
		BEQ      |loc_0803F86C|
|loc_0803F84C|
		LSL r3, r0, #0x1f
		BPL      |loc_0803F856|
		LDRB r3, [r4, #3]
		STRB r3, [r2]
		B        |loc_0803F85E|
|loc_0803F856|
		LSL r3, r1, #0x1f
		BPL      |loc_0803F85E|
		LDRB r3, [r4, #2]
		STRB r3, [r2]
|loc_0803F85E|
		LDR r3, [r4, #0x28]
		LSR r0, r0, #1
		ASR r1, r1, #1
		ADD r2, r3, r2
		ADD r3, r0, #0
		ORR r3, r1
		BNE      |loc_0803F84C|
|loc_0803F86C|
		MOV r0, lr
		ADD r0, #4
		MOV lr, r0
		B        |sub_0803F876|
|loc_0803F874|
		DCW     0xE00B
