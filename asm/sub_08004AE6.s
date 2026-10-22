	CODE16
|sub_08004AE6|
	LSL      r0, r0, #0
	LSL      r5, r4, #0xd
	LSR      r5, r0, #0x20
	BGE      |loc_08004B88|
	LSR      r7, r5, #1
	DCW      0xf74c,0xffff
	STRB     r4, [r4, r6]
	LSR      r5, r0, #0x20
	LSR      r4, r6, #2
	LSL      r0, r0, #0
	DCW      0xf740,0xffff
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	LDMIA    r2!, {r2, r5}
	LSR      r4, r6, #1
	LDR      r0, [pc, #0xac]
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r1, [r0, #8]
	LDR      r0, [pc, #0xac]
	LDRB     r6, [r1]
	LDRB     r7, [r1, #1]
	LDR      r1, [r0]
	MOV      r3, #0
	CMP      r1, #0
	MOV      ip, r1
	BLE      |loc_08004B4E|
	LDR      r0, [r0, #4]
	MOV      lr, r0
|loc_08004B22|
	MOV      r0, lr
	LSL      r1, r3, #2
	LDR      r0, [r0, r1]
	MOV      r1, #0
	LDR      r5, [r0, #0x14]
	CMP      r5, #0
	BLE      |loc_08004B48|
|loc_08004B30|
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	LDR      r2, [r2, #0x18]
	LDRB     r4, [r2]
	CMP      r4, r6
	BNE      |loc_08004B42|
	LDRB     r2, [r2, #1]
	CMP      r2, r7
	BEQ      |loc_08004B50|
|loc_08004B42|
	ADD      r1, #1
	CMP      r5, r1
	BGT      |loc_08004B30|
|loc_08004B48|
	ADD      r3, #1
	CMP      ip, r3
	BGT      |loc_08004B22|
|loc_08004B4E|
	MOV      r0, #0
|loc_08004B50|
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x64]
	MOV      r4, #0
	LDR      r3, [r0]
	MOV      ip, r3
	CMP      r3, #0
	BLE      |loc_08004BB2|
	LDR      r0, [r0, #4]
	MOV      lr, r0
	MOV      r0, lr
	LSL      r3, r4, #2
	LDR      r5, [r0, r3]
	MOV      r0, #0
	LDR      r7, [r5, #0x14]
	CMP      r7, #0
	BLE      |loc_08004BAC|
	LSL      r3, r0, #2
	ADD      r3, r3, r5
	LDR      r3, [r3, #0x18]
	LDRB     r6, [r3]
	CMP      r6, r1
	BNE      |loc_08004BA6|
	LDRB     r6, [r3, #1]
	CMP      r6, r2
	BNE      |loc_08004BA6|
	LDRH     r0, [r3, #2]
	LDR      r2, [sp]
|loc_08004B88|
	LSR      r1, r0, #3
	ADD      r1, r1, r2
	LSL      r2, r0, #0x1d
	ADD      r1, #0x80
	LDRB     r1, [r1, #0xd]
	LSR      r2, r2, #0x1d
	MOV      r0, #1
	LSL      r0, r2
	AND      r1, r0
	BEQ      |sub_08004BA2|
	MOV      r0, #1
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
