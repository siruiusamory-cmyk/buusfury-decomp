	CODE16
|loc_08013ABA|
	PUSH     {r4, r5, r6, r7}
	LDRB     r2, [r0, #0xc]
	MOV      r5, #0
	CMP      r2, #0
	BLE      |loc_08013B0E|
	MOV      r6, #0
|loc_08013AC6|
	ADD      r2, r0, r5
	LDRB     r2, [r2, #0xd]
	CMP      r2, r1
	BNE      |loc_08013B06|
	LDRB     r2, [r0, #0xc]
	ADD      r2, #0xff
	LSL      r3, r2, #0x18
	LSR      r3, r3, #0x18
	ADD      r2, r5, #0
	CMP      r3, r5
	STRB     r3, [r0, #0xc]
	BLE      |loc_08013AFC|
|loc_08013ADE|
	ADD      r3, r0, r2
	LDRB     r4, [r3, #0xe]
	STRB     r4, [r3, #0xd]
	LSL      r3, r2, #1
	ADD      r4, r3, r0
	ADD      r3, r4, #0
	ADD      r3, #0x20
	LDRB     r7, [r3, #0x10]
	ADD      r2, #1
	STRB     r7, [r3, #0xe]
	LDRB     r7, [r3, #0x11]
	STRB     r7, [r3, #0xf]
	LDRB     r3, [r0, #0xc]
	CMP      r3, r2
	BGT      |loc_08013ADE|
|loc_08013AFC|
	LDRB     r2, [r0, #0x15]
	LDRB     r3, [r0, #0xc]
	CMP      r2, r3
	BCC      |loc_08013B06|
	STRB     r6, [r0, #0x15]
|loc_08013B06|
	LDRB     r2, [r0, #0xc]
	ADD      r5, #1
	CMP      r2, r5
	BGT      |loc_08013AC6|
|loc_08013B0E|
	POP      {r4, r5, r6, r7}
	BX       lr
