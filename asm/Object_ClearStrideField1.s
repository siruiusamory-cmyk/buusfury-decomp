	CODE16
|Object_ClearStrideField1|
	MOV      r1, #0
	MOV      r2, #0
|loc_0803E3E8|
	LSL      r3, r1, #6
	ADD      r3, r3, r0
	ADD      r1, #1
	CMP      r1, #0x10
	STRB     r2, [r3, #0x10]
	BLT      |loc_0803E3E8|
	BX       lr
