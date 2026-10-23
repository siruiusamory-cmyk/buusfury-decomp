	CODE16
|sub_080076F4|
	PUSH     {r3, lr}
	LDR      r1, [r2]
	ADD      r0, r2, #0
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	LSR      r0, r0, #0x1f
	POP      {r3, pc}
|sub_0800770C|
|unk_0800770C|
	INCBIN	baserom.gba_0x770c_0x7710.extracted
|sub_08007710|
	DCW      0x1938
	DCW      0x0300
