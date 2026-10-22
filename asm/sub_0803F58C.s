	CODE16
|sub_0803F58C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x24]
	ADD      r5, r1, #0
	BL       |GBARam_Free|
	CMP      r5, #0
	BEQ      |loc_0803F5A2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0803F5A2|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	MOV      r7, #1
	ADD      r4, r0, #0
	CMP      r1, #0xff
	LDR      r2, [r0, #0xc]
	SUB      sp, #0x134
	BCC      |sub_0803F5C0|
	LDR      r5, [pc, #0x14c]
	ADD      r0, r7, #0
	CMP      r1, r5
	BCC      |sub_0803F5D0|
	MOV      r0, #0
	B        |sub_0803F5D0|
