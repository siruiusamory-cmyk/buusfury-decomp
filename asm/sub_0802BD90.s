	CODE16
|sub_0802BD90|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x30]
	ADD      r1, #1
	STR      r1, [r0, #0x30]
	CMP      r1, #0x3c
	BLE      |sub_0802BDAA|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x28]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #0
	POP      {r3, pc}
