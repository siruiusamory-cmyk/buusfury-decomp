	CODE16
|loc_08013DD6|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x54]
	MOV      r2, #0
|loc_08013DDC|
	LSL      r3, r2, #1
	ADD      r3, r3, r2
	LSL      r3, r3, #3
	ADD      r3, r3, r4
	LDRH     r3, [r3, #0xe]
	CMP      r3, r1
	BNE      |loc_08013DEE|
	STRB     r2, [r0, #0x14]
	POP      {r4, pc}
|loc_08013DEE|
	ADD      r2, #1
	CMP      r2, #0x36
	BLT      |loc_08013DDC|
	MOV      r2, #0xff
	LDR      r0, [pc, #0x28]
	ADD      r2, #0xc7
	MOV      r3, #0
	ADD      r0, #0x98
	LDR      r1, [pc, #0x34]
	BL       |inc_0x03d784_0x041118| + 0x790
	POP      {r4, pc}
