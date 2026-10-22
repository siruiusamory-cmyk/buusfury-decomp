	CODE16
|Object_Destroy24|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x220]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x21c]
	CMP      r1, r0
	BEQ      |loc_08038BCC|
	LDR      r0, [pc, #0x20c]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08038BCC|
	LDR      r0, [pc, #0x210]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08038BDA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08038BDA|
	POP      {r3, r4, r5, pc}
