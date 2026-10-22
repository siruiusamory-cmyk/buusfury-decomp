	CODE16
|sub_0801F384|
	MOV      r1, #2
	STRB     r1, [r0, #0xf]
	BX       lr
|sub_0801F38A|
	DCW      0x0000
	DCW      0x92ec,0x0804,0xffff
|sub_0801F392|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	POP      {r4, r5}
	LSR      r4, r0, #0x20
	LSR      r0, r6, #0x1f
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7}
	LDRB     r6, [r2, #4]
	MOV      r7, #0
	MVN      r7, r7
	CMP      r6, #0
	BNE      |sub_0801F3B6|
	ADD      r0, r7, #0
	POP      {r4, r5, r6, r7}
	BX       lr
