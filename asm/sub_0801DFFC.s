	CODE16
|sub_0801DFFC|
|unk_0801DFFC|
; cited by 0x00436D96 (a pool word names 0x0801E010)
		MOV r1, #1
		LSL r1, r1, #0xa
		ADD r2, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x138]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0x40]
		MOV r0, #1
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		LDR r1, [r4, #0x1c]
		ADD r0, sp, #0xc
		BL       |loc_0800FE34|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #0x20]
		ASR r1, r1, #1
		STR r0, [sp, #8]
		LDR r0, [pc, #0x10c]
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		LDR r2, [sp, #0x20]
		STR r0, [r4, #0x18]
		LSL r1, r1, #8
		LSL r2, r2, #8
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x24]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [r4, #0x1c]
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #0x10]
		ADD r0, r1, #0
		STR r1, [sp, #0xc]
		LDR r1, [sp, #0x10]
		STR r0, [sp, #0x14]
		ADD r0, r1, #0
		STR r1, [sp, #0x18]
		LDR r1, [r4, #0x1c]
		ADD r1, #0xff
		ADD r1, #0x91
		LDRB r1, [r1, #0xd]
		LSR r1, r1, #1
		ADD r0, r0, r1
		ADD r0, #1
		STR r0, [r4, #4]
		ADD r0, r4, #0
		DCW     0xE7BB
		PUSH {r4, lr}
		ADD r4, r0, #0
		ADD r0, #0x40
		LDMIA r0!, {r0, r1}
		SUB sp, #0x20
		CMP r1, #0
		BEQ      |loc_0801E09C|
		ADD r0, #1
		STR r0, [r4, #0x40]
		CMP r0, #0x38
		BLT      |loc_0801E0AE|
		MOV r0, #0x18
		STR r0, [r4, #0x40]
		B        |loc_0801E0AE|
|loc_0801E09C|
		CMP r0, #0x18
		BLT      |sub_0801E0A6|
		MOV r0, #0x17
		STR r0, [r4, #0x40]
		B        |loc_0801E0AE|
