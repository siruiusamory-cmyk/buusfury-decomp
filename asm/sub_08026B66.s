	CODE16
|sub_08026B66|
|unk_08026B66|
		LDR r0, [pc, #0x124]
		LDR r6, [pc, #0x124]
		STR r0, [r4]
		MOV r0, #0x80
		STRH r0, [r4, #0xe]
		LDR r0, [r6]
		MOV r1, #0x80
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08026B8C|
		MOV r1, #0x80
		LDR r0, [r6]
		BL       |sub_08011732|
		MOV r1, #0x80
		LDR r0, [r6]
		BL       |loc_0801124C|
|loc_08026B8C|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		STRH r0, [r4, #0xc]
		LDR r1, [pc, #0x100]
		LDR r2, [pc, #0xf8]
		STR r1, [r4]
		STR r7, [r4, #0x18]
		MOV r1, #0
		STRB r1, [r4, #0x11]
		STRB r1, [r4, #0x12]
		LSL r1, r5, #3
		ADD r2, #4
		ADD r1, r1, r2
		LDR r2, [pc, #0xf0]
		STRB r5, [r4, #0x10]
		LSL r0, r0, #5
		ADD r0, r0, r2
		STR r1, [r4, #0x14]
		LDR r1, [r1, #4]
		MOV r2, #0x80
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		DCW     0xE7D3
		PUSH {r3, lr}
		ADD r1, r0, #0
		LDRB r3, [r1, #0x10]
		MOV r2, #1
		LSL r2, r2, #0xf
		CMP r3, #0
		BEQ      |loc_08026BE6|
		CMP r3, #1
		BEQ      |loc_08026BFA|
		CMP r3, #2
		BEQ      |loc_08026C0E|
		CMP r3, #3
		BNE      |loc_08026C24|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x2c]
		LDR r0, [r0, #0x24]
		CMP r2, r0
		BGE      |loc_08026C22|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026BE6|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x30]
		LDR r0, [r0, #0x28]
		CMP r2, r0
		BGE      |loc_08026BF6|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026BF6|
		MOV r0, #0
		B        |loc_08026C24|
|loc_08026BFA|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x30]
		LDR r0, [r0, #0x20]
		CMP r2, r0
		BLE      |loc_08026C0A|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026C0A|
		MOV r0, #0
		B        |loc_08026C24|
|loc_08026C0E|
		LDR r0, [r1, #0x18]
		ADD r0, r0, r2
		LDR r2, [r0, #0x2c]
		LDR r0, [r0, #0x1c]
		CMP r2, r0
		BLE      |loc_08026C1E|
		MOV r0, #1
		B        |loc_08026C24|
|loc_08026C1E|
		MOV r0, #0
		B        |loc_08026C24|
|loc_08026C22|
		MOV r0, #0
|loc_08026C24|
		CMP r0, #0
		BEQ      |sub_08026C3C|
		LDRB r0, [r1, #0x12]
		ADD r0, #1
		STRB r0, [r1, #0x12]
		LSL r0, r0, #0x1b
		LSR r2, r0, #0x1d
		CMP r2, #4
		DCW     0xDB05
		MOV r0, #7
		SUB r2, r0, r2
		DCW     0xE002
