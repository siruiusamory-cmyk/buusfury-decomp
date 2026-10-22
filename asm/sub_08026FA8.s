	CODE16
|sub_08026FA8|
|unk_08026FA8|
		LDR r0, [pc, #0x204]
		MOV r6, #1
		LSL r6, r6, #0xa
		LDR r5, [pc, #0x204]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5, #4]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08026FD0|
		ADD r1, r6, #0
		LDR r0, [r5, #4]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5, #4]
		BL       |loc_0801124C|
|loc_08026FD0|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x1e4]
		MOV r5, #0xf
		STR r0, [r4]
		MOV r0, #0xc1
		LSL r0, r0, #4
		ADD r2, r4, r0
		MOV r7, #5
		LSL r7, r7, #0xc
		LSL r5, r5, #0xb
		STMIA r2!, {r5, r7}
		ADD r0, #8
		ADD r1, r4, r0
		MOV r5, #0
|loc_08026FEC|
|unk_08026FEC|
		STR r5, [r1]
		ADD r7, r4, #0
		ADD r7, #0x10
		STR r5, [r1, #4]
		LDR r0, [pc, #0x1bc]
		ADD r1, r7, #0
		ADD r0, #8
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDRH r0, [r4, #0xc]
		LDR r1, [pc, #0x1b8]
		ADD r2, r6, #0
		LSL r0, r0, #5
		ADD r0, r0, r1
		ADD r1, r7, #0
		BL       |Thunk_VramCopy|
		MOV r0, #0x10
		STRB r0, [r4, #8]
		MOV r0, #3
		LSL r0, r0, #0xa
		ADD r0, r4, r0
		STR r5, [r0, #0x24]
		STR r5, [r0, #0x20]
		ADD r0, r4, #0
		DCW     0xE7C2
		PUSH {r3, r4, r5, r6, r7, lr}
		LDR r7, [pc, #0x190]
		ADD r5, r0, #0
		LDR r0, [r7]
		MOV r1, #3
		LDRH r0, [r0, #4]
		LSL r1, r1, #0xa
		ADD r4, r5, r1
		LSL r0, r0, #0x1f
		LSR r0, r0, #0x1f
		MOV r6, #0
		CMP r0, #0
		BEQ      |loc_08027040|
		MOV r0, #1
		STR r0, [r4, #0x24]
		STR r6, [r4, #0x20]
|loc_08027040|
		LDR r0, [r7]
		LDRH r0, [r0, #6]
		LSL r0, r0, #0x1f
		BEQ      |loc_0802704A|
		STR r6, [r4, #0x24]
|loc_0802704A|
		MOV r2, #1
		LDR r1, [r4, #0x24]
		LSL r2, r2, #0xa
		CMP r1, #0
		LDR r1, [r4, #0x20]
		LDR r0, [pc, #0x164]
		BEQ      |sub_08027078|
		CMP r1, #4
		BGE      |loc_08027096|
		ADD r1, #1
		STR r1, [r4, #0x20]
		LSL r3, r1, #0x1f
		BMI      |loc_08027096|
		LDRH r3, [r5, #0xc]
		ASR r1, r1, #1
		LSL r1, r1, #0xa
		LSL r3, r3, #5
		ADD r0, r3, r0
		ADD r1, r1, r5
		ADD r1, #0x10
		BL       |Thunk_VramCopy|
		B        |loc_08027096|
