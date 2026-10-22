	CODE16
|sub_0802126A|
	LSR      r4, r0, #0x20
	STR      r4, [r0, r2]
	LSR      r2, r6, #1
	LDR      r0, [pc, #8]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	BL       |loc_080210B6|
	POP      {r3, pc}
|sub_0802127C|
|unk_0802127C|
	INCBIN	baserom.gba_0x2127c_0x2127e.extracted
