	CODE16
|sub_0803B9BE|
|unk_0803B9BE|
		ADD r7, r2, #0
		LDR r3, [sp, #0x38]
		MOV r2, #1
		CMP r3, #0
		BLE      |loc_0803B9CA|
		MOV r2, #0
|loc_0803B9CA|
		STRB r2, [r4, #0x10]
