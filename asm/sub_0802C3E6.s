	CODE16
|sub_0802C3E6|
|unk_0802C3E6|
; cited by 0x0802C344 (a pc-relative load targets 0x0802C3E8)
		LDR r7, [pc, #0x70]
		LDR r0, [r7]
		BL       |loc_080116FC|
		MOV r6, #1
		LSL r6, r6, #0xa
		CMP r0, r6
		BLT      |loc_0802C442|
		LSL r5, r6, #2
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r5, r0, r5
|loc_0802C400|
|unk_0802C400|
		ADD r0, sp, #0xc
		ADD r1, r4, #0
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
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r0, [sp, #8]
		MOV r2, #0x37
		STR r1, [sp, #0x1c]
		STR r0, [sp, #0x20]
		ADD r4, sp, #0x1c
		ADD r1, r4, #0
		STR r2, [sp, #8]
		MOV r3, #4
		MOV r0, #0
		LDR r2, [pc, #0x28]
		STR r5, [sp]
		STR r6, [sp, #4]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [r7]
		BL       |List_Append|
|loc_0802C442|
		MOV r0, #1
		B        |inc_0x2bb4c_0x2d1c0| + 0x896
