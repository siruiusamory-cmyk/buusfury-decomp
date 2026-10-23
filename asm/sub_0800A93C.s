|sub_0800A93C|
	EXPORT |sub_0800A93C|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_0800A94E|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800A958|
|loc_0800A94E|
	MOV      r1, #0xff
	STRB     r1, [r0, #4]
	MOV      r1, #0
	STR      r1, [r0]
	STR      r4, [r0, #8]
|loc_0800A958|
	POP      {r4, pc}
