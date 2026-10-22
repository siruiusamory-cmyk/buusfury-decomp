	CODE16
|loc_08004A88|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x78]
	MOV      r4, #0
	LDR      r3, [r0]
	MOV      ip, r3
	CMP      r3, #0
	BLE      |loc_08004AD2|
	LDR      r0, [r0, #4]
	MOV      lr, r0
	MOV      r0, lr
	LSL      r3, r4, #2
	LDR      r5, [r0, r3]
	MOV      r0, #0
	LDR      r7, [r5, #0x14]
	CMP      r7, #0
	BLE      |loc_08004ADC|
	LSL      r3, r0, #2
	ADD      r3, r3, r5
	LDR      r3, [r3, #0x18]
	LDRB     r6, [r3]
	CMP      r6, r1
	BNE      |sub_08004AD6|
	LDRB     r6, [r3, #1]
	CMP      r6, r2
	BNE      |sub_08004AD6|
	LDRH     r0, [r3, #2]
	LDR      r2, [sp]
	LSR      r1, r0, #3
	ADD      r1, r1, r2
	LSL      r3, r0, #0x1d
	ADD      r1, #0x80
	LDRB     r2, [r1, #0xd]
	LSR      r3, r3, #0x1d
	MOV      r0, #1
	LSL      r0, r3
	ORR      r0, r2
	STRB     r0, [r1, #0xd]
|loc_08004AD2|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
