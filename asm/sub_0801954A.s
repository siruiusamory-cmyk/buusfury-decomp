	CODE16
|sub_0801954A|
|unk_0801954A|
		MOV r5, #1
		LSL r5, r5, #0xc
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		LSR r1, r5, #2
		STR r1, [sp, #4]
		ADD r0, r0, r5
		STR r0, [sp]
		ADD r1, r6, #0
		MOV r3, #4
		ADD r0, r4, #0
		STR r7, [sp, #8]
		LDR r2, [pc, #0xc]
		BL       |loc_0802A81C|
		LDR r0, [pc, #0xc]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x4154
