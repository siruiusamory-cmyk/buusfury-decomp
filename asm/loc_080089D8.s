	CODE16
|loc_080089D8|
	PUSH     {lr}
	LDR      r1, [r0, #0x24]
	SUB      sp, #0x6c
	LSR      r2, r1, #0x10
	BNE      |sub_080089E8|
	ADD      r0, r1, #0
	ADD      sp, #0x6c
	POP      {pc}
