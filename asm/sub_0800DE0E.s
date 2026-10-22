	CODE16
|sub_0800DE0E|
|unk_0800DE0E|
		MOV r0, #0
|loc_0800DE10|
|unk_0800DE10|
		B        |inc_0x0158_0x143f2| + 0xdcb2
|loc_0800DE12|
|unk_0800DE12|
		ADD r0, r4, #0
	INCBIN  baserom.gba_0xde14_0xde16.extracted
|sub_0800DE16|
|unk_0800DE16|
	INCBIN	baserom.gba_0xde16_0xde1a.extracted
	LSL      r0, r0, #0
	BCS      |loc_0800DE10|
	LSR      r3, r7, #0x20
	ADR      r3, |loc_0800DE74|
	LSR      r4, r0, #0x20
	MOV      r5, #0xa4
	LSR      r7, r0, #0x20
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	PUSH     {r3, lr}
	LDRB     r1, [r2, #4]
	ADD      r1, #0xff
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	STRB     r1, [r2, #4]
	BNE      |sub_0800DE40|
	BL       |loc_0800EDA6|
	POP      {r3, pc}
