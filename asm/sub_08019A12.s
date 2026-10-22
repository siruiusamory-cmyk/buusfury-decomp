	CODE16
|sub_08019A12|
|unk_08019A12|
		LDR r0, [r4, #0x4c]
		CMP r0, #0
		BNE      |loc_08019ACA|
		LDR r0, [r2, #0x30]
		CMP r0, r4
		BNE      |loc_08019A22|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x461c
|loc_08019A22|
		LDR r1, [r2, #0x1c]
		ADD r5, r2, #4
		LDRB r3, [r1]
		CMP r3, #1
		BNE      |loc_08019A64|
		LDR r2, [r5]
		LDR r6, [r4, #0x30]
		ADD r0, r5, #0
		CMP r2, r6
		BGE      |loc_08019A64|
		LDR r2, [r4, #0x28]
		LDR r6, [r0, #8]
		CMP r2, r6
		BGE      |loc_08019A64|
		LDR r2, [r0, #4]
		LDR r6, [r4, #0x34]
		CMP r2, r6
		BGE      |loc_08019A64|
		LDR r2, [r4, #0x2c]
		LDR r0, [r0, #0xc]
		CMP r2, r0
		BGE      |loc_08019A64|
		LDRB r0, [r1, #1]
		CMP r0, #0xd
		BNE      |loc_08019A58|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x461c
|loc_08019A58|
		MOV r0, #0x10
		STR r0, [r4, #0x4c]
		LDR r0, [pc, #0x98]
		STR r0, [r4, #0x18]
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x461c
|loc_08019A64|
		CMP r3, #0
		BNE      |loc_08019ACA|
		LDR r0, [r5]
		LDR r1, [r4, #0x30]
		CMP r0, r1
		BGE      |loc_08019ACA|
		LDR r0, [r4, #0x28]
		LDR r1, [r5, #8]
		CMP r0, r1
		BGE      |loc_08019ACA|
		LDR r0, [r5, #4]
		LDR r1, [r4, #0x34]
		CMP r0, r1
		BGE      |loc_08019ACA|
		LDR r0, [r4, #0x2c]
		LDR r1, [r5, #0xc]
		CMP r0, r1
		BGE      |loc_08019ACA|
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ASR r0, r0, #8
		STR r0, [sp]
		ASR r1, r1, #8
		LDR r0, [pc, #0x6c]
		LDR r5, [pc, #0x54]
		STR r1, [sp, #4]
		LDR r6, [r0]
		SUB r5, #0xc
		LDR r0, [r5, #4]
		BL       |loc_080116FC|
		MOV r1, #0xff
		ADD r1, #1
		CMP r0, r1
		BLT      |loc_08019ABE|
		MOV r3, #2
		ADD r2, r6, #0
		MOV r0, #0
		MOV r1, sp
		BL       |loc_080197B4|
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |List_Append|
|loc_08019ABE|
		ADD r1, r4, #0
		LDR r0, [r5, #4]
		BL       |loc_08011944|
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x461c
|loc_08019ACA|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x461c
|loc_08019ACE|
|unk_08019ACE|
		B        |loc_08019AD0|
|loc_08019AD0|
		STR r0, [r4, #0x58]
		STR r2, [r4, #0x60]
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x461c
|loc_08019AD8|
|unk_08019AD8|
		B        |loc_08019ADA|
|loc_08019ADA|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		B        |inc_0x153f2_0x1a3f2| + 0x461c
