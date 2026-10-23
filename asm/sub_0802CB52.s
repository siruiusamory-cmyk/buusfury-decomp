	CODE16
|sub_0802CB52|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [r1, #4]
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	MOV      r1, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |loc_0802CB64|
	ADD      r1, r4, #0
|loc_0802CB64|
	STR      r1, [sp]
	LDR      r1, [r4, #0xc]
	MOV      r0, #0x18
	STR      r1, [sp, #4]
	LDR      r1, [r4, #0x10]
	STR      r1, [sp, #8]
	LDR      r6, [r4, #0x18]
	LDR      r7, [r4, #0x1c]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802CB90|
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0]
	LDR      r1, [sp]
	STR      r1, [r0, #4]
	LDR      r1, [sp, #4]
	STR      r1, [r0, #8]
	LDR      r1, [sp, #8]
	ADD      r0, #0xc
	STMIA    r0!, {r1, r6, r7}
	SUB      r0, #0x18
|loc_0802CB90|
	ADD      r6, r0, #0
	LDRB     r0, [r4, #8]
	LDR      r1, [pc, #0x18]
	LDRB     r1, [r1, r0]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_0802CBAA|
|unk_0802CBAA|
	INCBIN	baserom.gba_0x2cbaa_0x2cbae.extracted
|sub_0802CBAE|
	DCW      0x0804
	DCW      0x2670
	DCW      0x0807
