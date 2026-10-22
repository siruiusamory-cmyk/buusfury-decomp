	CODE16
|sub_08007C7C|
|unk_08007C7C|
		MOV r3, #1
		LSL r3, r3, #0xb
		ADD r3, sp
		LDR r3, [r3, #0x18]
		MOV r7, ip
		MUL r7, r3
		ADD r2, r7, r2
		LSL r3, r6, #2
		LDR r6, [pc, #0x1e8]
		ADD r6, sp
		STR r2, [r6, r3]
