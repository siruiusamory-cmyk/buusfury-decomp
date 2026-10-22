	CODE16
|sub_08042904|
|unk_08042904|
; cited by 0x08042660 (a pc-relative load targets 0x08042984)
		CMP r4, #0
		BNE      |inc_0x042118_0x049114| + 0x8c6
		BL       |loc_08043800|
		LDRB r0, [r0, #8]
		LDR r5, [pc, #0x2a0]
		STRH r0, [r5, #0x14]
		BL       |inc_0x042118_0x049114| + 0x1bc
		LDR r0, [sp, #0x20]
		LDRB r0, [r0]
		CMP r0, #0
		BEQ      |loc_08042950|
		LDRH r1, [r5, #0x14]
		MOV r7, #1
		BIC r0, r1
		LDR r1, [sp, #0x20]
		STRB r0, [r1]
		MOV r0, #0
		MOV r1, #0
|loc_0804292C|
		LDRH r2, [r5, #0x14]
		ADD r3, r7, #0
		LSL r3, r0
		AND r2, r3
		BEQ      |loc_0804293C|
		LSL r2, r0, #1
		ADD r2, r2, r5
		STRH r1, [r2, #0x34]
|loc_0804293C|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #4
		BLO      |loc_0804292C|
		LDRB r0, [r5, #6]
		CMP r0, #0
		BNE      |loc_08042950|
		STRB r1, [r5, #5]
		STRB r1, [r5, #4]
|loc_08042950|
		LDRB r0, [r5]
		LDRH r1, [r5, #0x14]
		ADD r3, sp, #0
		MOV ip, r0
		AND r0, r1
		STRB r0, [r3, #8]
		MOV r0, #0
		MOV r7, #1
|loc_08042960|
		ADD r3, sp, #0
		LDRB r3, [r3, #8]
		ADD r2, r7, #0
		LSL r2, r0
		AND r2, r3
		BEQ      |loc_08042976|
		LDRB r2, [r5, #1]
		CMP r2, #0
		BEQ      |loc_08042976|
		ADD r2, #0xff
		STRB r2, [r5, #1]
|loc_08042976|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #4
		BLO      |loc_08042960|
		MOV r0, ip
		BIC r0, r1
		STRB r0, [r5]
		LDRB r0, [r5, #7]
		CMP r0, #0
		BEQ      |inc_0x042118_0x049114| + 0x89e
		LDR r1, [pc, #0x21c]
		LDR r1, [r1]
		LDRB r1, [r1]
		CMP r1, #0xff
		BNE      |inc_0x042118_0x049114| + 0x8ba
		CMP r0, #8
		BNE      |inc_0x042118_0x049114| + 0x88e
		LDRH r0, [r5, #0x1c]
		STRH r0, [r5, #0x1a]
		MOV r0, #6
		STRB r0, [r5, #7]
		B        |inc_0x042118_0x049114| + 0x89c
|loc_080429A4|
|unk_080429A4|
		B        |inc_0x042118_0x049114| + 0x8c8
		LDRB r0, [r5, #4]
		CMP r0, #6
		BEQ      |loc_080429D2|
		CMP r0, #7
		BEQ      |loc_080429D2|
		STRB r7, [r5, #7]
		MOV r0, #5
		STRB r0, [r5, #4]
		LDR r0, [pc, #0x1f4]
		LDR r0, [r0]
		LDRB r0, [r0]
		CMP r0, #0xff
		BNE      |loc_080429D2|
		LDRB r0, [r5, #4]
		B        |inc_0x042118_0x049114| + 0x8b2
