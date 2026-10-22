	CODE16
|Gfx_BeginTileLoad1|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0]
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r1, r0, #1
	STRB     r1, [r4]
	CMP      r0, #0
	BNE      |loc_0804E4C0|
	LDR      r0, [pc, #0x20]
	ADD      r1, r5, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x110f4
	LSL      r0, r0, #0x10
	ASR      r0, r0, #0x10
	STRH     r0, [r4, #2]
	LDR      r1, [pc, #0x14]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	BL       |Thunk_VramCopy|
|loc_0804E4C0|
	POP      {r4, r5, r6, pc}
	LSL      r0, r0, #0
	MOV      r5, #0xe8
	LSR      r7, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r3, lr}
	ADD      r0, #0xc
	LDMIA    r0!, {r0, r1, r2}
	BL       |Gfx_BeginTileLoad1|
	POP      {r3, pc}
|sub_0804E4D8|
|unk_0804E4D8|
		BX       lr
	INCBIN  baserom.gba_0x4e4da_0x4e4dc.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4de_0x4e4e0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4e2_0x4e4e4.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4e6_0x4e4e8.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4ea_0x4e4ec.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4ee_0x4e4f0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4f2_0x4e4f4.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4f6_0x4e4f8.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4fa_0x4e4fc.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e4fe_0x4e500.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e502_0x4e504.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e506_0x4e508.extracted
		BX       lr
