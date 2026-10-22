	CODE16
|loc_08004A3A|
	PUSH     {r4, r5, lr}
	LDR      r3, [pc, #0xb0]
	ADD      r5, r0, #0
	ADD      sp, r3
	MOV      r4, sp
	MOV      r0, sp
	BL       |loc_08004838|
	LDR      r1, [pc, #0x98]
	MOV      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x24ca
	MOV      r1, #0x11
	LSL      r1, r1, #7
	ADD      r1, r4, r1
	STR      r0, [r1, #0x28]
	MOV      r1, #0x8b
	LSL      r1, r1, #4
	MUL      r1, r5
	LDR      r0, [pc, #0x90]
	MOV      r3, #0x8b
	LSL      r3, r3, #4
	ADD      r1, #0x10
	ADD      r2, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x245a
	LDR      r3, [pc, #0x84]
	ADD      sp, r3
	POP      {r4, r5, pc}
