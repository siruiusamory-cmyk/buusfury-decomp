|sub_08007A28|
	EXPORT |sub_08007A28|
	PUSH     {r3, lr}
	LDRB     r0, [r0, #4]
	LDR      r1, [pc, #0x28]
	MOV      r2, #1
	LSL      r0, r0, #0xb
	ADD      r0, r0, r1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	BL       |inc_0x049120_0x055620| + 0xc
	POP      {r3, pc}
|sub_08007A3E|
|unk_08007A3E|
		BX       lr
