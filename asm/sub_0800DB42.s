	CODE16
|sub_0800DB42|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |Handle_Acquire1|
	ADD      r0, r4, #0
	BL       |loc_0800D918|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BNE      |sub_0800DB60|
	BL       |loc_0800D918|
	MOV      r0, #0
	POP      {r3, pc}
