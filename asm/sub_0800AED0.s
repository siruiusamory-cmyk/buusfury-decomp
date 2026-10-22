	CODE16
|sub_0800AED0|
|unk_0800AED0|
		LDR r0, [r4, #0x38]
		CMP r0, #0
		BEQ      |loc_0800AEF0|
		LDR r0, [pc, #0x1c4]
		LDR r1, [pc, #0x1c4]
		LDR r0, [r0]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |loc_0800AEEC|
		MOV r0, #0
		MVN r0, r0
		STR r0, [r1]
		B        |loc_0800AEF0|
|loc_0800AEEC|
		LDR r0, [r4, #0x34]
		STR r0, [r1]
|loc_0800AEF0|
		LDR r0, [pc, #0x1b0]
		STR r0, [r5, #0x34]
		B        |inc_0x0158_0x143f2| + 0xad74
|loc_0800AEF6|
|unk_0800AEF6|
		CMP r1, r0
		BNE      |loc_0800AF6C|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0xae44
		MOV r0, #0
		STR r0, [sp, #4]
		LDR r0, [r4, #0x14]
		ADD r1, sp, #0xc
		STR r0, [sp, #0xc]
		MOV r0, #0
		STR r0, [r4, #0x38]
		STR r0, [r4, #0x3c]
		STR r1, [sp, #0x18]
|loc_0800AF12|
		LDR r0, [r4, #0x4c]
		MOV r2, #0
		LDR r7, [r0, #4]
		LDR r1, [sp, #0x18]
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xaca8
		CMP r0, #0
		BEQ      |loc_0800AF32|
		LDR r0, [r4, #0x38]
		ADD r0, #1
		STR r0, [r4, #0x38]
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BNE      |loc_0800AF32|
		SUB r7, #0x14
|loc_0800AF32|
		ADD r2, r7, #0
		ADD r0, r5, #0
		ADD r3, sp, #8
		LDR r1, [sp, #0xc]
		BL       |inc_0x03d784_0x041118| + 0x6e6
		LDR r0, [sp, #4]
		ADD r0, #1
		STR r0, [sp, #4]
		LDR r1, [r4, #0x4c]
		LDR r1, [r1]
		CMP r0, r1
		BGE      |loc_0800AF52|
		LDR r0, [sp, #0x14]
		CMP r0, #0
		BEQ      |loc_0800AF12|
|loc_0800AF52|
		LDR r0, [r4, #0x28]
		CMP r0, #0
		LDR r0, [r4, #0x4c]
		BEQ      |inc_0x0158_0x143f2| + 0xae16
		ADD r1, r0, #0
		LDR r0, [r0, #0xc]
		LDR r1, [r1]
		LDR r2, [sp, #4]
		SUB r1, r1, r2
		LSL r3, r1, #3
		SUB r1, r3, r1
		ADD r0, r0, r1
		B        |inc_0x0158_0x143f2| + 0xae18
|loc_0800AF6C|
|unk_0800AF6C|
; cited by 0x0800ADAA (a pc-relative load targets 0x0800B098)
		B        |loc_0800B022|
		LDR r0, [r0, #0xc]
		STRB r0, [r6, #5]
		LDR r0, [r4, #0x38]
		CMP r0, #0
		BEQ      |loc_0800AFA2|
		LDR r0, [r4, #0x48]
		CMP r0, #0
		BNE      |loc_0800AFA2|
		MOV r1, #0
		CMP r4, #0
		BEQ      |loc_0800AF88|
		ADD r1, r4, #0
		ADD r1, #0xc
|loc_0800AF88|
		MOV r0, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x24d6
		ADD r1, r0, #0
		STR r0, [r4, #0x48]
		LDR r0, [pc, #0x108]
		LDR r0, [r0, #4]
		BL       |List_Append|
		B        |loc_0800AFA2|
		LDRB r0, [r6, #5]
		ADD r0, #0xe
		STRB r0, [r6, #5]
|loc_0800AFA2|
		LDR r0, [r4, #0x4c]
		ADD r1, r4, #0
		ADD r1, #0x14
		MOV r2, #1
		LDR r7, [r0, #4]
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xaca8
		STR r0, [sp, #4]
		CMP r0, #0
		BEQ      |loc_0800AFC0|
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BNE      |loc_0800AFC0|
		SUB r7, #0x14
|loc_0800AFC0|
		ADD r2, r7, #0
		ADD r0, r5, #0
		ADD r3, sp, #8
		LDR r1, [r4, #0x14]
		BL       |inc_0x03d784_0x041118| + 0x6e6
		LDR r0, [sp, #0x14]
		STR r0, [r4, #0x20]
		LDR r0, [sp, #8]
		STR r0, [r4, #0x14]
		LDR r0, [sp, #0xc]
		STR r0, [r4, #0x18]
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0xaed6
		LDR r0, [r4, #0x4c]
		LDR r0, [r0, #8]
		LDR r1, [sp, #0x10]
		SUB r1, r7, r1
		ASR r1, r1, #1
		ADD r0, r0, r1
		STRB r0, [r6, #4]
		LDR r0, [sp, #4]
		CMP r0, #0
		BEQ      |loc_0800B00C|
		LDR r1, [r4, #0x3c]
		ADD r0, r4, #0
		ADD r2, r1, #1
		LSL r1, r1, #1
		STR r2, [r4, #0x3c]
		ADD r0, #0x64
		LDRB r2, [r0]
		ADD r1, r1, r4
		ADD r3, r1, #0
		ADD r3, #0x40
		STRB r2, [r3]
		LDRB r2, [r0, #1]
		STRB r2, [r3, #1]
|loc_0800B00C|
		MOV r0, #0
		STR r0, [r4, #0x2c]
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		LDR r1, [r4, #0x4c]
		LDR r1, [r1]
		CMP r0, r1
		BLT      |loc_0800B022|
		MOV r0, #1
		STR r0, [r4, #0x20]
