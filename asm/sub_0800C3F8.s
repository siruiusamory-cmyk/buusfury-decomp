	CODE16
|sub_0800C3F8|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_08011818|
	ADD      r0, r4, #0
	BL       |loc_0800C298|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r1, #0xb
	BEQ      |sub_0800C420|
	CMP      r1, #0x1f
	BNE      |loc_0800C428|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x18]
	LDR      r0, [r0]
	BL       |loc_08011944|
	MOV      r0, #0
	POP      {r3, pc}
