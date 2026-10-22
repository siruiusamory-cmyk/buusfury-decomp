	CODE16
|sub_08017884|
|unk_08017884|
		MOV r0, #0
		POP {r4, pc}
		PUSH {r4, lr}
		LDR r1, [r0, #4]
		ADD r4, r0, #0
		ADD r1, #1
		STR r1, [r0, #4]
		LDR r0, [r0, #8]
		CMP r1, r0
		BLE      |sub_080178A4|
		LSL r2, r0, #1
		SUB r1, r2, r1
		LSL r1, r1, #8
		BL       |sub_08046E58|
		B        |inc_0x153f2_0x1a3f2| + 0x24b8
