	CODE16
|sub_08029B30|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029B4C|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08029B4C|
	POP      {r4, pc}
|sub_08029B4E|
	DCW      0x0000
	DCW      0x1b94,0x0300,0xb6b8
|sub_08029B56|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x78]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x20
	CMP      r1, #0
	BNE      |sub_08029B6C|
	MOV      r0, #0
	ADD      sp, #0x20
	POP      {r4, pc}
