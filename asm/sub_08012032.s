	CODE16
|sub_08012032|
|unk_08012032|
		LDR r0, [pc, #0x170]
		MOV r1, #1
		STR r0, [r5]
		LDR r0, [pc, #0x150]
		LSL r1, r1, #0xc
		LDR r0, [r0, #4]
		BL       |sub_08011732|
		LDR r0, [pc, #0x148]
		MOV r1, #1
		LSL r1, r1, #0xc
		LDR r0, [r0, #4]
		BL       |loc_0801124C|
		ADD r3, sp, #0
		STRH r0, [r3, #0x14]
		LDR r0, [pc, #0x138]
		MOV r1, #1
		LSL r1, r1, #0xc
		LDR r0, [r0, #4]
		BL       |sub_08011732|
		LDR r0, [pc, #0x12c]
		MOV r1, #1
		LSL r1, r1, #0xc
		LDR r0, [r0, #4]
		BL       |loc_0801124C|
		ADD r3, sp, #0
		STRH r0, [r3, #0x16]
		CMP r6, #0
		BEQ      |loc_08012092|
		CMP r6, #7
		BEQ      |loc_08012092|
		LDR r0, [pc, #0x114]
		MOV r1, #1
		LSL r1, r1, #0xc
		LDR r0, [r0, #4]
		BL       |sub_08011732|
		LDR r0, [pc, #0x108]
		MOV r1, #1
		LSL r1, r1, #0xc
		LDR r0, [r0, #4]
		BL       |loc_0801124C|
		ADD r3, sp, #0
		STRH r0, [r3, #0x1a]
|loc_08012092|
		LDR r0, [pc, #0xf8]
		MOV r1, #1
		LSL r1, r1, #0xb
		LDR r0, [r0, #4]
		BL       |sub_08011732|
		LDR r0, [pc, #0xec]
		MOV r1, #1
		LSL r1, r1, #0xb
		LDR r0, [r0, #4]
		BL       |loc_0801124C|
		ADD r3, sp, #0
		STRH r0, [r3, #0x18]
		LDR r0, [pc, #0xdc]
		MOV r2, #0
		LDR r1, [r0, #8]
		LDR r0, [r0, #0xc]
		STR r1, [sp, #0xc]
		STR r0, [sp, #0x10]
		MOV r0, #0x78
		CMP r6, #0
		BEQ      |loc_080120D2|
		CMP r6, #1
		LDR r1, [r7, #4]
		BNE      |loc_080120D6|
		CMP r1, #0
		BLT      |loc_080120CC|
		STR r0, [sp, #0x10]
|loc_080120CC|
		LDR r1, [r7]
		LSR r2, r1, #0x1f
		B        |loc_080120E2|
|loc_080120D2|
		STR r0, [sp, #0x10]
		B        |loc_080120E2|
|loc_080120D6|
		CMP r1, #0
		BGE      |loc_080120DC|
		STR r0, [sp, #0x10]
|loc_080120DC|
		LDR r1, [r7]
		ASR r2, r1, #0x1f
		ADD r2, #1
|loc_080120E2|
		LDRH r1, [r4]
		CMP r1, #0x21
		BNE      |loc_080120EE|
		MOV r1, #0x28
		STR r1, [sp, #0x10]
		ADD r4, #2
|loc_080120EE|
		LDRH r1, [r4]
		CMP r1, #0x40
		BNE      |loc_080120FA|
		MOV r1, #0x50
		STR r1, [sp, #0x10]
		ADD r4, #2
|loc_080120FA|
		LDRH r1, [r4]
		CMP r1, #0x23
		BNE      |loc_08012104|
		STR r0, [sp, #0x10]
		ADD r4, #2
|loc_08012104|
		MOV r0, #0
		CMP r6, #7
		BNE      |loc_0801210C|
		MOV r0, #1
|loc_0801210C|
		CMP r6, #0
		BEQ      |loc_08012114|
		CMP r6, #7
		BNE      |loc_08012118|
|loc_08012114|
		MOV r1, #0
		B        |loc_08012144|
|loc_08012118|
		CMP r6, #8
		BGE      |loc_0801213E|
		LDR r1, [pc, #0x6c]
		MOV r3, #0x68
		LDR r1, [r1]
		LDRB r7, [r1]
		MUL r3, r7
		ADD r1, r3, r1
		MOV r3, #0x9f
		LSL r3, r3, #3
		ADD r1, r1, r3
		LDRB r1, [r1, #0x14]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r3, [pc, #0x58]
		LSL r1, r1, #3
		ADD r1, r1, r3
		ADD r1, r1, r6
		LDRB r6, [r1, #0xf]
|loc_0801213E|
		LDR r3, [pc, #0x54]
		LSL r1, r6, #2
		LDR r1, [r3, r1]
|loc_08012144|
		STR r2, [sp, #8]
		ADD r2, r4, #0
		STR r0, [sp]
		STR r1, [sp, #4]
		ADD r1, sp, #0x14
		MOV r0, #0
		ADD r3, sp, #0xc
		BL       |inc_0x0158_0x143f2| + 0xb030
		ADD r1, r0, #0
		STR r0, [r5, #4]
		LDR r0, [pc, #0x30]
		LDR r0, [r0, #4]
		BL       |List_Append|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0x11ed6
