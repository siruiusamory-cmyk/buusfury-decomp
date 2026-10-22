	CODE16
|sub_0800C052|
	MOV      r1, #1
	LSL      r1, r1, #0xc
	BL       |inc_0x046118_0x049114| + 0xe18
	STRH     r0, [r4, #0x1e]
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	CMP      r1, #2
	BLT      |sub_0800C068|
	MOV      r0, #2
	BX       lr
