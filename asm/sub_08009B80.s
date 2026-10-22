	CODE16
|sub_08009B80|
	PUSH     {r4, r5, r6, r7}
	LDR      r2, [r1, #0x48]
	MOV      r6, #0
	LDR      r2, [r2, #4]
	MOV      r4, #0
	LSR      r3, r2, #0x1f
	ADD      r2, r3, r2
	ASR      r2, r2, #1
	STRH     r2, [r0]
	STR      r6, [r0, #4]
	LDR      r2, [r1, #0xc]
	MOV      r3, #7
	LSL      r3, r3, #7
	CMP      r2, #0
	BLE      |loc_08009BCA|
	ADD      r7, r0, #4
|loc_08009BA0|
	LDR      r2, [r7]
	LSL      r6, r4, #2
	ADD      r5, r2, #1
	STR      r5, [r7]
	LDR      r5, [r1, #0x10]
	LSL      r2, r2, #3
	ADD      r2, r2, r7
	LDR      r5, [r5, r6]
	MOV      r6, #0
	ADD      r2, #4
	STRH     r6, [r2]
	ADD      r4, #1
	STRH     r4, [r2, #2]
	STR      r5, [r2, #4]
	LDRH     r2, [r5, #2]
	CMP      r2, r3
	BGE      |loc_08009BC4|
	ADD      r3, r2, #0
|loc_08009BC4|
	LDR      r2, [r1, #0xc]
	CMP      r2, r4
	BGT      |loc_08009BA0|
|loc_08009BCA|
	LDRH     r1, [r0]
	SUB      r1, r3, r1
	STRH     r1, [r0, #2]
	POP      {r4, r5, r6, r7}
	BX       lr
