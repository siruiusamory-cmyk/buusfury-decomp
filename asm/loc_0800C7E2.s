	CODE16
|loc_0800C7E2|
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x48]
	ADD      r5, r0, #0
	LDRB     r2, [r0, #4]
	LDR      r0, [r6]
	MOV      r1, #8
	BL       |List_CallMethod1|
	ADD      r4, r0, #0
	LDR      r0, [r6]
	ADD      r1, r0, #4
	LDR      r3, [r1]
	MOV      r0, #0
	CMP      r3, #0
	BLE      |loc_0800C810|
|loc_0800C800|
	LSL      r2, r0, #2
	ADD      r2, r2, r1
	LDR      r2, [r2, #4]
	CMP      r2, r4
	BEQ      |loc_0800C814|
	ADD      r0, #1
	CMP      r3, r0
	BGT      |loc_0800C800|
|loc_0800C810|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_0800C814|
	ADD      r2, r4, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |sub_0800C65E|
	ADD      r5, r0, #0
	ADD      r2, r0, #0
	LDR      r0, [r6]
	ADD      r1, r4, #0
	BL       |loc_080119BC|
	ADD      r0, r5, #0
	POP      {r4, r5, r6, pc}
|loc_0800C82E|
	DCW      0x0000
	DCW      0x2550,0x0807,0x268c,0x0807,0x1010,0x0300,0x1018,0x0300
	DCW      0xefec,0xffff,0x1014,0x0000,0xce00,0x0804,0x1008,0x0000
	DCW      0x0000,0x0601,0xe454
|loc_0800C856|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x24]
	SUB      sp, #0x18
	CMP      r0, #0
	BEQ      |loc_0800C874|
	SUB      r0, #1
	STR      r0, [r4, #0x24]
	BNE      |sub_0800C878|
	LDR      r4, [r4, #0x2c]
	LDR      r0, [r4, #0x20]
	ADD      r4, #0x24
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r4!, {r0, r1, r2, r3}
|loc_0800C874|
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
