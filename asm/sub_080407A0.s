	CODE16
|sub_080407A0|
	PUSH     {lr}
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	MOV      r2, #0
	CMP      r0, #4
	BNE      |loc_080407BC|
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	B        |loc_080407D8|
|loc_080407B4|
	DCW      0x52f8
	DCW      0x0300,0x7970,0x087b
