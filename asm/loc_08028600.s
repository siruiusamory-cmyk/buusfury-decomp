	CODE16
|loc_08028600|
		LDR r0, [r5, #4]
		CMP r0, #1
		BEQ      |loc_0802860E|
		CMP r0, #4
		BEQ      |loc_0802860E|
		CMP r0, #7
		BNE      |loc_08028628|
|loc_0802860E|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [r6]
		MOV r2, #2
		SUB r0, r0, r1
		STR r0, [sp, #4]
		ADD r0, r4, #0
		ADD r1, sp, #4
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_08028628|
		LDR r0, [r5, #4]
		CMP r0, #2
		BEQ      |loc_08028636|
		CMP r0, #5
		BEQ      |loc_08028636|
		CMP r0, #8
		BNE      |loc_08028650|
|loc_08028636|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [r6]
		MOV r2, #2
		ADD r0, r0, r1
		STR r0, [sp, #4]
		ADD r0, r4, #0
		ADD r1, sp, #4
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_08028650|
		LDR r0, [r5, #4]
		CMP r0, #3
		BEQ      |loc_0802865E|
		CMP r0, #4
		BEQ      |loc_0802865E|
		CMP r0, #5
		BNE      |loc_08028676|
|loc_0802865E|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		STR r1, [sp, #4]
		LDR r2, [r6]
		ADD r1, sp, #4
		SUB r0, r0, r2
		STR r0, [sp, #8]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_08028676|
		LDR r0, [r5, #4]
		CMP r0, #6
		BEQ      |loc_08028684|
		CMP r0, #7
		BEQ      |loc_08028684|
		CMP r0, #8
		BNE      |loc_0802869C|
|loc_08028684|
		LDR r0, [r7, #4]
		LDR r1, [r7]
		STR r0, [sp, #8]
		STR r1, [sp, #4]
		LDR r2, [r6]
		ADD r1, sp, #4
		ADD r0, r0, r2
		STR r0, [sp, #8]
		MOV r2, #1
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x12808
|loc_0802869C|
		LDRH r0, [r4, #0x12]
		LDR r1, [pc, #0x18]
		ADD r0, #8
		LSL r0, r0, #0x19
		LSR r0, r0, #0x19
		STRH r0, [r4, #0x12]
		LDR r0, [r1]
		CMP r0, #0
		BGT      |loc_080286B0|
		DCW     0xE734
|loc_080286B0|
		SUB r0, #1
		STR r0, [r1]
		DCW     0xE731
	INCBIN  baserom.gba_0x286b6_0x286b8.extracted
		DCD     0x03002FE4
	INCBIN  baserom.gba_0x286bc_0x286d2.extracted
