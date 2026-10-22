	CODE16
|sub_0804F20E|
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	BEQ      |loc_0804F240|
	LDR      r0, [pc, #0x2c]
	MOV      r5, #0
	STR      r0, [r4]
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BLE      |loc_0804F23A|
|loc_0804F222|
	LSL      r0, r5, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #8]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_0804F222|
|loc_0804F23A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0804F240|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	ADD      r2, sp, #0x3d0
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
|sub_0804F260|
|unk_0804F260|
		BX       lr
