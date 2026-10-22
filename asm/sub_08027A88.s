	CODE16
|sub_08027A88|
|unk_08027A88|
		LDR r2, [r1]
		ADD r3, r2, #0
		ADD r3, #8
		STR r3, [r1]
		LDR r3, [r1, #4]
		ADD r6, r3, #0
		ADD r6, #0x20
		STR r6, [r1, #4]
		LDR r6, [r1, #8]
		ADD r7, r6, #1
		STR r7, [r1, #8]
		MOV r1, #0x23
		LSL r1, r1, #8
		STR r1, [r2]
		MOV r1, #0xff
		ADD r1, #0xa1
		LDR r1, [r1, r4]
		LDR r7, [r0, #0x18]
		ASR r1, r1, #8
		MUL r1, r7
		LDR r7, [r0, #0x10]
		ASR r1, r1, #0x16
		ADD r7, r1, r7
		MOV r1, #0x23
		LSL r7, r7, #0x17
		LSR r7, r7, #7
		LSL r1, r1, #8
		ORR r1, r7
		STR r1, [r2]
		ADD r4, #0xff
		ADD r4, #0xa5
		LDR r4, [r4]
		LDR r7, [r0, #0x1c]
		ASR r4, r4, #8
		MUL r4, r7
		LDR r7, [r0, #0x14]
		ASR r4, r4, #0x16
		ADD r4, r4, r7
		LSL r4, r4, #0x18
		LSR r1, r1, #8
		LSL r1, r1, #8
		LSR r4, r4, #0x18
		ORR r1, r4
		MOV r4, #0x1f
		LSL r4, r4, #0x19
		BIC r1, r4
		LSL r4, r6, #0x1b
		LSR r4, r4, #2
		ORR r1, r4
		STR r1, [r2]
		LDRH r0, [r0, #0xc]
		LDR r1, [r2, #4]
		LSR r1, r1, #0xa
		LSL r0, r0, #0x16
		LSR r0, r0, #0x16
		LSL r1, r1, #0xa
		ORR r0, r1
		STR r0, [r2, #4]
		LDR r1, [r5, #0x44]
		ASR r1, r1, #2
		STRH r1, [r3, #6]
		LDR r1, [r5, #0x48]
		ASR r1, r1, #2
		STRH r1, [r3, #0x16]
		LDR r1, [r5, #0x4c]
		ASR r1, r1, #2
		STRH r1, [r3, #0xe]
		LDR r0, [r5, #0x50]
		ASR r0, r0, #2
		STRH r0, [r3, #0x1e]
		MOV r0, #0
		DCW     0xE7B5
