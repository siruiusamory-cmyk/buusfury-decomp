	CODE16
|sub_080059A0|
|unk_080059A0|
		LDR r1, [r0, #0xc]
		CMP r1, #0
		BEQ      |loc_080059AA|
		SUB r1, #1
		STR r1, [r0, #0xc]
|loc_080059AA|
		STR r4, [r0, #0x10]
		B        |loc_0800599C|
