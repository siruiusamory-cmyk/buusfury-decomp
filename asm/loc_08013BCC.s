	CODE16
|loc_08013BCC|
	PUSH     {r4, lr}
	LDRB     r4, [r0, #0xc]
	MOV      r2, #0
	CMP      r4, #0
	BLE      |loc_08013BEE|
|loc_08013BD6|
	ADD      r3, r0, r2
	LDRB     r3, [r3, #0xd]
	CMP      r3, r1
	BNE      |loc_08013BE8|
	LSL      r1, r2, #1
	ADD      r0, r1, r0
	ADD      r0, #0x2f
	LDRB     r0, [r0]
	POP      {r4, pc}
|loc_08013BE8|
	ADD      r2, #1
	CMP      r4, r2
	BGT      |loc_08013BD6|
|loc_08013BEE|
	MOV      r2, #0xff
	ADD      r2, #0x8e
	MOV      r3, #0
	ADR      r1, |loc_08013BF8|
	SUB      r1, #0x4c
|loc_08013BF8|
	LDR      r0, [pc, #0x224]
	BL       |inc_0x03d784_0x041118| + 0x790
	MOV      r0, #0
	POP      {r4, pc}
