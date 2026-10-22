	CODE16
|sub_0804EE6C|
|unk_0804EE6C|
		MOV r0, #0
		BX       lr
		LDR r0, [pc, #0x18]
		LDR r0, [r0]
		LDR r1, [r0, #0x58]
		ADD r1, #0x54
		LDR r1, [r1, #0x54]
		LDR r0, [r0, #0x50]
		CMP r1, r0
		BNE      |sub_0804EE84|
		MOV r0, #1
		B        |inc_0x049120_0x055620| + 0x5d66
