	CODE16
|Blend_WriteAlpha4|
	LDR      r1, [pc, #0x98]
	CMP      r0, #0x90
	BGT      |loc_08033826|
	MOV      r2, #0x90
	SUB      r0, r2, r0
	STRB     r0, [r1, #2]
	LDR      r0, [r4, #4]
	CMP      r0, #0x90
	BNE      |loc_08033836|
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |sub_08033808|
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
