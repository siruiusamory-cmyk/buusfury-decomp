; PATH-100-012 / R-RAW-001: the census run 0x082b8c38..0x082b9bb0 as LABELED RAW DATA.
; citation channel: an explicit citation set (--citations), not the loader channel

	EXPORT	|unk_082B8C38|
|unk_082B8C38|
; cited by runtime read, session rt001, RUNTIME_CITED.csv sha256 CCF19E3469778F3DA12B68A94EC4BCB9F96A819BCE9A574C4A5892CA9E0FC6CF; this fragment is span 2 of 2 of row 0x002b8bc8..0x002b9bb0, which the merged master splits: the JCALG1 container PATH-100-011 carries as a generated section sits between its spans; every one of the row's 10 citations reads an address in another span: 08012850=082B9BAC, 0803F5C4=082B9BA0, 0803F5C8=082B8CC8, 0803F5F0=082B9BA0, 0803F5F4=082B8CC8, 0803F5FA=082B8E88, 0803F658=082B8E8A, 08040034=082B9BA0, 08040038=082B8C8C, 0804003C=082B8C88


	INCBIN	baserom.gba_0x2b8c38_0x2b9bb0.extracted
