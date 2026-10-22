	AREA Head, CODE, READONLY
	ENTRY
		B         	Init

		GLOBAL RomHeaderNintendoLogo
RomHeaderNintendoLogo
|unk_08000004|
; cited by 0x08000078 (a pc-relative load targets 0x08000080)
		INCBIN	baserom.gba_0x4_0xa0.extracted
		
		GLOBAL RomHeaderGameTitle
RomHeaderGameTitle
|unk_080000A0|
		INCBIN	baserom.gba_0xa0_0xac.extracted

		GLOBAL RomHeaderGameCode
RomHeaderGameCode
|unk_080000AC|
		INCBIN	baserom.gba_0xac_0xb0.extracted

		GLOBAL RomHeaderMakerCode
RomHeaderMakerCode
|unk_080000B0|
		INCBIN	baserom.gba_0xb0_0xb2.extracted

		GLOBAL RomHeaderMagic
RomHeaderMagic
|unk_080000B2|
		INCBIN	baserom.gba_0xb2_0xb3.extracted

		GLOBAL RomHeaderMainUnitCode
RomHeaderMainUnitCode
|unk_080000B3|
		INCBIN	baserom.gba_0xb3_0xb4.extracted
		
		GLOBAL RomHeaderDeviceType
RomHeaderDeviceType
|unk_080000B4|
		INCBIN	baserom.gba_0xb4_0xb5.extracted
		
		GLOBAL RomHeaderReserved1
RomHeaderReserved1
|unk_080000B5|
		INCLUDE fill_b5.s
		GLOBAL RomHeaderSoftwareVersion
RomHeaderSoftwareVersion
|unk_080000BC|
		INCBIN	baserom.gba_0xbc_0xbd.extracted
		
		GLOBAL RomHeaderChecksum
RomHeaderChecksum
|unk_080000BD|
		INCBIN	baserom.gba_0xbd_0xbe.extracted
		
		GLOBAL RomHeaderReserved2
RomHeaderReserved2
|unk_080000BE|
		INCBIN	baserom.gba_0xbe_0xc0.extracted

	END