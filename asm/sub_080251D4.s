	CODE16
|sub_080251D4|
|unk_080251D4|
		MOV r3, #0x41
		LSL r3, r3, #6
		ADD r3, sp
		MOV r0, #3
		STRB r0, [r3, #7]
		MOV r0, #0x20
		SUB r3, #0x40
		STR r0, [r3, #0x4c]
		STR r1, [r3, #0x48]
		LDR r1, [pc, #0x140]
		MOV r0, #0xc3
		LSL r0, r0, #2
		LDR r1, [r1, r0]
		ADD r0, r3, #0
		ADD r0, #0x44
		BL       |loc_0803DADA|
		LDR r0, [r4, #4]
		MOV r1, #0
		STR r1, [r0, #0x20]
		LDR r0, [r4, #8]
		STR r1, [r0, #0x20]
		B        |sub_08025204|
|loc_08025202|
|unk_08025202|
		B        |loc_08025238|
