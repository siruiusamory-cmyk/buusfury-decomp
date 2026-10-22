	CODE16
|sub_08049DB0|
	LDRSB    r1, [r1, r7]
	LSL      r0, r0, #0
	STRH     r1, [r1, r6]
	LSL      r0, r0, #0
|unk_08049DB8|
	INCBIN	baserom.gba_0x49db8_0x49dba.extracted
	LSL      r0, r0, #0
	STR      r5, [r1, #0x10]
	LSL      r0, r0, #0
	LDRSB    r1, [r7, r6]
	LSL      r0, r0, #0
	STRH     r1, [r2, r6]
	LSL      r0, r0, #0
|unk_08049DC8|
	INCBIN	baserom.gba_0x49dc8_0x49dca.extracted
|sub_08049DCA|
|unk_08049DCA|
; cited by 0x08049A0C (a pc-relative load targets 0x08049DE4)
	INCBIN	baserom.gba_0x49dca_0x4a1fc.extracted
