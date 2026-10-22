	CODE16
|sub_0803A736|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #0x58]
	ADD      r5, r1, #0
	ADD      r0, #0x4c
	LDR      r0, [r0, #0x54]
	LDR      r1, [r1, #0x50]
	CMP      r0, r1
	BEQ      |loc_0803A74C|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_0803A74C|
	LDR      r0, [r4, #4]
	MOV      r6, #1
	CMP      r0, #0
	BNE      |loc_0803A76E|
	MOV      r0, #8
	STR      r6, [r4, #4]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A764|
	LDR      r1, [pc, #0x30]
	STR      r1, [r0]
|loc_0803A764|
	ADD      r1, r0, #0
	STR      r0, [r4, #8]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
|loc_0803A76E|
	LDR      r0, [r4, #8]
	LDR      r2, [r5, #0x14]
	ADD      r1, r6, #0
	CMP      r2, r0
	BEQ      |loc_0803A77A|
	MOV      r1, #0
|loc_0803A77A|
	SUB      r0, r6, r1
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A78E|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
|loc_0803A78E|
	POP      {r3, pc}
|sub_0803A790|
|unk_0803A790|
	INCBIN	baserom.gba_0x3a790_0x3a792.extracted
