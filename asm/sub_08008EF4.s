	CODE16
|sub_08008EF4|
|unk_08008EF4|
		MOV r0, #0x55
		LSL r0, r0, #3
		DCD     0xFB5EF034
		ADD r6, r0, #0
		BEQ      |sub_08008F10|
		ADD r3, r7, #0
		ADD r0, r6, #0
		MOV r2, sp
		LDR r1, [sp, #0x18]
		BL       |sub_08010A3A|
		LDR r0, [pc, #0x11c]
		STR r0, [r6]
