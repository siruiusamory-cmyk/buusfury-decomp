	CODE16
|sub_0803881A|
|unk_0803881A|
		STR r2, [r4, #0x30]
		LSL r1, r1, #0x1f
		LSR r1, r1, #0x1f
		LSL r3, r1, #1
		LDRH r0, [r4, #0xc]
		ADD r1, r3, r1
		LDR r2, [pc, #0x244]
		LSL r1, r1, #2
		LDR r7, [pc, #0x23c]
		ADD r1, r1, r2
		LSL r0, r0, #5
		ADD r0, r0, r7
		ADD r2, r6, #0
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x30]
		MOV r2, #1
		LSL r0, r0, #5
		ADD r0, r0, r7
		ADD r0, r0, r6
		LSL r2, r2, #9
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
|loc_0803884E|
|unk_0803884E|
		LDR r0, [sp, #0x38]
		CMP r0, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x3656
		LDR r1, [r4, #0x34]
		ADD r3, sp, #0
		STR r1, [sp, #0x20]
		LDR r1, [r4, #0x38]
		MOV r0, sp
		STRB r1, [r3, #0x14]
		LDR r1, [pc, #0x20c]
		STR r6, [sp, #0x18]
		STR r1, [sp, #0x1c]
		LDR r1, [r4, #0x34]
		ADD r6, r0, #4
		ADD r1, #0xff
		ADD r1, #0xc1
		LDR r1, [r1, #0x10]
		STRB r1, [r3]
		STR r4, [sp, #0x30]
		ADD r4, #0x18
		LDMIA r4!, {r1, r2, r3, r4}
		STMIA r6!, {r1, r2, r3, r4}
		ADD r2, r0, #0
		LDR r0, [r5]
		MOV r1, #0
		BL       |loc_08011C0C|
		B        |inc_0x351c0_0x3d4d0| + 0x3656
