	CODE16
|sub_0802CD84|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	BEQ      |loc_0802CDA4|
	MOV      r0, #0xaf
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |sub_0802CDA6|
	MOV      r0, #0xb0
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_0802CDA4|
	POP      {r3, r4, r5, pc}
