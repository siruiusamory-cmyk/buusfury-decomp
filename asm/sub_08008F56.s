	CODE16
|sub_08008F56|
|unk_08008F56|
		MOV r0, #0x55
|loc_08008F58|
|unk_08008F58|
		LSL r0, r0, #3
		DCW     0xF034
		DCW     0xFB2D
		ADD r5, r0, #0
		BEQ      |loc_08008F72|
		MOV r2, sp
		ADD r0, r5, #0
		LDR r1, [sp, #0x14]
		LDR r3, [sp, #0x38]
		BL       |sub_08010A3A|
		LDR r0, [pc, #0xb8]
		STR r0, [r5]
|loc_08008F72|
|unk_08008F72|
		LDR r7, [pc, #0xa4]
		LDR r0, [r7, #4]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |sub_08008F8A|
		ADD r7, r6, #0
		B        |inc_0x0158_0x143f2| + 0x8e34
