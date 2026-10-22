|Mosaic_WriteSize2|
	CODE16
|unk_0802CA2E|
		LSL r1, r1, #4
		BL       |sub_08046E58|
		LSL r3, r0, #4
		LDR r1, [pc, #0x6c]
		ADD r0, r3, r0
		STRB r0, [r1, #0xc]
		STRB r0, [r1, #0xd]
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xee0
