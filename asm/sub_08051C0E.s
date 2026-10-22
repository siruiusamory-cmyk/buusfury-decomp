	CODE16
|sub_08051C0E|
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08051C2A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051C2A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08051C42|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051C42|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08051C5A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051C5A|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051C6A|
	BL       |GBARam_Free|
|loc_08051C6A|
	POP      {r3, pc}
|sub_08051C6C|
|unk_08051C6C|
	INCBIN	baserom.gba_0x51c6c_0x51c6e.extracted
