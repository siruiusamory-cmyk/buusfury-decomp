	CODE16
|loc_0800FD08|
		ADD r1, r0, #1
		LSL r3, r0, #3
		SUB r0, r3, r0
		LSL r0, r0, #2
		ADD r0, r0, r5
		STR r1, [r5]
		MOV r5, #0
		ADD r0, #4
		STR r5, [r0, #0x10]
		LDMIA r6!, {r1, r2, r3, r6}
		STMIA r0!, {r1, r2, r3, r6}
		SUB r0, #0x10
		STRB r5, [r0, #0x14]
		STR r4, [r0, #0x18]
|loc_0800FD24|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf9fa
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x10180
		B        |inc_0x0158_0x143f2| + 0xf9fa
