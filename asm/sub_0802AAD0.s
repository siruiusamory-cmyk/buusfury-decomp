	CODE16
|sub_0802AAD0|
	EXPORT |sub_0802AAD0|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802AAEC|
	LDR      r1, [pc, #0x20]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0802AAEC|
	POP      {r4, pc}
	PUSH     {r3, lr}
	LDR      r3, [pc, #0x18]
	LDR      r3, [r3]
	CMP      r3, #0
	BLE      |sub_0802AB02|
	LDR      r0, [r0, #0xc]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
