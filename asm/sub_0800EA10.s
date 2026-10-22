	CODE16
|sub_0800EA10|
|unk_0800EA10|
		LDR r1, [sp, #0x24]
		MOV r0, #0x52
		ADD r1, #0xff
		ADD r1, #0x81
		LDR r1, [r1, #0x3c]
		MUL r0, r7
		ADD r0, r0, r1
		BL       |inc_0x03d784_0x041118| + 0x235a
		STR r0, [r4, #0x10]
		CMP r0, #0
		BEQ      |sub_0800EA2C|
		ASR r0, r5, #1
		ADD r5, r0, r5
