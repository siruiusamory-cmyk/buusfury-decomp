	CODE16
|loc_080116FC|
	PUSH     {r4}
	LDR      r1, [r0, #4]
	CMP      r1, #0x80
	BNE      |sub_0801170A|
	MOV      r0, #0
	POP      {r4}
	BX       lr
