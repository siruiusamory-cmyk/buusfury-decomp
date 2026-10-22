	CODE16
|sub_0800B386|
|unk_0800B386|
; cited by 0x0800B32C (a pc-relative load targets 0x0800B51C)
		LDR r0, [r6, #4]
		LDR r5, [r6]
		ADD r7, r0, #0
		ADD r0, #0x20
		STR r0, [r6, #4]
		LDR r0, [r6, #8]
		MOV r1, #1
		ADD r2, r0, #0
		ADD r0, #1
		STR r0, [r6, #8]
		STR r2, [sp, #4]
		LDR r3, [r4, #0x50]
		LSL r1, r1, #0xb
		ADD r0, r3, #0
		STR r3, [sp, #0x20]
		BL       |Thunk_SignedDivide|
		STR r0, [sp]
		LDR r3, [sp, #0x20]
		LDR r1, [r4, #0x5c]
		SUB r3, #8
		MOV ip, r3
		MUL r1, r3
		LDR r3, [pc, #0x170]
		LDR r2, [r4, #0x60]
		STR r3, [r5]
		LDR r0, [r4, #0x68]
		LDR r3, [r4, #0x50]
		ADD r2, #0xe0
		MUL r0, r3
		MOV r3, ip
		LSL r3, r3, #5
		ADD r0, r0, r3
		SUB r0, r0, r1
		STR r3, [sp, #0x1c]
		STR r3, [sp, #0x18]
		ASR r3, r0, #0x1f
		LSR r3, r3, #0x1d
		ADD r0, r3, r0
		ASR r0, r0, #3
		LSL r0, r0, #0x17
		LDR r3, [pc, #0x14c]
		LSR r0, r0, #7
		ORR r0, r3
		LSL r3, r2, #0x18
		LSR r3, r3, #0x18
		LSR r0, r0, #8
		LSL r0, r0, #8
		ORR r0, r3
		STR r3, [sp, #0x14]
		STR r3, [sp, #0x10]
		STR r0, [r5]
		ADD r3, r0, #0
		ADD r0, r4, #0
		ADD r0, #0x60
		MOV lr, r0
		LDRH r0, [r0, #0x18]
		LDR r2, [r5, #4]
		LSR r2, r2, #0xa
		LSL r0, r0, #0x16
		LSR r0, r0, #0x16
		LSL r2, r2, #0xa
		ORR r0, r2
		MOV r2, #0x1f
		LSL r2, r2, #0x19
		BIC r3, r2
		STR r0, [r5, #4]
		LDR r2, [sp, #4]
		ADD r0, r3, #0
		LSL r2, r2, #0x1b
		LSR r2, r2, #2
		STR r2, [sp, #0xc]
		STR r2, [sp, #8]
		ORR r0, r2
		LDR r2, [pc, #0x10c]
		STR r0, [r5]
		STR r2, [r5, #8]
		LDR r2, [r4, #0x6c]
		LDR r3, [r4, #0x50]
		ADD r0, r5, #0
		MUL r2, r3
		LDR r3, [sp, #0x18]
		ADD r0, #8
		ADD r2, r2, r3
		SUB r2, r2, r1
		ASR r3, r2, #0x1f
		LSR r3, r3, #0x1d
		ADD r2, r3, r2
		ASR r2, r2, #3
		LSL r2, r2, #0x17
		LDR r3, [pc, #0xec]
		LSR r2, r2, #7
		ORR r2, r3
		LSR r2, r2, #8
		LDR r3, [sp, #0x10]
		LSL r2, r2, #8
		ORR r2, r3
		STR r2, [r0]
		ADD r5, r2, #0
		MOV r2, lr
		LDRH r2, [r2, #0x1a]
		LDR r3, [r0, #4]
		LSR r3, r3, #0xa
		LSL r2, r2, #0x16
		LSR r2, r2, #0x16
		LSL r3, r3, #0xa
		ORR r2, r3
		STR r2, [r0, #4]
		ADD r2, r5, #0
		MOV r5, #0x1f
		LSL r5, r5, #0x19
		BIC r2, r5
		ADD r3, r2, #0
		LDR r2, [sp, #8]
		LDR r5, [pc, #0xc0]
		ORR r2, r3
		STR r2, [r0]
		ADD r0, #8
		STR r5, [r0]
		LDR r2, [r4, #0x70]
		LDR r3, [r4, #0x50]
		MUL r2, r3
		MOV r3, ip
		LSL r3, r3, #4
		ADD r2, r2, r3
		SUB r2, r2, r1
		ASR r3, r2, #0x1f
		LSR r3, r3, #0x1d
		ADD r2, r3, r2
		ASR r2, r2, #3
		LSL r2, r2, #0x17
		LSR r2, r2, #7
		ORR r2, r5
		LSR r2, r2, #8
		LDR r3, [sp, #0x10]
		LSL r2, r2, #8
		ORR r2, r3
		STR r2, [r0]
		ADD r5, r2, #0
		MOV r2, lr
		LDRH r2, [r2, #0x1c]
		LDR r3, [r0, #4]
		LSR r3, r3, #0xa
		LSL r2, r2, #0x16
		LSR r2, r2, #0x16
		LSL r3, r3, #0xa
		ORR r2, r3
		STR r2, [r0, #4]
		ADD r2, r5, #0
		MOV r5, #0x1f
		LSL r5, r5, #0x19
		LDR r3, [sp, #8]
		BIC r2, r5
		ORR r2, r3
		STR r2, [r0]
		LDR r2, [r4, #0x24]
		ADD r0, #8
		CMP r2, #0
		BEQ      |loc_0800B50A|
		LDR r3, [pc, #0x60]
		STR r3, [r0]
		LDR r2, [r4, #0x74]
		LDR r4, [r4, #0x50]
		MUL r2, r4
		LDR r4, [sp, #0x1c]
		ADD r2, r2, r4
		SUB r1, r2, r1
		ASR r2, r1, #0x1f
		LSR r2, r2, #0x1d
		ADD r1, r2, r1
		ASR r1, r1, #3
		LSL r1, r1, #0x17
		LSR r1, r1, #7
		ORR r1, r3
		LSR r1, r1, #8
		LDR r3, [sp, #0x14]
		LSL r1, r1, #8
		ORR r1, r3
		STR r1, [r0]
		MOV r2, lr
		LDRH r2, [r2, #0x1e]
		LDR r3, [r0, #4]
		LSR r3, r3, #0xa
		LSL r2, r2, #0x16
		LSR r2, r2, #0x16
		LSL r3, r3, #0xa
		ORR r2, r3
		STR r2, [r0, #4]
		ADD r2, r5, #0
		BIC r1, r2
		LDR r2, [sp, #0xc]
		ORR r1, r2
		STR r1, [r0]
		ADD r0, #8
|loc_0800B50A|
		LDR r1, [sp]
		MOV r2, #0
		STRH r1, [r7, #6]
		STRH r2, [r7, #0xe]
		STRH r2, [r7, #0x16]
		STRH r1, [r7, #0x1e]
		STR r0, [r6]
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xb22a
		DCD     0x08071720
		DCD     0x03002A60
		DCD     0x0800AE65
		DCD     0xC0002100
		DCD     0xC000A100
