	CODE16
|sub_0800A134|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A148|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A148|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0xb4]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A17C|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A17C|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0x80]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x70]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0xf
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	ADD      r6, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A1C2|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A1C2|
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0x40]
	STR      r0, [r4]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800A1E8|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800A1E8|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |sub_08009D24|
	LDR      r0, [pc, #0x20]
	STR      r0, [r4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|sub_0800A208|
|unk_0800A208|
	INCBIN	baserom.gba_0xa208_0xa20a.extracted
