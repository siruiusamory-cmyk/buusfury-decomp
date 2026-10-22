	CODE16
|sub_08033CBA|
	STR      r0, [sp, #0x28]
	ADD      r3, sp, #0
	STRB     r7, [r3, #0x10]
	STR      r4, [sp, #0x40]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r3, [r1, #0x24]
	ADD      r3, r3, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BEQ      |loc_08033CEC|
	LDR      r0, [pc, #0x94]
	MOV      r1, #0x5d
	LDR      r2, [pc, #0x94]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x94]
	LDR      r0, [r0]
	MOV      r2, #0x40
	ADD      r3, r7, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08033CEC|
	ADD      sp, #0x6c
	POP      {r4, r5, r6, r7, pc}
|sub_08033CF0|
|unk_08033CF0|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r1, #0
		LDRH r1, [r1, #0x12]
		ADD r1, #1
		LSL r3, r1, #0x10
		LSR r3, r3, #0x10
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0xc1
		STRH r3, [r4, #0x12]
		LDR r2, [r4, #0x50]
		CMP r3, #0x20
		BHS      |loc_08033D12|
		MOV r5, #0
		MOV r3, #1
		STR r3, [r1, #0xc]
		B        |inc_0x331c0_0x341c0| + 0xb78
|loc_08033D12|
		LDR r6, [r2]
		LDRB r7, [r0, #4]
		SUB r5, r6, #2
		LSL r5, r7
		ADD r5, #0x20
		CMP r5, r3
		BLE      |sub_08033D2C|
		SUB r3, #0x20
		ASR r3, r7
		ADD r5, r3, #1
		MOV r3, #0
		STR r3, [r1, #0xc]
		B        |inc_0x331c0_0x341c0| + 0xb78
