	CODE16
|sub_0803B2A8|
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803B2B8|
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0]
|loc_0803B2B8|
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803B2D6|
	LDR      r1, [pc, #0x14]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0803B2D6|
	POP      {r4, pc}
|loc_0803B2D8|
	DCW      0x32e4
	DCW      0x0300,0xcccd,0x42cc,0xb134,0x0877,0xb698
|loc_0803B2E6|
	LSR      r4, r0, #0x20
	BLS      |loc_0803B324|
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDRH     r1, [r1, #0x12]
	CMP      r1, #0
	BNE      |sub_0803B304|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
