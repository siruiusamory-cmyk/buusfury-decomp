	CODE16
|sub_08013924|
|unk_08013924|
		LDRB r0, [r4, #0x14]
		LDR r1, [pc, #0x274]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDRB r0, [r0]
		LSL r2, r0, #0x1b
		LSR r2, r2, #0x1f
		BNE      |loc_0801393C|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x137ca
|loc_0801393C|
		LSL r0, r0, #0x1d
		LSR r0, r0, #0x1f
		LDR r7, [pc, #0x25c]
		BEQ      |loc_080139EC|
		ADD r0, r7, #0
		LDR r0, [r0]
		LDRH r1, [r4, #2]
		MOV r3, #0x68
		MOV r7, #0x9f
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1c
		MUL r1, r3
		ADD r0, r1, r0
		LSL r7, r7, #3
		ADD r0, r0, r7
		MOV r6, #0
		ADD r1, r5, #0
		BL       |loc_08013914|
		ORR r6, r0
		LDR r0, [pc, #0x238]
		MOV r3, #0x68
		LDR r0, [r0]
		LDRH r1, [r4, #2]
		LSL r1, r1, #0x18
		LSR r1, r1, #0x1c
		MUL r1, r3
		ADD r0, r1, r0
		ADD r0, r0, r7
		ADD r1, r5, #0
		BL       |loc_08013914|
		ORR r0, r6
		ADD r5, r0, #0
		BEQ      |loc_080139E8|
		LDRH r0, [r4, #2]
		MOV r3, #0x68
		LDR r7, [pc, #0x218]
		LSL r2, r0, #0x18
		LSR r2, r2, #0x1c
		LSR r6, r0, #8
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1c
		LDR r1, [r7]
		MUL r2, r3
		ADD r2, r2, r1
		MOV r1, #0x9f
		LDR r7, [r7]
		MUL r0, r3
		LSL r1, r1, #3
		ADD r2, r2, r1
		ADD r0, r0, r7
		ADD r1, r0, r1
		ADD r3, r6, #0
		ADD r0, r4, #0
		BL       |loc_0801375E|
		LDRH r1, [r4, #0x18]
		LDR r6, [pc, #0x1f0]
		STRH r1, [r4, #0x16]
		LDRH r1, [r4, #0x1c]
		STRH r1, [r4, #0x1a]
		LDR r0, [r6]
		MOV r4, #0
		CMP r0, #0
		BEQ      |loc_080139E8|
		LDR r0, [r0, #0x14]
		LDR r1, [r0]
		LDR r2, [r1, #0x14]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_080139D8|
		MOV r4, #1
		LDR r0, [r6]
		BL       |inc_0x0158_0x143f2| + 0xf3e4
|loc_080139D8|
		LDR r0, [r6]
		BL       |loc_0801064C|
		CMP r4, #0
		BEQ      |loc_080139E8|
		LDR r0, [r6]
		BL       |inc_0x0158_0x143f2| + 0xf400
|loc_080139E8|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0x137ca
|loc_080139EC|
		ADD r0, r4, #0
		BL       |loc_080135D2|
		ADD r6, r0, #0
		LDR r0, [r4, #0x24]
		ADD r0, r0, r5
|loc_080139F8|
		STR r0, [r4, #0x24]
		LDR r1, [r4, #0x24]
		CMP r1, r0
		BNE      |loc_080139F8|
		CMP r6, #0xc8
		BLT      |loc_08013A08|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x137ca
|loc_08013A08|
		LDR r0, [r4, #0x24]
		LDR r2, [pc, #0x194]
		LSL r1, r6, #2
		ADD r2, #4
		ADD r1, r1, r2
		SUB r1, #0xff
		SUB r1, #1
		LDR r1, [r1, #0x3c]
		CMP r0, r1
		BHS      |loc_08013A20|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x137ca
|loc_08013A20|
		ADD r0, r4, #0
		BL       |loc_080135D2|
		ADD r2, r0, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |loc_08013678|
		LDR r6, [pc, #0x170]
		MOV r5, #0
		LDR r0, [r6]
		CMP r0, #0
		BEQ      |loc_08013A52|
		LDR r0, [r0, #0x14]
		LDR r1, [r0]
		LDR r2, [r1, #0x14]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_08013A52|
		MOV r5, #1
		LDR r0, [r6]
		BL       |inc_0x0158_0x143f2| + 0xf3e4
|loc_08013A52|
		LDR r0, [r7]
		LDR r1, [pc, #0x144]
		LDRB r0, [r0]
		STR r0, [sp]
		LDRB r0, [r4, #0x14]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDRB r0, [r0, #0xc]
		LDR r1, [r7]
		STRB r0, [r1]
		MOV r1, #0
		LDR r0, [pc, #0x138]
		BL       |sub_08012588|
		LDR r0, [sp]
		LDR r1, [r7]
		STRB r0, [r1]
		LDR r0, [r6]
		CMP r0, #0
		BEQ      |loc_08013A8C|
		BL       |loc_0801064C|
		CMP r5, #0
		BEQ      |loc_08013A8C|
		LDR r0, [r6]
		BL       |inc_0x0158_0x143f2| + 0xf400
|loc_08013A8C|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x137ca
