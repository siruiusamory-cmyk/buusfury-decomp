	CODE16
|sub_08022820|
|unk_08022820|
; cited by 0x080226E4 (a pc-relative load targets 0x080228FC)
		MOV r5, #2
		B        |loc_0802284A|
|loc_08022824|
		ASR r0, r4, #3
		ADD r0, r0, r6
		ADD r0, #0xff
		ADD r0, #1
		LSL r3, r4, #0x1d
		LSR r3, r3, #0x1d
		LDRB r1, [r0, #4]
		MOV r2, #2
		LSL r2, r3
		ORR r1, r2
		STRB r1, [r0, #4]
		ADD r0, sp, #8
		LDRB r1, [r0, r5]
		ADD r0, r4, #0
		ADD r0, r0, r6
		ADD r0, #0x80
		ADD r4, #1
		ADD r5, #1
		STRB r1, [r0, #4]
|loc_0802284A|
		LDR r0, [pc, #0xb0]
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x1c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, r5
		BGT      |loc_08022824|
		ADD r3, sp, #0
		LDRH r0, [r3, #0xc]
		LSL r0, r0, #0x14
		BPL      |loc_08022870|
		LDRH r0, [r3, #0xc]
		LSL r0, r0, #0x15
		LSR r0, r0, #0x18
		ADD r0, #1
		STR r0, [r7, #0x24]
|loc_08022870|
		LDR r1, [pc, #0x8c]
		LDR r0, [r7, #0x24]
		CMP r0, r1
		DCW     0xD0D1
		MOV r4, #0
		STR r4, [sp, #4]
		CMP r0, #0
		BLS      |loc_080228CC|
|loc_08022880|
		MOV r0, #0
		STR r0, [sp]
		MOV r5, #2
		B        |loc_080228A6|
|loc_08022888|
		ASR r0, r4, #3
		ADD r0, r0, r6
		ADD r0, #0xff
		ADD r0, #1
		LSL r2, r4, #0x1d
		LSR r2, r2, #0x1d
		LDRB r0, [r0, #4]
		MOV r1, #2
		LSL r1, r2
		AND r0, r1
		BEQ      |loc_080228A2|
		MOV r0, #1
		STR r0, [sp]
|loc_080228A2|
		ADD r4, #1
		ADD r5, #1
|loc_080228A6|
		LDR r0, [pc, #0x54]
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x1c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, r5
		BGT      |loc_08022888|
		LDR r0, [sp]
		CMP r0, #0
		DCW     0xD0AD
		LDR r1, [sp, #4]
		ADD r1, #1
		STR r1, [sp, #4]
		LDR r0, [r7, #0x24]
		CMP r0, r1
		BHI      |loc_08022880|
|loc_080228CC|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x1c]
		ADD r3, r2, r1
		LDR r1, [sp, #0x18]
		LDRB r2, [r1, #8]
		LDR r1, [sp, #0x10]
		BL       |inc_0x046118_0x049114| + 0x98e
		MOV r2, #0x80
		MOV r1, #0
		MVN r1, r1
		LDR r0, [sp, #0x10]
		BL       |sub_0804912C|
		MOV r2, #0x10
		MOV r1, #0
		LDR r0, [sp, #0x14]
		BL       |sub_0804912C|
		LDR r1, [pc, #8]
		STR r1, [r7, #0x24]
		DCW     0xE790
	INCBIN  baserom.gba_0x228fa_0x228fc.extracted
		DCD     0x0872BFA4
	INCBIN  baserom.gba_0x22900_0x22902.extracted
