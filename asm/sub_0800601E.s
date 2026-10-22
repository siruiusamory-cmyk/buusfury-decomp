	CODE16
|sub_0800601E|
|unk_0800601E|
		LSL r3, r2, #0x18
		LSR r3, r3, #0x1f
		BEQ      |loc_08006042|
		LDR r3, [r4, #0x10]
		CMP r3, #0
		BLT      |loc_08006042|
		ADD r3, r5, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #4]
		LDR r1, [r4, #0x10]
		ADD r0, #0xff
		ADD r0, #1
		ADD r0, #0xc
		STMIA r0!, {r1, r5}
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x5ec4
|loc_08006042|
		LSL r3, r2, #0x1a
		LSR r3, r3, #0x1f
		BEQ      |loc_08006066|
		LDR r3, [r4, #0x14]
		CMP r3, #0
		BLT      |loc_08006066|
		ADD r3, r5, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #4]
		LDR r1, [r4, #0x14]
		ADD r0, #0xff
		ADD r0, #1
		ADD r0, #0xc
		STMIA r0!, {r1, r5}
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x5ec4
|loc_08006066|
		LSL r2, r2, #0x1b
		LSR r2, r2, #0x1f
		BEQ      |loc_0800608A|
		LDR r2, [r4, #0x18]
		CMP r2, #0
		BLT      |loc_0800608A|
		ADD r3, r5, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #4]
		LDR r1, [r4, #0x18]
		ADD r0, #0xff
		ADD r0, #1
		ADD r0, #0xc
		STMIA r0!, {r1, r5}
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x5ec4
|loc_0800608A|
|unk_0800608A|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x18]
		ADD r1, r2, r1
	INCBIN  baserom.gba_0x6092_0x6094.extracted
|sub_08006094|
|unk_08006094|
	INCBIN	baserom.gba_0x6094_0x6098.extracted
	ADR      r2, |loc_0800617C|
	LSR      r4, r0, #0x20
	LSL      r0, r7, #4
	LSR      r7, r0, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x1f0]
	LSR      r1, r6, #0x20
