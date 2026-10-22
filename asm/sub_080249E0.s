	CODE16
|sub_080249E0|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r4, [pc, #0x30]
	ADD      r6, r1, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #5
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_08024A14|
	LDR      r0, [r4]
	MOV      r1, #0x80
	LDR      r0, [r0, #4]
	SUB      r0, r1, r0
	CMP      r0, #4
	BLT      |loc_08024A14|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |loc_080246B4|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08024A14|
	POP      {r4, r5, r6, pc}
|sub_08024A16|
	DCW      0x0000
	DCW      0xc394,0x0872,0x2fb8,0x0300,0x0000,0x0601,0xc3b8,0x0872
	DCW      0xffff
|sub_08024A2A|
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08024A44|
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08024A44|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
