	CODE16
|sub_08007874|
|unk_08007874|
		LDR r0, [pc, #0xfc]
		ADD r6, r4, #4
		STR r0, [r4]
		LDR r0, [r5]
		LDR r1, [r5, #4]
		LSL r0, r0, #0xa
		LSL r2, r1, #0xa
		LDR r1, [pc, #0xf4]
		STR r2, [sp, #0x1c]
		STR r0, [sp, #0x18]
		LDR r1, [r1, #4]
		ADD r7, r6, #4
		LDMIA r1!, {r3}
		LDR r1, [r1]
		SUB r0, r0, r3
		SUB r1, r2, r1
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x14]
		STR r1, [sp, #0x24]
		CMP r0, #0
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		STR r0, [sp, #0x20]
		BLT      |loc_080078A8|
		LDR r0, [sp, #0x20]
		B        |loc_080078AC|
|loc_080078A8|
		LDR r0, [sp, #0x20]
		NEG r0, r0
|loc_080078AC|
		LDR r1, [sp, #0x24]
		CMP r1, #0
		BLT      |loc_080078B6|
		LDR r1, [sp, #0x24]
		B        |loc_080078BA|
|loc_080078B6|
		LDR r1, [sp, #0x24]
		NEG r1, r1
|loc_080078BA|
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		STR r0, [sp, #0x10]
		STR r1, [sp, #0x14]
		STR r0, [sp, #0x18]
		STR r1, [sp, #0x1c]
		ADD r3, sp, #0x18
		LDMIA r3!, {r1, r3}
		ADD r2, sp, #0x18
		ADD r0, r2, #4
		CMP r1, r3
		BLE      |loc_080078D4|
		ADD r0, r2, #0
|loc_080078D4|
		LDR r1, [r0]
		LDR r0, [sp, #0x30]
		BL       |sub_08046E58|
		ASR r0, r0, #0xa
		ADD r0, #1
		STR r0, [r4, #0xc]
		STR r6, [sp, #0xc]
		LDR r0, [r4, #0xc]
		LSL r5, r0, #0xa
		LDR r0, [sp, #0x20]
		LSL r1, r0, #0xa
		ADD r0, r5, #0
		BL       |sub_08046E58|
		ADD r6, r0, #0
		LDR r0, [sp, #0x24]
		LSL r1, r0, #0xa
		ADD r0, r5, #0
		BL       |sub_08046E58|
		STR r0, [sp, #8]
		LDR r1, [sp, #8]
		ADD r0, r6, #0
		STR r6, [sp, #4]
		STR r6, [sp, #0x10]
		LDR r6, [sp, #0xc]
		STR r1, [sp, #0x14]
		STR r0, [r6]
		LDR r0, [sp, #0x14]
		STR r0, [r7]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x7718
		PUSH {r4, r5, lr}
		LDR r5, [pc, #0x5c]
		ADD r4, r0, #0
|loc_0800791C|
|unk_0800791C|
		LDR r2, [r5, #4]
		ADD r0, #4
		LDMIA r0!, {r3}
		LDMIA r2!, {r1}
		SUB sp, #0x1c
		ADD r1, r1, r3
		LDR r3, [r2]
		LDR r0, [r0]
		STR r1, [sp, #4]
		ADD r0, r3, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		LDR r0, [r5, #4]
		ADD r1, sp, #0x14
		ADD r0, #0x80
		LDR r0, [r0, #0x10]
		CMP r0, #0
		LDR r0, [r5, #4]
		BEQ      |sub_0800795C|
		LDR r1, [sp, #0x14]
		STR r1, [r0]
		LDR r0, [sp, #0x18]
		STR r0, [r2]
		LDR r0, [r5, #4]
		BL       |sub_0802ed98|
		B        |inc_0x0158_0x143f2| + 0x7808
