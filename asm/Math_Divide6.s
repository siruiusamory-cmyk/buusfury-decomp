|Math_Divide6|
	CODE16
|unk_0803E18E|
		LDR r2, [r4, #0x1c]
		ADD r0, r0, r2
		SUB r0, #1
		SUB r0, r0, r1
		ADD r1, r2, #0
		SWI 6
		ADD r7, r0, #0
		LDR r0, [r4, #0x20]
		LDR r1, [r4]
		LSL r0, r0, #1
		SUB r1, r0, r1
		LDR r0, [r4, #0x1c]
		ADD r2, r7, #0
		MUL r0, r7
		ADD r0, r1, r0
		STR r0, [sp]
		ADD r1, r6, #0
		ADD r0, r4, #0
		LDR r3, [r4, #0x18]
		BL       |inc_0x046118_0x049114| + 0x98e
		LSL r0, r7, #2
		ADD r6, r0, r6
		LDR r0, [sp]
		SUB r5, r5, r7
		STR r0, [r4]
		LDRB r0, [r4, #0x11]
		MOV r1, #4
		BIC r0, r1
		STRB r0, [r4, #0x11]
		LDR r0, [r4, #0x1c]
		STR r0, [r4, #4]
		B        |loc_0803E22A|
|loc_0803E1D0|
|unk_0803E1D0|
		LDR r1, [r4, #0x24]
		CMP r1, r7
		BLE      |loc_0803E1E6|
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		LDR r3, [r4, #0x18]
		BL       |inc_0x046118_0x049114| + 0x98e
		STR r7, [r4]
		B        |loc_0803E18C|
|loc_0803E1E6|
		ADD r2, r1, #0
		LDR r1, [r4, #0x1c]
		ADD r2, r2, r1
		SUB r2, #1
		SUB r0, r2, r0
		SWI 6
		ADD r7, r0, #0
		LDR r0, [r4, #0x24]
		LDR r1, [r4]
		LSL r0, r0, #1
		SUB r1, r0, r1
		LDR r0, [r4, #0x1c]
		ADD r2, r7, #0
		MUL r0, r7
		SUB r0, r1, r0
		SUB r0, #1
		STR r0, [sp]
		ADD r1, r6, #0
		ADD r0, r4, #0
		LDR r3, [r4, #0x18]
		BL       |inc_0x046118_0x049114| + 0x98e
		LSL r0, r7, #2
		ADD r6, r0, r6
		LDR r0, [sp]
		MOV r1, #4
		STR r0, [r4]
		LDRB r0, [r4, #0x11]
		SUB r5, r5, r7
		ORR r0, r1
		STRB r0, [r4, #0x11]
		LDR r0, [r4, #0x1c]
		NEG r0, r0
		STR r0, [r4, #4]
|loc_0803E22A|
		CMP r5, #0
		BGT      |inc_0x03d784_0x041118| + 0x9e6
		B        |loc_0803E18C|
|loc_0803E230|
|unk_0803E230|
		B        |inc_0x03d784_0x041118| + 0xb08
|loc_0803E232|
|unk_0803E232|
		B        |loc_0803E234|
|loc_0803E234|
		LDR r0, [r4, #4]
		LDR r2, [r4]
		MUL r0, r5
		ADD r7, r2, r0
		LDR r0, [r4, #0x24]
		CMP r0, r7
		BLE      |loc_0803E252|
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		LDR r3, [r4, #0x18]
		BL       |inc_0x046118_0x049114| + 0x98e
		STR r7, [r4]
		B        |loc_0803E18C|
|loc_0803E252|
		LDR r1, [r4, #0x1c]
		ADD r0, r0, r1
		SUB r0, #1
		SUB r0, r0, r2
		SWI 6
		ADD r7, r0, #0
		LDR r0, [r4, #0x1c]
		LDR r1, [r4]
		MUL r0, r7
		ADD r0, r1, r0
		LDR r1, [r4, #0x24]
		LDR r2, [r4, #0x20]
		SUB r1, r1, r2
		SUB r0, r0, r1
		STR r0, [sp]
		ADD r1, r6, #0
		ADD r2, r7, #0
		ADD r0, r4, #0
		LDR r3, [r4, #0x18]
		BL       |inc_0x046118_0x049114| + 0x98e
		LSL r0, r7, #2
		ADD r6, r0, r6
		LDR r0, [sp]
		SUB r5, r5, r7
		CMP r5, #0
		STR r0, [r4]
		BGT      |loc_0803E234|
		B        |loc_0803E18C|
		LDR r0, [r4, #4]
		LDR r2, [r4]
		MUL r0, r5
		ADD r7, r2, r0
		LDR r0, [r4, #0x24]
		CMP r0, r7
		BLE      |loc_0803E2AA|
		ADD r2, r5, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		LDR r3, [r4, #0x18]
		BL       |inc_0x042118_0x049114| + 0x498e
		STR r7, [r4]
		B        |loc_0803E18C|
|loc_0803E2AA|
		LDR r1, [r4, #0x1c]
		ADD r0, r0, r1
		SUB r0, #1
		SUB r0, r0, r2
		SWI 6
		ADD r2, r0, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		LDR r3, [r4, #0x18]
		BL       |inc_0x042118_0x049114| + 0x498e
		MOV r0, #0
		STRB r0, [r4, #0x10]
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BEQ      |inc_0x03d784_0x041118| + 0xa60
		ADD r0, #0x40
		LDRB r1, [r0, #0xa]
		MOV r2, #4
		BIC r1, r2
		STRB r1, [r0, #0xa]
		B        |loc_0803E18C|
