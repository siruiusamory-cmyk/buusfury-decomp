; PATH-100-009 / R-RAW-001: the census run 0x08704f90..0x08704fb8 as LABELED RAW DATA.

	EXPORT	|unk_08704F90|
|unk_08704F90|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x704f90_0x704f94.extracted
	EXPORT	|unk_08704F94|
|unk_08704F94|
; cited by 0x08704DB0 ldrh r5 +0x4

	INCBIN	baserom.gba_0x704f94_0x704fa4.extracted
	EXPORT	|unk_08704FA4|
|unk_08704FA4|
; cited by 0x08704DB4


	INCBIN	baserom.gba_0x704fa4_0x704fb8.extracted
