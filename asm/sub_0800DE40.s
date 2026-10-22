	CODE16
|sub_0800DE40|
|unk_0800DE40|
		LSR r1, r1, #2
		LDR r2, [pc, #0x18]
		LSL r1, r1, #2
		LDR r1, [r2, r1]
		LDR r2, [r0, #0x38]
		CMP r2, r1
		BEQ      |inc_0x0158_0x143f2| + 0xdce6
		BL       |sub_0800EECC|
		B        |inc_0x0158_0x143f2| + 0xdce6
