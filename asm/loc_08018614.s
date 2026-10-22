	CODE16
|loc_08018614|
	PUSH     {r4}
	LDR      r2, [r0, #0x10]
	SUB      sp, #0x10
	CMP      r2, #0
	BNE      |sub_08018626|
	MOV      r0, #0
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
