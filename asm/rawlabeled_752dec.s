; PATH-100-009 / R-RAW-001: the census run 0x08752dec..0x08752e18 as LABELED RAW DATA.

	EXPORT	|unk_08752DEC|
|unk_08752DEC|
; no citation: the run's first byte, a label boundary only

	DCD	|unk_03001C4C|
	DCD	|unk_03001068|
	DCD	|unk_03002BD8|
	EXPORT	|unk_08752DF8|
|unk_08752DF8|
; cited by 0x0802AF58 INDEXED base + register (r0, r0, r1), 0x0802AFAC, 0x0802B0D0


	INCBIN	baserom.gba_0x752df8_0x752e18.extracted
