	CODE16
|loc_08013B12|
	PUSH     {r4, r5}
	LDRB     r5, [r0, #0xc]
	MOV      r3, #0
	CMP      r5, #0
	BLE      |loc_08013B28|
	ADD      r4, r0, r3
	LDRB     r4, [r4, #0xd]
	CMP      r4, r1
	BNE      |sub_08013B2C|
	ADD      r0, r0, r3
	STRB     r2, [r0, #0xd]
|loc_08013B28|
	POP      {r4, r5}
	BX       lr
