	CODE16
|sub_0801F038|
	STR      r0, [r4, #0x1c]
	LDR      r0, [r4, #0x28]
	CMP      r0, #0
	BEQ      |loc_0801F044|
	SUB      r0, #1
	STR      r0, [r4, #0x28]
|loc_0801F044|
	LDR      r0, [r4, #0x28]
	STR      r0, [r4, #0x2c]
	STR      r6, [r4, #0x10]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801F052|
|unk_0801F052|
; cited by 0x0801ED38 (a pc-relative load targets 0x0801F060)
		SUB r0, #1
		STR r0, [r4, #0x2c]
|loc_0801F056|
		ADD r0, r5, #0
		BL       |loc_080067F4|
		DCW     0xE7F8
	INCBIN  baserom.gba_0x1f05e_0x1f06a.extracted
