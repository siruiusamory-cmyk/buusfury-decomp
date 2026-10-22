	CODE16
|Irq_WriteMaster2|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x40
	BL       |sub_080407A0|
	CMP      r0, #0
	BNE      |loc_0803FB8E|
	MOV      r0, #1
	B        |loc_0803FB90|
|loc_0803FB8E|
	MOV      r0, #0
|loc_0803FB90|
	STR      r0, [r4]
	CMP      r0, #0
	BEQ      |loc_0803FBDC|
	MOV      r0, #1
	LSL      r0, r0, #0xd
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x100]
	STR      r5, [r0]
	LDR      r0, [pc, #0x100]
	LDR      r0, [r0]
	BL       |loc_0803F278|
	BL       |loc_080401DA|
	LDR      r6, [pc, #0xf8]
	MOV      r0, #0
	STRH     r0, [r6, #8]
	MOV      r4, #0
	LSR      r7, r6, #0xd
|loc_0803FBBA|
	ASR      r0, r4, #3
	LSL      r0, r0, #0x10
	ADD      r1, r5, r4
	LSR      r0, r0, #0x10
	BL       |sub_08040868|
	ADD      r4, #8
	CMP      r4, r7
	BLT      |loc_0803FBBA|
	MOV      r0, #1
	STRH     r0, [r6, #8]
	BL       |loc_080401F4|
	LDR      r0, [pc, #0xd0]
	LDR      r0, [r0]
	BL       |loc_0803F28E|
|loc_0803FBDC|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r0, [r0]
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r5, r3, #0
	CMP      r0, #0
	BEQ      |loc_0803FC38|
	LDR      r0, [pc, #0xb4]
	ADD      r2, r5, #0
	LDR      r0, [r0]
	ADD      r0, r0, r6
	ADD      r1, r7, #0
	BL       |inc_0x049120_0x055620| + 0x24
	LDR      r0, [pc, #0xac]
	LDR      r0, [r0]
	BL       |loc_0803F278|
	BL       |loc_080401DA|
	LDR      r1, [pc, #0xa4]
	MOV      r0, #0
	STRH     r0, [r1, #8]
	MOV      r4, #0
	CMP      r5, #0
	BLE      |loc_0803FC26|
|loc_0803FC12|
	ADD      r1, r7, r4
	ADD      r0, r6, r4
	ASR      r0, r0, #3
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	BL       |sub_08040B5C|
	ADD      r4, #8
	CMP      r4, r5
	BLT      |loc_0803FC12|
|loc_0803FC26|
	LDR      r1, [pc, #0x84]
	MOV      r0, #1
	STRH     r0, [r1, #8]
	BL       |loc_080401F4|
	LDR      r0, [pc, #0x74]
	LDR      r0, [r0]
	BL       |loc_0803F28E|
|loc_0803FC38|
	POP      {r3, r4, r5, r6, r7, pc}
	ADD      r0, r1, #0
	ADD      r1, r2, #0
	ADD      r2, r3, #0
	PUSH     {r3, lr}
	LDR      r3, [pc, #0x60]
	LDR      r3, [r3]
	ADD      r1, r3, r1
	BL       |inc_0x049120_0x055620| + 0x24
	POP      {r3, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r6, r0, #0
	LDR      r0, [sp, #8]
	LDR      r1, [pc, #0x58]
	MOV      r5, #0
	MOV      r4, #1
	CMP      r0, #0
	STR      r1, [sp]
	BLE      |loc_0803FC9C|
|loc_0803FC62|
	LDR      r0, [sp]
	LDR      r1, [sp, #8]
	CMP      r1, r0
	BGE      |loc_0803FC6E|
	ADD      r0, sp, #8
	B        |loc_0803FC70|
|loc_0803FC6E|
	MOV      r0, sp
|loc_0803FC70|
	LDR      r0, [r0]
	SUB      r7, r1, r0
	STR      r7, [sp, #8]
	CMP      r0, #0
	BLE      |loc_0803FC88|
|loc_0803FC7A|
	LDRB     r1, [r6]
	ADD      r6, #1
	SUB      r0, #1
	ADD      r4, r1, r4
	ADD      r5, r5, r4
	CMP      r0, #0
	BGT      |loc_0803FC7A|
|loc_0803FC88|
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0xa060
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0xa060
	ADD      r5, r0, #0
	CMP      r7, #0
	BGT      |loc_0803FC62|
|loc_0803FC9C|
	LSL      r0, r5, #0x10
	ORR      r0, r4
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_0803FCA4|
|unk_0803FCA4|
	INCBIN	baserom.gba_0x3fca4_0x3fca6.extracted
