	CODE16
|sub_08025C14|
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x40]
	LSL      r0, r0, #0xd
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x10]
	ADD      r7, r5, #0
	LSL      r1, r1, #6
	ADD      r1, r0, r1
	ADD      r1, #0x4c
	STR      r1, [sp, #4]
	CMP      r5, #0x20
	BGE      |loc_08025C46|
	LSL      r0, r6, #1
	STR      r0, [sp, #0x28]
|loc_08025C30|
	LDR      r1, [sp, #4]
	LSL      r0, r7, #8
	ADD      r1, r0, r1
	LSL      r0, r7, #6
	ADD      r0, r0, r4
	LDR      r2, [sp, #0x28]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r7, #1
	CMP      r7, #0x20
	BLT      |loc_08025C30|
|loc_08025C46|
	LDR      r0, [sp, #0xc]
	CMP      r0, #3
	BLT      |sub_08025C66|
	CMP      r5, #0x20
	BGE      |loc_08025C62|
|loc_08025C50|
	LSL      r0, r5, #6
	ADD      r0, r0, r4
	MOV      r2, #0x40
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r5, #1
	CMP      r5, #0x20
	BLT      |loc_08025C50|
|loc_08025C62|
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
