	CODE16
|sub_0800B82C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_08011818|
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x10]
	POP      {r4, pc}
	CMP      r1, #0xb
	BNE      |sub_0800B84A|
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #0x10]
	MOV      r0, #0
	BX       lr
