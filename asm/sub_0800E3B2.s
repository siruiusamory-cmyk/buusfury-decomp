	CODE16
|sub_0800E3B2|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x26c]
	MOV      r1, #0x51
	LDR      r2, [pc, #0x26c]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x26c]
	LDR      r0, [r0]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r4, pc}
	MOV      r1, #0x51
	LDR      r2, [pc, #0x254]
	LSL      r1, r1, #3
	LDR      r0, [pc, #0x24c]
	ADD      r1, r1, r2
	PUSH     {r3, lr}
	LDR      r0, [r0]
	LDR      r2, [pc, #0x24c]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xb7e
	POP      {r3, pc}
