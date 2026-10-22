	CODE16
|unk_08036E8E|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r3, [r1, #0x74]
	ADD      r3, r3, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
	ADD      r2, #0x80
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xbc]
	PUSH     {r4}
	LDR      r2, [r0]
	SUB      sp, #0x20
	CMP      r2, #0
	BNE      |sub_08036EB8|
	MOV      r0, #0
	ADD      sp, #0x20
	POP      {r4}
	BX       lr
