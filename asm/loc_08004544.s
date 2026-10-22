	CODE16
|loc_08004544|
	PUSH     {r3, r4, r5, r6, r7, lr}
	MOV      r3, #0x68
	MUL      r3, r1
	MOV      r4, #0x9f
	LSL      r4, r4, #3
	ADD      r3, r3, r0
	ADD      r3, r3, r4
	LSL      r4, r2, #2
	ADD      r3, r4, r3
	ADD      r3, #0x3c
	MOV      lr, r3
	LDR      r3, [r3]
	MOV      ip, r4
	LDR      r5, [pc, #0x2b0]
	MOV      r4, ip
	LDR      r4, [r5, r4]
	CMP      r3, r4
	BEQ      |loc_080045AE|
	ADD      r5, r0, #0
	ADD      r5, #0xe4
	LDR      r6, [r5]
	MOV      r4, #0
	CMP      r6, #0
	BLE      |loc_080045B6|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	ADD      r0, #4
	LDR      r3, [r0]
	LSR      r7, r3, #0x1c
	SUB      r7, #1
	CMP      r7, r1
	BNE      |sub_080045B0|
	LSL      r7, r3, #4
	LSR      r7, r7, #4
	MOV      r3, #0x2c
	MUL      r3, r7
	LDR      r7, [pc, #0x284]
	ADD      r3, r3, r7
	LDRB     r3, [r3, #0x14]
	CMP      r3, r2
	BNE      |sub_080045B0|
	LDR      r1, [r0]
	LDR      r5, [pc, #0x274]
	LSL      r1, r1, #4
	LSR      r1, r1, #4
	STR      r1, [r0]
	MOV      r4, ip
	LDR      r0, [r5, r4]
	MOV      r3, lr
|loc_080045A6|
	STR      r0, [r3]
	LDR      r1, [r3]
	CMP      r1, r0
	BNE      |loc_080045A6|
|loc_080045AE|
	POP      {r3, r4, r5, r6, r7, pc}
