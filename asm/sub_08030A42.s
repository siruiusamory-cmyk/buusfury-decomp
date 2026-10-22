	CODE16
|sub_08030A42|
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #0x1c]
	MOV      r0, #1
	BX       lr
	PUSH     {r4}
	LDR      r1, [r0, #0x2c]
	CMP      r1, #0
	BNE      |loc_08030A64|
	LDR      r1, [pc, #0x4c]
	SUB      r1, #8
	LDR      r1, [r1]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1f
	BEQ      |sub_08030A68|
	MOV      r1, #1
	STR      r1, [r0, #0x2c]
|loc_08030A64|
	POP      {r4}
	BX       lr
