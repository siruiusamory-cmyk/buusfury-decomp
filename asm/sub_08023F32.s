	CODE16
|sub_08023F32|
|unk_08023F32|
		CMP r0, #4
		BHS      |loc_08023F3C|
		MOV r0, #0
		STRB r0, [r1, #0x11]
		DCW     0xE7F8
|loc_08023F3C|
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1e
		STRB r0, [r1, #0x11]
		BNE      |loc_08023F48|
		MOV r0, #2
		STRB r0, [r1, #0x11]
|loc_08023F48|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r2}
		LDR r0, [r0]
		ASR r2, r2, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r2, #0
		STR r2, [sp, #4]
		LDR r2, [sp, #8]
		STR r0, [sp, #0xc]
		STR r2, [sp, #0x10]
		LDRB r0, [r1, #0x10]
		LDR r2, [pc, #0xc4]
		LSL r0, r0, #3
		ADD r0, r0, r2
		LDR r2, [sp, #0xc]
		LDR r3, [r0]
		ADD r2, r2, r3
		LDR r3, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r2, [sp, #4]
		ADD r0, r3, r0
		STR r0, [sp, #8]
		ADD r0, r2, #0
		LDR r2, [sp, #8]
		STR r0, [sp, #0x14]
		ADD r0, sp, #0x14
		STR r2, [sp, #0x18]
	INCBIN  baserom.gba_0x23f84_0x23f86.extracted
|sub_08023F86|
|unk_08023F86|
	INCBIN	baserom.gba_0x23f86_0x23f8a.extracted
|dat_08023F8A|
	DCW      0x4828