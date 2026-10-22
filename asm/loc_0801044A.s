	CODE16
|loc_0801044A|
	LDR      r2, [r4, #0xc]
	ADD      r1, r2, r1
	ASR      r2, r1, #3
	SUB      r1, r1, r2
	STR      r1, [r4, #0xc]
	CMP      r1, #0
	BLE      |loc_0801045C|
	SUB      r1, #1
	STR      r1, [r4, #0xc]
|loc_0801045C|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x81
	LDR      r2, [r1, #0x2c]
	LDR      r3, [r4, #0xc]
	LDR      r6, [pc, #0x114]
	ADD      r2, r2, r3
	STR      r2, [r1, #0x2c]
	ADD      r2, r1, #0
	ADD      r2, #0x2c
	LDR      r3, [r2]
	LDR      r7, [r4, #8]
	ASR      r3, r3, #0xa
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x16
	LDR      r3, [r6, r3]
	MUL      r3, r7
	LDR      r7, [r1, #0x20]
	ASR      r3, r3, #0x12
	ADD      r3, r3, r7
	STR      r3, [r1, #0x20]
	LDR      r2, [r2]
	LDR      r3, [r4, #8]
	ASR      r2, r2, #0xa
	ADD      r2, #0x40
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x16
	LDR      r2, [r6, r2]
	MUL      r2, r3
	LDR      r3, [r1, #0x24]
	ASR      r2, r2, #0x12
	SUB      r2, r3, r2
	STR      r2, [r1, #0x24]
	BL       |loc_0800FEE2|
	LDR      r0, [r4, #0xc]
	CMP      r0, #0x80
	BLE      |sub_080104BE|
	MOV      r1, #0x10
	ADD      r0, r5, #0
	BL       |Record_SelectIndexed|
	LDR      r1, [r4, #4]
	MOV      r0, #2
	CMP      r1, #0
	BNE      |loc_080104BA|
	MOV      r0, #1
|loc_080104BA|
	STRB     r0, [r5, #0x10]
	POP      {r3, r4, r5, r6, r7, pc}
