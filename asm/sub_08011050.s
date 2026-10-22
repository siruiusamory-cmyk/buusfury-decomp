	CODE16
|sub_08011050|
	PUSH     {r3, lr}
	BL       |loc_0801155C|
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	CMP      r1, #0
	SUB      sp, #0x10
	BNE      |loc_080110CE|
	LDR      r0, [r2, #0x20]
	ADD      r5, r2, #0
	CMP      r0, r4
	BNE      |sub_08011070|
	MOV      r0, #0
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
