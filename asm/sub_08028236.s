	CODE16
|sub_08028236|
|unk_08028236|
; cited by 0x08028136 (a pc-relative load targets 0x08028368)
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
		LDR r0, [r4, #0x14]
		LSL r1, r1, #0xb
		STR r0, [sp, #0x10]
		BL       |sub_08046E58|
		MOV ip, r0
		LDR r0, [sp, #0x10]
		LDR r2, [pc, #0x12c]
		SUB r0, #8
		MOV lr, r0
		LSL r3, r0, #4
		STR r2, [r5]
		LDR r1, [r4, #0x14]
		SUB r0, r3, r0
		LSL r3, r1, #2
		ADD r1, r3, r1
		MOV r3, lr
		LSL r2, r3, #5
		LSL r1, r1, #3
		ADD r1, r1, r2
		LSL r0, r0, #3
		SUB r1, r1, r0
		STR r2, [sp, #0xc]
		ASR r2, r1, #0x1f
		LSR r2, r2, #0x1d
		ADD r1, r2, r1
		ASR r1, r1, #3
		LSL r1, r1, #0x17
		LDR r2, [pc, #0x100]
		LSR r1, r1, #7
		ORR r1, r2
		LSR r1, r1, #8
		LSL r1, r1, #8
		ADD r1, #0x30
		STR r1, [r5]
		LDRH r2, [r4, #0xc]
		ADD r3, r1, #0
		LDR r1, [r5, #4]
		LSL r2, r2, #0x16
		LSR r1, r1, #0xa
		LSL r1, r1, #0xa
		LSR r2, r2, #0x16
		ORR r1, r2
		MOV r2, #0x1f
		LSL r2, r2, #0x19
		BIC r3, r2
		STR r1, [r5, #4]
		LDR r2, [sp, #4]
		ADD r1, r3, #0
		LSL r2, r2, #0x1b
		LSR r2, r2, #2
		STR r2, [sp, #8]
		ORR r1, r2
		LDR r2, [pc, #0xd0]
		STR r1, [r5]
		STR r2, [r5, #8]
		LDR r2, [r4, #0x14]
		MOV r3, #0x68
		MUL r2, r3
		LDR r3, [sp, #0xc]
		ADD r1, r5, #0
		ADD r2, r2, r3
		SUB r2, r2, r0
		ASR r3, r2, #0x1f
		LSR r3, r3, #0x1d
		ADD r2, r3, r2
		ASR r2, r2, #3
		LSL r2, r2, #0x17
		LDR r3, [pc, #0xb0]
		LSR r2, r2, #7
		ORR r2, r3
		LSR r2, r2, #8
		LSL r2, r2, #8
		ADD r2, #0x30
		ADD r1, #8
		STR r2, [r1]
		ADD r5, r2, #0
		LDRH r2, [r4, #0xc]
		LDR r3, [r1, #4]
		ADD r2, #0x80
		LSL r2, r2, #0x16
		LSR r3, r3, #0xa
		LSL r3, r3, #0xa
		LSR r2, r2, #0x16
		ORR r2, r3
		STR r2, [r1, #4]
		ADD r2, r5, #0
		MOV r5, #0x1f
		LSL r5, r5, #0x19
		BIC r2, r5
		ADD r3, r2, #0
		LDR r2, [sp, #8]
		LDR r5, [pc, #0x84]
		ORR r2, r3
		STR r2, [r1]
		ADD r1, #8
		STR r5, [r1]
		LDR r2, [r4, #0x14]
		MOV r3, #0xa8
		MUL r2, r3
		MOV r3, lr
		LSL r3, r3, #4
		ADD r2, r2, r3
		SUB r0, r2, r0
		ASR r2, r0, #0x1f
		LSR r2, r2, #0x1d
		ADD r0, r2, r0
		ASR r0, r0, #3
		LSL r0, r0, #0x17
		LSR r0, r0, #7
		ORR r0, r5
		LSR r0, r0, #8
		LSL r0, r0, #8
		ADD r0, #0x30
		STR r0, [r1]
		LDRH r2, [r4, #0xc]
		LDR r3, [r1, #4]
		ADD r2, #0xff
		ADD r2, #1
		LSL r2, r2, #0x16
		LSR r3, r3, #0xa
		LSL r3, r3, #0xa
		LSR r2, r2, #0x16
		ORR r2, r3
		STR r2, [r1, #4]
		MOV r2, #0x1f
		LSL r2, r2, #0x19
		BIC r0, r2
		LDR r2, [sp, #8]
		ORR r0, r2
		STR r0, [r1]
		MOV r0, ip
		STRH r0, [r7, #6]
		MOV r2, #0
		STRH r2, [r7, #0xe]
		STRH r2, [r7, #0x16]
		STRH r0, [r7, #0x1e]
		ADD r1, #8
		STR r1, [r6]
		MOV r0, #0
		DCW     0xE765
	DCB	0x00,0x00
	DCD	0x08028035
	DCD	0x08049680
	DCD	0x0874EA54
	DCD	0x0804C9C8
	DCD	0x0802812D
	DCD	0x08071758
	DCD	0x0803F70D
	DCD	0x0806BCE8
		DCD     0xC0002100
		DCD     0xC000A100
