	CODE16
|sub_08019572|
	LSL      r0, r0, #0
	CMP      r7, #0xdc
	LSR      r1, r6, #1
	ADD      r2, pc, #0x300
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x24]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r1, r0, #0x1f
	BNE      |loc_0801958C|
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |sub_08019590|
|loc_0801958C|
	MOV      r0, #1
	BX       lr
