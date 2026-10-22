	CODE16
|sub_080091FE|
	LSR      r7, r0, #0x20
	ADD      r0, r5, r5
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_08009214|
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800921E|
|loc_08009214|
	MOV      r1, #0
	STR      r1, [r0]
	STR      r1, [r0, #4]
	STR      r1, [r0, #8]
	STR      r1, [r0, #0xc]
|loc_0800921E|
	POP      {r3, pc}
