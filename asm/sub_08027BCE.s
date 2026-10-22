	CODE16
|sub_08027BCE|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	SUB      r1, #1
	STR      r1, [r0, #0x10]
	BNE      |sub_08027BE2|
	LDR      r0, [r0, #0x18]
	BL       |sub_08027D3E|
	MOV      r0, #1
	POP      {r3, pc}
