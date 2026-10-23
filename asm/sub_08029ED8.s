	CODE16
|sub_08029ED8|
	EXPORT |sub_08029ED8|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x128]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x3c
	CMP      r1, #0
	BEQ      |loc_08029EF0|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	LDR      r0, [r0, r1]
	CMP      r0, #0
	BNE      |sub_08029EF6|
|loc_08029EF0|
	MOV      r0, #0
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
