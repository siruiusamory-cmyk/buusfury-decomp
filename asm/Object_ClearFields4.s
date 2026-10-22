	CODE16
|Object_ClearFields4|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r1, [r0, #4]
	BX       lr
|sub_0803B418|
|unk_0803B418|
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r0, [r0, #4]
		MOV r7, #1
		ADD r4, r1, #0
		CMP r0, #0
		SUB sp, #0x1c
		BNE      |inc_0x351c0_0x3d4d0| + 0x62f6
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r2, r4, #0
		ADD r2, #0xff
		ADD r2, #0xa1
		ADD r1, r2, #4
		LDR r3, [pc, #0xa8]
		MOV r6, #0
		CMP r0, #0
		LDR r0, [r3]
		BEQ      |sub_0803B46A|
		ADD r0, #0xff
		LSL r3, r7, #0xa
		STR r6, [sp, #0x10]
		STR r3, [sp, #0xc]
		ADD r0, #0xa1
		LDMIA r0!, {r3}
		LDR r0, [r0]
		LSL r6, r7, #0xa
		ADD r3, r3, r6
		STR r0, [sp, #8]
		ADD r0, r3, #0
		STR r3, [sp, #4]
		LDR r3, [sp, #8]
		STR r0, [sp, #0x14]
		STR r3, [sp, #0x18]
		STR r0, [r2]
		LDR r0, [sp, #0x18]
		STR r0, [r1]
		MOV r0, #2
		STRB r0, [r4, #0x10]
		B        |inc_0x351c0_0x3d4d0| + 0x62d2
