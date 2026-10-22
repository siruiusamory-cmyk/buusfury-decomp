	CODE16
|sub_080257DA|
|unk_080257DA|
		LDR r3, [pc, #0x304]
		LDR r0, [r3, #8]
		LDRB r0, [r0, #1]
		LSL r0, r0, #0x19
		LSR r0, r0, #0x1f
		DCW     0xD055
		ADD r0, r5, #4
		ADD r6, r5, #0
		ADD r6, #0x24
