	CODE16
|sub_08040868|
	PUSH     {r4, r5, r6, lr}
	SUB      sp, #0x88
	ADD      r5, r1, #0
	LSL      r0, r0, #0x10
	LSR      r3, r0, #0x10
	LDR      r0, [pc, #0xc]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	CMP      r3, r0
	BCC      |loc_08040888|
	LDR      r0, [pc, #4]
	B        |loc_0804090A|
|sub_08040880|
|unk_08040880|
	INCBIN	baserom.gba_0x40880_0x40882.extracted
