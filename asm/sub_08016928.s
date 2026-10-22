	CODE16
|sub_08016928|
	ADD      r3, r0, #0
	ADD      r3, #0xff
	ADD      r3, #0x35
	ADD      r2, r3, #0
	SUB      r2, #0x34
	PUSH     {r4}
	LDR      r4, [r2, #0x1c]
	CMP      r4, #0
	BEQ      |loc_08016940|
	MOV      r3, #0xa1
	LSL      r3, r3, #2
	ADD      r3, r0, r3
|loc_08016940|
	LDR      r0, [r3]
	CMP      r0, #0
	BNE      |sub_0801694A|
	POP      {r4}
	BX       lr
