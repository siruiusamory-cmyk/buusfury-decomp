; R-RAW-001: the census run 0x082b60a8..0x082b7e78 as LABELED RAW DATA.
; citation channel: an explicit citation set (--citations), not the loader channel

	EXPORT	|unk_082B60A8|
|unk_082B60A8|
; no citation: the run's first byte, a label boundary only
	INCBIN	build\animframe\gen_2b60a8_2b6854.bin

	EXPORT	|unk_082B6854|
|unk_082B6854|
; cited by pc 0x08009d04 read 0x082b6854 (width 4, frame 9560)
	INCBIN	build\animframe\gen_2b6854_2b7e58.bin

	EXPORT	|unk_082B7E58|
|unk_082B7E58|
; cited by pc 0x08009cf0 read 0x082b7e58 (width 1, frame 9560)
	INCBIN	baserom.gba_0x2b7e58_0x2b7e59.extracted

	EXPORT	|unk_082B7E59|
|unk_082B7E59|
; cited by pc 0x08009b32 read 0x082b7e59 (width 1, frame 9560)
	INCBIN	baserom.gba_0x2b7e59_0x2b7e5a.extracted

	EXPORT	|unk_082B7E5A|
|unk_082B7E5A|
; cited by pc 0x08009b34 read 0x082b7e5a (width 2, frame 9560), pc 0x08009bbc read 0x082b7e5a (width 2, frame 9557)
	INCBIN	baserom.gba_0x2b7e5a_0x2b7e5c.extracted

	EXPORT	|unk_082B7E5C|
|unk_082B7E5C|
; cited by pc 0x08009b26 read 0x082b7e5c (width 4, frame 9559)
	INCBIN	baserom.gba_0x2b7e5c_0x2b7e60.extracted

	EXPORT	|unk_082B7E60|
|unk_082B7E60|
; cited by pc 0x08009d02 read 0x082b7e60 (width 4, frame 9560)
	INCBIN	baserom.gba_0x2b7e60_0x2b7e74.extracted

	EXPORT	|unk_082B7E74|
|unk_082B7E74|
; cited by pc 0x08009bae read 0x082b7e74 (width 4, frame 9557)
	INCBIN	baserom.gba_0x2b7e74_0x2b7e78.extracted

