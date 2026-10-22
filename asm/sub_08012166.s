	CODE16
|sub_08012166|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	BL       |loc_0800B32C|
	CMP      r0, #0
	BEQ      |sub_08012188|
	LDR      r1, [r4, #4]
	LDR      r4, [pc, #0x14]
	LDR      r0, [r4, #4]
	BL       |loc_08011944|
	LDR      r0, [r4, #4]
	BL       |List_PopAll1|
	MOV      r0, #1
	POP      {r4, pc}
