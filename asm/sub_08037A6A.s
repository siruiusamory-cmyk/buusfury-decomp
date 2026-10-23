	CODE16
|sub_08037A6A|
|unk_08037A6A|
		MOV r1, #0
		LDR r2, [pc, #0xcc]
		STR r1, [sp, #0x24]
		CMP r4, #0
		LDR r7, [pc, #0xc4]
		STR r0, [sp, #0x28]
		STR r2, [sp, #0x20]
		BEQ      |loc_08037A80|
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0x8d
|loc_08037A80|
		ADD r0, sp, #0x20
		BL       |loc_0801599C|
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xb4]
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDMIA r0!, {r5, r6}
		MOV r1, #4
		ADD r0, r4, #0
		BL       |loc_0800EEB0|
		CMP r0, #0
		BNE      |loc_08037AB6|
		LDR r0, [sp, #0x24]
		MOV r4, #0
		CMP r0, #0
		STR r7, [sp, #0x20]
		BEQ      |loc_08037AB2|
		LDR r1, [r0]
		LDR r2, [r1]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_08037AB2|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x28a6
|loc_08037AB6|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		LSL r0, r5, #8
		ADD r5, r4, #0
		ADD r5, #0xff
		LSL r1, r6, #8
		STR r1, [sp, #0x1c]
		ADD r5, #0xa1
		STR r0, [sp, #0x18]
		LDR r0, [r5]
		LDR r1, [sp, #0x18]
		ADD r6, r5, #4
		ADD r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [sp, #0x1c]
		STR r0, [sp]
		ADD r1, r1, r2
		STR r1, [sp, #4]
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x14]
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x10
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_08037B06|
		LDR r0, [sp, #0x10]
		STR r0, [r5]
		LDR r0, [sp, #0x14]
		STR r0, [r6]
|loc_08037B06|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		LDR r0, [sp, #0x24]
		MOV r4, #0
		CMP r0, #0
		STR r7, [sp, #0x20]
		BEQ      |loc_08037B2A|
		LDR r1, [r0]
		LDR r2, [r1]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_08037B2A|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x28a6
	INCBIN  baserom.gba_0x37b2e_0x37b32.extracted
	CODE16
|dat_08037B32|
	DCW      0x0000
	DCW      0x1c34
	DCW      0x0300
	DCW      0x9acc
	DCW      0x0804
	DCW      0xae70
	DCW      0x0804
|unk_08037B40|
	INCBIN	baserom.gba_0x37b40_0x37b42.extracted
|dat_08037B42|
	DCW      0x0876
	DCW      0x3288
	DCW      0x0300
