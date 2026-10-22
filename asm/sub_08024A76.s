	CODE16
|sub_08024A76|
	LSL      r0, r0, #0
	LDR      r1, [sp, #0x350]
	LSR      r4, r0, #0x20
|loc_08024A7C|
	PUSH     {r3, lr}
	CMP      r0, #0
|loc_08024A80|
	BNE      |loc_08024A8C|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08024A9A|
|loc_08024A8C|
	LDR      r1, [pc, #0x2b4]
	STR      r1, [r0]
	MOV      r1, #0
	STRB     r1, [r0, #5]
	STRB     r1, [r0, #6]
	STR      r1, [r0, #8]
	STRB     r1, [r0, #4]
|loc_08024A9A|
	POP      {r3, pc}
|loc_08024A9C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x2a4]
	ADD      r4, r1, #0
	SUB      sp, #0x14
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	MOV      r2, #0x40
	MOV      r1, #0
	MOV      r0, #3
	LSL      r0, r0, #0x19
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x40
	LDR      r1, [pc, #0x290]
	LDR      r0, [pc, #0x290]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r1, [pc, #0x290]
	CMP      r4, #0
	BNE      |loc_08024ACA|
	MOV      r1, #0
|loc_08024ACA|
	MOV      r7, #1
	LSL      r7, r7, #0xb
	ADD      r2, r7, #0
	LDR      r0, [pc, #0x284]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #1
	STRB     r0, [r5, #4]
	LSL      r0, r0, #0xc
	BL       |GBARam_Malloc|
	LDR      r6, [pc, #0x264]
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	ADD      r6, #0x10
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x268]
	LDR      r2, [r6, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x264]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LSR      r3, r7, #1
	ADD      r6, r3, #0
	ADD      r0, r4, #0
	MOV      r1, #0
	SUB      r6, #0x88
|loc_08024B0A|
	LDRH     r2, [r0]
	ADD      r1, #1
	ADD      r2, r2, r6
	STRH     r2, [r0]
	ADD      r0, #2
	CMP      r1, r3
	BLT      |loc_08024B0A|
	ADD      r2, r7, #0
	LDR      r7, [pc, #0x248]
	ADD      r1, r4, #0
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x2c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_08024B60|
	LDR      r0, [pc, #0x214]
	ADD      r1, r4, #0
	SUB      r0, #0xd8
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r2, #0xff
	ADD      r2, #1
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x220]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #2
	STR      r0, [sp, #0xc]
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	ADD      r1, r7, #0
	STR      r6, [sp, #4]
	STR      r6, [sp, #8]
	LDR      r2, [pc, #0x210]
	BL       |inc_0x03d784_0x041118| + 0x28c
|loc_08024B60|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x30]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_08024B9E|
	LDR      r0, [pc, #0x1d8]
	ADD      r1, r4, #0
	SUB      r0, #0x78
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r2, #0xff
	ADD      r2, #1
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x1ec]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0x1c
	STR      r0, [sp, #4]
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, #2
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	ADD      r1, r7, #0
	STR      r6, [sp, #8]
	LDR      r2, [pc, #0x1d8]
	BL       |inc_0x03d784_0x041118| + 0x28c
|loc_08024B9E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	MOV      r0, #0x3b
	LSL      r0, r0, #7
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r1, #8]
	LDR      r0, [pc, #0x1c8]
	LDR      r4, [pc, #0x194]
	STRH     r0, [r1, #0xe]
	STRH     r6, [r1, #0x10]
	STRH     r6, [r1, #0x12]
	STRH     r6, [r1, #0x1c]
	STRH     r6, [r1, #0x1e]
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11426
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x1a8]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x1a0]
	LDR      r0, [pc, #0x1a0]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|loc_08024BE6|
	LDR      r1, [pc, #0x19c]
	LDR      r2, [pc, #0x19c]
	STRH     r1, [r2, #0x10]
	MOV      r1, #1
	STR      r1, [r0, #8]
	BX       lr
	LDRB     r1, [r0, #5]
	CMP      r1, #0
	BEQ      |loc_08024C02|
	LDR      r1, [pc, #0x190]
	LDR      r2, [pc, #0x18c]
	STRH     r1, [r2, #0x10]
	MOV      r1, #1
	STR      r1, [r0, #8]
|loc_08024C02|
	BX       lr
	PUSH     {r3, lr}
	LDRB     r1, [r0, #6]
	CMP      r1, #1
	BEQ      |sub_08024C22|
	CMP      r1, #2
	BNE      |loc_08024C34|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x38]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, pc}
