	CODE16
|sub_08007C92|
	ADD      r0, #1
	CMP      r0, #2
	BLT      |sub_08007C52|
|loc_08007C98|
	ADD      r1, #1
	CMP      r1, #2
	BLT      |loc_08007C2A|
	MOV      r6, #0
	MOV      r0, #0
	LDR      r1, [pc, #0x1d4]
	LSL      r2, r0, #2
	ADD      r1, sp
	LDR      r1, [r1, r2]
	CMP      r1, #0xff
	BEQ      |loc_08007CF8|
	MOV      ip, r1
	MOV      r3, ip
	LDR      r1, [r4, #8]
	LSL      r3, r3, #2
	ADD      r1, r1, r3
	LDR      r1, [r1, #0x18]
	CMP      r1, #0
	BNE      |sub_08007CCC|
	LDR      r1, [pc, #0x1ac]
	ADD      r2, r2, r4
	STR      r1, [r2, #0x10]
	MOV      r1, #1
	LSL      r1, r0
	ORR      r5, r1
	B        |loc_08007CFE|
