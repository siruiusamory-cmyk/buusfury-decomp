	CODE16
|loc_0800D754|
|unk_0800D754|
		NEG r1, r4
	LDR      r0, [r5, #8]
	BL       |Object_AppendEntry1|
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_0800D772|
	LDR      r1, [pc, #0x118]
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	STR      r2, [r0, #8]
	STR      r4, [r0, #0xc]
|loc_0800D772|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x110]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_0800D782|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_0800D782|
	LDR      r0, [r5, #4]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r1, #3
	SUB      sp, #0xc
	BEQ      |loc_0800D82E|
	LDR      r0, [pc, #0xdc]
	CMP      r6, #0xa
	BEQ      |loc_0800D7F6|
	CMP      r6, #0xb
	BEQ      |sub_0800D7B4|
	CMP      r6, #0x18
	BNE      |loc_0800D86A|
	LDR      r1, [r4, #0x48]
	MOV      r0, #1
	CMP      r1, r5
	BEQ      |loc_0800D7B0|
	MOV      r0, #0
|loc_0800D7B0|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
