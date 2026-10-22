; PATH-100-012 / R-RAW-001: the census run 0x0828fbe4..0x0828fc00 as LABELED RAW DATA.
; citation channel: an explicit citation set (--citations), not the loader channel

	EXPORT	|unk_0828FBE4|
|unk_0828FBE4|
; cited by runtime read, session rt001, RUNTIME_CITED.csv sha256 CCF19E3469778F3DA12B68A94EC4BCB9F96A819BCE9A574C4A5892CA9E0FC6CF; (pc, first_address_read): 0800769A=0828FBF4, 08009AF8=0828FBF0, 08009AFA=0828FBEC, 08009B00=0828FBE8, 08012674=0828FBFC, 08012676=0828FBE4


	INCBIN	build\mapcontainer\map_0028FBE4_0028FBFC.bin
|unk_0828FBFC|
	INCBIN	build\mapcontainer\map_0028FBFC_0028FC00.bin
