|sub_0800F4C0|
	EXPORT |sub_0800F4C0|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0800F4DA|
	CMP      r4, #0xe
	BLT      |sub_0800F4E2|
	MOV      r0, #2
	POP      {r4, pc}
|loc_0800F4DA|
	CMP      r4, #0xd
	BLT      |sub_0800F4E2|
	MOV      r0, #2
	POP      {r4, pc}
