	CODE16
|loc_08013B54|
	PUSH     {r3, r4, r5, lr}
	LDRB     r5, [r0, #0xc]
	MOV      r3, #0
	CMP      r5, #0
	BLE      |loc_08013B8A|
	ADD      r4, r0, r3
	LDRB     r4, [r4, #0xd]
	CMP      r4, r1
	BNE      |sub_08013B84|
	LSL      r1, r3, #1
	ADD      r0, r1, r0
	LSL      r1, r2, #0x18
	LSR      r1, r1, #0x18
	ADD      r0, #0x2e
	ADD      r3, r1, #0
|loc_08013B72|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08013B72|
|loc_08013B7A|
	STRB     r3, [r0, #1]
	LDRB     r1, [r0, #1]
	CMP      r1, r3
	BNE      |loc_08013B7A|
	POP      {r3, r4, r5, pc}
