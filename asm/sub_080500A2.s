	CODE16
|sub_080500A2|
	LSL      r0, r0, #0
	LDRH     r1, [r1, #0x12]
	MOV      r0, #1
	CMP      r1, #8
	BHI      |loc_080500AE|
	MOV      r0, #0
|loc_080500AE|
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x11
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed58
	CMP      r0, #0
	BNE      |sub_080500D0|
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed58
	CMP      r0, #0
	BNE      |sub_080500D0|
	MOV      r0, #1
	POP      {r4, pc}
