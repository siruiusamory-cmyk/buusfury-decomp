|Irq_WriteMaster3|
	CODE16
|unk_08040F5E|
		LDRB r0, [r1, #9]
		CMP r0, #4
		BHS      |loc_08040F6A|
		ADD r0, #1
		STRB r0, [r1, #9]
		B        |loc_08040F5A|
|loc_08040F6A|
		LDR r1, [pc, #0x24]
		STRH r4, [r1, #8]
		LDR r2, [pc, #0x24]
		LDRH r0, [r2]
		ORR r0, r3
		STRH r0, [r2]
		MOV r0, #1
		STRH r0, [r1, #8]
		B        |loc_08040F5A|
	INCBIN  baserom.gba_0x40f7c_0x40f7e.extracted
