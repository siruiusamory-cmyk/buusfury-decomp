	CODE16
|sub_0801F7FE|
|unk_0801F7FE|
		LDR r0, [r0, #0x24]
|loc_0801F800|
|unk_0801F800|
		LSL r3, r0, #3
		SUB r0, r3, r0
		LSL r0, r0, #1
		ADD r0, #0x2e
		STR r0, [r1, #4]
		MOV r2, #0x12
		STR r2, [r1]
		B        |loc_0801F7FA|
