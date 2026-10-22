	CODE16
|sub_08005732|
|unk_08005732|
		LDR r2, [r0, #0xc]
		CMP r2, #0
		BEQ      |loc_0800573C|
		SUB r2, #1
		STR r2, [r0, #0xc]
|loc_0800573C|
		STR r1, [r0, #0x10]
		B        |loc_0800572E|
