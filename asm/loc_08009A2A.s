	CODE16
|loc_08009A2A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r4, r0, #0
	ADD      r6, #0x80
	LDR      r0, [r6, #0x28]
	BL       |GBARam_Free|
	LDR      r0, [r6, #0x2c]
	BL       |GBARam_Free|
	LDR      r0, [r6, #0x30]
	BL       |GBARam_Free|
	LDR      r0, [pc, #0x98]
	ADD      r7, r4, #0
	LDR      r5, [r0]
	ADD      r7, #0x18
	LDR      r0, [r5]
	STR      r0, [r4]
	LDR      r1, [r5, #4]
	ADD      r0, r5, #0
	STR      r1, [r4, #4]
	LDR      r1, [r5, #8]
	ADD      r0, #0x18
	STR      r1, [r4, #8]
	LDR      r1, [r5, #0xc]
	STR      r1, [r4, #0xc]
	LDR      r1, [r5, #0x10]
	STR      r1, [r4, #0x10]
	LDR      r1, [r5, #0x14]
	STR      r1, [r4, #0x14]
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r7!, {r1, r2, r3}
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r7!, {r1, r2, r3}
	LDR      r2, [r5, #0x30]
	ADD      r0, r4, #0
	STR      r2, [r4, #0x30]
	LDR      r1, [r5, #0x34]
	ADD      r0, #0x38
	STR      r1, [r4, #0x34]
	ADD      r1, r5, #0
	ADD      r1, #0x38
	LDMIA    r1!, {r1, r2, r3}
	STMIA    r0!, {r1, r2, r3}
	LDR      r2, [pc, #0x5c]
	ADD      r1, r5, #0
	ADD      r1, #0x44
	STR      r2, [sp]
	ADD      r2, r1, #0
	MOV      r3, #8
	ADD      r2, #0x18
	BL       |inc_0x046118_0x049114| + 0xf00
	LDR      r2, [pc, #0x50]
	ADD      r1, r5, #0
	ADD      r1, #0x5c
	ADD      r0, r4, #0
	STR      r2, [sp]
	ADD      r2, r1, #0
	ADD      r0, #0x5c
	MOV      r3, #0xc
	ADD      r2, #0x30
	BL       |inc_0x046118_0x049114| + 0xf00
	MOV      r0, #0x8c
	LDR      r0, [r0, r5]
	ADD      r1, r5, #0
	STR      r0, [r6, #0xc]
	ADD      r0, r4, #0
	ADD      r1, #0x90
	MOV      r2, #0x34
	ADD      r0, #0x90
	BL       |inc_0x046118_0x049114| + 0xcb8
	LDR      r0, [pc, #0x1c]
	LDR      r0, [r0]
	BL       |GBARam_Free|
	LDR      r1, [pc, #0x14]
	MOV      r0, #0
	STR      r0, [r1]
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |loc_0800938C|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08009AD8|
|unk_08009AD8|
	INCBIN	baserom.gba_0x9ad8_0x9ada.extracted
