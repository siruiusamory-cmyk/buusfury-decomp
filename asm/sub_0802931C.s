	CODE16
|sub_0802931C|
	ADD      r3, r2, #0
	LDR      r4, [pc, #0x60]
	LDR      r0, [r5]
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x54]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
	LDR      r6, [r0, #0x14]
	MOV      r3, #0x68
	LDR      r5, [r5, #8]
	MUL      r3, r6
	ADD      r3, r3, r5
	ADD      r1, r3, r1
	LDR      r3, [r0, #0x18]
	LSL      r3, r3, #1
	ADD      r1, r3, r1
	ADD      r1, #0x2e
	LDRB     r3, [r1]
	SUB      r3, r3, r4
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
|loc_08029352|
	STRB     r3, [r1]
	LDRB     r4, [r1]
	CMP      r4, r3
	BNE      |loc_08029352|
	STR      r2, [r0, #0x10]
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_08029360|
	STRB     r3, [r1]
	LDRB     r4, [r1]
	CMP      r4, r3
	BNE      |loc_08029360|
	STR      r2, [r0, #0x10]
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|sub_0802936E|
|unk_0802936E|
		MOV r0, #0
		POP {r4, r5, r6, pc}
		MOV r0, #0
		BX       lr
	CODE16
|dat_08029376|
	DCW      0x0000
	DCW      0xf04c
	DCW      0x0874
	DCW      0x9488
	DCW      0x0831
	DCW      0x05c4
	DCW      0x0000
|loc_08029384|
	DCW      0xb5ff
	DCW      0xb081
	DCW      0x1c1f
	DCW      0x1c0d
	DCW      0x1c04
	DCW      0x2800
	DCW      0x9e0a
	DCW      0xd107
	DCW      0x2058
	DCW      0xf014
	DCW      0xf90f
	DCW      0x1c04
	DCW      0xd102
	DCW      0x1c20
	DCW      0xb005
	DCW      0xbdf0

