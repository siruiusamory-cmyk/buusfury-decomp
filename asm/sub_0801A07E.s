	CODE16
|sub_0801A07E|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801A096|
	LDR      r1, [pc, #0x288]
	STR      r1, [r0]
	MOV      r1, #0
	STRB     r1, [r0, #4]
	STR      r1, [r0, #8]
|loc_0801A096|
	ADD      r5, r0, #0
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x264]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_0801A0BA|
	MOV      r0, #0
	POP      {r3, pc}
