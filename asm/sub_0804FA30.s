	CODE16
|sub_0804FA30|
	LDRB     r0, [r0, #4]
	CMP      r0, #0
	BNE      |loc_0804FA3C|
	LDRH     r0, [r1, #0x12]
	CMP      r0, #0x10
	BCS      |sub_0804FA40|
|loc_0804FA3C|
	MOV      r0, #1
	BX       lr
