	CODE16
|Object_Destroy13|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x268]
	ADD      r6, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x44]
	LDR      r5, [pc, #0x264]
	CMP      r0, #0
	BNE      |loc_08021318|
	LDR      r2, [pc, #0x264]
	LDR      r0, [r5]
	LDR      r1, [pc, #0x25c]
	ADD      r0, r0, r2
	BL       |inc_0x03d784_0x041118| + 0xb7e
|loc_08021318|
	LDR      r0, [pc, #0x25c]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x25c]
	CMP      r1, r0
	BEQ      |loc_0802132A|
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0802132A|
	LDR      r0, [pc, #0x254]
	CMP      r6, #0
	STR      r0, [r4]
	BEQ      |loc_08021338|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08021338|
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	LDR      r1, [r0, #0x40]
	LDR      r2, [r0, #0x44]
	ADD      r4, r0, #0
	ADD      r1, #1
	CMP      r2, #0
	LDR      r0, [r0, #0x5c]
	SUB      sp, #0x34
	BEQ      |loc_0802142C|
	LDR      r2, [r4, #0x48]
	CMP      r2, #0
	BEQ      |loc_08021380|
	STR      r1, [r4, #0x40]
	LDRB     r2, [r0, #2]
	ASR      r1, r1, #2
	CMP      r2, r1
	BGT      |sub_0802136C|
	LDR      r5, [pc, #0x20c]
	ADD      r1, r4, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
