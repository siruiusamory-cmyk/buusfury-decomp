	CODE16
|sub_0804EF6C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EF88|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0xc]
	STR      r2, [r0]
	STR      r1, [r0, #0x10]
|loc_0804EF88|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LDMIA    r0!, {r3, r4, r5, r6}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EFAC|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0xc]
	STR      r2, [r0]
	STR      r1, [r0, #0x10]
|loc_0804EFAC|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LDMIA    r5!, {r2, r3, r4, r7}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EFD4|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #0x10]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0x14]
	STR      r2, [r0]
	STR      r1, [r0, #0x18]
|loc_0804EFD4|
	POP      {r4, pc}
	LSL      r0, r0, #0
	BEQ      |loc_0804EFAC|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EFFC|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #0x10]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0x14]
	STR      r2, [r0]
	STR      r1, [r0, #0x18]
|loc_0804EFFC|
	POP      {r4, pc}
	LSL      r0, r0, #0
	BPL      |loc_0804F00C|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x10
|unk_0804F00A|
	INCBIN	baserom.gba_0x4f00a_0x4f00c.extracted
|loc_0804F00C|
|unk_0804F00C|
	INCBIN	baserom.gba_0x4f00c_0x4f00e.extracted
	ADD      r4, r0, #0
	BNE      |sub_0804F016|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
