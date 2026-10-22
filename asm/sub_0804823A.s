	CODE16
|sub_0804823A|
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0xd0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048248|
	DCW      0x1964
	DCW      0x0300,0xbe08
|loc_0804824E|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0xc]
	MOV      r0, #0
	STR      r0, [r1]
	STR      r0, [r1, #4]
	STR      r0, [r1, #8]
	STR      r0, [r1, #0xc]
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, r2, r6
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x24]
	MOV      r2, #8
	ADD      r0, r4, #0
	ADD      r0, #0x44
	ADD      r1, r0, #0
	ADD      r1, #0x18
	LDR      r3, [pc, #0x1c]
	BL       |__vecmap1c__FPvT1iPFPv_v|
	ADD      r0, r4, #0
	ADD      r0, #0x5c
	ADD      r1, r0, #0
	MOV      r2, #0xc
	ADD      r1, #0x30
	LDR      r3, [pc, #0x10]
	BL       |__vecmap1c__FPvT1iPFPv_v|
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r4, r6
	LSL      r0, r0, #0xc
	LSL      r1, r4, #0x1d
	LSR      r5, r0, #0x20
	LSL      r1, r2, #0x1e
	LSR      r5, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_080482A0|
|unk_080482A0|
	INCBIN	baserom.gba_0x482a0_0x482a2.extracted
