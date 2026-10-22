	CODE16
|sub_0803B30E|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #0x58]
	ADD      r5, r1, #0
	ADD      r0, #0x48
	LDR      r0, [r0, #0x54]
	LDR      r1, [r1, #0x50]
	CMP      r0, r1
	BEQ      |loc_0803B324|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_0803B324|
	LDR      r0, [r4, #4]
	MOV      r6, #1
	CMP      r0, #0
	BNE      |loc_0803B346|
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803B33A|
	LDR      r1, [pc, #0x30]
	STR      r1, [r0]
|loc_0803B33A|
	ADD      r1, r0, #0
	STR      r0, [r4, #8]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	STR      r6, [r4, #4]
|loc_0803B346|
	LDR      r0, [r4, #8]
	LDR      r2, [r5, #0x14]
	ADD      r1, r6, #0
	CMP      r2, r0
	BEQ      |loc_0803B352|
	MOV      r1, #0
|loc_0803B352|
	SUB      r0, r6, r1
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803B366|
	LDR      r1, [pc, #8]
	STR      r1, [r0]
|loc_0803B366|
	POP      {r3, pc}
|sub_0803B368|
|unk_0803B368|
	INCBIN	baserom.gba_0x3b368_0x3b36a.extracted
