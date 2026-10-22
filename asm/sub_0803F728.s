	CODE16
|sub_0803F728|
|unk_0803F728|
		LDR r0, [r2]
		LSL r3, r1, #1
		LDRH r0, [r0, r3]
		CMP r0, #0
		BEQ      |loc_0803F736|
		MOV r0, #1
		B        |sub_0803F738|
|loc_0803F736|
		MOV r0, #0
