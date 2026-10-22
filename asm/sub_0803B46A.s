	CODE16
|sub_0803B46A|
	LDR      r3, [pc, #0x84]
	ADD      r0, #0xff
	STR      r6, [sp, #0x10]
	ADD      r0, #0xa1
	STR      r3, [sp, #0xc]
	LDMIA    r0!, {r3}
	LDR      r6, [pc, #0x78]
	LDR      r0, [r0]
	ADD      r3, r3, r6
	STR      r0, [sp, #8]
	ADD      r0, r3, #0
	STR      r3, [sp, #4]
	LDR      r3, [sp, #8]
	STR      r0, [sp, #0x14]
	STR      r3, [sp, #0x18]
	STR      r0, [r2]
	LDR      r0, [sp, #0x18]
	STR      r0, [r1]
	MOV      r0, #3
	STRB     r0, [r4, #0x10]
	MOV      r0, #8
	STR      r7, [r5, #4]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803B4A2|
	LDR      r1, [pc, #0x54]
	STR      r1, [r0]
|loc_0803B4A2|
	ADD      r6, r0, #0
	MOV      r1, #0x12
	STR      r0, [r5, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [r5, #8]
	LDR      r2, [r4, #0x14]
	ADD      r1, r7, #0
	CMP      r2, r0
	BEQ      |loc_0803B4C2|
	MOV      r1, #0
|loc_0803B4C2|
	SUB      r0, r7, r1
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803B4D8|
	LDR      r1, [pc, #0x20]
	STR      r1, [r0]
|loc_0803B4D8|
	POP      {r3, pc}
|loc_0803B4DA|
	DCW      0x0000
	DCW      0x8098,0x086b,0x1c34,0x0300,0xb158,0x0877,0x92a8,0x0831
	DCW      0x05c4,0x0000,0xec00,0xffff,0xd714,0x0804,0xc174,0x0804
