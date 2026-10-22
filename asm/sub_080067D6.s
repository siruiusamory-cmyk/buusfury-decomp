	CODE16
|sub_080067D6|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	PUSH     {r3, lr}
	LDR      r2, [r1, #0x10]
	CMP      r2, #0
	BNE      |loc_080067F2|
	MOV      r2, #1
	STR      r2, [r1, #0x10]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_080067F2|
	POP      {r3, pc}
