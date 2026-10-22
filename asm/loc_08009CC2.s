	CODE16
|loc_08009CC2|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08009D14|
	ADD      r6, r5, #4
	MOV      r7, #0
|loc_08009CD2|
	LSL      r0, r4, #3
	ADD      r0, r0, r6
	ADD      r0, #4
	LDRH     r1, [r0, #2]
	SUB      r1, #1
	LSL      r1, r1, #0x10
	ASR      r1, r1, #0x10
	STRH     r1, [r0, #2]
	BNE      |loc_08009D0C|
	LDRH     r1, [r0]
	ADD      r1, #1
	LSL      r1, r1, #0x10
	ASR      r1, r1, #0x10
	STRH     r1, [r0]
	LDR      r2, [r0, #4]
	LDRB     r2, [r2]
	CMP      r1, r2
	BLT      |loc_08009CF8|
	STRH     r7, [r0]
|loc_08009CF8|
	MOV      r3, #0
	LDRSH    r2, [r0, r3]
	LDR      r1, [r0, #4]
	LSL      r2, r2, #2
	ADD      r1, r1, r2
	LDR      r1, [r1, #4]
	LDR      r1, [r1]
	STRH     r1, [r0, #2]
	BL       |loc_08009B12|
|loc_08009D0C|
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08009CD2|
|loc_08009D14|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08009D16|
	DCW      0x0000
	DCW      0xe444,0x0804,0xeffc,0xffff,0x1004,0x0000
