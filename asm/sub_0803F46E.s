	CODE16
|sub_0803F46E|
	CMP      r0, #0
	BEQ      |loc_0803F53C|
	CMP      r1, #0xff
	BCC      |loc_0803F488|
	LDR      r0, [r2, #8]
	LDR      r6, [r2, #4]
	SUB      r1, #0xff
	SUB      r1, #1
	ADD      r2, r6, #0
	MUL      r2, r1
	LSL      r1, r2, #1
	ADD      r7, r0, r1
	B        |loc_0803F496|
|loc_0803F488|
	LDR      r0, [r2]
	LSL      r1, r1, #1
	LDRH     r1, [r0, r1]
	LSL      r1, r1, #1
	ADD      r7, r1, r0
	LDRH     r6, [r7]
	ADD      r7, #2
|loc_0803F496|
	LDR      r0, [r5, #4]
	LDR      r1, [r5]
	STR      r0, [sp, #0x20]
	ADD      r0, r1, r6
	STR      r0, [sp, #0x24]
	LDR      r0, [sp, #0x20]
	ADD      r2, r4, #0
	ADD      r0, #0x10
	STR      r0, [sp, #0x28]
	STR      r1, [sp, #0x1c]
	ADD      r1, sp, #0x1c
	ADD      r0, sp, #0xc
	ADD      r2, #0x10
	BL       |inc_0x049120_0x055620| + 0xa130
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	CMP      r0, r1
	BGE      |loc_0803F534|
	LDR      r0, [sp, #0x10]
	LDR      r1, [sp, #0x18]
	CMP      r0, r1
	BGE      |loc_0803F534|
	LDR      r0, [sp, #0x14]
	LDR      r1, [sp, #0xc]
	LDR      r2, [sp, #0x10]
	SUB      r0, r0, r1
	LDR      r1, [sp, #0x18]
	LDR      r3, [r5, #4]
	SUB      r1, r1, r2
	SUB      r2, r2, r3
	STR      r2, [sp, #8]
	MOV      r2, #1
	LSL      r2, r1
	SUB      r2, #1
	STR      r2, [sp, #4]
	LDR      r1, [sp, #0xc]
	LDR      r2, [r5]
	SUB      r1, r1, r2
	LSL      r1, r1, #1
	MOV      lr, r1
	LDR      r1, [sp, #0x10]
	LDR      r2, [r4, #0x28]
	ADD      lr, r7
	MUL      r1, r2
	LDR      r2, [r4, #0x24]
	ADD      r1, r1, r2
	LDR      r2, [sp, #0xc]
	ADD      r7, r1, r2
	MOV      r1, #0
	MOV      ip, r1
	CMP      r0, #0
	BLE      |loc_0803F534|
|loc_0803F500|
	MOV      r2, lr
	LDRH     r1, [r2]
	ADD      r2, #2
	MOV      lr, r2
	LDR      r2, [sp, #8]
	LSR      r1, r2
	LDR      r2, [sp, #4]
	AND      r1, r2
	ADD      r2, r7, #0
	CMP      r1, #0
	BEQ      |loc_0803F528|
|loc_0803F516|
	LSL      r3, r1, #0x1f
	BPL      |loc_0803F51E|
	LDRB     r3, [r4, #3]
	STRB     r3, [r2]
|loc_0803F51E|
	LDR      r3, [r4, #0x28]
	ASR      r1, r1, #1
	ADD      r2, r3, r2
	CMP      r1, #0
	BNE      |loc_0803F516|
|loc_0803F528|
	MOV      r1, ip
	ADD      r1, #1
	ADD      r7, #1
	CMP      r1, r0
	MOV      ip, r1
	BLT      |loc_0803F500|
|loc_0803F534|
	LDR      r0, [r5]
	ADD      r0, r0, r6
	ADD      r0, #1
	STR      r0, [r5]
|loc_0803F53C|
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
