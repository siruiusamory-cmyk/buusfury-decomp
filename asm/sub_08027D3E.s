	CODE16
|sub_08027D3E|
	MOV      r1, #0x10
	STR      r1, [r0, #0x4c]
	LDR      r1, [pc, #0x68]
	STR      r1, [r0, #0x18]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x4c]
	CMP      r1, #0
	BEQ      |sub_08027D62|
	SUB      r1, #1
	STR      r1, [r0, #0x4c]
	BNE      |loc_08027D60|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x44]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08027D60|
	POP      {r3, pc}
