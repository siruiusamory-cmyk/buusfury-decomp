	CODE16
|sub_08040F7E|
	LSL      r0, r0, #0xc
	LSL      r1, r0, #0
	LSL      r0, r0, #0x10
	LSL      r0, r4, #4
	LSL      r0, r0, #0x10
	DCW      0xfefe,0x0000
	LSL      r0, r0, #4
	LSL      r0, r0, #0x10
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	LDRB     r0, [r7, #0x1f]
	LSL      r0, r0, #0xc
	LDR      r2, [pc, #0x170]
	PUSH     {r3, lr}
	MOV      r1, #1
	STR      r1, [r2]
	LDR      r2, [pc, #0x16c]
	MOV      r1, #0
	STRB     r1, [r2]
	LDR      r2, [pc, #0x16c]
	MOV      r1, #0xff
	STRB     r1, [r2]
	MOV      r1, #0xa
	STR      r1, [r0, #4]
	BL       |Ram_ClearLimits1|
	BL       |loc_08040C78|
	POP      {r3, pc}
	LDR      r1, [pc, #0x150]
	PUSH     {r3, lr}
	MOV      r0, #0
	STR      r0, [r1]
	BL       |loc_08040D1E|
	BL       |Ram_ClearLimits1|
	POP      {r3, pc}
	LDR      r0, [pc, #0x148]
	LDRH     r0, [r0, #8]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	BX       lr
|sub_08040FD6|
|unk_08040FD6|
		PUSH {r4, r5, r6, lr}
		ADD r4, r0, #0
		LDR r2, [pc, #0x140]
		LDR r0, [pc, #0x140]
		MOV r6, #0
		STR r6, [r2]
		LDR r0, [r0]
		MOV r5, #0
		LSL r1, r0, #0x18
		BPL      |loc_08040FEE|
		MOV r1, #1
		STR r1, [r2]
|loc_08040FEE|
		LSL r0, r0, #0x17
		DCW     0xD519
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #8]
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #2
		LDR r1, [pc, #0x10c]
		BHS      |loc_0804100E|
		LDRB r2, [r1]
		CMP r0, r2
		BEQ      |loc_08041016|
|loc_0804100E|
		STRB r0, [r1]
		MOV r0, #0xa
		STR r0, [r4, #4]
		DCW     0xE007
|loc_08041016|
		LDR r0, [r4, #4]
		CMP r0, #0
		BLE      |sub_08041022|
		SUB r0, #1
		STR r0, [r4, #4]
		DCW     0xE001
