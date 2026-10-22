	CODE16
|loc_08042AAA|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |Bios_CpuSet2|
	MOV      r0, #4
	POP      {r3, r4, r5, pc}
