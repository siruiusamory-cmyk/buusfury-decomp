	CODE16
|sub_08009856|
|unk_08009856|
; cited by 0x004FDA02 (a pool word names 0x080098C0)
		LDR r0, [r6]
		LSR r2, r0, #3
		LSL r2, r2, #3
		STR r2, [sp, #0xc]
		LDR r0, [r6, #4]
		LSR r0, r0, #3
		LSL r0, r0, #3
		STR r0, [sp, #0x10]
		MOV r6, #0
|loc_08009868|
		ADD r4, r6, #0
		ADD r6, #1
		ADD r0, r4, #0
		BL       |sub_0803FAF6|
		LSL r1, r0, #0x1f
		BPL      |loc_08009898|
		ADD r3, r0, #0
		MUL r3, r0
		ADD r1, r3, r0
		CMP r1, r4
		BLT      |loc_0800988C|
		ADD r0, #1
		ASR r1, r0, #1
		SUB r0, r4, r3
		SUB r2, r0, r1
		ADD r2, #1
		B        |loc_080098B8|
|loc_0800988C|
		ADD r1, r0, #1
		ASR r2, r1, #1
		SUB r1, r2, r4
		ADD r1, r1, r3
		ADD r1, r1, r0
		B        |loc_080098B8|
|loc_08009898|
		ADD r3, r0, #0
		MUL r3, r0
		ADD r1, r3, r0
		CMP r1, r4
		BLT      |loc_080098AE|
		NEG r1, r0
		ASR r1, r1, #1
		SUB r2, r1, r4
		ADD r2, r2, r3
		ADD r2, r2, r0
		B        |loc_080098B8|
|loc_080098AE|
		NEG r1, r0
		ASR r2, r1, #1
		SUB r1, r4, r3
		SUB r0, r1, r0
		ADD r1, r0, r2
|loc_080098B8|
		LSL r0, r1, #3
		LSL r1, r2, #3
		LDR r2, [sp, #0xc]
		STR r0, [sp, #4]
		ADD r2, r2, r0
		LDR r0, [sp, #0x10]
		STR r1, [sp, #8]
		ADD r0, r0, r1
		STR r0, [sp, #8]
		STR r0, [sp, #0x18]
		STR r2, [sp, #4]
		STR r2, [sp, #0x14]
		LDR r1, [r5]
		ADD r0, r2, r1
		LDR r1, [sp, #0x18]
		LDR r2, [r5, #4]
		STR r0, [sp, #4]
		ADD r1, r1, r2
		STR r0, [sp, #0x1c]
		STR r1, [sp, #8]
		STR r1, [sp, #0x20]
		LDR r1, [r7, #0x28]
		ADD r0, sp, #0x14
		BL       |loc_08009324|
		CMP r0, #0
		BEQ      |loc_08009868|
		ADD r4, sp, #0x14
		LDMIA r4!, {r1, r2, r3, r4}
		LDR r0, [sp, #0x24]
		STMIA r0!, {r1, r2, r3, r4}
		B        |inc_0x0158_0x143f2| + 0x96fa
	INCBIN  baserom.gba_0x98f8_0x98fa.extracted
|sub_080098FA|
	DCW      0x0807
	DCW      0x0040
	DCW      0x0400
	DCW      0x0050
	DCW      0x0400
