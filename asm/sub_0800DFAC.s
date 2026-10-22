	CODE16
|sub_0800DFAC|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r0, #0xff
	BL       |inc_0x03d784_0x041118| + 0x2348
	STRH     r0, [r4, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r4, #8]
	MOV      r0, #0
	STRB     r0, [r4, #0x11]
	POP      {r4, pc}
|sub_0800DFD4|
|unk_0800DFD4|
		LDRH r2, [r1, #0x12]
		LDR r0, [r1, #0x50]
		ADD r2, #1
		LSL r2, r2, #0x10
		LSR r2, r2, #0x10
		LDR r0, [r0]
		STRH r2, [r1, #0x12]
		CMP r0, #2
		BNE      |inc_0x0158_0x143f2| + 0xdea0
		LSL r0, r2, #0x18
		LSR r0, r0, #0x18
		CMP r0, #0xf0
		BLS      |sub_0800DFF2|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0xde9c
