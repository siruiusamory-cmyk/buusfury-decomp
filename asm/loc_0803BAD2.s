	CODE16
|loc_0803BAD2|
	CMP      r0, #0
	BLE      |loc_0803BAEE|
	LDR      r2, [r4]
	ADD      r0, r4, #0
	LDR      r3, [r2, #0x54]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_0803BAEE|
	LDR      r0, [sp, #0x3c]
	STR      r0, [r5]
	LDR      r0, [sp, #0x40]
	STR      r0, [r6]
|loc_0803BAEE|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r2, [pc, #0x118]
	ADD      r5, r1, #0
	LDRB     r1, [r2]
	ADD      r4, r0, #0
	ADD      r0, r1, #1
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1d
	STRB     r1, [r4, #0x18]
	STRB     r0, [r2]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r5, #0
	LDR      r2, [r4, #0x1c]
	LDR      r3, [r4, #0x20]
	ADD      r0, r4, #0
	BL       |loc_0803B6EA|
	LDR      r1, [r5]
	ADD      r6, r0, #0
	LDR      r2, [r1, #0x48]
	ADD      r0, r5, #0
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r6, #0
	BNE      |loc_0803BB46|
	MOV      r0, #0
	STR      r0, [r4, #0x14]
|loc_0803BB46|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDRB     r0, [r0, #0x18]
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_0803BB86|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r4, #0
	LDR      r2, [r5, #0x1c]
	LDR      r3, [r5, #0x20]
	ADD      r0, r5, #0
	BL       |loc_0803B6EA|
	LDR      r1, [r4]
	ADD      r6, r0, #0
	LDR      r2, [r1, #0x48]
	ADD      r0, r4, #0
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r6, #0
	BNE      |loc_0803BB86|
	MOV      r3, #0
	STR      r3, [r5, #0x14]
|loc_0803BB86|
	LDRB     r0, [r5, #0x18]
	ADD      r1, r4, #0
	ADD      r0, #7
	LSL      r0, r0, #0x1d
	LSR      r0, r0, #0x1d
	STRB     r0, [r5, #0x18]
	ADD      r0, r5, #0
	BL       |sub_0803B934|
	MOV      r0, #0x4e
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	LDR      r2, [pc, #0x80]
	LDR      r1, [pc, #0x7c]
	LDR      r2, [r2]
	ADD      r7, r2, r1
	MOV      r2, #0x27
	LDR      r1, [pc, #0x7c]
	LSL      r2, r2, #4
	ADD      r6, r2, r1
	CMP      r0, r5
	BEQ      |loc_0803BBC8|
	MOV      r0, #0x11
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r5
	BEQ      |loc_0803BBC8|
	MOV      r0, #0x4c
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r5
	BNE      |loc_0803BBE0|
|loc_0803BBC8|
	LDRH     r0, [r4, #0x12]
	CMP      r0, #0
	BEQ      |loc_0803BBD2|
	CMP      r0, #0x10
	BNE      |loc_0803BC14|
|loc_0803BBD2|
	ADD      r1, r6, #0
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	B        |loc_0803BC14|
|loc_0803BBE0|
	MOV      r0, #0xa4
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r5
	BEQ      |loc_0803BBFE|
	MOV      r0, #0x44
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r5
	BEQ      |loc_0803BBFE|
	MOV      r0, #0xbf
	BL       |inc_0x0158_0x143f2|
	CMP      r0, r5
	BNE      |loc_0803BC14|
|loc_0803BBFE|
	LDRH     r0, [r4, #0x12]
	CMP      r0, #8
	BEQ      |loc_0803BC08|
	CMP      r0, #0x18
	BNE      |loc_0803BC14|
|loc_0803BC08|
	ADD      r1, r6, #0
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0803BC14|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0803BC18|
|unk_0803BC18|
	INCBIN	baserom.gba_0x3bc18_0x3bc1a.extracted
