	CODE16
|sub_0803F5C0|
|unk_0803F5C0|
		LDR r0, [r2]
		LSL r3, r1, #1
		LDRH r0, [r0, r3]
		CMP r0, #0
		BEQ      |loc_0803F5CE|
		MOV r0, #1
		B        |sub_0803F5D0|
|loc_0803F5CE|
		MOV r0, #0
