	CODE16
|sub_080296E8|
|unk_080296E8|
		LSL r0, r0, #0x15
		LSR r0, r0, #0x18
		STRB r0, [r4, #0x11]
		CMP r0, #1
		DCW     0xD3F8
		MOV r0, #1
		STRB r0, [r4, #0x11]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		LDR r0, [r5, #4]
		ADD r6, r4, #0
		LDR r2, [pc, #0x13c]
		ADD r6, #0xff
		LSL r0, r0, #3
		LDR r0, [r2, r0]
		ADD r6, #0xa1
		LDR r1, [r6]
		LSL r0, r0, #8
		ADD r0, r1, r0
		STR r0, [sp]
		LDR r1, [r5, #4]
		MOV r0, #0xff
		LSL r1, r1, #3
		ADD r1, r1, r2
		LDR r1, [r1, #4]
		ADD r0, #0xa5
		LDR r0, [r0, r4]
		LSL r1, r1, #8
		ADD r0, r0, r1
		STR r0, [sp, #4]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		MOV r3, sp
		ADD r2, r2, r1
		ADD r1, r3, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0802974C|
		LDR r0, [sp]
		STR r0, [r6]
		LDR r1, [sp, #4]
		STR r1, [r6, #4]
		B        |loc_08029768|
|loc_0802974C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_08029768|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		DCW     0xE7B5
		PUSH {r4, r5, r6, r7, lr}
		ADD r6, r0, #0
		LDR r0, [pc, #0xcc]
		SUB sp, #0xc
		ADD r4, r1, #0
		LDR r0, [r0]
		MOV r1, #0
		LDR r2, [pc, #0xcc]
		STR r1, [sp, #4]
		CMP r4, #0
		LDR r7, [pc, #0xc0]
		STR r0, [sp, #8]
		STR r2, [sp]
		BEQ      |loc_0802979A|
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0x8d
|loc_0802979A|
		MOV r0, sp
		BL       |loc_0801599C|
		LDR r0, [pc, #0xa8]
		LDR r1, [r0]
		LDRB r0, [r1, #0x10]
		CMP r0, #0
		BEQ      |loc_080297CC|
		CMP r0, #1
		BEQ      |loc_080297CC|
		CMP r0, #2
		BEQ      |loc_080297B6|
		CMP r0, #3
		DCW     0xD118
|loc_080297B6|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		MOV r1, #0xff
		ADD r1, #0xa5
		LDR r0, [r0]
		LDR r1, [r1, r4]
		CMP r0, r1
		BLE      |sub_080297E6|
		MOV r5, #1
		DCW     0xE00D
|loc_080297CC|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		MOV r1, #0xff
		ADD r1, #0xa1
		LDR r0, [r0]
		LDR r1, [r1, r4]
		CMP r0, r1
		BLE      |loc_080297E2|
		MOV r5, #2
		DCW     0xE002
|loc_080297E2|
		MOV r5, #3
		DCW     0xE000
