	CODE16
|__vecmap1c__FPvT1iPFPv_v|
	PUSH     {r6, r7, lr}
	PUSH     {r3, r4, r5}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	CMP      r0, r1
	BEQ      |loc_08047010|
|loc_08047004|
	ADD      r0, r4, #0
	BL       |sub_08046AAE|
	ADD      r4, r4, r6
	CMP      r4, r5
	BNE      |loc_08047004|
|loc_08047010|
	POP      {r3, r4, r5, r6, r7}
	POP      {r3}
	BX       r3
	LSL      r0, r0, #0
	PUSH     {r6, r7, lr}
	PUSH     {r3, r4, r5}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r7, r2, #0
	ADD      r6, r3, #0
	CMP      r1, r2
	BCS      |loc_0804703A|
|loc_08047028|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x18]
	BL       |loc_08046AA4|
	ADD      r4, r4, r6
	ADD      r5, r5, r6
	CMP      r4, r7
	BCC      |loc_08047028|
|loc_0804703A|
	POP      {r3, r4, r5, r6, r7}
	POP      {r3}
	BX       r3
|sub_08047040|
|unk_08047040|
; cited by 0x08046E0A (a pc-relative load targets 0x0804708C)
	INCBIN	baserom.gba_0x47040_0x47648.extracted
