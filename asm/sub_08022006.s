	CODE16
|sub_08022006|
|unk_08022006|
		LDR r6, [pc, #0xbc]
		LDR r3, [pc, #0xc4]
		LDR r0, [r6, #0x14]
		ADD r0, #0xff
		ADD r0, #0x81
		LDR r1, [r0, #0x10]
		LSL r2, r1, #8
		LSR r2, r2, #0x16
		STRH r2, [r0, #0xc]
		LSL r2, r2, #4
		AND r1, r3
		ORR r1, r2
		LDR r2, [r7, #0x10]
		LDR r3, [pc, #0xb0]
		CMP r2, #0
		BNE      |loc_08022034|
		LDR r2, [r6]
		AND r1, r3
		LDRH r2, [r2, #2]
		LSL r2, r2, #0x16
		LSR r2, r2, #8
		ORR r1, r2
		B        |loc_08022036|
|loc_08022034|
		AND r1, r3
|loc_08022036|
		LSR r1, r1, #2
		LSL r1, r1, #2
		ADD r1, #1
		ADD r3, r1, #0
		MOV r2, #0xc
		ADD r1, #4
		AND r1, r2
		BIC r3, r2
		ORR r1, r3
		ADD r3, r1, #0
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1e
		LSL r1, r1, #2
		BIC r3, r2
		ORR r1, r3
		LSL r3, r2, #0x1b
		ADD r2, r1, #0
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1e
		LSL r1, r1, #0x1d
		BIC r2, r3
		ORR r2, r1
		ADD r3, r2, #0
		LSL r1, r3, #8
		LSR r1, r1, #8
		MOV r2, #0
		CMP r1, #0
		BEQ      |loc_08022078|
|loc_0802206E|
		LSL r7, r1, #0x1f
		BPL      |loc_08022074|
		ADD r2, #1
|loc_08022074|
		LSR r1, r1, #1
		BNE      |loc_0802206E|
|loc_08022078|
		MOV r1, #0x1f
		LSL r1, r1, #0x18
		BIC r3, r1
		LSL r1, r2, #0x1b
		LSR r1, r1, #3
		ORR r1, r3
		STR r1, [r0, #0x10]
		LDR r0, [r6, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x20]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_080220A6|
		LDR r0, [r6, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x14]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
|loc_080220A6|
		MOV r0, #0
		STR r0, [r4, #0x14]
|loc_080220AA|
|unk_080220AA|
; cited by 0x08021EBE (a pc-relative load targets 0x080220C4)
		LDR r0, [r4, #0x18]
		MOV r1, #1
		CMP r0, #4
		BLT      |loc_080220B4|
		SUB r1, #5
|loc_080220B4|
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		LDRH r1, [r4, #0xc]
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0x2ab8
		DCW     0xE7A0
	INCBIN  baserom.gba_0x220c2_0x220d8.extracted
