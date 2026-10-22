	CODE16
|sub_08024528|
|unk_08024528|
		MOV r2, #0x20
		ADD r1, r4, #4
		LDR r0, [r5, #0x34]
		BL       |Thunk_VramCopy|
|loc_08024532|
|unk_08024532|
		LDR r1, [pc, #0x38]
		MOV r0, #0
		STR r0, [r1]
		MOV r0, #1
		STR r0, [r5, #0x3c]
		LDRB r1, [r4, #3]
		CMP r1, #0
		BEQ      |loc_08024544|
		MOV r0, #2
|loc_08024544|
		STR r0, [r6]
		B        |loc_08024512|
|loc_08024548|
|unk_08024548|
; cited by 0x0802431A (a pc-relative load targets 0x08024558)
		LDRB r1, [r4]
		MOV r0, #2
		CMP r1, #0
		BEQ      |loc_08024552|
		MOV r0, #3
|loc_08024552|
		STR r0, [r6]
		B        |loc_08024512|
	INCBIN  baserom.gba_0x24556_0x2455e.extracted
