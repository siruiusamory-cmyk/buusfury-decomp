	AREA Other, CODE, READONLY
	INCLUDE gba.inc
	INCLUDE ram.inc
unk_03000FB0    EQU     0x03000FB0
unk_03001068    EQU     0x03001068
unk_03001914    EQU     0x03001914
unk_0300197C    EQU     0x0300197C
unk_03001990    EQU     0x03001990
unk_030019A4    EQU     0x030019A4
unk_03001A68    EQU     0x03001A68
unk_03001C4C    EQU     0x03001C4C
unk_03002A60    EQU     0x03002A60
unk_03002A64    EQU     0x03002A64
unk_03002BAC    EQU     0x03002BAC
unk_03002BD4    EQU     0x03002BD4
unk_03002BD8    EQU     0x03002BD8
unk_03002C18    EQU     0x03002C18
unk_03002DAC    EQU     0x03002DAC
unk_03002F58    EQU     0x03002F58
unk_03003300    EQU     0x03003300
unk_03003898    EQU     0x03003898
unk_030038A4    EQU     0x030038A4
unk_03004A8C    EQU     0x03004A8C
        EXPORT  unk_03002A60
	INCLUDE sub_0806FE1A.s
	INCLUDE sub_080701EC.s
		INCBIN		build\asset_dialogbox.compressed
		INCBIN		build\asset_dialogbox_small.compressed
        CODE16
|inc_0x071c90_0x3715c0|
        EXPORT  |inc_0x071c90_0x3715c0|
        INCLUDE rawlabeled_71c90.s
        INCBIN  build\tilebank_0945c0.bin
        INCBIN  build\structured\gen_179764_179a50.bin
        INCBIN  build\mapcontainer\map_00179A50_00179C88.bin
        INCBIN  build\mapcontainer\map_00179C88_00179CB0.bin
        INCBIN  build\mapcontainer\map_00179CB0_00179E98.bin
        INCBIN  build\mapcontainer\map_00179E98_00179EC0.bin
        INCBIN  build\mapcontainer\map_00179EC0_0017A3AC.bin
        INCBIN  build\mapcontainer\map_0017A3AC_0017A3D4.bin
        INCBIN  build\mapcontainer\map_0017A3D4_0017A734.bin
        INCBIN  build\mapcontainer\map_0017A734_0017A75C.bin
        INCBIN  build\mapcontainer\map_0017A75C_0017A7C8.bin
|unk_0817A7C8|
        INCBIN  build\mapcontainer\map_0017A7C8_0017A7E0.bin
        INCBIN  build\mapcontainer\map_0017A7E0_0017A9AC.bin
        INCLUDE rawlabeled_17a9ac.s
        INCBIN  build\mapcontainer\map_0017B1B0_0017B200.bin
        INCBIN  build\mapcontainer\map_0017B200_0017B3A8.bin
        INCBIN  build\mapcontainer\map_0017B3A8_0017B3D0.bin
        INCBIN  build\mapcontainer\map_0017B3D0_0017B468.bin
        INCBIN  build\mapcontainer\map_0017B468_0017B484.bin
        INCBIN  build\mapcontainer\map_0017B484_0017B8D8.bin
        INCBIN  build\mapcontainer\map_0017B8D8_0017B900.bin
        INCBIN  build\mapcontainer\map_0017B900_0017BA00.bin
        INCBIN  build\mapcontainer\map_0017BA00_0017BA28.bin
        INCBIN  build\mapcontainer\map_0017BA28_0017BB28.bin
|unk_0817BB28|
        INCBIN  build\mapcontainer\map_0017BB28_0017BB40.bin
        INCBIN  build\mapcontainer\map_0017BB40_0017BCCC.bin
|unk_0817BCCC|
        INCBIN  build\animframe\gen_17bccc_17c0dc.bin
|unk_0817C0DC|
        INCBIN  build\mapcontainer\map_0017C0DC_0017C0F4.bin
        INCBIN  build\mapcontainer\map_0017C0F4_0017C144.bin
        INCBIN  build\mapcontainer\map_0017C144_0017C210.bin
        INCBIN  build\mapcontainer\map_0017C210_0017C22C.bin
        INCBIN  build\mapcontainer\map_0017C22C_0017C300.bin
        INCBIN  build\mapcontainer\map_0017C300_0017C31C.bin
        INCBIN  build\mapcontainer\map_0017C31C_0017C5EC.bin
        INCBIN  build\mapcontainer\map_0017C5EC_0017C608.bin
        INCBIN  build\mapcontainer\map_0017C608_0017C650.bin
        INCBIN  build\mapcontainer\map_0017C650_0017C66C.bin
        INCBIN  build\mapcontainer\map_0017C66C_0017C700.bin
|unk_0817C700|
        INCBIN  build\animframe\gen_17c700_17ca58.bin
|unk_0817CA58|
        INCBIN  build\mapcontainer\map_0017CA58_0017CAA0.bin
|unk_0817CAA0|
        INCBIN  build\mapcontainer\map_0017CAA0_0017CAA8.bin
        INCBIN  build\mapcontainer\map_0017CAA8_0017CAF8.bin
        INCBIN  build\mapcontainer\map_0017CAF8_0017CBAC.bin
        INCBIN  build\mapcontainer\map_0017CBAC_0017CBCC.bin
        INCBIN  build\mapcontainer\map_0017CBCC_0017CDF8.bin
        INCBIN  build\mapcontainer\map_0017CDF8_0017CE18.bin
        INCBIN  build\mapcontainer\map_0017CE18_0017CE9C.bin
        INCBIN  build\mapcontainer\map_0017CE9C_0017CEBC.bin
        INCBIN  build\mapcontainer\map_0017CEBC_0017CF5C.bin
|unk_0817CF5C|
        INCBIN  build\mapcontainer\map_0017CF5C_0017CF8C.bin
        INCBIN  build\mapcontainer\map_0017CF8C_0017D1C8.bin
|unk_0817D1C8|
        INCBIN  build\animframe\gen_17d1c8_17d340.bin
|unk_0817D340|
        INCBIN  build\mapcontainer\map_0017D340_0017D388.bin
|unk_0817D388|
        INCBIN  build\mapcontainer\map_0017D388_0017D390.bin
        INCBIN  build\mapcontainer\map_0017D390_0017D3E0.bin
        INCBIN  build\mapcontainer\map_0017D3E0_0017D510.bin
        INCBIN  build\mapcontainer\map_0017D510_0017D530.bin
        INCBIN  build\mapcontainer\map_0017D530_0017D574.bin
        INCBIN  build\mapcontainer\map_0017D574_0017D594.bin
        INCBIN  build\mapcontainer\map_0017D594_0017D900.bin
        INCBIN  build\mapcontainer\map_0017D900_0017D920.bin
        INCBIN  build\mapcontainer\map_0017D920_0017D9A4.bin
        INCBIN  build\mapcontainer\map_0017D9A4_0017D9C4.bin
        INCBIN  build\mapcontainer\map_0017D9C4_0017DAB0.bin
|unk_0817DAB0|
        INCBIN  build\animframe\gen_17dab0_17de24.bin
|unk_0817DE24|
        INCBIN  build\mapcontainer\map_0017DE24_0017DE6C.bin
|unk_0817DE6C|
        INCBIN  build\mapcontainer\map_0017DE6C_0017DE74.bin
        INCBIN  build\mapcontainer\map_0017DE74_0017DEC4.bin
        INCBIN  build\mapcontainer\map_0017DEC4_0017DEE4.bin
        INCBIN  build\mapcontainer\map_0017DEE4_0017E10C.bin
        INCBIN  build\mapcontainer\map_0017E10C_0017E12C.bin
        INCBIN  build\mapcontainer\map_0017E12C_0017E1B0.bin
        INCBIN  build\mapcontainer\map_0017E1B0_0017E1D0.bin
        INCBIN  build\mapcontainer\map_0017E1D0_0017E20C.bin
|unk_0817E20C|
        INCBIN  build\mapcontainer\map_0017E20C_0017E23C.bin
        INCBIN  build\mapcontainer\map_0017E23C_0017E44C.bin
|unk_0817E44C|
        INCBIN  build\animframe\gen_17e44c_17e5bc.bin
|unk_0817E5BC|
        INCBIN  build\mapcontainer\map_0017E5BC_0017E604.bin
|unk_0817E604|
        INCBIN  build\mapcontainer\map_0017E604_0017E60C.bin
        INCBIN  build\mapcontainer\map_0017E60C_0017E65C.bin
        INCBIN  build\mapcontainer\map_0017E65C_0017E790.bin
        INCBIN  build\mapcontainer\map_0017E790_0017E7B0.bin
        INCBIN  build\mapcontainer\map_0017E7B0_0017E7F8.bin
        INCBIN  build\mapcontainer\map_0017E7F8_0017E818.bin
        INCBIN  build\mapcontainer\map_0017E818_0017EBA0.bin
        INCBIN  build\mapcontainer\map_0017EBA0_0017EBE0.bin
        INCBIN  build\mapcontainer\map_0017EBE0_0017ECD4.bin
|unk_0817ECD4|
        INCBIN  build\mapcontainer\map_0017ECD4_0017ED1C.bin
|unk_0817ED1C|
        INCBIN  build\mapcontainer\map_0017ED1C_0017ED24.bin
        INCBIN  build\mapcontainer\map_0017ED24_0017ED74.bin
        INCBIN  build\mapcontainer\map_0017ED74_0017ED94.bin
        INCBIN  build\mapcontainer\map_0017ED94_0017EFC0.bin
        INCBIN  build\mapcontainer\map_0017EFC0_0017F000.bin
        INCBIN  build\mapcontainer\map_0017F000_0017F034.bin
|unk_0817F034|
        INCBIN  build\mapcontainer\map_0017F034_0017F094.bin
        INCBIN  build\mapcontainer\map_0017F094_0017F330.bin
|unk_0817F330|
        INCBIN  build\animframe\gen_17f330_17f48c.bin
|unk_0817F48C|
        INCBIN  build\mapcontainer\map_0017F48C_0017F4D4.bin
|unk_0817F4D4|
        INCBIN  build\mapcontainer\map_0017F4D4_0017F4DC.bin
        INCBIN  build\mapcontainer\map_0017F4DC_0017F52C.bin
        INCBIN  build\mapcontainer\map_0017F52C_0017F70C.bin
        INCBIN  build\mapcontainer\map_0017F70C_0017F74C.bin
        INCBIN  build\mapcontainer\map_0017F74C_0017FA28.bin
        INCBIN  build\mapcontainer\map_0017FA28_0017FA68.bin
        INCBIN  build\mapcontainer\map_0017FA68_0017FB64.bin
|unk_0817FB64|
        INCBIN  build\mapcontainer\map_0017FB64_0017FBAC.bin
|unk_0817FBAC|
        INCBIN  build\mapcontainer\map_0017FBAC_0017FBB4.bin
        INCBIN  build\mapcontainer\map_0017FBB4_0017FC04.bin
        INCBIN  build\mapcontainer\map_0017FC04_0017FD0C.bin
        INCBIN  build\mapcontainer\map_0017FD0C_0017FD2C.bin
        INCBIN  build\mapcontainer\map_0017FD2C_001803C0.bin
        INCBIN  build\mapcontainer\map_001803C0_001803E0.bin
        INCBIN  build\mapcontainer\map_001803E0_001805EC.bin
        INCBIN  build\mapcontainer\map_001805EC_0018060C.bin
        INCBIN  build\mapcontainer\map_0018060C_00180694.bin
|unk_08180694|
        INCBIN  build\animframe\gen_180694_180b40.bin
|unk_08180B40|
        INCBIN  build\mapcontainer\map_00180B40_00180B88.bin
|unk_08180B88|
        INCBIN  build\mapcontainer\map_00180B88_00180B90.bin
        INCBIN  build\mapcontainer\map_00180B90_00180BE0.bin
        INCBIN  build\mapcontainer\map_00180BE0_00180C00.bin
        INCBIN  build\mapcontainer\map_00180C00_001812A4.bin
        INCBIN  build\mapcontainer\map_001812A4_001812E4.bin
        INCBIN  build\mapcontainer\map_001812E4_00181348.bin
|unk_08181348|
        INCBIN  build\mapcontainer\map_00181348_00181390.bin
|unk_08181390|
        INCBIN  build\mapcontainer\map_00181390_00181398.bin
        INCBIN  build\mapcontainer\map_00181398_001813E8.bin
        INCBIN  build\mapcontainer\map_001813E8_00181448.bin
|unk_08181448|
        INCBIN  build\mapcontainer\map_00181448_00181490.bin
|unk_08181490|
        INCBIN  build\mapcontainer\map_00181490_00181498.bin
        INCBIN  build\mapcontainer\map_00181498_001814E8.bin
        INCBIN  build\mapcontainer\map_001814E8_00181548.bin
|unk_08181548|
        INCBIN  build\mapcontainer\map_00181548_00181590.bin
|unk_08181590|
        INCBIN  build\mapcontainer\map_00181590_00181598.bin
        INCBIN  build\mapcontainer\map_00181598_001815E8.bin
        INCBIN  build\mapcontainer\map_001815E8_001817F0.bin
        INCBIN  build\mapcontainer\map_001817F0_00181810.bin
        INCBIN  build\mapcontainer\map_00181810_001818B8.bin
        INCBIN  build\mapcontainer\map_001818B8_001818D4.bin
        INCBIN  build\mapcontainer\map_001818D4_00181C94.bin
        INCBIN  build\mapcontainer\map_00181C94_00181CB4.bin
        INCBIN  build\mapcontainer\map_00181CB4_00181F34.bin
        INCBIN  build\mapcontainer\map_00181F34_00181F54.bin
        INCBIN  build\mapcontainer\map_00181F54_00182054.bin
|unk_08182054|
        INCBIN  build\mapcontainer\map_00182054_0018206C.bin
|unk_0818206C|
        INCBIN  build\animframe\gen_18206c_1823f8.bin
|unk_081823F8|
        INCBIN  build\mapcontainer\map_001823F8_0018243C.bin
|unk_0818243C|
        INCBIN  build\mapcontainer\map_0018243C_00182444.bin
        INCBIN  build\mapcontainer\map_00182444_00182494.bin
        INCBIN  build\mapcontainer\map_00182494_001825AC.bin
        INCBIN  build\mapcontainer\map_001825AC_001825D4.bin
        INCBIN  build\mapcontainer\map_001825D4_001825FC.bin
        INCBIN  build\mapcontainer\map_001825FC_00182618.bin
        INCBIN  build\mapcontainer\map_00182618_001829D8.bin
        INCBIN  build\mapcontainer\map_001829D8_00182A00.bin
        INCBIN  build\mapcontainer\map_00182A00_00182C9C.bin
        INCBIN  build\mapcontainer\map_00182C9C_00182CC4.bin
        INCBIN  build\mapcontainer\map_00182CC4_00182DCC.bin
|unk_08182DCC|
        INCBIN  build\animframe\gen_182dcc_183090.bin
|unk_08183090|
        INCBIN  build\mapcontainer\map_00183090_001830D8.bin
|unk_081830D8|
        INCBIN  build\mapcontainer\map_001830D8_001830E0.bin
        INCBIN  build\mapcontainer\map_001830E0_00183130.bin
        INCBIN  build\mapcontainer\map_00183130_001831D8.bin
        INCBIN  build\mapcontainer\map_001831D8_001831F8.bin
        INCBIN  build\mapcontainer\map_001831F8_001834F0.bin
        INCBIN  build\mapcontainer\map_001834F0_00183510.bin
        INCBIN  build\mapcontainer\map_00183510_0018360C.bin
        INCBIN  build\mapcontainer\map_0018360C_0018362C.bin
        INCBIN  build\mapcontainer\map_0018362C_00183770.bin
        INCBIN  build\mapcontainer\map_00183770_00183790.bin
        INCBIN  build\mapcontainer\map_00183790_001837DC.bin
|unk_081837DC|
        INCBIN  build\animframe\gen_1837dc_183db4.bin
|unk_08183DB4|
        INCBIN  build\mapcontainer\map_00183DB4_00183DF4.bin
|unk_08183DF4|
        INCBIN  build\mapcontainer\map_00183DF4_00183DFC.bin
        INCBIN  build\mapcontainer\map_00183DFC_00183E4C.bin
        INCBIN  build\mapcontainer\map_00183E4C_00183F14.bin
        INCBIN  build\mapcontainer\map_00183F14_00183F3C.bin
        INCBIN  build\mapcontainer\map_00183F3C_00183F60.bin
        INCBIN  build\mapcontainer\map_00183F60_00183F80.bin
        INCBIN  build\mapcontainer\map_00183F80_0018438C.bin
        INCBIN  build\mapcontainer\map_0018438C_001843B4.bin
        INCBIN  build\mapcontainer\map_001843B4_001846C0.bin
        INCBIN  build\mapcontainer\map_001846C0_001846E8.bin
        INCBIN  build\mapcontainer\map_001846E8_001847B0.bin
|unk_081847B0|
        INCBIN  build\mapcontainer\map_001847B0_001847F8.bin
        INCBIN  build\jcalg1\gen_1847f8.bin
|unk_08184B58|
        INCBIN  build\mapcontainer\map_00184B58_00184B88.bin
|unk_08184B88|
        INCBIN  build\mapcontainer\map_00184B88_00184B8C.bin
        INCBIN  build\mapcontainer\map_00184B8C_00184BDC.bin
        INCBIN  build\mapcontainer\map_00184BDC_00184D60.bin
        INCBIN  build\mapcontainer\map_00184D60_00184D88.bin
        INCBIN  build\mapcontainer\map_00184D88_00184E24.bin
        INCBIN  build\mapcontainer\map_00184E24_00184E4C.bin
        INCBIN  build\mapcontainer\map_00184E4C_00185458.bin
        INCBIN  build\mapcontainer\map_00185458_00185480.bin
        INCBIN  build\mapcontainer\map_00185480_001859B0.bin
        INCBIN  build\mapcontainer\map_001859B0_001859D8.bin
        INCBIN  build\mapcontainer\map_001859D8_00185AF8.bin
|unk_08185AF8|
        INCBIN  build\animframe\gen_185af8_185d40.bin
|map_anim_row_08185D40|
|unk_08185D40|
	DCB 0x04,0x0e
	DCW 0x0372
	DCD 0x08185af8,0x08185bc0,0x08185c80,0x08185bc0
|unk_08185D54|
        INCBIN  build\animframe\gen_185d54_18611c.bin
|map_anim_row_0818611C|
|unk_0818611C|
	DCB 0x04,0x16
	DCW 0x035c
	DCD 0x08185d54,0x08185e80,0x08185fc4,0x08185e80
|unk_08186130|
        INCBIN  build\animframe\gen_186130_186378.bin
|map_anim_row_08186378|
|unk_08186378|
	DCB 0x04,0x07
	DCW 0x0355
	DCD 0x08186130,0x081861c0,0x08186250,0x081862e4
|unk_0818638C|
        INCBIN  build\animframe\gen_18638c_1866bc.bin
|map_anim_row_081866BC|
|unk_081866BC|
	DCB 0x04,0x06
	DCW 0x034f
	DCD 0x0818638c,0x08186458,0x08186520,0x081865f0
|unk_081866D0|
        INCBIN  build\animframe\gen_1866d0_1872f0.bin
|map_anim_row_081872F0|
|unk_081872F0|
	DCB 0x09,0x22
	DCW 0x032d
	DCD 0x081866d0,0x08186834,0x08186998,0x08186af4,0x08186c4c,0x08186d9c,0x08186eec,0x08187034
	DCD 0x0818718c
|unk_08187318|
        INCBIN  baserom.gba_0x187318_0x18732c.extracted
|unk_0818732C|
        INCBIN  build\mapcontainer\map_0018732C_0018735C.bin
|unk_0818735C|
        INCBIN  build\mapcontainer\map_0018735C_00187364.bin
        INCBIN  build\mapcontainer\map_00187364_001873B4.bin
        INCBIN  build\mapcontainer\map_001873B4_00187498.bin
        INCBIN  build\mapcontainer\map_00187498_001874B8.bin
        INCBIN  build\mapcontainer\map_001874B8_00187898.bin
        INCBIN  build\mapcontainer\map_00187898_001878B8.bin
        INCBIN  build\mapcontainer\map_001878B8_00187AA8.bin
        INCBIN  build\mapcontainer\map_00187AA8_00187AC8.bin
        INCBIN  build\mapcontainer\map_00187AC8_00187BC8.bin
        INCLUDE rawlabeled_187bc8.s
        INCBIN  build\mapcontainer\map_00187C14_00187C64.bin
        INCBIN  build\mapcontainer\map_00187C64_00187E18.bin
        INCBIN  build\mapcontainer\map_00187E18_00187E3C.bin
        INCBIN  build\mapcontainer\map_00187E3C_00187ED4.bin
        INCBIN  build\mapcontainer\map_00187ED4_00187EF0.bin
        INCBIN  build\mapcontainer\map_00187EF0_0018829C.bin
        INCBIN  build\mapcontainer\map_0018829C_001882C0.bin
        INCBIN  build\mapcontainer\map_001882C0_00188578.bin
        INCBIN  build\mapcontainer\map_00188578_0018859C.bin
        INCBIN  build\mapcontainer\map_0018859C_001886AC.bin
|unk_081886AC|
        INCBIN  build\animframe\gen_1886ac_188a20.bin
|unk_08188A20|
        INCBIN  build\mapcontainer\map_00188A20_00188A80.bin
|unk_08188A80|
        INCBIN  build\mapcontainer\map_00188A80_00188A8C.bin
        INCBIN  build\mapcontainer\map_00188A8C_00188ADC.bin
        INCBIN  build\mapcontainer\map_00188ADC_00188BC0.bin
        INCBIN  build\mapcontainer\map_00188BC0_00188BE0.bin
        INCBIN  build\mapcontainer\map_00188BE0_00189000.bin
        INCBIN  build\mapcontainer\map_00189000_00189020.bin
        INCBIN  build\mapcontainer\map_00189020_00189208.bin
        INCBIN  build\mapcontainer\map_00189208_00189228.bin
        INCBIN  build\mapcontainer\map_00189228_00189334.bin
        INCLUDE rawlabeled_189334.s
        INCBIN  build\mapcontainer\map_00189380_001893D0.bin
        INCBIN  build\mapcontainer\map_001893D0_00189484.bin
        INCBIN  build\mapcontainer\map_00189484_001894A4.bin
        INCBIN  build\mapcontainer\map_001894A4_001894BC.bin
        INCBIN  build\mapcontainer\map_001894BC_001894D8.bin
        INCBIN  build\mapcontainer\map_001894D8_001898B4.bin
        INCBIN  build\mapcontainer\map_001898B4_001898D4.bin
        INCBIN  build\mapcontainer\map_001898D4_00189B58.bin
        INCBIN  build\mapcontainer\map_00189B58_00189B78.bin
        INCBIN  build\mapcontainer\map_00189B78_00189C1C.bin
|unk_08189C1C|
        INCBIN  build\mapcontainer\map_00189C1C_00189C34.bin
|unk_08189C34|
        INCBIN  build\animframe\gen_189c34_189f7c.bin
|unk_08189F7C|
        INCBIN  build\mapcontainer\map_00189F7C_00189FA8.bin
|unk_08189FA8|
        INCBIN  build\mapcontainer\map_00189FA8_00189FAC.bin
        INCBIN  build\mapcontainer\map_00189FAC_00189FFC.bin
        INCBIN  build\mapcontainer\map_00189FFC_0018A07C.bin
|unk_0818A07C|
        INCBIN  build\mapcontainer\map_0018A07C_0018A0BC.bin
|unk_0818A0BC|
        INCBIN  build\mapcontainer\map_0018A0BC_0018A0C4.bin
        INCBIN  build\mapcontainer\map_0018A0C4_0018A114.bin
        INCBIN  build\mapcontainer\map_0018A114_0018A298.bin
        INCBIN  build\mapcontainer\map_0018A298_0018A2C0.bin
        INCBIN  build\mapcontainer\map_0018A2C0_0018A3C8.bin
        INCBIN  build\mapcontainer\map_0018A3C8_0018A3F0.bin
        INCBIN  build\mapcontainer\map_0018A3F0_0018AB04.bin
        INCBIN  build\mapcontainer\map_0018AB04_0018AB2C.bin
        INCBIN  build\mapcontainer\map_0018AB2C_0018B184.bin
        INCBIN  build\mapcontainer\map_0018B184_0018B1AC.bin
        INCBIN  build\mapcontainer\map_0018B1AC_0018B31C.bin
|unk_0818B31C|
        INCBIN  build\mapcontainer\map_0018B31C_0018B334.bin
|unk_0818B334|
        INCBIN  build\animframe\gen_18b334_18b6c0.bin
|map_anim_row_0818B6C0|
|unk_0818B6C0|
	DCB 0x04,0x10
	DCW 0x0370
	DCD 0x0818b334,0x0818b418,0x0818b4f4,0x0818b5e4
|map_anim_row_0818B6D4|
|unk_0818B6D4|
	DCB 0x09,0x22
	DCW 0x034e
	DCD 0x081866d0,0x08186834,0x08186998,0x08186af4,0x08186c4c,0x08186d9c,0x08186eec,0x08187034
	DCD 0x0818718c
|map_anim_row_0818B6FC|
|unk_0818B6FC|
	DCB 0x04,0x06
	DCW 0x0348
	DCD 0x0818638c,0x08186458,0x08186520,0x081865f0
|unk_0818B710|
        INCBIN  build\animframe\gen_18b710_18ba3c.bin
|map_anim_row_0818BA3C|
|unk_0818BA3C|
	DCB 0x03,0x13
	DCW 0x0335
	DCD 0x0818b710,0x0818b810,0x0818b91c
|map_anim_row_0818BA4C|
|unk_0818BA4C|
	DCB 0x04,0x07
	DCW 0x032e
	DCD 0x08186130,0x081861c0,0x08186250,0x081862e4
|unk_0818BA60|
        INCBIN  baserom.gba_0x18ba60_0x18ba74.extracted
|unk_0818BA74|
        INCBIN  build\mapcontainer\map_0018BA74_0018BAD4.bin
|unk_0818BAD4|
        INCBIN  build\mapcontainer\map_0018BAD4_0018BAE4.bin
        INCBIN  build\mapcontainer\map_0018BAE4_0018BB34.bin
        INCBIN  build\mapcontainer\map_0018BB34_0018BBD0.bin
        INCBIN  build\mapcontainer\map_0018BBD0_0018BBF0.bin
        INCBIN  build\mapcontainer\map_0018BBF0_0018BC8C.bin
        INCBIN  build\mapcontainer\map_0018BC8C_0018BCAC.bin
        INCBIN  build\mapcontainer\map_0018BCAC_0018C0E4.bin
        INCBIN  build\mapcontainer\map_0018C0E4_0018C10C.bin
        INCBIN  build\mapcontainer\map_0018C10C_0018C500.bin
        INCBIN  build\mapcontainer\map_0018C500_0018C528.bin
        INCBIN  build\mapcontainer\map_0018C528_0018C638.bin
|unk_0818C638|
        INCBIN  build\animframe\gen_18c638_18ca38.bin
|map_anim_row_0818CA38|
|unk_0818CA38|
	DCB 0x03,0x17
	DCW 0x0369
	DCD 0x0818c638,0x0818c774,0x0818c8cc
|map_anim_row_0818CA48|
|unk_0818CA48|
	DCB 0x09,0x22
	DCW 0x0347
	DCD 0x081866d0,0x08186834,0x08186998,0x08186af4,0x08186c4c,0x08186d9c,0x08186eec,0x08187034
	DCD 0x0818718c
|unk_0818CA70|
        INCBIN  build\animframe\gen_18ca70_18cc8c.bin
|map_anim_row_0818CC8C|
|unk_0818CC8C|
	DCB 0x04,0x08
	DCW 0x033f
	DCD 0x0818ca70,0x0818cae0,0x0818cb6c,0x0818cc00
|unk_0818CCA0|
        INCBIN  baserom.gba_0x18cca0_0x18ccac.extracted
|unk_0818CCAC|
        INCBIN  build\mapcontainer\map_0018CCAC_0018CD0C.bin
|unk_0818CD0C|
        INCBIN  build\mapcontainer\map_0018CD0C_0018CD1C.bin
        INCBIN  build\mapcontainer\map_0018CD1C_0018CD6C.bin
        INCBIN  build\mapcontainer\map_0018CD6C_0018CE08.bin
        INCBIN  build\mapcontainer\map_0018CE08_0018CE28.bin
        INCBIN  build\mapcontainer\map_0018CE28_0018CED4.bin
        INCBIN  build\mapcontainer\map_0018CED4_0018CEF4.bin
        INCBIN  build\mapcontainer\map_0018CEF4_0018D440.bin
        INCBIN  build\mapcontainer\map_0018D440_0018D468.bin
        INCBIN  build\mapcontainer\map_0018D468_0018D6AC.bin
        INCBIN  build\mapcontainer\map_0018D6AC_0018D6D4.bin
        INCBIN  build\mapcontainer\map_0018D6D4_0018D808.bin
|unk_0818D808|
        INCBIN  build\animframe\gen_18d808_18dbac.bin
|map_anim_row_0818DBAC|
|unk_0818DBAC|
	DCB 0x03,0x15
	DCW 0x036b
	DCD 0x0818d808,0x0818d924,0x0818da5c
|map_anim_row_0818DBBC|
|unk_0818DBBC|
	DCB 0x09,0x22
	DCW 0x0349
	DCD 0x081866d0,0x08186834,0x08186998,0x08186af4,0x08186c4c,0x08186d9c,0x08186eec,0x08187034
	DCD 0x0818718c
|unk_0818DBE4|
        INCBIN  build\animframe\gen_18dbe4_18ddf4.bin
|map_anim_row_0818DDF4|
|unk_0818DDF4|
	DCB 0x04,0x08
	DCW 0x0341
	DCD 0x0818dbe4,0x0818dc58,0x0818dcdc,0x0818dd70
|unk_0818DE08|
        INCBIN  baserom.gba_0x18de08_0x18de14.extracted
|unk_0818DE14|
        INCBIN  build\mapcontainer\map_0018DE14_0018DE74.bin
|unk_0818DE74|
        INCBIN  build\mapcontainer\map_0018DE74_0018DE84.bin
        INCBIN  build\mapcontainer\map_0018DE84_0018DED4.bin
        INCBIN  build\mapcontainer\map_0018DED4_0018E4A8.bin
        INCBIN  build\mapcontainer\map_0018E4A8_0018E4E4.bin
        INCBIN  build\mapcontainer\map_0018E4E4_0018E718.bin
        INCBIN  build\mapcontainer\map_0018E718_0018E748.bin
        INCBIN  build\mapcontainer\map_0018E748_0018F274.bin
        INCBIN  build\mapcontainer\map_0018F274_0018F2BC.bin
        INCBIN  build\mapcontainer\map_0018F2BC_0018FDE4.bin
        INCBIN  build\mapcontainer\map_0018FDE4_0018FE2C.bin
        INCBIN  build\mapcontainer\map_0018FE2C_00190088.bin
        INCLUDE rawlabeled_190088.s
        INCBIN  build\mapcontainer\map_001900D0_00190240.bin
|map_anim_row_08190240|
|unk_08190240|
	DCB 0x09,0x22
	DCW 0x035e
	DCD 0x081866d0,0x08186834,0x08186998,0x08186af4,0x08186c4c,0x08186d9c,0x08186eec,0x08187034
	DCD 0x0818718c
|map_anim_row_08190268|
|unk_08190268|
	DCB 0x03,0x1d
	DCW 0x0341
	DCD 0x08180694,0x0818080c,0x08180998
|unk_08190278|
        INCBIN  build\animframe\gen_190278_190630.bin
|map_anim_row_08190630|
|unk_08190630|
	DCB 0x04,0x11
	DCW 0x0330
	DCD 0x08190278,0x08190360,0x0819044c,0x08190544
|unk_08190644|
        INCBIN  baserom.gba_0x190644_0x190650.extracted
|unk_08190650|
        INCBIN  build\mapcontainer\map_00190650_00190680.bin
|unk_08190680|
        INCBIN  build\mapcontainer\map_00190680_00190688.bin
        INCBIN  build\mapcontainer\map_00190688_001906D8.bin
        INCBIN  build\mapcontainer\map_001906D8_0019076C.bin
        INCBIN  build\mapcontainer\map_0019076C_00190788.bin
        INCBIN  build\mapcontainer\map_00190788_001908B0.bin
        INCBIN  build\mapcontainer\map_001908B0_001908CC.bin
        INCBIN  build\mapcontainer\map_001908CC_00190A90.bin
        INCBIN  build\mapcontainer\map_00190A90_00190AAC.bin
        INCBIN  build\mapcontainer\map_00190AAC_00190C70.bin
        INCBIN  build\mapcontainer\map_00190C70_00190C8C.bin
        INCBIN  build\mapcontainer\map_00190C8C_00190D24.bin
        INCBIN  build\mapcontainer\map_00190D24_00190D74.bin
        INCBIN  build\mapcontainer\map_00190D74_00190DF4.bin
        INCBIN  build\mapcontainer\map_00190DF4_00190E10.bin
        INCBIN  build\mapcontainer\map_00190E10_00190FD0.bin
        INCBIN  build\mapcontainer\map_00190FD0_00190FEC.bin
        INCBIN  build\mapcontainer\map_00190FEC_001910F0.bin
        INCBIN  build\mapcontainer\map_001910F0_0019110C.bin
        INCBIN  build\mapcontainer\map_0019110C_001911D8.bin
        INCLUDE rawlabeled_1911d8.s
        INCBIN  build\mapcontainer\map_001912E4_00191334.bin
        INCBIN  build\mapcontainer\map_00191334_00191C34.bin
        INCBIN  build\mapcontainer\map_00191C34_00191C5C.bin
        INCBIN  build\mapcontainer\map_00191C5C_001921C4.bin
        INCBIN  build\mapcontainer\map_001921C4_001921EC.bin
        INCBIN  build\mapcontainer\map_001921EC_00192364.bin
|unk_08192364|
        INCBIN  build\mapcontainer\map_00192364_0019239C.bin
|unk_0819239C|
        INCBIN  build\mapcontainer\map_0019239C_001923A0.bin
        INCBIN  build\mapcontainer\map_001923A0_001923F0.bin
        INCBIN  build\mapcontainer\map_001923F0_0019261C.bin
        INCBIN  build\mapcontainer\map_0019261C_00192644.bin
        INCBIN  build\mapcontainer\map_00192644_00192AD0.bin
        INCBIN  build\mapcontainer\map_00192AD0_00192AF8.bin
        INCBIN  build\mapcontainer\map_00192AF8_00193180.bin
        INCBIN  build\mapcontainer\map_00193180_001931A8.bin
        INCBIN  build\mapcontainer\map_001931A8_001937AC.bin
        INCBIN  build\mapcontainer\map_001937AC_001937D4.bin
        INCBIN  build\mapcontainer\map_001937D4_00193A10.bin
|unk_08193A10|
        INCBIN  build\mapcontainer\map_00193A10_00193A28.bin
|unk_08193A28|
        INCBIN  build\mapcontainer\map_00193A28_00193A2C.bin
        INCBIN  build\mapcontainer\map_00193A2C_00193A7C.bin
        INCBIN  build\mapcontainer\map_00193A7C_00193BE0.bin
        INCBIN  build\mapcontainer\map_00193BE0_00193C00.bin
        INCBIN  build\mapcontainer\map_00193C00_00193CF8.bin
        INCBIN  build\mapcontainer\map_00193CF8_00193D18.bin
        INCBIN  build\mapcontainer\map_00193D18_001941DC.bin
        INCBIN  build\mapcontainer\map_001941DC_001941FC.bin
        INCBIN  build\mapcontainer\map_001941FC_0019448C.bin
        INCBIN  build\mapcontainer\map_0019448C_001944AC.bin
        INCBIN  build\mapcontainer\map_001944AC_001945EC.bin
|unk_081945EC|
        INCBIN  build\mapcontainer\map_001945EC_00194604.bin
        INCBIN  build\mapcontainer\map_00194604_0019470C.bin
|unk_0819470C|
        INCBIN  build\mapcontainer\map_0019470C_0019473C.bin
|unk_0819473C|
        INCBIN  build\mapcontainer\map_0019473C_00194744.bin
        INCBIN  build\mapcontainer\map_00194744_00194794.bin
        INCBIN  build\mapcontainer\map_00194794_00194A24.bin
        INCBIN  build\mapcontainer\map_00194A24_00194A4C.bin
        INCBIN  build\mapcontainer\map_00194A4C_00194B5C.bin
        INCBIN  build\mapcontainer\map_00194B5C_00194B84.bin
        INCBIN  build\mapcontainer\map_00194B84_001953C4.bin
        INCBIN  build\mapcontainer\map_001953C4_001953EC.bin
        INCBIN  build\mapcontainer\map_001953EC_00195A04.bin
        INCBIN  build\mapcontainer\map_00195A04_00195A2C.bin
        INCBIN  build\mapcontainer\map_00195A2C_00195C3C.bin
|unk_08195C3C|
        INCBIN  build\mapcontainer\map_00195C3C_00195C54.bin
        INCBIN  build\jcalg1\gen_195c54.bin
|unk_08195CBC|
        INCBIN  build\mapcontainer\map_00195CBC_00195CEC.bin
|unk_08195CEC|
        INCBIN  build\mapcontainer\map_00195CEC_00195CF4.bin
        INCBIN  build\mapcontainer\map_00195CF4_00195D44.bin
        INCBIN  build\mapcontainer\map_00195D44_00195FAC.bin
        INCBIN  build\mapcontainer\map_00195FAC_00195FD4.bin
        INCBIN  build\mapcontainer\map_00195FD4_00196124.bin
        INCBIN  build\mapcontainer\map_00196124_0019614C.bin
        INCBIN  build\mapcontainer\map_0019614C_00196808.bin
        INCBIN  build\mapcontainer\map_00196808_00196830.bin
        INCBIN  build\mapcontainer\map_00196830_00196DE4.bin
        INCBIN  build\mapcontainer\map_00196DE4_00196E0C.bin
        INCBIN  build\mapcontainer\map_00196E0C_00196FA8.bin
|unk_08196FA8|
        INCBIN  build\mapcontainer\map_00196FA8_00196FF0.bin
        INCBIN  build\mapcontainer\map_00196FF0_001971D0.bin
|unk_081971D0|
        INCBIN  build\mapcontainer\map_001971D0_00197200.bin
|unk_08197200|
        INCBIN  build\mapcontainer\map_00197200_00197208.bin
        INCBIN  build\mapcontainer\map_00197208_00197258.bin
        INCBIN  build\mapcontainer\map_00197258_00197388.bin
        INCBIN  build\mapcontainer\map_00197388_001973AC.bin
        INCBIN  build\mapcontainer\map_001973AC_00197494.bin
        INCBIN  build\mapcontainer\map_00197494_001974B8.bin
        INCBIN  build\mapcontainer\map_001974B8_00197B04.bin
        INCBIN  build\mapcontainer\map_00197B04_00197B28.bin
        INCBIN  build\mapcontainer\map_00197B28_00197EBC.bin
        INCBIN  build\mapcontainer\map_00197EBC_00197EE4.bin
        INCBIN  build\mapcontainer\map_00197EE4_0019807C.bin
|unk_0819807C|
        INCBIN  build\mapcontainer\map_0019807C_001980AC.bin
|unk_081980AC|
        INCBIN  build\mapcontainer\map_001980AC_001980B4.bin
        INCBIN  build\mapcontainer\map_001980B4_00198104.bin
        INCBIN  build\mapcontainer\map_00198104_0019830C.bin
        INCBIN  build\mapcontainer\map_0019830C_00198334.bin
        INCBIN  build\mapcontainer\map_00198334_00198418.bin
        INCBIN  build\mapcontainer\map_00198418_00198440.bin
        INCBIN  build\mapcontainer\map_00198440_00198904.bin
        INCBIN  build\mapcontainer\map_00198904_0019892C.bin
        INCBIN  build\mapcontainer\map_0019892C_00198D5C.bin
        INCBIN  build\mapcontainer\map_00198D5C_00198D84.bin
        INCBIN  build\mapcontainer\map_00198D84_00198EF0.bin
|unk_08198EF0|
        INCBIN  build\mapcontainer\map_00198EF0_00198F20.bin
|unk_08198F20|
        INCBIN  build\mapcontainer\map_00198F20_00198F28.bin
        INCBIN  build\mapcontainer\map_00198F28_00198F78.bin
        INCBIN  build\mapcontainer\map_00198F78_00199124.bin
        INCBIN  build\mapcontainer\map_00199124_0019914C.bin
        INCBIN  build\mapcontainer\map_0019914C_00199664.bin
        INCBIN  build\mapcontainer\map_00199664_0019968C.bin
        INCBIN  build\mapcontainer\map_0019968C_001999C0.bin
        INCBIN  build\mapcontainer\map_001999C0_001999E8.bin
        INCBIN  build\mapcontainer\map_001999E8_00199B54.bin
|unk_08199B54|
        INCBIN  build\mapcontainer\map_00199B54_00199B6C.bin
        INCBIN  build\mapcontainer\map_00199B6C_00199CF4.bin
|unk_08199CF4|
        INCBIN  build\mapcontainer\map_00199CF4_00199D0C.bin
|unk_08199D0C|
        INCBIN  build\mapcontainer\map_00199D0C_00199D10.bin
        INCBIN  build\mapcontainer\map_00199D10_00199D60.bin
        INCBIN  build\mapcontainer\map_00199D60_00199F6C.bin
        INCBIN  build\mapcontainer\map_00199F6C_00199F9C.bin
        INCBIN  build\mapcontainer\map_00199F9C_0019A7CC.bin
        INCBIN  build\mapcontainer\map_0019A7CC_0019A7FC.bin
        INCBIN  build\mapcontainer\map_0019A7FC_0019AA44.bin
        INCBIN  build\mapcontainer\map_0019AA44_0019AA64.bin
        INCBIN  build\mapcontainer\map_0019AA64_0019ACBC.bin
        INCBIN  build\mapcontainer\map_0019ACBC_0019ACDC.bin
        INCBIN  build\mapcontainer\map_0019ACDC_0019AE34.bin
|unk_0819AE34|
        INCBIN  build\mapcontainer\map_0019AE34_0019AE4C.bin
        INCBIN  build\mapcontainer\map_0019AE4C_0019AEAC.bin
        INCLUDE rawlabeled_19aeac.s
        INCBIN  build\mapcontainer\map_0019B178_0019B1C8.bin
        INCBIN  build\mapcontainer\map_0019B1C8_0019B2F8.bin
        INCBIN  build\mapcontainer\map_0019B2F8_0019B314.bin
        INCBIN  build\mapcontainer\map_0019B314_0019B3A0.bin
        INCBIN  build\mapcontainer\map_0019B3A0_0019B3BC.bin
        INCBIN  build\mapcontainer\map_0019B3BC_0019B540.bin
        INCBIN  build\mapcontainer\map_0019B540_0019B55C.bin
        INCBIN  build\mapcontainer\map_0019B55C_0019B5A0.bin
        INCBIN  build\mapcontainer\map_0019B5A0_0019B5BC.bin
        INCBIN  build\mapcontainer\map_0019B5BC_0019B658.bin
|unk_0819B658|
        INCBIN  build\mapcontainer\map_0019B658_0019B670.bin
|unk_0819B670|
        INCBIN  build\mapcontainer\map_0019B670_0019B674.bin
        INCBIN  build\mapcontainer\map_0019B674_0019B6C4.bin
        INCBIN  build\mapcontainer\map_0019B6C4_0019B984.bin
        INCBIN  build\mapcontainer\map_0019B984_0019B9AC.bin
        INCBIN  build\mapcontainer\map_0019B9AC_0019BA44.bin
        INCBIN  build\mapcontainer\map_0019BA44_0019BA6C.bin
        INCBIN  build\mapcontainer\map_0019BA6C_0019BC74.bin
        INCBIN  build\mapcontainer\map_0019BC74_0019BC9C.bin
        INCBIN  build\mapcontainer\map_0019BC9C_0019C218.bin
        INCBIN  build\mapcontainer\map_0019C218_0019C240.bin
        INCBIN  build\mapcontainer\map_0019C240_0019C368.bin
|unk_0819C368|
        INCBIN  build\mapcontainer\map_0019C368_0019C380.bin
        INCBIN  build\mapcontainer\map_0019C380_0019C744.bin
        INCLUDE rawlabeled_19c744.s
        INCBIN  build\mapcontainer\map_0019C8A8_0019C8F8.bin
        INCBIN  build\mapcontainer\map_0019C8F8_0019CB08.bin
        INCBIN  build\mapcontainer\map_0019CB08_0019CB30.bin
        INCBIN  build\mapcontainer\map_0019CB30_0019CC30.bin
        INCBIN  build\mapcontainer\map_0019CC30_0019CC50.bin
        INCBIN  build\mapcontainer\map_0019CC50_0019CE90.bin
        INCBIN  build\mapcontainer\map_0019CE90_0019CEB8.bin
        INCBIN  build\mapcontainer\map_0019CEB8_0019D428.bin
        INCBIN  build\mapcontainer\map_0019D428_0019D450.bin
        INCBIN  build\mapcontainer\map_0019D450_0019D5DC.bin
|unk_0819D5DC|
        INCBIN  build\mapcontainer\map_0019D5DC_0019D664.bin
|unk_0819D664|
        INCBIN  build\mapcontainer\map_0019D664_0019D66C.bin
        INCBIN  build\mapcontainer\map_0019D66C_0019D6BC.bin
        INCBIN  build\mapcontainer\map_0019D6BC_0019D7C4.bin
        INCBIN  build\mapcontainer\map_0019D7C4_0019D7F4.bin
        INCBIN  build\mapcontainer\map_0019D7F4_0019E700.bin
        INCBIN  build\mapcontainer\map_0019E700_0019E748.bin
        INCBIN  build\mapcontainer\map_0019E748_0019F5B0.bin
        INCBIN  build\mapcontainer\map_0019F5B0_0019F5F8.bin
        INCBIN  build\mapcontainer\map_0019F5F8_0019F7F4.bin
|unk_0819F7F4|
        INCBIN  build\mapcontainer\map_0019F7F4_0019F854.bin
        INCBIN  build\mapcontainer\map_0019F854_0019FC04.bin
|map_anim_row_0819FC04|
|unk_0819FC04|
	DCB 0x02,0x04
	DCW 0x037c
	DCD 0x0819c788,0x0819c7f4
|unk_0819FC10|
        INCBIN  build\animframe\gen_19fc10_1a01fc.bin
|map_anim_row_081A01FC|
|unk_081A01FC|
	DCB 0x10,0x09
	DCW 0x0373
	DCD 0x0819fc10,0x0819fcec,0x0819fdc4,0x0819fe98,0x0819fc10,0x0819fcec,0x0819ff70,0x0819fcec
	DCD 0x081a004c,0x0819fcec,0x081a0128,0x0819fe98,0x081a0128,0x0819fe98,0x081a0128,0x0819fe98
|unk_081A0240|
        INCBIN  baserom.gba_0x1a0240_0x1a0248.extracted
|unk_081A0248|
        INCBIN  build\mapcontainer\map_001A0248_001A0260.bin
|unk_081A0260|
        INCBIN  build\mapcontainer\map_001A0260_001A0264.bin
        INCBIN  build\mapcontainer\map_001A0264_001A02B4.bin
        INCBIN  build\mapcontainer\map_001A02B4_001A0508.bin
        INCBIN  build\mapcontainer\map_001A0508_001A0530.bin
        INCBIN  build\mapcontainer\map_001A0530_001A0B70.bin
        INCBIN  build\mapcontainer\map_001A0B70_001A0B98.bin
        INCBIN  build\mapcontainer\map_001A0B98_001A1158.bin
        INCBIN  build\mapcontainer\map_001A1158_001A1180.bin
        INCBIN  build\mapcontainer\map_001A1180_001A1290.bin
|unk_081A1290|
        INCBIN  build\mapcontainer\map_001A1290_001A1330.bin
|unk_081A1330|
        INCBIN  build\mapcontainer\map_001A1330_001A133C.bin
        INCBIN  build\mapcontainer\map_001A133C_001A138C.bin
        INCBIN  build\mapcontainer\map_001A138C_001A165C.bin
        INCBIN  build\mapcontainer\map_001A165C_001A1684.bin
        INCBIN  build\mapcontainer\map_001A1684_001A18C8.bin
        INCBIN  build\mapcontainer\map_001A18C8_001A18F0.bin
        INCBIN  build\mapcontainer\map_001A18F0_001A1C98.bin
        INCBIN  build\mapcontainer\map_001A1C98_001A1CC0.bin
        INCBIN  build\mapcontainer\map_001A1CC0_001A227C.bin
        INCBIN  build\mapcontainer\map_001A227C_001A22A4.bin
        INCBIN  build\mapcontainer\map_001A22A4_001A241C.bin
|unk_081A241C|
        INCBIN  build\mapcontainer\map_001A241C_001A2434.bin
|map_anim_row_081A2434|
|unk_081A2434|
	DCB 0x04,0x03
	DCW 0x037d
	DCD 0x0819b130,0x0819b0ac,0x0819b0d8,0x0819b104
|map_anim_row_081A2448|
|unk_081A2448|
	DCB 0x02,0x04
	DCW 0x0379
	DCD 0x0819c788,0x0819c7f4
|unk_081A2454|
        INCBIN  build\animframe\gen_1a2454_1a2854.bin
|map_anim_row_081A2854|
|unk_081A2854|
	DCB 0x04,0x12
	DCW 0x0367
	DCD 0x081a2454,0x081a254c,0x081a264c,0x081a2754
|map_anim_row_081A2868|
|unk_081A2868|
	DCB 0x10,0x0b
	DCW 0x035c
	DCD 0x0817a9ac,0x0817aaac,0x0817abac,0x0817aca4,0x0817a9ac,0x0817aaac,0x0817ada4,0x0817aaac
	DCD 0x0817aea4,0x0817aaac,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4
|unk_081A28AC|
        INCBIN  build\animframe\gen_1a28ac_1a2be8.bin
|map_anim_row_081A2BE8|
|unk_081A2BE8|
	DCB 0x04,0x06
	DCW 0x0356
	DCD 0x081a28ac,0x081a297c,0x081a2a48,0x081a2b18
|unk_081A2BFC|
        INCBIN  build\animframe\gen_1a2bfc_1a2e44.bin
|map_anim_row_081A2E44|
|unk_081A2E44|
	DCB 0x04,0x07
	DCW 0x034f
	DCD 0x081a2bfc,0x081a2c8c,0x081a2d1c,0x081a2db0
|unk_081A2E58|
        INCBIN  baserom.gba_0x1a2e58_0x1a2e70.extracted
|unk_081A2E70|
        INCBIN  build\mapcontainer\map_001A2E70_001A2E88.bin
|unk_081A2E88|
        INCBIN  build\mapcontainer\map_001A2E88_001A2E8C.bin
        INCBIN  build\mapcontainer\map_001A2E8C_001A2EDC.bin
        INCBIN  build\mapcontainer\map_001A2EDC_001A2FD4.bin
        INCBIN  build\mapcontainer\map_001A2FD4_001A2FF4.bin
        INCBIN  build\mapcontainer\map_001A2FF4_001A332C.bin
        INCBIN  build\mapcontainer\map_001A332C_001A334C.bin
        INCBIN  build\mapcontainer\map_001A334C_001A33C4.bin
        INCBIN  build\mapcontainer\map_001A33C4_001A33E4.bin
        INCBIN  build\mapcontainer\map_001A33E4_001A3410.bin
        INCBIN  build\mapcontainer\map_001A3410_001A3460.bin
        INCBIN  build\mapcontainer\map_001A3460_001A3530.bin
        INCBIN  build\mapcontainer\map_001A3530_001A354C.bin
        INCBIN  build\mapcontainer\map_001A354C_001A3604.bin
        INCBIN  build\mapcontainer\map_001A3604_001A3620.bin
        INCBIN  build\mapcontainer\map_001A3620_001A372C.bin
        INCBIN  build\mapcontainer\map_001A372C_001A3748.bin
        INCBIN  build\mapcontainer\map_001A3748_001A38AC.bin
        INCBIN  build\mapcontainer\map_001A38AC_001A38C8.bin
        INCBIN  build\mapcontainer\map_001A38C8_001A38F0.bin
        INCBIN  build\mapcontainer\map_001A38F0_001A3940.bin
        INCBIN  build\mapcontainer\map_001A3940_001A3B34.bin
        INCBIN  build\mapcontainer\map_001A3B34_001A3B5C.bin
        INCBIN  build\mapcontainer\map_001A3B5C_001A3D7C.bin
        INCBIN  build\mapcontainer\map_001A3D7C_001A3DA4.bin
        INCBIN  build\mapcontainer\map_001A3DA4_001A4054.bin
        INCBIN  build\mapcontainer\map_001A4054_001A407C.bin
        INCBIN  build\mapcontainer\map_001A407C_001A4394.bin
        INCBIN  build\mapcontainer\map_001A4394_001A43BC.bin
        INCBIN  build\mapcontainer\map_001A43BC_001A4490.bin
|unk_081A4490|
        INCBIN  build\mapcontainer\map_001A4490_001A44A8.bin
|unk_081A44A8|
        INCBIN  build\mapcontainer\map_001A44A8_001A44AC.bin
        INCBIN  build\mapcontainer\map_001A44AC_001A44FC.bin
        INCBIN  build\mapcontainer\map_001A44FC_001A466C.bin
        INCBIN  build\mapcontainer\map_001A466C_001A468C.bin
        INCBIN  build\mapcontainer\map_001A468C_001A48B4.bin
        INCBIN  build\mapcontainer\map_001A48B4_001A48D4.bin
        INCBIN  build\mapcontainer\map_001A48D4_001A4B30.bin
        INCBIN  build\mapcontainer\map_001A4B30_001A4B50.bin
        INCBIN  build\mapcontainer\map_001A4B50_001A4DAC.bin
        INCBIN  build\mapcontainer\map_001A4DAC_001A4DCC.bin
        INCBIN  build\mapcontainer\map_001A4DCC_001A4F18.bin
|unk_081A4F18|
        INCBIN  build\mapcontainer\map_001A4F18_001A4F30.bin
        INCBIN  build\mapcontainer\map_001A4F30_001A539C.bin
|unk_081A539C|
        INCBIN  build\mapcontainer\map_001A539C_001A53CC.bin
|unk_081A53CC|
        INCBIN  build\mapcontainer\map_001A53CC_001A53D4.bin
        INCBIN  build\mapcontainer\map_001A53D4_001A5424.bin
        INCBIN  build\mapcontainer\map_001A5424_001A5678.bin
        INCBIN  build\mapcontainer\map_001A5678_001A5694.bin
        INCBIN  build\mapcontainer\map_001A5694_001A56F0.bin
        INCBIN  build\mapcontainer\map_001A56F0_001A570C.bin
        INCBIN  build\mapcontainer\map_001A570C_001A5860.bin
        INCBIN  build\mapcontainer\map_001A5860_001A587C.bin
        INCBIN  build\mapcontainer\map_001A587C_001A5A1C.bin
        INCBIN  build\mapcontainer\map_001A5A1C_001A5A38.bin
        INCBIN  build\mapcontainer\map_001A5A38_001A5B7C.bin
|unk_081A5B7C|
        INCBIN  build\mapcontainer\map_001A5B7C_001A5B94.bin
|unk_081A5B94|
        INCBIN  build\mapcontainer\map_001A5B94_001A5BC4.bin
|unk_081A5BC4|
        INCBIN  build\mapcontainer\map_001A5BC4_001A5BCC.bin
        INCBIN  build\mapcontainer\map_001A5BCC_001A5C1C.bin
        INCBIN  build\mapcontainer\map_001A5C1C_001A5F2C.bin
        INCBIN  build\mapcontainer\map_001A5F2C_001A5F54.bin
        INCBIN  build\mapcontainer\map_001A5F54_001A5F9C.bin
        INCBIN  build\mapcontainer\map_001A5F9C_001A5FB8.bin
        INCBIN  build\mapcontainer\map_001A5FB8_001A62A0.bin
        INCBIN  build\mapcontainer\map_001A62A0_001A62C8.bin
        INCBIN  build\mapcontainer\map_001A62C8_001A6384.bin
|unk_081A6384|
        INCBIN  build\mapcontainer\map_001A6384_001A639C.bin
        INCBIN  build\mapcontainer\map_001A639C_001A6890.bin
|unk_081A6890|
        INCBIN  build\mapcontainer\map_001A6890_001A68F0.bin
|unk_081A68F0|
        INCBIN  build\mapcontainer\map_001A68F0_001A68F4.bin
        INCBIN  build\mapcontainer\map_001A68F4_001A6944.bin
        INCBIN  build\mapcontainer\map_001A6944_001A6B20.bin
        INCBIN  build\mapcontainer\map_001A6B20_001A6B5C.bin
        INCBIN  build\mapcontainer\map_001A6B5C_001A70FC.bin
        INCBIN  build\mapcontainer\map_001A70FC_001A7138.bin
        INCBIN  build\mapcontainer\map_001A7138_001A744C.bin
        INCBIN  build\mapcontainer\map_001A744C_001A7488.bin
        INCBIN  build\mapcontainer\map_001A7488_001A7F14.bin
        INCBIN  build\mapcontainer\map_001A7F14_001A7F6C.bin
        INCBIN  build\mapcontainer\map_001A7F6C_001A8110.bin
|unk_081A8110|
        INCBIN  build\mapcontainer\map_001A8110_001A89E0.bin
        INCBIN  build\mapcontainer\map_001A89E0_001A90A8.bin
|unk_081A90A8|
        INCBIN  build\animframe\gen_1a90a8_1a9570.bin
|unk_081A9570|
        INCBIN  build\mapcontainer\map_001A9570_001A95E8.bin
|unk_081A95E8|
        INCBIN  build\mapcontainer\map_001A95E8_001A95F0.bin
        INCBIN  build\mapcontainer\map_001A95F0_001A9640.bin
        INCBIN  build\mapcontainer\map_001A9640_001A9BC4.bin
        INCBIN  build\mapcontainer\map_001A9BC4_001A9BF4.bin
        INCBIN  build\mapcontainer\map_001A9BF4_001A9D8C.bin
        INCBIN  build\mapcontainer\map_001A9D8C_001A9DB4.bin
        INCBIN  build\mapcontainer\map_001A9DB4_001AA2E4.bin
        INCBIN  build\mapcontainer\map_001AA2E4_001AA314.bin
        INCBIN  build\mapcontainer\map_001AA314_001AA81C.bin
        INCBIN  build\mapcontainer\map_001AA81C_001AA83C.bin
        INCBIN  build\mapcontainer\map_001AA83C_001AA968.bin
|unk_081AA968|
        INCBIN  build\mapcontainer\map_001AA968_001AA9B0.bin
        INCBIN  build\mapcontainer\map_001AA9B0_001AAC54.bin
|unk_081AAC54|
        INCBIN  build\mapcontainer\map_001AAC54_001AACCC.bin
|unk_081AACCC|
        INCBIN  build\mapcontainer\map_001AACCC_001AACD4.bin
        INCBIN  build\mapcontainer\map_001AACD4_001AAD24.bin
        INCBIN  build\mapcontainer\map_001AAD24_001AADF8.bin
        INCBIN  build\mapcontainer\map_001AADF8_001AAE14.bin
        INCBIN  build\mapcontainer\map_001AAE14_001AAEA8.bin
        INCBIN  build\mapcontainer\map_001AAEA8_001AAEC4.bin
        INCBIN  build\mapcontainer\map_001AAEC4_001AB38C.bin
        INCBIN  build\mapcontainer\map_001AB38C_001AB3A8.bin
        INCBIN  build\mapcontainer\map_001AB3A8_001AB430.bin
        INCLUDE rawlabeled_1ab430.s
        INCBIN  build\mapcontainer\map_001AB484_001AB4D4.bin
        INCBIN  build\mapcontainer\map_001AB4D4_001AB6F4.bin
        INCBIN  build\mapcontainer\map_001AB6F4_001AB71C.bin
        INCBIN  build\mapcontainer\map_001AB71C_001AB7FC.bin
        INCBIN  build\mapcontainer\map_001AB7FC_001AB824.bin
        INCBIN  build\mapcontainer\map_001AB824_001ABBC4.bin
        INCBIN  build\mapcontainer\map_001ABBC4_001ABBEC.bin
        INCBIN  build\mapcontainer\map_001ABBEC_001ABCE8.bin
|unk_081ABCE8|
        INCBIN  build\mapcontainer\map_001ABCE8_001ABE98.bin
        INCBIN  build\jcalg1\gen_1abe98.bin
|unk_081ABF28|
        INCBIN  build\animframe\gen_1abf28_1ac1dc.bin
|map_anim_row_081AC1DC|
|unk_081AC1DC|
	DCB 0x10,0x04
	DCW 0x037c
	DCD 0x081abf28,0x081abf8c,0x081abff0,0x081ac050,0x081abf28,0x081abf8c,0x081ac0b4,0x081abf8c
	DCD 0x081ac118,0x081abf8c,0x081ac17c,0x081ac050,0x081ac17c,0x081ac050,0x081ac17c,0x081ac050
|unk_081AC220|
        INCBIN  build\animframe\gen_1ac220_1ac550.bin
|map_anim_row_081AC550|
|unk_081AC550|
	DCB 0x04,0x06
	DCW 0x0376
	DCD 0x081ac220,0x081ac2ec,0x081ac3b4,0x081ac484
|unk_081AC564|
        INCBIN  build\animframe\gen_1ac564_1ac754.bin
|map_anim_row_081AC754|
|unk_081AC754|
	DCB 0x04,0x06
	DCW 0x0370
	DCD 0x081ac564,0x081ac5e0,0x081ac658,0x081ac6d8
|unk_081AC768|
        INCBIN  build\animframe\gen_1ac768_1ad15c.bin
|map_anim_row_081AD15C|
|unk_081AD15C|
	DCB 0x09,0x1b
	DCW 0x0355
	DCD 0x081ac768,0x081ac884,0x081ac99c,0x081acaa0,0x081acbd4,0x081accf0,0x081ace00,0x081acefc
	DCD 0x081ad028
|unk_081AD184|
        INCBIN  baserom.gba_0x1ad184_0x1ad194.extracted
|unk_081AD194|
        INCBIN  build\mapcontainer\map_001AD194_001AD1DC.bin
|unk_081AD1DC|
        INCBIN  build\mapcontainer\map_001AD1DC_001AD1E8.bin
        INCBIN  build\mapcontainer\map_001AD1E8_001AD238.bin
        INCBIN  build\mapcontainer\map_001AD238_001AD320.bin
        INCBIN  build\mapcontainer\map_001AD320_001AD348.bin
        INCBIN  build\mapcontainer\map_001AD348_001AD4FC.bin
        INCBIN  build\mapcontainer\map_001AD4FC_001AD524.bin
        INCBIN  build\mapcontainer\map_001AD524_001AD7D4.bin
        INCBIN  build\mapcontainer\map_001AD7D4_001AD7FC.bin
        INCBIN  build\mapcontainer\map_001AD7FC_001ADCC4.bin
        INCBIN  build\mapcontainer\map_001ADCC4_001ADCE0.bin
        INCBIN  build\mapcontainer\map_001ADCE0_001ADDB4.bin
|unk_081ADDB4|
        INCBIN  build\animframe\gen_1addb4_1ae1dc.bin
|map_anim_row_081AE1DC|
|unk_081AE1DC|
	DCB 0x10,0x06
	DCW 0x037a
	DCD 0x081addb4,0x081ade4c,0x081adee8,0x081adf7c,0x081addb4,0x081ade4c,0x081ae018,0x081ade4c
	DCD 0x081ae0b0,0x081ade4c,0x081ae148,0x081adf7c,0x081ae148,0x081adf7c,0x081ae148,0x081adf7c
|map_anim_row_081AE220|
|unk_081AE220|
	DCB 0x04,0x06
	DCW 0x0374
	DCD 0x081ac220,0x081ac2ec,0x081ac3b4,0x081ac484
|unk_081AE234|
        INCBIN  build\animframe\gen_1ae234_1aeae0.bin
|map_anim_row_081AEAE0|
|unk_081AEAE0|
	DCB 0x09,0x17
	DCW 0x035d
	DCD 0x081ae234,0x081ae338,0x081ae434,0x081ae504,0x081ae5f8,0x081ae6c8,0x081ae7c4,0x081ae8b0
	DCD 0x081ae9c4
|map_anim_row_081AEB08|
|unk_081AEB08|
	DCB 0x04,0x06
	DCW 0x0357
	DCD 0x081ac564,0x081ac5e0,0x081ac658,0x081ac6d8
|unk_081AEB1C|
        INCBIN  baserom.gba_0x1aeb1c_0x1aeb2c.extracted
|unk_081AEB2C|
        INCBIN  build\mapcontainer\map_001AEB2C_001AEB5C.bin
|unk_081AEB5C|
        INCBIN  build\mapcontainer\map_001AEB5C_001AEB64.bin
        INCBIN  build\mapcontainer\map_001AEB64_001AEBB4.bin
        INCBIN  build\mapcontainer\map_001AEBB4_001AEDB4.bin
        INCBIN  build\mapcontainer\map_001AEDB4_001AEDDC.bin
        INCBIN  build\mapcontainer\map_001AEDDC_001AEE60.bin
        INCBIN  build\mapcontainer\map_001AEE60_001AEE80.bin
        INCBIN  build\mapcontainer\map_001AEE80_001AF228.bin
        INCBIN  build\mapcontainer\map_001AF228_001AF250.bin
        INCBIN  build\mapcontainer\map_001AF250_001AF324.bin
|unk_081AF324|
        INCBIN  build\mapcontainer\map_001AF324_001AF534.bin
        INCBIN  build\mapcontainer\map_001AF534_001AF7CC.bin
|unk_081AF7CC|
        INCBIN  build\mapcontainer\map_001AF7CC_001AF870.bin
|unk_081AF870|
        INCBIN  build\mapcontainer\map_001AF870_001AF874.bin
        INCBIN  build\mapcontainer\map_001AF874_001AF8C4.bin
        INCBIN  build\mapcontainer\map_001AF8C4_001AF988.bin
        INCBIN  build\mapcontainer\map_001AF988_001AF9B0.bin
        INCBIN  build\mapcontainer\map_001AF9B0_001AFA5C.bin
        INCBIN  build\mapcontainer\map_001AFA5C_001AFA84.bin
        INCBIN  build\mapcontainer\map_001AFA84_001AFDC0.bin
        INCBIN  build\mapcontainer\map_001AFDC0_001AFDE8.bin
        INCBIN  build\mapcontainer\map_001AFDE8_001AFEA8.bin
|unk_081AFEA8|
        INCBIN  build\mapcontainer\map_001AFEA8_001AFEC0.bin
        INCBIN  build\mapcontainer\map_001AFEC0_001AFFA8.bin
|unk_081AFFA8|
        INCBIN  build\mapcontainer\map_001AFFA8_001B0034.bin
|unk_081B0034|
        INCBIN  build\mapcontainer\map_001B0034_001B0040.bin
        INCBIN  build\mapcontainer\map_001B0040_001B0090.bin
        INCBIN  build\mapcontainer\map_001B0090_001B0188.bin
        INCBIN  build\mapcontainer\map_001B0188_001B01A4.bin
        INCBIN  build\mapcontainer\map_001B01A4_001B01F0.bin
        INCBIN  build\mapcontainer\map_001B01F0_001B020C.bin
        INCBIN  build\mapcontainer\map_001B020C_001B02E0.bin
        INCBIN  build\mapcontainer\map_001B02E0_001B02FC.bin
        INCBIN  build\mapcontainer\map_001B02FC_001B037C.bin
|unk_081B037C|
        INCBIN  build\mapcontainer\map_001B037C_001B03F4.bin
|unk_081B03F4|
        INCBIN  build\mapcontainer\map_001B03F4_001B03FC.bin
        INCBIN  build\mapcontainer\map_001B03FC_001B044C.bin
        INCBIN  build\mapcontainer\map_001B044C_001B067C.bin
        INCBIN  build\mapcontainer\map_001B067C_001B069C.bin
        INCBIN  build\mapcontainer\map_001B069C_001B06F4.bin
        INCBIN  build\mapcontainer\map_001B06F4_001B0714.bin
        INCBIN  build\mapcontainer\map_001B0714_001B08A4.bin
        INCBIN  build\mapcontainer\map_001B08A4_001B08C4.bin
        INCBIN  build\mapcontainer\map_001B08C4_001B0B60.bin
        INCBIN  build\mapcontainer\map_001B0B60_001B0B80.bin
        INCBIN  build\mapcontainer\map_001B0B80_001B0CCC.bin
|unk_081B0CCC|
        INCBIN  build\mapcontainer\map_001B0CCC_001B0CFC.bin
        INCBIN  build\mapcontainer\map_001B0CFC_001B0DCC.bin
|unk_081B0DCC|
        INCBIN  build\mapcontainer\map_001B0DCC_001B0DFC.bin
|unk_081B0DFC|
        INCBIN  build\mapcontainer\map_001B0DFC_001B0E04.bin
        INCBIN  build\mapcontainer\map_001B0E04_001B0E54.bin
        INCBIN  build\mapcontainer\map_001B0E54_001B108C.bin
        INCBIN  build\mapcontainer\map_001B108C_001B10B4.bin
        INCBIN  build\mapcontainer\map_001B10B4_001B142C.bin
        INCBIN  build\mapcontainer\map_001B142C_001B1454.bin
        INCBIN  build\mapcontainer\map_001B1454_001B1874.bin
        INCBIN  build\mapcontainer\map_001B1874_001B189C.bin
        INCBIN  build\mapcontainer\map_001B189C_001B1A08.bin
|unk_081B1A08|
        INCBIN  build\mapcontainer\map_001B1A08_001B1A20.bin
|unk_081B1A20|
        INCBIN  build\mapcontainer\map_001B1A20_001B1A50.bin
|unk_081B1A50|
        INCBIN  build\mapcontainer\map_001B1A50_001B1A58.bin
        INCBIN  build\mapcontainer\map_001B1A58_001B1AA8.bin
        INCBIN  build\mapcontainer\map_001B1AA8_001B1AF8.bin
        INCBIN  build\mapcontainer\map_001B1AF8_001B1B14.bin
        INCBIN  build\mapcontainer\map_001B1B14_001B1BB8.bin
        INCBIN  build\mapcontainer\map_001B1BB8_001B1BD4.bin
        INCBIN  build\mapcontainer\map_001B1BD4_001B1C88.bin
        INCBIN  build\mapcontainer\map_001B1C88_001B1CA4.bin
        INCBIN  build\mapcontainer\map_001B1CA4_001B1CF8.bin
|unk_081B1CF8|
        INCBIN  build\mapcontainer\map_001B1CF8_001B1DE8.bin
        INCBIN  build\mapcontainer\map_001B1DE8_001B1FF4.bin
|unk_081B1FF4|
        INCBIN  build\mapcontainer\map_001B1FF4_001B200C.bin
|unk_081B200C|
        INCBIN  build\mapcontainer\map_001B200C_001B2010.bin
        INCBIN  build\mapcontainer\map_001B2010_001B2060.bin
        INCBIN  build\mapcontainer\map_001B2060_001B2174.bin
        INCBIN  build\mapcontainer\map_001B2174_001B219C.bin
        INCBIN  build\mapcontainer\map_001B219C_001B24E8.bin
        INCBIN  build\mapcontainer\map_001B24E8_001B2510.bin
        INCBIN  build\mapcontainer\map_001B2510_001B2C54.bin
        INCBIN  build\mapcontainer\map_001B2C54_001B2C7C.bin
        INCBIN  build\mapcontainer\map_001B2C7C_001B2C9C.bin
        INCBIN  build\mapcontainer\map_001B2C9C_001B2CBC.bin
        INCBIN  build\mapcontainer\map_001B2CBC_001B2DAC.bin
|map_anim_row_081B2DAC|
|unk_081B2DAC|
	DCB 0x02,0x01
	DCW 0x037f
	DCD 0x0819125c,0x08191288
|map_anim_row_081B2DB8|
|unk_081B2DB8|
	DCB 0x02,0x02
	DCW 0x037d
	DCD 0x081911d8,0x08191214
|unk_081B2DC4|
        INCBIN  build\animframe\gen_1b2dc4_1b2efc.bin
|map_anim_row_081B2EFC|
|unk_081B2EFC|
	DCB 0x04,0x04
	DCW 0x0379
	DCD 0x081b2dc4,0x081b2e2c,0x081b2e90,0x081b2e2c
|unk_081B2F10|
        INCBIN  baserom.gba_0x1b2f10_0x1b2f1c.extracted
|unk_081B2F1C|
        INCBIN  build\mapcontainer\map_001B2F1C_001B2F34.bin
|unk_081B2F34|
        INCBIN  build\mapcontainer\map_001B2F34_001B2F38.bin
        INCBIN  build\mapcontainer\map_001B2F38_001B2F88.bin
        INCBIN  build\mapcontainer\map_001B2F88_001B31D0.bin
        INCBIN  build\mapcontainer\map_001B31D0_001B31F0.bin
        INCBIN  build\mapcontainer\map_001B31F0_001B3288.bin
        INCBIN  build\mapcontainer\map_001B3288_001B32A4.bin
        INCBIN  build\mapcontainer\map_001B32A4_001B372C.bin
        INCBIN  build\mapcontainer\map_001B372C_001B374C.bin
        INCBIN  build\mapcontainer\map_001B374C_001B3958.bin
        INCBIN  build\mapcontainer\map_001B3958_001B3978.bin
        INCBIN  build\mapcontainer\map_001B3978_001B3A70.bin
|unk_081B3A70|
        INCBIN  build\mapcontainer\map_001B3A70_001B3AA0.bin
|unk_081B3AA0|
        INCBIN  build\mapcontainer\map_001B3AA0_001B3AA8.bin
        INCBIN  build\mapcontainer\map_001B3AA8_001B3AF8.bin
        INCBIN  build\mapcontainer\map_001B3AF8_001B3DF4.bin
        INCBIN  build\mapcontainer\map_001B3DF4_001B3E1C.bin
        INCBIN  build\mapcontainer\map_001B3E1C_001B3EA0.bin
        INCBIN  build\mapcontainer\map_001B3EA0_001B3EC0.bin
        INCBIN  build\mapcontainer\map_001B3EC0_001B41D8.bin
        INCBIN  build\mapcontainer\map_001B41D8_001B4200.bin
        INCBIN  build\mapcontainer\map_001B4200_001B4300.bin
        INCBIN  build\mapcontainer\map_001B4300_001B4328.bin
        INCBIN  build\mapcontainer\map_001B4328_001B4488.bin
|unk_081B4488|
        INCBIN  build\mapcontainer\map_001B4488_001B44B8.bin
|unk_081B44B8|
        INCBIN  build\mapcontainer\map_001B44B8_001B44C0.bin
        INCBIN  build\mapcontainer\map_001B44C0_001B4510.bin
        INCBIN  build\mapcontainer\map_001B4510_001B4714.bin
        INCBIN  build\mapcontainer\map_001B4714_001B4734.bin
        INCBIN  build\mapcontainer\map_001B4734_001B47D4.bin
        INCBIN  build\mapcontainer\map_001B47D4_001B47F4.bin
        INCBIN  build\mapcontainer\map_001B47F4_001B4ACC.bin
        INCBIN  build\mapcontainer\map_001B4ACC_001B4AEC.bin
        INCBIN  build\mapcontainer\map_001B4AEC_001B4CF8.bin
        INCBIN  build\mapcontainer\map_001B4CF8_001B4D18.bin
        INCBIN  build\mapcontainer\map_001B4D18_001B4E28.bin
|unk_081B4E28|
        INCBIN  build\mapcontainer\map_001B4E28_001B4E58.bin
|unk_081B4E58|
        INCBIN  build\mapcontainer\map_001B4E58_001B4E60.bin
        INCBIN  build\mapcontainer\map_001B4E60_001B4EB0.bin
        INCBIN  build\mapcontainer\map_001B4EB0_001B50C8.bin
        INCBIN  build\mapcontainer\map_001B50C8_001B50E8.bin
        INCBIN  build\mapcontainer\map_001B50E8_001B5194.bin
        INCBIN  build\mapcontainer\map_001B5194_001B51B4.bin
        INCBIN  build\mapcontainer\map_001B51B4_001B5410.bin
        INCBIN  build\mapcontainer\map_001B5410_001B5430.bin
        INCBIN  build\mapcontainer\map_001B5430_001B5650.bin
        INCBIN  build\mapcontainer\map_001B5650_001B5670.bin
        INCBIN  build\mapcontainer\map_001B5670_001B5790.bin
|unk_081B5790|
        INCBIN  build\mapcontainer\map_001B5790_001B57C0.bin
|unk_081B57C0|
        INCBIN  build\mapcontainer\map_001B57C0_001B57C8.bin
        INCBIN  build\mapcontainer\map_001B57C8_001B5818.bin
        INCBIN  build\mapcontainer\map_001B5818_001B5A6C.bin
        INCBIN  build\mapcontainer\map_001B5A6C_001B5A94.bin
        INCBIN  build\mapcontainer\map_001B5A94_001B5B34.bin
        INCBIN  build\mapcontainer\map_001B5B34_001B5B5C.bin
        INCBIN  build\mapcontainer\map_001B5B5C_001B5F10.bin
        INCBIN  build\mapcontainer\map_001B5F10_001B5F38.bin
        INCBIN  build\mapcontainer\map_001B5F38_001B6038.bin
        INCBIN  build\mapcontainer\map_001B6038_001B6060.bin
        INCBIN  build\mapcontainer\map_001B6060_001B618C.bin
|unk_081B618C|
        INCBIN  build\mapcontainer\map_001B618C_001B61BC.bin
|unk_081B61BC|
        INCBIN  build\mapcontainer\map_001B61BC_001B61C4.bin
        INCBIN  build\mapcontainer\map_001B61C4_001B6214.bin
        INCBIN  build\mapcontainer\map_001B6214_001B63C0.bin
        INCBIN  build\mapcontainer\map_001B63C0_001B63DC.bin
        INCBIN  build\mapcontainer\map_001B63DC_001B646C.bin
        INCBIN  build\mapcontainer\map_001B646C_001B6488.bin
        INCBIN  build\mapcontainer\map_001B6488_001B669C.bin
        INCBIN  build\mapcontainer\map_001B669C_001B66B8.bin
        INCBIN  build\mapcontainer\map_001B66B8_001B66FC.bin
        INCBIN  build\mapcontainer\map_001B66FC_001B6718.bin
        INCBIN  build\mapcontainer\map_001B6718_001B6810.bin
|unk_081B6810|
        INCBIN  build\mapcontainer\map_001B6810_001B6840.bin
|unk_081B6840|
        INCBIN  build\mapcontainer\map_001B6840_001B6848.bin
        INCBIN  build\mapcontainer\map_001B6848_001B6898.bin
        INCBIN  build\mapcontainer\map_001B6898_001B6AF0.bin
        INCBIN  build\mapcontainer\map_001B6AF0_001B6B10.bin
        INCBIN  build\mapcontainer\map_001B6B10_001B6BB8.bin
        INCBIN  build\mapcontainer\map_001B6BB8_001B6BD8.bin
        INCBIN  build\mapcontainer\map_001B6BD8_001B6DF8.bin
        INCBIN  build\mapcontainer\map_001B6DF8_001B6E18.bin
        INCBIN  build\mapcontainer\map_001B6E18_001B6E98.bin
        INCBIN  build\mapcontainer\map_001B6E98_001B6EB8.bin
        INCBIN  build\mapcontainer\map_001B6EB8_001B6FEC.bin
|unk_081B6FEC|
        INCBIN  build\mapcontainer\map_001B6FEC_001B7004.bin
        INCBIN  build\mapcontainer\map_001B7004_001B71B8.bin
|unk_081B71B8|
        INCBIN  build\mapcontainer\map_001B71B8_001B7200.bin
|unk_081B7200|
        INCBIN  build\mapcontainer\map_001B7200_001B720C.bin
        INCBIN  build\mapcontainer\map_001B720C_001B725C.bin
        INCBIN  build\mapcontainer\map_001B725C_001B74B4.bin
        INCBIN  build\mapcontainer\map_001B74B4_001B74D4.bin
        INCBIN  build\mapcontainer\map_001B74D4_001B7560.bin
        INCBIN  build\mapcontainer\map_001B7560_001B7580.bin
        INCBIN  build\mapcontainer\map_001B7580_001B78A0.bin
        INCBIN  build\mapcontainer\map_001B78A0_001B78C0.bin
        INCBIN  build\mapcontainer\map_001B78C0_001B7AC8.bin
        INCBIN  build\mapcontainer\map_001B7AC8_001B7AE8.bin
        INCBIN  build\mapcontainer\map_001B7AE8_001B7BFC.bin
|unk_081B7BFC|
        INCBIN  build\mapcontainer\map_001B7BFC_001B7C2C.bin
|unk_081B7C2C|
        INCBIN  build\mapcontainer\map_001B7C2C_001B7C34.bin
        INCBIN  build\mapcontainer\map_001B7C34_001B7C84.bin
        INCBIN  build\mapcontainer\map_001B7C84_001B8028.bin
        INCBIN  build\mapcontainer\map_001B8028_001B8050.bin
        INCBIN  build\mapcontainer\map_001B8050_001B8174.bin
        INCBIN  build\mapcontainer\map_001B8174_001B819C.bin
        INCBIN  build\mapcontainer\map_001B819C_001B8598.bin
        INCBIN  build\mapcontainer\map_001B8598_001B85C0.bin
        INCBIN  build\mapcontainer\map_001B85C0_001B86C0.bin
        INCBIN  build\mapcontainer\map_001B86C0_001B86E8.bin
        INCBIN  build\mapcontainer\map_001B86E8_001B8818.bin
|unk_081B8818|
        INCBIN  build\mapcontainer\map_001B8818_001B8860.bin
|unk_081B8860|
        INCBIN  build\mapcontainer\map_001B8860_001B886C.bin
        INCBIN  build\mapcontainer\map_001B886C_001B88BC.bin
        INCBIN  build\mapcontainer\map_001B88BC_001B8DA4.bin
        INCBIN  build\mapcontainer\map_001B8DA4_001B8DD4.bin
        INCBIN  build\mapcontainer\map_001B8DD4_001B8F2C.bin
        INCBIN  build\mapcontainer\map_001B8F2C_001B8F5C.bin
        INCBIN  build\mapcontainer\map_001B8F5C_001B9680.bin
        INCBIN  build\mapcontainer\map_001B9680_001B96B0.bin
        INCBIN  build\mapcontainer\map_001B96B0_001B99E0.bin
        INCBIN  build\mapcontainer\map_001B99E0_001B9A10.bin
        INCBIN  build\mapcontainer\map_001B9A10_001B9BB8.bin
        INCLUDE rawlabeled_1b9bb8.s
        INCBIN  build\mapcontainer\map_001B9C0C_001B9C5C.bin
        INCBIN  build\mapcontainer\map_001B9C5C_001B9DFC.bin
        INCBIN  build\mapcontainer\map_001B9DFC_001B9E18.bin
        INCBIN  build\mapcontainer\map_001B9E18_001B9EA8.bin
        INCBIN  build\mapcontainer\map_001B9EA8_001B9EC4.bin
        INCBIN  build\mapcontainer\map_001B9EC4_001BA06C.bin
        INCBIN  build\mapcontainer\map_001BA06C_001BA088.bin
        INCBIN  build\mapcontainer\map_001BA088_001BA0CC.bin
        INCBIN  build\mapcontainer\map_001BA0CC_001BA0E8.bin
        INCBIN  build\mapcontainer\map_001BA0E8_001BA1D8.bin
|unk_081BA1D8|
        INCBIN  build\mapcontainer\map_001BA1D8_001BA208.bin
|unk_081BA208|
        INCBIN  build\mapcontainer\map_001BA208_001BA210.bin
        INCBIN  build\mapcontainer\map_001BA210_001BA260.bin
        INCBIN  build\mapcontainer\map_001BA260_001BA64C.bin
        INCBIN  build\mapcontainer\map_001BA64C_001BA674.bin
        INCBIN  build\mapcontainer\map_001BA674_001BA790.bin
        INCBIN  build\mapcontainer\map_001BA790_001BA7B8.bin
        INCBIN  build\mapcontainer\map_001BA7B8_001BAD14.bin
        INCBIN  build\mapcontainer\map_001BAD14_001BAD3C.bin
        INCBIN  build\mapcontainer\map_001BAD3C_001BAE4C.bin
        INCBIN  build\mapcontainer\map_001BAE4C_001BAE74.bin
        INCBIN  build\mapcontainer\map_001BAE74_001BB010.bin
|unk_081BB010|
        INCBIN  build\mapcontainer\map_001BB010_001BB070.bin
|unk_081BB070|
        INCBIN  build\mapcontainer\map_001BB070_001BB080.bin
        INCBIN  build\mapcontainer\map_001BB080_001BB0D0.bin
        INCBIN  build\mapcontainer\map_001BB0D0_001BB5B8.bin
        INCBIN  build\mapcontainer\map_001BB5B8_001BB5F4.bin
        INCBIN  build\mapcontainer\map_001BB5F4_001BB8B4.bin
        INCBIN  build\mapcontainer\map_001BB8B4_001BB8F0.bin
        INCBIN  build\mapcontainer\map_001BB8F0_001BC67C.bin
        INCBIN  build\mapcontainer\map_001BC67C_001BC6C4.bin
        INCBIN  build\mapcontainer\map_001BC6C4_001BD900.bin
        INCBIN  build\mapcontainer\map_001BD900_001BD958.bin
        INCBIN  build\mapcontainer\map_001BD958_001BDC54.bin
|unk_081BDC54|
        INCBIN  build\mapcontainer\map_001BDC54_001BDF24.bin
        INCBIN  build\mapcontainer\map_001BDF24_001BE0F0.bin
|unk_081BE0F0|
        INCBIN  build\mapcontainer\map_001BE0F0_001BE260.bin
|unk_081BE260|
        INCBIN  build\mapcontainer\map_001BE260_001BE298.bin
        INCBIN  build\mapcontainer\map_001BE298_001BE2E8.bin
        INCBIN  build\mapcontainer\map_001BE2E8_001BE4D0.bin
        INCBIN  build\mapcontainer\map_001BE4D0_001BE4F8.bin
        INCBIN  build\mapcontainer\map_001BE4F8_001BE624.bin
        INCBIN  build\mapcontainer\map_001BE624_001BE644.bin
        INCBIN  build\mapcontainer\map_001BE644_001BE90C.bin
        INCBIN  build\mapcontainer\map_001BE90C_001BE934.bin
        INCBIN  build\mapcontainer\map_001BE934_001BEEC4.bin
        INCBIN  build\mapcontainer\map_001BEEC4_001BEEEC.bin
        INCBIN  build\mapcontainer\map_001BEEEC_001BF08C.bin
|unk_081BF08C|
        INCBIN  build\mapcontainer\map_001BF08C_001BF124.bin
|unk_081BF124|
        INCBIN  build\mapcontainer\map_001BF124_001BF12C.bin
        INCBIN  build\mapcontainer\map_001BF12C_001BF17C.bin
        INCBIN  build\mapcontainer\map_001BF17C_001BF358.bin
        INCBIN  build\mapcontainer\map_001BF358_001BF378.bin
        INCBIN  build\mapcontainer\map_001BF378_001BF480.bin
        INCBIN  build\mapcontainer\map_001BF480_001BF4A0.bin
        INCBIN  build\mapcontainer\map_001BF4A0_001BF64C.bin
        INCBIN  build\mapcontainer\map_001BF64C_001BF66C.bin
        INCBIN  build\mapcontainer\map_001BF66C_001BF97C.bin
        INCBIN  build\mapcontainer\map_001BF97C_001BF99C.bin
        INCBIN  build\mapcontainer\map_001BF99C_001BFAA4.bin
        INCLUDE rawlabeled_1bfaa4.s
        INCBIN  build\mapcontainer\map_001BFE30_001BFE80.bin
        INCBIN  build\mapcontainer\map_001BFE80_001C0140.bin
        INCBIN  build\mapcontainer\map_001C0140_001C0168.bin
        INCBIN  build\mapcontainer\map_001C0168_001C021C.bin
        INCBIN  build\mapcontainer\map_001C021C_001C0244.bin
        INCBIN  build\mapcontainer\map_001C0244_001C0508.bin
        INCBIN  build\mapcontainer\map_001C0508_001C0530.bin
        INCBIN  build\mapcontainer\map_001C0530_001C0B08.bin
        INCBIN  build\mapcontainer\map_001C0B08_001C0B30.bin
        INCBIN  build\mapcontainer\map_001C0B30_001C0CB4.bin
|unk_081C0CB4|
        INCBIN  build\animframe\gen_1c0cb4_1c0d68.bin
|unk_081C0D68|
        INCBIN  build\mapcontainer\map_001C0D68_001C0E30.bin
|unk_081C0E30|
        INCBIN  build\mapcontainer\map_001C0E30_001C0E38.bin
        INCBIN  build\mapcontainer\map_001C0E38_001C0E88.bin
        INCBIN  build\mapcontainer\map_001C0E88_001C0FE4.bin
        INCBIN  build\mapcontainer\map_001C0FE4_001C1004.bin
        INCBIN  build\mapcontainer\map_001C1004_001C109C.bin
        INCBIN  build\mapcontainer\map_001C109C_001C10BC.bin
        INCBIN  build\mapcontainer\map_001C10BC_001C11B4.bin
        INCBIN  build\mapcontainer\map_001C11B4_001C11D4.bin
        INCBIN  build\mapcontainer\map_001C11D4_001C1504.bin
        INCBIN  build\mapcontainer\map_001C1504_001C1524.bin
        INCBIN  build\mapcontainer\map_001C1524_001C1630.bin
|map_anim_row_081C1630|
|unk_081C1630|
	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x081911d8,0x08191214
|map_anim_row_081C163C|
|unk_081C163C|
	DCB 0x02,0x02
	DCW 0x037c
	DCD 0x081bfd60,0x081bfd9c
|unk_081C1648|
        INCBIN  build\animframe\gen_1c1648_1c18e4.bin
|map_anim_row_081C18E4|
|unk_081C18E4|
	DCB 0x04,0x10
	DCW 0x036c
	DCD 0x081c1648,0x081c1728,0x081c1800,0x081c1728
|map_anim_row_081C18F8|
|unk_081C18F8|
	DCB 0x04,0x03
	DCW 0x0369
	DCD 0x0819b130,0x0819b0ac,0x0819b0d8,0x0819b104
|map_anim_row_081C190C|
|unk_081C190C|
	DCB 0x10,0x0b
	DCW 0x035e
	DCD 0x0817a9ac,0x0817aaac,0x0817abac,0x0817aca4,0x0817a9ac,0x0817aaac,0x0817ada4,0x0817aaac
	DCD 0x0817aea4,0x0817aaac,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4
|unk_081C1950|
        INCBIN  baserom.gba_0x1c1950_0x1c1964.extracted
|unk_081C1964|
        INCBIN  build\mapcontainer\map_001C1964_001C1994.bin
|unk_081C1994|
        INCBIN  build\mapcontainer\map_001C1994_001C199C.bin
        INCBIN  build\mapcontainer\map_001C199C_001C19EC.bin
        INCBIN  build\mapcontainer\map_001C19EC_001C1DB0.bin
        INCBIN  build\mapcontainer\map_001C1DB0_001C1DD8.bin
        INCBIN  build\mapcontainer\map_001C1DD8_001C1EF0.bin
        INCBIN  build\mapcontainer\map_001C1EF0_001C1F18.bin
        INCBIN  build\mapcontainer\map_001C1F18_001C2118.bin
        INCBIN  build\mapcontainer\map_001C2118_001C2140.bin
        INCBIN  build\mapcontainer\map_001C2140_001C271C.bin
        INCBIN  build\mapcontainer\map_001C271C_001C2744.bin
        INCBIN  build\mapcontainer\map_001C2744_001C28D4.bin
|unk_081C28D4|
        INCBIN  build\mapcontainer\map_001C28D4_001C299C.bin
|unk_081C299C|
        INCBIN  build\mapcontainer\map_001C299C_001C29A4.bin
        INCBIN  build\mapcontainer\map_001C29A4_001C29F4.bin
        INCBIN  build\mapcontainer\map_001C29F4_001C2B58.bin
        INCBIN  build\mapcontainer\map_001C2B58_001C2B78.bin
        INCBIN  build\mapcontainer\map_001C2B78_001C2C18.bin
        INCBIN  build\mapcontainer\map_001C2C18_001C2C38.bin
        INCBIN  build\mapcontainer\map_001C2C38_001C2CE4.bin
        INCBIN  build\mapcontainer\map_001C2CE4_001C2D04.bin
        INCBIN  build\mapcontainer\map_001C2D04_001C2DF8.bin
        INCBIN  build\mapcontainer\map_001C2DF8_001C2E18.bin
        INCBIN  build\mapcontainer\map_001C2E18_001C2EF4.bin
|unk_081C2EF4|
        INCBIN  build\mapcontainer\map_001C2EF4_001C2F0C.bin
        INCBIN  build\mapcontainer\map_001C2F0C_001C2FF4.bin
|unk_081C2FF4|
        INCBIN  build\animframe\gen_1c2ff4_1c30a8.bin
|unk_081C30A8|
        INCBIN  build\mapcontainer\map_001C30A8_001C3118.bin
|unk_081C3118|
        INCBIN  build\mapcontainer\map_001C3118_001C3120.bin
        INCBIN  build\mapcontainer\map_001C3120_001C3170.bin
        INCBIN  build\mapcontainer\map_001C3170_001C344C.bin
        INCBIN  build\mapcontainer\map_001C344C_001C3474.bin
        INCBIN  build\mapcontainer\map_001C3474_001C355C.bin
        INCBIN  build\mapcontainer\map_001C355C_001C357C.bin
        INCBIN  build\mapcontainer\map_001C357C_001C3628.bin
        INCBIN  build\mapcontainer\map_001C3628_001C3648.bin
        INCBIN  build\mapcontainer\map_001C3648_001C3924.bin
        INCBIN  build\mapcontainer\map_001C3924_001C394C.bin
        INCBIN  build\mapcontainer\map_001C394C_001C3A70.bin
|map_anim_row_081C3A70|
|unk_081C3A70|
	DCB 0x04,0x03
	DCW 0x037d
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|map_anim_row_081C3A84|
|unk_081C3A84|
	DCB 0x10,0x04
	DCW 0x0379
	DCD 0x081abf28,0x081abf8c,0x081abff0,0x081ac050,0x081abf28,0x081abf8c,0x081ac0b4,0x081abf8c
	DCD 0x081ac118,0x081abf8c,0x081ac17c,0x081ac050,0x081ac17c,0x081ac050,0x081ac17c,0x081ac050
|unk_081C3AC8|
        INCBIN  build\animframe\gen_1c3ac8_1c3bb8.bin
|map_anim_row_081C3BB8|
|unk_081C3BB8|
	DCB 0x04,0x03
	DCW 0x0376
	DCD 0x081c3ac8,0x081c3af8,0x081c3b38,0x081c3b78
|map_anim_row_081C3BCC|
|unk_081C3BCC|
	DCB 0x02,0x02
	DCW 0x0374
	DCD 0x081911d8,0x08191214
|map_anim_row_081C3BD8|
|unk_081C3BD8|
	DCB 0x02,0x01
	DCW 0x0373
	DCD 0x08191288,0x0819125c
|unk_081C3BE4|
        INCBIN  baserom.gba_0x1c3be4_0x1c3bf8.extracted
|unk_081C3BF8|
        INCBIN  build\mapcontainer\map_001C3BF8_001C3C28.bin
|unk_081C3C28|
        INCBIN  build\mapcontainer\map_001C3C28_001C3C30.bin
        INCBIN  build\mapcontainer\map_001C3C30_001C3C80.bin
        INCBIN  build\mapcontainer\map_001C3C80_001C3DFC.bin
        INCBIN  build\mapcontainer\map_001C3DFC_001C3E1C.bin
        INCBIN  build\mapcontainer\map_001C3E1C_001C3EEC.bin
        INCBIN  build\mapcontainer\map_001C3EEC_001C3F0C.bin
        INCBIN  build\mapcontainer\map_001C3F0C_001C4008.bin
        INCBIN  build\mapcontainer\map_001C4008_001C4028.bin
        INCBIN  build\mapcontainer\map_001C4028_001C420C.bin
        INCBIN  build\mapcontainer\map_001C420C_001C422C.bin
        INCBIN  build\mapcontainer\map_001C422C_001C4348.bin
|unk_081C4348|
        INCBIN  build\mapcontainer\map_001C4348_001C4410.bin
|unk_081C4410|
        INCBIN  build\mapcontainer\map_001C4410_001C4418.bin
        INCBIN  build\mapcontainer\map_001C4418_001C4468.bin
        INCBIN  build\mapcontainer\map_001C4468_001C4644.bin
        INCBIN  build\mapcontainer\map_001C4644_001C466C.bin
        INCBIN  build\mapcontainer\map_001C466C_001C4780.bin
        INCBIN  build\mapcontainer\map_001C4780_001C47A0.bin
        INCBIN  build\mapcontainer\map_001C47A0_001C4A10.bin
        INCBIN  build\mapcontainer\map_001C4A10_001C4A38.bin
        INCBIN  build\mapcontainer\map_001C4A38_001C4C60.bin
        INCBIN  build\mapcontainer\map_001C4C60_001C4C88.bin
        INCBIN  build\mapcontainer\map_001C4C88_001C4DC4.bin
|unk_081C4DC4|
        INCBIN  build\mapcontainer\map_001C4DC4_001C4DDC.bin
|unk_081C4DDC|
        INCBIN  build\mapcontainer\map_001C4DDC_001C4ED4.bin
|unk_081C4ED4|
        INCBIN  build\mapcontainer\map_001C4ED4_001C4EE4.bin
        INCBIN  build\mapcontainer\map_001C4EE4_001C4F34.bin
        INCBIN  build\mapcontainer\map_001C4F34_001C5310.bin
        INCBIN  build\mapcontainer\map_001C5310_001C5338.bin
        INCBIN  build\mapcontainer\map_001C5338_001C54BC.bin
        INCBIN  build\mapcontainer\map_001C54BC_001C54E4.bin
        INCBIN  build\mapcontainer\map_001C54E4_001C5868.bin
        INCBIN  build\mapcontainer\map_001C5868_001C5890.bin
        INCBIN  build\mapcontainer\map_001C5890_001C5E9C.bin
        INCBIN  build\mapcontainer\map_001C5E9C_001C5EC4.bin
        INCBIN  build\mapcontainer\map_001C5EC4_001C6064.bin
|unk_081C6064|
        INCBIN  build\mapcontainer\map_001C6064_001C6174.bin
|unk_081C6174|
        INCBIN  build\mapcontainer\map_001C6174_001C6188.bin
        INCBIN  build\mapcontainer\map_001C6188_001C61D8.bin
        INCBIN  build\mapcontainer\map_001C61D8_001C6578.bin
        INCBIN  build\mapcontainer\map_001C6578_001C65A0.bin
        INCBIN  build\mapcontainer\map_001C65A0_001C6614.bin
        INCBIN  build\mapcontainer\map_001C6614_001C6634.bin
        INCBIN  build\mapcontainer\map_001C6634_001C6A60.bin
        INCBIN  build\mapcontainer\map_001C6A60_001C6A88.bin
        INCBIN  build\mapcontainer\map_001C6A88_001C6B90.bin
|unk_081C6B90|
        INCBIN  build\mapcontainer\map_001C6B90_001C6C28.bin
|unk_081C6C28|
        INCBIN  build\mapcontainer\map_001C6C28_001C6C30.bin
        INCBIN  build\mapcontainer\map_001C6C30_001C6C80.bin
        INCBIN  build\mapcontainer\map_001C6C80_001C7118.bin
        INCBIN  build\mapcontainer\map_001C7118_001C7140.bin
        INCBIN  build\mapcontainer\map_001C7140_001C7258.bin
        INCBIN  build\mapcontainer\map_001C7258_001C7280.bin
        INCBIN  build\mapcontainer\map_001C7280_001C7364.bin
        INCBIN  build\mapcontainer\map_001C7364_001C738C.bin
        INCBIN  build\mapcontainer\map_001C738C_001C7A10.bin
        INCBIN  build\mapcontainer\map_001C7A10_001C7A38.bin
        INCBIN  build\mapcontainer\map_001C7A38_001C7BE8.bin
|unk_081C7BE8|
        INCBIN  build\mapcontainer\map_001C7BE8_001C7C00.bin
        INCBIN  build\mapcontainer\map_001C7C00_001C7C48.bin
|map_anim_row_081C7C48|
|unk_081C7C48|
	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x081911d8,0x08191214
|map_anim_row_081C7C54|
|unk_081C7C54|
	DCB 0x10,0x0b
	DCW 0x0373
	DCD 0x0817a9ac,0x0817aaac,0x0817abac,0x0817aca4,0x0817a9ac,0x0817aaac,0x0817ada4,0x0817aaac
	DCD 0x0817aea4,0x0817aaac,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4
|unk_081C7C98|
        INCBIN  build\animframe\gen_1c7c98_1c7edc.bin
|map_anim_row_081C7EDC|
|unk_081C7EDC|
	DCB 0x04,0x0e
	DCW 0x0365
	DCD 0x081c7c98,0x081c7d5c,0x081c7e18,0x081c7d5c
|map_anim_row_081C7EF0|
|unk_081C7EF0|
	DCB 0x04,0x03
	DCW 0x0362
	DCD 0x0819b130,0x0819b0ac,0x0819b0d8,0x0819b104
|map_anim_row_081C7F04|
|unk_081C7F04|
	DCB 0x02,0x02
	DCW 0x0360
	DCD 0x081bfd60,0x081bfd9c
|unk_081C7F10|
        INCBIN  baserom.gba_0x1c7f10_0x1c7f24.extracted
|unk_081C7F24|
        INCBIN  build\mapcontainer\map_001C7F24_001C7F54.bin
|unk_081C7F54|
        INCBIN  build\mapcontainer\map_001C7F54_001C7F5C.bin
        INCBIN  build\mapcontainer\map_001C7F5C_001C7FAC.bin
        INCBIN  build\mapcontainer\map_001C7FAC_001C8240.bin
        INCBIN  build\mapcontainer\map_001C8240_001C8260.bin
        INCBIN  build\mapcontainer\map_001C8260_001C82F8.bin
        INCBIN  build\mapcontainer\map_001C82F8_001C8318.bin
        INCBIN  build\mapcontainer\map_001C8318_001C8774.bin
        INCBIN  build\mapcontainer\map_001C8774_001C8794.bin
        INCBIN  build\mapcontainer\map_001C8794_001C88D4.bin
|unk_081C88D4|
        INCBIN  build\mapcontainer\map_001C88D4_001C896C.bin
|unk_081C896C|
        INCBIN  build\mapcontainer\map_001C896C_001C8974.bin
        INCBIN  build\mapcontainer\map_001C8974_001C89C4.bin
        INCBIN  build\mapcontainer\map_001C89C4_001C8B44.bin
        INCBIN  build\mapcontainer\map_001C8B44_001C8B64.bin
        INCBIN  build\mapcontainer\map_001C8B64_001C8BC8.bin
        INCBIN  build\mapcontainer\map_001C8BC8_001C8BE8.bin
        INCBIN  build\mapcontainer\map_001C8BE8_001C8C74.bin
        INCBIN  build\mapcontainer\map_001C8C74_001C8C94.bin
        INCBIN  build\mapcontainer\map_001C8C94_001C9098.bin
        INCBIN  build\mapcontainer\map_001C9098_001C90B8.bin
        INCBIN  build\mapcontainer\map_001C90B8_001C91D8.bin
|unk_081C91D8|
        INCBIN  build\mapcontainer\map_001C91D8_001C9270.bin
|unk_081C9270|
        INCBIN  build\mapcontainer\map_001C9270_001C9278.bin
        INCBIN  build\mapcontainer\map_001C9278_001C92C8.bin
        INCBIN  build\mapcontainer\map_001C92C8_001C94E4.bin
        INCBIN  build\mapcontainer\map_001C94E4_001C9504.bin
        INCBIN  build\mapcontainer\map_001C9504_001C9544.bin
        INCBIN  build\mapcontainer\map_001C9544_001C9560.bin
        INCBIN  build\mapcontainer\map_001C9560_001C9624.bin
        INCBIN  build\mapcontainer\map_001C9624_001C9644.bin
        INCBIN  build\mapcontainer\map_001C9644_001C99C4.bin
        INCBIN  build\mapcontainer\map_001C99C4_001C99E4.bin
        INCBIN  build\mapcontainer\map_001C99E4_001C9B48.bin
|unk_081C9B48|
        INCBIN  build\mapcontainer\map_001C9B48_001C9BE0.bin
|unk_081C9BE0|
        INCBIN  build\mapcontainer\map_001C9BE0_001C9BE8.bin
        INCBIN  build\mapcontainer\map_001C9BE8_001C9C38.bin
        INCBIN  build\mapcontainer\map_001C9C38_001C9F58.bin
        INCBIN  build\mapcontainer\map_001C9F58_001C9F78.bin
        INCBIN  build\mapcontainer\map_001C9F78_001CA000.bin
        INCBIN  build\mapcontainer\map_001CA000_001CA020.bin
        INCBIN  build\mapcontainer\map_001CA020_001CA3E0.bin
        INCBIN  build\mapcontainer\map_001CA3E0_001CA400.bin
        INCBIN  build\mapcontainer\map_001CA400_001CA528.bin
|unk_081CA528|
        INCBIN  build\mapcontainer\map_001CA528_001CA5D8.bin
|unk_081CA5D8|
        INCBIN  build\mapcontainer\map_001CA5D8_001CA5E4.bin
        INCBIN  build\mapcontainer\map_001CA5E4_001CA634.bin
        INCBIN  build\mapcontainer\map_001CA634_001CAA10.bin
        INCBIN  build\mapcontainer\map_001CAA10_001CAA38.bin
        INCBIN  build\mapcontainer\map_001CAA38_001CAAF0.bin
        INCBIN  build\mapcontainer\map_001CAAF0_001CAB18.bin
        INCBIN  build\mapcontainer\map_001CAB18_001CAF58.bin
        INCBIN  build\mapcontainer\map_001CAF58_001CAF80.bin
        INCBIN  build\mapcontainer\map_001CAF80_001CB0CC.bin
|unk_081CB0CC|
        INCBIN  build\mapcontainer\map_001CB0CC_001CB164.bin
|unk_081CB164|
        INCBIN  build\mapcontainer\map_001CB164_001CB16C.bin
        INCBIN  build\mapcontainer\map_001CB16C_001CB1BC.bin
        INCBIN  build\mapcontainer\map_001CB1BC_001CB8FC.bin
        INCBIN  build\mapcontainer\map_001CB8FC_001CB944.bin
        INCBIN  build\mapcontainer\map_001CB944_001CBEB4.bin
        INCBIN  build\mapcontainer\map_001CBEB4_001CBF0C.bin
        INCBIN  build\mapcontainer\map_001CBF0C_001CC790.bin
        INCBIN  build\mapcontainer\map_001CC790_001CC7E8.bin
        INCBIN  build\mapcontainer\map_001CC7E8_001CDDE0.bin
        INCBIN  build\mapcontainer\map_001CDDE0_001CDE38.bin
        INCBIN  build\mapcontainer\map_001CDE38_001CDF74.bin
|unk_081CDF74|
        INCBIN  build\mapcontainer\map_001CDF74_001CE034.bin
        INCBIN  build\mapcontainer\map_001CE034_001CE30C.bin
|unk_081CE30C|
        INCBIN  build\mapcontainer\map_001CE30C_001CE3A4.bin
|unk_081CE3A4|
        INCBIN  build\mapcontainer\map_001CE3A4_001CE3AC.bin
        INCBIN  build\mapcontainer\map_001CE3AC_001CE3FC.bin
        INCBIN  build\mapcontainer\map_001CE3FC_001CE620.bin
        INCBIN  build\mapcontainer\map_001CE620_001CE640.bin
        INCBIN  build\mapcontainer\map_001CE640_001CE6A8.bin
        INCBIN  build\mapcontainer\map_001CE6A8_001CE6C8.bin
        INCBIN  build\mapcontainer\map_001CE6C8_001CE8A4.bin
        INCBIN  build\mapcontainer\map_001CE8A4_001CE8C4.bin
        INCBIN  build\mapcontainer\map_001CE8C4_001CEB1C.bin
        INCBIN  build\mapcontainer\map_001CEB1C_001CEB3C.bin
        INCBIN  build\mapcontainer\map_001CEB3C_001CEBD4.bin
|unk_081CEBD4|
        INCBIN  build\mapcontainer\map_001CEBD4_001CEC94.bin
        INCBIN  build\mapcontainer\map_001CEC94_001CED8C.bin
|unk_081CED8C|
        INCBIN  build\mapcontainer\map_001CED8C_001CEDA4.bin
|unk_081CEDA4|
        INCBIN  build\mapcontainer\map_001CEDA4_001CEDA8.bin
        INCBIN  build\mapcontainer\map_001CEDA8_001CEDF8.bin
        INCBIN  build\mapcontainer\map_001CEDF8_001CF014.bin
        INCBIN  build\mapcontainer\map_001CF014_001CF03C.bin
        INCBIN  build\mapcontainer\map_001CF03C_001CF218.bin
        INCBIN  build\mapcontainer\map_001CF218_001CF238.bin
        INCBIN  build\mapcontainer\map_001CF238_001CF550.bin
        INCBIN  build\mapcontainer\map_001CF550_001CF578.bin
        INCBIN  build\mapcontainer\map_001CF578_001CF63C.bin
|unk_081CF63C|
        INCBIN  build\mapcontainer\map_001CF63C_001CF66C.bin
        INCBIN  build\mapcontainer\map_001CF66C_001CF9D4.bin
|unk_081CF9D4|
        INCBIN  build\mapcontainer\map_001CF9D4_001CFA04.bin
|unk_081CFA04|
        INCBIN  build\mapcontainer\map_001CFA04_001CFA0C.bin
        INCBIN  build\mapcontainer\map_001CFA0C_001CFA5C.bin
        INCBIN  build\mapcontainer\map_001CFA5C_001CFC2C.bin
        INCBIN  build\mapcontainer\map_001CFC2C_001CFC4C.bin
        INCBIN  build\mapcontainer\map_001CFC4C_001CFC88.bin
        INCBIN  build\mapcontainer\map_001CFC88_001CFCA4.bin
        INCBIN  build\mapcontainer\map_001CFCA4_001CFD70.bin
        INCBIN  build\mapcontainer\map_001CFD70_001CFD90.bin
        INCBIN  build\mapcontainer\map_001CFD90_001D00A0.bin
        INCBIN  build\mapcontainer\map_001D00A0_001D00C0.bin
        INCBIN  build\mapcontainer\map_001D00C0_001D0184.bin
|unk_081D0184|
        INCBIN  build\mapcontainer\map_001D0184_001D01B4.bin
|unk_081D01B4|
        INCBIN  build\mapcontainer\map_001D01B4_001D01BC.bin
        INCBIN  build\mapcontainer\map_001D01BC_001D020C.bin
        INCBIN  build\mapcontainer\map_001D020C_001D03B8.bin
        INCBIN  build\mapcontainer\map_001D03B8_001D03D8.bin
        INCBIN  build\mapcontainer\map_001D03D8_001D0570.bin
        INCBIN  build\mapcontainer\map_001D0570_001D0590.bin
        INCBIN  build\mapcontainer\map_001D0590_001D081C.bin
        INCBIN  build\mapcontainer\map_001D081C_001D083C.bin
        INCBIN  build\mapcontainer\map_001D083C_001D08EC.bin
|unk_081D08EC|
        INCBIN  build\mapcontainer\map_001D08EC_001D091C.bin
        INCBIN  build\mapcontainer\map_001D091C_001D09E4.bin
|unk_081D09E4|
        INCBIN  build\mapcontainer\map_001D09E4_001D0A14.bin
|unk_081D0A14|
        INCBIN  build\mapcontainer\map_001D0A14_001D0A1C.bin
        INCBIN  build\mapcontainer\map_001D0A1C_001D0A6C.bin
        INCBIN  build\mapcontainer\map_001D0A6C_001D0C58.bin
        INCBIN  build\mapcontainer\map_001D0C58_001D0C80.bin
        INCBIN  build\mapcontainer\map_001D0C80_001D0D2C.bin
        INCBIN  build\mapcontainer\map_001D0D2C_001D0D4C.bin
        INCBIN  build\mapcontainer\map_001D0D4C_001D11A8.bin
        INCBIN  build\mapcontainer\map_001D11A8_001D11D0.bin
        INCBIN  build\mapcontainer\map_001D11D0_001D1298.bin
|unk_081D1298|
        INCBIN  build\mapcontainer\map_001D1298_001D1328.bin
        INCBIN  build\mapcontainer\map_001D1328_001D146C.bin
|unk_081D146C|
        INCBIN  build\mapcontainer\map_001D146C_001D149C.bin
|unk_081D149C|
        INCBIN  build\mapcontainer\map_001D149C_001D14A4.bin
        INCBIN  build\mapcontainer\map_001D14A4_001D14F4.bin
        INCBIN  build\mapcontainer\map_001D14F4_001D16F8.bin
        INCBIN  build\mapcontainer\map_001D16F8_001D1720.bin
        INCBIN  build\mapcontainer\map_001D1720_001D1770.bin
        INCBIN  build\mapcontainer\map_001D1770_001D1790.bin
        INCBIN  build\mapcontainer\map_001D1790_001D18E8.bin
        INCBIN  build\mapcontainer\map_001D18E8_001D1908.bin
        INCBIN  build\mapcontainer\map_001D1908_001D1B80.bin
        INCBIN  build\mapcontainer\map_001D1B80_001D1BA8.bin
        INCBIN  build\mapcontainer\map_001D1BA8_001D1C74.bin
|unk_081D1C74|
        INCBIN  build\mapcontainer\map_001D1C74_001D1CBC.bin
|unk_081D1CBC|
        INCBIN  build\mapcontainer\map_001D1CBC_001D1CC8.bin
        INCBIN  build\mapcontainer\map_001D1CC8_001D1D18.bin
        INCBIN  build\mapcontainer\map_001D1D18_001D1D70.bin
        INCBIN  build\mapcontainer\map_001D1D70_001D1D90.bin
        INCBIN  build\mapcontainer\map_001D1D90_001D1FFC.bin
        INCBIN  build\mapcontainer\map_001D1FFC_001D201C.bin
        INCBIN  build\mapcontainer\map_001D201C_001D21BC.bin
        INCBIN  build\mapcontainer\map_001D21BC_001D21DC.bin
        INCBIN  build\mapcontainer\map_001D21DC_001D2504.bin
        INCBIN  build\mapcontainer\map_001D2504_001D2524.bin
        INCBIN  build\mapcontainer\map_001D2524_001D25E8.bin
        INCLUDE rawlabeled_1d25e8.s
        INCBIN  build\mapcontainer\map_001D2798_001D27E8.bin
        INCBIN  build\mapcontainer\map_001D27E8_001D2928.bin
        INCBIN  build\mapcontainer\map_001D2928_001D2944.bin
        INCBIN  build\mapcontainer\map_001D2944_001D2A74.bin
        INCBIN  build\mapcontainer\map_001D2A74_001D2A90.bin
        INCBIN  build\mapcontainer\map_001D2A90_001D2B60.bin
        INCBIN  build\mapcontainer\map_001D2B60_001D2B7C.bin
        INCBIN  build\mapcontainer\map_001D2B7C_001D2C28.bin
|unk_081D2C28|
        INCBIN  build\mapcontainer\map_001D2C28_001D2C40.bin
|unk_081D2C40|
        INCBIN  build\mapcontainer\map_001D2C40_001D2C44.bin
        INCBIN  build\mapcontainer\map_001D2C44_001D2C94.bin
        INCBIN  build\mapcontainer\map_001D2C94_001D2FC0.bin
        INCBIN  build\mapcontainer\map_001D2FC0_001D3000.bin
        INCBIN  build\mapcontainer\map_001D3000_001D3138.bin
        INCBIN  build\mapcontainer\map_001D3138_001D3170.bin
        INCBIN  build\mapcontainer\map_001D3170_001D3A20.bin
        INCBIN  build\mapcontainer\map_001D3A20_001D3A60.bin
        INCBIN  build\mapcontainer\map_001D3A60_001D3C60.bin
        INCBIN  build\mapcontainer\map_001D3C60_001D3CA0.bin
        INCBIN  build\mapcontainer\map_001D3CA0_001D3D38.bin
|unk_081D3D38|
        INCBIN  build\mapcontainer\map_001D3D38_001D3D68.bin
|unk_081D3D68|
        INCBIN  build\mapcontainer\map_001D3D68_001D3DB0.bin
|unk_081D3DB0|
        INCBIN  build\mapcontainer\map_001D3DB0_001D3DBC.bin
        INCBIN  build\mapcontainer\map_001D3DBC_001D3E0C.bin
        INCBIN  build\mapcontainer\map_001D3E0C_001D4070.bin
        INCBIN  build\mapcontainer\map_001D4070_001D4098.bin
        INCBIN  build\mapcontainer\map_001D4098_001D41FC.bin
        INCBIN  build\mapcontainer\map_001D41FC_001D421C.bin
        INCBIN  build\mapcontainer\map_001D421C_001D44E0.bin
        INCBIN  build\mapcontainer\map_001D44E0_001D4508.bin
        INCBIN  build\mapcontainer\map_001D4508_001D45F0.bin
|unk_081D45F0|
        INCBIN  build\mapcontainer\map_001D45F0_001D4638.bin
        INCBIN  build\mapcontainer\map_001D4638_001D482C.bin
|unk_081D482C|
        INCBIN  build\mapcontainer\map_001D482C_001D488C.bin
|unk_081D488C|
        INCBIN  build\mapcontainer\map_001D488C_001D489C.bin
        INCBIN  build\mapcontainer\map_001D489C_001D48EC.bin
        INCBIN  build\mapcontainer\map_001D48EC_001D4A80.bin
        INCBIN  build\mapcontainer\map_001D4A80_001D4AA0.bin
        INCBIN  build\mapcontainer\map_001D4AA0_001D4ACC.bin
        INCBIN  build\mapcontainer\map_001D4ACC_001D4AE8.bin
        INCBIN  build\mapcontainer\map_001D4AE8_001D4BD0.bin
        INCBIN  build\mapcontainer\map_001D4BD0_001D4BF0.bin
        INCBIN  build\mapcontainer\map_001D4BF0_001D4D7C.bin
        INCBIN  build\mapcontainer\map_001D4D7C_001D4D9C.bin
        INCBIN  build\mapcontainer\map_001D4D9C_001D4E44.bin
        INCLUDE rawlabeled_1d4e44.s
        INCBIN  build\mapcontainer\map_001D4EA4_001D4EF4.bin
        INCBIN  build\mapcontainer\map_001D4EF4_001D5098.bin
        INCBIN  build\mapcontainer\map_001D5098_001D50B8.bin
        INCBIN  build\mapcontainer\map_001D50B8_001D51A0.bin
        INCBIN  build\mapcontainer\map_001D51A0_001D51C0.bin
        INCBIN  build\mapcontainer\map_001D51C0_001D53B0.bin
        INCBIN  build\mapcontainer\map_001D53B0_001D53D0.bin
        INCBIN  build\mapcontainer\map_001D53D0_001D5480.bin
|unk_081D5480|
        INCBIN  build\mapcontainer\map_001D5480_001D54B0.bin
|unk_081D54B0|
        INCBIN  build\mapcontainer\map_001D54B0_001D54B8.bin
        INCBIN  build\mapcontainer\map_001D54B8_001D5508.bin
        INCBIN  build\mapcontainer\map_001D5508_001D5680.bin
        INCBIN  build\mapcontainer\map_001D5680_001D56A0.bin
        INCBIN  build\mapcontainer\map_001D56A0_001D57F0.bin
        INCBIN  build\mapcontainer\map_001D57F0_001D5810.bin
        INCBIN  build\mapcontainer\map_001D5810_001D59B0.bin
        INCBIN  build\mapcontainer\map_001D59B0_001D59D0.bin
        INCBIN  build\mapcontainer\map_001D59D0_001D5A9C.bin
|unk_081D5A9C|
        INCBIN  build\mapcontainer\map_001D5A9C_001D5ACC.bin
|unk_081D5ACC|
        INCBIN  build\mapcontainer\map_001D5ACC_001D5AD4.bin
        INCBIN  build\mapcontainer\map_001D5AD4_001D5B24.bin
        INCBIN  build\mapcontainer\map_001D5B24_001D5CB0.bin
        INCBIN  build\mapcontainer\map_001D5CB0_001D5CD0.bin
        INCBIN  build\mapcontainer\map_001D5CD0_001D5D78.bin
        INCBIN  build\mapcontainer\map_001D5D78_001D5D94.bin
        INCBIN  build\mapcontainer\map_001D5D94_001D5F74.bin
        INCBIN  build\mapcontainer\map_001D5F74_001D5F94.bin
        INCBIN  build\mapcontainer\map_001D5F94_001D606C.bin
        INCLUDE rawlabeled_1d606c.s
        INCBIN  build\mapcontainer\map_001D60DC_001D612C.bin
        INCBIN  build\mapcontainer\map_001D612C_001D62CC.bin
        INCBIN  build\mapcontainer\map_001D62CC_001D62EC.bin
        INCBIN  build\mapcontainer\map_001D62EC_001D6328.bin
        INCBIN  build\mapcontainer\map_001D6328_001D6344.bin
        INCBIN  build\mapcontainer\map_001D6344_001D64B4.bin
        INCBIN  build\mapcontainer\map_001D64B4_001D64D4.bin
        INCBIN  build\mapcontainer\map_001D64D4_001D67F8.bin
        INCBIN  build\mapcontainer\map_001D67F8_001D6818.bin
        INCBIN  build\mapcontainer\map_001D6818_001D68F4.bin
|unk_081D68F4|
        INCBIN  build\mapcontainer\map_001D68F4_001D693C.bin
|unk_081D693C|
        INCBIN  build\mapcontainer\map_001D693C_001D6948.bin
        INCBIN  build\mapcontainer\map_001D6948_001D6998.bin
        INCBIN  build\mapcontainer\map_001D6998_001D6C2C.bin
        INCBIN  build\mapcontainer\map_001D6C2C_001D6C5C.bin
        INCBIN  build\mapcontainer\map_001D6C5C_001D6CC4.bin
        INCBIN  build\mapcontainer\map_001D6CC4_001D6CE4.bin
        INCBIN  build\mapcontainer\map_001D6CE4_001D7050.bin
        INCBIN  build\mapcontainer\map_001D7050_001D7088.bin
        INCBIN  build\mapcontainer\map_001D7088_001D7174.bin
        INCLUDE rawlabeled_1d7174.s
        INCBIN  build\mapcontainer\map_001D71D4_001D7224.bin
        INCBIN  build\mapcontainer\map_001D7224_001D7310.bin
        INCBIN  build\mapcontainer\map_001D7310_001D7338.bin
        INCBIN  build\mapcontainer\map_001D7338_001D7648.bin
        INCBIN  build\mapcontainer\map_001D7648_001D7678.bin
        INCBIN  build\mapcontainer\map_001D7678_001D78D4.bin
        INCBIN  build\mapcontainer\map_001D78D4_001D7904.bin
        INCBIN  build\mapcontainer\map_001D7904_001D7C84.bin
        INCBIN  build\mapcontainer\map_001D7C84_001D7CB4.bin
        INCBIN  build\mapcontainer\map_001D7CB4_001D7DA8.bin
|unk_081D7DA8|
        INCBIN  build\mapcontainer\map_001D7DA8_001D7E00.bin
|unk_081D7E00|
        INCBIN  build\mapcontainer\map_001D7E00_001D7E08.bin
        INCBIN  build\mapcontainer\map_001D7E08_001D7E58.bin
        INCBIN  build\mapcontainer\map_001D7E58_001D7FF0.bin
        INCBIN  build\mapcontainer\map_001D7FF0_001D8010.bin
        INCBIN  build\mapcontainer\map_001D8010_001D819C.bin
        INCBIN  build\mapcontainer\map_001D819C_001D81BC.bin
        INCBIN  build\mapcontainer\map_001D81BC_001D8268.bin
        INCBIN  build\mapcontainer\map_001D8268_001D8284.bin
        INCBIN  build\mapcontainer\map_001D8284_001D8490.bin
        INCBIN  build\mapcontainer\map_001D8490_001D84B0.bin
        INCBIN  build\mapcontainer\map_001D84B0_001D857C.bin
        INCLUDE rawlabeled_1d857c.s
        INCBIN  build\mapcontainer\map_001D85B4_001D8604.bin
        INCBIN  build\mapcontainer\map_001D8604_001D8950.bin
        INCBIN  build\mapcontainer\map_001D8950_001D8980.bin
        INCBIN  build\mapcontainer\map_001D8980_001D89C8.bin
        INCBIN  build\mapcontainer\map_001D89C8_001D89E8.bin
        INCBIN  build\mapcontainer\map_001D89E8_001D8C34.bin
        INCBIN  build\mapcontainer\map_001D8C34_001D8C64.bin
        INCBIN  build\mapcontainer\map_001D8C64_001D9298.bin
        INCBIN  build\mapcontainer\map_001D9298_001D92D0.bin
        INCBIN  build\mapcontainer\map_001D92D0_001D93EC.bin
|unk_081D93EC|
        INCBIN  build\mapcontainer\map_001D93EC_001D9524.bin
        INCBIN  build\mapcontainer\map_001D9524_001D9674.bin
|unk_081D9674|
        INCBIN  build\mapcontainer\map_001D9674_001D96A4.bin
|unk_081D96A4|
        INCBIN  build\mapcontainer\map_001D96A4_001D96AC.bin
        INCBIN  build\mapcontainer\map_001D96AC_001D96FC.bin
        INCBIN  build\mapcontainer\map_001D96FC_001D9840.bin
        INCBIN  build\mapcontainer\map_001D9840_001D9860.bin
        INCBIN  build\mapcontainer\map_001D9860_001D9898.bin
        INCBIN  build\mapcontainer\map_001D9898_001D98B4.bin
        INCBIN  build\mapcontainer\map_001D98B4_001D9A80.bin
        INCBIN  build\mapcontainer\map_001D9A80_001D9AA0.bin
        INCBIN  build\mapcontainer\map_001D9AA0_001D9C6C.bin
        INCBIN  build\mapcontainer\map_001D9C6C_001D9C8C.bin
        INCBIN  build\mapcontainer\map_001D9C8C_001D9D54.bin
|unk_081D9D54|
        INCBIN  build\mapcontainer\map_001D9D54_001D9D9C.bin
        INCBIN  build\mapcontainer\map_001D9D9C_001D9FE0.bin
|unk_081D9FE0|
        INCBIN  build\mapcontainer\map_001D9FE0_001D9FF8.bin
|unk_081D9FF8|
        INCBIN  build\mapcontainer\map_001D9FF8_001D9FFC.bin
        INCBIN  build\mapcontainer\map_001D9FFC_001DA04C.bin
        INCBIN  build\mapcontainer\map_001DA04C_001DA23C.bin
        INCBIN  build\mapcontainer\map_001DA23C_001DA264.bin
        INCBIN  build\mapcontainer\map_001DA264_001DA354.bin
        INCBIN  build\mapcontainer\map_001DA354_001DA370.bin
        INCBIN  build\mapcontainer\map_001DA370_001DA6BC.bin
        INCBIN  build\mapcontainer\map_001DA6BC_001DA6E4.bin
        INCBIN  build\mapcontainer\map_001DA6E4_001DA7B0.bin
|unk_081DA7B0|
        INCBIN  build\mapcontainer\map_001DA7B0_001DA840.bin
        INCBIN  build\mapcontainer\map_001DA840_001DAC90.bin
|unk_081DAC90|
        INCBIN  build\mapcontainer\map_001DAC90_001DAD00.bin
|unk_081DAD00|
        INCBIN  build\mapcontainer\map_001DAD00_001DAD0C.bin
        INCBIN  build\mapcontainer\map_001DAD0C_001DAD5C.bin
        INCBIN  build\mapcontainer\map_001DAD5C_001DAFBC.bin
        INCBIN  build\mapcontainer\map_001DAFBC_001DAFDC.bin
        INCBIN  build\mapcontainer\map_001DAFDC_001DB04C.bin
        INCBIN  build\mapcontainer\map_001DB04C_001DB06C.bin
        INCBIN  build\mapcontainer\map_001DB06C_001DB0F4.bin
        INCBIN  build\mapcontainer\map_001DB0F4_001DB114.bin
        INCBIN  build\mapcontainer\map_001DB114_001DB274.bin
        INCBIN  build\mapcontainer\map_001DB274_001DB294.bin
        INCBIN  build\mapcontainer\map_001DB294_001DB334.bin
|unk_081DB334|
        INCBIN  build\mapcontainer\map_001DB334_001DB34C.bin
        INCBIN  build\mapcontainer\map_001DB34C_001DB374.bin
|unk_081DB374|
        INCBIN  build\mapcontainer\map_001DB374_001DB3A4.bin
|unk_081DB3A4|
        INCBIN  build\mapcontainer\map_001DB3A4_001DB3AC.bin
        INCBIN  build\mapcontainer\map_001DB3AC_001DB3FC.bin
        INCBIN  build\mapcontainer\map_001DB3FC_001DB450.bin
        INCBIN  build\mapcontainer\map_001DB450_001DB46C.bin
        INCBIN  build\mapcontainer\map_001DB46C_001DB668.bin
        INCBIN  build\mapcontainer\map_001DB668_001DB690.bin
        INCBIN  build\mapcontainer\map_001DB690_001DB870.bin
        INCBIN  build\mapcontainer\map_001DB870_001DB890.bin
        INCBIN  build\mapcontainer\map_001DB890_001DBBDC.bin
        INCBIN  build\mapcontainer\map_001DBBDC_001DBC04.bin
        INCBIN  build\mapcontainer\map_001DBC04_001DBCE0.bin
|unk_081DBCE0|
        INCBIN  build\mapcontainer\map_001DBCE0_001DBD28.bin
|unk_081DBD28|
        INCBIN  build\mapcontainer\map_001DBD28_001DBD34.bin
        INCBIN  build\mapcontainer\map_001DBD34_001DBD84.bin
        INCBIN  build\mapcontainer\map_001DBD84_001DBFD4.bin
        INCBIN  build\mapcontainer\map_001DBFD4_001DC004.bin
        INCBIN  build\mapcontainer\map_001DC004_001DC420.bin
        INCBIN  build\mapcontainer\map_001DC420_001DC450.bin
        INCBIN  build\mapcontainer\map_001DC450_001DC7AC.bin
        INCBIN  build\mapcontainer\map_001DC7AC_001DC7DC.bin
        INCBIN  build\mapcontainer\map_001DC7DC_001DCB30.bin
        INCBIN  build\mapcontainer\map_001DCB30_001DCB60.bin
        INCBIN  build\mapcontainer\map_001DCB60_001DCCC8.bin
|unk_081DCCC8|
        INCBIN  build\mapcontainer\map_001DCCC8_001DCCE0.bin
        INCBIN  build\mapcontainer\map_001DCCE0_001DCD68.bin
|unk_081DCD68|
        INCBIN  build\mapcontainer\map_001DCD68_001DCD98.bin
|unk_081DCD98|
        INCBIN  build\mapcontainer\map_001DCD98_001DCDA0.bin
        INCBIN  build\mapcontainer\map_001DCDA0_001DCDF0.bin
        INCBIN  build\mapcontainer\map_001DCDF0_001DD07C.bin
        INCBIN  build\mapcontainer\map_001DD07C_001DD0A4.bin
        INCBIN  build\mapcontainer\map_001DD0A4_001DD320.bin
        INCBIN  build\mapcontainer\map_001DD320_001DD348.bin
        INCBIN  build\mapcontainer\map_001DD348_001DD4CC.bin
        INCBIN  build\mapcontainer\map_001DD4CC_001DD4F4.bin
        INCBIN  build\mapcontainer\map_001DD4F4_001DD778.bin
        INCBIN  build\mapcontainer\map_001DD778_001DD7A0.bin
        INCBIN  build\mapcontainer\map_001DD7A0_001DD900.bin
|unk_081DD900|
        INCBIN  build\mapcontainer\map_001DD900_001DD960.bin
        INCBIN  build\mapcontainer\map_001DD960_001DDBE4.bin
|unk_081DDBE4|
        INCBIN  build\mapcontainer\map_001DDBE4_001DDBFC.bin
|unk_081DDBFC|
        INCBIN  build\mapcontainer\map_001DDBFC_001DDC00.bin
        INCBIN  build\mapcontainer\map_001DDC00_001DDC50.bin
        INCBIN  build\mapcontainer\map_001DDC50_001DDEA8.bin
        INCBIN  build\mapcontainer\map_001DDEA8_001DDED0.bin
        INCBIN  build\mapcontainer\map_001DDED0_001DE1C8.bin
        INCBIN  build\mapcontainer\map_001DE1C8_001DE1F0.bin
        INCBIN  build\mapcontainer\map_001DE1F0_001DE910.bin
        INCBIN  build\mapcontainer\map_001DE910_001DE938.bin
        INCBIN  build\mapcontainer\map_001DE938_001DEA60.bin
        INCBIN  build\mapcontainer\map_001DEA60_001DEA80.bin
        INCBIN  build\mapcontainer\map_001DEA80_001DEB1C.bin
|unk_081DEB1C|
        INCBIN  build\mapcontainer\map_001DEB1C_001DEB94.bin
        INCBIN  build\mapcontainer\map_001DEB94_001DEF58.bin
|unk_081DEF58|
        INCBIN  build\mapcontainer\map_001DEF58_001DEF70.bin
|unk_081DEF70|
        INCBIN  build\mapcontainer\map_001DEF70_001DEF74.bin
        INCBIN  build\mapcontainer\map_001DEF74_001DEFC4.bin
        INCBIN  build\mapcontainer\map_001DEFC4_001DF33C.bin
        INCBIN  build\mapcontainer\map_001DF33C_001DF364.bin
        INCBIN  build\mapcontainer\map_001DF364_001DF654.bin
        INCBIN  build\mapcontainer\map_001DF654_001DF67C.bin
        INCBIN  build\mapcontainer\map_001DF67C_001DF9E8.bin
        INCBIN  build\mapcontainer\map_001DF9E8_001DFA10.bin
        INCBIN  build\mapcontainer\map_001DFA10_001DFDD8.bin
        INCBIN  build\mapcontainer\map_001DFDD8_001DFE00.bin
        INCBIN  build\mapcontainer\map_001DFE00_001DFF10.bin
|unk_081DFF10|
        INCBIN  build\mapcontainer\map_001DFF10_001DFF28.bin
|unk_081DFF28|
        INCBIN  build\mapcontainer\map_001DFF28_001DFF2C.bin
        INCBIN  build\mapcontainer\map_001DFF2C_001DFF7C.bin
        INCBIN  build\mapcontainer\map_001DFF7C_001E02D8.bin
        INCBIN  build\mapcontainer\map_001E02D8_001E0300.bin
        INCBIN  build\mapcontainer\map_001E0300_001E06B4.bin
        INCBIN  build\mapcontainer\map_001E06B4_001E06DC.bin
        INCBIN  build\mapcontainer\map_001E06DC_001E0AB0.bin
        INCBIN  build\mapcontainer\map_001E0AB0_001E0AD8.bin
        INCBIN  build\mapcontainer\map_001E0AD8_001E10A4.bin
        INCBIN  build\mapcontainer\map_001E10A4_001E10CC.bin
        INCBIN  build\mapcontainer\map_001E10CC_001E11E8.bin
|unk_081E11E8|
        INCBIN  build\mapcontainer\map_001E11E8_001E1260.bin
|unk_081E1260|
        INCBIN  build\mapcontainer\map_001E1260_001E1268.bin
        INCBIN  build\mapcontainer\map_001E1268_001E12B8.bin
        INCBIN  build\mapcontainer\map_001E12B8_001E1544.bin
        INCBIN  build\mapcontainer\map_001E1544_001E156C.bin
        INCBIN  build\mapcontainer\map_001E156C_001E18F8.bin
        INCBIN  build\mapcontainer\map_001E18F8_001E1918.bin
        INCBIN  build\mapcontainer\map_001E1918_001E1DA8.bin
        INCBIN  build\mapcontainer\map_001E1DA8_001E1DD0.bin
        INCBIN  build\mapcontainer\map_001E1DD0_001E239C.bin
        INCBIN  build\mapcontainer\map_001E239C_001E23C4.bin
        INCBIN  build\mapcontainer\map_001E23C4_001E24F4.bin
|unk_081E24F4|
        INCBIN  build\animframe\gen_1e24f4_1e2b58.bin
|unk_081E2B58|
        INCBIN  build\mapcontainer\map_001E2B58_001E2BD0.bin
|unk_081E2BD0|
        INCBIN  build\mapcontainer\map_001E2BD0_001E2BD8.bin
        INCBIN  build\mapcontainer\map_001E2BD8_001E2C28.bin
        INCBIN  build\mapcontainer\map_001E2C28_001E2E58.bin
        INCBIN  build\mapcontainer\map_001E2E58_001E2E78.bin
        INCBIN  build\mapcontainer\map_001E2E78_001E3238.bin
        INCBIN  build\mapcontainer\map_001E3238_001E3258.bin
        INCBIN  build\mapcontainer\map_001E3258_001E3458.bin
        INCBIN  build\mapcontainer\map_001E3458_001E3478.bin
        INCBIN  build\mapcontainer\map_001E3478_001E35AC.bin
        INCBIN  build\mapcontainer\map_001E35AC_001E35CC.bin
        INCBIN  build\mapcontainer\map_001E35CC_001E36CC.bin
|unk_081E36CC|
        INCBIN  build\mapcontainer\map_001E36CC_001E36E4.bin
        INCBIN  build\mapcontainer\map_001E36E4_001E3780.bin
|unk_081E3780|
        INCBIN  build\mapcontainer\map_001E3780_001E37B0.bin
|unk_081E37B0|
        INCBIN  build\mapcontainer\map_001E37B0_001E37B8.bin
        INCBIN  build\mapcontainer\map_001E37B8_001E3808.bin
        INCBIN  build\mapcontainer\map_001E3808_001E3974.bin
        INCBIN  build\mapcontainer\map_001E3974_001E3994.bin
        INCBIN  build\mapcontainer\map_001E3994_001E3C34.bin
        INCBIN  build\mapcontainer\map_001E3C34_001E3C54.bin
        INCBIN  build\mapcontainer\map_001E3C54_001E3E38.bin
        INCBIN  build\mapcontainer\map_001E3E38_001E3E58.bin
        INCBIN  build\mapcontainer\map_001E3E58_001E40C4.bin
        INCBIN  build\mapcontainer\map_001E40C4_001E40E4.bin
        INCBIN  build\mapcontainer\map_001E40E4_001E41E0.bin
        INCLUDE rawlabeled_1e41e0.s
        INCBIN  build\mapcontainer\map_001E4800_001E4850.bin
        INCBIN  build\mapcontainer\map_001E4850_001E4AD8.bin
        INCBIN  build\mapcontainer\map_001E4AD8_001E4B00.bin
        INCBIN  build\mapcontainer\map_001E4B00_001E539C.bin
        INCBIN  build\mapcontainer\map_001E539C_001E53C4.bin
        INCBIN  build\mapcontainer\map_001E53C4_001E5AB8.bin
        INCBIN  build\mapcontainer\map_001E5AB8_001E5AE0.bin
        INCBIN  build\mapcontainer\map_001E5AE0_001E63D8.bin
        INCBIN  build\mapcontainer\map_001E63D8_001E6400.bin
        INCBIN  build\mapcontainer\map_001E6400_001E6588.bin
|unk_081E6588|
        INCBIN  build\mapcontainer\map_001E6588_001E65B8.bin
        INCBIN  build\mapcontainer\map_001E65B8_001E6E2C.bin
|unk_081E6E2C|
        INCBIN  build\mapcontainer\map_001E6E2C_001E6EBC.bin
|unk_081E6EBC|
        INCBIN  build\mapcontainer\map_001E6EBC_001E6EC8.bin
        INCBIN  build\mapcontainer\map_001E6EC8_001E6F18.bin
        INCBIN  build\mapcontainer\map_001E6F18_001E7408.bin
        INCBIN  build\mapcontainer\map_001E7408_001E7430.bin
        INCBIN  build\mapcontainer\map_001E7430_001E7804.bin
        INCBIN  build\mapcontainer\map_001E7804_001E782C.bin
        INCBIN  build\mapcontainer\map_001E782C_001E7898.bin
|unk_081E7898|
        INCBIN  build\mapcontainer\map_001E7898_001E7910.bin
|unk_081E7910|
        INCBIN  build\mapcontainer\map_001E7910_001E7918.bin
        INCBIN  build\mapcontainer\map_001E7918_001E7968.bin
        INCBIN  build\mapcontainer\map_001E7968_001E79A8.bin
        INCBIN  build\mapcontainer\map_001E79A8_001E7B10.bin
        INCBIN  build\mapcontainer\map_001E7B10_001E7B50.bin
        INCBIN  build\mapcontainer\map_001E7B50_001E7B8C.bin
|unk_081E7B8C|
        INCBIN  build\mapcontainer\map_001E7B8C_001E7BD4.bin
        INCBIN  build\mapcontainer\map_001E7BD4_001E7D58.bin
|unk_081E7D58|
        INCBIN  build\mapcontainer\map_001E7D58_001E7D88.bin
|unk_081E7D88|
        INCBIN  build\mapcontainer\map_001E7D88_001E7D90.bin
        INCBIN  build\mapcontainer\map_001E7D90_001E7DE0.bin
        INCBIN  build\mapcontainer\map_001E7DE0_001E8114.bin
        INCBIN  build\mapcontainer\map_001E8114_001E813C.bin
        INCBIN  build\mapcontainer\map_001E813C_001E8428.bin
        INCBIN  build\mapcontainer\map_001E8428_001E8448.bin
        INCBIN  build\mapcontainer\map_001E8448_001E8948.bin
        INCBIN  build\mapcontainer\map_001E8948_001E8970.bin
        INCBIN  build\mapcontainer\map_001E8970_001E8F34.bin
        INCBIN  build\mapcontainer\map_001E8F34_001E8F5C.bin
        INCBIN  build\mapcontainer\map_001E8F5C_001E900C.bin
|unk_081E900C|
        INCBIN  build\mapcontainer\map_001E900C_001E9084.bin
|unk_081E9084|
        INCBIN  build\mapcontainer\map_001E9084_001E908C.bin
        INCBIN  build\mapcontainer\map_001E908C_001E90DC.bin
        INCBIN  build\mapcontainer\map_001E90DC_001E93C0.bin
        INCBIN  build\mapcontainer\map_001E93C0_001E93E8.bin
        INCBIN  build\mapcontainer\map_001E93E8_001E97D8.bin
        INCBIN  build\mapcontainer\map_001E97D8_001E9800.bin
        INCBIN  build\mapcontainer\map_001E9800_001E9C04.bin
        INCBIN  build\mapcontainer\map_001E9C04_001E9C2C.bin
        INCBIN  build\mapcontainer\map_001E9C2C_001EA1F4.bin
        INCBIN  build\mapcontainer\map_001EA1F4_001EA21C.bin
        INCBIN  build\mapcontainer\map_001EA21C_001EA2D8.bin
|unk_081EA2D8|
        INCBIN  build\animframe\gen_1ea2d8_1ea714.bin
|unk_081EA714|
        INCBIN  build\mapcontainer\map_001EA714_001EA78C.bin
|unk_081EA78C|
        INCBIN  build\mapcontainer\map_001EA78C_001EA794.bin
        INCBIN  build\mapcontainer\map_001EA794_001EA7E4.bin
        INCBIN  build\mapcontainer\map_001EA7E4_001EA824.bin
        INCBIN  build\mapcontainer\map_001EA824_001EA99C.bin
        INCBIN  build\mapcontainer\map_001EA99C_001EA9DC.bin
|unk_081EA9DC|
        INCBIN  build\mapcontainer\map_001EA9DC_001EAA0C.bin
|unk_081EAA0C|
        INCBIN  build\mapcontainer\map_001EAA0C_001EAA3C.bin
|unk_081EAA3C|
        INCBIN  build\mapcontainer\map_001EAA3C_001EAA44.bin
        INCBIN  build\mapcontainer\map_001EAA44_001EAA94.bin
        INCBIN  build\mapcontainer\map_001EAA94_001EB078.bin
        INCBIN  build\mapcontainer\map_001EB078_001EB0A0.bin
        INCBIN  build\mapcontainer\map_001EB0A0_001EB19C.bin
        INCBIN  build\mapcontainer\map_001EB19C_001EB1BC.bin
        INCBIN  build\mapcontainer\map_001EB1BC_001EB8C0.bin
        INCBIN  build\mapcontainer\map_001EB8C0_001EB8E8.bin
        INCBIN  build\mapcontainer\map_001EB8E8_001EBEB8.bin
        INCBIN  build\mapcontainer\map_001EBEB8_001EBEE0.bin
        INCBIN  build\mapcontainer\map_001EBEE0_001EC044.bin
|unk_081EC044|
        INCBIN  build\mapcontainer\map_001EC044_001EC0D4.bin
|unk_081EC0D4|
        INCBIN  build\mapcontainer\map_001EC0D4_001EC0E0.bin
        INCBIN  build\mapcontainer\map_001EC0E0_001EC130.bin
        INCBIN  build\mapcontainer\map_001EC130_001EC360.bin
        INCBIN  build\mapcontainer\map_001EC360_001EC380.bin
        INCBIN  build\mapcontainer\map_001EC380_001EC73C.bin
        INCBIN  build\mapcontainer\map_001EC73C_001EC75C.bin
        INCBIN  build\mapcontainer\map_001EC75C_001EC978.bin
        INCBIN  build\mapcontainer\map_001EC978_001EC9B8.bin
        INCBIN  build\mapcontainer\map_001EC9B8_001ECA40.bin
|unk_081ECA40|
        INCBIN  build\mapcontainer\map_001ECA40_001ECA70.bin
|unk_081ECA70|
        INCBIN  build\mapcontainer\map_001ECA70_001ECA78.bin
        INCBIN  build\mapcontainer\map_001ECA78_001ECAC8.bin
        INCBIN  build\mapcontainer\map_001ECAC8_001ECDE8.bin
        INCBIN  build\mapcontainer\map_001ECDE8_001ECE10.bin
        INCBIN  build\mapcontainer\map_001ECE10_001ED0D8.bin
        INCBIN  build\mapcontainer\map_001ED0D8_001ED0F8.bin
        INCBIN  build\mapcontainer\map_001ED0F8_001ED66C.bin
        INCBIN  build\mapcontainer\map_001ED66C_001ED694.bin
        INCBIN  build\mapcontainer\map_001ED694_001EDC5C.bin
        INCBIN  build\mapcontainer\map_001EDC5C_001EDC84.bin
        INCBIN  build\mapcontainer\map_001EDC84_001EDDA8.bin
|unk_081EDDA8|
        INCBIN  build\mapcontainer\map_001EDDA8_001EDE20.bin
|unk_081EDE20|
        INCBIN  build\mapcontainer\map_001EDE20_001EDE28.bin
        INCBIN  build\mapcontainer\map_001EDE28_001EDE78.bin
        INCBIN  build\mapcontainer\map_001EDE78_001EE178.bin
        INCBIN  build\mapcontainer\map_001EE178_001EE1A0.bin
        INCBIN  build\mapcontainer\map_001EE1A0_001EE5DC.bin
        INCBIN  build\mapcontainer\map_001EE5DC_001EE604.bin
        INCBIN  build\mapcontainer\map_001EE604_001EEA44.bin
        INCBIN  build\mapcontainer\map_001EEA44_001EEA6C.bin
        INCBIN  build\mapcontainer\map_001EEA6C_001EF034.bin
        INCBIN  build\mapcontainer\map_001EF034_001EF05C.bin
        INCBIN  build\mapcontainer\map_001EF05C_001EF1A8.bin
|unk_081EF1A8|
        INCBIN  build\mapcontainer\map_001EF1A8_001EF220.bin
|unk_081EF220|
        INCBIN  build\mapcontainer\map_001EF220_001EF228.bin
        INCBIN  build\mapcontainer\map_001EF228_001EF278.bin
        INCBIN  build\mapcontainer\map_001EF278_001EF4A8.bin
        INCBIN  build\mapcontainer\map_001EF4A8_001EF4C8.bin
        INCBIN  build\mapcontainer\map_001EF4C8_001EF880.bin
        INCBIN  build\mapcontainer\map_001EF880_001EF8A0.bin
        INCBIN  build\mapcontainer\map_001EF8A0_001EFA60.bin
        INCBIN  build\mapcontainer\map_001EFA60_001EFA80.bin
        INCBIN  build\mapcontainer\map_001EFA80_001EFBB4.bin
        INCBIN  build\mapcontainer\map_001EFBB4_001EFBD4.bin
        INCBIN  build\mapcontainer\map_001EFBD4_001EFC4C.bin
|unk_081EFC4C|
        INCBIN  build\mapcontainer\map_001EFC4C_001EFC7C.bin
|unk_081EFC7C|
        INCBIN  build\mapcontainer\map_001EFC7C_001EFC84.bin
        INCBIN  build\mapcontainer\map_001EFC84_001EFCD4.bin
        INCBIN  build\mapcontainer\map_001EFCD4_001F006C.bin
        INCBIN  build\mapcontainer\map_001F006C_001F0094.bin
        INCBIN  build\mapcontainer\map_001F0094_001F05DC.bin
        INCBIN  build\mapcontainer\map_001F05DC_001F05FC.bin
        INCBIN  build\mapcontainer\map_001F05FC_001F0B3C.bin
        INCBIN  build\mapcontainer\map_001F0B3C_001F0B64.bin
        INCBIN  build\mapcontainer\map_001F0B64_001F0DDC.bin
        INCBIN  build\mapcontainer\map_001F0DDC_001F0E04.bin
        INCBIN  build\mapcontainer\map_001F0E04_001F0F5C.bin
|unk_081F0F5C|
        INCBIN  build\mapcontainer\map_001F0F5C_001F0FEC.bin
|unk_081F0FEC|
        INCBIN  build\mapcontainer\map_001F0FEC_001F0FF8.bin
        INCBIN  build\mapcontainer\map_001F0FF8_001F1048.bin
        INCBIN  build\mapcontainer\map_001F1048_001F13BC.bin
        INCBIN  build\mapcontainer\map_001F13BC_001F13E4.bin
        INCBIN  build\mapcontainer\map_001F13E4_001F1498.bin
        INCBIN  build\mapcontainer\map_001F1498_001F14C0.bin
        INCBIN  build\mapcontainer\map_001F14C0_001F18D8.bin
        INCBIN  build\mapcontainer\map_001F18D8_001F1900.bin
        INCBIN  build\mapcontainer\map_001F1900_001F1D54.bin
        INCBIN  build\mapcontainer\map_001F1D54_001F1D7C.bin
        INCBIN  build\mapcontainer\map_001F1D7C_001F1E44.bin
|unk_081F1E44|
        INCBIN  build\mapcontainer\map_001F1E44_001F1EBC.bin
|unk_081F1EBC|
        INCBIN  build\mapcontainer\map_001F1EBC_001F1EC4.bin
        INCBIN  build\mapcontainer\map_001F1EC4_001F1F14.bin
        INCBIN  build\mapcontainer\map_001F1F14_001F1F54.bin
        INCBIN  build\mapcontainer\map_001F1F54_001F20C0.bin
        INCBIN  build\mapcontainer\map_001F20C0_001F2100.bin
|unk_081F2100|
        INCBIN  build\mapcontainer\map_001F2100_001F2118.bin
|unk_081F2118|
        INCBIN  build\mapcontainer\map_001F2118_001F2148.bin
|unk_081F2148|
        INCBIN  build\mapcontainer\map_001F2148_001F2150.bin
        INCBIN  build\mapcontainer\map_001F2150_001F21A0.bin
        INCBIN  build\mapcontainer\map_001F21A0_001F24A4.bin
        INCBIN  build\mapcontainer\map_001F24A4_001F24CC.bin
        INCBIN  build\mapcontainer\map_001F24CC_001F289C.bin
        INCBIN  build\mapcontainer\map_001F289C_001F28C4.bin
        INCBIN  build\mapcontainer\map_001F28C4_001F2E20.bin
        INCBIN  build\mapcontainer\map_001F2E20_001F2E48.bin
        INCBIN  build\mapcontainer\map_001F2E48_001F30C8.bin
        INCBIN  build\mapcontainer\map_001F30C8_001F30F0.bin
        INCBIN  build\mapcontainer\map_001F30F0_001F31F8.bin
|unk_081F31F8|
        INCBIN  build\mapcontainer\map_001F31F8_001F3270.bin
|unk_081F3270|
        INCBIN  build\mapcontainer\map_001F3270_001F3278.bin
        INCBIN  build\mapcontainer\map_001F3278_001F32C8.bin
        INCBIN  build\mapcontainer\map_001F32C8_001F353C.bin
        INCBIN  build\mapcontainer\map_001F353C_001F355C.bin
        INCBIN  build\mapcontainer\map_001F355C_001F36F8.bin
        INCBIN  build\mapcontainer\map_001F36F8_001F3718.bin
        INCBIN  build\mapcontainer\map_001F3718_001F3AC0.bin
        INCBIN  build\mapcontainer\map_001F3AC0_001F3AE0.bin
        INCBIN  build\mapcontainer\map_001F3AE0_001F3F9C.bin
        INCBIN  build\mapcontainer\map_001F3F9C_001F3FBC.bin
        INCBIN  build\mapcontainer\map_001F3FBC_001F40D8.bin
|unk_081F40D8|
        INCBIN  build\mapcontainer\map_001F40D8_001F4118.bin
|unk_081F4118|
        INCBIN  build\mapcontainer\map_001F4118_001F4120.bin
        INCBIN  build\mapcontainer\map_001F4120_001F4170.bin
        INCBIN  build\mapcontainer\map_001F4170_001F4440.bin
        INCBIN  build\mapcontainer\map_001F4440_001F4460.bin
        INCBIN  build\mapcontainer\map_001F4460_001F4830.bin
        INCBIN  build\mapcontainer\map_001F4830_001F4850.bin
        INCBIN  build\mapcontainer\map_001F4850_001F4C8C.bin
        INCBIN  build\mapcontainer\map_001F4C8C_001F4CAC.bin
        INCBIN  build\mapcontainer\map_001F4CAC_001F4EC4.bin
        INCBIN  build\mapcontainer\map_001F4EC4_001F4EE4.bin
        INCBIN  build\mapcontainer\map_001F4EE4_001F5028.bin
|unk_081F5028|
        INCBIN  build\animframe\gen_1f5028_1f50fc.bin
|unk_081F50FC|
        INCBIN  build\mapcontainer\map_001F50FC_001F513C.bin
|unk_081F513C|
        INCBIN  build\mapcontainer\map_001F513C_001F5144.bin
        INCBIN  build\mapcontainer\map_001F5144_001F5194.bin
        INCBIN  build\mapcontainer\map_001F5194_001F550C.bin
        INCBIN  build\mapcontainer\map_001F550C_001F5534.bin
        INCBIN  build\mapcontainer\map_001F5534_001F5940.bin
        INCBIN  build\mapcontainer\map_001F5940_001F5968.bin
        INCBIN  build\mapcontainer\map_001F5968_001F5F50.bin
        INCBIN  build\mapcontainer\map_001F5F50_001F5F78.bin
        INCBIN  build\mapcontainer\map_001F5F78_001F61CC.bin
        INCBIN  build\mapcontainer\map_001F61CC_001F61F4.bin
        INCBIN  build\mapcontainer\map_001F61F4_001F63B8.bin
|unk_081F63B8|
        INCBIN  build\mapcontainer\map_001F63B8_001F6430.bin
        INCBIN  build\mapcontainer\map_001F6430_001F6750.bin
|unk_081F6750|
        INCBIN  build\mapcontainer\map_001F6750_001F6778.bin
|unk_081F6778|
        INCBIN  build\mapcontainer\map_001F6778_001F677C.bin
        INCBIN  build\mapcontainer\map_001F677C_001F67CC.bin
        INCBIN  build\mapcontainer\map_001F67CC_001F68C4.bin
        INCBIN  build\mapcontainer\map_001F68C4_001F68EC.bin
        INCBIN  build\mapcontainer\map_001F68EC_001F6A74.bin
        INCBIN  build\mapcontainer\map_001F6A74_001F6A9C.bin
        INCBIN  build\mapcontainer\map_001F6A9C_001F6D64.bin
        INCBIN  build\mapcontainer\map_001F6D64_001F6D8C.bin
        INCBIN  build\mapcontainer\map_001F6D8C_001F6F7C.bin
        INCBIN  build\mapcontainer\map_001F6F7C_001F6F9C.bin
        INCBIN  build\mapcontainer\map_001F6F9C_001F7020.bin
|unk_081F7020|
        INCBIN  build\mapcontainer\map_001F7020_001F7050.bin
        INCBIN  build\mapcontainer\map_001F7050_001F71B4.bin
        INCBIN  build\mapcontainer\map_001F71B4_001F7204.bin
        INCBIN  build\mapcontainer\map_001F7204_001F72D8.bin
        INCBIN  build\mapcontainer\map_001F72D8_001F72F8.bin
        INCBIN  build\mapcontainer\map_001F72F8_001F7380.bin
        INCBIN  build\mapcontainer\map_001F7380_001F73A0.bin
        INCBIN  build\mapcontainer\map_001F73A0_001F7544.bin
        INCBIN  build\mapcontainer\map_001F7544_001F7564.bin
        INCBIN  build\mapcontainer\map_001F7564_001F7958.bin
        INCBIN  build\mapcontainer\map_001F7958_001F7974.bin
        INCBIN  build\mapcontainer\map_001F7974_001F79F4.bin
|unk_081F79F4|
        INCBIN  build\mapcontainer\map_001F79F4_001F7A0C.bin
        INCBIN  build\mapcontainer\map_001F7A0C_001F7AF4.bin
|unk_081F7AF4|
        INCBIN  build\mapcontainer\map_001F7AF4_001F7B0C.bin
|unk_081F7B0C|
        INCBIN  build\mapcontainer\map_001F7B0C_001F7B10.bin
        INCBIN  build\mapcontainer\map_001F7B10_001F7B60.bin
        INCBIN  build\mapcontainer\map_001F7B60_001F7BF0.bin
        INCBIN  build\mapcontainer\map_001F7BF0_001F7C10.bin
        INCBIN  build\mapcontainer\map_001F7C10_001F7DAC.bin
        INCBIN  build\mapcontainer\map_001F7DAC_001F7DD0.bin
        INCBIN  build\mapcontainer\map_001F7DD0_001F827C.bin
        INCBIN  build\mapcontainer\map_001F827C_001F82A0.bin
        INCBIN  build\mapcontainer\map_001F82A0_001F848C.bin
        INCBIN  build\mapcontainer\map_001F848C_001F84AC.bin
        INCBIN  build\mapcontainer\map_001F84AC_001F8548.bin
|unk_081F8548|
        INCBIN  build\mapcontainer\map_001F8548_001F8590.bin
        INCBIN  build\mapcontainer\map_001F8590_001F880C.bin
        INCLUDE rawlabeled_1f880c.s
        INCBIN  build\mapcontainer\map_001F88D8_001F8928.bin
        INCBIN  build\mapcontainer\map_001F8928_001F89B8.bin
        INCBIN  build\mapcontainer\map_001F89B8_001F89D4.bin
        INCBIN  build\mapcontainer\map_001F89D4_001F8A70.bin
        INCBIN  build\mapcontainer\map_001F8A70_001F8A8C.bin
        INCBIN  build\mapcontainer\map_001F8A8C_001F8B8C.bin
        INCBIN  build\mapcontainer\map_001F8B8C_001F8BA8.bin
        INCBIN  build\mapcontainer\map_001F8BA8_001F8C1C.bin
|unk_081F8C1C|
        INCBIN  build\mapcontainer\map_001F8C1C_001F8C34.bin
|unk_081F8C34|
        INCBIN  build\mapcontainer\map_001F8C34_001F8C4C.bin
|unk_081F8C4C|
        INCBIN  build\mapcontainer\map_001F8C4C_001F8C50.bin
        INCBIN  build\mapcontainer\map_001F8C50_001F8CA0.bin
        INCBIN  build\mapcontainer\map_001F8CA0_001F8D08.bin
        INCBIN  build\mapcontainer\map_001F8D08_001F8D28.bin
        INCBIN  build\mapcontainer\map_001F8D28_001F8DC4.bin
        INCBIN  build\mapcontainer\map_001F8DC4_001F8DE4.bin
        INCBIN  build\mapcontainer\map_001F8DE4_001F90A0.bin
        INCBIN  build\mapcontainer\map_001F90A0_001F90C0.bin
        INCBIN  build\mapcontainer\map_001F90C0_001F94B8.bin
        INCBIN  build\mapcontainer\map_001F94B8_001F94D4.bin
        INCBIN  build\mapcontainer\map_001F94D4_001F9518.bin
|unk_081F9518|
        INCBIN  build\mapcontainer\map_001F9518_001F95C0.bin
        INCBIN  build\mapcontainer\map_001F95C0_001F97EC.bin
|unk_081F97EC|
        INCBIN  build\mapcontainer\map_001F97EC_001F981C.bin
|unk_081F981C|
        INCBIN  build\mapcontainer\map_001F981C_001F9824.bin
        INCBIN  build\mapcontainer\map_001F9824_001F9874.bin
        INCBIN  build\mapcontainer\map_001F9874_001F98D0.bin
        INCBIN  build\mapcontainer\map_001F98D0_001F98F0.bin
        INCBIN  build\mapcontainer\map_001F98F0_001F9970.bin
        INCBIN  build\mapcontainer\map_001F9970_001F9990.bin
        INCBIN  build\mapcontainer\map_001F9990_001F9C4C.bin
        INCBIN  build\mapcontainer\map_001F9C4C_001F9C88.bin
        INCBIN  build\mapcontainer\map_001F9C88_001F9CD0.bin
|unk_081F9CD0|
        INCBIN  build\mapcontainer\map_001F9CD0_001F9D00.bin
|unk_081F9D00|
        INCBIN  build\mapcontainer\map_001F9D00_001F9D08.bin
        INCBIN  build\mapcontainer\map_001F9D08_001F9D58.bin
        INCBIN  build\mapcontainer\map_001F9D58_001F9DC8.bin
        INCBIN  build\mapcontainer\map_001F9DC8_001F9DE4.bin
        INCBIN  build\mapcontainer\map_001F9DE4_001F9ED0.bin
        INCBIN  build\mapcontainer\map_001F9ED0_001F9EEC.bin
        INCBIN  build\mapcontainer\map_001F9EEC_001F9F88.bin
        INCBIN  build\mapcontainer\map_001F9F88_001F9FA4.bin
        INCBIN  build\mapcontainer\map_001F9FA4_001FA008.bin
|unk_081FA008|
        INCBIN  build\mapcontainer\map_001FA008_001FA020.bin
|unk_081FA020|
        INCBIN  build\mapcontainer\map_001FA020_001FA038.bin
|unk_081FA038|
        INCBIN  build\mapcontainer\map_001FA038_001FA03C.bin
        INCBIN  build\mapcontainer\map_001FA03C_001FA08C.bin
        INCBIN  build\mapcontainer\map_001FA08C_001FA120.bin
        INCBIN  build\mapcontainer\map_001FA120_001FA13C.bin
        INCBIN  build\mapcontainer\map_001FA13C_001FA1D8.bin
        INCBIN  build\mapcontainer\map_001FA1D8_001FA1F4.bin
        INCBIN  build\mapcontainer\map_001FA1F4_001FA2F0.bin
        INCBIN  build\mapcontainer\map_001FA2F0_001FA30C.bin
        INCBIN  build\mapcontainer\map_001FA30C_001FA358.bin
|unk_081FA358|
        INCBIN  build\mapcontainer\map_001FA358_001FA370.bin
|unk_081FA370|
        INCBIN  build\mapcontainer\map_001FA370_001FA388.bin
|unk_081FA388|
        INCBIN  build\mapcontainer\map_001FA388_001FA38C.bin
        INCBIN  build\mapcontainer\map_001FA38C_001FA3DC.bin
        INCBIN  build\mapcontainer\map_001FA3DC_001FA458.bin
|unk_081FA458|
        INCBIN  build\mapcontainer\map_001FA458_001FA488.bin
|unk_081FA488|
        INCBIN  build\mapcontainer\map_001FA488_001FA490.bin
        INCBIN  build\mapcontainer\map_001FA490_001FA4E0.bin
        INCBIN  build\mapcontainer\map_001FA4E0_001FA55C.bin
|unk_081FA55C|
        INCBIN  build\mapcontainer\map_001FA55C_001FA58C.bin
|unk_081FA58C|
        INCBIN  build\mapcontainer\map_001FA58C_001FA594.bin
        INCBIN  build\mapcontainer\map_001FA594_001FA5E4.bin
        INCBIN  build\mapcontainer\map_001FA5E4_001FA650.bin
        INCBIN  build\mapcontainer\map_001FA650_001FA66C.bin
        INCBIN  build\mapcontainer\map_001FA66C_001FA758.bin
        INCBIN  build\mapcontainer\map_001FA758_001FA774.bin
        INCBIN  build\mapcontainer\map_001FA774_001FA808.bin
        INCBIN  build\mapcontainer\map_001FA808_001FA824.bin
|unk_081FA824|
        INCBIN  build\mapcontainer\map_001FA824_001FA83C.bin
|unk_081FA83C|
        INCBIN  build\mapcontainer\map_001FA83C_001FA854.bin
|unk_081FA854|
        INCBIN  build\mapcontainer\map_001FA854_001FA858.bin
        INCBIN  build\mapcontainer\map_001FA858_001FA8A8.bin
        INCBIN  build\mapcontainer\map_001FA8A8_001FA92C.bin
        INCBIN  build\mapcontainer\map_001FA92C_001FA948.bin
        INCBIN  build\mapcontainer\map_001FA948_001FAAA8.bin
        INCBIN  build\mapcontainer\map_001FAAA8_001FAAC4.bin
        INCBIN  build\mapcontainer\map_001FAAC4_001FAB3C.bin
|unk_081FAB3C|
        INCBIN  build\mapcontainer\map_001FAB3C_001FAB54.bin
|unk_081FAB54|
        INCBIN  build\mapcontainer\map_001FAB54_001FAB6C.bin
|unk_081FAB6C|
        INCBIN  build\mapcontainer\map_001FAB6C_001FAB70.bin
        INCBIN  build\mapcontainer\map_001FAB70_001FABC0.bin
        INCBIN  build\mapcontainer\map_001FABC0_001FAC40.bin
        INCBIN  build\mapcontainer\map_001FAC40_001FAC60.bin
        INCBIN  build\mapcontainer\map_001FAC60_001FACC0.bin
        INCBIN  build\mapcontainer\map_001FACC0_001FACE0.bin
        INCBIN  build\mapcontainer\map_001FACE0_001FAD00.bin
        INCBIN  build\mapcontainer\map_001FAD00_001FAD1C.bin
        INCBIN  build\mapcontainer\map_001FAD1C_001FAFE0.bin
        INCBIN  build\mapcontainer\map_001FAFE0_001FB000.bin
        INCBIN  build\mapcontainer\map_001FB000_001FB060.bin
|unk_081FB060|
        INCBIN  build\animframe\gen_1fb060_1fb0c8.bin
|map_anim_row_081FB0C8|
|unk_081FB0C8|
	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x081fb060,0x081fb094
|unk_081FB0D4|
        INCBIN  build\animframe\gen_1fb0d4_1fb334.bin
|map_anim_row_081FB334|
|unk_081FB334|
	DCB 0x02,0x0f
	DCW 0x036f
	DCD 0x081fb0d4,0x081fb204
|unk_081FB340|
        INCBIN  baserom.gba_0x1fb340_0x1fb348.extracted
|unk_081FB348|
        INCBIN  build\mapcontainer\map_001FB348_001FB378.bin
|unk_081FB378|
        INCBIN  build\mapcontainer\map_001FB378_001FB380.bin
        INCBIN  build\mapcontainer\map_001FB380_001FB3D0.bin
        INCBIN  build\mapcontainer\map_001FB3D0_001FB468.bin
        INCBIN  build\mapcontainer\map_001FB468_001FB488.bin
        INCBIN  build\mapcontainer\map_001FB488_001FB550.bin
        INCBIN  build\mapcontainer\map_001FB550_001FB570.bin
        INCBIN  build\mapcontainer\map_001FB570_001FB7E8.bin
        INCBIN  build\mapcontainer\map_001FB7E8_001FB808.bin
        INCBIN  build\mapcontainer\map_001FB808_001FBB7C.bin
        INCBIN  build\mapcontainer\map_001FBB7C_001FBB98.bin
        INCBIN  build\mapcontainer\map_001FBB98_001FBC28.bin
|unk_081FBC28|
        INCBIN  build\mapcontainer\map_001FBC28_001FBC58.bin
|unk_081FBC58|
        INCBIN  build\mapcontainer\map_001FBC58_001FBC60.bin
        INCBIN  build\mapcontainer\map_001FBC60_001FBCB0.bin
        INCBIN  build\mapcontainer\map_001FBCB0_001FBD50.bin
        INCBIN  build\mapcontainer\map_001FBD50_001FBD70.bin
        INCBIN  build\mapcontainer\map_001FBD70_001FBE4C.bin
        INCBIN  build\mapcontainer\map_001FBE4C_001FBE6C.bin
        INCBIN  build\mapcontainer\map_001FBE6C_001FC128.bin
        INCBIN  build\mapcontainer\map_001FC128_001FC148.bin
        INCBIN  build\mapcontainer\map_001FC148_001FC540.bin
        INCBIN  build\mapcontainer\map_001FC540_001FC55C.bin
        INCBIN  build\mapcontainer\map_001FC55C_001FC5B0.bin
        INCLUDE rawlabeled_1fc5b0.s
        INCBIN  build\mapcontainer\map_001FC690_001FC6E0.bin
        INCBIN  build\mapcontainer\map_001FC6E0_001FC700.bin
        INCBIN  build\mapcontainer\map_001FC700_001FC720.bin
        INCBIN  build\mapcontainer\map_001FC720_001FC740.bin
        INCBIN  build\mapcontainer\map_001FC740_001FC75C.bin
        INCBIN  build\mapcontainer\map_001FC75C_001FC908.bin
        INCBIN  build\mapcontainer\map_001FC908_001FC928.bin
|unk_081FC928|
        INCBIN  build\mapcontainer\map_001FC928_001FC978.bin
|unk_081FC978|
        INCBIN  build\mapcontainer\map_001FC978_001FC980.bin
        INCBIN  build\mapcontainer\map_001FC980_001FC9D0.bin
        INCBIN  build\mapcontainer\map_001FC9D0_001FCA28.bin
        INCBIN  build\mapcontainer\map_001FCA28_001FCA44.bin
        INCBIN  build\mapcontainer\map_001FCA44_001FCA70.bin
        INCBIN  build\mapcontainer\map_001FCA70_001FCA8C.bin
        INCBIN  build\mapcontainer\map_001FCA8C_001FCB80.bin
        INCBIN  build\mapcontainer\map_001FCB80_001FCB9C.bin
        INCBIN  build\mapcontainer\map_001FCB9C_001FCC20.bin
        INCBIN  build\mapcontainer\map_001FCC20_001FCC3C.bin
        INCBIN  build\mapcontainer\map_001FCC3C_001FCC60.bin
|unk_081FCC60|
        INCBIN  build\mapcontainer\map_001FCC60_001FCC78.bin
|unk_081FCC78|
        INCBIN  build\mapcontainer\map_001FCC78_001FCC90.bin
|unk_081FCC90|
        INCBIN  build\mapcontainer\map_001FCC90_001FCC94.bin
        INCBIN  build\mapcontainer\map_001FCC94_001FCCE4.bin
        INCBIN  build\mapcontainer\map_001FCCE4_001FCD38.bin
|unk_081FCD38|
        INCBIN  build\mapcontainer\map_001FCD38_001FCD50.bin
|unk_081FCD50|
        INCBIN  build\mapcontainer\map_001FCD50_001FCD68.bin
|unk_081FCD68|
        INCBIN  build\mapcontainer\map_001FCD68_001FCD6C.bin
        INCBIN  build\mapcontainer\map_001FCD6C_001FCDBC.bin
        INCBIN  build\mapcontainer\map_001FCDBC_001FCE38.bin
|unk_081FCE38|
        INCBIN  build\mapcontainer\map_001FCE38_001FCE68.bin
|unk_081FCE68|
        INCBIN  build\mapcontainer\map_001FCE68_001FCE70.bin
        INCBIN  build\mapcontainer\map_001FCE70_001FCEC0.bin
        INCBIN  build\mapcontainer\map_001FCEC0_001FCF3C.bin
|unk_081FCF3C|
        INCBIN  build\mapcontainer\map_001FCF3C_001FCF6C.bin
|unk_081FCF6C|
        INCBIN  build\mapcontainer\map_001FCF6C_001FCF74.bin
        INCBIN  build\mapcontainer\map_001FCF74_001FCFC4.bin
        INCBIN  build\mapcontainer\map_001FCFC4_001FD018.bin
|unk_081FD018|
        INCBIN  build\mapcontainer\map_001FD018_001FD030.bin
|unk_081FD030|
        INCBIN  build\mapcontainer\map_001FD030_001FD048.bin
|unk_081FD048|
        INCBIN  build\mapcontainer\map_001FD048_001FD04C.bin
        INCBIN  build\mapcontainer\map_001FD04C_001FD09C.bin
        INCBIN  build\mapcontainer\map_001FD09C_001FD0F0.bin
|unk_081FD0F0|
        INCBIN  build\mapcontainer\map_001FD0F0_001FD108.bin
|unk_081FD108|
        INCBIN  build\mapcontainer\map_001FD108_001FD120.bin
|unk_081FD120|
        INCBIN  build\mapcontainer\map_001FD120_001FD124.bin
        INCBIN  build\mapcontainer\map_001FD124_001FD174.bin
        INCBIN  build\mapcontainer\map_001FD174_001FD1F0.bin
|unk_081FD1F0|
        INCBIN  build\mapcontainer\map_001FD1F0_001FD298.bin
|unk_081FD298|
        INCBIN  build\mapcontainer\map_001FD298_001FD2C8.bin
|unk_081FD2C8|
        INCBIN  build\mapcontainer\map_001FD2C8_001FD2D0.bin
        INCBIN  build\mapcontainer\map_001FD2D0_001FD320.bin
        INCBIN  build\mapcontainer\map_001FD320_001FD39C.bin
|unk_081FD39C|
        INCBIN  build\mapcontainer\map_001FD39C_001FD3CC.bin
|unk_081FD3CC|
        INCBIN  build\mapcontainer\map_001FD3CC_001FD3D4.bin
        INCBIN  build\mapcontainer\map_001FD3D4_001FD424.bin
        INCBIN  build\mapcontainer\map_001FD424_001FD478.bin
|unk_081FD478|
        INCBIN  build\mapcontainer\map_001FD478_001FD490.bin
|unk_081FD490|
        INCBIN  build\mapcontainer\map_001FD490_001FD4A8.bin
|unk_081FD4A8|
        INCBIN  build\mapcontainer\map_001FD4A8_001FD4AC.bin
        INCBIN  build\mapcontainer\map_001FD4AC_001FD4FC.bin
        INCBIN  build\mapcontainer\map_001FD4FC_001FD694.bin
        INCBIN  build\mapcontainer\map_001FD694_001FD6C4.bin
        INCBIN  build\mapcontainer\map_001FD6C4_001FDA78.bin
        INCBIN  build\mapcontainer\map_001FDA78_001FDAA8.bin
        INCBIN  build\mapcontainer\map_001FDAA8_001FDB6C.bin
        INCBIN  build\mapcontainer\map_001FDB6C_001FDB8C.bin
        INCBIN  build\mapcontainer\map_001FDB8C_001FDDDC.bin
        INCBIN  build\mapcontainer\map_001FDDDC_001FDDFC.bin
        INCBIN  build\mapcontainer\map_001FDDFC_001FDEA8.bin
|unk_081FDEA8|
        INCBIN  build\mapcontainer\map_001FDEA8_001FDEC0.bin
|unk_081FDEC0|
        INCBIN  build\mapcontainer\map_001FDEC0_001FDED8.bin
|unk_081FDED8|
        INCBIN  build\mapcontainer\map_001FDED8_001FDEDC.bin
        INCBIN  build\mapcontainer\map_001FDEDC_001FDF2C.bin
        INCBIN  build\mapcontainer\map_001FDF2C_001FE0B0.bin
        INCBIN  build\mapcontainer\map_001FE0B0_001FE0D0.bin
        INCBIN  build\mapcontainer\map_001FE0D0_001FE2BC.bin
        INCBIN  build\mapcontainer\map_001FE2BC_001FE2DC.bin
        INCBIN  build\mapcontainer\map_001FE2DC_001FE3A0.bin
        INCBIN  build\mapcontainer\map_001FE3A0_001FE3C0.bin
        INCBIN  build\mapcontainer\map_001FE3C0_001FE60C.bin
        INCBIN  build\mapcontainer\map_001FE60C_001FE62C.bin
        INCBIN  build\mapcontainer\map_001FE62C_001FE6CC.bin
|unk_081FE6CC|
        INCBIN  build\mapcontainer\map_001FE6CC_001FE6FC.bin
|unk_081FE6FC|
        INCBIN  build\mapcontainer\map_001FE6FC_001FE704.bin
        INCBIN  build\mapcontainer\map_001FE704_001FE754.bin
        INCBIN  build\mapcontainer\map_001FE754_001FE894.bin
        INCBIN  build\mapcontainer\map_001FE894_001FE8B4.bin
        INCBIN  build\mapcontainer\map_001FE8B4_001FEAE0.bin
        INCBIN  build\mapcontainer\map_001FEAE0_001FEB00.bin
        INCBIN  build\mapcontainer\map_001FEB00_001FEBC4.bin
        INCBIN  build\mapcontainer\map_001FEBC4_001FEBE4.bin
        INCBIN  build\mapcontainer\map_001FEBE4_001FEE30.bin
        INCBIN  build\mapcontainer\map_001FEE30_001FEE50.bin
        INCBIN  build\mapcontainer\map_001FEE50_001FEF08.bin
|unk_081FEF08|
        INCBIN  build\mapcontainer\map_001FEF08_001FEF20.bin
|unk_081FEF20|
        INCBIN  build\mapcontainer\map_001FEF20_001FEF38.bin
|unk_081FEF38|
        INCBIN  build\mapcontainer\map_001FEF38_001FEF3C.bin
        INCBIN  build\mapcontainer\map_001FEF3C_001FEF8C.bin
        INCBIN  build\mapcontainer\map_001FEF8C_001FF090.bin
        INCBIN  build\mapcontainer\map_001FF090_001FF0B8.bin
        INCBIN  build\mapcontainer\map_001FF0B8_001FF278.bin
        INCBIN  build\mapcontainer\map_001FF278_001FF298.bin
        INCBIN  build\mapcontainer\map_001FF298_001FF378.bin
        INCBIN  build\mapcontainer\map_001FF378_001FF398.bin
        INCBIN  build\mapcontainer\map_001FF398_001FF3F0.bin
|unk_081FF3F0|
        INCBIN  build\mapcontainer\map_001FF3F0_001FF408.bin
        INCBIN  build\mapcontainer\map_001FF408_001FF490.bin
|unk_081FF490|
        INCBIN  build\mapcontainer\map_001FF490_001FF4A8.bin
|unk_081FF4A8|
        INCBIN  build\mapcontainer\map_001FF4A8_001FF4AC.bin
        INCBIN  build\mapcontainer\map_001FF4AC_001FF4FC.bin
        INCBIN  build\mapcontainer\map_001FF4FC_001FF580.bin
        INCBIN  build\mapcontainer\map_001FF580_001FF5C8.bin
        INCBIN  build\mapcontainer\map_001FF5C8_001FF5E8.bin
        INCBIN  build\mapcontainer\map_001FF5E8_001FF618.bin
|unk_081FF618|
        INCBIN  build\mapcontainer\map_001FF618_001FF648.bin
|unk_081FF648|
        INCBIN  build\mapcontainer\map_001FF648_001FF650.bin
        INCBIN  build\mapcontainer\map_001FF650_001FF6A0.bin
        INCBIN  build\mapcontainer\map_001FF6A0_001FF6E8.bin
        INCBIN  build\mapcontainer\map_001FF6E8_001FF708.bin
|unk_081FF708|
        INCBIN  build\mapcontainer\map_001FF708_001FF738.bin
|unk_081FF738|
        INCBIN  build\mapcontainer\map_001FF738_001FF740.bin
        INCBIN  build\mapcontainer\map_001FF740_001FF790.bin
        INCBIN  build\mapcontainer\map_001FF790_001FF7F4.bin
        INCBIN  build\mapcontainer\map_001FF7F4_001FF81C.bin
        INCBIN  build\mapcontainer\map_001FF81C_001FF8E8.bin
        INCBIN  build\mapcontainer\map_001FF8E8_001FF908.bin
        INCBIN  build\mapcontainer\map_001FF908_001FF928.bin
        INCBIN  build\mapcontainer\map_001FF928_001FF954.bin
|unk_081FF954|
        INCBIN  build\mapcontainer\map_001FF954_001FF96C.bin
|unk_081FF96C|
        INCBIN  build\mapcontainer\map_001FF96C_001FF970.bin
        INCBIN  build\mapcontainer\map_001FF970_001FF9C0.bin
        INCBIN  build\mapcontainer\map_001FF9C0_001FF9F4.bin
        INCBIN  build\mapcontainer\map_001FF9F4_001FFA10.bin
        INCBIN  build\mapcontainer\map_001FFA10_001FFF04.bin
        INCBIN  build\mapcontainer\map_001FFF04_001FFF2C.bin
        INCBIN  build\mapcontainer\map_001FFF2C_00200074.bin
        INCBIN  build\mapcontainer\map_00200074_00200094.bin
        INCBIN  build\mapcontainer\map_00200094_0020037C.bin
        INCBIN  build\mapcontainer\map_0020037C_0020039C.bin
        INCBIN  build\mapcontainer\map_0020039C_002003FC.bin
|unk_082003FC|
        INCBIN  build\mapcontainer\map_002003FC_00200414.bin
        INCBIN  build\mapcontainer\map_00200414_00200464.bin
        INCBIN  build\mapcontainer\map_00200464_00200934.bin
        INCBIN  build\mapcontainer\map_00200934_0020095C.bin
        INCBIN  build\mapcontainer\map_0020095C_00200AA4.bin
        INCBIN  build\mapcontainer\map_00200AA4_00200AC4.bin
        INCBIN  build\mapcontainer\map_00200AC4_00200DB0.bin
        INCBIN  build\mapcontainer\map_00200DB0_00200DD0.bin
        INCBIN  build\mapcontainer\map_00200DD0_00200E18.bin
        INCBIN  build\mapcontainer\map_00200E18_00200E68.bin
        INCBIN  build\mapcontainer\map_00200E68_00200E90.bin
        INCBIN  build\mapcontainer\map_00200E90_00200ED0.bin
        INCBIN  build\mapcontainer\map_00200ED0_00200F20.bin
        INCBIN  build\mapcontainer\map_00200F20_00200F48.bin
        INCBIN  build\mapcontainer\map_00200F48_00200F88.bin
|unk_08200F88|
        INCBIN  build\mapcontainer\map_00200F88_00200FA0.bin
        INCBIN  build\mapcontainer\map_00200FA0_002010E0.bin
        INCBIN  build\mapcontainer\map_002010E0_00201130.bin
        INCBIN  build\mapcontainer\map_00201130_002011E8.bin
        INCBIN  build\mapcontainer\map_002011E8_00201210.bin
        INCBIN  build\mapcontainer\map_00201210_00201650.bin
        INCBIN  build\mapcontainer\map_00201650_00201678.bin
        INCBIN  build\mapcontainer\map_00201678_002018D4.bin
        INCBIN  build\mapcontainer\map_002018D4_002018FC.bin
        INCBIN  build\mapcontainer\map_002018FC_00201A70.bin
|unk_08201A70|
        INCBIN  build\mapcontainer\map_00201A70_00201AA0.bin
|unk_08201AA0|
        INCBIN  build\mapcontainer\map_00201AA0_00201B00.bin
|unk_08201B00|
        INCBIN  build\mapcontainer\map_00201B00_00201B10.bin
        INCBIN  build\mapcontainer\map_00201B10_00201B60.bin
        INCBIN  build\mapcontainer\map_00201B60_00201B9C.bin
        INCBIN  build\mapcontainer\map_00201B9C_00201BBC.bin
        INCBIN  build\mapcontainer\map_00201BBC_00201CF4.bin
        INCBIN  build\mapcontainer\map_00201CF4_00201D1C.bin
        INCBIN  build\mapcontainer\map_00201D1C_002021AC.bin
        INCBIN  build\mapcontainer\map_002021AC_002021D4.bin
        INCBIN  build\mapcontainer\map_002021D4_00202454.bin
        INCBIN  build\mapcontainer\map_00202454_0020247C.bin
        INCBIN  build\mapcontainer\map_0020247C_002025C0.bin
|unk_082025C0|
        INCBIN  build\mapcontainer\map_002025C0_00202680.bin
        INCBIN  build\mapcontainer\map_00202680_0020270C.bin
|unk_0820270C|
        INCBIN  build\mapcontainer\map_0020270C_00202784.bin
|unk_08202784|
        INCBIN  build\mapcontainer\map_00202784_00202798.bin
        INCBIN  build\mapcontainer\map_00202798_002027E8.bin
        INCBIN  build\mapcontainer\map_002027E8_00202944.bin
        INCBIN  build\mapcontainer\map_00202944_0020296C.bin
        INCBIN  build\mapcontainer\map_0020296C_00202D9C.bin
        INCBIN  build\mapcontainer\map_00202D9C_00202DC4.bin
        INCBIN  build\mapcontainer\map_00202DC4_0020307C.bin
        INCBIN  build\mapcontainer\map_0020307C_002030A4.bin
        INCBIN  build\mapcontainer\map_002030A4_00203210.bin
|unk_08203210|
        INCBIN  build\mapcontainer\map_00203210_00203288.bin
|unk_08203288|
        INCBIN  build\mapcontainer\map_00203288_0020329C.bin
        INCBIN  build\mapcontainer\map_0020329C_002032EC.bin
        INCBIN  build\mapcontainer\map_002032EC_002038F4.bin
        INCBIN  build\mapcontainer\map_002038F4_0020391C.bin
        INCBIN  build\mapcontainer\map_0020391C_00203C2C.bin
        INCBIN  build\mapcontainer\map_00203C2C_00203C54.bin
        INCBIN  build\mapcontainer\map_00203C54_00203CF8.bin
        INCBIN  build\mapcontainer\map_00203CF8_00203D18.bin
        INCBIN  build\mapcontainer\map_00203D18_00203F88.bin
        INCBIN  build\mapcontainer\map_00203F88_00203FA4.bin
        INCBIN  build\mapcontainer\map_00203FA4_002041B0.bin
|unk_082041B0|
        INCBIN  build\mapcontainer\map_002041B0_002041E0.bin
        INCBIN  build\mapcontainer\map_002041E0_002048B0.bin
|unk_082048B0|
        INCBIN  build\mapcontainer\map_002048B0_00204910.bin
|unk_08204910|
        INCBIN  build\mapcontainer\map_00204910_00204920.bin
        INCBIN  build\mapcontainer\map_00204920_00204970.bin
        INCBIN  build\mapcontainer\map_00204970_00204AEC.bin
        INCBIN  build\mapcontainer\map_00204AEC_00204B14.bin
        INCBIN  build\mapcontainer\map_00204B14_00204BF0.bin
        INCBIN  build\mapcontainer\map_00204BF0_00204C18.bin
        INCBIN  build\mapcontainer\map_00204C18_00204CC8.bin
|unk_08204CC8|
        INCBIN  build\mapcontainer\map_00204CC8_00204D28.bin
        INCBIN  build\mapcontainer\map_00204D28_00204ECC.bin
|unk_08204ECC|
        INCBIN  build\mapcontainer\map_00204ECC_00204F2C.bin
|unk_08204F2C|
        INCBIN  build\mapcontainer\map_00204F2C_00204F3C.bin
        INCBIN  build\mapcontainer\map_00204F3C_00204F8C.bin
        INCBIN  build\mapcontainer\map_00204F8C_0020500C.bin
        INCBIN  build\mapcontainer\map_0020500C_0020502C.bin
        INCBIN  build\mapcontainer\map_0020502C_00205174.bin
        INCBIN  build\mapcontainer\map_00205174_0020519C.bin
        INCBIN  build\mapcontainer\map_0020519C_00205294.bin
        INCBIN  build\mapcontainer\map_00205294_002052BC.bin
        INCBIN  build\mapcontainer\map_002052BC_0020537C.bin
|unk_0820537C|
        INCBIN  build\mapcontainer\map_0020537C_002053C4.bin
|unk_082053C4|
        INCBIN  build\mapcontainer\map_002053C4_00205424.bin
|unk_08205424|
        INCBIN  build\mapcontainer\map_00205424_00205434.bin
        INCBIN  build\mapcontainer\map_00205434_00205484.bin
        INCBIN  build\mapcontainer\map_00205484_00205598.bin
        INCBIN  build\mapcontainer\map_00205598_002055B8.bin
        INCBIN  build\mapcontainer\map_002055B8_00205758.bin
        INCBIN  build\mapcontainer\map_00205758_00205780.bin
        INCBIN  build\mapcontainer\map_00205780_0020587C.bin
        INCBIN  build\mapcontainer\map_0020587C_0020589C.bin
        INCBIN  build\mapcontainer\map_0020589C_00205AB4.bin
        INCBIN  build\mapcontainer\map_00205AB4_00205ADC.bin
        INCBIN  build\mapcontainer\map_00205ADC_00205C2C.bin
|unk_08205C2C|
        INCBIN  build\mapcontainer\map_00205C2C_00205CA4.bin
        INCBIN  build\mapcontainer\map_00205CA4_00205F08.bin
        INCLUDE rawlabeled_205f08.s
        INCBIN  build\mapcontainer\map_00205F78_00205FC8.bin
        INCBIN  build\mapcontainer\map_00205FC8_00206004.bin
        INCBIN  build\mapcontainer\map_00206004_00206024.bin
        INCBIN  build\mapcontainer\map_00206024_0020617C.bin
        INCBIN  build\mapcontainer\map_0020617C_002061A4.bin
        INCBIN  build\mapcontainer\map_002061A4_0020624C.bin
        INCBIN  build\mapcontainer\map_0020624C_00206274.bin
        INCBIN  build\mapcontainer\map_00206274_0020630C.bin
        INCLUDE rawlabeled_20630c.s
        INCBIN  build\mapcontainer\map_00206394_002063E4.bin
        INCBIN  build\mapcontainer\map_002063E4_002064E4.bin
        INCBIN  build\mapcontainer\map_002064E4_0020650C.bin
        INCBIN  build\mapcontainer\map_0020650C_00206598.bin
        INCBIN  build\mapcontainer\map_00206598_002065C0.bin
        INCBIN  build\mapcontainer\map_002065C0_002065FC.bin
        INCLUDE rawlabeled_2065fc.s
        INCBIN  build\mapcontainer\map_002066E4_00206734.bin
        INCBIN  build\mapcontainer\map_00206734_00206770.bin
        INCBIN  build\mapcontainer\map_00206770_00206790.bin
        INCBIN  build\mapcontainer\map_00206790_002068FC.bin
        INCBIN  build\mapcontainer\map_002068FC_00206924.bin
        INCBIN  build\mapcontainer\map_00206924_002069F0.bin
        INCBIN  build\mapcontainer\map_002069F0_00206A18.bin
        INCBIN  build\mapcontainer\map_00206A18_00206AC8.bin
|unk_08206AC8|
        INCBIN  build\mapcontainer\map_00206AC8_00206B28.bin
|unk_08206B28|
        INCBIN  build\mapcontainer\map_00206B28_00206B88.bin
|unk_08206B88|
        INCBIN  build\mapcontainer\map_00206B88_00206B98.bin
        INCBIN  build\mapcontainer\map_00206B98_00206BE8.bin
        INCBIN  build\mapcontainer\map_00206BE8_00206CBC.bin
        INCBIN  build\mapcontainer\map_00206CBC_00206CDC.bin
        INCBIN  build\mapcontainer\map_00206CDC_00206D18.bin
        INCBIN  build\mapcontainer\map_00206D18_00206D34.bin
        INCBIN  build\mapcontainer\map_00206D34_00206EC4.bin
        INCBIN  build\mapcontainer\map_00206EC4_00206EEC.bin
        INCBIN  build\mapcontainer\map_00206EEC_00206FE0.bin
        INCBIN  build\mapcontainer\map_00206FE0_00207008.bin
        INCBIN  build\mapcontainer\map_00207008_00207108.bin
|unk_08207108|
        INCBIN  build\mapcontainer\map_00207108_00207168.bin
|unk_08207168|
        INCBIN  build\mapcontainer\map_00207168_002071C8.bin
|unk_082071C8|
        INCBIN  build\mapcontainer\map_002071C8_002071D8.bin
        INCBIN  build\mapcontainer\map_002071D8_00207228.bin
        INCBIN  build\mapcontainer\map_00207228_002073CC.bin
        INCBIN  build\mapcontainer\map_002073CC_002073F4.bin
        INCBIN  build\mapcontainer\map_002073F4_002074DC.bin
        INCBIN  build\mapcontainer\map_002074DC_00207504.bin
        INCBIN  build\mapcontainer\map_00207504_002075C0.bin
|unk_082075C0|
        INCBIN  build\mapcontainer\map_002075C0_00207680.bin
        INCBIN  build\mapcontainer\map_00207680_002079CC.bin
|unk_082079CC|
        INCBIN  build\mapcontainer\map_002079CC_00207A2C.bin
|unk_08207A2C|
        INCBIN  build\mapcontainer\map_00207A2C_00207A3C.bin
        INCBIN  build\mapcontainer\map_00207A3C_00207A8C.bin
        INCBIN  build\mapcontainer\map_00207A8C_00207C2C.bin
        INCBIN  build\mapcontainer\map_00207C2C_00207C54.bin
        INCBIN  build\mapcontainer\map_00207C54_00207D64.bin
        INCBIN  build\mapcontainer\map_00207D64_00207D8C.bin
        INCBIN  build\mapcontainer\map_00207D8C_00207E6C.bin
|unk_08207E6C|
        INCBIN  build\mapcontainer\map_00207E6C_00207F14.bin
|unk_08207F14|
        INCBIN  build\mapcontainer\map_00207F14_00207F5C.bin
|unk_08207F5C|
        INCBIN  build\mapcontainer\map_00207F5C_00207F68.bin
        INCBIN  build\mapcontainer\map_00207F68_00207FB8.bin
        INCBIN  build\mapcontainer\map_00207FB8_00207FF4.bin
        INCBIN  build\mapcontainer\map_00207FF4_00208014.bin
        INCBIN  build\mapcontainer\map_00208014_002081A4.bin
        INCBIN  build\mapcontainer\map_002081A4_002081CC.bin
        INCBIN  build\mapcontainer\map_002081CC_002082C4.bin
        INCBIN  build\mapcontainer\map_002082C4_002082EC.bin
        INCBIN  build\mapcontainer\map_002082EC_002083C0.bin
|unk_082083C0|
        INCBIN  build\mapcontainer\map_002083C0_00208408.bin
|unk_08208408|
        INCBIN  build\mapcontainer\map_00208408_00208450.bin
|unk_08208450|
        INCBIN  build\mapcontainer\map_00208450_0020845C.bin
        INCBIN  build\mapcontainer\map_0020845C_002084AC.bin
        INCBIN  build\mapcontainer\map_002084AC_002084E8.bin
        INCBIN  build\mapcontainer\map_002084E8_00208504.bin
        INCBIN  build\mapcontainer\map_00208504_0020866C.bin
        INCBIN  build\mapcontainer\map_0020866C_00208694.bin
        INCBIN  build\mapcontainer\map_00208694_002086F0.bin
        INCBIN  build\mapcontainer\map_002086F0_00208718.bin
        INCBIN  build\mapcontainer\map_00208718_002087B0.bin
|unk_082087B0|
        INCBIN  build\mapcontainer\map_002087B0_00208840.bin
|unk_08208840|
        INCBIN  build\mapcontainer\map_00208840_00208888.bin
|unk_08208888|
        INCBIN  build\mapcontainer\map_00208888_00208894.bin
        INCBIN  build\mapcontainer\map_00208894_002088E4.bin
        INCBIN  build\mapcontainer\map_002088E4_00208B8C.bin
        INCBIN  build\mapcontainer\map_00208B8C_00208BB4.bin
        INCBIN  build\mapcontainer\map_00208BB4_00208CBC.bin
        INCBIN  build\mapcontainer\map_00208CBC_00208CE4.bin
        INCBIN  build\mapcontainer\map_00208CE4_00208E60.bin
        INCBIN  build\mapcontainer\map_00208E60_00208E88.bin
        INCBIN  build\mapcontainer\map_00208E88_00209080.bin
        INCBIN  build\mapcontainer\map_00209080_002090A8.bin
        INCBIN  build\mapcontainer\map_002090A8_002091A0.bin
|unk_082091A0|
        INCBIN  build\mapcontainer\map_002091A0_00209200.bin
        INCBIN  build\mapcontainer\map_00209200_00209498.bin
|unk_08209498|
        INCBIN  build\mapcontainer\map_00209498_002094E0.bin
|unk_082094E0|
        INCBIN  build\mapcontainer\map_002094E0_002094EC.bin
        INCBIN  build\mapcontainer\map_002094EC_0020953C.bin
        INCBIN  build\mapcontainer\map_0020953C_00209674.bin
        INCBIN  build\mapcontainer\map_00209674_0020969C.bin
        INCBIN  build\mapcontainer\map_0020969C_0020985C.bin
        INCBIN  build\mapcontainer\map_0020985C_00209884.bin
        INCBIN  build\mapcontainer\map_00209884_00209A9C.bin
        INCBIN  build\mapcontainer\map_00209A9C_00209AC4.bin
        INCBIN  build\mapcontainer\map_00209AC4_00209B4C.bin
|unk_08209B4C|
        INCBIN  build\mapcontainer\map_00209B4C_00209BC4.bin
        INCBIN  build\mapcontainer\map_00209BC4_0020A250.bin
|unk_0820A250|
        INCBIN  build\mapcontainer\map_0020A250_0020A280.bin
|unk_0820A280|
        INCBIN  build\mapcontainer\map_0020A280_0020A288.bin
        INCBIN  build\mapcontainer\map_0020A288_0020A2D8.bin
        INCBIN  build\mapcontainer\map_0020A2D8_0020A384.bin
        INCBIN  build\mapcontainer\map_0020A384_0020A3A0.bin
        INCBIN  build\mapcontainer\map_0020A3A0_0020A4D8.bin
        INCBIN  build\mapcontainer\map_0020A4D8_0020A4F4.bin
        INCBIN  build\mapcontainer\map_0020A4F4_0020A5A0.bin
        INCBIN  build\mapcontainer\map_0020A5A0_0020A5BC.bin
        INCBIN  build\mapcontainer\map_0020A5BC_0020A640.bin
|unk_0820A640|
        INCBIN  build\mapcontainer\map_0020A640_0020A670.bin
|unk_0820A670|
        INCBIN  build\mapcontainer\map_0020A670_0020A678.bin
        INCBIN  build\mapcontainer\map_0020A678_0020A6C8.bin
        INCBIN  build\mapcontainer\map_0020A6C8_0020A750.bin
        INCBIN  build\mapcontainer\map_0020A750_0020A76C.bin
        INCBIN  build\mapcontainer\map_0020A76C_0020A82C.bin
        INCBIN  build\mapcontainer\map_0020A82C_0020A848.bin
        INCBIN  build\mapcontainer\map_0020A848_0020A884.bin
        INCBIN  build\mapcontainer\map_0020A884_0020A8A0.bin
        INCBIN  build\mapcontainer\map_0020A8A0_0020A908.bin
|unk_0820A908|
        INCBIN  build\mapcontainer\map_0020A908_0020A920.bin
|unk_0820A920|
        INCBIN  build\mapcontainer\map_0020A920_0020A924.bin
        INCBIN  build\mapcontainer\map_0020A924_0020A974.bin
        INCBIN  build\mapcontainer\map_0020A974_0020AA44.bin
        INCBIN  build\mapcontainer\map_0020AA44_0020AA64.bin
        INCBIN  build\mapcontainer\map_0020AA64_0020AAC0.bin
        INCBIN  build\mapcontainer\map_0020AAC0_0020AADC.bin
        INCBIN  build\mapcontainer\map_0020AADC_0020AC2C.bin
        INCBIN  build\mapcontainer\map_0020AC2C_0020AC4C.bin
        INCBIN  build\mapcontainer\map_0020AC4C_0020AD5C.bin
        INCBIN  build\mapcontainer\map_0020AD5C_0020AD7C.bin
        INCBIN  build\mapcontainer\map_0020AD7C_0020ADF8.bin
|unk_0820ADF8|
        INCBIN  build\mapcontainer\map_0020ADF8_0020AE40.bin
|unk_0820AE40|
        INCBIN  build\mapcontainer\map_0020AE40_0020AE4C.bin
        INCBIN  build\mapcontainer\map_0020AE4C_0020AE9C.bin
        INCBIN  build\mapcontainer\map_0020AE9C_0020AF5C.bin
        INCBIN  build\mapcontainer\map_0020AF5C_0020AF7C.bin
        INCBIN  build\mapcontainer\map_0020AF7C_0020B074.bin
        INCBIN  build\mapcontainer\map_0020B074_0020B094.bin
        INCBIN  build\mapcontainer\map_0020B094_0020B1BC.bin
        INCBIN  build\mapcontainer\map_0020B1BC_0020B1DC.bin
        INCBIN  build\mapcontainer\map_0020B1DC_0020B24C.bin
|unk_0820B24C|
        INCBIN  build\mapcontainer\map_0020B24C_0020B27C.bin
|unk_0820B27C|
        INCBIN  build\mapcontainer\map_0020B27C_0020B284.bin
        INCBIN  build\mapcontainer\map_0020B284_0020B2D4.bin
        INCBIN  build\mapcontainer\map_0020B2D4_0020B3A4.bin
        INCBIN  build\mapcontainer\map_0020B3A4_0020B3C4.bin
        INCBIN  build\mapcontainer\map_0020B3C4_0020B42C.bin
        INCBIN  build\mapcontainer\map_0020B42C_0020B448.bin
        INCBIN  build\mapcontainer\map_0020B448_0020B6EC.bin
        INCBIN  build\mapcontainer\map_0020B6EC_0020B70C.bin
        INCBIN  build\mapcontainer\map_0020B70C_0020B8CC.bin
        INCBIN  build\mapcontainer\map_0020B8CC_0020B8EC.bin
        INCBIN  build\mapcontainer\map_0020B8EC_0020B998.bin
|unk_0820B998|
        INCBIN  build\mapcontainer\map_0020B998_0020B9C8.bin
|unk_0820B9C8|
        INCBIN  build\mapcontainer\map_0020B9C8_0020B9D0.bin
        INCBIN  build\mapcontainer\map_0020B9D0_0020BA20.bin
        INCBIN  build\mapcontainer\map_0020BA20_0020BB68.bin
        INCBIN  build\mapcontainer\map_0020BB68_0020BB88.bin
        INCBIN  build\mapcontainer\map_0020BB88_0020BDF0.bin
        INCBIN  build\mapcontainer\map_0020BDF0_0020BE10.bin
        INCBIN  build\mapcontainer\map_0020BE10_0020BFCC.bin
        INCBIN  build\mapcontainer\map_0020BFCC_0020BFEC.bin
        INCBIN  build\mapcontainer\map_0020BFEC_0020C0C0.bin
|unk_0820C0C0|
        INCBIN  build\mapcontainer\map_0020C0C0_0020C0F0.bin
|unk_0820C0F0|
        INCBIN  build\mapcontainer\map_0020C0F0_0020C0F8.bin
        INCBIN  build\mapcontainer\map_0020C0F8_0020C148.bin
        INCBIN  build\mapcontainer\map_0020C148_0020C1F0.bin
        INCBIN  build\mapcontainer\map_0020C1F0_0020C20C.bin
        INCBIN  build\mapcontainer\map_0020C20C_0020C2D4.bin
        INCBIN  build\mapcontainer\map_0020C2D4_0020C2F0.bin
        INCBIN  build\mapcontainer\map_0020C2F0_0020C374.bin
        INCBIN  build\mapcontainer\map_0020C374_0020C390.bin
        INCBIN  build\mapcontainer\map_0020C390_0020C40C.bin
|unk_0820C40C|
        INCBIN  build\mapcontainer\map_0020C40C_0020C43C.bin
|unk_0820C43C|
        INCBIN  build\mapcontainer\map_0020C43C_0020C444.bin
        INCBIN  build\mapcontainer\map_0020C444_0020C494.bin
        INCBIN  build\mapcontainer\map_0020C494_0020C50C.bin
        INCBIN  build\mapcontainer\map_0020C50C_0020C52C.bin
        INCBIN  build\mapcontainer\map_0020C52C_0020C6EC.bin
        INCBIN  build\mapcontainer\map_0020C6EC_0020C70C.bin
        INCBIN  build\mapcontainer\map_0020C70C_0020C980.bin
        INCBIN  build\mapcontainer\map_0020C980_0020C9A0.bin
        INCBIN  build\mapcontainer\map_0020C9A0_0020CA54.bin
|unk_0820CA54|
        INCBIN  build\mapcontainer\map_0020CA54_0020CA6C.bin
|unk_0820CA6C|
        INCBIN  build\mapcontainer\map_0020CA6C_0020CA70.bin
        INCBIN  build\mapcontainer\map_0020CA70_0020CAC0.bin
        INCBIN  build\mapcontainer\map_0020CAC0_0020CB64.bin
        INCBIN  build\mapcontainer\map_0020CB64_0020CB80.bin
        INCBIN  build\mapcontainer\map_0020CB80_0020CC24.bin
        INCBIN  build\mapcontainer\map_0020CC24_0020CC40.bin
        INCBIN  build\mapcontainer\map_0020CC40_0020CCD0.bin
        INCBIN  build\mapcontainer\map_0020CCD0_0020CCEC.bin
        INCBIN  build\mapcontainer\map_0020CCEC_0020CD58.bin
|unk_0820CD58|
        INCBIN  build\mapcontainer\map_0020CD58_0020CD88.bin
|unk_0820CD88|
        INCBIN  build\mapcontainer\map_0020CD88_0020CD90.bin
        INCBIN  build\mapcontainer\map_0020CD90_0020CDE0.bin
        INCBIN  build\mapcontainer\map_0020CDE0_0020CF0C.bin
        INCBIN  build\mapcontainer\map_0020CF0C_0020CF2C.bin
        INCBIN  build\mapcontainer\map_0020CF2C_0020D09C.bin
        INCBIN  build\mapcontainer\map_0020D09C_0020D0BC.bin
        INCBIN  build\mapcontainer\map_0020D0BC_0020D1EC.bin
        INCBIN  build\mapcontainer\map_0020D1EC_0020D20C.bin
        INCBIN  build\mapcontainer\map_0020D20C_0020D298.bin
        INCLUDE rawlabeled_20d298.s
        INCBIN  build\mapcontainer\map_0020D308_0020D358.bin
        INCBIN  build\mapcontainer\map_0020D358_0020D400.bin
        INCBIN  build\mapcontainer\map_0020D400_0020D41C.bin
        INCBIN  build\mapcontainer\map_0020D41C_0020D504.bin
        INCBIN  build\mapcontainer\map_0020D504_0020D520.bin
        INCBIN  build\mapcontainer\map_0020D520_0020D5E0.bin
        INCBIN  build\mapcontainer\map_0020D5E0_0020D5FC.bin
        INCBIN  build\mapcontainer\map_0020D5FC_0020D674.bin
|unk_0820D674|
        INCBIN  build\mapcontainer\map_0020D674_0020D68C.bin
        INCBIN  build\mapcontainer\map_0020D68C_0020D834.bin
|unk_0820D834|
        INCBIN  build\mapcontainer\map_0020D834_0020D84C.bin
|unk_0820D84C|
        INCBIN  build\mapcontainer\map_0020D84C_0020D850.bin
        INCBIN  build\mapcontainer\map_0020D850_0020D8A0.bin
        INCBIN  build\mapcontainer\map_0020D8A0_0020D944.bin
        INCBIN  build\mapcontainer\map_0020D944_0020D960.bin
        INCBIN  build\mapcontainer\map_0020D960_0020D990.bin
        INCBIN  build\mapcontainer\map_0020D990_0020D9AC.bin
        INCBIN  build\mapcontainer\map_0020D9AC_0020DA50.bin
        INCBIN  build\mapcontainer\map_0020DA50_0020DA6C.bin
        INCBIN  build\mapcontainer\map_0020DA6C_0020DB0C.bin
        INCBIN  build\mapcontainer\map_0020DB0C_0020DB28.bin
        INCBIN  build\mapcontainer\map_0020DB28_0020DB9C.bin
|unk_0820DB9C|
        INCBIN  build\mapcontainer\map_0020DB9C_0020DBCC.bin
|unk_0820DBCC|
        INCBIN  build\mapcontainer\map_0020DBCC_0020DBD4.bin
        INCBIN  build\mapcontainer\map_0020DBD4_0020DC24.bin
        INCBIN  build\mapcontainer\map_0020DC24_0020DCE8.bin
        INCBIN  build\mapcontainer\map_0020DCE8_0020DD08.bin
        INCBIN  build\mapcontainer\map_0020DD08_0020DD68.bin
        INCBIN  build\mapcontainer\map_0020DD68_0020DD84.bin
        INCBIN  build\mapcontainer\map_0020DD84_0020DF04.bin
        INCBIN  build\mapcontainer\map_0020DF04_0020DF24.bin
        INCBIN  build\mapcontainer\map_0020DF24_0020DFFC.bin
        INCBIN  build\mapcontainer\map_0020DFFC_0020E01C.bin
        INCBIN  build\mapcontainer\map_0020E01C_0020E090.bin
|unk_0820E090|
        INCBIN  build\mapcontainer\map_0020E090_0020E0C0.bin
|unk_0820E0C0|
        INCBIN  build\mapcontainer\map_0020E0C0_0020E0C8.bin
        INCBIN  build\mapcontainer\map_0020E0C8_0020E118.bin
        INCBIN  build\mapcontainer\map_0020E118_0020E1C4.bin
        INCBIN  build\mapcontainer\map_0020E1C4_0020E1E0.bin
        INCBIN  build\mapcontainer\map_0020E1E0_0020E238.bin
        INCBIN  build\mapcontainer\map_0020E238_0020E254.bin
        INCBIN  build\mapcontainer\map_0020E254_0020E33C.bin
        INCBIN  build\mapcontainer\map_0020E33C_0020E358.bin
        INCBIN  build\mapcontainer\map_0020E358_0020E3F8.bin
        INCBIN  build\mapcontainer\map_0020E3F8_0020E414.bin
        INCBIN  build\mapcontainer\map_0020E414_0020E490.bin
|unk_0820E490|
        INCBIN  build\mapcontainer\map_0020E490_0020E4A8.bin
|unk_0820E4A8|
        INCBIN  build\mapcontainer\map_0020E4A8_0020E4D8.bin
|unk_0820E4D8|
        INCBIN  build\mapcontainer\map_0020E4D8_0020E4E0.bin
        INCBIN  build\mapcontainer\map_0020E4E0_0020E530.bin
        INCBIN  build\mapcontainer\map_0020E530_0020E688.bin
        INCBIN  build\mapcontainer\map_0020E688_0020E6A8.bin
        INCBIN  build\mapcontainer\map_0020E6A8_0020E708.bin
        INCBIN  build\mapcontainer\map_0020E708_0020E724.bin
        INCBIN  build\mapcontainer\map_0020E724_0020E8F0.bin
        INCBIN  build\mapcontainer\map_0020E8F0_0020E910.bin
        INCBIN  build\mapcontainer\map_0020E910_0020EA54.bin
        INCBIN  build\mapcontainer\map_0020EA54_0020EA74.bin
        INCBIN  build\mapcontainer\map_0020EA74_0020EB08.bin
|unk_0820EB08|
        INCBIN  build\mapcontainer\map_0020EB08_0020EB50.bin
|unk_0820EB50|
        INCBIN  build\mapcontainer\map_0020EB50_0020EB5C.bin
        INCBIN  build\mapcontainer\map_0020EB5C_0020EBAC.bin
        INCBIN  build\mapcontainer\map_0020EBAC_0020EC64.bin
        INCBIN  build\mapcontainer\map_0020EC64_0020EC80.bin
        INCBIN  build\mapcontainer\map_0020EC80_0020ECE0.bin
        INCBIN  build\mapcontainer\map_0020ECE0_0020ECFC.bin
        INCBIN  build\mapcontainer\map_0020ECFC_0020EE04.bin
        INCBIN  build\mapcontainer\map_0020EE04_0020EE20.bin
        INCBIN  build\mapcontainer\map_0020EE20_0020EEC8.bin
        INCBIN  build\mapcontainer\map_0020EEC8_0020EEE4.bin
        INCBIN  build\mapcontainer\map_0020EEE4_0020EF60.bin
|unk_0820EF60|
        INCBIN  build\mapcontainer\map_0020EF60_0020EFC0.bin
|unk_0820EFC0|
        INCBIN  build\mapcontainer\map_0020EFC0_0020EFD0.bin
        INCBIN  build\mapcontainer\map_0020EFD0_0020F020.bin
        INCBIN  build\mapcontainer\map_0020F020_0020F0B4.bin
        INCBIN  build\mapcontainer\map_0020F0B4_0020F0E4.bin
        INCBIN  build\mapcontainer\map_0020F0E4_0020F7E0.bin
        INCBIN  build\mapcontainer\map_0020F7E0_0020F810.bin
        INCBIN  build\mapcontainer\map_0020F810_0020FE78.bin
        INCBIN  build\mapcontainer\map_0020FE78_0020FEA8.bin
        INCBIN  build\mapcontainer\map_0020FEA8_002102BC.bin
        INCBIN  build\mapcontainer\map_002102BC_002102EC.bin
        INCBIN  build\mapcontainer\map_002102EC_002103DC.bin
|unk_082103DC|
        INCBIN  build\mapcontainer\map_002103DC_0021040C.bin
|unk_0821040C|
        INCBIN  build\mapcontainer\map_0021040C_00210414.bin
        INCBIN  build\mapcontainer\map_00210414_00210464.bin
        INCBIN  build\mapcontainer\map_00210464_00210674.bin
        INCBIN  build\mapcontainer\map_00210674_00210694.bin
        INCBIN  build\mapcontainer\map_00210694_00210814.bin
        INCBIN  build\mapcontainer\map_00210814_00210834.bin
        INCBIN  build\mapcontainer\map_00210834_0021099C.bin
        INCBIN  build\mapcontainer\map_0021099C_002109BC.bin
        INCBIN  build\mapcontainer\map_002109BC_00210A54.bin
|unk_08210A54|
        INCBIN  build\mapcontainer\map_00210A54_00210A84.bin
|unk_08210A84|
        INCBIN  build\mapcontainer\map_00210A84_00210A8C.bin
        INCBIN  build\mapcontainer\map_00210A8C_00210ADC.bin
        INCBIN  build\mapcontainer\map_00210ADC_00210C7C.bin
        INCBIN  build\mapcontainer\map_00210C7C_00210C98.bin
        INCBIN  build\mapcontainer\map_00210C98_00210D98.bin
        INCBIN  build\mapcontainer\map_00210D98_00210DB4.bin
        INCBIN  build\mapcontainer\map_00210DB4_00210FEC.bin
        INCBIN  build\mapcontainer\map_00210FEC_00211008.bin
        INCBIN  build\mapcontainer\map_00211008_002110DC.bin
|unk_082110DC|
        INCBIN  build\mapcontainer\map_002110DC_002110F4.bin
|unk_082110F4|
        INCBIN  build\mapcontainer\map_002110F4_002110F8.bin
        INCBIN  build\mapcontainer\map_002110F8_00211148.bin
        INCBIN  build\mapcontainer\map_00211148_002111C0.bin
        INCBIN  build\mapcontainer\map_002111C0_002111DC.bin
        INCBIN  build\mapcontainer\map_002111DC_002112B8.bin
        INCBIN  build\mapcontainer\map_002112B8_002112D4.bin
        INCBIN  build\mapcontainer\map_002112D4_0021135C.bin
        INCBIN  build\mapcontainer\map_0021135C_00211378.bin
        INCBIN  build\mapcontainer\map_00211378_002113E4.bin
|unk_082113E4|
        INCBIN  build\animframe\gen_2113e4_2115d4.bin
|map_anim_row_082115D4|
|unk_082115D4|
	DCB 0x04,0x06
	DCW 0x037a
	DCD 0x082113e4,0x08211460,0x082114d8,0x08211558
|unk_082115E8|
        INCBIN  build\animframe\gen_2115e8_211648.bin
|map_anim_row_08211648|
|unk_08211648|
	DCB 0x04,0x01
	DCW 0x0379
	DCD 0x082115e8,0x08211600,0x08211618,0x08211630
|unk_0821165C|
        INCBIN  baserom.gba_0x21165c_0x211664.extracted
|unk_08211664|
        INCBIN  build\mapcontainer\map_00211664_002116AC.bin
|unk_082116AC|
        INCBIN  build\mapcontainer\map_002116AC_002116B8.bin
        INCBIN  build\mapcontainer\map_002116B8_00211708.bin
        INCBIN  build\mapcontainer\map_00211708_00211790.bin
        INCBIN  build\mapcontainer\map_00211790_002117B0.bin
        INCBIN  build\mapcontainer\map_002117B0_00211818.bin
        INCBIN  build\mapcontainer\map_00211818_00211838.bin
        INCBIN  build\mapcontainer\map_00211838_00211964.bin
        INCBIN  build\mapcontainer\map_00211964_00211984.bin
        INCBIN  build\mapcontainer\map_00211984_002119F8.bin
|map_anim_row_082119F8|
|unk_082119F8|
	DCB 0x04,0x06
	DCW 0x037a
	DCD 0x082113e4,0x08211460,0x082114d8,0x08211558
|unk_08211A0C|
        INCBIN  build\animframe\gen_211a0c_211abc.bin
|map_anim_row_08211ABC|
|unk_08211ABC|
	DCB 0x04,0x03
	DCW 0x0377
	DCD 0x08211a0c,0x08211a38,0x08211a64,0x08211a90
|unk_08211AD0|
        INCBIN  baserom.gba_0x211ad0_0x211ad8.extracted
|unk_08211AD8|
        INCBIN  build\mapcontainer\map_00211AD8_00211B38.bin
|unk_08211B38|
        INCBIN  build\mapcontainer\map_00211B38_00211B48.bin
        INCBIN  build\mapcontainer\map_00211B48_00211B98.bin
        INCBIN  build\mapcontainer\map_00211B98_00211C10.bin
        INCBIN  build\mapcontainer\map_00211C10_00211C2C.bin
        INCBIN  build\mapcontainer\map_00211C2C_00211CE0.bin
        INCBIN  build\mapcontainer\map_00211CE0_00211CFC.bin
        INCBIN  build\mapcontainer\map_00211CFC_00211D70.bin
        INCBIN  build\mapcontainer\map_00211D70_00211D8C.bin
        INCBIN  build\mapcontainer\map_00211D8C_00211E08.bin
|unk_08211E08|
        INCBIN  build\mapcontainer\map_00211E08_00211E68.bin
|unk_08211E68|
        INCBIN  build\mapcontainer\map_00211E68_00211E74.bin
        INCBIN  build\mapcontainer\map_00211E74_00211EC4.bin
        INCBIN  build\mapcontainer\map_00211EC4_00211EFC.bin
        INCBIN  build\mapcontainer\map_00211EFC_00211F18.bin
        INCBIN  build\mapcontainer\map_00211F18_00211F8C.bin
        INCBIN  build\mapcontainer\map_00211F8C_00211FA8.bin
        INCBIN  build\mapcontainer\map_00211FA8_002120BC.bin
        INCBIN  build\mapcontainer\map_002120BC_002120D8.bin
        INCBIN  build\mapcontainer\map_002120D8_00212140.bin
        INCBIN  build\mapcontainer\map_00212140_0021215C.bin
        INCBIN  build\mapcontainer\map_0021215C_002121E4.bin
|unk_082121E4|
        INCBIN  build\mapcontainer\map_002121E4_00212214.bin
|unk_08212214|
        INCBIN  build\mapcontainer\map_00212214_0021221C.bin
        INCBIN  build\mapcontainer\map_0021221C_0021226C.bin
        INCBIN  build\mapcontainer\map_0021226C_002123C8.bin
        INCBIN  build\mapcontainer\map_002123C8_002123E4.bin
        INCBIN  build\mapcontainer\map_002123E4_00212450.bin
        INCBIN  build\mapcontainer\map_00212450_0021246C.bin
        INCBIN  build\mapcontainer\map_0021246C_0021258C.bin
        INCBIN  build\mapcontainer\map_0021258C_002125A8.bin
        INCBIN  build\mapcontainer\map_002125A8_002127E0.bin
        INCBIN  build\mapcontainer\map_002127E0_002127FC.bin
        INCBIN  build\mapcontainer\map_002127FC_002128C8.bin
|unk_082128C8|
        INCBIN  build\mapcontainer\map_002128C8_002128F8.bin
|unk_082128F8|
        INCBIN  build\mapcontainer\map_002128F8_00212900.bin
        INCBIN  build\mapcontainer\map_00212900_00212950.bin
        INCBIN  build\mapcontainer\map_00212950_00212B24.bin
        INCBIN  build\mapcontainer\map_00212B24_00212B44.bin
        INCBIN  build\mapcontainer\map_00212B44_00212BF8.bin
        INCBIN  build\mapcontainer\map_00212BF8_00212C18.bin
        INCBIN  build\mapcontainer\map_00212C18_00212FC0.bin
        INCBIN  build\mapcontainer\map_00212FC0_00212FE0.bin
        INCBIN  build\mapcontainer\map_00212FE0_00213280.bin
        INCBIN  build\mapcontainer\map_00213280_002132A0.bin
        INCBIN  build\mapcontainer\map_002132A0_002133A4.bin
|unk_082133A4|
        INCBIN  build\animframe\gen_2133a4_213514.bin
|unk_08213514|
        INCBIN  build\mapcontainer\map_00213514_002135A4.bin
|unk_082135A4|
        INCBIN  build\mapcontainer\map_002135A4_002135B4.bin
        INCBIN  build\mapcontainer\map_002135B4_00213604.bin
        INCBIN  build\mapcontainer\map_00213604_00213718.bin
        INCBIN  build\mapcontainer\map_00213718_00213738.bin
        INCBIN  build\mapcontainer\map_00213738_00213780.bin
        INCBIN  build\mapcontainer\map_00213780_0021379C.bin
        INCBIN  build\mapcontainer\map_0021379C_002139EC.bin
        INCBIN  build\mapcontainer\map_002139EC_00213A0C.bin
        INCBIN  build\mapcontainer\map_00213A0C_00213BE0.bin
        INCBIN  build\mapcontainer\map_00213BE0_00213C00.bin
        INCBIN  build\mapcontainer\map_00213C00_00213CFC.bin
|unk_08213CFC|
        INCBIN  build\mapcontainer\map_00213CFC_00213D2C.bin
|unk_08213D2C|
        INCBIN  build\mapcontainer\map_00213D2C_00213D34.bin
        INCBIN  build\mapcontainer\map_00213D34_00213D84.bin
        INCBIN  build\mapcontainer\map_00213D84_00213E28.bin
        INCBIN  build\mapcontainer\map_00213E28_00213E44.bin
        INCBIN  build\mapcontainer\map_00213E44_00213F3C.bin
        INCBIN  build\mapcontainer\map_00213F3C_00213F58.bin
        INCBIN  build\mapcontainer\map_00213F58_002140C8.bin
        INCBIN  build\mapcontainer\map_002140C8_002140E4.bin
        INCBIN  build\mapcontainer\map_002140E4_0021417C.bin
        INCBIN  build\mapcontainer\map_0021417C_00214198.bin
        INCBIN  build\mapcontainer\map_00214198_0021426C.bin
|unk_0821426C|
        INCBIN  build\mapcontainer\map_0021426C_0021429C.bin
|unk_0821429C|
        INCBIN  build\mapcontainer\map_0021429C_002142A4.bin
        INCBIN  build\mapcontainer\map_002142A4_002142F4.bin
        INCBIN  build\mapcontainer\map_002142F4_002143B4.bin
        INCBIN  build\mapcontainer\map_002143B4_002143D4.bin
        INCBIN  build\mapcontainer\map_002143D4_00214670.bin
        INCBIN  build\mapcontainer\map_00214670_00214690.bin
        INCBIN  build\mapcontainer\map_00214690_00214850.bin
        INCBIN  build\mapcontainer\map_00214850_00214870.bin
        INCBIN  build\mapcontainer\map_00214870_00214964.bin
|unk_08214964|
        INCBIN  build\mapcontainer\map_00214964_00214994.bin
|unk_08214994|
        INCBIN  build\mapcontainer\map_00214994_0021499C.bin
        INCBIN  build\mapcontainer\map_0021499C_002149EC.bin
        INCBIN  build\mapcontainer\map_002149EC_00214AF8.bin
        INCBIN  build\mapcontainer\map_00214AF8_00214B18.bin
        INCBIN  build\mapcontainer\map_00214B18_00214CC8.bin
        INCBIN  build\mapcontainer\map_00214CC8_00214CE8.bin
        INCBIN  build\mapcontainer\map_00214CE8_00214E84.bin
        INCBIN  build\mapcontainer\map_00214E84_00214EA4.bin
        INCBIN  build\mapcontainer\map_00214EA4_00215020.bin
        INCBIN  build\mapcontainer\map_00215020_00215040.bin
        INCBIN  build\mapcontainer\map_00215040_00215100.bin
|unk_08215100|
        INCBIN  build\mapcontainer\map_00215100_00215160.bin
|unk_08215160|
        INCBIN  build\mapcontainer\map_00215160_00215178.bin
|unk_08215178|
        INCBIN  build\mapcontainer\map_00215178_0021517C.bin
        INCBIN  build\mapcontainer\map_0021517C_002151CC.bin
        INCBIN  build\mapcontainer\map_002151CC_00215320.bin
        INCBIN  build\mapcontainer\map_00215320_0021533C.bin
        INCBIN  build\mapcontainer\map_0021533C_00215410.bin
        INCBIN  build\mapcontainer\map_00215410_0021542C.bin
        INCBIN  build\mapcontainer\map_0021542C_002155B8.bin
        INCBIN  build\mapcontainer\map_002155B8_002155D4.bin
        INCBIN  build\mapcontainer\map_002155D4_002158BC.bin
        INCBIN  build\mapcontainer\map_002158BC_002158D8.bin
        INCBIN  build\mapcontainer\map_002158D8_00215938.bin
|unk_08215938|
        INCBIN  build\mapcontainer\map_00215938_00215950.bin
|unk_08215950|
        INCBIN  build\mapcontainer\map_00215950_00215954.bin
        INCBIN  build\mapcontainer\map_00215954_002159A4.bin
        INCBIN  build\mapcontainer\map_002159A4_00215A34.bin
        INCBIN  build\mapcontainer\map_00215A34_00215A50.bin
        INCBIN  build\mapcontainer\map_00215A50_00215AE8.bin
        INCBIN  build\mapcontainer\map_00215AE8_00215B04.bin
        INCBIN  build\mapcontainer\map_00215B04_00215C94.bin
        INCBIN  build\mapcontainer\map_00215C94_00215CB0.bin
        INCBIN  build\mapcontainer\map_00215CB0_00215E44.bin
        INCBIN  build\mapcontainer\map_00215E44_00215E60.bin
        INCBIN  build\mapcontainer\map_00215E60_00215F20.bin
|unk_08215F20|
        INCBIN  build\mapcontainer\map_00215F20_00215F98.bin
|unk_08215F98|
        INCBIN  build\animframe\gen_215f98_2161ac.bin
|map_anim_row_082161AC|
|unk_082161AC|
	DCB 0x03,0x06
	DCW 0x037a
	DCD 0x08215f98,0x0821604c,0x08216100
|unk_082161BC|
        INCBIN  build\animframe\gen_2161bc_2162ec.bin
|map_anim_row_082162EC|
|unk_082162EC|
	DCB 0x04,0x02
	DCW 0x0378
	DCD 0x082161bc,0x08216208,0x08216254,0x082162a0
|unk_08216300|
        INCBIN  baserom.gba_0x216300_0x216308.extracted
|unk_08216308|
        INCBIN  build\mapcontainer\map_00216308_00216320.bin
|unk_08216320|
        INCBIN  build\mapcontainer\map_00216320_00216324.bin
        INCBIN  build\mapcontainer\map_00216324_00216374.bin
        INCBIN  build\mapcontainer\map_00216374_002163D4.bin
        INCBIN  build\mapcontainer\map_002163D4_002163F0.bin
        INCBIN  build\mapcontainer\map_002163F0_002164D0.bin
        INCBIN  build\mapcontainer\map_002164D0_002164EC.bin
        INCBIN  build\mapcontainer\map_002164EC_00216534.bin
        INCBIN  build\mapcontainer\map_00216534_00216550.bin
        INCBIN  build\mapcontainer\map_00216550_00216668.bin
        INCBIN  build\mapcontainer\map_00216668_00216684.bin
        INCBIN  build\mapcontainer\map_00216684_00216718.bin
|unk_08216718|
        INCBIN  build\mapcontainer\map_00216718_00216790.bin
        INCBIN  build\mapcontainer\map_00216790_002169FC.bin
|unk_082169FC|
        INCBIN  build\mapcontainer\map_002169FC_00216A14.bin
|unk_08216A14|
        INCBIN  build\mapcontainer\map_00216A14_00216A18.bin
        INCBIN  build\mapcontainer\map_00216A18_00216A68.bin
        INCBIN  build\mapcontainer\map_00216A68_00216AE8.bin
        INCBIN  build\mapcontainer\map_00216AE8_00216B04.bin
        INCBIN  build\mapcontainer\map_00216B04_00216BA0.bin
        INCBIN  build\mapcontainer\map_00216BA0_00216BBC.bin
        INCBIN  build\mapcontainer\map_00216BBC_00216C8C.bin
        INCBIN  build\mapcontainer\map_00216C8C_00216CA8.bin
        INCBIN  build\mapcontainer\map_00216CA8_00216E34.bin
        INCBIN  build\mapcontainer\map_00216E34_00216E50.bin
        INCBIN  build\mapcontainer\map_00216E50_00216F28.bin
|unk_08216F28|
        INCBIN  build\mapcontainer\map_00216F28_00216FD0.bin
        INCBIN  build\mapcontainer\map_00216FD0_00217150.bin
|unk_08217150|
        INCBIN  build\mapcontainer\map_00217150_00217180.bin
|unk_08217180|
        INCBIN  build\mapcontainer\map_00217180_00217188.bin
        INCBIN  build\mapcontainer\map_00217188_002171D8.bin
        INCBIN  build\mapcontainer\map_002171D8_00217298.bin
        INCBIN  build\mapcontainer\map_00217298_002172B4.bin
        INCBIN  build\mapcontainer\map_002172B4_0021733C.bin
        INCBIN  build\mapcontainer\map_0021733C_00217358.bin
        INCBIN  build\mapcontainer\map_00217358_002173CC.bin
        INCBIN  build\mapcontainer\map_002173CC_002173E8.bin
        INCBIN  build\mapcontainer\map_002173E8_002175E0.bin
        INCBIN  build\mapcontainer\map_002175E0_002175FC.bin
        INCBIN  build\mapcontainer\map_002175FC_002176BC.bin
|unk_082176BC|
        INCBIN  build\mapcontainer\map_002176BC_002176EC.bin
|unk_082176EC|
        INCBIN  build\animframe\gen_2176ec_2177b4.bin
|unk_082177B4|
        INCBIN  build\mapcontainer\map_002177B4_00217800.bin
|unk_08217800|
        INCBIN  build\mapcontainer\map_00217800_00217808.bin
        INCBIN  build\mapcontainer\map_00217808_00217858.bin
        INCBIN  build\mapcontainer\map_00217858_002178B8.bin
        INCBIN  build\mapcontainer\map_002178B8_002178D4.bin
        INCBIN  build\mapcontainer\map_002178D4_00217908.bin
        INCBIN  build\mapcontainer\map_00217908_00217924.bin
        INCBIN  build\mapcontainer\map_00217924_00217A18.bin
        INCBIN  build\mapcontainer\map_00217A18_00217A34.bin
        INCBIN  build\mapcontainer\map_00217A34_00217C48.bin
        INCBIN  build\mapcontainer\map_00217C48_00217C64.bin
        INCBIN  build\mapcontainer\map_00217C64_00217D30.bin
|unk_08217D30|
        INCBIN  build\mapcontainer\map_00217D30_00217DC0.bin
        INCBIN  build\mapcontainer\map_00217DC0_00217F88.bin
|unk_08217F88|
        INCBIN  build\mapcontainer\map_00217F88_00217FD4.bin
|unk_08217FD4|
        INCBIN  build\mapcontainer\map_00217FD4_00217FDC.bin
        INCBIN  build\mapcontainer\map_00217FDC_0021802C.bin
        INCBIN  build\mapcontainer\map_0021802C_002183FC.bin
        INCBIN  build\mapcontainer\map_002183FC_00218424.bin
        INCBIN  build\mapcontainer\map_00218424_002185B0.bin
        INCBIN  build\mapcontainer\map_002185B0_002185D8.bin
        INCBIN  build\mapcontainer\map_002185D8_002187FC.bin
        INCBIN  build\mapcontainer\map_002187FC_00218824.bin
        INCBIN  build\mapcontainer\map_00218824_00218CCC.bin
        INCBIN  build\mapcontainer\map_00218CCC_00218CF4.bin
        INCBIN  build\mapcontainer\map_00218CF4_00218E6C.bin
|unk_08218E6C|
        INCBIN  build\mapcontainer\map_00218E6C_00218EE4.bin
        INCBIN  build\mapcontainer\map_00218EE4_00219044.bin
|unk_08219044|
        INCBIN  build\mapcontainer\map_00219044_002190A4.bin
|unk_082190A4|
        INCBIN  build\mapcontainer\map_002190A4_002190B4.bin
        INCBIN  build\mapcontainer\map_002190B4_00219104.bin
        INCBIN  build\mapcontainer\map_00219104_002191E4.bin
        INCBIN  build\mapcontainer\map_002191E4_00219204.bin
        INCBIN  build\mapcontainer\map_00219204_002193A4.bin
        INCBIN  build\mapcontainer\map_002193A4_002193C4.bin
        INCBIN  build\mapcontainer\map_002193C4_002195CC.bin
        INCBIN  build\mapcontainer\map_002195CC_002195EC.bin
        INCBIN  build\mapcontainer\map_002195EC_0021986C.bin
        INCBIN  build\mapcontainer\map_0021986C_0021988C.bin
        INCBIN  build\mapcontainer\map_0021988C_002199A4.bin
|unk_082199A4|
        INCBIN  build\mapcontainer\map_002199A4_002199D4.bin
|unk_082199D4|
        INCBIN  build\mapcontainer\map_002199D4_002199DC.bin
        INCBIN  build\mapcontainer\map_002199DC_00219A2C.bin
        INCBIN  build\mapcontainer\map_00219A2C_00219AEC.bin
        INCBIN  build\mapcontainer\map_00219AEC_00219B08.bin
        INCBIN  build\mapcontainer\map_00219B08_00219C78.bin
        INCBIN  build\mapcontainer\map_00219C78_00219C94.bin
        INCBIN  build\mapcontainer\map_00219C94_00219CF8.bin
        INCBIN  build\mapcontainer\map_00219CF8_00219D14.bin
        INCBIN  build\mapcontainer\map_00219D14_00219DB0.bin
|unk_08219DB0|
        INCBIN  build\mapcontainer\map_00219DB0_00219DE0.bin
|unk_08219DE0|
        INCBIN  build\mapcontainer\map_00219DE0_00219DE8.bin
        INCBIN  build\mapcontainer\map_00219DE8_00219E38.bin
        INCBIN  build\mapcontainer\map_00219E38_0021A250.bin
        INCBIN  build\mapcontainer\map_0021A250_0021A278.bin
        INCBIN  build\mapcontainer\map_0021A278_0021A5D0.bin
        INCBIN  build\mapcontainer\map_0021A5D0_0021A5F8.bin
        INCBIN  build\mapcontainer\map_0021A5F8_0021AA3C.bin
        INCBIN  build\mapcontainer\map_0021AA3C_0021AA64.bin
        INCBIN  build\mapcontainer\map_0021AA64_0021ACA4.bin
        INCBIN  build\mapcontainer\map_0021ACA4_0021ACCC.bin
        INCBIN  build\mapcontainer\map_0021ACCC_0021AE40.bin
|unk_0821AE40|
        INCBIN  build\mapcontainer\map_0021AE40_0021AEA0.bin
|unk_0821AEA0|
        INCBIN  build\mapcontainer\map_0021AEA0_0021AEA8.bin
        INCBIN  build\mapcontainer\map_0021AEA8_0021AEF8.bin
        INCBIN  build\mapcontainer\map_0021AEF8_0021AFC0.bin
        INCBIN  build\mapcontainer\map_0021AFC0_0021AFDC.bin
        INCBIN  build\mapcontainer\map_0021AFDC_0021B094.bin
        INCBIN  build\mapcontainer\map_0021B094_0021B0B4.bin
        INCBIN  build\mapcontainer\map_0021B0B4_0021B310.bin
        INCBIN  build\mapcontainer\map_0021B310_0021B330.bin
        INCBIN  build\mapcontainer\map_0021B330_0021B470.bin
        INCBIN  build\mapcontainer\map_0021B470_0021B490.bin
        INCBIN  build\mapcontainer\map_0021B490_0021B5A8.bin
|unk_0821B5A8|
        INCBIN  build\mapcontainer\map_0021B5A8_0021B5D8.bin
|unk_0821B5D8|
        INCBIN  build\mapcontainer\map_0021B5D8_0021B5E0.bin
        INCBIN  build\mapcontainer\map_0021B5E0_0021B630.bin
        INCBIN  build\mapcontainer\map_0021B630_0021B830.bin
        INCBIN  build\mapcontainer\map_0021B830_0021B850.bin
        INCBIN  build\mapcontainer\map_0021B850_0021B9A8.bin
        INCBIN  build\mapcontainer\map_0021B9A8_0021B9C8.bin
        INCBIN  build\mapcontainer\map_0021B9C8_0021BC8C.bin
        INCBIN  build\mapcontainer\map_0021BC8C_0021BCAC.bin
        INCBIN  build\mapcontainer\map_0021BCAC_0021BF08.bin
        INCBIN  build\mapcontainer\map_0021BF08_0021BF28.bin
        INCBIN  build\mapcontainer\map_0021BF28_0021C070.bin
|unk_0821C070|
        INCBIN  build\mapcontainer\map_0021C070_0021C0B8.bin
|unk_0821C0B8|
        INCBIN  build\mapcontainer\map_0021C0B8_0021C0C4.bin
        INCBIN  build\mapcontainer\map_0021C0C4_0021C114.bin
        INCBIN  build\mapcontainer\map_0021C114_0021C26C.bin
        INCBIN  build\mapcontainer\map_0021C26C_0021C28C.bin
        INCBIN  build\mapcontainer\map_0021C28C_0021C318.bin
        INCBIN  build\mapcontainer\map_0021C318_0021C338.bin
        INCBIN  build\mapcontainer\map_0021C338_0021C670.bin
        INCBIN  build\mapcontainer\map_0021C670_0021C690.bin
        INCBIN  build\mapcontainer\map_0021C690_0021C900.bin
        INCBIN  build\mapcontainer\map_0021C900_0021C920.bin
        INCBIN  build\mapcontainer\map_0021C920_0021CA44.bin
|unk_0821CA44|
        INCBIN  build\mapcontainer\map_0021CA44_0021CA74.bin
|unk_0821CA74|
        INCBIN  build\mapcontainer\map_0021CA74_0021CA7C.bin
        INCBIN  build\mapcontainer\map_0021CA7C_0021CACC.bin
        INCBIN  build\mapcontainer\map_0021CACC_0021CB20.bin
        INCBIN  build\mapcontainer\map_0021CB20_0021CB3C.bin
        INCBIN  build\mapcontainer\map_0021CB3C_0021CD2C.bin
        INCBIN  build\mapcontainer\map_0021CD2C_0021CD54.bin
        INCBIN  build\mapcontainer\map_0021CD54_0021D1A8.bin
        INCBIN  build\mapcontainer\map_0021D1A8_0021D1D0.bin
        INCBIN  build\mapcontainer\map_0021D1D0_0021D390.bin
        INCBIN  build\mapcontainer\map_0021D390_0021D3B8.bin
        INCBIN  build\mapcontainer\map_0021D3B8_0021D4D4.bin
|unk_0821D4D4|
        INCBIN  build\mapcontainer\map_0021D4D4_0021D534.bin
|unk_0821D534|
        INCBIN  build\mapcontainer\map_0021D534_0021D53C.bin
        INCBIN  build\mapcontainer\map_0021D53C_0021D58C.bin
        INCBIN  build\mapcontainer\map_0021D58C_0021D60C.bin
        INCBIN  build\mapcontainer\map_0021D60C_0021D62C.bin
        INCBIN  build\mapcontainer\map_0021D62C_0021D7D4.bin
        INCBIN  build\mapcontainer\map_0021D7D4_0021D7F4.bin
        INCBIN  build\mapcontainer\map_0021D7F4_0021DB84.bin
        INCBIN  build\mapcontainer\map_0021DB84_0021DBA4.bin
        INCBIN  build\mapcontainer\map_0021DBA4_0021DC64.bin
        INCBIN  build\mapcontainer\map_0021DC64_0021DC84.bin
        INCBIN  build\mapcontainer\map_0021DC84_0021DD88.bin
|map_anim_row_0821DD88|
|unk_0821DD88|
	DCB 0x04,0x03
	DCW 0x037d
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|unk_0821DD9C|
        INCBIN  build\animframe\gen_21dd9c_21e0b4.bin
|map_anim_row_0821E0B4|
|unk_0821E0B4|
	DCB 0x04,0x12
	DCW 0x036b
	DCD 0x0821dd9c,0x0821dea0,0x0821dfa8,0x0821dea0
|unk_0821E0C8|
        INCBIN  baserom.gba_0x21e0c8_0x21e0d0.extracted
|unk_0821E0D0|
        INCBIN  build\mapcontainer\map_0021E0D0_0021E100.bin
|unk_0821E100|
        INCBIN  build\mapcontainer\map_0021E100_0021E108.bin
        INCBIN  build\mapcontainer\map_0021E108_0021E158.bin
        INCBIN  build\mapcontainer\map_0021E158_0021E188.bin
        INCBIN  build\mapcontainer\map_0021E188_0021E1A4.bin
        INCBIN  build\mapcontainer\map_0021E1A4_0021E28C.bin
        INCBIN  build\mapcontainer\map_0021E28C_0021E2AC.bin
        INCBIN  build\mapcontainer\map_0021E2AC_0021E594.bin
        INCBIN  build\mapcontainer\map_0021E594_0021E5B4.bin
        INCBIN  build\mapcontainer\map_0021E5B4_0021E724.bin
        INCBIN  build\mapcontainer\map_0021E724_0021E744.bin
        INCBIN  build\mapcontainer\map_0021E744_0021E878.bin
|unk_0821E878|
        INCBIN  build\animframe\gen_21e878_21ee20.bin
|unk_0821EE20|
        INCBIN  build\mapcontainer\map_0021EE20_0021EEB8.bin
|unk_0821EEB8|
        INCBIN  build\mapcontainer\map_0021EEB8_0021EEC0.bin
        INCBIN  build\mapcontainer\map_0021EEC0_0021EF10.bin
        INCBIN  build\mapcontainer\map_0021EF10_0021EFDC.bin
        INCBIN  build\mapcontainer\map_0021EFDC_0021EFFC.bin
        INCBIN  build\mapcontainer\map_0021EFFC_0021F1C8.bin
        INCBIN  build\mapcontainer\map_0021F1C8_0021F1F0.bin
        INCBIN  build\mapcontainer\map_0021F1F0_0021F574.bin
        INCBIN  build\mapcontainer\map_0021F574_0021F59C.bin
        INCBIN  build\mapcontainer\map_0021F59C_0021F808.bin
        INCBIN  build\mapcontainer\map_0021F808_0021F830.bin
        INCBIN  build\mapcontainer\map_0021F830_0021F99C.bin
|unk_0821F99C|
        INCBIN  build\mapcontainer\map_0021F99C_0021F9CC.bin
        INCBIN  build\mapcontainer\map_0021F9CC_0021FC4C.bin
        INCLUDE rawlabeled_21fc4c.s
        INCBIN  build\mapcontainer\map_002205F8_00220648.bin
        INCBIN  build\mapcontainer\map_00220648_00220804.bin
|unk_08220804|
        INCBIN  build\mapcontainer\map_00220804_0022082C.bin
        INCBIN  build\jcalg1\gen_22082c.bin
|unk_08220EEC|
        INCBIN  build\mapcontainer\map_00220EEC_00220F14.bin
        INCBIN  build\jcalg1\gen_220f14.bin
|unk_08221418|
        INCBIN  build\mapcontainer\map_00221418_00221440.bin
        INCBIN  build\jcalg1\gen_221440.bin
|unk_08221884|
        INCBIN  build\mapcontainer\map_00221884_002218AC.bin
        INCBIN  build\jcalg1\gen_2218ac.bin
|unk_08221A08|
        INCBIN  build\mapcontainer\map_00221A08_00221A50.bin
        INCBIN  build\jcalg1\gen_221a50.bin
|unk_0822229C|
        INCBIN  build\mapcontainer\map_0022229C_002222EC.bin
        INCBIN  build\mapcontainer\map_002222EC_002224A8.bin
        INCBIN  build\mapcontainer\map_002224A8_002224D0.bin
        INCBIN  build\mapcontainer\map_002224D0_00222A44.bin
        INCBIN  build\mapcontainer\map_00222A44_00222A6C.bin
        INCBIN  build\mapcontainer\map_00222A6C_00222F84.bin
        INCBIN  build\mapcontainer\map_00222F84_00222FAC.bin
        INCBIN  build\mapcontainer\map_00222FAC_00223040.bin
|unk_08223040|
        INCBIN  build\mapcontainer\map_00223040_00223070.bin
        INCBIN  build\mapcontainer\map_00223070_002237C8.bin
        INCBIN  build\mapcontainer\map_002237C8_00223818.bin
        INCBIN  build\mapcontainer\map_00223818_00223A88.bin
        INCBIN  build\mapcontainer\map_00223A88_00223AB8.bin
        INCBIN  build\mapcontainer\map_00223AB8_00224010.bin
        INCBIN  build\mapcontainer\map_00224010_00224040.bin
        INCBIN  build\mapcontainer\map_00224040_00224590.bin
        INCBIN  build\mapcontainer\map_00224590_002245C0.bin
        INCBIN  build\mapcontainer\map_002245C0_002246E0.bin
|unk_082246E0|
        INCBIN  build\mapcontainer\map_002246E0_00224758.bin
        INCBIN  build\mapcontainer\map_00224758_00224C18.bin
        INCBIN  build\mapcontainer\map_00224C18_00224C68.bin
        INCBIN  build\mapcontainer\map_00224C68_00224D74.bin
        INCBIN  build\mapcontainer\map_00224D74_00224D94.bin
        INCBIN  build\mapcontainer\map_00224D94_00224E8C.bin
        INCBIN  build\mapcontainer\map_00224E8C_00224EA8.bin
        INCBIN  build\mapcontainer\map_00224EA8_00224F8C.bin
        INCBIN  build\mapcontainer\map_00224F8C_00224FAC.bin
        INCBIN  build\mapcontainer\map_00224FAC_00225024.bin
|unk_08225024|
        INCBIN  build\animframe\gen_225024_2250b4.bin
|unk_082250B4|
        INCBIN  build\mapcontainer\map_002250B4_002250CC.bin
        INCBIN  build\mapcontainer\map_002250CC_0022511C.bin
        INCBIN  build\mapcontainer\map_0022511C_00225414.bin
        INCBIN  build\mapcontainer\map_00225414_0022543C.bin
        INCBIN  build\mapcontainer\map_0022543C_00225B10.bin
        INCBIN  build\mapcontainer\map_00225B10_00225B38.bin
        INCBIN  build\mapcontainer\map_00225B38_00225DE8.bin
        INCBIN  build\mapcontainer\map_00225DE8_00225E10.bin
        INCBIN  build\mapcontainer\map_00225E10_00225FB8.bin
|unk_08225FB8|
        INCBIN  build\animframe\gen_225fb8_2260a0.bin
|map_anim_row_082260A0|
|unk_082260A0|
	DCB 0x04,0x08
	DCW 0x0378
	DCD 0x08225fb8,0x08225ff4,0x0822602c,0x08226064
|unk_082260B4|
        INCBIN  build\animframe\gen_2260b4_2264f8.bin
|map_anim_row_082264F8|
|unk_082264F8|
	DCB 0x04,0x13
	DCW 0x0365
	DCD 0x082260b4,0x082261c4,0x082262d0,0x082263ec
|unk_0822650C|
        INCBIN  baserom.gba_0x22650c_0x226514.extracted
        INCBIN  build\mapcontainer\map_00226514_00226564.bin
        INCBIN  build\mapcontainer\map_00226564_0022660C.bin
        INCBIN  build\mapcontainer\map_0022660C_00226628.bin
        INCBIN  build\mapcontainer\map_00226628_00226704.bin
        INCBIN  build\mapcontainer\map_00226704_00226720.bin
        INCBIN  build\mapcontainer\map_00226720_002267B0.bin
        INCBIN  build\mapcontainer\map_002267B0_002267CC.bin
        INCBIN  build\mapcontainer\map_002267CC_00226848.bin
|unk_08226848|
        INCBIN  build\mapcontainer\map_00226848_00226878.bin
        INCBIN  build\mapcontainer\map_00226878_002268FC.bin
        INCBIN  build\mapcontainer\map_002268FC_0022694C.bin
        INCBIN  build\mapcontainer\map_0022694C_002269E0.bin
        INCBIN  build\mapcontainer\map_002269E0_002269FC.bin
        INCBIN  build\mapcontainer\map_002269FC_00226ACC.bin
        INCBIN  build\mapcontainer\map_00226ACC_00226AE8.bin
        INCBIN  build\mapcontainer\map_00226AE8_00226B68.bin
        INCBIN  build\mapcontainer\map_00226B68_00226B84.bin
        INCBIN  build\mapcontainer\map_00226B84_00226BFC.bin
|unk_08226BFC|
        INCBIN  build\mapcontainer\map_00226BFC_00226C44.bin
        INCBIN  build\mapcontainer\map_00226C44_00226C6C.bin
        INCBIN  build\mapcontainer\map_00226C6C_00226CBC.bin
        INCBIN  build\mapcontainer\map_00226CBC_00226DD4.bin
        INCBIN  build\mapcontainer\map_00226DD4_00226DF4.bin
        INCBIN  build\mapcontainer\map_00226DF4_00226F2C.bin
        INCBIN  build\mapcontainer\map_00226F2C_00226F4C.bin
        INCBIN  build\mapcontainer\map_00226F4C_00227074.bin
        INCBIN  build\mapcontainer\map_00227074_00227094.bin
        INCBIN  build\mapcontainer\map_00227094_00227120.bin
|unk_08227120|
        INCBIN  build\mapcontainer\map_00227120_00227150.bin
        INCBIN  build\mapcontainer\map_00227150_002272A8.bin
        INCBIN  build\mapcontainer\map_002272A8_002272F8.bin
        INCBIN  build\mapcontainer\map_002272F8_002273A4.bin
        INCBIN  build\mapcontainer\map_002273A4_002273C0.bin
        INCBIN  build\mapcontainer\map_002273C0_002273EC.bin
        INCBIN  build\mapcontainer\map_002273EC_00227408.bin
        INCBIN  build\mapcontainer\map_00227408_0022750C.bin
        INCBIN  build\mapcontainer\map_0022750C_00227528.bin
        INCBIN  build\mapcontainer\map_00227528_002275B8.bin
        INCBIN  build\mapcontainer\map_002275B8_002275D4.bin
        INCBIN  build\mapcontainer\map_002275D4_0022766C.bin
|unk_0822766C|
        INCBIN  build\mapcontainer\map_0022766C_00227684.bin
        INCBIN  build\mapcontainer\map_00227684_002277B8.bin
        INCBIN  build\mapcontainer\map_002277B8_00227808.bin
        INCBIN  build\mapcontainer\map_00227808_002278B4.bin
        INCBIN  build\mapcontainer\map_002278B4_002278D0.bin
        INCBIN  build\mapcontainer\map_002278D0_002279BC.bin
        INCBIN  build\mapcontainer\map_002279BC_002279D8.bin
        INCBIN  build\mapcontainer\map_002279D8_00227A64.bin
        INCBIN  build\mapcontainer\map_00227A64_00227A80.bin
        INCBIN  build\mapcontainer\map_00227A80_00227ADC.bin
|unk_08227ADC|
        INCBIN  build\mapcontainer\map_00227ADC_00227B0C.bin
        INCBIN  build\mapcontainer\map_00227B0C_00227B5C.bin
        INCBIN  build\mapcontainer\map_00227B5C_00227BF0.bin
        INCBIN  build\mapcontainer\map_00227BF0_00227C0C.bin
        INCBIN  build\mapcontainer\map_00227C0C_00227C34.bin
        INCBIN  build\mapcontainer\map_00227C34_00227C50.bin
        INCBIN  build\mapcontainer\map_00227C50_00227D3C.bin
        INCBIN  build\mapcontainer\map_00227D3C_00227D58.bin
        INCBIN  build\mapcontainer\map_00227D58_00227DE8.bin
        INCBIN  build\mapcontainer\map_00227DE8_00227E04.bin
        INCBIN  build\mapcontainer\map_00227E04_00227E8C.bin
|unk_08227E8C|
        INCBIN  build\mapcontainer\map_00227E8C_00227EA4.bin
        INCBIN  build\mapcontainer\map_00227EA4_00227EF4.bin
        INCBIN  build\mapcontainer\map_00227EF4_00227F7C.bin
        INCBIN  build\mapcontainer\map_00227F7C_00227F98.bin
        INCBIN  build\mapcontainer\map_00227F98_00228014.bin
        INCBIN  build\mapcontainer\map_00228014_00228030.bin
        INCBIN  build\mapcontainer\map_00228030_002280BC.bin
        INCBIN  build\mapcontainer\map_002280BC_002280D8.bin
        INCBIN  build\mapcontainer\map_002280D8_00228154.bin
|unk_08228154|
        INCBIN  build\mapcontainer\map_00228154_0022816C.bin
        INCBIN  build\mapcontainer\map_0022816C_00228290.bin
        INCBIN  build\mapcontainer\map_00228290_002282E0.bin
        INCBIN  build\mapcontainer\map_002282E0_002283B0.bin
        INCBIN  build\mapcontainer\map_002283B0_002283CC.bin
        INCBIN  build\mapcontainer\map_002283CC_00228400.bin
        INCBIN  build\mapcontainer\map_00228400_0022841C.bin
        INCBIN  build\mapcontainer\map_0022841C_00228520.bin
        INCBIN  build\mapcontainer\map_00228520_0022853C.bin
        INCBIN  build\mapcontainer\map_0022853C_002285C8.bin
        INCBIN  build\mapcontainer\map_002285C8_002285E4.bin
        INCBIN  build\mapcontainer\map_002285E4_00228684.bin
|unk_08228684|
        INCBIN  build\mapcontainer\map_00228684_002286B4.bin
        INCBIN  build\mapcontainer\map_002286B4_00228704.bin
        INCBIN  build\mapcontainer\map_00228704_0022879C.bin
        INCBIN  build\mapcontainer\map_0022879C_002287B8.bin
        INCBIN  build\mapcontainer\map_002287B8_002288C4.bin
        INCBIN  build\mapcontainer\map_002288C4_002288E0.bin
        INCBIN  build\mapcontainer\map_002288E0_00228970.bin
        INCBIN  build\mapcontainer\map_00228970_0022898C.bin
        INCBIN  build\mapcontainer\map_0022898C_00228A20.bin
|unk_08228A20|
        INCBIN  build\mapcontainer\map_00228A20_00228A68.bin
        INCBIN  build\mapcontainer\map_00228A68_00228C10.bin
        INCBIN  build\mapcontainer\map_00228C10_00228C60.bin
        INCBIN  build\mapcontainer\map_00228C60_00228D14.bin
        INCBIN  build\mapcontainer\map_00228D14_00228D30.bin
        INCBIN  build\mapcontainer\map_00228D30_00228DCC.bin
        INCBIN  build\mapcontainer\map_00228DCC_00228E04.bin
        INCBIN  build\mapcontainer\map_00228E04_00228E84.bin
        INCBIN  build\mapcontainer\map_00228E84_00228ED4.bin
        INCBIN  build\mapcontainer\map_00228ED4_00228F84.bin
        INCBIN  build\mapcontainer\map_00228F84_00228FA0.bin
        INCBIN  build\mapcontainer\map_00228FA0_00229084.bin
        INCBIN  build\mapcontainer\map_00229084_002290A0.bin
        INCBIN  build\mapcontainer\map_002290A0_00229130.bin
        INCBIN  build\mapcontainer\map_00229130_0022914C.bin
        INCBIN  build\mapcontainer\map_0022914C_002291D8.bin
|unk_082291D8|
        INCBIN  build\mapcontainer\map_002291D8_00229208.bin
        INCBIN  build\mapcontainer\map_00229208_00229258.bin
        INCBIN  build\mapcontainer\map_00229258_002294D8.bin
        INCBIN  build\mapcontainer\map_002294D8_00229500.bin
        INCBIN  build\mapcontainer\map_00229500_00229C08.bin
        INCBIN  build\mapcontainer\map_00229C08_00229C30.bin
        INCBIN  build\mapcontainer\map_00229C30_00229DF0.bin
        INCBIN  build\mapcontainer\map_00229DF0_00229E18.bin
        INCBIN  build\mapcontainer\map_00229E18_00229F50.bin
        INCBIN  build\mapcontainer\map_00229F50_00229FA0.bin
        INCBIN  build\mapcontainer\map_00229FA0_0022A024.bin
        INCBIN  build\mapcontainer\map_0022A024_0022A040.bin
        INCBIN  build\mapcontainer\map_0022A040_0022A06C.bin
        INCBIN  build\mapcontainer\map_0022A06C_0022A088.bin
        INCBIN  build\mapcontainer\map_0022A088_0022A19C.bin
        INCBIN  build\mapcontainer\map_0022A19C_0022A1B8.bin
        INCBIN  build\mapcontainer\map_0022A1B8_0022A248.bin
        INCBIN  build\mapcontainer\map_0022A248_0022A264.bin
        INCBIN  build\mapcontainer\map_0022A264_0022A2FC.bin
|unk_0822A2FC|
        INCBIN  build\mapcontainer\map_0022A2FC_0022A32C.bin
        INCBIN  build\mapcontainer\map_0022A32C_0022A478.bin
        INCBIN  build\mapcontainer\map_0022A478_0022A4C8.bin
        INCBIN  build\mapcontainer\map_0022A4C8_0022A57C.bin
        INCBIN  build\mapcontainer\map_0022A57C_0022A598.bin
        INCBIN  build\mapcontainer\map_0022A598_0022A630.bin
        INCBIN  build\mapcontainer\map_0022A630_0022A64C.bin
        INCBIN  build\mapcontainer\map_0022A64C_0022A6CC.bin
        INCBIN  build\mapcontainer\map_0022A6CC_0022A6E8.bin
        INCBIN  build\mapcontainer\map_0022A6E8_0022A768.bin
|unk_0822A768|
        INCBIN  build\mapcontainer\map_0022A768_0022A798.bin
        INCBIN  build\mapcontainer\map_0022A798_0022A7E8.bin
        INCBIN  build\mapcontainer\map_0022A7E8_0022A8A8.bin
        INCBIN  build\mapcontainer\map_0022A8A8_0022A8C4.bin
        INCBIN  build\mapcontainer\map_0022A8C4_0022AA18.bin
        INCBIN  build\mapcontainer\map_0022AA18_0022AA40.bin
        INCBIN  build\mapcontainer\map_0022AA40_0022AD94.bin
        INCBIN  build\mapcontainer\map_0022AD94_0022ADBC.bin
        INCBIN  build\mapcontainer\map_0022ADBC_0022B090.bin
        INCBIN  build\mapcontainer\map_0022B090_0022B0B8.bin
        INCBIN  build\mapcontainer\map_0022B0B8_0022B178.bin
|unk_0822B178|
        INCBIN  build\mapcontainer\map_0022B178_0022B190.bin
        INCBIN  build\mapcontainer\map_0022B190_0022B1E0.bin
        INCBIN  build\mapcontainer\map_0022B1E0_0022B370.bin
        INCBIN  build\mapcontainer\map_0022B370_0022B398.bin
        INCBIN  build\mapcontainer\map_0022B398_0022B754.bin
        INCBIN  build\mapcontainer\map_0022B754_0022B77C.bin
        INCBIN  build\mapcontainer\map_0022B77C_0022B97C.bin
        INCBIN  build\mapcontainer\map_0022B97C_0022B9A4.bin
        INCBIN  build\mapcontainer\map_0022B9A4_0022BA74.bin
|unk_0822BA74|
        INCBIN  build\mapcontainer\map_0022BA74_0022BA8C.bin
        INCBIN  build\mapcontainer\map_0022BA8C_0022BB50.bin
        INCBIN  build\mapcontainer\map_0022BB50_0022BBA0.bin
        INCBIN  build\mapcontainer\map_0022BBA0_0022BCB8.bin
        INCBIN  build\mapcontainer\map_0022BCB8_0022BCD8.bin
        INCBIN  build\mapcontainer\map_0022BCD8_0022BED4.bin
        INCBIN  build\mapcontainer\map_0022BED4_0022BEF4.bin
        INCBIN  build\mapcontainer\map_0022BEF4_0022C038.bin
        INCBIN  build\mapcontainer\map_0022C038_0022C058.bin
        INCBIN  build\mapcontainer\map_0022C058_0022C11C.bin
|unk_0822C11C|
        INCBIN  build\mapcontainer\map_0022C11C_0022C1F4.bin
        INCBIN  build\mapcontainer\map_0022C1F4_0022C6E4.bin
        INCBIN  build\mapcontainer\map_0022C6E4_0022C734.bin
        INCBIN  build\mapcontainer\map_0022C734_0022C870.bin
        INCBIN  build\mapcontainer\map_0022C870_0022C890.bin
        INCBIN  build\mapcontainer\map_0022C890_0022CA1C.bin
        INCBIN  build\mapcontainer\map_0022CA1C_0022CA3C.bin
        INCBIN  build\mapcontainer\map_0022CA3C_0022CB48.bin
        INCBIN  build\mapcontainer\map_0022CB48_0022CB68.bin
        INCBIN  build\mapcontainer\map_0022CB68_0022CC08.bin
        INCBIN  build\mapcontainer\map_0022CC08_0022CC58.bin
        INCBIN  build\mapcontainer\map_0022CC58_0022CD08.bin
        INCBIN  build\mapcontainer\map_0022CD08_0022CD24.bin
        INCBIN  build\mapcontainer\map_0022CD24_0022CE08.bin
        INCBIN  build\mapcontainer\map_0022CE08_0022CE24.bin
        INCBIN  build\mapcontainer\map_0022CE24_0022CEB4.bin
        INCBIN  build\mapcontainer\map_0022CEB4_0022CED0.bin
        INCBIN  build\mapcontainer\map_0022CED0_0022CF10.bin
|unk_0822CF10|
        INCBIN  build\mapcontainer\map_0022CF10_0022CF28.bin
        INCBIN  build\mapcontainer\map_0022CF28_0022CF78.bin
        INCBIN  build\mapcontainer\map_0022CF78_0022D038.bin
        INCBIN  build\mapcontainer\map_0022D038_0022D054.bin
        INCBIN  build\mapcontainer\map_0022D054_0022D194.bin
        INCBIN  build\mapcontainer\map_0022D194_0022D1BC.bin
        INCBIN  build\mapcontainer\map_0022D1BC_0022D544.bin
        INCBIN  build\mapcontainer\map_0022D544_0022D56C.bin
        INCBIN  build\mapcontainer\map_0022D56C_0022D838.bin
        INCBIN  build\mapcontainer\map_0022D838_0022D860.bin
        INCBIN  build\mapcontainer\map_0022D860_0022D930.bin
|unk_0822D930|
        INCBIN  build\mapcontainer\map_0022D930_0022D978.bin
        INCBIN  build\mapcontainer\map_0022D978_0022DBC4.bin
        INCBIN  build\mapcontainer\map_0022DBC4_0022DC14.bin
        INCBIN  build\mapcontainer\map_0022DC14_0022DC34.bin
        INCBIN  build\mapcontainer\map_0022DC34_0022DD6C.bin
        INCBIN  build\mapcontainer\map_0022DD6C_0022DD8C.bin
        INCBIN  build\mapcontainer\map_0022DD8C_0022DECC.bin
        INCBIN  build\mapcontainer\map_0022DECC_0022DEEC.bin
        INCBIN  build\mapcontainer\map_0022DEEC_0022DF58.bin
|unk_0822DF58|
        INCBIN  build\mapcontainer\map_0022DF58_0022DF88.bin
        INCBIN  build\mapcontainer\map_0022DF88_0022DFD8.bin
        INCBIN  build\mapcontainer\map_0022DFD8_0022DFF4.bin
        INCBIN  build\mapcontainer\map_0022DFF4_0022E0D4.bin
        INCBIN  build\mapcontainer\map_0022E0D4_0022E0F0.bin
        INCBIN  build\mapcontainer\map_0022E0F0_0022E188.bin
        INCBIN  build\mapcontainer\map_0022E188_0022E1A4.bin
        INCBIN  build\mapcontainer\map_0022E1A4_0022E1D8.bin
|unk_0822E1D8|
        INCBIN  build\mapcontainer\map_0022E1D8_0022E1F0.bin
        INCBIN  build\mapcontainer\map_0022E1F0_0022E240.bin
        INCBIN  build\mapcontainer\map_0022E240_0022E25C.bin
        INCBIN  build\mapcontainer\map_0022E25C_0022E31C.bin
        INCBIN  build\mapcontainer\map_0022E31C_0022E344.bin
        INCBIN  build\mapcontainer\map_0022E344_0022E634.bin
        INCBIN  build\mapcontainer\map_0022E634_0022E65C.bin
        INCBIN  build\mapcontainer\map_0022E65C_0022E930.bin
        INCBIN  build\mapcontainer\map_0022E930_0022E958.bin
        INCBIN  build\mapcontainer\map_0022E958_0022EA1C.bin
|unk_0822EA1C|
        INCBIN  build\mapcontainer\map_0022EA1C_0022EA4C.bin
|unk_0822EA4C|
        INCBIN  build\mapcontainer\map_0022EA4C_0022EA94.bin
|unk_0822EA94|
        INCBIN  build\mapcontainer\map_0022EA94_0022EAA0.bin
        INCBIN  build\mapcontainer\map_0022EAA0_0022EAF0.bin
        INCBIN  build\mapcontainer\map_0022EAF0_0022EB80.bin
        INCBIN  build\mapcontainer\map_0022EB80_0022EBA0.bin
        INCBIN  build\mapcontainer\map_0022EBA0_0022ED50.bin
        INCBIN  build\mapcontainer\map_0022ED50_0022ED70.bin
        INCBIN  build\mapcontainer\map_0022ED70_0022EEB4.bin
        INCBIN  build\mapcontainer\map_0022EEB4_0022EED4.bin
        INCBIN  build\mapcontainer\map_0022EED4_0022EF54.bin
|unk_0822EF54|
        INCBIN  build\mapcontainer\map_0022EF54_0022EF84.bin
        INCBIN  build\mapcontainer\map_0022EF84_0022EFD4.bin
        INCBIN  build\mapcontainer\map_0022EFD4_0022F674.bin
|unk_0822F674|
        INCBIN  build\mapcontainer\map_0022F674_0022F6A4.bin
        INCBIN  build\mapcontainer\map_0022F6A4_0022F748.bin
|unk_0822F748|
        INCBIN  build\mapcontainer\map_0022F748_0022F778.bin
        INCBIN  build\jcalg1\gen_22f778.bin
        INCBIN  build\mapcontainer\map_0022FAAC_0022FB10.bin
|unk_0822FB10|
        INCBIN  build\mapcontainer\map_0022FB10_0022FB40.bin
        INCBIN  build\mapcontainer\map_0022FB40_0023048C.bin
|unk_0823048C|
        INCBIN  build\mapcontainer\map_0023048C_002304C4.bin
        INCBIN  build\jcalg1\gen_2304c4.bin
|unk_08230654|
        INCBIN  build\mapcontainer\map_00230654_00230714.bin
        INCBIN  build\jcalg1\gen_230714.bin
|unk_08230BFC|
        INCBIN  build\mapcontainer\map_00230BFC_00230C64.bin
|unk_08230C64|
        INCBIN  build\mapcontainer\map_00230C64_00230CB4.bin
        INCBIN  build\mapcontainer\map_00230CB4_002313C0.bin
        INCBIN  build\mapcontainer\map_002313C0_00231420.bin
        INCBIN  build\mapcontainer\map_00231420_00231754.bin
        INCBIN  build\mapcontainer\map_00231754_00231784.bin
        INCBIN  build\mapcontainer\map_00231784_00232028.bin
        INCBIN  build\mapcontainer\map_00232028_00232060.bin
        INCBIN  build\mapcontainer\map_00232060_0023220C.bin
|unk_0823220C|
        INCBIN  build\mapcontainer\map_0023220C_002322CC.bin
|unk_082322CC|
        INCBIN  build\mapcontainer\map_002322CC_00232334.bin
        INCBIN  build\mapcontainer\map_00232334_00232384.bin
        INCBIN  build\mapcontainer\map_00232384_0023275C.bin
|unk_0823275C|
        INCBIN  build\mapcontainer\map_0023275C_00232780.bin
        INCBIN  build\jcalg1\gen_232780.bin
|unk_08232C30|
        INCBIN  build\mapcontainer\map_00232C30_00232C50.bin
        INCBIN  build\jcalg1\gen_232c50.bin
|unk_08232D48|
        INCBIN  build\mapcontainer\map_00232D48_00232D60.bin
        INCBIN  build\jcalg1\gen_232d60.bin
|unk_08232F50|
        INCBIN  build\mapcontainer\map_00232F50_00232F68.bin
|unk_08232F68|
        INCBIN  build\mapcontainer\map_00232F68_00232F6C.bin
|unk_08232F6C|
        INCBIN  build\mapcontainer\map_00232F6C_00232FBC.bin
        INCBIN  build\mapcontainer\map_00232FBC_00233394.bin
        INCBIN  build\mapcontainer\map_00233394_002333B8.bin
        INCBIN  build\mapcontainer\map_002333B8_002333E4.bin
        INCBIN  build\mapcontainer\map_002333E4_00233400.bin
        INCBIN  build\mapcontainer\map_00233400_00233474.bin
        INCBIN  build\mapcontainer\map_00233474_00233494.bin
        INCBIN  build\mapcontainer\map_00233494_00233948.bin
        INCBIN  build\mapcontainer\map_00233948_00233968.bin
        INCBIN  build\mapcontainer\map_00233968_00233A34.bin
|unk_08233A34|
        INCBIN  build\mapcontainer\map_00233A34_00233A4C.bin
|unk_08233A4C|
        INCBIN  build\mapcontainer\map_00233A4C_00233A64.bin
|unk_08233A64|
        INCBIN  build\mapcontainer\map_00233A64_00233A68.bin
        INCBIN  build\mapcontainer\map_00233A68_00233AB8.bin
        INCBIN  build\mapcontainer\map_00233AB8_00233D10.bin
        INCBIN  build\mapcontainer\map_00233D10_00233D30.bin
        INCBIN  build\mapcontainer\map_00233D30_00234038.bin
        INCBIN  build\mapcontainer\map_00234038_00234058.bin
        INCBIN  build\mapcontainer\map_00234058_002341D8.bin
        INCBIN  build\mapcontainer\map_002341D8_002341F8.bin
        INCBIN  build\mapcontainer\map_002341F8_00234514.bin
        INCBIN  build\mapcontainer\map_00234514_00234534.bin
        INCBIN  build\mapcontainer\map_00234534_002346D0.bin
        INCLUDE rawlabeled_2346d0.s
        INCBIN  build\mapcontainer\map_0023475C_002347AC.bin
        INCBIN  build\mapcontainer\map_002347AC_00234A64.bin
        INCBIN  build\mapcontainer\map_00234A64_00234A8C.bin
        INCBIN  build\mapcontainer\map_00234A8C_00234AC8.bin
        INCBIN  build\mapcontainer\map_00234AC8_00234AE8.bin
        INCBIN  build\mapcontainer\map_00234AE8_00234FCC.bin
        INCBIN  build\mapcontainer\map_00234FCC_00234FF4.bin
        INCBIN  build\mapcontainer\map_00234FF4_0023556C.bin
        INCBIN  build\mapcontainer\map_0023556C_00235594.bin
        INCBIN  build\mapcontainer\map_00235594_00235710.bin
|unk_08235710|
        INCBIN  build\mapcontainer\map_00235710_00235788.bin
        INCBIN  build\mapcontainer\map_00235788_00235A10.bin
|unk_08235A10|
        INCBIN  build\mapcontainer\map_00235A10_00235A98.bin
|unk_08235A98|
        INCBIN  build\mapcontainer\map_00235A98_00235AA0.bin
        INCBIN  build\mapcontainer\map_00235AA0_00235AF0.bin
        INCBIN  build\mapcontainer\map_00235AF0_00235C90.bin
        INCBIN  build\mapcontainer\map_00235C90_00235CB0.bin
        INCBIN  build\mapcontainer\map_00235CB0_00235CEC.bin
        INCBIN  build\mapcontainer\map_00235CEC_00235D08.bin
        INCBIN  build\mapcontainer\map_00235D08_00236004.bin
        INCBIN  build\mapcontainer\map_00236004_00236024.bin
        INCBIN  build\mapcontainer\map_00236024_00236340.bin
        INCBIN  build\mapcontainer\map_00236340_00236360.bin
        INCBIN  build\mapcontainer\map_00236360_00236470.bin
|map_anim_row_08236470|
|unk_08236470|
	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x081911d8,0x08191214
|map_anim_row_0823647C|
|unk_0823647C|
	DCB 0x02,0x02
	DCW 0x037c
	DCD 0x081bfd60,0x081bfd9c
|unk_08236488|
        INCBIN  build\animframe\gen_236488_236988.bin
|map_anim_row_08236988|
|unk_08236988|
	DCB 0x10,0x08
	DCW 0x0374
	DCD 0x08236488,0x08236540,0x082365f8,0x082366ac,0x08236488,0x08236540,0x08236764,0x08236540
	DCD 0x0823681c,0x08236540,0x082368d4,0x082366ac,0x082368d4,0x082366ac,0x082368d4,0x082366ac
|unk_082369CC|
        INCBIN  baserom.gba_0x2369cc_0x2369d8.extracted
|unk_082369D8|
        INCBIN  build\mapcontainer\map_002369D8_00236A08.bin
|unk_08236A08|
        INCBIN  build\mapcontainer\map_00236A08_00236A10.bin
        INCBIN  build\mapcontainer\map_00236A10_00236A60.bin
        INCBIN  build\mapcontainer\map_00236A60_00236DEC.bin
        INCBIN  build\mapcontainer\map_00236DEC_00236E14.bin
        INCBIN  build\mapcontainer\map_00236E14_00236EA4.bin
        INCBIN  build\mapcontainer\map_00236EA4_00236ECC.bin
        INCBIN  build\mapcontainer\map_00236ECC_00237544.bin
        INCBIN  build\mapcontainer\map_00237544_0023756C.bin
        INCBIN  build\mapcontainer\map_0023756C_00237D14.bin
        INCBIN  build\mapcontainer\map_00237D14_00237D3C.bin
        INCBIN  build\mapcontainer\map_00237D3C_00237F20.bin
|unk_08237F20|
        INCBIN  build\mapcontainer\map_00237F20_00237F38.bin
        INCBIN  build\mapcontainer\map_00237F38_0023805C.bin
|unk_0823805C|
        INCBIN  build\mapcontainer\map_0023805C_002380F4.bin
|unk_082380F4|
        INCBIN  build\mapcontainer\map_002380F4_002380FC.bin
        INCBIN  build\mapcontainer\map_002380FC_0023814C.bin
        INCBIN  build\mapcontainer\map_0023814C_002383D0.bin
        INCBIN  build\mapcontainer\map_002383D0_002383F0.bin
        INCBIN  build\mapcontainer\map_002383F0_00238474.bin
        INCBIN  build\mapcontainer\map_00238474_00238494.bin
        INCBIN  build\mapcontainer\map_00238494_00238700.bin
        INCBIN  build\mapcontainer\map_00238700_00238720.bin
        INCBIN  build\mapcontainer\map_00238720_0023881C.bin
|unk_0823881C|
        INCBIN  build\mapcontainer\map_0023881C_002388B4.bin
|unk_082388B4|
        INCBIN  build\mapcontainer\map_002388B4_002388BC.bin
        INCBIN  build\mapcontainer\map_002388BC_0023890C.bin
        INCBIN  build\mapcontainer\map_0023890C_00238BCC.bin
        INCBIN  build\mapcontainer\map_00238BCC_00238BEC.bin
        INCBIN  build\mapcontainer\map_00238BEC_00238C14.bin
        INCBIN  build\mapcontainer\map_00238C14_00238C34.bin
        INCBIN  build\mapcontainer\map_00238C34_00238D1C.bin
        INCBIN  build\mapcontainer\map_00238D1C_00238D3C.bin
        INCBIN  build\mapcontainer\map_00238D3C_00238FE0.bin
        INCBIN  build\mapcontainer\map_00238FE0_00239000.bin
        INCBIN  build\mapcontainer\map_00239000_002390FC.bin
|unk_082390FC|
        INCBIN  build\mapcontainer\map_002390FC_0023915C.bin
        INCBIN  build\mapcontainer\map_0023915C_002393F0.bin
        INCLUDE rawlabeled_2393f0.s
        INCBIN  build\mapcontainer\map_00239474_002394C4.bin
        INCBIN  build\mapcontainer\map_002394C4_00239A30.bin
        INCBIN  build\mapcontainer\map_00239A30_00239A58.bin
        INCBIN  build\mapcontainer\map_00239A58_00239C30.bin
        INCBIN  build\mapcontainer\map_00239C30_00239C58.bin
        INCBIN  build\mapcontainer\map_00239C58_0023A2D0.bin
        INCBIN  build\mapcontainer\map_0023A2D0_0023A2F8.bin
        INCBIN  build\mapcontainer\map_0023A2F8_0023A4A8.bin
|unk_0823A4A8|
        INCBIN  build\mapcontainer\map_0023A4A8_0023A4C0.bin
|unk_0823A4C0|
        INCBIN  build\mapcontainer\map_0023A4C0_0023A558.bin
|unk_0823A558|
        INCBIN  build\mapcontainer\map_0023A558_0023A560.bin
        INCBIN  build\mapcontainer\map_0023A560_0023A5B0.bin
        INCBIN  build\mapcontainer\map_0023A5B0_0023A880.bin
        INCBIN  build\mapcontainer\map_0023A880_0023A8A0.bin
        INCBIN  build\mapcontainer\map_0023A8A0_0023A9B0.bin
        INCBIN  build\mapcontainer\map_0023A9B0_0023A9D0.bin
        INCBIN  build\mapcontainer\map_0023A9D0_0023AE10.bin
        INCBIN  build\mapcontainer\map_0023AE10_0023AE30.bin
        INCBIN  build\mapcontainer\map_0023AE30_0023AF80.bin
|unk_0823AF80|
        INCBIN  build\mapcontainer\map_0023AF80_0023AF98.bin
|unk_0823AF98|
        INCBIN  build\mapcontainer\map_0023AF98_0023B030.bin
|unk_0823B030|
        INCBIN  build\mapcontainer\map_0023B030_0023B038.bin
        INCBIN  build\mapcontainer\map_0023B038_0023B088.bin
        INCBIN  build\mapcontainer\map_0023B088_0023B4C4.bin
        INCBIN  build\mapcontainer\map_0023B4C4_0023B4E8.bin
        INCBIN  build\mapcontainer\map_0023B4E8_0023B530.bin
        INCBIN  build\mapcontainer\map_0023B530_0023B554.bin
        INCBIN  build\mapcontainer\map_0023B554_0023B680.bin
        INCBIN  build\mapcontainer\map_0023B680_0023B6A4.bin
        INCBIN  build\mapcontainer\map_0023B6A4_0023BC0C.bin
        INCBIN  build\mapcontainer\map_0023BC0C_0023BC30.bin
        INCBIN  build\mapcontainer\map_0023BC30_0023BD7C.bin
|unk_0823BD7C|
        INCBIN  build\mapcontainer\map_0023BD7C_0023BDAC.bin
        INCBIN  build\mapcontainer\map_0023BDAC_0023BF5C.bin
|unk_0823BF5C|
        INCBIN  build\mapcontainer\map_0023BF5C_0023C00C.bin
|unk_0823C00C|
        INCBIN  build\mapcontainer\map_0023C00C_0023C018.bin
        INCBIN  build\mapcontainer\map_0023C018_0023C068.bin
        INCBIN  build\mapcontainer\map_0023C068_0023C338.bin
        INCBIN  build\mapcontainer\map_0023C338_0023C358.bin
        INCBIN  build\mapcontainer\map_0023C358_0023C410.bin
        INCBIN  build\mapcontainer\map_0023C410_0023C430.bin
        INCBIN  build\mapcontainer\map_0023C430_0023C788.bin
        INCBIN  build\mapcontainer\map_0023C788_0023C7A8.bin
        INCBIN  build\mapcontainer\map_0023C7A8_0023C8CC.bin
|unk_0823C8CC|
        INCBIN  build\mapcontainer\map_0023C8CC_0023C964.bin
|unk_0823C964|
        INCBIN  build\mapcontainer\map_0023C964_0023C96C.bin
        INCBIN  build\mapcontainer\map_0023C96C_0023C9BC.bin
        INCBIN  build\mapcontainer\map_0023C9BC_0023CCD0.bin
        INCBIN  build\mapcontainer\map_0023CCD0_0023CCF0.bin
        INCBIN  build\mapcontainer\map_0023CCF0_0023CE08.bin
        INCBIN  build\mapcontainer\map_0023CE08_0023CE28.bin
        INCBIN  build\mapcontainer\map_0023CE28_0023D274.bin
        INCBIN  build\mapcontainer\map_0023D274_0023D294.bin
        INCBIN  build\mapcontainer\map_0023D294_0023D3F0.bin
|unk_0823D3F0|
        INCBIN  build\mapcontainer\map_0023D3F0_0023D498.bin
        INCBIN  build\mapcontainer\map_0023D498_0023D810.bin
        INCLUDE rawlabeled_23d810.s
        INCBIN  build\mapcontainer\map_0023D894_0023D8E4.bin
        INCBIN  build\mapcontainer\map_0023D8E4_0023DB8C.bin
        INCBIN  build\mapcontainer\map_0023DB8C_0023DBAC.bin
        INCBIN  build\mapcontainer\map_0023DBAC_0023DC24.bin
        INCBIN  build\mapcontainer\map_0023DC24_0023DC44.bin
        INCBIN  build\mapcontainer\map_0023DC44_0023DFA4.bin
        INCBIN  build\mapcontainer\map_0023DFA4_0023DFC4.bin
        INCBIN  build\mapcontainer\map_0023DFC4_0023E0B0.bin
|unk_0823E0B0|
        INCBIN  build\mapcontainer\map_0023E0B0_0023E148.bin
|unk_0823E148|
        INCBIN  build\mapcontainer\map_0023E148_0023E150.bin
        INCBIN  build\mapcontainer\map_0023E150_0023E1A0.bin
        INCBIN  build\mapcontainer\map_0023E1A0_0023EAE8.bin
        INCBIN  build\mapcontainer\map_0023EAE8_0023EB24.bin
        INCBIN  build\mapcontainer\map_0023EB24_0023ED98.bin
        INCBIN  build\mapcontainer\map_0023ED98_0023EDD4.bin
        INCBIN  build\mapcontainer\map_0023EDD4_0023FC9C.bin
        INCBIN  build\mapcontainer\map_0023FC9C_0023FCD8.bin
        INCBIN  build\mapcontainer\map_0023FCD8_0023FF58.bin
|unk_0823FF58|
        INCBIN  build\mapcontainer\map_0023FF58_0023FF88.bin
|unk_0823FF88|
        INCBIN  build\mapcontainer\map_0023FF88_00240038.bin
|unk_08240038|
        INCBIN  build\mapcontainer\map_00240038_00240044.bin
        INCBIN  build\mapcontainer\map_00240044_00240094.bin
        INCBIN  build\mapcontainer\map_00240094_00240378.bin
        INCBIN  build\mapcontainer\map_00240378_00240398.bin
        INCBIN  build\mapcontainer\map_00240398_002403C0.bin
        INCBIN  build\mapcontainer\map_002403C0_002403DC.bin
        INCBIN  build\mapcontainer\map_002403DC_0024051C.bin
        INCBIN  build\mapcontainer\map_0024051C_0024053C.bin
        INCBIN  build\mapcontainer\map_0024053C_0024097C.bin
        INCBIN  build\mapcontainer\map_0024097C_0024099C.bin
        INCBIN  build\mapcontainer\map_0024099C_00240AD0.bin
|unk_08240AD0|
        INCBIN  build\mapcontainer\map_00240AD0_00240B18.bin
|unk_08240B18|
        INCBIN  build\mapcontainer\map_00240B18_00240BB0.bin
|unk_08240BB0|
        INCBIN  build\mapcontainer\map_00240BB0_00240BB8.bin
        INCBIN  build\mapcontainer\map_00240BB8_00240C08.bin
        INCBIN  build\mapcontainer\map_00240C08_00241038.bin
        INCBIN  build\mapcontainer\map_00241038_00241060.bin
        INCBIN  build\mapcontainer\map_00241060_002411C8.bin
        INCBIN  build\mapcontainer\map_002411C8_002411F0.bin
        INCBIN  build\mapcontainer\map_002411F0_002417A0.bin
        INCBIN  build\mapcontainer\map_002417A0_002417C8.bin
        INCBIN  build\mapcontainer\map_002417C8_00241924.bin
|unk_08241924|
        INCBIN  build\mapcontainer\map_00241924_0024196C.bin
        INCBIN  build\mapcontainer\map_0024196C_00241C90.bin
|unk_08241C90|
        INCBIN  build\mapcontainer\map_00241C90_00241D10.bin
|unk_08241D10|
        INCBIN  build\mapcontainer\map_00241D10_00241D14.bin
        INCBIN  build\mapcontainer\map_00241D14_00241D64.bin
        INCBIN  build\mapcontainer\map_00241D64_002427C8.bin
        INCBIN  build\mapcontainer\map_002427C8_00242804.bin
        INCBIN  build\mapcontainer\map_00242804_002432E4.bin
        INCBIN  build\mapcontainer\map_002432E4_00243320.bin
        INCBIN  build\mapcontainer\map_00243320_00243B98.bin
        INCBIN  build\mapcontainer\map_00243B98_00243BF0.bin
        INCBIN  build\mapcontainer\map_00243BF0_00244430.bin
        INCBIN  build\mapcontainer\map_00244430_00244488.bin
        INCBIN  build\mapcontainer\map_00244488_0024451C.bin
|unk_0824451C|
        INCBIN  build\animframe\gen_24451c_2445d4.bin
|unk_082445D4|
        INCBIN  build\mapcontainer\map_002445D4_002445FC.bin
|unk_082445FC|
        INCBIN  build\mapcontainer\map_002445FC_00244600.bin
        INCBIN  build\mapcontainer\map_00244600_00244650.bin
        INCBIN  build\mapcontainer\map_00244650_00244E40.bin
        INCBIN  build\mapcontainer\map_00244E40_00244E7C.bin
        INCBIN  build\mapcontainer\map_00244E7C_0024594C.bin
        INCBIN  build\mapcontainer\map_0024594C_00245988.bin
        INCBIN  build\mapcontainer\map_00245988_00246200.bin
        INCBIN  build\mapcontainer\map_00246200_00246258.bin
        INCBIN  build\mapcontainer\map_00246258_00246A80.bin
        INCBIN  build\mapcontainer\map_00246A80_00246AD8.bin
        INCBIN  build\mapcontainer\map_00246AD8_00246B08.bin
|unk_08246B08|
        INCBIN  build\mapcontainer\map_00246B08_00246B30.bin
|unk_08246B30|
        INCBIN  build\mapcontainer\map_00246B30_00246B34.bin
        INCBIN  build\mapcontainer\map_00246B34_00246B84.bin
        INCBIN  build\mapcontainer\map_00246B84_00246C7C.bin
        INCBIN  build\mapcontainer\map_00246C7C_00246CA4.bin
        INCBIN  build\mapcontainer\map_00246CA4_00246E5C.bin
        INCBIN  build\mapcontainer\map_00246E5C_00246E84.bin
        INCBIN  build\mapcontainer\map_00246E84_00247154.bin
        INCBIN  build\mapcontainer\map_00247154_0024717C.bin
        INCBIN  build\mapcontainer\map_0024717C_0024720C.bin
|unk_0824720C|
        INCBIN  build\mapcontainer\map_0024720C_00247254.bin
        INCBIN  build\mapcontainer\map_00247254_00247388.bin
|unk_08247388|
        INCBIN  build\mapcontainer\map_00247388_002473A0.bin
|unk_082473A0|
        INCBIN  build\mapcontainer\map_002473A0_002473A4.bin
        INCBIN  build\mapcontainer\map_002473A4_002473F4.bin
        INCBIN  build\mapcontainer\map_002473F4_00247480.bin
        INCBIN  build\mapcontainer\map_00247480_002474A0.bin
        INCBIN  build\mapcontainer\map_002474A0_002475DC.bin
        INCBIN  build\mapcontainer\map_002475DC_002475FC.bin
        INCBIN  build\mapcontainer\map_002475FC_0024771C.bin
        INCBIN  build\mapcontainer\map_0024771C_0024773C.bin
        INCBIN  build\mapcontainer\map_0024773C_0024779C.bin
|unk_0824779C|
        INCBIN  build\mapcontainer\map_0024779C_002477B4.bin
        INCBIN  build\mapcontainer\map_002477B4_002478AC.bin
|unk_082478AC|
        INCBIN  build\mapcontainer\map_002478AC_002478DC.bin
|unk_082478DC|
        INCBIN  build\mapcontainer\map_002478DC_002478E4.bin
        INCBIN  build\mapcontainer\map_002478E4_00247934.bin
        INCBIN  build\mapcontainer\map_00247934_00247B00.bin
        INCBIN  build\mapcontainer\map_00247B00_00247B20.bin
        INCBIN  build\mapcontainer\map_00247B20_00247B6C.bin
        INCBIN  build\mapcontainer\map_00247B6C_00247B8C.bin
        INCBIN  build\mapcontainer\map_00247B8C_00247CEC.bin
        INCBIN  build\mapcontainer\map_00247CEC_00247D0C.bin
        INCBIN  build\mapcontainer\map_00247D0C_00247DB8.bin
        INCBIN  build\mapcontainer\map_00247DB8_00247DD8.bin
        INCBIN  build\mapcontainer\map_00247DD8_00247E7C.bin
|unk_08247E7C|
        INCBIN  build\mapcontainer\map_00247E7C_00247E94.bin
        INCBIN  build\mapcontainer\map_00247E94_00248070.bin
|unk_08248070|
        INCBIN  build\mapcontainer\map_00248070_002480A0.bin
|unk_082480A0|
        INCBIN  build\mapcontainer\map_002480A0_002480A8.bin
        INCBIN  build\mapcontainer\map_002480A8_002480F8.bin
        INCBIN  build\mapcontainer\map_002480F8_00248AA8.bin
        INCBIN  build\mapcontainer\map_00248AA8_00248AD8.bin
        INCBIN  build\mapcontainer\map_00248AD8_00248DC8.bin
        INCBIN  build\mapcontainer\map_00248DC8_00248E00.bin
        INCBIN  build\mapcontainer\map_00248E00_00249384.bin
        INCBIN  build\mapcontainer\map_00249384_002493BC.bin
        INCBIN  build\mapcontainer\map_002493BC_00249C00.bin
        INCBIN  build\mapcontainer\map_00249C00_00249C38.bin
        INCBIN  build\mapcontainer\map_00249C38_00249D80.bin
|unk_08249D80|
        INCBIN  build\mapcontainer\map_00249D80_00249EA0.bin
        INCBIN  build\mapcontainer\map_00249EA0_00249EBC.bin
|unk_08249EBC|
        INCBIN  build\mapcontainer\map_00249EBC_00249F3C.bin
|unk_08249F3C|
        INCBIN  build\mapcontainer\map_00249F3C_00249F40.bin
        INCBIN  build\mapcontainer\map_00249F40_00249F90.bin
        INCBIN  build\mapcontainer\map_00249F90_0024A1CC.bin
|unk_0824A1CC|
        INCBIN  build\mapcontainer\map_0024A1CC_0024A1F4.bin
        INCBIN  build\jcalg1\gen_24a1f4.bin
|unk_0824A2A8|
        INCBIN  build\mapcontainer\map_0024A2A8_0024A2D8.bin
        INCBIN  build\jcalg1\gen_24a2d8.bin
|unk_0824A8C8|
        INCBIN  build\mapcontainer\map_0024A8C8_0024A8F8.bin
        INCBIN  build\jcalg1\gen_24a8f8.bin
|unk_0824AC58|
        INCBIN  build\mapcontainer\map_0024AC58_0024AC88.bin
        INCBIN  build\jcalg1\gen_24ac88.bin
|unk_0824ADC8|
        INCBIN  build\mapcontainer\map_0024ADC8_0024ADE0.bin
|unk_0824ADE0|
        INCBIN  build\mapcontainer\map_0024ADE0_0024AE70.bin
|unk_0824AE70|
        INCBIN  build\mapcontainer\map_0024AE70_0024AE74.bin
|unk_0824AE74|
        INCBIN  build\mapcontainer\map_0024AE74_0024AEC4.bin
        INCBIN  build\mapcontainer\map_0024AEC4_0024B248.bin
        INCBIN  build\mapcontainer\map_0024B248_0024B270.bin
        INCBIN  build\mapcontainer\map_0024B270_0024B324.bin
        INCBIN  build\mapcontainer\map_0024B324_0024B354.bin
        INCBIN  build\mapcontainer\map_0024B354_0024BA40.bin
        INCBIN  build\mapcontainer\map_0024BA40_0024BA70.bin
        INCBIN  build\mapcontainer\map_0024BA70_0024BDD0.bin
        INCBIN  build\mapcontainer\map_0024BDD0_0024BE00.bin
        INCBIN  build\mapcontainer\map_0024BE00_0024BF54.bin
|unk_0824BF54|
        INCBIN  build\mapcontainer\map_0024BF54_0024BF6C.bin
|unk_0824BF6C|
        INCBIN  build\mapcontainer\map_0024BF6C_0024BFFC.bin
|unk_0824BFFC|
        INCBIN  build\mapcontainer\map_0024BFFC_0024C000.bin
        INCBIN  build\mapcontainer\map_0024C000_0024C050.bin
        INCBIN  build\mapcontainer\map_0024C050_0024C1E4.bin
        INCBIN  build\mapcontainer\map_0024C1E4_0024C214.bin
        INCBIN  build\mapcontainer\map_0024C214_0024CB94.bin
        INCBIN  build\mapcontainer\map_0024CB94_0024CBD0.bin
        INCBIN  build\mapcontainer\map_0024CBD0_0024D8B0.bin
        INCBIN  build\mapcontainer\map_0024D8B0_0024D8EC.bin
        INCBIN  build\mapcontainer\map_0024D8EC_0024DB1C.bin
        INCBIN  build\mapcontainer\map_0024DB1C_0024DB3C.bin
        INCBIN  build\mapcontainer\map_0024DB3C_0024DCC0.bin
|unk_0824DCC0|
        INCBIN  build\mapcontainer\map_0024DCC0_0024DDB0.bin
        INCBIN  build\mapcontainer\map_0024DDB0_0024E184.bin
        INCBIN  build\mapcontainer\map_0024E184_0024E1D4.bin
        INCBIN  build\mapcontainer\map_0024E1D4_0024E3B4.bin
        INCBIN  build\mapcontainer\map_0024E3B4_0024E3DC.bin
        INCBIN  build\mapcontainer\map_0024E3DC_0024EA9C.bin
        INCBIN  build\mapcontainer\map_0024EA9C_0024EAC4.bin
        INCBIN  build\mapcontainer\map_0024EAC4_0024F048.bin
        INCBIN  build\mapcontainer\map_0024F048_0024F070.bin
        INCBIN  build\mapcontainer\map_0024F070_0024F424.bin
        INCBIN  build\mapcontainer\map_0024F424_0024F44C.bin
        INCBIN  build\mapcontainer\map_0024F44C_0024F4E4.bin
|unk_0824F4E4|
        INCBIN  build\mapcontainer\map_0024F4E4_0024F55C.bin
        INCBIN  build\mapcontainer\map_0024F55C_0024F5AC.bin
        INCBIN  build\mapcontainer\map_0024F5AC_0024F848.bin
        INCBIN  build\mapcontainer\map_0024F848_0024F864.bin
        INCBIN  build\mapcontainer\map_0024F864_0024F9DC.bin
        INCBIN  build\mapcontainer\map_0024F9DC_0024F9F8.bin
        INCBIN  build\mapcontainer\map_0024F9F8_0024FA54.bin
        INCBIN  build\mapcontainer\map_0024FA54_0024FA70.bin
        INCBIN  build\mapcontainer\map_0024FA70_0024FCA8.bin
        INCBIN  build\mapcontainer\map_0024FCA8_0024FCC4.bin
        INCBIN  build\mapcontainer\map_0024FCC4_0024FD48.bin
|unk_0824FD48|
        INCBIN  build\mapcontainer\map_0024FD48_0024FDD8.bin
        INCBIN  build\mapcontainer\map_0024FDD8_0024FED0.bin
|unk_0824FED0|
        INCBIN  build\mapcontainer\map_0024FED0_0024FEE8.bin
|unk_0824FEE8|
        INCBIN  build\mapcontainer\map_0024FEE8_0024FEEC.bin
        INCBIN  build\mapcontainer\map_0024FEEC_0024FF3C.bin
        INCBIN  build\mapcontainer\map_0024FF3C_002501A8.bin
        INCBIN  build\mapcontainer\map_002501A8_002501D0.bin
        INCBIN  build\mapcontainer\map_002501D0_00250380.bin
        INCBIN  build\mapcontainer\map_00250380_002503A8.bin
        INCBIN  build\mapcontainer\map_002503A8_002505D8.bin
        INCBIN  build\mapcontainer\map_002505D8_002505F8.bin
        INCBIN  build\mapcontainer\map_002505F8_0025066C.bin
|unk_0825066C|
        INCBIN  build\mapcontainer\map_0025066C_00250744.bin
        INCBIN  build\mapcontainer\map_00250744_00250A08.bin
|unk_08250A08|
        INCBIN  build\mapcontainer\map_00250A08_00250A20.bin
|unk_08250A20|
        INCBIN  build\mapcontainer\map_00250A20_00250A24.bin
        INCBIN  build\mapcontainer\map_00250A24_00250A74.bin
        INCBIN  build\mapcontainer\map_00250A74_00250B50.bin
        INCBIN  build\mapcontainer\map_00250B50_00250B70.bin
        INCBIN  build\mapcontainer\map_00250B70_00250E98.bin
        INCBIN  build\mapcontainer\map_00250E98_00250EC0.bin
        INCBIN  build\mapcontainer\map_00250EC0_002510F0.bin
        INCBIN  build\mapcontainer\map_002510F0_00251110.bin
        INCBIN  build\mapcontainer\map_00251110_002511A4.bin
|unk_082511A4|
        INCBIN  build\mapcontainer\map_002511A4_0025133C.bin
        INCBIN  build\mapcontainer\map_0025133C_0025184C.bin
        INCBIN  build\mapcontainer\map_0025184C_0025189C.bin
        INCBIN  build\mapcontainer\map_0025189C_00251B40.bin
        INCBIN  build\mapcontainer\map_00251B40_00251B60.bin
        INCBIN  build\mapcontainer\map_00251B60_00251B94.bin
|unk_08251B94|
        INCBIN  build\mapcontainer\map_00251B94_00251BF4.bin
|unk_08251BF4|
        INCBIN  build\mapcontainer\map_00251BF4_00251C04.bin
        INCBIN  build\mapcontainer\map_00251C04_00251C54.bin
        INCBIN  build\mapcontainer\map_00251C54_00251F10.bin
        INCBIN  build\mapcontainer\map_00251F10_00251F30.bin
        INCBIN  build\mapcontainer\map_00251F30_00251F4C.bin
|unk_08251F4C|
        INCBIN  build\mapcontainer\map_00251F4C_00251FC4.bin
|unk_08251FC4|
        INCBIN  build\mapcontainer\map_00251FC4_00251FD8.bin
        INCBIN  build\mapcontainer\map_00251FD8_00252028.bin
        INCBIN  build\mapcontainer\map_00252028_00252048.bin
        INCLUDE rawlabeled_252048.s
        INCBIN  build\mapcontainer\map_002520D4_00252124.bin
        INCBIN  build\mapcontainer\map_00252124_00252184.bin
        INCBIN  build\mapcontainer\map_00252184_002521A0.bin
        INCBIN  build\mapcontainer\map_002521A0_002523F4.bin
        INCBIN  build\mapcontainer\map_002523F4_00252414.bin
        INCBIN  build\mapcontainer\map_00252414_0025258C.bin
        INCBIN  build\mapcontainer\map_0025258C_002525AC.bin
        INCBIN  build\mapcontainer\map_002525AC_00252AF8.bin
        INCBIN  build\mapcontainer\map_00252AF8_00252B20.bin
        INCBIN  build\mapcontainer\map_00252B20_00252BBC.bin
|unk_08252BBC|
        INCBIN  build\mapcontainer\map_00252BBC_00252BEC.bin
|unk_08252BEC|
        INCBIN  build\animframe\gen_252bec_253558.bin
|unk_08253558|
        INCBIN  build\mapcontainer\map_00253558_002535D0.bin
|unk_082535D0|
        INCBIN  build\mapcontainer\map_002535D0_002535E0.bin
        INCBIN  build\mapcontainer\map_002535E0_00253630.bin
        INCBIN  build\mapcontainer\map_00253630_002536CC.bin
        INCBIN  build\mapcontainer\map_002536CC_002536E8.bin
        INCBIN  build\mapcontainer\map_002536E8_00253728.bin
        INCBIN  build\mapcontainer\map_00253728_00253744.bin
        INCBIN  build\mapcontainer\map_00253744_00253890.bin
        INCBIN  build\mapcontainer\map_00253890_002538AC.bin
        INCBIN  build\mapcontainer\map_002538AC_00253908.bin
|unk_08253908|
        INCBIN  build\mapcontainer\map_00253908_00253920.bin
|unk_08253920|
        INCBIN  build\mapcontainer\map_00253920_00253924.bin
        INCBIN  build\mapcontainer\map_00253924_00253974.bin
        INCBIN  build\mapcontainer\map_00253974_00253990.bin
        INCBIN  build\mapcontainer\map_00253990_002539AC.bin
        INCBIN  build\mapcontainer\map_002539AC_00253A00.bin
        INCBIN  build\mapcontainer\map_00253A00_00253A1C.bin
        INCBIN  build\mapcontainer\map_00253A1C_00253A58.bin
        INCBIN  build\mapcontainer\map_00253A58_00253A74.bin
        INCBIN  build\mapcontainer\map_00253A74_00253B7C.bin
        INCBIN  build\mapcontainer\map_00253B7C_00253B98.bin
        INCBIN  build\mapcontainer\map_00253B98_00253C00.bin
|unk_08253C00|
        INCBIN  build\mapcontainer\map_00253C00_00253DC8.bin
|unk_08253DC8|
        INCBIN  build\mapcontainer\map_00253DC8_00253DE0.bin
|unk_08253DE0|
        INCBIN  build\mapcontainer\map_00253DE0_00253DE4.bin
        INCBIN  build\mapcontainer\map_00253DE4_00253E34.bin
        INCBIN  build\mapcontainer\map_00253E34_00253FB0.bin
        INCBIN  build\mapcontainer\map_00253FB0_00253FCC.bin
        INCBIN  build\mapcontainer\map_00253FCC_00254088.bin
        INCBIN  build\mapcontainer\map_00254088_002540A4.bin
        INCBIN  build\mapcontainer\map_002540A4_0025432C.bin
        INCBIN  build\mapcontainer\map_0025432C_00254348.bin
        INCBIN  build\mapcontainer\map_00254348_0025440C.bin
|unk_0825440C|
        INCBIN  build\mapcontainer\map_0025440C_00254454.bin
        INCBIN  build\mapcontainer\map_00254454_0025464C.bin
        INCLUDE rawlabeled_25464c.s
        INCBIN  build\mapcontainer\map_002546A0_002546F0.bin
        INCBIN  build\mapcontainer\map_002546F0_00254894.bin
        INCBIN  build\mapcontainer\map_00254894_002548B0.bin
        INCBIN  build\mapcontainer\map_002548B0_002548E8.bin
        INCBIN  build\mapcontainer\map_002548E8_00254904.bin
        INCBIN  build\mapcontainer\map_00254904_002549C4.bin
        INCBIN  build\mapcontainer\map_002549C4_002549E0.bin
        INCBIN  build\mapcontainer\map_002549E0_00254C34.bin
        INCBIN  build\mapcontainer\map_00254C34_00254C50.bin
        INCBIN  build\mapcontainer\map_00254C50_00254CF4.bin
|unk_08254CF4|
        INCBIN  build\mapcontainer\map_00254CF4_00254D84.bin
|unk_08254D84|
        INCBIN  build\mapcontainer\map_00254D84_00254D9C.bin
|unk_08254D9C|
        INCBIN  build\mapcontainer\map_00254D9C_00254DA0.bin
        INCBIN  build\mapcontainer\map_00254DA0_00254DF0.bin
        INCBIN  build\mapcontainer\map_00254DF0_002552D0.bin
        INCBIN  build\mapcontainer\map_002552D0_002552F0.bin
        INCBIN  build\mapcontainer\map_002552F0_00255594.bin
        INCBIN  build\mapcontainer\map_00255594_002555B4.bin
        INCBIN  build\mapcontainer\map_002555B4_002556D4.bin
        INCBIN  build\mapcontainer\map_002556D4_002556F4.bin
        INCBIN  build\mapcontainer\map_002556F4_00255A44.bin
        INCBIN  build\mapcontainer\map_00255A44_00255A64.bin
        INCBIN  build\mapcontainer\map_00255A64_00255B30.bin
|unk_08255B30|
        INCBIN  build\mapcontainer\map_00255B30_00255B60.bin
        INCBIN  build\mapcontainer\map_00255B60_00255C64.bin
|unk_08255C64|
        INCBIN  build\mapcontainer\map_00255C64_00255C94.bin
|unk_08255C94|
        INCBIN  build\mapcontainer\map_00255C94_00255C9C.bin
        INCBIN  build\mapcontainer\map_00255C9C_00255CEC.bin
        INCBIN  build\mapcontainer\map_00255CEC_00255E78.bin
        INCBIN  build\mapcontainer\map_00255E78_00255E94.bin
        INCBIN  build\mapcontainer\map_00255E94_00255EC8.bin
        INCBIN  build\mapcontainer\map_00255EC8_00255EE4.bin
        INCBIN  build\mapcontainer\map_00255EE4_00256048.bin
        INCBIN  build\mapcontainer\map_00256048_00256064.bin
        INCBIN  build\mapcontainer\map_00256064_002560D4.bin
|unk_082560D4|
        INCBIN  build\mapcontainer\map_002560D4_00256104.bin
|unk_08256104|
        INCBIN  build\mapcontainer\map_00256104_0025610C.bin
        INCBIN  build\mapcontainer\map_0025610C_0025615C.bin
        INCBIN  build\mapcontainer\map_0025615C_00256650.bin
        INCBIN  build\mapcontainer\map_00256650_00256670.bin
        INCBIN  build\mapcontainer\map_00256670_0025691C.bin
        INCBIN  build\mapcontainer\map_0025691C_0025693C.bin
        INCBIN  build\mapcontainer\map_0025693C_00256A80.bin
        INCBIN  build\mapcontainer\map_00256A80_00256AA0.bin
        INCBIN  build\mapcontainer\map_00256AA0_00256DA0.bin
        INCBIN  build\mapcontainer\map_00256DA0_00256DC0.bin
        INCBIN  build\mapcontainer\map_00256DC0_00256EAC.bin
|unk_08256EAC|
        INCBIN  build\mapcontainer\map_00256EAC_00256EC4.bin
|unk_08256EC4|
        INCBIN  build\mapcontainer\map_00256EC4_00256F24.bin
|unk_08256F24|
        INCBIN  build\mapcontainer\map_00256F24_00256F34.bin
        INCBIN  build\mapcontainer\map_00256F34_00256F84.bin
        INCBIN  build\mapcontainer\map_00256F84_002572F4.bin
        INCBIN  build\mapcontainer\map_002572F4_00257324.bin
        INCBIN  build\mapcontainer\map_00257324_00257840.bin
        INCBIN  build\mapcontainer\map_00257840_0025787C.bin
        INCBIN  build\mapcontainer\map_0025787C_00258094.bin
        INCBIN  build\mapcontainer\map_00258094_002580D0.bin
        INCBIN  build\mapcontainer\map_002580D0_0025831C.bin
        INCBIN  build\mapcontainer\map_0025831C_0025833C.bin
        INCBIN  build\mapcontainer\map_0025833C_00258514.bin
|unk_08258514|
        INCBIN  build\mapcontainer\map_00258514_0025867C.bin
        INCBIN  build\mapcontainer\map_0025867C_00258B9C.bin
|unk_08258B9C|
        INCBIN  build\mapcontainer\map_00258B9C_00258BB4.bin
|unk_08258BB4|
        INCBIN  build\mapcontainer\map_00258BB4_00258BB8.bin
        INCBIN  build\mapcontainer\map_00258BB8_00258C08.bin
        INCBIN  build\mapcontainer\map_00258C08_00258EB0.bin
        INCBIN  build\mapcontainer\map_00258EB0_00258ECC.bin
        INCBIN  build\mapcontainer\map_00258ECC_00258F18.bin
        INCBIN  build\mapcontainer\map_00258F18_00258F34.bin
        INCBIN  build\mapcontainer\map_00258F34_0025906C.bin
        INCBIN  build\mapcontainer\map_0025906C_00259088.bin
        INCBIN  build\mapcontainer\map_00259088_002590F0.bin
|unk_082590F0|
        INCBIN  build\mapcontainer\map_002590F0_00259108.bin
|unk_08259108|
        INCBIN  build\mapcontainer\map_00259108_0025910C.bin
        INCBIN  build\mapcontainer\map_0025910C_0025915C.bin
        INCBIN  build\mapcontainer\map_0025915C_00259428.bin
        INCBIN  build\mapcontainer\map_00259428_00259450.bin
        INCBIN  build\mapcontainer\map_00259450_002594DC.bin
        INCBIN  build\mapcontainer\map_002594DC_00259504.bin
        INCBIN  build\mapcontainer\map_00259504_002597DC.bin
        INCBIN  build\mapcontainer\map_002597DC_002597FC.bin
        INCBIN  build\mapcontainer\map_002597FC_002598A8.bin
|unk_082598A8|
        INCBIN  build\mapcontainer\map_002598A8_002598C0.bin
        INCBIN  build\mapcontainer\map_002598C0_00259A88.bin
|unk_08259A88|
        INCBIN  build\animframe\gen_259a88_259be4.bin
|unk_08259BE4|
        INCBIN  build\mapcontainer\map_00259BE4_00259C34.bin
|unk_08259C34|
        INCBIN  build\mapcontainer\map_00259C34_00259C3C.bin
        INCBIN  build\mapcontainer\map_00259C3C_00259C8C.bin
        INCBIN  build\mapcontainer\map_00259C8C_00259FAC.bin
        INCBIN  build\mapcontainer\map_00259FAC_00259FDC.bin
        INCBIN  build\mapcontainer\map_00259FDC_0025A5F0.bin
        INCBIN  build\mapcontainer\map_0025A5F0_0025A638.bin
        INCBIN  build\mapcontainer\map_0025A638_0025AB10.bin
        INCBIN  build\mapcontainer\map_0025AB10_0025AB58.bin
        INCBIN  build\mapcontainer\map_0025AB58_0025C064.bin
        INCBIN  build\mapcontainer\map_0025C064_0025C0BC.bin
        INCBIN  build\mapcontainer\map_0025C0BC_0025C338.bin
|unk_0825C338|
        INCBIN  build\mapcontainer\map_0025C338_0025C3B0.bin
        INCBIN  build\mapcontainer\map_0025C3B0_0025C6E4.bin
|map_anim_row_0825C6E4|
|unk_0825C6E4|
	DCB 0x04,0x03
	DCW 0x037d
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|map_anim_row_0825C6F8|
|unk_0825C6F8|
	DCB 0x12,0x17
	DCW 0x0366
	DCD 0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c,0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c
	DCD 0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c,0x0821fc60,0x0821fd7c,0x0821fee8,0x082200a0
	DCD 0x08220288,0x08220434
|unk_0825C744|
        INCBIN  build\animframe\gen_25c744_25c7fc.bin
|map_anim_row_0825C7FC|
|unk_0825C7FC|
	DCB 0x02,0x03
	DCW 0x0363
	DCD 0x0825c744,0x0825c7a0
|unk_0825C808|
        INCBIN  baserom.gba_0x25c808_0x25c814.extracted
|unk_0825C814|
        INCBIN  build\mapcontainer\map_0025C814_0025C82C.bin
|unk_0825C82C|
        INCBIN  build\mapcontainer\map_0025C82C_0025C830.bin
        INCBIN  build\mapcontainer\map_0025C830_0025C880.bin
        INCBIN  build\mapcontainer\map_0025C880_0025CAEC.bin
        INCBIN  build\mapcontainer\map_0025CAEC_0025CB14.bin
        INCBIN  build\mapcontainer\map_0025CB14_0025CB64.bin
        INCBIN  build\mapcontainer\map_0025CB64_0025CB84.bin
        INCBIN  build\mapcontainer\map_0025CB84_0025D038.bin
        INCBIN  build\mapcontainer\map_0025D038_0025D060.bin
        INCBIN  build\mapcontainer\map_0025D060_0025D420.bin
        INCBIN  build\mapcontainer\map_0025D420_0025D448.bin
        INCBIN  build\mapcontainer\map_0025D448_0025D51C.bin
|unk_0825D51C|
        INCBIN  build\mapcontainer\map_0025D51C_0025D534.bin
        INCBIN  build\mapcontainer\map_0025D534_0025D5A0.bin
|unk_0825D5A0|
        INCBIN  build\animframe\gen_25d5a0_25d604.bin
|map_anim_row_0825D604|
|unk_0825D604|
	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x0825d5a0,0x0825d5d4
|unk_0825D610|
        INCBIN  build\animframe\gen_25d610_25d688.bin
|map_anim_row_0825D688|
|unk_0825D688|
	DCB 0x02,0x02
	DCW 0x037c
	DCD 0x0825d610,0x0825d64c
|unk_0825D694|
        INCBIN  build\animframe\gen_25d694_25d6e4.bin
|map_anim_row_0825D6E4|
|unk_0825D6E4|
	DCB 0x02,0x01
	DCW 0x037b
	DCD 0x0825d694,0x0825d6bc
|unk_0825D6F0|
        INCBIN  build\animframe\gen_25d6f0_25d858.bin
|map_anim_row_0825D858|
|unk_0825D858|
	DCB 0x07,0x04
	DCW 0x0377
	DCD 0x0825d6f0,0x0825d724,0x0825d758,0x0825d78c,0x0825d7bc,0x0825d7f0,0x0825d824
|unk_0825D878|
        INCBIN  build\animframe\gen_25d878_25dad8.bin
|map_anim_row_0825DAD8|
|unk_0825DAD8|
	DCB 0x07,0x04
	DCW 0x0373
	DCD 0x0825d878,0x0825d8d0,0x0825d924,0x0825d97c,0x0825d9d4,0x0825da2c,0x0825da80
|unk_0825DAF8|
        INCBIN  build\animframe\gen_25daf8_25df18.bin
|map_anim_row_0825DF18|
|unk_0825DF18|
	DCB 0x0c,0x08
	DCW 0x036b
	DCD 0x0825daf8,0x0825db50,0x0825dba8,0x0825dc04,0x0825dc60,0x0825dcb4,0x0825dd10,0x0825dd68
	DCD 0x0825ddc4,0x0825de1c,0x0825de74,0x0825dec8
|unk_0825DF4C|
        INCBIN  baserom.gba_0x25df4c_0x25df64.extracted
|unk_0825DF64|
        INCBIN  build\mapcontainer\map_0025DF64_0025DF94.bin
|unk_0825DF94|
        INCBIN  build\mapcontainer\map_0025DF94_0025DF9C.bin
        INCBIN  build\mapcontainer\map_0025DF9C_0025DFEC.bin
        INCBIN  build\mapcontainer\map_0025DFEC_0025E0E4.bin
        INCBIN  build\mapcontainer\map_0025E0E4_0025E10C.bin
        INCBIN  build\mapcontainer\map_0025E10C_0025E16C.bin
        INCBIN  build\mapcontainer\map_0025E16C_0025E18C.bin
        INCBIN  build\mapcontainer\map_0025E18C_0025E29C.bin
        INCBIN  build\mapcontainer\map_0025E29C_0025E2C4.bin
        INCBIN  build\mapcontainer\map_0025E2C4_0025E31C.bin
|unk_0825E31C|
        INCBIN  build\mapcontainer\map_0025E31C_0025E334.bin
|unk_0825E334|
        INCBIN  build\mapcontainer\map_0025E334_0025E338.bin
        INCBIN  build\mapcontainer\map_0025E338_0025E388.bin
        INCBIN  build\mapcontainer\map_0025E388_0025E59C.bin
        INCBIN  build\mapcontainer\map_0025E59C_0025E5C4.bin
        INCBIN  build\mapcontainer\map_0025E5C4_0025E810.bin
        INCBIN  build\mapcontainer\map_0025E810_0025E838.bin
        INCBIN  build\mapcontainer\map_0025E838_0025EA8C.bin
        INCBIN  build\mapcontainer\map_0025EA8C_0025EAB4.bin
        INCBIN  build\mapcontainer\map_0025EAB4_0025EB64.bin
|unk_0825EB64|
        INCBIN  build\animframe\gen_25eb64_25edb4.bin
|map_anim_row_0825EDB4|
|unk_0825EDB4|
	DCB 0x10,0x01
	DCW 0x037f
	DCD 0x0825eb64,0x0825eb88,0x0825ebac,0x0825ebd0,0x0825ebf4,0x0825ec1c,0x0825ec44,0x0825ec68
	DCD 0x0825ec8c,0x0825ecb0,0x0825ecd4,0x0825ecf8,0x0825ed1c,0x0825ed44,0x0825ed6c,0x0825ed90
|unk_0825EDF8|
        INCBIN  build\animframe\gen_25edf8_25f3f8.bin
|map_anim_row_0825F3F8|
|unk_0825F3F8|
	DCB 0x20,0x04
	DCW 0x037b
	DCD 0x0825edf8,0x0825ee2c,0x0825ee60,0x0825ee90,0x0825eec0,0x0825eefc,0x0825ef30,0x0825ef68
	DCD 0x0825ef9c,0x0825efc4,0x0825efec,0x0825f014,0x0825f03c,0x0825f06c,0x0825f09c,0x0825f0d0
	DCD 0x0825f104,0x0825f134,0x0825f164,0x0825f194,0x0825f1c4,0x0825f1f4,0x0825f224,0x0825f258
	DCD 0x0825f288,0x0825f2b8,0x0825f2e0,0x0825f308,0x0825f330,0x0825f360,0x0825f390,0x0825f3c4
|unk_0825F47C|
        INCBIN  build\animframe\gen_25f47c_25f554.bin
|map_anim_row_0825F554|
|unk_0825F554|
	DCB 0x08,0x02
	DCW 0x0379
	DCD 0x0825f47c,0x0825f494,0x0825f4b0,0x0825f4c8,0x0825f4e4,0x0825f500,0x0825f51c,0x0825f538
|unk_0825F578|
        INCBIN  baserom.gba_0x25f578_0x25f584.extracted
|unk_0825F584|
        INCBIN  build\mapcontainer\map_0025F584_0025F59C.bin
|unk_0825F59C|
        INCBIN  build\mapcontainer\map_0025F59C_0025F5A0.bin
        INCBIN  build\mapcontainer\map_0025F5A0_0025F5F0.bin
        INCBIN  build\mapcontainer\map_0025F5F0_0025F6D8.bin
        INCBIN  build\mapcontainer\map_0025F6D8_0025F700.bin
        INCBIN  build\mapcontainer\map_0025F700_0025F838.bin
        INCBIN  build\mapcontainer\map_0025F838_0025F860.bin
        INCBIN  build\mapcontainer\map_0025F860_0025F9DC.bin
        INCBIN  build\mapcontainer\map_0025F9DC_0025FA04.bin
        INCBIN  build\mapcontainer\map_0025FA04_0025FAA0.bin
|unk_0825FAA0|
        INCBIN  build\mapcontainer\map_0025FAA0_0025FC08.bin
        INCBIN  build\mapcontainer\map_0025FC08_002607B4.bin
|unk_082607B4|
        INCBIN  build\mapcontainer\map_002607B4_002607CC.bin
|unk_082607CC|
        INCBIN  build\mapcontainer\map_002607CC_002607D0.bin
        INCBIN  build\mapcontainer\map_002607D0_00260820.bin
        INCBIN  build\mapcontainer\map_00260820_00260994.bin
        INCBIN  build\mapcontainer\map_00260994_002609BC.bin
        INCBIN  build\mapcontainer\map_002609BC_00260AB8.bin
        INCBIN  build\mapcontainer\map_00260AB8_00260AE0.bin
        INCBIN  build\mapcontainer\map_00260AE0_00260CA0.bin
        INCBIN  build\mapcontainer\map_00260CA0_00260CC8.bin
        INCBIN  build\mapcontainer\map_00260CC8_00260D50.bin
|unk_08260D50|
        INCBIN  build\mapcontainer\map_00260D50_00260D80.bin
        INCBIN  build\mapcontainer\map_00260D80_00260EA8.bin
        INCLUDE rawlabeled_260ea8.s
        INCBIN  build\mapcontainer\map_00261130_00261180.bin
        INCBIN  build\mapcontainer\map_00261180_002619EC.bin
        INCBIN  build\mapcontainer\map_002619EC_00261A28.bin
        INCBIN  build\mapcontainer\map_00261A28_00261A48.bin
        INCBIN  build\mapcontainer\map_00261A48_00261A70.bin
        INCBIN  build\mapcontainer\map_00261A70_00261D88.bin
        INCBIN  build\mapcontainer\map_00261D88_00261DD0.bin
        INCBIN  build\mapcontainer\map_00261DD0_00262C68.bin
        INCBIN  build\mapcontainer\map_00262C68_00262CC0.bin
        INCBIN  build\mapcontainer\map_00262CC0_00262E20.bin
|unk_08262E20|
        INCBIN  build\mapcontainer\map_00262E20_00262E38.bin
        INCBIN  build\mapcontainer\map_00262E38_00262F74.bin
|map_anim_row_08262F74|
|unk_08262F74|
	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x081911d8,0x08191214
|map_anim_row_08262F80|
|unk_08262F80|
	DCB 0x02,0x02
	DCW 0x037c
	DCD 0x081bfd60,0x081bfd9c
|map_anim_row_08262F8C|
|unk_08262F8C|
	DCB 0x10,0x0b
	DCW 0x0371
	DCD 0x0817a9ac,0x0817aaac,0x0817abac,0x0817aca4,0x0817a9ac,0x0817aaac,0x0817ada4,0x0817aaac
	DCD 0x0817aea4,0x0817aaac,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4
|unk_08262FD0|
        INCBIN  build\animframe\gen_262fd0_263528.bin
|map_anim_row_08263528|
|unk_08263528|
	DCB 0x04,0x13
	DCW 0x035e
	DCD 0x08262fd0,0x0826311c,0x0826327c,0x082633d0
|unk_0826353C|
        INCBIN  build\animframe\gen_26353c_263760.bin
|map_anim_row_08263760|
|unk_08263760|
	DCB 0x04,0x0d
	DCW 0x0351
	DCD 0x0826353c,0x082635f4,0x082636a8,0x082635f4
|map_anim_row_08263774|
|unk_08263774|
	DCB 0x04,0x03
	DCW 0x034e
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|unk_08263788|
        INCBIN  baserom.gba_0x263788_0x2637a0.extracted
|unk_082637A0|
        INCBIN  build\mapcontainer\map_002637A0_002637E8.bin
|unk_082637E8|
        INCBIN  build\mapcontainer\map_002637E8_002637F4.bin
        INCBIN  build\mapcontainer\map_002637F4_00263844.bin
        INCBIN  build\mapcontainer\map_00263844_002638A8.bin
        INCBIN  build\mapcontainer\map_002638A8_002638C4.bin
        INCBIN  build\mapcontainer\map_002638C4_00263980.bin
        INCBIN  build\mapcontainer\map_00263980_0026399C.bin
        INCBIN  build\mapcontainer\map_0026399C_002639F8.bin
|unk_082639F8|
        INCBIN  build\mapcontainer\map_002639F8_00263A28.bin
|unk_08263A28|
        INCBIN  build\mapcontainer\map_00263A28_00263A30.bin
        INCBIN  build\mapcontainer\map_00263A30_00263A80.bin
        INCBIN  build\mapcontainer\map_00263A80_00263AF4.bin
        INCBIN  build\mapcontainer\map_00263AF4_00263B10.bin
        INCBIN  build\mapcontainer\map_00263B10_00263B58.bin
        INCBIN  build\mapcontainer\map_00263B58_00263B74.bin
        INCBIN  build\mapcontainer\map_00263B74_00263CD0.bin
        INCBIN  build\mapcontainer\map_00263CD0_00263CEC.bin
        INCBIN  build\mapcontainer\map_00263CEC_00263DE8.bin
        INCBIN  build\mapcontainer\map_00263DE8_00263E04.bin
        INCBIN  build\mapcontainer\map_00263E04_00263E94.bin
|unk_08263E94|
        INCBIN  build\mapcontainer\map_00263E94_00263EAC.bin
|unk_08263EAC|
        INCBIN  build\animframe\gen_263eac_264210.bin
|map_anim_row_08264210|
|unk_08264210|
	DCB 0x04,0x09
	DCW 0x0377
	DCD 0x08263eac,0x08263f7c,0x08264058,0x08264130
|unk_08264224|
        INCBIN  build\animframe\gen_264224_264580.bin
|map_anim_row_08264580|
|unk_08264580|
	DCB 0x0c,0x06
	DCW 0x0371
	DCD 0x08264224,0x0826426c,0x082642b4,0x08264300,0x0826434c,0x08264394,0x082643d8,0x08264420
	DCD 0x08264468,0x082644ac,0x082644f4,0x0826453c
|map_anim_row_082645B4|
|unk_082645B4|
	DCB 0x07,0x04
	DCW 0x036d
	DCD 0x0825d6f0,0x0825d724,0x0825d758,0x0825d78c,0x0825d7bc,0x0825d7f0,0x0825d824
|unk_082645D4|
        INCBIN  baserom.gba_0x2645d4_0x2645e0.extracted
|unk_082645E0|
        INCBIN  build\mapcontainer\map_002645E0_002645F8.bin
|unk_082645F8|
        INCBIN  build\mapcontainer\map_002645F8_002645FC.bin
        INCBIN  build\mapcontainer\map_002645FC_0026464C.bin
        INCBIN  build\mapcontainer\map_0026464C_002646D4.bin
        INCBIN  build\mapcontainer\map_002646D4_002646F0.bin
        INCBIN  build\mapcontainer\map_002646F0_0026474C.bin
        INCBIN  build\mapcontainer\map_0026474C_00264768.bin
        INCBIN  build\mapcontainer\map_00264768_0026485C.bin
        INCBIN  build\mapcontainer\map_0026485C_00264878.bin
        INCBIN  build\mapcontainer\map_00264878_002648EC.bin
|unk_082648EC|
        INCBIN  build\mapcontainer\map_002648EC_00264904.bin
        INCBIN  build\mapcontainer\map_00264904_00264D50.bin
|unk_08264D50|
        INCBIN  build\mapcontainer\map_00264D50_00264DB0.bin
|unk_08264DB0|
        INCBIN  build\mapcontainer\map_00264DB0_00264DC0.bin
        INCBIN  build\mapcontainer\map_00264DC0_00264E10.bin
        INCBIN  build\mapcontainer\map_00264E10_0026512C.bin
|unk_0826512C|
        INCBIN  build\mapcontainer\map_0026512C_00265154.bin
        INCBIN  build\jcalg1\gen_265154.bin
        INCBIN  build\mapcontainer\map_002653E4_0026561C.bin
|unk_0826561C|
        INCBIN  build\mapcontainer\map_0026561C_00265644.bin
        INCBIN  build\jcalg1\gen_265644.bin
        INCBIN  build\mapcontainer\map_002658D8_002659D4.bin
|unk_082659D4|
        INCBIN  build\mapcontainer\map_002659D4_002659FC.bin
        INCBIN  build\jcalg1\gen_2659fc.bin
|unk_08265F74|
        INCBIN  build\mapcontainer\map_00265F74_00265F9C.bin
        INCBIN  build\jcalg1\gen_265f9c.bin
|unk_0826608C|
        INCBIN  build\mapcontainer\map_0026608C_0026617C.bin
        INCBIN  build\jcalg1\gen_26617c.bin
|unk_08266648|
        INCBIN  build\mapcontainer\map_00266648_002666B0.bin
|unk_082666B0|
        INCBIN  build\mapcontainer\map_002666B0_002666BC.bin
|unk_082666BC|
        INCBIN  build\mapcontainer\map_002666BC_0026670C.bin
        INCBIN  build\mapcontainer\map_0026670C_00266BF4.bin
        INCBIN  build\mapcontainer\map_00266BF4_00266C1C.bin
        INCBIN  build\mapcontainer\map_00266C1C_00266E68.bin
        INCBIN  build\mapcontainer\map_00266E68_00266E88.bin
        INCBIN  build\mapcontainer\map_00266E88_002672D4.bin
        INCBIN  build\mapcontainer\map_002672D4_002672FC.bin
        INCBIN  build\mapcontainer\map_002672FC_0026785C.bin
        INCBIN  build\mapcontainer\map_0026785C_00267884.bin
        INCBIN  build\mapcontainer\map_00267884_00267998.bin
|unk_08267998|
        INCBIN  build\mapcontainer\map_00267998_00267A88.bin
|unk_08267A88|
        INCBIN  build\mapcontainer\map_00267A88_00267AF0.bin
|unk_08267AF0|
        INCBIN  build\mapcontainer\map_00267AF0_00267AFC.bin
        INCBIN  build\mapcontainer\map_00267AFC_00267B4C.bin
        INCBIN  build\mapcontainer\map_00267B4C_002685F0.bin
        INCBIN  build\mapcontainer\map_002685F0_00268638.bin
        INCBIN  build\mapcontainer\map_00268638_00268718.bin
        INCBIN  build\mapcontainer\map_00268718_00268748.bin
        INCBIN  build\mapcontainer\map_00268748_0026922C.bin
        INCBIN  build\mapcontainer\map_0026922C_00269284.bin
        INCBIN  build\mapcontainer\map_00269284_0026A1CC.bin
        INCBIN  build\mapcontainer\map_0026A1CC_0026A234.bin
        INCBIN  build\mapcontainer\map_0026A234_0026A410.bin
|unk_0826A410|
        INCBIN  build\mapcontainer\map_0026A410_0026A458.bin
        INCBIN  build\mapcontainer\map_0026A458_0026A6D8.bin
|unk_0826A6D8|
        INCBIN  build\mapcontainer\map_0026A6D8_0026A770.bin
|unk_0826A770|
        INCBIN  build\mapcontainer\map_0026A770_0026A778.bin
        INCBIN  build\mapcontainer\map_0026A778_0026A7C8.bin
        INCBIN  build\mapcontainer\map_0026A7C8_0026A86C.bin
        INCBIN  build\mapcontainer\map_0026A86C_0026A888.bin
        INCBIN  build\mapcontainer\map_0026A888_0026A89C.bin
        INCBIN  build\mapcontainer\map_0026A89C_0026A8EC.bin
        INCBIN  build\mapcontainer\map_0026A8EC_0026A99C.bin
        INCBIN  build\mapcontainer\map_0026A99C_0026A9B8.bin
        INCBIN  build\mapcontainer\map_0026A9B8_0026AA64.bin
        INCBIN  build\mapcontainer\map_0026AA64_0026AA80.bin
        INCBIN  build\mapcontainer\map_0026AA80_0026AB30.bin
        INCBIN  build\mapcontainer\map_0026AB30_0026AB4C.bin
        INCBIN  build\mapcontainer\map_0026AB4C_0026AB78.bin
        INCBIN  build\mapcontainer\map_0026AB78_0026AB94.bin
        INCBIN  build\mapcontainer\map_0026AB94_0026ABC0.bin
|unk_0826ABC0|
        INCBIN  build\mapcontainer\map_0026ABC0_0026AC08.bin
        INCBIN  build\mapcontainer\map_0026AC08_0026AD50.bin
        INCBIN  build\mapcontainer\map_0026AD50_0026ADA0.bin
        INCBIN  build\mapcontainer\map_0026ADA0_0026AE74.bin
        INCBIN  build\mapcontainer\map_0026AE74_0026AE9C.bin
        INCBIN  build\mapcontainer\map_0026AE9C_0026AFB8.bin
        INCBIN  build\mapcontainer\map_0026AFB8_0026AFD8.bin
        INCBIN  build\mapcontainer\map_0026AFD8_0026B0BC.bin
        INCBIN  build\mapcontainer\map_0026B0BC_0026B0E4.bin
        INCBIN  build\mapcontainer\map_0026B0E4_0026B14C.bin
|unk_0826B14C|
        INCBIN  build\mapcontainer\map_0026B14C_0026B26C.bin
        INCBIN  build\mapcontainer\map_0026B26C_0026B808.bin
|unk_0826B808|
        INCBIN  build\mapcontainer\map_0026B808_0026B820.bin
|unk_0826B820|
        INCBIN  build\mapcontainer\map_0026B820_0026B824.bin
        INCBIN  build\mapcontainer\map_0026B824_0026B874.bin
        INCBIN  build\mapcontainer\map_0026B874_0026B8F4.bin
        INCBIN  build\mapcontainer\map_0026B8F4_0026B91C.bin
        INCBIN  build\mapcontainer\map_0026B91C_0026BA44.bin
        INCBIN  build\mapcontainer\map_0026BA44_0026BA64.bin
        INCBIN  build\mapcontainer\map_0026BA64_0026BB08.bin
        INCBIN  build\mapcontainer\map_0026BB08_0026BB30.bin
        INCBIN  build\mapcontainer\map_0026BB30_0026BB94.bin
|unk_0826BB94|
        INCBIN  build\mapcontainer\map_0026BB94_0026BC9C.bin
        INCBIN  build\mapcontainer\map_0026BC9C_0026C29C.bin
|unk_0826C29C|
        INCBIN  build\mapcontainer\map_0026C29C_0026C2B4.bin
|unk_0826C2B4|
        INCBIN  build\mapcontainer\map_0026C2B4_0026C2B8.bin
        INCBIN  build\mapcontainer\map_0026C2B8_0026C308.bin
        INCBIN  build\mapcontainer\map_0026C308_0026C434.bin
        INCBIN  build\mapcontainer\map_0026C434_0026C45C.bin
        INCBIN  build\mapcontainer\map_0026C45C_0026C61C.bin
        INCBIN  build\mapcontainer\map_0026C61C_0026C644.bin
        INCBIN  build\mapcontainer\map_0026C644_0026C830.bin
        INCBIN  build\mapcontainer\map_0026C830_0026C858.bin
        INCBIN  build\mapcontainer\map_0026C858_0026C8D4.bin
|unk_0826C8D4|
        INCBIN  build\mapcontainer\map_0026C8D4_0026C97C.bin
        INCBIN  build\mapcontainer\map_0026C97C_0026CE28.bin
|unk_0826CE28|
        INCBIN  build\mapcontainer\map_0026CE28_0026CE70.bin
|unk_0826CE70|
        INCBIN  build\mapcontainer\map_0026CE70_0026CE7C.bin
        INCBIN  build\mapcontainer\map_0026CE7C_0026CECC.bin
        INCBIN  build\mapcontainer\map_0026CECC_0026D03C.bin
        INCBIN  build\mapcontainer\map_0026D03C_0026D05C.bin
        INCBIN  build\mapcontainer\map_0026D05C_0026D148.bin
        INCBIN  build\mapcontainer\map_0026D148_0026D168.bin
        INCBIN  build\mapcontainer\map_0026D168_0026D3B8.bin
        INCBIN  build\mapcontainer\map_0026D3B8_0026D3D8.bin
        INCBIN  build\mapcontainer\map_0026D3D8_0026D48C.bin
|unk_0826D48C|
        INCBIN  build\mapcontainer\map_0026D48C_0026D4DC.bin
|unk_0826D4DC|
        INCBIN  build\mapcontainer\map_0026D4DC_0026D4E4.bin
        INCBIN  build\mapcontainer\map_0026D4E4_0026D534.bin
        INCBIN  build\mapcontainer\map_0026D534_0026D574.bin
        INCBIN  build\mapcontainer\map_0026D574_0026D590.bin
        INCBIN  build\mapcontainer\map_0026D590_0026D7E0.bin
        INCBIN  build\mapcontainer\map_0026D7E0_0026D800.bin
        INCBIN  build\mapcontainer\map_0026D800_0026D9BC.bin
        INCBIN  build\mapcontainer\map_0026D9BC_0026D9DC.bin
        INCBIN  build\mapcontainer\map_0026D9DC_0026DAA0.bin
|unk_0826DAA0|
        INCBIN  build\mapcontainer\map_0026DAA0_0026DAF0.bin
|unk_0826DAF0|
        INCBIN  build\mapcontainer\map_0026DAF0_0026DAF8.bin
        INCBIN  build\mapcontainer\map_0026DAF8_0026DB48.bin
        INCBIN  build\mapcontainer\map_0026DB48_0026DB80.bin
        INCBIN  build\mapcontainer\map_0026DB80_0026DB9C.bin
        INCBIN  build\mapcontainer\map_0026DB9C_0026DDC4.bin
        INCBIN  build\mapcontainer\map_0026DDC4_0026DDE4.bin
        INCBIN  build\mapcontainer\map_0026DDE4_0026DFA4.bin
        INCBIN  build\mapcontainer\map_0026DFA4_0026DFC4.bin
        INCBIN  build\mapcontainer\map_0026DFC4_0026E074.bin
|unk_0826E074|
        INCBIN  build\mapcontainer\map_0026E074_0026E0C4.bin
|unk_0826E0C4|
        INCBIN  build\mapcontainer\map_0026E0C4_0026E0CC.bin
        INCBIN  build\mapcontainer\map_0026E0CC_0026E11C.bin
        INCBIN  build\mapcontainer\map_0026E11C_0026E16C.bin
        INCBIN  build\mapcontainer\map_0026E16C_0026E188.bin
        INCBIN  build\mapcontainer\map_0026E188_0026E3F8.bin
        INCBIN  build\mapcontainer\map_0026E3F8_0026E418.bin
        INCBIN  build\mapcontainer\map_0026E418_0026E598.bin
        INCBIN  build\mapcontainer\map_0026E598_0026E5B8.bin
        INCBIN  build\mapcontainer\map_0026E5B8_0026E678.bin
|unk_0826E678|
        INCBIN  build\mapcontainer\map_0026E678_0026E6C8.bin
|unk_0826E6C8|
        INCBIN  build\mapcontainer\map_0026E6C8_0026E6D0.bin
        INCBIN  build\mapcontainer\map_0026E6D0_0026E720.bin
        INCBIN  build\mapcontainer\map_0026E720_0026E76C.bin
        INCBIN  build\mapcontainer\map_0026E76C_0026E788.bin
        INCBIN  build\mapcontainer\map_0026E788_0026E9CC.bin
        INCBIN  build\mapcontainer\map_0026E9CC_0026E9EC.bin
        INCBIN  build\mapcontainer\map_0026E9EC_0026EB90.bin
        INCBIN  build\mapcontainer\map_0026EB90_0026EBB0.bin
        INCBIN  build\mapcontainer\map_0026EBB0_0026EC80.bin
|unk_0826EC80|
        INCBIN  build\mapcontainer\map_0026EC80_0026ECD0.bin
|unk_0826ECD0|
        INCBIN  build\mapcontainer\map_0026ECD0_0026ECD8.bin
        INCBIN  build\mapcontainer\map_0026ECD8_0026ED28.bin
        INCBIN  build\mapcontainer\map_0026ED28_0026EE38.bin
        INCBIN  build\mapcontainer\map_0026EE38_0026EE58.bin
        INCBIN  build\mapcontainer\map_0026EE58_0026F01C.bin
        INCBIN  build\mapcontainer\map_0026F01C_0026F03C.bin
        INCBIN  build\mapcontainer\map_0026F03C_0026F2D4.bin
        INCBIN  build\mapcontainer\map_0026F2D4_0026F2F4.bin
        INCBIN  build\mapcontainer\map_0026F2F4_0026F5E4.bin
        INCBIN  build\mapcontainer\map_0026F5E4_0026F604.bin
        INCBIN  build\mapcontainer\map_0026F604_0026F6C0.bin
|unk_0826F6C0|
        INCBIN  build\animframe\gen_26f6c0_26fd70.bin
|unk_0826FD70|
        INCBIN  build\mapcontainer\map_0026FD70_0026FE20.bin
|unk_0826FE20|
        INCBIN  build\mapcontainer\map_0026FE20_0026FE2C.bin
        INCBIN  build\mapcontainer\map_0026FE2C_0026FE7C.bin
        INCBIN  build\mapcontainer\map_0026FE7C_0026FEDC.bin
        INCBIN  build\mapcontainer\map_0026FEDC_0026FF04.bin
        INCBIN  build\mapcontainer\map_0026FF04_0026FF74.bin
        INCBIN  build\mapcontainer\map_0026FF74_0026FF9C.bin
        INCBIN  build\mapcontainer\map_0026FF9C_002703F8.bin
        INCBIN  build\mapcontainer\map_002703F8_00270420.bin
        INCBIN  build\mapcontainer\map_00270420_002708B8.bin
        INCBIN  build\mapcontainer\map_002708B8_002708E0.bin
        INCBIN  build\mapcontainer\map_002708E0_002709C4.bin
|unk_082709C4|
        INCBIN  build\mapcontainer\map_002709C4_002709FC.bin
|unk_082709FC|
        INCBIN  build\mapcontainer\map_002709FC_00270A00.bin
        INCBIN  build\mapcontainer\map_00270A00_00270A50.bin
        INCBIN  build\mapcontainer\map_00270A50_00270ADC.bin
        INCBIN  build\mapcontainer\map_00270ADC_00270AF8.bin
        INCBIN  build\mapcontainer\map_00270AF8_00270CC4.bin
        INCBIN  build\mapcontainer\map_00270CC4_00270CE0.bin
        INCBIN  build\mapcontainer\map_00270CE0_00270D38.bin
|unk_08270D38|
        INCBIN  build\mapcontainer\map_00270D38_00270D50.bin
|unk_08270D50|
        INCBIN  build\mapcontainer\map_00270D50_00270D54.bin
        INCBIN  build\mapcontainer\map_00270D54_00270DA4.bin
        INCBIN  build\mapcontainer\map_00270DA4_00270EBC.bin
        INCBIN  build\mapcontainer\map_00270EBC_00270EDC.bin
        INCBIN  build\mapcontainer\map_00270EDC_00271084.bin
        INCBIN  build\mapcontainer\map_00271084_002710A4.bin
        INCBIN  build\mapcontainer\map_002710A4_00271134.bin
|unk_08271134|
        INCBIN  build\mapcontainer\map_00271134_0027114C.bin
        INCBIN  build\mapcontainer\map_0027114C_00271258.bin
|unk_08271258|
        INCBIN  build\mapcontainer\map_00271258_00271288.bin
|unk_08271288|
        INCBIN  build\mapcontainer\map_00271288_00271290.bin
        INCBIN  build\mapcontainer\map_00271290_002712E0.bin
        INCBIN  build\mapcontainer\map_002712E0_00271414.bin
        INCBIN  build\mapcontainer\map_00271414_00271434.bin
        INCBIN  build\mapcontainer\map_00271434_00271520.bin
        INCBIN  build\mapcontainer\map_00271520_00271540.bin
        INCBIN  build\mapcontainer\map_00271540_002716FC.bin
        INCBIN  build\mapcontainer\map_002716FC_0027171C.bin
        INCBIN  build\mapcontainer\map_0027171C_00271878.bin
        INCBIN  build\mapcontainer\map_00271878_00271898.bin
        INCBIN  build\mapcontainer\map_00271898_00271948.bin
|unk_08271948|
        INCBIN  build\mapcontainer\map_00271948_00271978.bin
|unk_08271978|
        INCBIN  build\mapcontainer\map_00271978_00271980.bin
        INCBIN  build\mapcontainer\map_00271980_002719D0.bin
        INCBIN  build\mapcontainer\map_002719D0_00271B00.bin
        INCBIN  build\mapcontainer\map_00271B00_00271B1C.bin
        INCBIN  build\mapcontainer\map_00271B1C_00271B4C.bin
        INCBIN  build\mapcontainer\map_00271B4C_00271B68.bin
        INCBIN  build\mapcontainer\map_00271B68_00271C18.bin
        INCBIN  build\mapcontainer\map_00271C18_00271C34.bin
        INCBIN  build\mapcontainer\map_00271C34_00271E1C.bin
        INCBIN  build\mapcontainer\map_00271E1C_00271E38.bin
        INCBIN  build\mapcontainer\map_00271E38_00271EC4.bin
|unk_08271EC4|
        INCBIN  build\mapcontainer\map_00271EC4_00271EF4.bin
|unk_08271EF4|
        INCBIN  build\mapcontainer\map_00271EF4_00271F0C.bin
|unk_08271F0C|
        INCBIN  build\mapcontainer\map_00271F0C_00271F10.bin
        INCBIN  build\mapcontainer\map_00271F10_00271F60.bin
        INCBIN  build\mapcontainer\map_00271F60_00272074.bin
        INCBIN  build\mapcontainer\map_00272074_0027209C.bin
        INCBIN  build\mapcontainer\map_0027209C_002720F4.bin
        INCBIN  build\mapcontainer\map_002720F4_00272110.bin
        INCBIN  build\mapcontainer\map_00272110_00272280.bin
        INCBIN  build\mapcontainer\map_00272280_002722A0.bin
        INCBIN  build\mapcontainer\map_002722A0_002724D8.bin
        INCBIN  build\mapcontainer\map_002724D8_00272500.bin
        INCBIN  build\mapcontainer\map_00272500_002725B8.bin
|unk_082725B8|
        INCBIN  build\mapcontainer\map_002725B8_002725E8.bin
|unk_082725E8|
        INCBIN  build\mapcontainer\map_002725E8_002725F0.bin
        INCBIN  build\mapcontainer\map_002725F0_00272640.bin
        INCBIN  build\mapcontainer\map_00272640_00272698.bin
        INCBIN  build\mapcontainer\map_00272698_002726B8.bin
        INCBIN  build\mapcontainer\map_002726B8_00272744.bin
        INCBIN  build\mapcontainer\map_00272744_00272764.bin
        INCBIN  build\mapcontainer\map_00272764_002729F0.bin
        INCBIN  build\mapcontainer\map_002729F0_00272A10.bin
        INCBIN  build\mapcontainer\map_00272A10_00272C70.bin
        INCBIN  build\mapcontainer\map_00272C70_00272C98.bin
        INCBIN  build\mapcontainer\map_00272C98_00272D48.bin
        INCLUDE rawlabeled_272d48.s
        INCBIN  build\mapcontainer\map_00272DA0_00272DF0.bin
        INCBIN  build\mapcontainer\map_00272DF0_00272FC0.bin
        INCBIN  build\mapcontainer\map_00272FC0_00272FF0.bin
        INCBIN  build\mapcontainer\map_00272FF0_00273214.bin
        INCBIN  build\mapcontainer\map_00273214_00273234.bin
        INCBIN  build\mapcontainer\map_00273234_00273400.bin
        INCBIN  build\mapcontainer\map_00273400_00273430.bin
        INCBIN  build\mapcontainer\map_00273430_0027391C.bin
        INCBIN  build\mapcontainer\map_0027391C_00273954.bin
        INCBIN  build\mapcontainer\map_00273954_00273A40.bin
|unk_08273A40|
        INCBIN  build\mapcontainer\map_00273A40_00273AA8.bin
|unk_08273AA8|
        INCBIN  build\mapcontainer\map_00273AA8_00273AB4.bin
        INCBIN  build\mapcontainer\map_00273AB4_00273B04.bin
        INCBIN  build\mapcontainer\map_00273B04_00273D64.bin
        INCBIN  build\mapcontainer\map_00273D64_00273D88.bin
        INCBIN  build\mapcontainer\map_00273D88_00273ED0.bin
        INCBIN  build\mapcontainer\map_00273ED0_00273EF4.bin
        INCBIN  build\mapcontainer\map_00273EF4_00274158.bin
        INCBIN  build\mapcontainer\map_00274158_0027417C.bin
        INCBIN  build\mapcontainer\map_0027417C_00274494.bin
        INCBIN  build\mapcontainer\map_00274494_002744BC.bin
        INCBIN  build\mapcontainer\map_002744BC_00274598.bin
|unk_08274598|
        INCBIN  build\animframe\gen_274598_274d84.bin
|unk_08274D84|
        INCBIN  build\mapcontainer\map_00274D84_00274E34.bin
|unk_08274E34|
        INCBIN  build\mapcontainer\map_00274E34_00274E4C.bin
        INCBIN  build\mapcontainer\map_00274E4C_00274E9C.bin
        INCBIN  build\mapcontainer\map_00274E9C_00275058.bin
        INCBIN  build\mapcontainer\map_00275058_00275080.bin
        INCBIN  build\mapcontainer\map_00275080_002753E8.bin
        INCBIN  build\mapcontainer\map_002753E8_0027540C.bin
        INCBIN  build\mapcontainer\map_0027540C_002757FC.bin
        INCBIN  build\mapcontainer\map_002757FC_00275820.bin
        INCBIN  build\mapcontainer\map_00275820_00275B20.bin
        INCBIN  build\mapcontainer\map_00275B20_00275B58.bin
        INCBIN  build\mapcontainer\map_00275B58_00275C60.bin
        INCLUDE rawlabeled_275c60.s
        INCBIN  build\mapcontainer\map_00275CA8_00275FE8.bin
        INCLUDE rawlabeled_275fe8.s
        INCBIN  build\mapcontainer\map_00276088_002760D8.bin
        INCBIN  build\mapcontainer\map_002760D8_00276448.bin
        INCBIN  build\mapcontainer\map_00276448_00276470.bin
        INCBIN  build\mapcontainer\map_00276470_00276714.bin
        INCBIN  build\mapcontainer\map_00276714_0027673C.bin
        INCBIN  build\mapcontainer\map_0027673C_00276BD8.bin
        INCBIN  build\mapcontainer\map_00276BD8_00276C00.bin
        INCBIN  build\mapcontainer\map_00276C00_00276D40.bin
|unk_08276D40|
        INCBIN  build\mapcontainer\map_00276D40_00276D58.bin
|unk_08276D58|
        INCBIN  build\mapcontainer\map_00276D58_00276DD8.bin
|unk_08276DD8|
        INCBIN  build\mapcontainer\map_00276DD8_00276DDC.bin
        INCBIN  build\mapcontainer\map_00276DDC_00276E2C.bin
        INCBIN  build\mapcontainer\map_00276E2C_00276F74.bin
        INCBIN  build\mapcontainer\map_00276F74_00276F90.bin
        INCBIN  build\mapcontainer\map_00276F90_00277004.bin
        INCBIN  build\mapcontainer\map_00277004_00277020.bin
        INCBIN  build\mapcontainer\map_00277020_002770A0.bin
        INCBIN  build\mapcontainer\map_002770A0_002770BC.bin
        INCBIN  build\mapcontainer\map_002770BC_002771AC.bin
        INCBIN  build\mapcontainer\map_002771AC_002771C8.bin
        INCBIN  build\mapcontainer\map_002771C8_0027723C.bin
|unk_0827723C|
        INCBIN  build\mapcontainer\map_0027723C_00277284.bin
        INCBIN  build\mapcontainer\map_00277284_00277374.bin
|unk_08277374|
        INCBIN  build\mapcontainer\map_00277374_0027738C.bin
|unk_0827738C|
        INCBIN  build\mapcontainer\map_0027738C_00277390.bin
        INCBIN  build\mapcontainer\map_00277390_002773E0.bin
        INCBIN  build\mapcontainer\map_002773E0_00277408.bin
        INCBIN  build\mapcontainer\map_00277408_00277424.bin
        INCBIN  build\mapcontainer\map_00277424_002774D8.bin
        INCBIN  build\mapcontainer\map_002774D8_002774F4.bin
        INCBIN  build\mapcontainer\map_002774F4_002776DC.bin
        INCBIN  build\mapcontainer\map_002776DC_002776F8.bin
        INCBIN  build\mapcontainer\map_002776F8_00277838.bin
        INCBIN  build\mapcontainer\map_00277838_00277854.bin
        INCBIN  build\mapcontainer\map_00277854_00277950.bin
|unk_08277950|
        INCBIN  build\mapcontainer\map_00277950_00277998.bin
        INCBIN  build\mapcontainer\map_00277998_00277C08.bin
|unk_08277C08|
        INCBIN  build\animframe\gen_277c08_277c60.bin
|map_anim_row_08277C60|
|unk_08277C60|
	DCB 0x02,0x01
	DCW 0x037f
	DCD 0x08277c08,0x08277c34
|map_anim_row_08277C6C|
|unk_08277C6C|
	DCB 0x04,0x03
	DCW 0x037c
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|unk_08277C80|
        INCBIN  build\animframe\gen_277c80_2781e4.bin
|map_anim_row_082781E4|
|unk_082781E4|
	DCB 0x12,0x0d
	DCW 0x036f
	DCD 0x08277c80,0x08277d1c,0x08277df4,0x08277d1c,0x08277c80,0x08277d1c,0x08277df4,0x08277d1c
	DCD 0x08277c80,0x08277d1c,0x08277df4,0x08277d1c,0x08277c80,0x08277d1c,0x08277df4,0x08277ef8
	DCD 0x0827801c,0x08278118
|unk_08278230|
        INCBIN  baserom.gba_0x278230_0x27823c.extracted
|unk_0827823C|
        INCBIN  build\mapcontainer\map_0027823C_00278254.bin
|unk_08278254|
        INCBIN  build\mapcontainer\map_00278254_00278258.bin
        INCBIN  build\mapcontainer\map_00278258_002782A8.bin
        INCBIN  build\mapcontainer\map_002782A8_00278364.bin
        INCBIN  build\mapcontainer\map_00278364_00278380.bin
        INCBIN  build\mapcontainer\map_00278380_00278408.bin
        INCBIN  build\mapcontainer\map_00278408_00278424.bin
        INCBIN  build\mapcontainer\map_00278424_0027861C.bin
        INCBIN  build\mapcontainer\map_0027861C_0027863C.bin
        INCBIN  build\mapcontainer\map_0027863C_002787A8.bin
        INCBIN  build\mapcontainer\map_002787A8_002787C8.bin
        INCBIN  build\mapcontainer\map_002787C8_002788CC.bin
|unk_082788CC|
        INCBIN  build\mapcontainer\map_002788CC_002789CC.bin
|unk_082789CC|
        INCBIN  build\mapcontainer\map_002789CC_002789D4.bin
        INCBIN  build\mapcontainer\map_002789D4_00278A24.bin
        INCBIN  build\mapcontainer\map_00278A24_00278AB4.bin
        INCBIN  build\mapcontainer\map_00278AB4_00278AD0.bin
        INCBIN  build\mapcontainer\map_00278AD0_00278B7C.bin
        INCBIN  build\mapcontainer\map_00278B7C_00278B9C.bin
        INCBIN  build\mapcontainer\map_00278B9C_00278DD0.bin
        INCBIN  build\mapcontainer\map_00278DD0_00278DF0.bin
        INCBIN  build\mapcontainer\map_00278DF0_00278FD8.bin
        INCBIN  build\mapcontainer\map_00278FD8_00278FF8.bin
        INCBIN  build\mapcontainer\map_00278FF8_00279120.bin
|unk_08279120|
        INCBIN  build\mapcontainer\map_00279120_00279220.bin
|unk_08279220|
        INCBIN  build\mapcontainer\map_00279220_00279228.bin
        INCBIN  build\mapcontainer\map_00279228_00279278.bin
        INCBIN  build\mapcontainer\map_00279278_0027934C.bin
        INCBIN  build\mapcontainer\map_0027934C_00279368.bin
        INCBIN  build\mapcontainer\map_00279368_00279410.bin
        INCBIN  build\mapcontainer\map_00279410_00279430.bin
        INCBIN  build\mapcontainer\map_00279430_002796CC.bin
        INCBIN  build\mapcontainer\map_002796CC_002796EC.bin
        INCBIN  build\mapcontainer\map_002796EC_00279924.bin
        INCBIN  build\mapcontainer\map_00279924_00279944.bin
        INCBIN  build\mapcontainer\map_00279944_00279ABC.bin
|map_anim_row_08279ABC|
|unk_08279ABC|
	DCB 0x04,0x03
	DCW 0x037d
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|map_anim_row_08279AD0|
|unk_08279AD0|
	DCB 0x02,0x01
	DCW 0x037c
	DCD 0x08191288,0x0819125c
|map_anim_row_08279ADC|
|unk_08279ADC|
	DCB 0x02,0x01
	DCW 0x037b
	DCD 0x08277c08,0x08277c34
|map_anim_row_08279AE8|
|unk_08279AE8|
	DCB 0x12,0x17
	DCW 0x0364
	DCD 0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c,0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c
	DCD 0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c,0x0821fc60,0x0821fd7c,0x0821fee8,0x082200a0
	DCD 0x08220288,0x08220434
|unk_08279B34|
        INCBIN  build\animframe\gen_279b34_279e94.bin
|map_anim_row_08279E94|
|unk_08279E94|
	DCB 0x10,0x05
	DCW 0x035f
	DCD 0x08279b34,0x08279bb4,0x08279c30,0x08279ca4,0x08279b34,0x08279bb4,0x08279d20,0x08279bb4
	DCD 0x08279da0,0x08279bb4,0x08279e20,0x08279ca4,0x08279e20,0x08279ca4,0x08279e20,0x08279ca4
|unk_08279ED8|
        INCBIN  baserom.gba_0x279ed8_0x279eec.extracted
|unk_08279EEC|
        INCBIN  build\mapcontainer\map_00279EEC_00279F1C.bin
|unk_08279F1C|
        INCBIN  build\mapcontainer\map_00279F1C_00279F24.bin
        INCBIN  build\mapcontainer\map_00279F24_00279F74.bin
        INCBIN  build\mapcontainer\map_00279F74_00279FC8.bin
        INCBIN  build\mapcontainer\map_00279FC8_00279FE4.bin
        INCBIN  build\mapcontainer\map_00279FE4_0027A084.bin
        INCBIN  build\mapcontainer\map_0027A084_0027A0A0.bin
        INCBIN  build\mapcontainer\map_0027A0A0_0027A290.bin
        INCBIN  build\mapcontainer\map_0027A290_0027A2AC.bin
        INCBIN  build\mapcontainer\map_0027A2AC_0027A370.bin
        INCBIN  build\mapcontainer\map_0027A370_0027A38C.bin
        INCBIN  build\mapcontainer\map_0027A38C_0027A4A0.bin
|unk_0827A4A0|
        INCBIN  build\mapcontainer\map_0027A4A0_0027A548.bin
|unk_0827A548|
        INCBIN  build\mapcontainer\map_0027A548_0027A550.bin
        INCBIN  build\mapcontainer\map_0027A550_0027A5A0.bin
        INCBIN  build\mapcontainer\map_0027A5A0_0027A5D8.bin
        INCBIN  build\mapcontainer\map_0027A5D8_0027A5F4.bin
        INCBIN  build\mapcontainer\map_0027A5F4_0027A688.bin
        INCBIN  build\mapcontainer\map_0027A688_0027A6A4.bin
        INCBIN  build\mapcontainer\map_0027A6A4_0027A758.bin
        INCBIN  build\mapcontainer\map_0027A758_0027A774.bin
        INCBIN  build\mapcontainer\map_0027A774_0027A834.bin
        INCBIN  build\mapcontainer\map_0027A834_0027A850.bin
        INCBIN  build\mapcontainer\map_0027A850_0027A900.bin
|unk_0827A900|
        INCBIN  build\mapcontainer\map_0027A900_0027A930.bin
|unk_0827A930|
        INCBIN  build\mapcontainer\map_0027A930_0027A938.bin
        INCBIN  build\mapcontainer\map_0027A938_0027A988.bin
        INCBIN  build\mapcontainer\map_0027A988_0027A9FC.bin
        INCBIN  build\mapcontainer\map_0027A9FC_0027AA18.bin
        INCBIN  build\mapcontainer\map_0027AA18_0027AAB4.bin
        INCBIN  build\mapcontainer\map_0027AAB4_0027AAD0.bin
        INCBIN  build\mapcontainer\map_0027AAD0_0027AC68.bin
        INCBIN  build\mapcontainer\map_0027AC68_0027AC84.bin
        INCBIN  build\mapcontainer\map_0027AC84_0027AD5C.bin
        INCBIN  build\mapcontainer\map_0027AD5C_0027AD78.bin
        INCBIN  build\mapcontainer\map_0027AD78_0027AE9C.bin
|unk_0827AE9C|
        INCBIN  build\mapcontainer\map_0027AE9C_0027AECC.bin
|unk_0827AECC|
        INCBIN  build\mapcontainer\map_0027AECC_0027AED4.bin
        INCBIN  build\mapcontainer\map_0027AED4_0027AF24.bin
        INCBIN  build\mapcontainer\map_0027AF24_0027B27C.bin
        INCBIN  build\mapcontainer\map_0027B27C_0027B2A4.bin
        INCBIN  build\mapcontainer\map_0027B2A4_0027B3B8.bin
        INCBIN  build\mapcontainer\map_0027B3B8_0027B3D8.bin
        INCBIN  build\mapcontainer\map_0027B3D8_0027B6C4.bin
        INCBIN  build\mapcontainer\map_0027B6C4_0027B6E4.bin
        INCBIN  build\mapcontainer\map_0027B6E4_0027BBF8.bin
        INCBIN  build\mapcontainer\map_0027BBF8_0027BC20.bin
        INCBIN  build\mapcontainer\map_0027BC20_0027BD78.bin
|unk_0827BD78|
        INCBIN  build\mapcontainer\map_0027BD78_0027BDA8.bin
        INCBIN  build\mapcontainer\map_0027BDA8_0027C04C.bin
|unk_0827C04C|
        INCBIN  build\mapcontainer\map_0027C04C_0027C0E4.bin
|unk_0827C0E4|
        INCBIN  build\mapcontainer\map_0027C0E4_0027C0EC.bin
        INCBIN  build\mapcontainer\map_0027C0EC_0027C13C.bin
        INCBIN  build\mapcontainer\map_0027C13C_0027C2B8.bin
        INCBIN  build\mapcontainer\map_0027C2B8_0027C2D4.bin
        INCBIN  build\mapcontainer\map_0027C2D4_0027C330.bin
        INCBIN  build\mapcontainer\map_0027C330_0027C34C.bin
        INCBIN  build\mapcontainer\map_0027C34C_0027C50C.bin
        INCBIN  build\mapcontainer\map_0027C50C_0027C528.bin
        INCBIN  build\mapcontainer\map_0027C528_0027C614.bin
|unk_0827C614|
        INCBIN  build\mapcontainer\map_0027C614_0027C6AC.bin
|unk_0827C6AC|
        INCBIN  build\mapcontainer\map_0027C6AC_0027C6B4.bin
        INCBIN  build\mapcontainer\map_0027C6B4_0027C704.bin
        INCBIN  build\mapcontainer\map_0027C704_0027C868.bin
        INCBIN  build\mapcontainer\map_0027C868_0027C884.bin
        INCBIN  build\mapcontainer\map_0027C884_0027C8C8.bin
        INCBIN  build\mapcontainer\map_0027C8C8_0027C8E4.bin
        INCBIN  build\mapcontainer\map_0027C8E4_0027CA44.bin
        INCBIN  build\mapcontainer\map_0027CA44_0027CA60.bin
        INCBIN  build\mapcontainer\map_0027CA60_0027CB28.bin
|unk_0827CB28|
        INCBIN  build\mapcontainer\map_0027CB28_0027CBC0.bin
|unk_0827CBC0|
        INCBIN  build\mapcontainer\map_0027CBC0_0027CBC8.bin
        INCBIN  build\mapcontainer\map_0027CBC8_0027CC18.bin
        INCBIN  build\mapcontainer\map_0027CC18_0027CEC0.bin
        INCBIN  build\mapcontainer\map_0027CEC0_0027CEE0.bin
        INCBIN  build\mapcontainer\map_0027CEE0_0027CF6C.bin
        INCBIN  build\mapcontainer\map_0027CF6C_0027CF8C.bin
        INCBIN  build\mapcontainer\map_0027CF8C_0027D2E0.bin
        INCBIN  build\mapcontainer\map_0027D2E0_0027D300.bin
        INCBIN  build\mapcontainer\map_0027D300_0027D454.bin
|unk_0827D454|
        INCBIN  build\mapcontainer\map_0027D454_0027D4EC.bin
|unk_0827D4EC|
        INCBIN  build\mapcontainer\map_0027D4EC_0027D4F4.bin
        INCBIN  build\mapcontainer\map_0027D4F4_0027D544.bin
        INCBIN  build\mapcontainer\map_0027D544_0027D7D0.bin
        INCBIN  build\mapcontainer\map_0027D7D0_0027D7F8.bin
        INCBIN  build\mapcontainer\map_0027D7F8_0027D91C.bin
        INCBIN  build\mapcontainer\map_0027D91C_0027D944.bin
        INCBIN  build\mapcontainer\map_0027D944_0027DAD4.bin
        INCBIN  build\mapcontainer\map_0027DAD4_0027DAFC.bin
        INCBIN  build\mapcontainer\map_0027DAFC_0027DF68.bin
        INCBIN  build\mapcontainer\map_0027DF68_0027DF90.bin
        INCBIN  build\mapcontainer\map_0027DF90_0027E0D4.bin
|unk_0827E0D4|
        INCBIN  build\mapcontainer\map_0027E0D4_0027E0EC.bin
        INCBIN  build\mapcontainer\map_0027E0EC_0027E288.bin
|unk_0827E288|
        INCBIN  build\mapcontainer\map_0027E288_0027E338.bin
|unk_0827E338|
        INCBIN  build\mapcontainer\map_0027E338_0027E344.bin
        INCBIN  build\mapcontainer\map_0027E344_0027E394.bin
        INCBIN  build\mapcontainer\map_0027E394_0027E83C.bin
        INCBIN  build\mapcontainer\map_0027E83C_0027E864.bin
        INCBIN  build\mapcontainer\map_0027E864_0027E930.bin
        INCBIN  build\mapcontainer\map_0027E930_0027E958.bin
        INCBIN  build\mapcontainer\map_0027E958_0027EEFC.bin
        INCBIN  build\mapcontainer\map_0027EEFC_0027EF24.bin
        INCBIN  build\mapcontainer\map_0027EF24_0027F088.bin
|unk_0827F088|
        INCBIN  build\mapcontainer\map_0027F088_0027F120.bin
|unk_0827F120|
        INCBIN  build\mapcontainer\map_0027F120_0027F128.bin
        INCBIN  build\mapcontainer\map_0027F128_0027F178.bin
        INCBIN  build\mapcontainer\map_0027F178_0027F3DC.bin
        INCBIN  build\mapcontainer\map_0027F3DC_0027F3FC.bin
        INCBIN  build\mapcontainer\map_0027F3FC_0027F444.bin
        INCBIN  build\mapcontainer\map_0027F444_0027F464.bin
        INCBIN  build\mapcontainer\map_0027F464_0027F50C.bin
        INCBIN  build\mapcontainer\map_0027F50C_0027F52C.bin
        INCBIN  build\mapcontainer\map_0027F52C_0027F87C.bin
        INCBIN  build\mapcontainer\map_0027F87C_0027F89C.bin
        INCBIN  build\mapcontainer\map_0027F89C_0027F9B0.bin
|unk_0827F9B0|
        INCBIN  build\mapcontainer\map_0027F9B0_0027F9E0.bin
|unk_0827F9E0|
        INCBIN  build\mapcontainer\map_0027F9E0_0027FA78.bin
|unk_0827FA78|
        INCBIN  build\mapcontainer\map_0027FA78_0027FA80.bin
        INCBIN  build\mapcontainer\map_0027FA80_0027FAD0.bin
        INCBIN  build\mapcontainer\map_0027FAD0_0027FD9C.bin
        INCBIN  build\mapcontainer\map_0027FD9C_0027FDBC.bin
        INCBIN  build\mapcontainer\map_0027FDBC_0027FE74.bin
        INCBIN  build\mapcontainer\map_0027FE74_0027FE94.bin
        INCBIN  build\mapcontainer\map_0027FE94_002801FC.bin
        INCBIN  build\mapcontainer\map_002801FC_0028021C.bin
        INCBIN  build\mapcontainer\map_0028021C_00280378.bin
|unk_08280378|
        INCBIN  build\mapcontainer\map_00280378_002803D8.bin
        INCBIN  build\mapcontainer\map_002803D8_002805E4.bin
|unk_082805E4|
        INCBIN  build\mapcontainer\map_002805E4_00280664.bin
|unk_08280664|
        INCBIN  build\mapcontainer\map_00280664_00280668.bin
        INCBIN  build\mapcontainer\map_00280668_002806B8.bin
        INCBIN  build\mapcontainer\map_002806B8_00280800.bin
        INCBIN  build\mapcontainer\map_00280800_0028081C.bin
        INCBIN  build\mapcontainer\map_0028081C_00280874.bin
        INCBIN  build\mapcontainer\map_00280874_00280890.bin
        INCBIN  build\mapcontainer\map_00280890_002809E4.bin
        INCBIN  build\mapcontainer\map_002809E4_00280A00.bin
        INCBIN  build\mapcontainer\map_00280A00_00280AD8.bin
|unk_08280AD8|
        INCBIN  build\mapcontainer\map_00280AD8_00280B70.bin
|unk_08280B70|
        INCBIN  build\mapcontainer\map_00280B70_00280B78.bin
        INCBIN  build\mapcontainer\map_00280B78_00280BC8.bin
        INCBIN  build\mapcontainer\map_00280BC8_00281068.bin
        INCBIN  build\mapcontainer\map_00281068_00281090.bin
        INCBIN  build\mapcontainer\map_00281090_00281118.bin
        INCBIN  build\mapcontainer\map_00281118_00281138.bin
        INCBIN  build\mapcontainer\map_00281138_00281744.bin
        INCBIN  build\mapcontainer\map_00281744_0028176C.bin
        INCBIN  build\mapcontainer\map_0028176C_002818CC.bin
|unk_082818CC|
        INCBIN  build\mapcontainer\map_002818CC_00281964.bin
|unk_08281964|
        INCBIN  build\mapcontainer\map_00281964_0028196C.bin
        INCBIN  build\mapcontainer\map_0028196C_002819BC.bin
        INCBIN  build\mapcontainer\map_002819BC_00281B2C.bin
        INCBIN  build\mapcontainer\map_00281B2C_00281B48.bin
        INCBIN  build\mapcontainer\map_00281B48_00281B88.bin
        INCBIN  build\mapcontainer\map_00281B88_00281BA4.bin
        INCBIN  build\mapcontainer\map_00281BA4_00281D3C.bin
        INCBIN  build\mapcontainer\map_00281D3C_00281D58.bin
        INCBIN  build\mapcontainer\map_00281D58_00281E18.bin
|unk_08281E18|
        INCBIN  build\mapcontainer\map_00281E18_00281EB0.bin
|unk_08281EB0|
        INCBIN  build\mapcontainer\map_00281EB0_00281EB8.bin
        INCBIN  build\mapcontainer\map_00281EB8_00281F08.bin
        INCBIN  build\mapcontainer\map_00281F08_00282320.bin
        INCBIN  build\mapcontainer\map_00282320_00282348.bin
        INCBIN  build\mapcontainer\map_00282348_002823E0.bin
        INCBIN  build\mapcontainer\map_002823E0_00282400.bin
        INCBIN  build\mapcontainer\map_00282400_0028283C.bin
        INCBIN  build\mapcontainer\map_0028283C_00282864.bin
        INCBIN  build\mapcontainer\map_00282864_002829B4.bin
|unk_082829B4|
        INCBIN  build\mapcontainer\map_002829B4_002829CC.bin
        INCBIN  build\mapcontainer\map_002829CC_00282AB4.bin
|unk_08282AB4|
        INCBIN  build\mapcontainer\map_00282AB4_00282B4C.bin
|unk_08282B4C|
        INCBIN  build\mapcontainer\map_00282B4C_00282B54.bin
        INCBIN  build\mapcontainer\map_00282B54_00282BA4.bin
        INCBIN  build\mapcontainer\map_00282BA4_00282E50.bin
        INCBIN  build\mapcontainer\map_00282E50_00282E70.bin
        INCBIN  build\mapcontainer\map_00282E70_00282EC4.bin
        INCBIN  build\mapcontainer\map_00282EC4_00282EE0.bin
        INCBIN  build\mapcontainer\map_00282EE0_002832AC.bin
        INCBIN  build\mapcontainer\map_002832AC_002832CC.bin
        INCBIN  build\mapcontainer\map_002832CC_00283414.bin
|unk_08283414|
        INCBIN  build\mapcontainer\map_00283414_002834AC.bin
|unk_082834AC|
        INCBIN  build\mapcontainer\map_002834AC_002834B4.bin
        INCBIN  build\mapcontainer\map_002834B4_00283504.bin
        INCBIN  build\mapcontainer\map_00283504_00283830.bin
        INCBIN  build\mapcontainer\map_00283830_00283850.bin
        INCBIN  build\mapcontainer\map_00283850_00283928.bin
        INCBIN  build\mapcontainer\map_00283928_00283948.bin
        INCBIN  build\mapcontainer\map_00283948_00283D90.bin
        INCBIN  build\mapcontainer\map_00283D90_00283DB0.bin
        INCBIN  build\mapcontainer\map_00283DB0_00283F20.bin
|unk_08283F20|
        INCBIN  build\mapcontainer\map_00283F20_00283F50.bin
|unk_08283F50|
        INCBIN  build\mapcontainer\map_00283F50_00284000.bin
|unk_08284000|
        INCBIN  build\mapcontainer\map_00284000_0028400C.bin
        INCBIN  build\mapcontainer\map_0028400C_0028405C.bin
        INCBIN  build\mapcontainer\map_0028405C_002841B0.bin
        INCBIN  build\mapcontainer\map_002841B0_002841CC.bin
        INCBIN  build\mapcontainer\map_002841CC_0028421C.bin
        INCBIN  build\mapcontainer\map_0028421C_00284238.bin
        INCBIN  build\mapcontainer\map_00284238_00284404.bin
        INCBIN  build\mapcontainer\map_00284404_00284420.bin
        INCBIN  build\mapcontainer\map_00284420_002844E4.bin
|unk_082844E4|
        INCBIN  build\mapcontainer\map_002844E4_002844FC.bin
        INCBIN  build\mapcontainer\map_002844FC_002845D8.bin
|unk_082845D8|
        INCBIN  build\mapcontainer\map_002845D8_00284670.bin
|unk_08284670|
        INCBIN  build\mapcontainer\map_00284670_00284678.bin
        INCBIN  build\mapcontainer\map_00284678_002846C8.bin
        INCBIN  build\mapcontainer\map_002846C8_002847F4.bin
        INCBIN  build\mapcontainer\map_002847F4_00284810.bin
        INCBIN  build\mapcontainer\map_00284810_0028483C.bin
        INCBIN  build\mapcontainer\map_0028483C_00284858.bin
        INCBIN  build\mapcontainer\map_00284858_002849FC.bin
        INCBIN  build\mapcontainer\map_002849FC_00284A18.bin
        INCBIN  build\mapcontainer\map_00284A18_00284AE0.bin
|unk_08284AE0|
        INCBIN  build\mapcontainer\map_00284AE0_00284B78.bin
|unk_08284B78|
        INCBIN  build\mapcontainer\map_00284B78_00284B80.bin
        INCBIN  build\mapcontainer\map_00284B80_00284BD0.bin
        INCBIN  build\mapcontainer\map_00284BD0_00284F9C.bin
        INCBIN  build\mapcontainer\map_00284F9C_00284FC4.bin
        INCBIN  build\mapcontainer\map_00284FC4_002850FC.bin
        INCBIN  build\mapcontainer\map_002850FC_0028511C.bin
        INCBIN  build\mapcontainer\map_0028511C_0028529C.bin
        INCBIN  build\mapcontainer\map_0028529C_002852BC.bin
        INCBIN  build\mapcontainer\map_002852BC_00285A10.bin
        INCBIN  build\mapcontainer\map_00285A10_00285A38.bin
        INCBIN  build\mapcontainer\map_00285A38_00285C18.bin
|unk_08285C18|
        INCBIN  build\animframe\gen_285c18_285e20.bin
|unk_08285E20|
        INCBIN  build\mapcontainer\map_00285E20_00285F18.bin
|unk_08285F18|
        INCBIN  build\mapcontainer\map_00285F18_00285F28.bin
        INCBIN  build\mapcontainer\map_00285F28_00285F78.bin
        INCBIN  build\mapcontainer\map_00285F78_002862E4.bin
        INCBIN  build\mapcontainer\map_002862E4_0028630C.bin
        INCBIN  build\mapcontainer\map_0028630C_00286384.bin
        INCBIN  build\mapcontainer\map_00286384_002863A0.bin
        INCBIN  build\mapcontainer\map_002863A0_00286728.bin
        INCBIN  build\mapcontainer\map_00286728_00286750.bin
        INCBIN  build\mapcontainer\map_00286750_00286884.bin
|unk_08286884|
        INCBIN  build\mapcontainer\map_00286884_00286934.bin
|unk_08286934|
        INCBIN  build\mapcontainer\map_00286934_00286940.bin
        INCBIN  build\mapcontainer\map_00286940_00286990.bin
        INCBIN  build\mapcontainer\map_00286990_00286CFC.bin
        INCBIN  build\mapcontainer\map_00286CFC_00286D24.bin
        INCBIN  build\mapcontainer\map_00286D24_00286D84.bin
        INCBIN  build\mapcontainer\map_00286D84_00286DA4.bin
        INCBIN  build\mapcontainer\map_00286DA4_00286EF0.bin
        INCBIN  build\mapcontainer\map_00286EF0_00286F10.bin
        INCBIN  build\mapcontainer\map_00286F10_002873C8.bin
        INCBIN  build\mapcontainer\map_002873C8_002873F0.bin
        INCBIN  build\mapcontainer\map_002873F0_00287508.bin
|unk_08287508|
        INCBIN  build\mapcontainer\map_00287508_002875B8.bin
|unk_082875B8|
        INCBIN  build\mapcontainer\map_002875B8_002875C0.bin
        INCBIN  build\mapcontainer\map_002875C0_00287610.bin
        INCBIN  build\mapcontainer\map_00287610_00287AAC.bin
        INCBIN  build\mapcontainer\map_00287AAC_00287AD4.bin
        INCBIN  build\mapcontainer\map_00287AD4_00287BF4.bin
        INCBIN  build\mapcontainer\map_00287BF4_00287C1C.bin
        INCBIN  build\mapcontainer\map_00287C1C_002882FC.bin
        INCBIN  build\mapcontainer\map_002882FC_00288324.bin
        INCBIN  build\mapcontainer\map_00288324_00288CB8.bin
        INCBIN  build\mapcontainer\map_00288CB8_00288CE0.bin
        INCBIN  build\mapcontainer\map_00288CE0_00288F00.bin
        INCLUDE rawlabeled_288f00.s
        INCBIN  build\mapcontainer\map_00288F60_0028943C.bin
        INCLUDE rawlabeled_28943c.s
        INCBIN  build\mapcontainer\map_002898C0_00289910.bin
        INCBIN  build\mapcontainer\map_00289910_00289A00.bin
        INCBIN  build\mapcontainer\map_00289A00_00289A20.bin
        INCBIN  build\mapcontainer\map_00289A20_00289A44.bin
        INCBIN  build\mapcontainer\map_00289A44_00289A60.bin
        INCBIN  build\mapcontainer\map_00289A60_00289A84.bin
        INCBIN  build\mapcontainer\map_00289A84_00289AA0.bin
        INCBIN  build\mapcontainer\map_00289AA0_00289D30.bin
        INCBIN  build\mapcontainer\map_00289D30_00289D50.bin
        INCBIN  build\mapcontainer\map_00289D50_00289DE4.bin
|unk_08289DE4|
        INCBIN  build\mapcontainer\map_00289DE4_00289E44.bin
        INCBIN  build\mapcontainer\map_00289E44_0028A1C8.bin
|unk_0828A1C8|
        INCBIN  build\mapcontainer\map_0028A1C8_0028A1E0.bin
|unk_0828A1E0|
        INCBIN  build\mapcontainer\map_0028A1E0_0028A1E4.bin
        INCBIN  build\mapcontainer\map_0028A1E4_0028A234.bin
        INCBIN  build\mapcontainer\map_0028A234_0028A2A4.bin
        INCBIN  build\mapcontainer\map_0028A2A4_0028A2C0.bin
        INCBIN  build\mapcontainer\map_0028A2C0_0028A5B8.bin
        INCBIN  build\mapcontainer\map_0028A5B8_0028A5D4.bin
        INCBIN  build\mapcontainer\map_0028A5D4_0028A678.bin
|unk_0828A678|
        INCBIN  build\mapcontainer\map_0028A678_0028A690.bin
        INCBIN  build\mapcontainer\map_0028A690_0028A6F4.bin
|unk_0828A6F4|
        INCBIN  build\mapcontainer\map_0028A6F4_0028A70C.bin
|unk_0828A70C|
        INCBIN  build\mapcontainer\map_0028A70C_0028A710.bin
        INCBIN  build\mapcontainer\map_0028A710_0028A760.bin
        INCBIN  build\mapcontainer\map_0028A760_0028A82C.bin
        INCBIN  build\mapcontainer\map_0028A82C_0028A84C.bin
        INCBIN  build\mapcontainer\map_0028A84C_0028A870.bin
        INCBIN  build\mapcontainer\map_0028A870_0028A88C.bin
        INCBIN  build\mapcontainer\map_0028A88C_0028A900.bin
        INCBIN  build\mapcontainer\map_0028A900_0028A920.bin
        INCBIN  build\mapcontainer\map_0028A920_0028AB18.bin
        INCBIN  build\mapcontainer\map_0028AB18_0028AB38.bin
        INCBIN  build\mapcontainer\map_0028AB38_0028ABD4.bin
|unk_0828ABD4|
        INCBIN  build\mapcontainer\map_0028ABD4_0028AC04.bin
        INCBIN  build\mapcontainer\map_0028AC04_0028AE60.bin
|unk_0828AE60|
        INCBIN  build\mapcontainer\map_0028AE60_0028AEA8.bin
|unk_0828AEA8|
        INCBIN  build\mapcontainer\map_0028AEA8_0028AEB4.bin
        INCBIN  build\mapcontainer\map_0028AEB4_0028AF04.bin
        INCBIN  build\mapcontainer\map_0028AF04_0028B084.bin
        INCBIN  build\mapcontainer\map_0028B084_0028B0AC.bin
        INCBIN  build\mapcontainer\map_0028B0AC_0028B5B4.bin
        INCBIN  build\mapcontainer\map_0028B5B4_0028B5DC.bin
        INCBIN  build\mapcontainer\map_0028B5DC_0028B6E8.bin
        INCLUDE rawlabeled_28b6e8.s
        INCBIN  build\mapcontainer\map_0028B7C0_0028BB54.bin
        INCLUDE rawlabeled_28bb54.s
        INCBIN  build\mapcontainer\map_0028BBA8_0028BBF8.bin
        INCBIN  build\mapcontainer\map_0028BBF8_0028BC74.bin
        INCBIN  build\mapcontainer\map_0028BC74_0028BC90.bin
        INCBIN  build\mapcontainer\map_0028BC90_0028BF1C.bin
        INCBIN  build\mapcontainer\map_0028BF1C_0028BF38.bin
        INCBIN  build\mapcontainer\map_0028BF38_0028C000.bin
        INCLUDE rawlabeled_28c000.s
        INCBIN  build\mapcontainer\map_0028C0F0_0028C4B4.bin
        INCLUDE rawlabeled_28c4b4.s
        INCBIN  build\mapcontainer\map_0028C4D0_0028C520.bin
        INCBIN  build\mapcontainer\map_0028C520_0028CCC4.bin
        INCBIN  build\mapcontainer\map_0028CCC4_0028CD00.bin
        INCBIN  build\mapcontainer\map_0028CD00_0028D8CC.bin
        INCBIN  build\mapcontainer\map_0028D8CC_0028D908.bin
        INCBIN  build\mapcontainer\map_0028D908_0028E200.bin
        INCBIN  build\mapcontainer\map_0028E200_0028E258.bin
        INCBIN  build\mapcontainer\map_0028E258_0028EAD4.bin
        INCBIN  build\mapcontainer\map_0028EAD4_0028EB2C.bin
        INCBIN  build\mapcontainer\map_0028EB2C_0028EC28.bin
        INCLUDE rawlabeled_28ec28.s
        INCBIN  build\mapcontainer\map_0028ECF0_0028ED40.bin
        INCBIN  build\mapcontainer\map_0028ED40_0028F0D4.bin
        INCBIN  build\mapcontainer\map_0028F0D4_0028F0FC.bin
        INCBIN  build\mapcontainer\map_0028F0FC_0028F1C0.bin
        INCBIN  build\mapcontainer\map_0028F1C0_0028F1E8.bin
        INCBIN  build\mapcontainer\map_0028F1E8_0028F760.bin
        INCBIN  build\mapcontainer\map_0028F760_0028F788.bin
        INCBIN  build\mapcontainer\map_0028F788_0028F958.bin
        INCBIN  build\mapcontainer\map_0028F958_0028F980.bin
        INCBIN  build\mapcontainer\map_0028F980_0028FAAC.bin
        INCLUDE rawlabeled_28faac.s
        INCBIN  build\mapcontainer\map_0028FADC_0028FBE4.bin
        INCLUDE rawlabeled_28fbe4.s
        INCBIN  build\mapcontainer\map_0028FC00_0028FC50.bin
        INCBIN  build\mapcontainer\map_0028FC50_0028FE68.bin
        INCBIN  build\mapcontainer\map_0028FE68_0028FE88.bin
        INCBIN  build\mapcontainer\map_0028FE88_0028FF30.bin
        INCBIN  build\mapcontainer\map_0028FF30_0028FF50.bin
        INCBIN  build\mapcontainer\map_0028FF50_0029017C.bin
        INCBIN  build\mapcontainer\map_0029017C_0029019C.bin
        INCBIN  build\mapcontainer\map_0029019C_00290294.bin
        INCBIN  build\mapcontainer\map_00290294_002902B4.bin
        INCBIN  build\mapcontainer\map_002902B4_00290394.bin
        INCLUDE rawlabeled_290394.s
        INCBIN  build\mapcontainer\map_002903AC_00290560.bin
        INCLUDE rawlabeled_290560.s
        INCBIN  build\mapcontainer\map_00290598_002905E8.bin
        INCBIN  build\mapcontainer\map_002905E8_00290834.bin
        INCBIN  build\mapcontainer\map_00290834_0029085C.bin
        INCBIN  build\mapcontainer\map_0029085C_00290A5C.bin
        INCBIN  build\mapcontainer\map_00290A5C_00290A84.bin
        INCBIN  build\mapcontainer\map_00290A84_00290E24.bin
        INCBIN  build\mapcontainer\map_00290E24_00290E44.bin
        INCBIN  build\mapcontainer\map_00290E44_00291150.bin
        INCBIN  build\mapcontainer\map_00291150_00291178.bin
        INCBIN  build\mapcontainer\map_00291178_002912F4.bin
        INCLUDE rawlabeled_2912f4.s
        INCBIN  build\mapcontainer\map_0029139C_002913EC.bin
        INCBIN  build\mapcontainer\map_002913EC_00291750.bin
        INCBIN  build\mapcontainer\map_00291750_00291778.bin
        INCBIN  build\mapcontainer\map_00291778_002919F4.bin
        INCBIN  build\mapcontainer\map_002919F4_00291A14.bin
        INCBIN  build\mapcontainer\map_00291A14_00291B38.bin
        INCBIN  build\mapcontainer\map_00291B38_00291B60.bin
        INCBIN  build\mapcontainer\map_00291B60_00291C50.bin
        INCLUDE rawlabeled_291c50.s
        INCBIN  build\mapcontainer\map_00291CE0_00291D30.bin
        INCBIN  build\mapcontainer\map_00291D30_00291D68.bin
        INCBIN  build\mapcontainer\map_00291D68_00291D84.bin
        INCBIN  build\mapcontainer\map_00291D84_0029213C.bin
        INCBIN  build\mapcontainer\map_0029213C_00292164.bin
        INCBIN  build\mapcontainer\map_00292164_0029255C.bin
        INCBIN  build\mapcontainer\map_0029255C_00292584.bin
        INCBIN  build\mapcontainer\map_00292584_00292680.bin
        INCBIN  build\mapcontainer\map_00292680_002926A8.bin
        INCBIN  build\mapcontainer\map_002926A8_002927A4.bin
        INCLUDE rawlabeled_2927a4.s
        INCBIN  build\mapcontainer\map_00292834_00292884.bin
        INCBIN  build\mapcontainer\map_00292884_002928C0.bin
        INCBIN  build\mapcontainer\map_002928C0_002928DC.bin
        INCBIN  build\mapcontainer\map_002928DC_00292C88.bin
        INCBIN  build\mapcontainer\map_00292C88_00292CB0.bin
        INCBIN  build\mapcontainer\map_00292CB0_00293000.bin
        INCBIN  build\mapcontainer\map_00293000_00293028.bin
        INCBIN  build\mapcontainer\map_00293028_002932D0.bin
        INCBIN  build\mapcontainer\map_002932D0_002932F8.bin
        INCBIN  build\mapcontainer\map_002932F8_002933E4.bin
        INCLUDE rawlabeled_2933e4.s
        INCBIN  build\mapcontainer\map_00293474_002934C4.bin
        INCBIN  build\mapcontainer\map_002934C4_00293BEC.bin
        INCBIN  build\mapcontainer\map_00293BEC_00293C1C.bin
        INCBIN  build\mapcontainer\map_00293C1C_002941CC.bin
        INCBIN  build\mapcontainer\map_002941CC_002941FC.bin
        INCBIN  build\mapcontainer\map_002941FC_00294628.bin
        INCBIN  build\mapcontainer\map_00294628_00294660.bin
        INCBIN  build\mapcontainer\map_00294660_0029478C.bin
        INCLUDE rawlabeled_29478c.s
        INCBIN  build\mapcontainer\map_002947EC_002948D8.bin
        INCLUDE rawlabeled_2948d8.s
        INCBIN  build\mapcontainer\map_00294968_002949B8.bin
        INCBIN  build\mapcontainer\map_002949B8_00294CC8.bin
        INCBIN  build\mapcontainer\map_00294CC8_00294CF8.bin
        INCBIN  build\mapcontainer\map_00294CF8_00295140.bin
        INCBIN  build\mapcontainer\map_00295140_00295170.bin
        INCBIN  build\mapcontainer\map_00295170_00295A74.bin
        INCBIN  build\mapcontainer\map_00295A74_00295AA4.bin
        INCBIN  build\mapcontainer\map_00295AA4_00295BCC.bin
        INCLUDE rawlabeled_295bcc.s
        INCBIN  build\mapcontainer\map_00295C58_00295CA8.bin
        INCBIN  build\mapcontainer\map_00295CA8_00295D10.bin
        INCBIN  build\mapcontainer\map_00295D10_00295D38.bin
        INCBIN  build\mapcontainer\map_00295D38_00295ED4.bin
        INCBIN  build\mapcontainer\map_00295ED4_00295F04.bin
        INCBIN  build\mapcontainer\map_00295F04_00296270.bin
        INCBIN  build\mapcontainer\map_00296270_002962A0.bin
        INCBIN  build\mapcontainer\map_002962A0_00296C70.bin
        INCBIN  build\mapcontainer\map_00296C70_00296CA8.bin
        INCBIN  build\mapcontainer\map_00296CA8_00296D4C.bin
        INCLUDE rawlabeled_296d4c.s
        INCBIN  build\mapcontainer\map_00296D9C_00296DEC.bin
        INCBIN  build\mapcontainer\map_00296DEC_00296E5C.bin
        INCBIN  build\mapcontainer\map_00296E5C_00296E84.bin
        INCBIN  build\mapcontainer\map_00296E84_00296FC0.bin
        INCBIN  build\mapcontainer\map_00296FC0_00296FE8.bin
        INCBIN  build\mapcontainer\map_00296FE8_0029768C.bin
        INCBIN  build\mapcontainer\map_0029768C_002976B4.bin
        INCBIN  build\mapcontainer\map_002976B4_00297BB4.bin
        INCBIN  build\mapcontainer\map_00297BB4_00297BDC.bin
        INCBIN  build\mapcontainer\map_00297BDC_00297C68.bin
|unk_08297C68|
        INCBIN  build\mapcontainer\map_00297C68_00297C80.bin
|unk_08297C80|
        INCBIN  build\mapcontainer\map_00297C80_00297C84.bin
        INCBIN  build\mapcontainer\map_00297C84_00297CD4.bin
        INCBIN  build\mapcontainer\map_00297CD4_00297E34.bin
        INCBIN  build\mapcontainer\map_00297E34_00297E5C.bin
        INCBIN  build\mapcontainer\map_00297E5C_00298064.bin
        INCBIN  build\mapcontainer\map_00298064_0029808C.bin
        INCBIN  build\mapcontainer\map_0029808C_002980F8.bin
|unk_082980F8|
        INCBIN  build\mapcontainer\map_002980F8_00298140.bin
        INCBIN  build\mapcontainer\map_00298140_00298324.bin
|unk_08298324|
        INCBIN  build\mapcontainer\map_00298324_00298354.bin
|unk_08298354|
        INCBIN  build\mapcontainer\map_00298354_0029835C.bin
        INCBIN  build\mapcontainer\map_0029835C_002983AC.bin
        INCBIN  build\mapcontainer\map_002983AC_002986A0.bin
        INCBIN  build\mapcontainer\map_002986A0_002986C0.bin
        INCBIN  build\mapcontainer\map_002986C0_002987E0.bin
        INCBIN  build\mapcontainer\map_002987E0_00298810.bin
        INCBIN  build\mapcontainer\map_00298810_00298CB8.bin
        INCBIN  build\mapcontainer\map_00298CB8_00298CE8.bin
        INCBIN  build\mapcontainer\map_00298CE8_0029959C.bin
        INCBIN  build\mapcontainer\map_0029959C_002995D4.bin
        INCBIN  build\mapcontainer\map_002995D4_00299698.bin
|unk_08299698|
        INCBIN  build\mapcontainer\map_00299698_002996C8.bin
|unk_082996C8|
        INCBIN  build\mapcontainer\map_002996C8_002996D0.bin
        INCBIN  build\mapcontainer\map_002996D0_00299720.bin
        INCBIN  build\mapcontainer\map_00299720_0029A20C.bin
        INCBIN  build\mapcontainer\map_0029A20C_0029A244.bin
        INCBIN  build\mapcontainer\map_0029A244_0029A77C.bin
        INCBIN  build\mapcontainer\map_0029A77C_0029A7A8.bin
        INCBIN  build\mapcontainer\map_0029A7A8_0029B1F4.bin
        INCBIN  build\mapcontainer\map_0029B1F4_0029B22C.bin
        INCBIN  build\mapcontainer\map_0029B22C_0029B308.bin
|unk_0829B308|
        INCBIN  baserom.gba_0x29b308_0x29b320.extracted
        INCBIN  build\mapcontainer\map_0029B320_0029B340.bin
        INCBIN  build\mapcontainer\map_0029B340_0029B380.bin
        INCBIN  build\mapcontainer\map_0029B380_0029B478.bin
|unk_0829B478|
        INCBIN  build\mapcontainer\map_0029B478_0029B490.bin
|unk_0829B490|
        INCBIN  build\mapcontainer\map_0029B490_0029B494.bin
        INCBIN  build\mapcontainer\map_0029B494_0029B4E4.bin
        INCBIN  build\mapcontainer\map_0029B4E4_0029B65C.bin
        INCBIN  build\mapcontainer\map_0029B65C_0029B678.bin
        INCBIN  build\mapcontainer\map_0029B678_0029B7C8.bin
        INCBIN  build\mapcontainer\map_0029B7C8_0029B7E4.bin
        INCBIN  build\mapcontainer\map_0029B7E4_0029B904.bin
        INCBIN  build\mapcontainer\map_0029B904_0029B920.bin
        INCBIN  build\mapcontainer\map_0029B920_0029B938.bin
        INCBIN  build\mapcontainer\map_0029B938_0029B988.bin
        INCBIN  build\mapcontainer\map_0029B988_0029BE50.bin
        INCBIN  build\mapcontainer\map_0029BE50_0029BE6C.bin
        INCBIN  build\mapcontainer\map_0029BE6C_0029BE88.bin
        INCBIN  build\mapcontainer\map_0029BE88_0029BED8.bin
        INCBIN  build\mapcontainer\map_0029BED8_0029BEF4.bin
        INCBIN  build\mapcontainer\map_0029BEF4_0029BF44.bin
        INCBIN  build\mapcontainer\map_0029BF44_0029C0A8.bin
        INCBIN  build\mapcontainer\map_0029C0A8_0029C0C4.bin
        INCBIN  build\mapcontainer\map_0029C0C4_0029C204.bin
        INCBIN  build\mapcontainer\map_0029C204_0029C220.bin
        INCBIN  build\mapcontainer\map_0029C220_0029C258.bin
        INCBIN  build\mapcontainer\map_0029C258_0029C274.bin
        INCBIN  build\mapcontainer\map_0029C274_0029C2D8.bin
        INCBIN  build\mapcontainer\map_0029C2D8_0029C328.bin
        INCBIN  build\mapcontainer\map_0029C328_0029C7E0.bin
        INCBIN  build\mapcontainer\map_0029C7E0_0029C808.bin
        INCBIN  build\mapcontainer\map_0029C808_0029C9D4.bin
        INCBIN  build\mapcontainer\map_0029C9D4_0029C9FC.bin
        INCBIN  build\mapcontainer\map_0029C9FC_0029CF48.bin
        INCBIN  build\mapcontainer\map_0029CF48_0029CF70.bin
        INCBIN  build\mapcontainer\map_0029CF70_0029D074.bin
|unk_0829D074|
        INCBIN  build\mapcontainer\map_0029D074_0029D194.bin
        INCBIN  build\mapcontainer\map_0029D194_0029D26C.bin
        INCBIN  build\mapcontainer\map_0029D26C_0029D2BC.bin
        INCBIN  build\mapcontainer\map_0029D2BC_0029D32C.bin
        INCBIN  build\mapcontainer\map_0029D32C_0029D34C.bin
        INCBIN  build\mapcontainer\map_0029D34C_0029D974.bin
        INCBIN  build\mapcontainer\map_0029D974_0029D99C.bin
        INCBIN  build\mapcontainer\map_0029D99C_0029DA60.bin
        INCBIN  build\mapcontainer\map_0029DA60_0029DA80.bin
        INCBIN  build\mapcontainer\map_0029DA80_0029DCCC.bin
        INCBIN  build\mapcontainer\map_0029DCCC_0029DCEC.bin
        INCBIN  build\mapcontainer\map_0029DCEC_0029DD8C.bin
|unk_0829DD8C|
        INCBIN  build\mapcontainer\map_0029DD8C_0029DE64.bin
        INCBIN  build\mapcontainer\map_0029DE64_0029E274.bin
|unk_0829E274|
        INCBIN  build\mapcontainer\map_0029E274_0029E28C.bin
        INCBIN  build\mapcontainer\map_0029E28C_0029E2DC.bin
        INCBIN  build\mapcontainer\map_0029E2DC_0029E484.bin
        INCBIN  build\mapcontainer\map_0029E484_0029E4A4.bin
        INCBIN  build\mapcontainer\map_0029E4A4_0029E98C.bin
        INCBIN  build\mapcontainer\map_0029E98C_0029E9AC.bin
        INCBIN  build\mapcontainer\map_0029E9AC_0029EA98.bin
        INCBIN  build\mapcontainer\map_0029EA98_0029EAB8.bin
        INCBIN  build\mapcontainer\map_0029EAB8_0029EC20.bin
        INCBIN  build\mapcontainer\map_0029EC20_0029EC40.bin
        INCBIN  build\mapcontainer\map_0029EC40_0029ECA4.bin
|unk_0829ECA4|
        INCBIN  build\mapcontainer\map_0029ECA4_0029ED4C.bin
        INCBIN  build\mapcontainer\map_0029ED4C_0029EFB0.bin
        INCBIN  build\mapcontainer\map_0029EFB0_0029F000.bin
        INCBIN  build\mapcontainer\map_0029F000_0029F04C.bin
        INCBIN  build\mapcontainer\map_0029F04C_0029F068.bin
        INCBIN  build\mapcontainer\map_0029F068_0029F0A0.bin
        INCBIN  build\mapcontainer\map_0029F0A0_0029F0BC.bin
        INCBIN  build\mapcontainer\map_0029F0BC_0029F3C4.bin
        INCBIN  build\mapcontainer\map_0029F3C4_0029F3E0.bin
        INCBIN  build\mapcontainer\map_0029F3E0_0029F4B4.bin
        INCBIN  build\mapcontainer\map_0029F4B4_0029F4D4.bin
        INCBIN  build\mapcontainer\map_0029F4D4_0029F4EC.bin
        INCBIN  build\mapcontainer\map_0029F4EC_0029F53C.bin
        INCBIN  build\mapcontainer\map_0029F53C_0029F6E4.bin
        INCBIN  build\mapcontainer\map_0029F6E4_0029F700.bin
        INCBIN  build\mapcontainer\map_0029F700_0029F808.bin
        INCBIN  build\mapcontainer\map_0029F808_0029F814.bin
        INCBIN  build\mapcontainer\map_0029F814_002ABF00.bin
        INCBIN  build\mapcontainer\map_002ABF00_002AC138.bin
        INCBIN  build\mapcontainer\map_002AC138_002AC150.bin
|unk_082AC150|
        INCBIN  build\mapcontainer\map_002AC150_002ACA20.bin
        INCBIN  build\mapcontainer\map_002ACA20_002AD8BC.bin
        INCBIN  build\mapcontainer\map_002AD8BC_002AD90C.bin
        INCBIN  build\mapcontainer\map_002AD90C_002ADB60.bin
        INCBIN  build\mapcontainer\map_002ADB60_002ADB80.bin
        INCBIN  build\mapcontainer\map_002ADB80_002AE010.bin
        INCBIN  build\mapcontainer\map_002AE010_002AE030.bin
        INCBIN  build\mapcontainer\map_002AE030_002AE058.bin
        INCLUDE rawlabeled_2ae058.s
        INCBIN  build\mapcontainer\map_002AE088_002AE2D0.bin
        INCBIN  build\mapcontainer\map_002AE2D0_002AE320.bin
        INCBIN  build\mapcontainer\map_002AE320_002AE4BC.bin
        INCBIN  build\mapcontainer\map_002AE4BC_002AE4DC.bin
        INCBIN  build\mapcontainer\map_002AE4DC_002AE5B0.bin
        INCBIN  build\mapcontainer\map_002AE5B0_002AE5D0.bin
        INCBIN  build\mapcontainer\map_002AE5D0_002AE910.bin
        INCBIN  build\mapcontainer\map_002AE910_002AE938.bin
        INCBIN  build\mapcontainer\map_002AE938_002AED6C.bin
        INCBIN  build\mapcontainer\map_002AED6C_002AED88.bin
        INCBIN  build\mapcontainer\map_002AED88_002AEE10.bin
        INCBIN  build\mapcontainer\map_002AEE10_002AEE60.bin
        INCBIN  build\mapcontainer\map_002AEE60_002AEF40.bin
        INCBIN  build\mapcontainer\map_002AEF40_002AEF5C.bin
        INCBIN  build\mapcontainer\map_002AEF5C_002AEFBC.bin
        INCBIN  build\mapcontainer\map_002AEFBC_002AEFD8.bin
        INCBIN  build\mapcontainer\map_002AEFD8_002AF1C4.bin
        INCBIN  build\mapcontainer\map_002AF1C4_002AF1E0.bin
        INCBIN  build\mapcontainer\map_002AF1E0_002AF22C.bin
        INCBIN  build\mapcontainer\map_002AF22C_002AF27C.bin
        INCBIN  build\mapcontainer\map_002AF27C_002AF2F0.bin
        INCBIN  build\mapcontainer\map_002AF2F0_002AF30C.bin
        INCBIN  build\mapcontainer\map_002AF30C_002AF7B0.bin
        INCBIN  build\mapcontainer\map_002AF7B0_002AF7CC.bin
        INCBIN  build\mapcontainer\map_002AF7CC_002AF9D0.bin
        INCBIN  build\mapcontainer\map_002AF9D0_002AF9F0.bin
        INCBIN  build\mapcontainer\map_002AF9F0_002AFC7C.bin
        INCBIN  build\mapcontainer\map_002AFC7C_002AFC9C.bin
        INCBIN  build\mapcontainer\map_002AFC9C_002AFCE4.bin
|unk_082AFCE4|
        INCBIN  build\mapcontainer\map_002AFCE4_002AFCFC.bin
        INCBIN  build\mapcontainer\map_002AFCFC_002AFF74.bin
        INCBIN  build\mapcontainer\map_002AFF74_002AFFC4.bin
        INCBIN  build\mapcontainer\map_002AFFC4_002B0110.bin
        INCBIN  build\mapcontainer\map_002B0110_002B0130.bin
        INCBIN  build\mapcontainer\map_002B0130_002B0274.bin
        INCBIN  build\mapcontainer\map_002B0274_002B0290.bin
        INCBIN  build\mapcontainer\map_002B0290_002B053C.bin
        INCBIN  build\mapcontainer\map_002B053C_002B0558.bin
        INCBIN  build\mapcontainer\map_002B0558_002B061C.bin
        INCBIN  build\mapcontainer\map_002B061C_002B063C.bin
        INCBIN  build\mapcontainer\map_002B063C_002B0674.bin
        INCBIN  build\mapcontainer\map_002B0674_002B06C4.bin
        INCBIN  build\mapcontainer\map_002B06C4_002B08EC.bin
        INCBIN  build\mapcontainer\map_002B08EC_002B090C.bin
        INCBIN  build\mapcontainer\map_002B090C_002B0958.bin
        INCBIN  build\mapcontainer\map_002B0958_002B0978.bin
        INCBIN  build\mapcontainer\map_002B0978_002B0CA0.bin
        INCBIN  build\mapcontainer\map_002B0CA0_002B0CC0.bin
        INCBIN  build\mapcontainer\map_002B0CC0_002B0D94.bin
        INCBIN  build\mapcontainer\map_002B0D94_002B0DB4.bin
        INCBIN  build\mapcontainer\map_002B0DB4_002B0DF4.bin
        INCBIN  build\mapcontainer\map_002B0DF4_002B0E44.bin
        INCBIN  build\mapcontainer\map_002B0E44_002B13E8.bin
        INCBIN  build\mapcontainer\map_002B13E8_002B1418.bin
        INCBIN  build\mapcontainer\map_002B1418_002B1750.bin
        INCBIN  build\mapcontainer\map_002B1750_002B1780.bin
        INCBIN  build\mapcontainer\map_002B1780_002B1DF0.bin
        INCBIN  build\mapcontainer\map_002B1DF0_002B1E20.bin
        INCBIN  build\mapcontainer\map_002B1E20_002B1F04.bin
|unk_082B1F04|
        INCBIN  build\mapcontainer\map_002B1F04_002B1F34.bin
        INCBIN  build\mapcontainer\map_002B1F34_002B1FAC.bin
        INCBIN  build\mapcontainer\map_002B1FAC_002B1FFC.bin
        INCBIN  build\mapcontainer\map_002B1FFC_002B20C4.bin
        INCBIN  build\mapcontainer\map_002B20C4_002B20EC.bin
        INCBIN  build\mapcontainer\map_002B20EC_002B2844.bin
        INCBIN  build\mapcontainer\map_002B2844_002B286C.bin
        INCBIN  build\mapcontainer\map_002B286C_002B28FC.bin
|unk_082B28FC|
        INCBIN  build\mapcontainer\map_002B28FC_002B2914.bin
        INCBIN  build\mapcontainer\map_002B2914_002B2998.bin
|unk_082B2998|
        INCBIN  build\animframe\gen_2b2998_2b2a10.bin
|unk_082B2A10|
        INCBIN  build\mapcontainer\map_002B2A10_002B2A40.bin
        INCBIN  build\mapcontainer\map_002B2A40_002B2A90.bin
        INCBIN  build\mapcontainer\map_002B2A90_002B2BDC.bin
        INCBIN  build\mapcontainer\map_002B2BDC_002B2BF8.bin
        INCBIN  build\mapcontainer\map_002B2BF8_002B2C68.bin
        INCBIN  build\mapcontainer\map_002B2C68_002B2C84.bin
        INCBIN  build\mapcontainer\map_002B2C84_002B2D90.bin
        INCBIN  build\mapcontainer\map_002B2D90_002B2DAC.bin
        INCBIN  build\mapcontainer\map_002B2DAC_002B31A8.bin
        INCBIN  build\mapcontainer\map_002B31A8_002B31C4.bin
        INCBIN  build\mapcontainer\map_002B31C4_002B31E8.bin
|unk_082B31E8|
        INCBIN  build\animframe\gen_2b31e8_2b3484.bin
|map_anim_row_082B3484|
|unk_082B3484|
	DCB 0x06,0x04
	DCW 0x037c
	DCD 0x082b31e8,0x082b3254,0x082b32c0,0x082b332c,0x082b339c,0x082b3410
|unk_082B34A0|
        INCBIN  build\animframe\gen_2b34a0_2b3600.bin
|map_anim_row_082B3600|
|unk_082B3600|
	DCB 0x06,0x02
	DCW 0x037a
	DCD 0x082b34a0,0x082b34dc,0x082b3518,0x082b3550,0x082b358c,0x082b35c8
|unk_082B361C|
        INCBIN  build\animframe\gen_2b361c_2b380c.bin
|map_anim_row_082B380C|
|unk_082B380C|
	DCB 0x04,0x04
	DCW 0x0376
	DCD 0x082b361c,0x082b3698,0x082b3714,0x082b3790
|unk_082B3820|
        INCBIN  build\animframe\gen_2b3820_2b3cc4.bin
|map_anim_row_082B3CC4|
|unk_082B3CC4|
	DCB 0x04,0x10
	DCW 0x0366
	DCD 0x082b3820,0x082b3940,0x082b3a70,0x082b3b90
|unk_082B3CD8|
        INCBIN  build\animframe\gen_2b3cd8_2b3e44.bin
|map_anim_row_082B3E44|
|unk_082B3E44|
	DCB 0x04,0x07
	DCW 0x035f
	DCD 0x082b3cd8,0x082b3d4c,0x082b3dc0,0x082b3d4c
|unk_082B3E58|
        INCBIN  baserom.gba_0x2b3e58_0x2b3e6c.extracted
        INCBIN  build\mapcontainer\map_002B3E6C_002B3EBC.bin
        INCBIN  build\mapcontainer\map_002B3EBC_002B4348.bin
        INCBIN  build\mapcontainer\map_002B4348_002B4364.bin
        INCBIN  build\mapcontainer\map_002B4364_002B43C4.bin
        INCBIN  build\mapcontainer\map_002B43C4_002B4414.bin
        INCBIN  build\mapcontainer\map_002B4414_002B44C8.bin
        INCBIN  build\mapcontainer\map_002B44C8_002B44E8.bin
        INCBIN  build\mapcontainer\map_002B44E8_002B4598.bin
        INCBIN  build\mapcontainer\map_002B4598_002B45B8.bin
        INCBIN  build\mapcontainer\map_002B45B8_002B4670.bin
        INCBIN  build\mapcontainer\map_002B4670_002B4690.bin
        INCBIN  build\mapcontainer\map_002B4690_002B493C.bin
        INCBIN  build\mapcontainer\map_002B493C_002B495C.bin
        INCBIN  build\mapcontainer\map_002B495C_002B4994.bin
|unk_082B4994|
        INCBIN  build\mapcontainer\map_002B4994_002B49AC.bin
        INCBIN  build\mapcontainer\map_002B49AC_002B4A38.bin
        INCBIN  build\mapcontainer\map_002B4A38_002B4A88.bin
        INCBIN  build\mapcontainer\map_002B4A88_002B4B10.bin
        INCBIN  build\mapcontainer\map_002B4B10_002B4B2C.bin
        INCBIN  build\mapcontainer\map_002B4B2C_002B4BC8.bin
        INCBIN  build\mapcontainer\map_002B4BC8_002B4BE4.bin
        INCBIN  build\mapcontainer\map_002B4BE4_002B4C48.bin
        INCBIN  build\mapcontainer\map_002B4C48_002B4C64.bin
        INCBIN  build\mapcontainer\map_002B4C64_002B4E50.bin
        INCBIN  build\mapcontainer\map_002B4E50_002B4E70.bin
        INCBIN  build\mapcontainer\map_002B4E70_002B4EB0.bin
        INCBIN  build\mapcontainer\map_002B4EB0_002B4F00.bin
        INCBIN  build\mapcontainer\map_002B4F00_002B53BC.bin
        INCBIN  build\mapcontainer\map_002B53BC_002B53D8.bin
        INCBIN  build\mapcontainer\map_002B53D8_002B53F4.bin
        INCBIN  build\mapcontainer\map_002B53F4_002B5444.bin
        INCBIN  build\mapcontainer\map_002B5444_002B568C.bin
        INCBIN  build\mapcontainer\map_002B568C_002B56A8.bin
        INCBIN  build\mapcontainer\map_002B56A8_002B56E4.bin
        INCBIN  build\mapcontainer\map_002B56E4_002B5734.bin
        INCBIN  build\mapcontainer\map_002B5734_002B5AC4.bin
        INCBIN  build\mapcontainer\map_002B5AC4_002B5AE0.bin
        INCBIN  build\mapcontainer\map_002B5AE0_002B5B2C.bin
        INCBIN  build\mapcontainer\map_002B5B2C_002B5B7C.bin
        INCBIN  build\mapcontainer\map_002B5B7C_002B5E5C.bin
        INCBIN  build\mapcontainer\map_002B5E5C_002B5E78.bin
        INCBIN  build\mapcontainer\map_002B5E78_002B5E94.bin
        INCBIN  build\mapcontainer\map_002B5E94_002B5EE4.bin
        INCBIN  build\mapcontainer\map_002B5EE4_002B5F00.bin
        INCBIN  build\mapcontainer\map_002B5F00_002B5F1C.bin
|unk_082B5F1C|
        INCBIN  baserom.gba_0x2b5f1c_0x2b5f28.extracted
        INCBIN  build\mapcontainer\map_002B5F28_002B5F78.bin
        INCBIN  build\mapcontainer\map_002B5F78_002B5F94.bin
        INCLUDE rawlabeled_2b5f94.s
        INCBIN  build\mapcontainer\map_002B5FA0_002B5FF0.bin
        INCBIN  build\mapcontainer\map_002B5FF0_002B608C.bin
|unk_082B608C|
        INCBIN  build\mapcontainer\map_002B608C_002B60A8.bin
        INCLUDE rawlabeled_2b60a8.s
|unk_082B7E78|
        INCBIN  build\mapcontainer\map_002B7E78_002B7EC8.bin
        INCBIN  build\mapcontainer\map_002B7EC8_002B84D0.bin
        INCBIN  build\mapcontainer\map_002B84D0_002B84F4.bin
        INCBIN  build\mapcontainer\map_002B84F4_002B87C4.bin
        INCBIN  build\mapcontainer\map_002B87C4_002B87E4.bin
        INCBIN  build\mapcontainer\map_002B87E4_002B891C.bin
        INCBIN  build\mapcontainer\map_002B891C_002B8940.bin
        INCBIN  build\mapcontainer\map_002B8940_002B8BC8.bin
        INCLUDE rawlabeled_2b8bc8.s
        INCBIN  build\jcalg1\gen_2b8bf4.bin
        INCLUDE rawlabeled_2b8c38.s
        INCBIN  build\assetdir\assetdir_002B9BB0_003192A5.bin
|unk_083192A5|
        INCBIN  baserom.gba_0x3192a5_0x3192a8.extracted
        INCBIN  build\assetdir\assetdir_003192A8_003195A8.bin
        INCBIN  build\assetdir\assetdir_003195A8_0036D18A.bin
|unk_0836D18A|
        INCBIN  baserom.gba_0x36d18a_0x36d18c.extracted
        INCBIN  build\assetdir\assetdir_0036D18C_0036D540.bin
        INCLUDE assetdir3_36d540.s
|sub_083715c0|
        LSL      r1,r4,#0
        LDRB     r1,[r0]
        LSL      r3,r3,#8
        MOV      r3,#0x42
        ASR      r3,r2,#0x10
        MOV      r6,#0x15
        MOV      r7,#0x18
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r2,#4
        ADD      r2,#3
        MOV      r3,#0x35
        MOV      r6,#0x11
        MOV      r7,#0x16
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSR      r3,r4,#0x18
        MOV      r1,#0x24
        ASR      r6,r4,#0x10
        LSR      r7,r4,#0xc
        LSL      r0,r3,#0
        STM      r1!,{r6}
        ASR      r6,r7,#0x18
        LSL      r0,r0,#5
        STM      r2!,{r1,r2}
        ASR      r4,r7,#4
        ADD      r0,r0,r1
        STM      r3!,{r2}
        ASR      r2,r6,#8
        ADD      r6,r2,r0
        ADD      r4,pc,#0x10
        LSR      r2,r6,#0x1c
        STM      r5!,{r6}
        ASR      r6,r7,#0x1c
        ADD      r4,r5,r0
        STM      r7!,{r1,r3,r5,r6,r7}
        ASR      r2,r6,#8
        ADD      r1,r4,r0
        LDRH     r6,[r4]
        LDMIA    r0!,{r3,r4}
        MOV      r2,#0
        MOV      r3,#0x3c
        MOV      r7,#0x1e
        LSL      r2,r3,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x38
        MOV      r7,#0x26
        ADD      r0,sp,#0x48
        LSR      r2,r6,#0x1c
        LSL      r5,r1,#0
        ADD      r2,#0x22
        CMP      r7,#0x23
        MOV      r1,#0x24
        LSR      r7,r4,#0xc
        LSL      r0,r0,#4
        SUB      r4,#0x4b
        LSL      r3,r2,#4
        MOV      r2,#6
        MOV      r3,#0x26
        STR      r4,[sp,#0xdc]
        CMP      r0,r8
        ADD      r2,#0xc6
        SUB      r3,r2,#0
        AND      r0,r3
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x1a
        MOV      r6,#0x29
        MOV      r7,#0x26
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0xd
        MOV      r6,#0x27
        MOV      r7,#0x24
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSL      r2,r4,#4
        MOV      r4,#0x23
        MOV      r1,#0x24
        MOV      r2,#0x26
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        MOV      r3,#0x35
        STR      r4,[sp,#0x84]
        CMP      r0,r8
        MOV      r1,#0x26
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r6,#0x1e
        MOV      r7,#0x1f
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1a
        MOV      r6,#0x1c
        MOV      r7,#0x1d
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        ADD      r3,r4,r4
        MOV      r1,#0x24
        SUB      r6,r4,r4
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        LSL      r2,r2
        ASR      r3,r4,#0x18
        LSL      r4,r2
        MOV      r6,#0x45
        STR      r7,[sp,#0x68]
        LSL      r1,r4,#0
        LDRB     r1,[r0]
        LSL      r3,r3,#8
        ADD      r0,#0x22
        ASR      r3,r4,#0xc
        LDRB     r4,[r0]
        LSL      r3,r3,#8
        LDRB     r5,[r0]
        LSL      r3,r3,#8
        ADD      r6,r4,r0
        SUB      r7,r4,r0
        LSL      r0,r5,#0x1c
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,#4
        ASR      r3,r4,#4
        ASR      r6,r4,#0x18
        ASR      r7,r4,#8
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0xe
        MOV      r6,#0x21
        MOV      r7,#0x14
        LSR      r3,r1,#0x20
        SUB      r0,r7,r5
        LSL      r2,r0,#0
        LDR      r3,[pc,#4]
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        ADD      r5,#0x92
        ASR      r3,r2,#0x1a
        LSL      r4,r2
        MOV      r6,#0x45
        STR      r7,[sp,#0x48]
        LSL      r1,r4,#0
        CMP      r0,#0x22
        SUB      r3,r4,#0
        LSR      r6,r4,#0x1c
        SUB      r7,r4,r0
        LSL      r0,r5,#0x1c
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,r0
        MOV      r6,#0x23
        LSR      r6,r4,#0x18
        ASR      r7,r4,#8
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0x2f
        MOV      r6,#0x21
        MOV      r7,#0xb
        LSL      r3,r1,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        STR      r2,[sp,#0x18]
        MOV      r3,#0x40
        STR      r4,[sp,#0xdc]
        CMP      r0,r8
        ASR      r6,r2,#0xa
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x30
        MOV      r6,#0x29
        MOV      r7,#0x18
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1f
        MOV      r6,#0x27
        MOV      r7,#0x1e
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        MOV      r4,#0x23
        MOV      r1,#0x24
        MOV      r6,#0x26
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        ADD      r5,#0x92
        MOV      r1,#0x23
        LSL      r4,r2
        MOV      r6,#0x45
        STR      r7,[sp,#0xb0]
        LSL      r1,r4,#0
        CMP      r0,#0x22
        SUB      r3,r4,#0
        MOV      r1,#0x26
        SUB      r7,r4,r0
        LSL      r0,r5,#0x1c
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,r0
        ADD      r3,r4,#0
        SUB      r6,r4,#4
        ASR      r7,r4,#8
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0x19
        MOV      r6,#0x21
        MOV      r7,#0x1d
        LSL      r3,r1,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        STR      r2,[sp,#0x18]
        MOV      r3,#0x40
        STR      r4,[sp,#0x58]
        CMP      r0,r8
        SUB      r6,r4,r0
        MOV      r1,#0x97
        LSL      r0,r0,#4
        SUB      r0,r7,r5
        MOV      r2,#2
        MOV      r3,#0x30
        LSL      r3,r2,#0x10
        LSL      r0,r6,#0x17
        MOV      r6,#0xf0
        MOV      r7,#0x18
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1f
        MOV      r6,#0x11
        MOV      r7,#0x16
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        LSR      r3,r4,#0x18
        MOV      r1,#0x24
        ASR      r6,r4,#0x10
        LSR      r7,r4,#0xc
|unk_083717C0|
        INCBIN	baserom.gba_0x3717c0_0x3717c2.extracted
        LSL      r0,r0,#4
        SUB      r6,#0x4b
        LSL      r6,r2,#4
        STR      r2,[sp,#0x18]
        STRB     r5,[r6,#0xc]
        ASR      r3,r6,#0x18
        ADD      r3,#0x74
        ADD      r5,#0x40
        MOV      r6,#0x3f
        STRB     r2,[r2,#0x1c]
        MOV      r1,#0x33
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r6,#0x1e
        MOV      r7,#0xf
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1a
        MOV      r6,#0x26
        MOV      r7,#0xe
        LDRB     r2,[r2]
        LSR      r3,r6,#0x14
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0x2f
        MOV      r6,#0x21
        MOV      r7,#0xb
        LSL      r3,r1,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        STR      r2,[sp,#0x18]
        MOV      r3,#0x40
        STR      r4,[sp,#0xdc]
        CMP      r0,r8
        ADD      r3,#0x76
        STR      r7,[sp,#0x48]
        LSL      r1,r4,#0
        ADD      r0,#0x22
        CMP      r1,#0x23
        ADD      r6,r4,r0
        SUB      r7,r4,r0
        LSL      r0,r5,#0x1c
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,#4
        MOV      r7,#0x23
        SUB      r6,r4,#0
        ASR      r7,r4,#8
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0x24
        MOV      r6,#0x21
        MOV      r7,#0x26
        LSL      r3,r1,#0
        SUB      r6,#0x11
        LSL      r6,r2,#4
        STR      r2,[sp,#0x18]
        MOV      r3,#0x35
        STR      r4,[sp,#0x84]
        CMP      r0,r8
        CMP      r4,#0x26
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r6,#0x1e
        MOV      r7,#0x21
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1a
        MOV      r6,#0x1c
        MOV      r7,#0x1f
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        ADD      r3,r4,r4
        MOV      r1,#0x24
        ADD      r6,r4,#4
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        LSL      r2,r2
        ASR      r3,r4,#0x18
        LSL      r4,r2
        MOV      r6,#0x45
        STR      r7,[sp,#0x68]
        LSL      r1,r4,#0
        LDRB     r1,[r0]
        LSL      r3,r3,#8
        ADD      r0,#0x22
        ASR      r3,r4,#0xc
        ASR      r4,r2,#0x14
        ADD      r6,r4,r0
        SUB      r7,r4,r0
        LSL      r0,r5,#0x1c
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,#4
        ASR      r3,r4,#4
        ASR      r6,r4,#0x18
        ASR      r7,r4,#8
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0xe
        MOV      r6,#0x21
        MOV      r7,#0x14
        ADD      r3,r1,r0
        LSL      r0,r0,#4
        SUB      r6,#0x4b
        LSL      r6,r2,#4
        STR      r2,[sp,#0x18]
        STR      r3,[sp,#0xd4]
        STR      r4,[sp,#0x58]
        CMP      r0,r8
        ASR      r6,r4,#8
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r6,#0x1e
        MOV      r7,#0xf
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1a
        MOV      r6,#0x26
        MOV      r7,#0xe
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        CMP      r7,#0x23
        MOV      r1,#0x24
        LSR      r6,r4,#0xc
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        LSL      r2,r2
        ADD      r7,#0x23
        LSL      r4,r2
        STR      r6,[sp,#0x114]
        STR      r7,[sp,#0x48]
        LSL      r1,r4,#0
        ADD      r0,#0x22
        CMP      r1,#0x23
        ADD      r6,r4,r0
        SUB      r7,r4,r0
        LSL      r0,r5,#0x1c
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,#4
        MOV      r7,#0x23
        SUB      r6,r4,#0
        ASR      r7,r4,#8
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0x24
        MOV      r6,#0x21
        MOV      r7,#0x26
        LSL      r3,r1,#0
        SUB      r6,#0x11
        LSL      r6,r2,#4
        STR      r2,[sp,#0x18]
        MOV      r3,#0x35
        STR      r4,[sp,#0x84]
        CMP      r0,r8
        CMP      r4,#0x26
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r6,#0x1e
        MOV      r7,#0x21
        CMP      r0,#0x1a
        LSL      r7,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1a
        MOV      r6,#0x1c
        MOV      r7,#0x1f
        LDR      r0,[sp,#0x48]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        ADD      r3,r4,r4
        MOV      r1,#0x24
        ADD      r6,r4,#4
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        SUB      r2,r4,r7
        MOV      r3,#0x40
        STR      r4,[sp,#0x58]
        CMP      r0,r8
        SUB      r6,r4,r0
        MOV      r1,#0x97
        LSL      r0,r0,#4
        SUB      r0,r7,r5
        TST      r2,r0
        ASR      r3,r4,#0xc
        ASR      r4,r2,#0x14
        ADD      r6,r4,r0
        SUB      r7,r4,r0
        LSL      r0,r5,#0x1c
        ASR      r0,r0,#4
        LSL      r1,r0,#0xc
        ADD      r5,#0x32
        ASR      r3,r4,#4
        ASR      r6,r4,#0x18
        ASR      r7,r4,#8
        LSR      r0,r3,#0x16
        MOV      r3,#0
        MOV      r4,#0xe
        MOV      r6,#0x21
        MOV      r7,#0x14
        ADD      r3,r1,r0
        AND      r0,r0
        SUB      r6,#0xc1
        AND      r6,r2
        LSL      r1,r0,#0x18
        SUB      r4,#0xc2
        AND      r1,r2
        LSL      r0,r3,#0x10
        ADD      r2,#0xc3
        ASR      r2,r2,#0x18
        LSL      r0,r3,#0x10
        ADD      r2,#0xa4
        AND      r7,r1
        SUB      r6,#0xc5
        CMP      r4,#0x17
|unk_0837199A|
        INCBIN	baserom.gba_0x37199a_0x37199c.extracted
        ADD      r2,#0xc7
        MOV      r1,#0x12
        MOV      r6,#0x18
        ADD      r0,r1,r2
        LSL      r0,r1,#3
        SUB      r4,#0x22
        SUB      r3,r4,#0
        ASR      r4,r4,#0x18
        SUB      r7,r4,r0
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r0,#0x22
        MOV      r1,#0x93
        LSL      r4,r2
        LSL      r5,r2
        MOV      r1,#0x97
        SUB      r6,#0xa8
        LSR      r7,r2,#0x14
        MOV      r2,#0
        MOV      r3,#0x32
        MOV      r5,#0x1f
        MOV      r7,#0x35
        LSL      r5,r3,#0
        LDR      r3,[pc,#4]
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        MOV      r6,#0x22
        ADD      r3,r4,#0
        CMP      r3,#0x25
        ADD      r2,#0xc6
        LSL      r2,r2,#0x1c
        AND      r0,r3
        ADD      r7,r4,r0
        ASR      r0,r3,#0xe
        MOV      r2,#0
        MOV      r3,#0x1a
        MOV      r4,#0x1a
        MOV      r5,#0x2e
        MOV      r6,#0x20
        MOV      r7,#9
        CMP      r0,#0x14
        LSL      r0,r2,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0xd
        MOV      r4,#0x17
        MOV      r5,#0x1d
        STR      r6,[sp,#0x58]
        MOV      r7,#0xa
        CMP      r0,#0xf
        LSL      r5,r1,#0
        LSL      r2,r4,#4
        ASR      r3,r4,#0x14
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSR      r6,r4,#4
        LSR      r7,r4,#0xc
        LSR      r0,r5,#8
        ASR      r0,r0,#4
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        MOV      r3,#0x35
        STR      r4,[sp,#0x48]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x20]
        CMP      r0,#0x21
        LSL      r7,r0,#0
        CMP      r0,#0x22
        ASR      r3,r4,#0x20
        SUB      r7,r4,r0
        LSL      r0,r5,#0xc
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,r0
        LSR      r3,r4,#0x14
        LSL      r6,r4,#0x1c
        ASR      r7,r4,#8
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0xb
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#6
        LSL      r3,r1,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        B        |loc_08371e5c|
        AND      r3,r3
        ASR      r4,r2,#0x1a
        ASR      r5,r2,#0x1a
        LSL      r6,r4,#0x14
        MOV      r1,#0x97
        ASR      r0,r0
        MOV      r7,#0x42
        LSL      r2,r3,#0
        SUB      r1,#0xd1
        LSL      r1,r0,#0xc
        SUB      r1,#0x32
        LSL      r6,r4,#0x10
        ASR      r7,r4,#8
        MOV      r4,#0
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#3
        LSL      r3,r1,#0
        SUB      r6,#0x11
        LSL      r6,r2,#4
        ADD      r2,pc,#0x18
        SUB      r4,r7,r0
        STR      r3,[sp,#0xd4]
        STR      r4,[sp,#0x58]
        STR      r5,[sp,#0x100]
        STR      r7,[sp,#0xb0]
        LSL      r1,r4,#0
        CMP      r0,#0x22
        SUB      r3,r4,#0
        ASR      r4,r4,#0x18
        SUB      r7,r4,r0
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,r0
        MOV      r1,#0x93
        LSL      r4,r2
        LSL      r5,r2
        MOV      r1,#0x97
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r5,#0x1f
        MOV      r7,#0x35
        LSL      r5,r3,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        STR      r2,[sp,#0x18]
        MOV      r3,#0x40
        MOV      r5,#0x1c
        LSL      r3,r5,#0x18
        LSL      r4,r6,#0x1e
        ADD      r7,r4,r0
        ASR      r0,r3,#0xe
        MOV      r2,#0
        MOV      r3,#0x30
        MOV      r4,#0x1a
        MOV      r5,#0x2e
        MOV      r6,#0x20
        MOV      r7,#9
        CMP      r0,#0x14
        LSL      r0,r2,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1f
        MOV      r4,#0x17
        MOV      r5,#0x1d
        STR      r6,[sp,#0x58]
        MOV      r7,#0xa
        CMP      r0,#0xf
        LSL      r5,r1,#0
        SUB      r4,#1
        ASR      r1,r4,#4
        LSL      r3,r0,#8
        SUB      r6,r3,r4
        ASR      r1,r4,#4
        MOV      r3,#3
        MOV      r4,#0x15
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#9
        CMP      r0,#0xb
        LSL      r2,r1,#0
        AND      r1,r2
        LSL      r1,r0,#0x18
        LSL      r2,r2
        ASR      r3,r4,#8
        ASR      r4,r2,#0x1a
        ASR      r5,r2,#0x1a
        LSR      r6,r4,#0x20
        MOV      r1,#0x97
        LSL      r0,r5,#0x1c
        MOV      r3,#0
        MOV      r7,#0x10
        CMP      r0,#0x1a
        LSL      r3,r0,#0
        LSL      r1,r0,#6
        MOV      r3,#3
        MOV      r6,#0xd
        MOV      r7,#7
        LSL      r2,r2,#0
        LSR      r3,r4,#0xc
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0x18
        LSR      r7,r4,#0xc
        BNE      |loc_08371b24|
        LSL      r2,r6,#4
|loc_08371b24|
        ADD      r2,#6
        STR      r4,[sp,#0xd0]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x14]
        LSL      r1,r4,#0
        SUB      r7,r4,r0
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        LSL      r6,r4,#0x10
        ASR      r7,r4,#8
        MOV      r4,#0
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#3
        LSL      r3,r1,#0
        LDR      r3,[pc,#4]
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        LDR      r3,[pc,#8]
        ASR      r4,r7,#4
        LSL      r0,r3,#0x10
        ADD      r5,pc,#0xc
        ASR      r3,r6,#0x18
        ADD      r3,#0x74
        STRB     r0,[r0,#0x15]
        CMP      r4,#0x3f
        ADD      r5,pc,#0x1c
        MOV      r1,#0x33
        LSL      r0,r3,#1
        SUB      r4,#0x22
        SUB      r3,r4,#0
        ASR      r4,r4,#0x18
        SUB      r7,r4,r0
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r0,#0x22
        MOV      r1,#0x93
        LSL      r4,r2
        LSL      r5,r2
        MOV      r1,#0x97
        SUB      r7,#0x78
        LSL      r5,r1,#0
        ADD      r2,#0x22
        SUB      r3,r4,#4
        ADD      r5,#0x25
        ADD      r7,r4,#4
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        MOV      r6,#0x22
        ADD      r3,r4,#0
        CMP      r3,#0x25
        ADD      r5,pc,#0x18
        LSL      r3,r6,#0x1c
        ADD      r7,r4,r0
        ASR      r0,r3,#0xe
        MOV      r2,#0
        MOV      r3,#0x1a
        MOV      r4,#0x1a
        MOV      r5,#0x2e
        MOV      r6,#0x20
        MOV      r7,#9
        CMP      r0,#0x14
        LSL      r0,r2,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0xd
        MOV      r4,#0x17
        MOV      r5,#0x1d
        STR      r6,[sp,#0x58]
        MOV      r7,#0xa
        CMP      r0,#0xf
        LSL      r5,r1,#0
        LSL      r2,r4,#4
        ASR      r3,r4,#0x14
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSR      r6,r4,#4
        LSR      r7,r4,#0xc
        LSR      r0,r5,#8
        ASR      r0,r0,#4
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        MOV      r3,#0x35
        STR      r4,[sp,#0x48]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x20]
        CMP      r0,#0x21
        LSL      r7,r0,#0
        CMP      r0,#0x22
        ASR      r3,r4,#0x20
        SUB      r7,r4,r0
        LSL      r0,r5,#0xc
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,r0
        LSR      r3,r4,#0x14
        LSL      r6,r4,#0x1c
        ASR      r7,r4,#8
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r4,#0xb
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#6
        LSL      r3,r1,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        B        |loc_08372012|
        AND      r3,r3
        ASR      r4,r2,#0x1a
        ASR      r5,r2,#0x1a
        LSL      r6,r4,#0x14
        MOV      r1,#0x97
        ASR      r0,r0
        MOV      r7,#0x42
        LSL      r2,r3,#0
        SUB      r1,#0xd1
        LSL      r1,r0,#0xc
        SUB      r1,#0x32
        LSL      r6,r4,#0x10
        ASR      r7,r4,#8
        MOV      r4,#0
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#3
        LSL      r3,r1,#0
        SUB      r6,#0x11
        LSL      r6,r2,#4
        ADD      r2,pc,#0x18
        SUB      r4,r7,r0
        STR      r3,[sp,#0xd4]
        STR      r4,[sp,#0x58]
        STR      r5,[sp,#0x100]
        STR      r7,[sp,#0xb0]
        LSL      r1,r4,#0
        CMP      r0,#0x22
        SUB      r3,r4,#0
        ASR      r4,r4,#0x18
        SUB      r7,r4,r0
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,r0
        MOV      r1,#0x93
        LSL      r4,r2
        LSL      r5,r2
        MOV      r1,#0x97
        LSR      r0,r3,#0x16
        MOV      r2,#0
        MOV      r3,#0xd
        MOV      r5,#0x1f
        MOV      r7,#0x35
        LSL      r5,r3,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        STR      r2,[sp,#0x18]
        MOV      r3,#0x40
        MOV      r5,#0x1c
        LSL      r3,r5,#0x18
        LSL      r4,r6,#0x1e
        ADD      r7,r4,r0
        ASR      r0,r3,#0xe
        MOV      r2,#0
        MOV      r3,#0x30
        MOV      r4,#0x1a
        MOV      r5,#0x2e
        MOV      r6,#0x20
        MOV      r7,#9
        CMP      r0,#0x14
        LSL      r0,r2,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1f
        MOV      r4,#0x17
        MOV      r5,#0x1d
        STR      r6,[sp,#0x58]
        MOV      r7,#0xa
        CMP      r0,#0xf
        LSL      r5,r1,#0
        SUB      r4,#1
        ASR      r1,r4,#4
        LSL      r3,r0,#8
        SUB      r6,r3,r4
        ASR      r1,r4,#4
        MOV      r3,#3
        MOV      r4,#0x15
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#9
        CMP      r0,#0xb
        LSL      r2,r1,#0
        AND      r1,r2
        LSL      r1,r0,#0x18
        LSL      r2,r2
        ASR      r3,r4,#8
        ASR      r4,r2,#0x1a
        ASR      r5,r2,#0x1a
        LSR      r6,r4,#0x20
        MOV      r1,#0x97
        LSL      r0,r5,#0x1c
        MOV      r3,#0
        MOV      r7,#0x10
        CMP      r0,#0x1a
        LSL      r3,r0,#0
        LSL      r1,r0,#6
        MOV      r3,#3
        MOV      r6,#0xd
        MOV      r7,#7
        LSL      r2,r2,#0
        LSR      r3,r4,#0xc
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0x18
        LSR      r7,r4,#0xc
        BNE      |loc_08371cda|
        LSL      r2,r6,#4
|loc_08371cda|
        ADD      r2,#6
        STR      r4,[sp,#0xd0]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x14]
        LSL      r1,r4,#0
        SUB      r7,r4,r0
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        LSL      r6,r4,#0x10
        ASR      r7,r4,#8
        MOV      r4,#0
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#3
        LSL      r3,r1,#0
        STM      r1!,{r6}
        ASR      r6,r7,#0x18
        LSL      r0,r0,#5
        STM      r2!,{r1,r2}
        ASR      r4,r7,#4
        ADD      r0,r0,r1
        STM      r3!,{r2}
        ASR      r5,r6,#8
        ADD      r6,r2,r0
        ADD      r4,pc,#0x10
        LSR      r5,r6,#0x1c
        STM      r5!,{r6}
        ASR      r1,r0,#0x1d
        ADD      r4,r5,r0
        STM      r7!,{r1,r3,r5,r6,r7}
        ASR      r5,r6,#8
        ADD      r1,r4,r0
        LDRH     r6,[r4]
        LDMIA    r0!,{r3,r4}
        MOV      r2,#0
        MOV      r3,#0x3c
        MOV      r4,#0x1e
        MOV      r7,#0x16
        LSL      r2,r3,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        STR      r3,[sp,#0xe0]
        STR      r4,[sp,#0x84]
        STR      r5,[sp,#0x100]
        STR      r7,[sp,#0x100]
        ADD      r0,sp,#0x84
        ASR      r1,r0,#0x1d
        LSL      r5,r1,#0
        ADD      r2,#0x22
        SUB      r3,r4,#4
        ADD      r5,#0x25
        ADD      r7,r4,#4
        LSL      r0,r0,#4
        SUB      r4,#0x4b
        LSL      r3,r2,#4
        MOV      r2,#6
        MOV      r3,#0x26
        MOV      r5,#0x1c
        STM      r6!,{r0,r1,r3,r5}
        ASR      r5,r6,#8
        ADD      r7,r0,r0
        MOV      r7,#0x40
        LDR      r0,[sp,#0x60]
        LSL      r3,r2,#0
        SUB      r2,r4,r0
        SUB      r3,r4,r0
        CMP      r6,#0x24
        MOV      r0,#0x25
        LSR      r6,r4,#4
        ASR      r7,r4,#0x10
        ASR      r0,r5,#0x20
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        LSR      r2,r4,#0x14
        ASR      r3,r4,#0x1c
        ADD      r4,r4,#4
        ASR      r5,r4,#0x18
        LSR      r6,r2,#0xa
        LSR      r7,r4,#0x1c
        LSR      r0,r5,#0x14
        MOV      r2,#0
        MOV      r3,#1
        MOV      r4,#0x15
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#9
        CMP      r0,#0xb
        LSL      r2,r1,#0
        SUB      r6,#0x11
        LSL      r6,r2,#4
        B        |loc_083721a0|
        ADD      r5,#0x1a
        ASR      r3,r4,#8
        ASR      r4,r2,#0x1a
        ASR      r5,r2,#0x1a
        LSR      r6,r4,#0x20
        MOV      r1,#0x97
        LSL      r0,r5,#0x1c
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r7,#0x10
        CMP      r0,#0x1a
        LSL      r3,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1a
        MOV      r6,#0xd
        MOV      r7,#7
        LSL      r2,r2,#0
        LSR      r2,r4,#0x14
        LSR      r3,r4,#0xc
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0x18
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        SUB      r2,r4,r7
        STR      r4,[sp,#0x100]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x14]
        LSL      r1,r4,#0
        NEG      r1,r0
        SUB      r7,r4,r0
        BNE      |loc_08371ddc|
        LSL      r1,r7,#4
|loc_08371ddc|
        ADD      r2,#3
        MOV      r6,#0x39
        MOV      r7,#4
        LSL      r2,r2,#0
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0xc
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        SUB      r4,#0xa2
        ADD      r5,#0x1a
        ASR      r3,r2,#0x1a
        LSL      r4,r2
        CMP      r4,#0x95
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r4,#0x1e
        MOV      r7,#0x16
        LSL      r2,r3,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        STR      r3,[sp,#0x68]
        STR      r4,[sp,#0x84]
        STR      r5,[sp,#0x100]
        STR      r7,[sp,#0x100]
        LDR      r0,[sp,#0x84]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        SUB      r3,r4,#4
        ADD      r5,#0x25
        ADD      r7,r4,#4
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        LSL      r2,r2
        ADD      r3,r4,#0
        CMP      r3,#0x25
        PUSH     {r1,r2}
        MOV      r7,#7
        LDR      r0,[sp,#0x60]
        LSL      r3,r2,#0
        ADD      r0,#0x22
        SUB      r3,r4,r0
        CMP      r6,#0x24
        MOV      r0,#0x25
        LSR      r6,r4,#4
        ASR      r7,r4,#0x10
        ASR      r0,r5,#0x20
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,#4
        ASR      r3,r4,#0x1c
        ADD      r4,r4,#4
        ASR      r5,r4,#0x18
        LSR      r6,r2,#0xa
        LSR      r7,r4,#0x1c
        LSR      r0,r5,#0x14
        LSL      r0,r0,#4
        MOV      r1,#0x3c
        LSL      r1,r2,#0xc
        SUB      r2,r0,#0
|loc_08371e5c|
        MOV      r1,#0x1b
        LSL      r1,r2,#0xc
        ASR      r3,r4,#0x14
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSR      r6,r4,#4
        LSR      r7,r4,#0xc
        LSR      r0,r5,#8
        ASR      r0,r0,#4
        LSL      r0,r0,#5
        STR      r2,[sp,#0x18]
        MOV      r3,#0x40
        STR      r4,[sp,#0x48]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x20]
        CMP      r0,#0x21
        LSL      r7,r0,#0
        ASR      r3,r4,#0x20
        SUB      r7,r4,r0
        LSL      r0,r5,#0xc
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        LSR      r3,r4,#0x14
        LSL      r6,r4,#0x1c
        ASR      r7,r4,#8
        MOV      r3,#0
        MOV      r4,#0xb
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#6
        LSL      r3,r1,#0
        ADD      r2,#0xd1
        LSL      r1,r0,#0x18
        ADD      r4,#0x32
        ASR      r4,r2,#0x1a
        ASR      r5,r2,#0x1a
        LSL      r6,r4,#0x14
        MOV      r1,#0x97
        MOV      r7,#0
        LSL      r2,r3,#0
        LSL      r1,r0,#6
        MOV      r6,#3
        MOV      r7,#4
        LSL      r2,r2,#0
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0xc
        LSR      r7,r4,#0xc
        LSL      r0,r0,#4
        SUB      r6,#0x4b
        LSL      r6,r2,#4
        LSL      r6,r0,#8
        SUB      r4,#0x4b
        ADD      r1,r2,r0
        LSL      r4,r0,#0xc
        ADD      r3,#0xa5
        STRB     r6,[r2,#0x10]
        AND      r3,r6
        SUB      r7,#0x75
        LSL      r4,r5,#0x1c
        ADD      r3,#0xa5
        LDR      r1,[r4,r0]
        MOV      r2,#0
        MOV      r3,#0x3c
        MOV      r4,#0x1e
        MOV      r7,#0x16
        LSL      r2,r3,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        STR      r3,[sp,#0xe0]
        STR      r4,[sp,#0x84]
        STR      r5,[sp,#0x100]
        STR      r7,[sp,#0x100]
        LDRB     r1,[r4]
        LSR      r7,r7,#0x14
        MOV      r2,#0
        MOV      r3,#0x32
        MOV      r5,#0x1f
        MOV      r7,#0x35
        LSL      r5,r3,#0
        SUB      r4,#0x11
        LSL      r3,r2,#4
        MOV      r2,#6
        MOV      r3,#0x26
        MOV      r5,#0x1c
        LSL      r3,r5,#0x18
        ADD      r3,#0xa5
        MOV      r7,#7
        LDR      r0,[sp,#0x60]
        LSL      r3,r2,#0
        SUB      r2,r4,r0
        SUB      r3,r4,r0
        CMP      r6,#0x24
        MOV      r0,#0x25
        LSR      r6,r4,#4
        ASR      r7,r4,#0x10
        ASR      r0,r5,#0x20
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        LSR      r2,r4,#0x14
        ASR      r3,r4,#0x1c
        ADD      r4,r4,#4
        ASR      r5,r4,#0x18
        LSR      r6,r2,#0xa
        LSR      r7,r4,#0x1c
        LSR      r0,r5,#0x14
        MOV      r2,#0
        MOV      r3,#1
        MOV      r4,#0x15
        MOV      r5,#0xb
        MOV      r6,#0xb
        MOV      r7,#9
        CMP      r0,#0xb
        LSL      r2,r1,#0
        SUB      r6,#0x11
        LSL      r6,r2,#4
        B        |loc_08372356|
        ADD      r5,#0x1a
        ASR      r3,r4,#8
        ASR      r4,r2,#0x1a
        ASR      r5,r2,#0x1a
        LSR      r6,r4,#0x20
        MOV      r1,#0x97
        LSL      r0,r5,#0x1c
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r7,#0x10
        CMP      r0,#0x1a
        LSL      r3,r0,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        MOV      r3,#0x1a
        MOV      r6,#0xd
        MOV      r7,#7
        LSL      r2,r2,#0
        LSR      r2,r4,#0x14
        LSR      r3,r4,#0xc
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0x18
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        SUB      r2,r4,r7
        STR      r4,[sp,#0x100]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x14]
        LSL      r1,r4,#0
        NEG      r1,r0
        SUB      r7,r4,r0
        BNE      |loc_08371f92|
        LSL      r1,r7,#4
|loc_08371f92|
        ADD      r2,#3
        MOV      r6,#0x39
        MOV      r7,#4
        LSL      r2,r2,#0
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0xc
        LSR      r7,r4,#0xc
        ASR      r0,r0,#4
        ASR      r6,r7,#0x18
        LSL      r1,r0,#0x18
        SUB      r4,#0xa2
        ADD      r5,#0x1a
        ASR      r3,r2,#0x1a
        LSL      r4,r2
        CMP      r4,#0x95
        MOV      r1,#0x97
        MOV      r2,#0
        MOV      r3,#0x28
        MOV      r4,#0x1e
        MOV      r7,#0x16
        LSL      r2,r3,#0
        LSL      r1,r0,#6
        MOV      r2,#3
        STR      r3,[sp,#0x68]
        STR      r4,[sp,#0x84]
        STR      r5,[sp,#0x100]
        STR      r7,[sp,#0x100]
        LDR      r0,[sp,#0x84]
        LSL      r5,r1,#0
        LSR      r2,r4,#0x14
        SUB      r3,r4,#4
        ADD      r5,#0x25
        ADD      r7,r4,#4
        ASR      r0,r0,#4
        ASR      r4,r7,#0xc
        LSL      r1,r0,#0x18
        LSL      r2,r2
        ADD      r3,r4,#0
        CMP      r3,#0x25
        PUSH     {r1,r2}
        MOV      r7,#7
        LDR      r0,[sp,#0x60]
        LSL      r3,r2,#0
        ADD      r0,#0x22
        SUB      r3,r4,r0
        CMP      r6,#0x24
        MOV      r0,#0x25
        LSR      r6,r4,#4
        ASR      r7,r4,#0x10
        ASR      r0,r5,#0x20
        STRH     r0,[r0,#8]
        LSL      r1,r0,#0xc
        SUB      r2,r4,#4
        ASR      r3,r4,#0x1c
        ADD      r4,r4,#4
        ASR      r5,r4,#0x18
        LSR      r6,r2,#0xa
        LSR      r7,r4,#0x1c
        LSR      r0,r5,#0x14
        LSL      r0,r0,#4
        MOV      r1,#0x3c
        LSL      r1,r2,#0xc
        SUB      r2,r0,#0
|loc_08372012|
        MOV      r1,#0x1b
        LSL      r1,r2,#0xc
        ASR      r3,r4,#0x14
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSR      r6,r4,#4
        LSR      r7,r4,#0xc
        LSR      r0,r5,#8
        ASR      r0,r0,#4
        LSL      r0,r0,#5
        STR      r2,[sp,#0x18]
        MOV      r3,#0x40
        STR      r4,[sp,#0x48]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x20]
        CMP      r0,#0x21
        LSL      r7,r0,#0
        NEG      r1,r0
        ASR      r3,r4,#0x20
        SUB      r7,r4,r0
        LSL      r0,r5,#0xc
        BNE      |loc_08372042|
        LSL      r0,r6,#4
|loc_08372042|
        ADD      r2,#3
        MOV      r3,#0x34
        MOV      r6,#0xd
        MOV      r7,#7
        LSL      r2,r2,#0
        LSR      r3,r4,#0xc
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0x18
        LSR      r7,r4,#0xc
        BNE      |loc_0837205a|
        LSL      r4,r6,#4
|loc_0837205a|
        ADD      r2,#6
        STR      r4,[sp,#0xdc]
        STR      r5,[sp,#0x58]
        MOV      r6,#0x16
        STR      r7,[sp,#0x14]
        LSL      r1,r4,#0
        NEG      r1,r0
        SUB      r7,r4,r0
        BNE      |loc_0837206e|
        LSL      r0,r6,#4
|loc_0837206e|
        ADD      r2,#3
        MOV      r6,#0x2d
        MOV      r7,#4
        LSL      r2,r2,#0
        LSR      r4,r4,#0xc
        LSR      r5,r4,#0xc
        LSL      r6,r4,#0xc
        LSR      r7,r4,#0xc
        AND      r0,r0
        SUB      r4,#0xc1
        AND      r6,r2
        LSL      r1,r0,#0x18
        SUB      r4,#0xa2
        MOV      r1,#0x1a
        ADD      r2,#0xc4
        AND      r7,r1
        LSL      r0,r3,#0x10
        ADD      r2,#0xc5
        MOV      r1,#0x12
        LSR      r0,r3,#0x10
        SUB      r4,#0xc6
        AND      r1,r2
        LSL      r0,r3,#0x10
        ADD      r2,#0xc7
        CMP      r4,#0x12
        LSL      r0,r3,#0x10
        ADD      r0,r1,r2
        LSL      r0,r1,#3
        MOV      r1,#0x24
        SUB      r4,#0x26
        CMP      r3,#0x27
        ADD      r2,#0xa8
        LSL      r2,r2,#0x1c
        LSL      r0,r0,#4
        LSL      r0,r7,#5
        LSL      r3,r0,#8
        ADD      r2,r2,r5
        ADD      r2,#0xc3
        LSR      r2,r2,#8
        LDMIA    r0!,{r3,r4}
        LSL      r4,r2
        SUB      r6,#0xa5
        CMP      r5,#0x17
        SUB      r0,#0x26
        STR      r2,[sp]
        MOV      r4,#0xb
        MOV      r6,#0x21
        MOV      r7,#0x32
        ADD      r0,sp,#0xa8
        ASR      r6,r7,#0x1c
        LSL      r1,r1,#0
        LDRH     r1,[r0,r0]
        LSL      r3,r2,#4
        B        |loc_083724e8|
        CMP      r4,#0x1a
        SUB      r6,#0xa3
        LSR      r7,r2,#0x18
        LSL      r4,r2
        ADD      r2,#0xa5
        MOV      r1,#0x12
        CMP      r4,#0x26
        MOV      r4,#0
        MOV      r6,#0x21
        MOV      r7,#0x26
        ADD      r0,sp,#0xa4
        ASR      r2,r6,#8
        LSL      r7,r0,#0
        ASR      r1,r2,#0x18
        LSL      r1,r0,#0xc
        ADD      r2,r4,r7
        ADD      r3,pc,#0x84
        ASR      r2,r6,#8
        STR      r4,[sp,#0x28]
        MOV      r6,#0x40
        LSL      r1,r4,#0
        SUB      r4,#1
        ASR      r1,r4,#4
        STR      r2,[sp,#0xc]
        MOV      r4,#0xb
        MOV      r6,#0x21
        MOV      r7,#0x1b
        LSL      r0,r5,#0
        AND      r1,r2
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        STR      r4,[sp,#0x84]
        ADD      r5,pc,#0x100
        ASR      r6,r7,#0x1c
        MOV      r6,#0x2c
        LSL      r5,r2,#0
        MOV      r1,#0x24
        LSR      r6,r4,#0x1c
        MOV      r7,#0x27
        SUB      r6,#0xa8
        LSR      r7,r2,#4
        LSL      r0,r0,#4
        LSL      r0,r7,#5
        ASR      r3,r0,#8
        ADD      r3,pc,#0x64
        ASR      r6,r7,#0x1c
        STR      r4,[sp,#0x34]
        ADD      r5,pc,#0x100
        ASR      r2,r6,#8
        MOV      r6,#0x21
        LSL      r1,r1,#0
        LSR      r2,r2,#0xe
        MOV      r1,#0x24
        LSL      r6,r4,#0x14
        MOV      r6,#0x27
        ADD      r2,#0xa8
        LSL      r2,r2,#0x1c
        LSL      r0,r0,#4
        ASR      r2,r3,#0xd
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        ADD      r3,pc,#0xb0
        ASR      r2,r6,#8
        STR      r4,[sp,#0x28]
        MOV      r6,#0x40
        LSL      r1,r0,#0
        MOV      r1,#0x24
        SUB      r6,#0xa5
        CMP      r4,#0x17
        MOV      r5,#0x27
        ASR      r0,r0,#4
        LSL      r6,r2,#4
        B        |loc_08372574|
        MOV      r1,#0x19
        LSL      r4,r2
        SUB      r6,#0xa8
        LSR      r7,r2,#4
        STR      r2,[sp]
        ADD      r3,pc,#0x2c
        ASR      r6,r7,#0x1c
        MOV      r4,#0xd
        MOV      r7,#0x21
        LSL      r4,r4,#0
        LDRB     r1,[r0]
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        STR      r4,[sp,#0x84]
        LSL      r0,r0,#0x15
        ADD      r7,#0x3c
        LSR      r4,r0,#0x20
        MOV      r4,#0
        LSL      r1,r4,#0x14
        LSL      r4,r6
        MOV      r3,#0x27
        SUB      r4,#8
        LSL      r3,r1,#0x10
        LSL      r0,r1,#0
        LSL      r1,r2,#4
        ASR      r3,r0,#8
|loc_083721a0|
        LSL      r1,r3,#0xc
        ASR      r4,r7,#4
        LSR      r4,r0,#0x20
        LSL      r4,r2
        CMP      r5,#0x95
        PUSH     {r3}
        LSL      r5,r1,#0
        LSR      r2,r2,#0xe
        PUSH     {r0,r1}
        MOV      r4,#0x13
        MOV      r7,#0x21
        LDR      r0,[sp,#0x88]
        LSL      r1,r1,#0
        LDRH     r1,[r0,r0]
        LSL      r3,r2,#4
        B        |inc_0x3725c0_0x3bb78c| + 0xe
        CMP      r4,#0x1a
        LSR      r3,r2,#0x1a
        LSL      r4,r2
        ADD      r2,#0xa5
        MOV      r1,#0x12
        MOV      r4,#0
        MOV      r7,#0x21
        ADD      r0,sp,#0x84
        ASR      r2,r6,#8
        LSL      r7,r0,#0
        ASR      r1,r2,#0x18
        LSL      r1,r0,#0xc
        ADD      r2,r4,r7
        ADD      r3,pc,#0x84
        ASR      r2,r6,#8
        STR      r4,[sp,#0x28]
        MOV      r7,#0x40
        LSL      r0,r4,#0
        LSR      r2,r2,#0xe
        MOV      r1,#0x24
        LSL      r0,r0,#4
        LSL      r0,r7,#5
        B        |inc_0x3725c0_0x3bb78c| + 0x3c
        MOV      r1,#0x1a
        LSL      r4,r2
        SUB      r6,#0xa5
        CMP      r4,#0x17
        SUB      r7,r4,#4
        MOV      r4,#0
        ADD      r0,sp,#0x84
        ASR      r6,r7,#0x1c
        LSL      r1,r1,#0
        LSL      r1,r2,#4
        ASR      r3,r0,#8
        ADD      r3,pc,#0x64
        ASR      r6,r7,#0x1c
        STR      r4,[sp,#0x34]
        ADD      r5,pc,#0x100
        ASR      r2,r6,#8
        MOV      r7,#0x21
        LSL      r6,r3,#0
        LSR      r2,r2,#0xe
        MOV      r1,#0x24
        ADD      r2,#0xa8
        LSL      r2,r2,#0x1c
        LSL      r0,r0,#4
        ASR      r2,r3,#0xd
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        ADD      r3,pc,#0xb0
        ASR      r2,r6,#8
        STR      r4,[sp,#0x28]
        MOV      r7,#0x40
        LSL      r5,r3,#0
        MOV      r1,#0x24
        SUB      r6,#0xa5
        CMP      r4,#0x17
        ASR      r0,r0,#4
        LSL      r6,r2,#4
        B        |inc_0x3725c0_0x3bb78c| + 0x80
        MOV      r1,#0x19
        LSL      r4,r2
        ADD      r7,r4,#0
        SUB      r6,#0xa8
        LSR      r7,r2,#4
        STR      r2,[sp]
        ADD      r3,pc,#0x2c
        ASR      r6,r7,#0x1c
        MOV      r4,#0xd
        LSL      r1,r4,#0
        LDRB     r1,[r0]
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        STR      r4,[sp,#0x84]
        ADD      r5,pc,#0x100
        ASR      r2,r6,#8
        MOV      r7,#0x21
        LSL      r3,r3,#0
        MOV      r1,#0x24
        ADD      r2,#0xa8
        LSL      r2,r2,#0x1c
        ASR      r0,r0,#4
        LSL      r1,r0,#0xc
        ADD      r2,r2,r4
        ADD      r2,#0xa3
        LSR      r2,r2,#8
        LSL      r4,r2
        SUB      r6,#0xa5
        CMP      r5,#0x17
        SUB      r7,r4,r0
        STR      r2,[sp]
        MOV      r4,#0xb
        ADD      r0,sp,#0x84
        ASR      r6,r7,#0x1c
        LSL      r1,r1,#0
        LDRH     r1,[r0,r0]
        LSL      r3,r2,#4
        B        |inc_0x3725c0_0x3bb78c| + 0xd2
        CMP      r4,#0x1a
        SUB      r6,#0xa3
        LSR      r7,r2,#0x18
        LSL      r4,r2
        ADD      r2,#0xa5
        MOV      r1,#0x12
        ADD      r7,r4,r4
        MOV      r4,#0
        ADD      r0,sp,#0x84
        ASR      r2,r6,#8
        LSL      r7,r0,#0
        ASR      r1,r2,#0x18
        LSL      r1,r0,#0xc
        ADD      r2,r4,r7
        ADD      r3,pc,#0x84
        ASR      r2,r6,#8
        STR      r4,[sp,#0x28]
        MOV      r7,#0x40
        LSL      r0,r3,#0
        SUB      r4,#1
        ASR      r1,r4,#4
        STR      r2,[sp,#0xc]
        MOV      r4,#0xb
        LSL      r1,r4,#0
        AND      r1,r2
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        STR      r4,[sp,#0x84]
        ADD      r5,pc,#0x100
        ASR      r6,r7,#0x1c
        MOV      r7,#0x2c
        LSL      r7,r2,#0
        MOV      r1,#0x24
        SUB      r6,#0xa8
        LSR      r7,r2,#4
        LSL      r0,r0,#4
        LSL      r0,r7,#5
        ASR      r3,r0,#8
        ADD      r3,pc,#0x64
        ASR      r6,r7,#0x1c
        STR      r4,[sp,#0x34]
        ADD      r5,pc,#0x100
        ASR      r2,r6,#8
        MOV      r7,#0x21
        LSL      r6,r2,#0
        LSR      r2,r2,#0xe
        MOV      r1,#0x24
        ASR      r7,r4,#0x14
        ADD      r2,#0xa8
        LSL      r2,r2,#0x1c
        LSL      r0,r0,#4
        ASR      r2,r3,#0xd
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        ADD      r3,pc,#0xb0
        ASR      r2,r6,#8
        STR      r4,[sp,#0x28]
        LSL      r0,r0,#1
        MOV      r1,#0x24
        SUB      r6,#0xa5
        CMP      r4,#0x17
        ASR      r7,r4,#0x10
        ASR      r0,r0,#4
        LSL      r6,r2,#4
        B        |inc_0x3725c0_0x3bb78c| + 0x14e
        MOV      r1,#0x19
        LSL      r4,r2
        SUB      r6,#0xa8
        LSR      r7,r2,#4
        STR      r2,[sp]
        ADD      r3,pc,#0x2c
        ASR      r6,r7,#0x1c
        MOV      r4,#0xd
        MOV      r7,#0x21
        LSL      r3,r2,#0
        LDRB     r1,[r0]
        LSL      r1,r0,#0x18
        SUB      r2,r4,r3
        STRB     r1,[r4,#0x10]
        AND      r5,r6
        ADD      r5,pc,#0x14
        ADD      r7,#0x41
        MOV      r4,#0
        MOV      r7,#0x21
        LSR      r2,r2,#0x20
        ADD      r5,#0x87
        LSR      r2,r2,#0xc
        ASR      r0,r0,#4
        LSL      r1,r0,#0xc
        ADD      r2,r2,r4
        ASR      r3,r2,#4
        ADD      r3,#0x74
        STRB     r0,[r0,#0x15]
        CMP      r5,#0x3f
        SUB      r6,#0x18
        LSR      r7,r2,#0x14
        STR      r2,[sp]
        ASR      r3,r1,#0xc
        MOV      r4,#0x13
        MOV      r7,#0x21
        ADD      r0,sp,#0x44
        ASR      r3,r6,#8
        LSL      r1,r1,#0
        LDRH     r1,[r0,r0]
        LSL      r3,r2,#4
|loc_08372356|
        B        |inc_0x3725c0_0x3bb78c| + 0x1a6
|dat_08372358|
|unk_08372358|
        INCBIN	baserom.gba_0x372358_0x3724e8.extracted
|loc_083724e8|
|unk_083724E8|
        	SUB r0, #0x22
        	LSL r5, r0, #1
        	LDRH r1, [r0, r0]
        	LSL r3, r2, #4
        	B        |inc_0x3725c0_0x3bb78c| + 0x340
|unk_083724F2|
        INCBIN  baserom.gba_0x3724f2_0x372574.extracted
|loc_08372574|
|unk_08372574|
; cited by 0x083724D4 (a pc-relative load targets 0x083725B4)
        	ADD r7, #0x1b
        	SUB r0, #0x3f
        	LSL r6, r7, #0
        	ADD r3, r2, #6
        	MOV r1, #0x24
        	ADD r3, #0x37
        	ASR r0, r0, #4
        	LSL r1, r0, #0xc
        	ADD r2, r2, r4
        	CMP r3, #0x93
        	LSL r4, r2
        	SUB r5, r4, r0
        	STR r2, [sp]
        	MOV r3, #0xb
        	MOV r4, #0xe
        	SUB r0, #0x21
        	LSL r7, r7, #0
        	LDRH r1, [r0, r0]
        	LSL r3, r2, #4
        	B        |inc_0x3725c0_0x3bb78c| + 0x3ea
|unk_0837259C|
        INCBIN  baserom.gba_0x37259c_0x3725c0.extracted
|inc_0x3725c0_0x3bb78c|
        INCLUDE assetdir3_3725c0.s
        INCLUDE rawlabeled_3bb78c.s
|inc_0x3bbbb0_0x3bbe70|
|unk_083BBBB0|
        INCBIN  baserom.gba_0x3bbbb0_0x3bbe70.extracted
        INCLUDE rawlabeled_3bbe70.s
        CODE32
		INCBIN		build\asset_splash.compressed
|inc_0x3c33f8_0x3c34d0|
        INCLUDE rawlabeled_3c33f8.s
        INCBIN  build\spritecontainer\sprite_003C34D0_003C3A24.bin
        INCBIN  build\spritecontainer\sprite_003C3A24_003C3AC4.bin
        INCBIN  build\spritecontainer\sprite_003C3AC4_003C3AE8.bin
        INCBIN  build\spritecontainer\sprite_003C3AE8_003C465C.bin
        INCBIN  build\spritecontainer\sprite_003C465C_003C46FC.bin
        INCBIN  build\spritecontainer\sprite_003C46FC_003C4720.bin
        INCBIN  build\spritecontainer\sprite_003C4720_003C49A0.bin
        INCBIN  build\spritecontainer\sprite_003C49A0_003C4A40.bin
        INCBIN  build\spritecontainer\sprite_003C4A40_003C4A64.bin
        INCBIN  build\spritecontainer\sprite_003C4A64_003C5124.bin
        INCBIN  build\spritecontainer\sprite_003C5124_003C51C4.bin
        INCBIN  build\spritecontainer\sprite_003C51C4_003C5208.bin
        INCBIN  build\spritecontainer\sprite_003C5208_003C5828.bin
        INCBIN  build\spritecontainer\sprite_003C5828_003C58C8.bin
        INCBIN  build\spritecontainer\sprite_003C58C8_003C58EC.bin
        INCBIN  build\spritecontainer\sprite_003C58EC_003C6420.bin
        INCBIN  build\spritecontainer\sprite_003C6420_003C6510.bin
        INCBIN  build\spritecontainer\sprite_003C6510_003C6544.bin
        INCBIN  build\spritecontainer\sprite_003C6544_003C6C84.bin
        INCBIN  build\spritecontainer\sprite_003C6C84_003C6D24.bin
        INCBIN  build\spritecontainer\sprite_003C6D24_003C6D48.bin
        INCBIN  build\spritecontainer\sprite_003C6D48_003C7A70.bin
        INCBIN  build\spritecontainer\sprite_003C7A70_003C7B60.bin
        INCBIN  build\spritecontainer\sprite_003C7B60_003C7B94.bin
        INCBIN  build\spritecontainer\sprite_003C7B94_003C8288.bin
        INCBIN  build\spritecontainer\sprite_003C8288_003C8328.bin
        INCBIN  build\spritecontainer\sprite_003C8328_003C834C.bin
        INCBIN  build\spritecontainer\sprite_003C834C_003C8FD8.bin
        INCBIN  build\spritecontainer\sprite_003C8FD8_003C90C8.bin
        INCBIN  build\spritecontainer\sprite_003C90C8_003C90FC.bin
        INCBIN  build\spritecontainer\sprite_003C90FC_003C95F4.bin
        INCBIN  build\spritecontainer\sprite_003C95F4_003C9694.bin
        INCBIN  build\spritecontainer\sprite_003C9694_003C96B8.bin
        INCBIN  build\spritecontainer\sprite_003C96B8_003CA298.bin
        INCBIN  build\spritecontainer\sprite_003CA298_003CA3D8.bin
        INCBIN  build\spritecontainer\sprite_003CA3D8_003CA41C.bin
        INCBIN  build\spritecontainer\sprite_003CA41C_003CA86C.bin
        INCBIN  build\spritecontainer\sprite_003CA86C_003CA90C.bin
        INCBIN  build\spritecontainer\sprite_003CA90C_003CA930.bin
        INCBIN  build\spritecontainer\sprite_003CA930_003CB5C8.bin
        INCBIN  build\spritecontainer\sprite_003CB5C8_003CB708.bin
        INCBIN  build\spritecontainer\sprite_003CB708_003CB74C.bin
        INCBIN  build\spritecontainer\sprite_003CB74C_003CBD74.bin
        INCBIN  build\spritecontainer\sprite_003CBD74_003CBE14.bin
        INCBIN  build\spritecontainer\sprite_003CBE14_003CBE38.bin
        INCBIN  build\spritecontainer\sprite_003CBE38_003CC29C.bin
        INCBIN  build\spritecontainer\sprite_003CC29C_003CC33C.bin
        INCBIN  build\spritecontainer\sprite_003CC33C_003CC360.bin
        INCBIN  build\spritecontainer\sprite_003CC360_003CCDC8.bin
        INCBIN  build\spritecontainer\sprite_003CCDC8_003CCF08.bin
        INCBIN  build\spritecontainer\sprite_003CCF08_003CCF4C.bin
        INCBIN  build\spritecontainer\sprite_003CCF4C_003CDC28.bin
        INCBIN  build\spritecontainer\sprite_003CDC28_003CDD68.bin
        INCBIN  build\spritecontainer\sprite_003CDD68_003CDDAC.bin
        INCBIN  build\spritecontainer\sprite_003CDDAC_003CE5C4.bin
        INCBIN  build\spritecontainer\sprite_003CE5C4_003CE6B4.bin
        INCBIN  build\spritecontainer\sprite_003CE6B4_003CE6E8.bin
        INCBIN  build\spritecontainer\sprite_003CE6E8_003CED28.bin
        INCBIN  build\spritecontainer\sprite_003CED28_003CEDC8.bin
        INCBIN  build\spritecontainer\sprite_003CEDC8_003CEDEC.bin
        INCBIN  build\spritecontainer\sprite_003CEDEC_003CEE3C.bin
        INCBIN  build\spritecontainer\sprite_003CEE3C_003CEE50.bin
        INCBIN  build\spritecontainer\sprite_003CEE50_003CF360.bin
        INCBIN  build\spritecontainer\sprite_003CF360_003CF400.bin
        INCBIN  build\spritecontainer\sprite_003CF400_003CF424.bin
        INCBIN  build\spritecontainer\sprite_003CF424_003D009C.bin
        INCBIN  build\spritecontainer\sprite_003D009C_003D01DC.bin
        INCBIN  build\spritecontainer\sprite_003D01DC_003D0220.bin
        INCBIN  build\spritecontainer\sprite_003D0220_003D0C90.bin
        INCBIN  build\spritecontainer\sprite_003D0C90_003D0D80.bin
        INCBIN  build\spritecontainer\sprite_003D0D80_003D0DB4.bin
        INCBIN  build\spritecontainer\sprite_003D0DB4_003D1140.bin
        INCBIN  build\spritecontainer\sprite_003D1140_003D117C.bin
        INCBIN  build\spritecontainer\sprite_003D117C_003D11B0.bin
        INCBIN  build\spritecontainer\sprite_003D11B0_003D1C34.bin
        INCBIN  build\spritecontainer\sprite_003D1C34_003D1D24.bin
        INCBIN  build\spritecontainer\sprite_003D1D24_003D1D58.bin
        INCBIN  build\spritecontainer\sprite_003D1D58_003D227C.bin
        INCBIN  build\spritecontainer\sprite_003D227C_003D22CC.bin
        INCBIN  build\spritecontainer\sprite_003D22CC_003D2310.bin
        INCBIN  build\spritecontainer\sprite_003D2310_003D28C4.bin
        INCBIN  build\spritecontainer\sprite_003D28C4_003D2914.bin
        INCBIN  build\spritecontainer\sprite_003D2914_003D2958.bin
        INCBIN  build\spritecontainer\sprite_003D2958_003D29DC.bin
        INCBIN  build\spritecontainer\sprite_003D29DC_003D2A04.bin
        INCBIN  build\spritecontainer\sprite_003D2A04_003D2A28.bin
        INCBIN  build\spritecontainer\sprite_003D2A28_003D2BA4.bin
        INCBIN  build\spritecontainer\sprite_003D2BA4_003D2BF4.bin
        INCBIN  build\spritecontainer\sprite_003D2BF4_003D2C38.bin
        INCBIN  build\spritecontainer\sprite_003D2C38_003D2F44.bin
        INCBIN  build\spritecontainer\sprite_003D2F44_003D2FE4.bin
        INCBIN  build\spritecontainer\sprite_003D2FE4_003D3008.bin
        INCBIN  build\spritecontainer\sprite_003D3008_003D3778.bin
        INCBIN  build\spritecontainer\sprite_003D3778_003D38B8.bin
        INCBIN  build\spritecontainer\sprite_003D38B8_003D38FC.bin
        INCBIN  build\spritecontainer\sprite_003D38FC_003D3BCC.bin
        INCBIN  build\spritecontainer\sprite_003D3BCC_003D3C1C.bin
        INCBIN  build\spritecontainer\sprite_003D3C1C_003D3C60.bin
        INCBIN  build\spritecontainer\sprite_003D3C60_003D4CF4.bin
        INCBIN  build\spritecontainer\sprite_003D4CF4_003D4D94.bin
        INCBIN  build\spritecontainer\sprite_003D4D94_003D4DB8.bin
        INCBIN  build\spritecontainer\sprite_003D4DB8_003D7B3C.bin
        INCBIN  build\spritecontainer\sprite_003D7B3C_003D7C7C.bin
        INCBIN  build\spritecontainer\sprite_003D7C7C_003D7CC0.bin
        INCBIN  build\spritecontainer\sprite_003D7CC0_003DAE6C.bin
        INCBIN  build\spritecontainer\sprite_003DAE6C_003DAFAC.bin
        INCBIN  build\spritecontainer\sprite_003DAFAC_003DAFF0.bin
        INCBIN  build\spritecontainer\sprite_003DAFF0_003DDFD4.bin
        INCBIN  build\spritecontainer\sprite_003DDFD4_003DE114.bin
        INCBIN  build\spritecontainer\sprite_003DE114_003DE158.bin
        INCBIN  build\spritecontainer\sprite_003DE158_003DE770.bin
        INCBIN  build\spritecontainer\sprite_003DE770_003DE7C0.bin
        INCBIN  build\spritecontainer\sprite_003DE7C0_003DE804.bin
        INCBIN  build\spritecontainer\sprite_003DE804_003DE964.bin
        INCBIN  build\spritecontainer\sprite_003DE964_003DE9B4.bin
        INCBIN  build\spritecontainer\sprite_003DE9B4_003DE9F8.bin
        INCBIN  build\spritecontainer\sprite_003DE9F8_003DED00.bin
        INCBIN  build\spritecontainer\sprite_003DED00_003DEDA0.bin
        INCBIN  build\spritecontainer\sprite_003DEDA0_003DEDC4.bin
        INCBIN  build\spritecontainer\sprite_003DEDC4_003DF96C.bin
        INCBIN  build\spritecontainer\sprite_003DF96C_003DFAAC.bin
        INCBIN  build\spritecontainer\sprite_003DFAAC_003DFAF0.bin
        INCBIN  build\spritecontainer\sprite_003DFAF0_003E0838.bin
        INCBIN  build\spritecontainer\sprite_003E0838_003E0978.bin
        INCBIN  build\spritecontainer\sprite_003E0978_003E09BC.bin
        INCBIN  build\spritecontainer\sprite_003E09BC_003E1378.bin
        INCBIN  build\spritecontainer\sprite_003E1378_003E1468.bin
        INCBIN  build\spritecontainer\sprite_003E1468_003E149C.bin
        INCBIN  build\spritecontainer\sprite_003E149C_003E21EC.bin
        INCBIN  build\spritecontainer\sprite_003E21EC_003E232C.bin
        INCBIN  build\spritecontainer\sprite_003E232C_003E2370.bin
        INCBIN  build\spritecontainer\sprite_003E2370_003E27EC.bin
        INCBIN  build\spritecontainer\sprite_003E27EC_003E288C.bin
        INCBIN  build\spritecontainer\sprite_003E288C_003E28B0.bin
        INCBIN  build\spritecontainer\sprite_003E28B0_003E3328.bin
        INCBIN  build\spritecontainer\sprite_003E3328_003E3468.bin
        INCBIN  build\spritecontainer\sprite_003E3468_003E34AC.bin
        INCBIN  build\spritecontainer\sprite_003E34AC_003E40A4.bin
        INCBIN  build\spritecontainer\sprite_003E40A4_003E41E4.bin
        INCBIN  build\spritecontainer\sprite_003E41E4_003E4228.bin
        INCBIN  build\spritecontainer\sprite_003E4228_003E47B8.bin
        INCBIN  build\spritecontainer\sprite_003E47B8_003E4858.bin
        INCBIN  build\spritecontainer\sprite_003E4858_003E487C.bin
        INCBIN  build\spritecontainer\sprite_003E487C_003E4CF0.bin
        INCBIN  build\spritecontainer\sprite_003E4CF0_003E4D90.bin
        INCBIN  build\spritecontainer\sprite_003E4D90_003E4DB4.bin
        INCBIN  build\spritecontainer\sprite_003E4DB4_003E5244.bin
        INCBIN  build\spritecontainer\sprite_003E5244_003E52E4.bin
        INCBIN  build\spritecontainer\sprite_003E52E4_003E5308.bin
        INCBIN  build\spritecontainer\sprite_003E5308_003E5DD8.bin
        INCBIN  build\spritecontainer\sprite_003E5DD8_003E5F18.bin
        INCBIN  build\spritecontainer\sprite_003E5F18_003E5F5C.bin
        INCBIN  build\spritecontainer\sprite_003E5F5C_003E62F0.bin
        INCBIN  build\spritecontainer\sprite_003E62F0_003E6390.bin
        INCBIN  build\spritecontainer\sprite_003E6390_003E63B4.bin
        INCBIN  build\spritecontainer\sprite_003E63B4_003E7800.bin
        INCBIN  build\spritecontainer\sprite_003E7800_003E78A0.bin
        INCBIN  build\spritecontainer\sprite_003E78A0_003E78C4.bin
        INCBIN  build\spritecontainer\sprite_003E78C4_003EA838.bin
        INCBIN  build\spritecontainer\sprite_003EA838_003EA978.bin
        INCBIN  build\spritecontainer\sprite_003EA978_003EA9BC.bin
        INCBIN  build\spritecontainer\sprite_003EA9BC_003ECB8C.bin
        INCBIN  build\spritecontainer\sprite_003ECB8C_003ECC7C.bin
        INCBIN  build\spritecontainer\sprite_003ECC7C_003ECCB0.bin
        INCBIN  build\spritecontainer\sprite_003ECCB0_003EFA28.bin
        INCBIN  build\spritecontainer\sprite_003EFA28_003EFB68.bin
        INCBIN  build\spritecontainer\sprite_003EFB68_003EFBAC.bin
        INCBIN  build\spritecontainer\sprite_003EFBAC_003F0648.bin
        INCBIN  build\spritecontainer\sprite_003F0648_003F0698.bin
        INCBIN  build\spritecontainer\sprite_003F0698_003F06AC.bin
        INCBIN  build\spritecontainer\sprite_003F06AC_003F28A4.bin
        INCBIN  build\spritecontainer\sprite_003F28A4_003F2994.bin
        INCBIN  build\spritecontainer\sprite_003F2994_003F29C8.bin
        INCBIN  build\spritecontainer\sprite_003F29C8_003F4EE4.bin
        INCBIN  build\spritecontainer\sprite_003F4EE4_003F4F84.bin
        INCBIN  build\spritecontainer\sprite_003F4F84_003F5008.bin
        INCBIN  build\spritecontainer\sprite_003F5008_003F7BE4.bin
        INCBIN  build\spritecontainer\sprite_003F7BE4_003F7D24.bin
        INCBIN  build\spritecontainer\sprite_003F7D24_003F7D68.bin
        INCBIN  build\spritecontainer\sprite_003F7D68_003F8EC0.bin
        INCBIN  build\spritecontainer\sprite_003F8EC0_003F8F60.bin
        INCBIN  build\spritecontainer\sprite_003F8F60_003F8FE4.bin
        INCBIN  build\spritecontainer\sprite_003F8FE4_003FA8B8.bin
        INCBIN  build\spritecontainer\sprite_003FA8B8_003FA930.bin
        INCBIN  build\spritecontainer\sprite_003FA930_003FA994.bin
        INCBIN  build\spritecontainer\sprite_003FA994_003FBDA8.bin
        INCBIN  build\spritecontainer\sprite_003FBDA8_003FBE20.bin
        INCBIN  build\spritecontainer\sprite_003FBE20_003FBE84.bin
        INCBIN  build\spritecontainer\sprite_003FBE84_003FC2CC.bin
        INCBIN  build\spritecontainer\sprite_003FC2CC_003FC36C.bin
        INCBIN  build\spritecontainer\sprite_003FC36C_003FC390.bin
        INCBIN  build\spritecontainer\sprite_003FC390_003FCD10.bin
        INCBIN  build\spritecontainer\sprite_003FCD10_003FCE50.bin
        INCBIN  build\spritecontainer\sprite_003FCE50_003FCE94.bin
        INCBIN  build\spritecontainer\sprite_003FCE94_003FD3E0.bin
        INCBIN  build\spritecontainer\sprite_003FD3E0_003FD480.bin
        INCBIN  build\spritecontainer\sprite_003FD480_003FD4A4.bin
        INCBIN  build\spritecontainer\sprite_003FD4A4_003FE12C.bin
        INCBIN  build\spritecontainer\sprite_003FE12C_003FE26C.bin
        INCBIN  build\spritecontainer\sprite_003FE26C_003FE2B0.bin
        INCBIN  build\spritecontainer\sprite_003FE2B0_003FE800.bin
        INCBIN  build\spritecontainer\sprite_003FE800_003FE8A0.bin
        INCBIN  build\spritecontainer\sprite_003FE8A0_003FE8C4.bin
        INCBIN  build\spritecontainer\sprite_003FE8C4_003FF564.bin
        INCBIN  build\spritecontainer\sprite_003FF564_003FF604.bin
        INCBIN  build\spritecontainer\sprite_003FF604_003FF628.bin
        INCBIN  build\spritecontainer\sprite_003FF628_00401470.bin
        INCBIN  build\spritecontainer\sprite_00401470_004015B0.bin
        INCBIN  build\spritecontainer\sprite_004015B0_004015F4.bin
        INCBIN  build\spritecontainer\sprite_004015F4_00401F44.bin
        INCBIN  build\spritecontainer\sprite_00401F44_00401FBC.bin
        INCBIN  build\spritecontainer\sprite_00401FBC_00401FF0.bin
        INCBIN  build\spritecontainer\sprite_00401FF0_004045CC.bin
        INCBIN  build\spritecontainer\sprite_004045CC_0040470C.bin
        INCBIN  build\spritecontainer\sprite_0040470C_00404750.bin
        INCBIN  build\spritecontainer\sprite_00404750_00404DC4.bin
        INCBIN  build\spritecontainer\sprite_00404DC4_00404E14.bin
        INCBIN  build\spritecontainer\sprite_00404E14_00404E28.bin
        INCBIN  build\spritecontainer\sprite_00404E28_00406340.bin
        INCBIN  build\spritecontainer\sprite_00406340_004063CC.bin
        INCBIN  build\spritecontainer\sprite_004063CC_00406440.bin
        INCBIN  build\spritecontainer\sprite_00406440_00406CE8.bin
        INCBIN  build\spritecontainer\sprite_00406CE8_00406D88.bin
        INCBIN  build\spritecontainer\sprite_00406D88_00406DAC.bin
        INCBIN  build\spritecontainer\sprite_00406DAC_004090AC.bin
        INCBIN  build\spritecontainer\sprite_004090AC_004091EC.bin
        INCBIN  build\spritecontainer\sprite_004091EC_00409230.bin
        INCBIN  build\spritecontainer\sprite_00409230_0040AE68.bin
        INCBIN  build\spritecontainer\sprite_0040AE68_0040AF58.bin
        INCBIN  build\spritecontainer\sprite_0040AF58_0040AF8C.bin
        INCBIN  build\spritecontainer\sprite_0040AF8C_0040D6A0.bin
        INCBIN  build\spritecontainer\sprite_0040D6A0_0040D7E0.bin
        INCBIN  build\spritecontainer\sprite_0040D7E0_0040D824.bin
        INCBIN  build\spritecontainer\sprite_0040D824_0040E078.bin
        INCBIN  build\spritecontainer\sprite_0040E078_0040E0C8.bin
        INCBIN  build\spritecontainer\sprite_0040E0C8_0040E0DC.bin
        INCBIN  build\spritecontainer\sprite_0040E0DC_00410558.bin
        INCBIN  build\spritecontainer\sprite_00410558_00410698.bin
        INCBIN  build\spritecontainer\sprite_00410698_004106DC.bin
        INCBIN  build\spritecontainer\sprite_004106DC_004126BC.bin
        INCBIN  build\spritecontainer\sprite_004126BC_00412748.bin
        INCBIN  build\spritecontainer\sprite_00412748_004127BC.bin
        INCBIN  build\spritecontainer\sprite_004127BC_0041456C.bin
        INCBIN  build\spritecontainer\sprite_0041456C_004146AC.bin
        INCBIN  build\spritecontainer\sprite_004146AC_004146F0.bin
        INCBIN  build\spritecontainer\sprite_004146F0_004151F0.bin
        INCBIN  build\spritecontainer\sprite_004151F0_00415290.bin
        INCBIN  build\spritecontainer\sprite_00415290_004152D4.bin
        INCBIN  build\spritecontainer\sprite_004152D4_00417B2C.bin
        INCBIN  build\spritecontainer\sprite_00417B2C_00417C6C.bin
        INCBIN  build\spritecontainer\sprite_00417C6C_00417CB0.bin
        INCBIN  build\spritecontainer\sprite_00417CB0_0041ADA0.bin
        INCBIN  build\spritecontainer\sprite_0041ADA0_0041AF30.bin
        INCBIN  build\spritecontainer\sprite_0041AF30_0041AF84.bin
        INCBIN  build\spritecontainer\sprite_0041AF84_0041C804.bin
        INCBIN  build\spritecontainer\sprite_0041C804_0041C91C.bin
        INCBIN  build\spritecontainer\sprite_0041C91C_0041C990.bin
        INCBIN  build\spritecontainer\sprite_0041C990_0041CBC8.bin
        INCBIN  build\spritecontainer\sprite_0041CBC8_0041CD08.bin
        INCBIN  build\spritecontainer\sprite_0041CD08_0041CD4C.bin
        INCBIN  build\spritecontainer\sprite_0041CD4C_0041D178.bin
        INCBIN  build\spritecontainer\sprite_0041D178_0041D268.bin
        INCBIN  build\spritecontainer\sprite_0041D268_0041D29C.bin
        INCBIN  build\spritecontainer\sprite_0041D29C_0041D2FC.bin
        INCBIN  build\spritecontainer\sprite_0041D2FC_0041D310.bin
        INCBIN  build\spritecontainer\sprite_0041D310_0041D324.bin
        INCBIN  build\spritecontainer\sprite_0041D324_0041D45C.bin
        INCBIN  build\spritecontainer\sprite_0041D45C_0041D498.bin
        INCBIN  build\spritecontainer\sprite_0041D498_0041D4CC.bin
        INCBIN  build\spritecontainer\sprite_0041D4CC_0041D994.bin
        INCBIN  build\spritecontainer\sprite_0041D994_0041DA0C.bin
        INCBIN  build\spritecontainer\sprite_0041DA0C_0041DA70.bin
        INCBIN  build\spritecontainer\sprite_0041DA70_0041DF80.bin
        INCBIN  build\spritecontainer\sprite_0041DF80_0041E020.bin
        INCBIN  build\spritecontainer\sprite_0041E020_0041E044.bin
        INCBIN  build\spritecontainer\sprite_0041E044_0041EC08.bin
        INCBIN  build\spritecontainer\sprite_0041EC08_0041ED48.bin
        INCBIN  build\spritecontainer\sprite_0041ED48_0041ED8C.bin
        INCBIN  build\spritecontainer\sprite_0041ED8C_0041F70C.bin
        INCBIN  build\spritecontainer\sprite_0041F70C_0041F7FC.bin
        INCBIN  build\spritecontainer\sprite_0041F7FC_0041F830.bin
        INCBIN  build\spritecontainer\sprite_0041F830_004204E0.bin
        INCBIN  build\spritecontainer\sprite_004204E0_00420620.bin
        INCBIN  build\spritecontainer\sprite_00420620_00420664.bin
        INCBIN  build\spritecontainer\sprite_00420664_00421408.bin
        INCBIN  build\spritecontainer\sprite_00421408_00421548.bin
        INCBIN  build\spritecontainer\sprite_00421548_0042158C.bin
        INCBIN  build\spritecontainer\sprite_0042158C_00421864.bin
        INCBIN  build\spritecontainer\sprite_00421864_004218B4.bin
        INCBIN  build\spritecontainer\sprite_004218B4_004218C8.bin
        INCBIN  build\spritecontainer\sprite_004218C8_004223BC.bin
        INCBIN  build\spritecontainer\sprite_004223BC_004224AC.bin
        INCBIN  build\spritecontainer\sprite_004224AC_004224E0.bin
        INCBIN  build\spritecontainer\sprite_004224E0_00423128.bin
        INCBIN  build\spritecontainer\sprite_00423128_00423208.bin
        INCBIN  build\spritecontainer\sprite_00423208_0042327C.bin
        INCBIN  build\spritecontainer\sprite_0042327C_00423C80.bin
        INCBIN  build\spritecontainer\sprite_00423C80_00423DC0.bin
        INCBIN  build\spritecontainer\sprite_00423DC0_00423E04.bin
        INCBIN  build\spritecontainer\sprite_00423E04_00424F9C.bin
        INCBIN  build\spritecontainer\sprite_00424F9C_00425084.bin
        INCBIN  build\spritecontainer\sprite_00425084_00425138.bin
        INCBIN  build\spritecontainer\sprite_00425138_0042573C.bin
        INCBIN  build\spritecontainer\sprite_0042573C_004257A0.bin
        INCBIN  build\spritecontainer\sprite_004257A0_004257F4.bin
        INCBIN  build\spritecontainer\sprite_004257F4_00425A14.bin
        INCBIN  build\spritecontainer\sprite_00425A14_00425A28.bin
        INCBIN  build\spritecontainer\sprite_00425A28_00425A3C.bin
        INCBIN  build\spritecontainer\sprite_00425A3C_00426224.bin
        INCBIN  build\spritecontainer\sprite_00426224_00426260.bin
        INCBIN  build\spritecontainer\sprite_00426260_00426294.bin
        INCBIN  build\spritecontainer\sprite_00426294_004264AC.bin
        INCBIN  build\spritecontainer\sprite_004264AC_004264C0.bin
        INCBIN  build\spritecontainer\sprite_004264C0_004264D4.bin
        INCBIN  build\spritecontainer\sprite_004264D4_004266D0.bin
        INCBIN  build\spritecontainer\sprite_004266D0_004266E4.bin
        INCBIN  build\spritecontainer\sprite_004266E4_004266F8.bin
        INCBIN  build\spritecontainer\sprite_004266F8_004273AC.bin
        INCBIN  build\spritecontainer\sprite_004273AC_0042744C.bin
        INCBIN  build\spritecontainer\sprite_0042744C_00427470.bin
        INCBIN  build\spritecontainer\sprite_00427470_004292A0.bin
        INCBIN  build\spritecontainer\sprite_004292A0_004293E0.bin
        INCBIN  build\spritecontainer\sprite_004293E0_00429424.bin
        INCBIN  build\spritecontainer\sprite_00429424_0042AD24.bin
        INCBIN  build\spritecontainer\sprite_0042AD24_0042AE14.bin
        INCBIN  build\spritecontainer\sprite_0042AE14_0042AE48.bin
        INCBIN  build\spritecontainer\sprite_0042AE48_0042D210.bin
        INCBIN  build\spritecontainer\sprite_0042D210_0042D350.bin
        INCBIN  build\spritecontainer\sprite_0042D350_0042D394.bin
        INCBIN  build\spritecontainer\sprite_0042D394_0042DA54.bin
        INCBIN  build\spritecontainer\sprite_0042DA54_0042DAA4.bin
        INCBIN  build\spritecontainer\sprite_0042DAA4_0042DAB8.bin
        INCBIN  build\spritecontainer\sprite_0042DAB8_0042F6FC.bin
        INCBIN  build\spritecontainer\sprite_0042F6FC_0042F7EC.bin
        INCBIN  build\spritecontainer\sprite_0042F7EC_0042F820.bin
        INCBIN  build\spritecontainer\sprite_0042F820_004315E0.bin
        INCBIN  build\spritecontainer\sprite_004315E0_0043166C.bin
        INCBIN  build\spritecontainer\sprite_0043166C_004316E0.bin
        INCBIN  build\spritecontainer\sprite_004316E0_004321DC.bin
        INCBIN  build\spritecontainer\sprite_004321DC_0043222C.bin
        INCBIN  build\spritecontainer\sprite_0043222C_00432270.bin
        INCBIN  build\spritecontainer\sprite_00432270_00433A18.bin
        INCBIN  build\spritecontainer\sprite_00433A18_00433B58.bin
        INCBIN  build\spritecontainer\sprite_00433B58_00433B9C.bin
        INCBIN  build\spritecontainer\sprite_00433B9C_0043456C.bin
        INCBIN  build\spritecontainer\sprite_0043456C_0043460C.bin
        INCBIN  build\spritecontainer\sprite_0043460C_00434650.bin
        INCBIN  build\spritecontainer\sprite_00434650_00436924.bin
        INCBIN  build\spritecontainer\sprite_00436924_00436A64.bin
        INCBIN  build\spritecontainer\sprite_00436A64_00436AA8.bin
        INCBIN  build\spritecontainer\sprite_00436AA8_00439780.bin
        INCBIN  build\spritecontainer\sprite_00439780_00439910.bin
        INCBIN  build\spritecontainer\sprite_00439910_00439964.bin
        INCBIN  build\spritecontainer\sprite_00439964_0043AF3C.bin
        INCBIN  build\spritecontainer\sprite_0043AF3C_0043B054.bin
        INCBIN  build\spritecontainer\sprite_0043B054_0043B0C8.bin
        INCBIN  build\spritecontainer\sprite_0043B0C8_0043E8BC.bin
        INCBIN  build\spritecontainer\sprite_0043E8BC_0043EA4C.bin
        INCBIN  build\spritecontainer\sprite_0043EA4C_0043EAA0.bin
        INCBIN  build\spritecontainer\sprite_0043EAA0_0043ED80.bin
        INCBIN  build\spritecontainer\sprite_0043ED80_0043EDA8.bin
        INCBIN  build\spritecontainer\sprite_0043EDA8_0043EDBC.bin
        INCBIN  build\spritecontainer\sprite_0043EDBC_0043FBA0.bin
        INCBIN  build\spritecontainer\sprite_0043FBA0_0043FC40.bin
        INCBIN  build\spritecontainer\sprite_0043FC40_0043FC64.bin
        INCBIN  build\spritecontainer\sprite_0043FC64_00441BDC.bin
        INCBIN  build\spritecontainer\sprite_00441BDC_00441D1C.bin
        INCBIN  build\spritecontainer\sprite_00441D1C_00441D60.bin
        INCBIN  build\spritecontainer\sprite_00441D60_00443798.bin
        INCBIN  build\spritecontainer\sprite_00443798_00443888.bin
        INCBIN  build\spritecontainer\sprite_00443888_004438BC.bin
        INCBIN  build\spritecontainer\sprite_004438BC_00445FAC.bin
        INCBIN  build\spritecontainer\sprite_00445FAC_004460EC.bin
        INCBIN  build\spritecontainer\sprite_004460EC_00446130.bin
        INCBIN  build\spritecontainer\sprite_00446130_00446868.bin
        INCBIN  build\spritecontainer\sprite_00446868_004468B8.bin
        INCBIN  build\spritecontainer\sprite_004468B8_004468CC.bin
        INCBIN  build\spritecontainer\sprite_004468CC_004487B0.bin
        INCBIN  build\spritecontainer\sprite_004487B0_004488A0.bin
        INCBIN  build\spritecontainer\sprite_004488A0_004488D4.bin
        INCBIN  build\spritecontainer\sprite_004488D4_0044A798.bin
        INCBIN  build\spritecontainer\sprite_0044A798_0044A824.bin
        INCBIN  build\spritecontainer\sprite_0044A824_0044A898.bin
        INCBIN  build\spritecontainer\sprite_0044A898_0044C1EC.bin
        INCBIN  build\spritecontainer\sprite_0044C1EC_0044C32C.bin
        INCBIN  build\spritecontainer\sprite_0044C32C_0044C370.bin
        INCBIN  build\spritecontainer\sprite_0044C370_0044CE80.bin
        INCBIN  build\spritecontainer\sprite_0044CE80_0044CF20.bin
        INCBIN  build\spritecontainer\sprite_0044CF20_0044CF64.bin
        INCBIN  build\spritecontainer\sprite_0044CF64_00450268.bin
        INCBIN  build\spritecontainer\sprite_00450268_004503F8.bin
        INCBIN  build\spritecontainer\sprite_004503F8_0045044C.bin
        INCBIN  build\spritecontainer\sprite_0045044C_00451228.bin
        INCBIN  build\spritecontainer\sprite_00451228_004512C8.bin
        INCBIN  build\spritecontainer\sprite_004512C8_004512EC.bin
        INCBIN  build\spritecontainer\sprite_004512EC_0045328C.bin
        INCBIN  build\spritecontainer\sprite_0045328C_004533CC.bin
        INCBIN  build\spritecontainer\sprite_004533CC_00453410.bin
        INCBIN  build\spritecontainer\sprite_00453410_00454E54.bin
        INCBIN  build\spritecontainer\sprite_00454E54_00454F44.bin
        INCBIN  build\spritecontainer\sprite_00454F44_00454F78.bin
        INCBIN  build\spritecontainer\sprite_00454F78_00457634.bin
        INCBIN  build\spritecontainer\sprite_00457634_00457774.bin
        INCBIN  build\spritecontainer\sprite_00457774_004577B8.bin
        INCBIN  build\spritecontainer\sprite_004577B8_00457EE0.bin
        INCBIN  build\spritecontainer\sprite_00457EE0_00457F30.bin
        INCBIN  build\spritecontainer\sprite_00457F30_00457F44.bin
        INCBIN  build\spritecontainer\sprite_00457F44_00459DC4.bin
        INCBIN  build\spritecontainer\sprite_00459DC4_00459EB4.bin
        INCBIN  build\spritecontainer\sprite_00459EB4_00459EE8.bin
        INCBIN  build\spritecontainer\sprite_00459EE8_0045BD60.bin
        INCBIN  build\spritecontainer\sprite_0045BD60_0045BDEC.bin
        INCBIN  build\spritecontainer\sprite_0045BDEC_0045BE60.bin
        INCBIN  build\spritecontainer\sprite_0045BE60_0045D744.bin
        INCBIN  build\spritecontainer\sprite_0045D744_0045D884.bin
        INCBIN  build\spritecontainer\sprite_0045D884_0045D8C8.bin
        INCBIN  build\spritecontainer\sprite_0045D8C8_0045FE58.bin
        INCBIN  build\spritecontainer\sprite_0045FE58_0045FF98.bin
        INCBIN  build\spritecontainer\sprite_0045FF98_0045FFDC.bin
        INCBIN  build\spritecontainer\sprite_0045FFDC_00460AC4.bin
        INCBIN  build\spritecontainer\sprite_00460AC4_00460B64.bin
        INCBIN  build\spritecontainer\sprite_00460B64_00460BA8.bin
        INCBIN  build\spritecontainer\sprite_00460BA8_00463CE4.bin
        INCBIN  build\spritecontainer\sprite_00463CE4_00463E74.bin
        INCBIN  build\spritecontainer\sprite_00463E74_00463EC8.bin
        INCBIN  build\spritecontainer\sprite_00463EC8_0046651C.bin
        INCBIN  build\spritecontainer\sprite_0046651C_0046665C.bin
        INCBIN  build\spritecontainer\sprite_0046665C_004666A0.bin
        INCBIN  build\spritecontainer\sprite_004666A0_00467D40.bin
        INCBIN  build\spritecontainer\sprite_00467D40_00467E58.bin
        INCBIN  build\spritecontainer\sprite_00467E58_00467ECC.bin
        INCBIN  build\spritecontainer\sprite_00467ECC_0046BA18.bin
        INCBIN  build\spritecontainer\sprite_0046BA18_0046BBA8.bin
        INCBIN  build\spritecontainer\sprite_0046BBA8_0046BBFC.bin
        INCBIN  build\spritecontainer\sprite_0046BBFC_0046C788.bin
        INCBIN  build\spritecontainer\sprite_0046C788_0046C7D8.bin
        INCBIN  build\spritecontainer\sprite_0046C7D8_0046C81C.bin
        INCBIN  build\spritecontainer\sprite_0046C81C_0046C948.bin
        INCBIN  build\spritecontainer\sprite_0046C948_0046C984.bin
        INCBIN  build\spritecontainer\sprite_0046C984_0046C9B8.bin
        INCBIN  build\spritecontainer\sprite_0046C9B8_0046CBD8.bin
        INCBIN  build\spritecontainer\sprite_0046CBD8_0046CC28.bin
        INCBIN  build\spritecontainer\sprite_0046CC28_0046CC6C.bin
        INCBIN  build\spritecontainer\sprite_0046CC6C_0046D008.bin
        INCBIN  build\spritecontainer\sprite_0046D008_0046D058.bin
        INCBIN  build\spritecontainer\sprite_0046D058_0046D09C.bin
        INCBIN  build\spritecontainer\sprite_0046D09C_0046D258.bin
        INCBIN  build\spritecontainer\sprite_0046D258_0046D2A8.bin
        INCBIN  build\spritecontainer\sprite_0046D2A8_0046D2EC.bin
|unk_0846D2EC|
        INCBIN  build\spritecontainer\sprite_0046D2EC_0046D354.bin
        INCBIN  build\spritecontainer\sprite_0046D354_0046D37C.bin
        INCBIN  build\spritecontainer\sprite_0046D37C_0046E3B4.bin
        INCBIN  build\spritecontainer\sprite_0046E3B4_0046E454.bin
        INCBIN  build\spritecontainer\sprite_0046E454_0046E478.bin
        INCBIN  build\spritecontainer\sprite_0046E478_00470954.bin
        INCBIN  build\spritecontainer\sprite_00470954_00470A94.bin
        INCBIN  build\spritecontainer\sprite_00470A94_00470AD8.bin
        INCBIN  build\spritecontainer\sprite_00470AD8_00473334.bin
        INCBIN  build\spritecontainer\sprite_00473334_00473474.bin
        INCBIN  build\spritecontainer\sprite_00473474_004734B8.bin
        INCBIN  build\spritecontainer\sprite_004734B8_00474FC8.bin
        INCBIN  build\spritecontainer\sprite_00474FC8_004750B8.bin
        INCBIN  build\spritecontainer\sprite_004750B8_004750EC.bin
        INCBIN  build\spritecontainer\sprite_004750EC_0047553C.bin
        INCBIN  build\spritecontainer\sprite_0047553C_004755DC.bin
        INCBIN  build\spritecontainer\sprite_004755DC_00475600.bin
        INCBIN  build\spritecontainer\sprite_00475600_004760C0.bin
        INCBIN  build\spritecontainer\sprite_004760C0_00476200.bin
        INCBIN  build\spritecontainer\sprite_00476200_00476244.bin
        INCBIN  build\spritecontainer\sprite_00476244_00477038.bin
        INCBIN  build\spritecontainer\sprite_00477038_00477178.bin
        INCBIN  build\spritecontainer\sprite_00477178_004771BC.bin
        INCBIN  build\spritecontainer\sprite_004771BC_00477A94.bin
        INCBIN  build\spritecontainer\sprite_00477A94_00477B84.bin
        INCBIN  build\spritecontainer\sprite_00477B84_00477BB8.bin
        INCBIN  build\spritecontainer\sprite_00477BB8_00477DD0.bin
        INCBIN  build\spritecontainer\sprite_00477DD0_00477F10.bin
        INCBIN  build\spritecontainer\sprite_00477F10_00477F54.bin
        INCBIN  build\spritecontainer\sprite_00477F54_00478550.bin
        INCBIN  build\spritecontainer\sprite_00478550_004785F0.bin
        INCBIN  build\spritecontainer\sprite_004785F0_00478614.bin
        INCBIN  build\spritecontainer\sprite_00478614_004791E0.bin
        INCBIN  build\spritecontainer\sprite_004791E0_00479320.bin
        INCBIN  build\spritecontainer\sprite_00479320_00479364.bin
        INCBIN  build\spritecontainer\sprite_00479364_00479868.bin
        INCBIN  build\spritecontainer\sprite_00479868_00479908.bin
        INCBIN  build\spritecontainer\sprite_00479908_0047992C.bin
        INCBIN  build\spritecontainer\sprite_0047992C_00479BDC.bin
        INCBIN  build\spritecontainer\sprite_00479BDC_00479C04.bin
        INCBIN  build\spritecontainer\sprite_00479C04_00479C28.bin
        INCBIN  build\spritecontainer\sprite_00479C28_00479F88.bin
        INCBIN  build\spritecontainer\sprite_00479F88_00479FD8.bin
        INCBIN  build\spritecontainer\sprite_00479FD8_0047A01C.bin
        INCBIN  build\spritecontainer\sprite_0047A01C_0047A4D0.bin
        INCBIN  build\spritecontainer\sprite_0047A4D0_0047A570.bin
        INCBIN  build\spritecontainer\sprite_0047A570_0047A594.bin
        INCBIN  build\spritecontainer\sprite_0047A594_0047B0C4.bin
        INCBIN  build\spritecontainer\sprite_0047B0C4_0047B204.bin
        INCBIN  build\spritecontainer\sprite_0047B204_0047B248.bin
        INCBIN  build\spritecontainer\sprite_0047B248_0047B7D4.bin
        INCBIN  build\spritecontainer\sprite_0047B7D4_0047B874.bin
        INCBIN  build\spritecontainer\sprite_0047B874_0047B898.bin
        INCBIN  build\spritecontainer\sprite_0047B898_0047BDC4.bin
        INCBIN  build\spritecontainer\sprite_0047BDC4_0047BE64.bin
        INCBIN  build\spritecontainer\sprite_0047BE64_0047BE88.bin
        INCBIN  build\spritecontainer\sprite_0047BE88_0047CAA0.bin
        INCBIN  build\spritecontainer\sprite_0047CAA0_0047CBE0.bin
        INCBIN  build\spritecontainer\sprite_0047CBE0_0047CC24.bin
        INCBIN  build\spritecontainer\sprite_0047CC24_0047D9E8.bin
        INCBIN  build\spritecontainer\sprite_0047D9E8_0047DB28.bin
        INCBIN  build\spritecontainer\sprite_0047DB28_0047DB6C.bin
        INCBIN  build\spritecontainer\sprite_0047DB6C_0047DE2C.bin
        INCBIN  build\spritecontainer\sprite_0047DE2C_0047DE7C.bin
        INCBIN  build\spritecontainer\sprite_0047DE7C_0047DE90.bin
        INCBIN  build\spritecontainer\sprite_0047DE90_0047E82C.bin
        INCBIN  build\spritecontainer\sprite_0047E82C_0047E91C.bin
        INCBIN  build\spritecontainer\sprite_0047E91C_0047E950.bin
        INCBIN  build\spritecontainer\sprite_0047E950_0047EEE0.bin
        INCBIN  build\spritecontainer\sprite_0047EEE0_0047EF80.bin
        INCBIN  build\spritecontainer\sprite_0047EF80_0047EFA4.bin
        INCBIN  build\spritecontainer\sprite_0047EFA4_0047FCD8.bin
        INCBIN  build\spritecontainer\sprite_0047FCD8_0047FE18.bin
        INCBIN  build\spritecontainer\sprite_0047FE18_0047FE5C.bin
        INCBIN  build\spritecontainer\sprite_0047FE5C_00480F40.bin
        INCBIN  build\spritecontainer\sprite_00480F40_00481080.bin
        INCBIN  build\spritecontainer\sprite_00481080_004810C4.bin
        INCBIN  build\spritecontainer\sprite_004810C4_00481F90.bin
        INCBIN  build\spritecontainer\sprite_00481F90_004820D0.bin
        INCBIN  build\spritecontainer\sprite_004820D0_00482114.bin
        INCBIN  build\spritecontainer\sprite_00482114_004825BC.bin
        INCBIN  build\spritecontainer\sprite_004825BC_0048260C.bin
        INCBIN  build\spritecontainer\sprite_0048260C_00482620.bin
        INCBIN  build\spritecontainer\sprite_00482620_0048336C.bin
        INCBIN  build\spritecontainer\sprite_0048336C_0048345C.bin
        INCBIN  build\spritecontainer\sprite_0048345C_00483490.bin
        INCBIN  build\spritecontainer\sprite_00483490_00483B78.bin
        INCBIN  build\spritecontainer\sprite_00483B78_00483C18.bin
        INCBIN  build\spritecontainer\sprite_00483C18_00483C3C.bin
        INCBIN  build\spritecontainer\sprite_00483C3C_004850B4.bin
        INCBIN  build\spritecontainer\sprite_004850B4_00485154.bin
        INCBIN  build\spritecontainer\sprite_00485154_00485178.bin
        INCBIN  build\spritecontainer\sprite_00485178_00488310.bin
        INCBIN  build\spritecontainer\sprite_00488310_00488450.bin
        INCBIN  build\spritecontainer\sprite_00488450_00488494.bin
        INCBIN  build\spritecontainer\sprite_00488494_0048B594.bin
        INCBIN  build\spritecontainer\sprite_0048B594_0048B6D4.bin
        INCBIN  build\spritecontainer\sprite_0048B6D4_0048B718.bin
        INCBIN  build\spritecontainer\sprite_0048B718_0048C328.bin
        INCBIN  build\spritecontainer\sprite_0048C328_0048C378.bin
        INCBIN  build\spritecontainer\sprite_0048C378_0048C38C.bin
        INCBIN  build\spritecontainer\sprite_0048C38C_0048ED34.bin
        INCBIN  build\spritecontainer\sprite_0048ED34_0048EE24.bin
        INCBIN  build\spritecontainer\sprite_0048EE24_0048EE58.bin
        INCBIN  build\spritecontainer\sprite_0048EE58_0048FED8.bin
        INCBIN  build\spritecontainer\sprite_0048FED8_0048FF78.bin
        INCBIN  build\spritecontainer\sprite_0048FF78_0048FFBC.bin
        INCBIN  build\spritecontainer\sprite_0048FFBC_00490E74.bin
        INCBIN  build\spritecontainer\sprite_00490E74_00490EC4.bin
        INCBIN  build\spritecontainer\sprite_00490EC4_00490F08.bin
        INCBIN  build\spritecontainer\sprite_00490F08_004919C0.bin
        INCBIN  build\spritecontainer\sprite_004919C0_004919E8.bin
        INCBIN  build\spritecontainer\sprite_004919E8_00491A0C.bin
        INCBIN  build\spritecontainer\sprite_00491A0C_00495430.bin
        INCBIN  build\spritecontainer\sprite_00495430_00495520.bin
        INCBIN  build\spritecontainer\sprite_00495520_004955E4.bin
        INCBIN  build\spritecontainer\sprite_004955E4_00496920.bin
        INCBIN  build\spritecontainer\sprite_00496920_00496970.bin
        INCBIN  build\spritecontainer\sprite_00496970_004969B4.bin
        INCBIN  build\spritecontainer\sprite_004969B4_00496B80.bin
        INCBIN  build\spritecontainer\sprite_00496B80_00496B94.bin
        INCBIN  build\spritecontainer\sprite_00496B94_00496BA8.bin
        INCBIN  build\spritecontainer\sprite_00496BA8_00496BD0.bin
        INCBIN  build\spritecontainer\sprite_00496BD0_00496BF4.bin
        INCBIN  build\spritecontainer\sprite_00496BF4_00497378.bin
        INCBIN  build\spritecontainer\sprite_00497378_004973C8.bin
        INCBIN  build\spritecontainer\sprite_004973C8_0049740C.bin
        INCBIN  build\spritecontainer\sprite_0049740C_004977B4.bin
        INCBIN  build\spritecontainer\sprite_004977B4_00497854.bin
        INCBIN  build\spritecontainer\sprite_00497854_00497878.bin
        INCBIN  build\spritecontainer\sprite_00497878_004987C0.bin
        INCBIN  build\spritecontainer\sprite_004987C0_00498900.bin
        INCBIN  build\spritecontainer\sprite_00498900_00498944.bin
        INCBIN  build\spritecontainer\sprite_00498944_00499544.bin
        INCBIN  build\spritecontainer\sprite_00499544_00499634.bin
        INCBIN  build\spritecontainer\sprite_00499634_00499668.bin
        INCBIN  build\spritecontainer\sprite_00499668_00499B54.bin
        INCBIN  build\spritecontainer\sprite_00499B54_00499BF4.bin
        INCBIN  build\spritecontainer\sprite_00499BF4_00499C18.bin
        INCBIN  build\spritecontainer\sprite_00499C18_0049A7B0.bin
        INCBIN  build\spritecontainer\sprite_0049A7B0_0049A8F0.bin
        INCBIN  build\spritecontainer\sprite_0049A8F0_0049A934.bin
        INCBIN  build\spritecontainer\sprite_0049A934_0049ABFC.bin
        INCBIN  build\spritecontainer\sprite_0049ABFC_0049AC9C.bin
        INCBIN  build\spritecontainer\sprite_0049AC9C_0049ACC0.bin
        INCBIN  build\spritecontainer\sprite_0049ACC0_0049B1D0.bin
        INCBIN  build\spritecontainer\sprite_0049B1D0_0049B220.bin
        INCBIN  build\spritecontainer\sprite_0049B220_0049B264.bin
        INCBIN  build\spritecontainer\sprite_0049B264_0049CA84.bin
        INCBIN  build\spritecontainer\sprite_0049CA84_0049CB24.bin
        INCBIN  build\spritecontainer\sprite_0049CB24_0049CB48.bin
        INCBIN  build\spritecontainer\sprite_0049CB48_004A0000.bin
        INCBIN  build\spritecontainer\sprite_004A0000_004A0140.bin
        INCBIN  build\spritecontainer\sprite_004A0140_004A0184.bin
        INCBIN  build\spritecontainer\sprite_004A0184_004A3988.bin
        INCBIN  build\spritecontainer\sprite_004A3988_004A3AC8.bin
        INCBIN  build\spritecontainer\sprite_004A3AC8_004A3B0C.bin
        INCBIN  build\spritecontainer\sprite_004A3B0C_004A6080.bin
        INCBIN  build\spritecontainer\sprite_004A6080_004A61C0.bin
        INCBIN  build\spritecontainer\sprite_004A61C0_004A6204.bin
        INCBIN  build\spritecontainer\sprite_004A6204_004A8E80.bin
        INCBIN  build\spritecontainer\sprite_004A8E80_004A8FC0.bin
        INCBIN  build\spritecontainer\sprite_004A8FC0_004A9004.bin
        INCBIN  build\spritecontainer\sprite_004A9004_004A94CC.bin
        INCBIN  build\spritecontainer\sprite_004A94CC_004A956C.bin
        INCBIN  build\spritecontainer\sprite_004A956C_004A9590.bin
        INCBIN  build\spritecontainer\sprite_004A9590_004AA114.bin
        INCBIN  build\spritecontainer\sprite_004AA114_004AA254.bin
        INCBIN  build\spritecontainer\sprite_004AA254_004AA298.bin
        INCBIN  build\spritecontainer\sprite_004AA298_004AA560.bin
        INCBIN  build\spritecontainer\sprite_004AA560_004AA600.bin
        INCBIN  build\spritecontainer\sprite_004AA600_004AA624.bin
        INCBIN  build\spritecontainer\sprite_004AA624_004AAA80.bin
        INCBIN  build\spritecontainer\sprite_004AAA80_004AAB20.bin
        INCBIN  build\spritecontainer\sprite_004AAB20_004AAB44.bin
        INCBIN  build\spritecontainer\sprite_004AAB44_004ABCC8.bin
        INCBIN  build\spritecontainer\sprite_004ABCC8_004ABE08.bin
        INCBIN  build\spritecontainer\sprite_004ABE08_004ABE4C.bin
        INCBIN  build\spritecontainer\sprite_004ABE4C_004AC388.bin
        INCBIN  build\spritecontainer\sprite_004AC388_004AC428.bin
        INCBIN  build\spritecontainer\sprite_004AC428_004AC44C.bin
        INCBIN  build\spritecontainer\sprite_004AC44C_004AD0B8.bin
        INCBIN  build\spritecontainer\sprite_004AD0B8_004AD1F8.bin
        INCBIN  build\spritecontainer\sprite_004AD1F8_004AD23C.bin
        INCBIN  build\spritecontainer\sprite_004AD23C_004AD77C.bin
        INCBIN  build\spritecontainer\sprite_004AD77C_004AD81C.bin
        INCBIN  build\spritecontainer\sprite_004AD81C_004AD840.bin
        INCBIN  build\spritecontainer\sprite_004AD840_004ADC4C.bin
        INCBIN  build\spritecontainer\sprite_004ADC4C_004ADCEC.bin
        INCBIN  build\spritecontainer\sprite_004ADCEC_004ADD30.bin
|unk_084ADD30|
        INCBIN  build\spritecontainer\sprite_004ADD30_004ADD90.bin
        INCBIN  build\spritecontainer\sprite_004ADD90_004ADDD8.bin
        INCBIN  build\spritecontainer\sprite_004ADDD8_004ADE90.bin
        INCBIN  build\spritecontainer\sprite_004ADE90_004ADF08.bin
        INCBIN  build\spritecontainer\sprite_004ADF08_004ADF6C.bin
        INCBIN  build\spritecontainer\sprite_004ADF6C_004AE428.bin
        INCBIN  build\spritecontainer\sprite_004AE428_004AE4C8.bin
        INCBIN  build\spritecontainer\sprite_004AE4C8_004AE4EC.bin
        INCBIN  build\spritecontainer\sprite_004AE4EC_004AF044.bin
        INCBIN  build\spritecontainer\sprite_004AF044_004AF184.bin
        INCBIN  build\spritecontainer\sprite_004AF184_004AF1C8.bin
        INCBIN  build\spritecontainer\sprite_004AF1C8_004AF694.bin
        INCBIN  build\spritecontainer\sprite_004AF694_004AF734.bin
        INCBIN  build\spritecontainer\sprite_004AF734_004AF758.bin
        INCBIN  build\spritecontainer\sprite_004AF758_004AF898.bin
        INCBIN  build\spritecontainer\sprite_004AF898_004AF938.bin
        INCBIN  build\spritecontainer\sprite_004AF938_004AF97C.bin
        INCBIN  build\spritecontainer\sprite_004AF97C_004AFA60.bin
        INCBIN  build\spritecontainer\sprite_004AFA60_004AFB00.bin
        INCBIN  build\spritecontainer\sprite_004AFB00_004AFB44.bin
        INCBIN  build\spritecontainer\sprite_004AFB44_004B010C.bin
        INCBIN  build\spritecontainer\sprite_004B010C_004B01AC.bin
        INCBIN  build\spritecontainer\sprite_004B01AC_004B01D0.bin
        INCBIN  build\spritecontainer\sprite_004B01D0_004B0F54.bin
        INCBIN  build\spritecontainer\sprite_004B0F54_004B1094.bin
        INCBIN  build\spritecontainer\sprite_004B1094_004B10D8.bin
        INCBIN  build\spritecontainer\sprite_004B10D8_004B19CC.bin
        INCBIN  build\spritecontainer\sprite_004B19CC_004B1ABC.bin
        INCBIN  build\spritecontainer\sprite_004B1ABC_004B1AF0.bin
        INCBIN  build\spritecontainer\sprite_004B1AF0_004B1B24.bin
        INCBIN  build\spritecontainer\sprite_004B1B24_004B1B74.bin
        INCBIN  build\spritecontainer\sprite_004B1B74_004B1BB8.bin
        INCBIN  build\spritecontainer\sprite_004B1BB8_004B1BCC.bin
        INCBIN  build\spritecontainer\sprite_004B1BCC_004B1BE0.bin
        INCBIN  build\spritecontainer\sprite_004B1BE0_004B21F4.bin
        INCBIN  build\spritecontainer\sprite_004B21F4_004B226C.bin
        INCBIN  build\spritecontainer\sprite_004B226C_004B22D0.bin
        INCBIN  build\spritecontainer\sprite_004B22D0_004B2F1C.bin
        INCBIN  build\spritecontainer\sprite_004B2F1C_004B305C.bin
        INCBIN  build\spritecontainer\sprite_004B305C_004B30A0.bin
        INCBIN  build\spritecontainer\sprite_004B30A0_004B4390.bin
        INCBIN  build\spritecontainer\sprite_004B4390_004B44D0.bin
        INCBIN  build\spritecontainer\sprite_004B44D0_004B4514.bin
        INCBIN  build\spritecontainer\sprite_004B4514_004B5290.bin
        INCBIN  build\spritecontainer\sprite_004B5290_004B5380.bin
        INCBIN  build\spritecontainer\sprite_004B5380_004B53B4.bin
        INCBIN  build\spritecontainer\sprite_004B53B4_004B542C.bin
        INCBIN  build\spritecontainer\sprite_004B542C_004B5490.bin
        INCBIN  build\spritecontainer\sprite_004B5490_004B7E40.bin
        INCBIN  build\spritecontainer\sprite_004B7E40_004B7F80.bin
        INCBIN  build\spritecontainer\sprite_004B7F80_004B7FC4.bin
        INCBIN  build\spritecontainer\sprite_004B7FC4_004B88DC.bin
        INCBIN  build\spritecontainer\sprite_004B88DC_004B8904.bin
        INCBIN  build\spritecontainer\sprite_004B8904_004B8928.bin
        INCBIN  build\spritecontainer\sprite_004B8928_004B8E14.bin
        INCBIN  build\spritecontainer\sprite_004B8E14_004B8EB4.bin
        INCBIN  build\spritecontainer\sprite_004B8EB4_004B8ED8.bin
        INCBIN  build\spritecontainer\sprite_004B8ED8_004B9AC0.bin
        INCBIN  build\spritecontainer\sprite_004B9AC0_004B9C00.bin
        INCBIN  build\spritecontainer\sprite_004B9C00_004B9C44.bin
        INCBIN  build\spritecontainer\sprite_004B9C44_004BA138.bin
        INCBIN  build\spritecontainer\sprite_004BA138_004BA1D8.bin
        INCBIN  build\spritecontainer\sprite_004BA1D8_004BA1FC.bin
|unk_084BA1FC|
        INCBIN  build\spritecontainer\sprite_004BA1FC_004BA3B4.bin
        INCBIN  build\spritecontainer\sprite_004BA3B4_004BA404.bin
        INCBIN  build\spritecontainer\sprite_004BA404_004BA9C8.bin
        INCBIN  build\spritecontainer\sprite_004BA9C8_004BAA68.bin
        INCBIN  build\spritecontainer\sprite_004BAA68_004BAA8C.bin
        INCBIN  build\spritecontainer\sprite_004BAA8C_004BB814.bin
        INCBIN  build\spritecontainer\sprite_004BB814_004BB954.bin
        INCBIN  build\spritecontainer\sprite_004BB954_004BB998.bin
        INCBIN  build\spritecontainer\sprite_004BB998_004BC7AC.bin
        INCBIN  build\spritecontainer\sprite_004BC7AC_004BC8EC.bin
        INCBIN  build\spritecontainer\sprite_004BC8EC_004BC930.bin
        INCBIN  build\spritecontainer\sprite_004BC930_004BD3A0.bin
        INCBIN  build\spritecontainer\sprite_004BD3A0_004BD490.bin
        INCBIN  build\spritecontainer\sprite_004BD490_004BD4C4.bin
        INCBIN  build\spritecontainer\sprite_004BD4C4_004BE404.bin
        INCBIN  build\spritecontainer\sprite_004BE404_004BE544.bin
        INCBIN  build\spritecontainer\sprite_004BE544_004BE588.bin
        INCBIN  build\spritecontainer\sprite_004BE588_004BF448.bin
        INCBIN  build\spritecontainer\sprite_004BF448_004BF588.bin
        INCBIN  build\spritecontainer\sprite_004BF588_004BF5CC.bin
        INCBIN  build\spritecontainer\sprite_004BF5CC_004C04FC.bin
        INCBIN  build\spritecontainer\sprite_004C04FC_004C063C.bin
        INCBIN  build\spritecontainer\sprite_004C063C_004C0680.bin
        INCBIN  build\spritecontainer\sprite_004C0680_004C09C4.bin
        INCBIN  build\spritecontainer\sprite_004C09C4_004C0A14.bin
        INCBIN  build\spritecontainer\sprite_004C0A14_004C0A28.bin
        INCBIN  build\spritecontainer\sprite_004C0A28_004C149C.bin
        INCBIN  build\spritecontainer\sprite_004C149C_004C158C.bin
        INCBIN  build\spritecontainer\sprite_004C158C_004C15C0.bin
        INCBIN  build\spritecontainer\sprite_004C15C0_004C1C84.bin
        INCBIN  build\spritecontainer\sprite_004C1C84_004C1D24.bin
        INCBIN  build\spritecontainer\sprite_004C1D24_004C1D48.bin
        INCBIN  build\spritecontainer\sprite_004C1D48_004C1F84.bin
        INCBIN  build\spritecontainer\sprite_004C1F84_004C1FAC.bin
        INCBIN  build\spritecontainer\sprite_004C1FAC_004C1FD0.bin
        INCBIN  build\spritecontainer\sprite_004C1FD0_004C29DC.bin
        INCBIN  build\spritecontainer\sprite_004C29DC_004C2ACC.bin
        INCBIN  build\spritecontainer\sprite_004C2ACC_004C2B00.bin
        INCBIN  build\spritecontainer\sprite_004C2B00_004C3648.bin
        INCBIN  build\spritecontainer\sprite_004C3648_004C3788.bin
        INCBIN  build\spritecontainer\sprite_004C3788_004C37CC.bin
        INCBIN  build\spritecontainer\sprite_004C37CC_004C406C.bin
        INCBIN  build\spritecontainer\sprite_004C406C_004C41AC.bin
        INCBIN  build\spritecontainer\sprite_004C41AC_004C41F0.bin
        INCBIN  build\spritecontainer\sprite_004C41F0_004C4644.bin
        INCBIN  build\spritecontainer\sprite_004C4644_004C46E4.bin
        INCBIN  build\spritecontainer\sprite_004C46E4_004C4728.bin
        INCBIN  build\spritecontainer\sprite_004C4728_004C5250.bin
        INCBIN  build\spritecontainer\sprite_004C5250_004C5340.bin
        INCBIN  build\spritecontainer\sprite_004C5340_004C5374.bin
        INCBIN  build\spritecontainer\sprite_004C5374_004C625C.bin
        INCBIN  build\spritecontainer\sprite_004C625C_004C639C.bin
        INCBIN  build\spritecontainer\sprite_004C639C_004C63E0.bin
        INCBIN  build\spritecontainer\sprite_004C63E0_004C6670.bin
        INCBIN  build\spritecontainer\sprite_004C6670_004C6698.bin
        INCBIN  build\spritecontainer\sprite_004C6698_004C66BC.bin
        INCBIN  build\spritecontainer\sprite_004C66BC_004C6AA0.bin
        INCBIN  build\spritecontainer\sprite_004C6AA0_004C6ADC.bin
        INCBIN  build\spritecontainer\sprite_004C6ADC_004C6B10.bin
        INCBIN  build\spritecontainer\sprite_004C6B10_004C6D3C.bin
        INCBIN  build\spritecontainer\sprite_004C6D3C_004C6D64.bin
        INCBIN  build\spritecontainer\sprite_004C6D64_004C6D88.bin
        INCBIN  build\spritecontainer\sprite_004C6D88_004C70F4.bin
        INCBIN  build\spritecontainer\sprite_004C70F4_004C7130.bin
        INCBIN  build\spritecontainer\sprite_004C7130_004C7164.bin
        INCBIN  build\spritecontainer\sprite_004C7164_004C7560.bin
        INCBIN  build\spritecontainer\sprite_004C7560_004C7600.bin
        INCBIN  build\spritecontainer\sprite_004C7600_004C7624.bin
        INCBIN  build\spritecontainer\sprite_004C7624_004C7F64.bin
        INCBIN  build\spritecontainer\sprite_004C7F64_004C80A4.bin
        INCBIN  build\spritecontainer\sprite_004C80A4_004C80E8.bin
        INCBIN  build\spritecontainer\sprite_004C80E8_004C8A78.bin
        INCBIN  build\spritecontainer\sprite_004C8A78_004C8BB8.bin
        INCBIN  build\spritecontainer\sprite_004C8BB8_004C8BFC.bin
        INCBIN  build\spritecontainer\sprite_004C8BFC_004C9310.bin
        INCBIN  build\spritecontainer\sprite_004C9310_004C9400.bin
        INCBIN  build\spritecontainer\sprite_004C9400_004C9434.bin
        INCBIN  build\spritecontainer\sprite_004C9434_004C97F0.bin
        INCBIN  build\spritecontainer\sprite_004C97F0_004C9890.bin
        INCBIN  build\spritecontainer\sprite_004C9890_004C98B4.bin
        INCBIN  build\spritecontainer\sprite_004C98B4_004C9EF8.bin
        INCBIN  build\spritecontainer\sprite_004C9EF8_004CA038.bin
        INCBIN  build\spritecontainer\sprite_004CA038_004CA07C.bin
        INCBIN  build\spritecontainer\sprite_004CA07C_004CA7DC.bin
        INCBIN  build\spritecontainer\sprite_004CA7DC_004CA8CC.bin
        INCBIN  build\spritecontainer\sprite_004CA8CC_004CA900.bin
        INCBIN  build\spritecontainer\sprite_004CA900_004CAD30.bin
        INCBIN  build\spritecontainer\sprite_004CAD30_004CADD0.bin
        INCBIN  build\spritecontainer\sprite_004CADD0_004CADF4.bin
        INCBIN  build\spritecontainer\sprite_004CADF4_004CB7D8.bin
        INCBIN  build\spritecontainer\sprite_004CB7D8_004CB918.bin
        INCBIN  build\spritecontainer\sprite_004CB918_004CB95C.bin
        INCBIN  build\spritecontainer\sprite_004CB95C_004CC3D8.bin
        INCBIN  build\spritecontainer\sprite_004CC3D8_004CC518.bin
        INCBIN  build\spritecontainer\sprite_004CC518_004CC55C.bin
        INCBIN  build\spritecontainer\sprite_004CC55C_004CCD60.bin
        INCBIN  build\spritecontainer\sprite_004CCD60_004CCE50.bin
        INCBIN  build\spritecontainer\sprite_004CCE50_004CCE84.bin
        INCBIN  build\spritecontainer\sprite_004CCE84_004CDAD4.bin
        INCBIN  build\spritecontainer\sprite_004CDAD4_004CDC14.bin
        INCBIN  build\spritecontainer\sprite_004CDC14_004CDC58.bin
        INCBIN  build\spritecontainer\sprite_004CDC58_004CE854.bin
        INCBIN  build\spritecontainer\sprite_004CE854_004CE994.bin
        INCBIN  build\spritecontainer\sprite_004CE994_004CE9D8.bin
        INCBIN  build\spritecontainer\sprite_004CE9D8_004CEC20.bin
        INCBIN  build\spritecontainer\sprite_004CEC20_004CEC70.bin
        INCBIN  build\spritecontainer\sprite_004CEC70_004CEC84.bin
        INCBIN  build\spritecontainer\sprite_004CEC84_004CF318.bin
        INCBIN  build\spritecontainer\sprite_004CF318_004CF3F4.bin
        INCBIN  build\spritecontainer\sprite_004CF3F4_004CF4A8.bin
        INCBIN  build\spritecontainer\sprite_004CF4A8_004CFCA4.bin
        INCBIN  build\spritecontainer\sprite_004CFCA4_004CFD94.bin
        INCBIN  build\spritecontainer\sprite_004CFD94_004CFDC8.bin
        INCBIN  build\spritecontainer\sprite_004CFDC8_004D03E4.bin
        INCBIN  build\spritecontainer\sprite_004D03E4_004D04C0.bin
        INCBIN  build\spritecontainer\sprite_004D04C0_004D0574.bin
        INCBIN  build\spritecontainer\sprite_004D0574_004D09AC.bin
        INCBIN  build\spritecontainer\sprite_004D09AC_004D0A4C.bin
        INCBIN  build\spritecontainer\sprite_004D0A4C_004D0A70.bin
        INCBIN  build\spritecontainer\sprite_004D0A70_004D0C54.bin
        INCBIN  build\spritecontainer\sprite_004D0C54_004D0C7C.bin
        INCBIN  build\spritecontainer\sprite_004D0C7C_004D0CA0.bin
        INCBIN  build\spritecontainer\sprite_004D0CA0_004D1408.bin
        INCBIN  build\spritecontainer\sprite_004D1408_004D14F8.bin
        INCBIN  build\spritecontainer\sprite_004D14F8_004D152C.bin
        INCBIN  build\spritecontainer\sprite_004D152C_004D1BE0.bin
        INCBIN  build\spritecontainer\sprite_004D1BE0_004D1D20.bin
        INCBIN  build\spritecontainer\sprite_004D1D20_004D1D64.bin
        INCBIN  build\spritecontainer\sprite_004D1D64_004D2398.bin
        INCBIN  build\spritecontainer\sprite_004D2398_004D24D8.bin
        INCBIN  build\spritecontainer\sprite_004D24D8_004D251C.bin
        INCBIN  build\spritecontainer\sprite_004D251C_004D2888.bin
        INCBIN  build\spritecontainer\sprite_004D2888_004D2928.bin
        INCBIN  build\spritecontainer\sprite_004D2928_004D296C.bin
        INCBIN  build\spritecontainer\sprite_004D296C_004D310C.bin
        INCBIN  build\spritecontainer\sprite_004D310C_004D31FC.bin
        INCBIN  build\spritecontainer\sprite_004D31FC_004D3230.bin
        INCBIN  build\spritecontainer\sprite_004D3230_004D39E0.bin
        INCBIN  build\spritecontainer\sprite_004D39E0_004D3AA8.bin
        INCBIN  build\spritecontainer\sprite_004D3AA8_004D3B4C.bin
        INCBIN  build\spritecontainer\sprite_004D3B4C_004D4400.bin
        INCBIN  build\spritecontainer\sprite_004D4400_004D44F0.bin
        INCBIN  build\spritecontainer\sprite_004D44F0_004D4524.bin
        INCBIN  build\spritecontainer\sprite_004D4524_004D4A24.bin
        INCBIN  build\spritecontainer\sprite_004D4A24_004D4AC4.bin
        INCBIN  build\spritecontainer\sprite_004D4AC4_004D4AE8.bin
        INCBIN  build\spritecontainer\sprite_004D4AE8_004D5680.bin
        INCBIN  build\spritecontainer\sprite_004D5680_004D57C0.bin
        INCBIN  build\spritecontainer\sprite_004D57C0_004D5804.bin
        INCBIN  build\spritecontainer\sprite_004D5804_004D642C.bin
        INCBIN  build\spritecontainer\sprite_004D642C_004D656C.bin
        INCBIN  build\spritecontainer\sprite_004D656C_004D65B0.bin
        INCBIN  build\spritecontainer\sprite_004D65B0_004D6F08.bin
        INCBIN  build\spritecontainer\sprite_004D6F08_004D6FF8.bin
        INCBIN  build\spritecontainer\sprite_004D6FF8_004D702C.bin
        INCBIN  build\spritecontainer\sprite_004D702C_004D7528.bin
        INCBIN  build\spritecontainer\sprite_004D7528_004D75C8.bin
        INCBIN  build\spritecontainer\sprite_004D75C8_004D75EC.bin
        INCBIN  build\spritecontainer\sprite_004D75EC_004D7EDC.bin
        INCBIN  build\spritecontainer\sprite_004D7EDC_004D7F54.bin
        INCBIN  build\spritecontainer\sprite_004D7F54_004D7FB8.bin
        INCBIN  build\spritecontainer\sprite_004D7FB8_004D8588.bin
        INCBIN  build\spritecontainer\sprite_004D8588_004D8628.bin
        INCBIN  build\spritecontainer\sprite_004D8628_004D864C.bin
        INCBIN  build\spritecontainer\sprite_004D864C_004D93B4.bin
        INCBIN  build\spritecontainer\sprite_004D93B4_004D94F4.bin
        INCBIN  build\spritecontainer\sprite_004D94F4_004D9538.bin
        INCBIN  build\spritecontainer\sprite_004D9538_004DA800.bin
        INCBIN  build\spritecontainer\sprite_004DA800_004DA940.bin
        INCBIN  build\spritecontainer\sprite_004DA940_004DA984.bin
        INCBIN  build\spritecontainer\sprite_004DA984_004DAE14.bin
        INCBIN  build\spritecontainer\sprite_004DAE14_004DAEB4.bin
        INCBIN  build\spritecontainer\sprite_004DAEB4_004DAED8.bin
        INCBIN  build\spritecontainer\sprite_004DAED8_004DB98C.bin
        INCBIN  build\spritecontainer\sprite_004DB98C_004DBACC.bin
        INCBIN  build\spritecontainer\sprite_004DBACC_004DBB10.bin
        INCBIN  build\spritecontainer\sprite_004DBB10_004DC638.bin
        INCBIN  build\spritecontainer\sprite_004DC638_004DC778.bin
        INCBIN  build\spritecontainer\sprite_004DC778_004DC7BC.bin
        INCBIN  build\spritecontainer\sprite_004DC7BC_004DD08C.bin
        INCBIN  build\spritecontainer\sprite_004DD08C_004DD17C.bin
        INCBIN  build\spritecontainer\sprite_004DD17C_004DD1B0.bin
        INCBIN  build\spritecontainer\sprite_004DD1B0_004DDEE0.bin
        INCBIN  build\spritecontainer\sprite_004DDEE0_004DE020.bin
        INCBIN  build\spritecontainer\sprite_004DE020_004DE064.bin
        INCBIN  build\spritecontainer\sprite_004DE064_004DECD8.bin
        INCBIN  build\spritecontainer\sprite_004DECD8_004DEE18.bin
        INCBIN  build\spritecontainer\sprite_004DEE18_004DEE5C.bin
        INCBIN  build\spritecontainer\sprite_004DEE5C_004DF0F8.bin
        INCBIN  build\spritecontainer\sprite_004DF0F8_004DF148.bin
        INCBIN  build\spritecontainer\sprite_004DF148_004DF15C.bin
        INCBIN  build\spritecontainer\sprite_004DF15C_004DF88C.bin
        INCBIN  build\spritecontainer\sprite_004DF88C_004DF968.bin
        INCBIN  build\spritecontainer\sprite_004DF968_004DFA1C.bin
        INCBIN  build\spritecontainer\sprite_004DFA1C_004E0284.bin
        INCBIN  build\spritecontainer\sprite_004E0284_004E0374.bin
        INCBIN  build\spritecontainer\sprite_004E0374_004E03A8.bin
        INCBIN  build\spritecontainer\sprite_004E03A8_004E076C.bin
        INCBIN  build\spritecontainer\sprite_004E076C_004E080C.bin
        INCBIN  build\spritecontainer\sprite_004E080C_004E0830.bin
        INCBIN  build\spritecontainer\sprite_004E0830_004E0A3C.bin
        INCBIN  build\spritecontainer\sprite_004E0A3C_004E0A64.bin
        INCBIN  build\spritecontainer\sprite_004E0A64_004E0A88.bin
        INCBIN  build\spritecontainer\sprite_004E0A88_004E1298.bin
        INCBIN  build\spritecontainer\sprite_004E1298_004E1388.bin
        INCBIN  build\spritecontainer\sprite_004E1388_004E13BC.bin
        INCBIN  build\spritecontainer\sprite_004E13BC_004E1AE0.bin
        INCBIN  build\spritecontainer\sprite_004E1AE0_004E1C20.bin
        INCBIN  build\spritecontainer\sprite_004E1C20_004E1C64.bin
        INCBIN  build\spritecontainer\sprite_004E1C64_004E231C.bin
        INCBIN  build\spritecontainer\sprite_004E231C_004E245C.bin
        INCBIN  build\spritecontainer\sprite_004E245C_004E24A0.bin
        INCBIN  build\spritecontainer\sprite_004E24A0_004E2870.bin
        INCBIN  build\spritecontainer\sprite_004E2870_004E2910.bin
        INCBIN  build\spritecontainer\sprite_004E2910_004E2954.bin
        INCBIN  build\spritecontainer\sprite_004E2954_004E31A8.bin
        INCBIN  build\spritecontainer\sprite_004E31A8_004E3298.bin
        INCBIN  build\spritecontainer\sprite_004E3298_004E32CC.bin
        INCBIN  build\spritecontainer\sprite_004E32CC_004E3C34.bin
        INCBIN  build\spritecontainer\sprite_004E3C34_004E3D24.bin
        INCBIN  build\spritecontainer\sprite_004E3D24_004E3D58.bin
        INCBIN  build\spritecontainer\sprite_004E3D58_004E4098.bin
        INCBIN  build\spritecontainer\sprite_004E4098_004E4138.bin
        INCBIN  build\spritecontainer\sprite_004E4138_004E415C.bin
        INCBIN  build\spritecontainer\sprite_004E415C_004E4E78.bin
        INCBIN  build\spritecontainer\sprite_004E4E78_004E4FB8.bin
        INCBIN  build\spritecontainer\sprite_004E4FB8_004E4FFC.bin
        INCBIN  build\spritecontainer\sprite_004E4FFC_004E5F24.bin
        INCBIN  build\spritecontainer\sprite_004E5F24_004E6064.bin
        INCBIN  build\spritecontainer\sprite_004E6064_004E60A8.bin
        INCBIN  build\spritecontainer\sprite_004E60A8_004E6AE4.bin
        INCBIN  build\spritecontainer\sprite_004E6AE4_004E6BD4.bin
        INCBIN  build\spritecontainer\sprite_004E6BD4_004E6C08.bin
        INCBIN  build\spritecontainer\sprite_004E6C08_004E7BD0.bin
        INCBIN  build\spritecontainer\sprite_004E7BD0_004E7D10.bin
        INCBIN  build\spritecontainer\sprite_004E7D10_004E7D54.bin
        INCBIN  build\spritecontainer\sprite_004E7D54_004E8D40.bin
        INCBIN  build\spritecontainer\sprite_004E8D40_004E8E80.bin
        INCBIN  build\spritecontainer\sprite_004E8E80_004E8EC4.bin
        INCBIN  build\spritecontainer\sprite_004E8EC4_004E91E0.bin
        INCBIN  build\spritecontainer\sprite_004E91E0_004E9230.bin
        INCBIN  build\spritecontainer\sprite_004E9230_004E9244.bin
        INCBIN  build\spritecontainer\sprite_004E9244_004E9D88.bin
        INCBIN  build\spritecontainer\sprite_004E9D88_004E9E78.bin
        INCBIN  build\spritecontainer\sprite_004E9E78_004E9EAC.bin
        INCBIN  build\spritecontainer\sprite_004E9EAC_004EA108.bin
        INCBIN  build\spritecontainer\sprite_004EA108_004EA1BC.bin
        INCBIN  build\spritecontainer\sprite_004EA1BC_004EA250.bin
        INCBIN  build\spritecontainer\sprite_004EA250_004EA55C.bin
        INCBIN  build\spritecontainer\sprite_004EA55C_004EA5FC.bin
        INCBIN  build\spritecontainer\sprite_004EA5FC_004EA620.bin
        INCBIN  build\spritecontainer\sprite_004EA620_004EA84C.bin
        INCBIN  build\spritecontainer\sprite_004EA84C_004EA874.bin
        INCBIN  build\spritecontainer\sprite_004EA874_004EA898.bin
        INCBIN  build\spritecontainer\sprite_004EA898_004EB6E4.bin
        INCBIN  build\spritecontainer\sprite_004EB6E4_004EB824.bin
        INCBIN  build\spritecontainer\sprite_004EB824_004EB868.bin
        INCBIN  build\spritecontainer\sprite_004EB868_004EC350.bin
        INCBIN  build\spritecontainer\sprite_004EC350_004EC490.bin
        INCBIN  build\spritecontainer\sprite_004EC490_004EC4D4.bin
        INCBIN  build\spritecontainer\sprite_004EC4D4_004ECE0C.bin
        INCBIN  build\spritecontainer\sprite_004ECE0C_004ECF4C.bin
        INCBIN  build\spritecontainer\sprite_004ECF4C_004ECF90.bin
        INCBIN  build\spritecontainer\sprite_004ECF90_004ED400.bin
        INCBIN  build\spritecontainer\sprite_004ED400_004ED4A0.bin
        INCBIN  build\spritecontainer\sprite_004ED4A0_004ED4E4.bin
        INCBIN  build\spritecontainer\sprite_004ED4E4_004EDFC0.bin
        INCBIN  build\spritecontainer\sprite_004EDFC0_004EE0B0.bin
        INCBIN  build\spritecontainer\sprite_004EE0B0_004EE0E4.bin
        INCBIN  build\spritecontainer\sprite_004EE0E4_004EE198.bin
        INCBIN  build\spritecontainer\sprite_004EE198_004EE22C.bin
        INCBIN  build\spritecontainer\sprite_004EE22C_004EF184.bin
        INCBIN  build\spritecontainer\sprite_004EF184_004EF2C4.bin
        INCBIN  build\spritecontainer\sprite_004EF2C4_004EF308.bin
        INCBIN  build\spritecontainer\sprite_004EF308_004EF758.bin
        INCBIN  build\spritecontainer\sprite_004EF758_004EF7F8.bin
        INCBIN  build\spritecontainer\sprite_004EF7F8_004EF81C.bin
        INCBIN  build\spritecontainer\sprite_004EF81C_004F0258.bin
        INCBIN  build\spritecontainer\sprite_004F0258_004F0398.bin
        INCBIN  build\spritecontainer\sprite_004F0398_004F03DC.bin
        INCBIN  build\spritecontainer\sprite_004F03DC_004F0E8C.bin
        INCBIN  build\spritecontainer\sprite_004F0E8C_004F0FCC.bin
        INCBIN  build\spritecontainer\sprite_004F0FCC_004F1010.bin
        INCBIN  build\spritecontainer\sprite_004F1010_004F1844.bin
        INCBIN  build\spritecontainer\sprite_004F1844_004F1934.bin
        INCBIN  build\spritecontainer\sprite_004F1934_004F1968.bin
        INCBIN  build\spritecontainer\sprite_004F1968_004F25BC.bin
        INCBIN  build\spritecontainer\sprite_004F25BC_004F26FC.bin
        INCBIN  build\spritecontainer\sprite_004F26FC_004F2740.bin
        INCBIN  build\spritecontainer\sprite_004F2740_004F3370.bin
        INCBIN  build\spritecontainer\sprite_004F3370_004F34B0.bin
        INCBIN  build\spritecontainer\sprite_004F34B0_004F34F4.bin
        INCBIN  build\spritecontainer\sprite_004F34F4_004F3760.bin
        INCBIN  build\spritecontainer\sprite_004F3760_004F37B0.bin
        INCBIN  build\spritecontainer\sprite_004F37B0_004F37C4.bin
        INCBIN  build\spritecontainer\sprite_004F37C4_004F3EA4.bin
        INCBIN  build\spritecontainer\sprite_004F3EA4_004F3F80.bin
        INCBIN  build\spritecontainer\sprite_004F3F80_004F4034.bin
        INCBIN  build\spritecontainer\sprite_004F4034_004F4840.bin
        INCBIN  build\spritecontainer\sprite_004F4840_004F4930.bin
        INCBIN  build\spritecontainer\sprite_004F4930_004F4964.bin
        INCBIN  build\spritecontainer\sprite_004F4964_004F4F74.bin
        INCBIN  build\spritecontainer\sprite_004F4F74_004F5050.bin
        INCBIN  build\spritecontainer\sprite_004F5050_004F5104.bin
        INCBIN  build\spritecontainer\sprite_004F5104_004F5534.bin
        INCBIN  build\spritecontainer\sprite_004F5534_004F55D4.bin
        INCBIN  build\spritecontainer\sprite_004F55D4_004F55F8.bin
        INCBIN  build\spritecontainer\sprite_004F55F8_004F57C4.bin
        INCBIN  build\spritecontainer\sprite_004F57C4_004F57EC.bin
        INCBIN  build\spritecontainer\sprite_004F57EC_004F5810.bin
        INCBIN  build\spritecontainer\sprite_004F5810_004F5FB0.bin
        INCBIN  build\spritecontainer\sprite_004F5FB0_004F60A0.bin
        INCBIN  build\spritecontainer\sprite_004F60A0_004F60D4.bin
        INCBIN  build\spritecontainer\sprite_004F60D4_004F6860.bin
        INCBIN  build\spritecontainer\sprite_004F6860_004F69A0.bin
        INCBIN  build\spritecontainer\sprite_004F69A0_004F69E4.bin
        INCBIN  build\spritecontainer\sprite_004F69E4_004F7130.bin
        INCBIN  build\spritecontainer\sprite_004F7130_004F7270.bin
        INCBIN  build\spritecontainer\sprite_004F7270_004F72B4.bin
        INCBIN  build\spritecontainer\sprite_004F72B4_004F764C.bin
        INCBIN  build\spritecontainer\sprite_004F764C_004F76EC.bin
        INCBIN  build\spritecontainer\sprite_004F76EC_004F7730.bin
        INCBIN  build\spritecontainer\sprite_004F7730_004F7F30.bin
        INCBIN  build\spritecontainer\sprite_004F7F30_004F8020.bin
        INCBIN  build\spritecontainer\sprite_004F8020_004F8054.bin
        INCBIN  build\spritecontainer\sprite_004F8054_004F8904.bin
        INCBIN  build\spritecontainer\sprite_004F8904_004F89F4.bin
        INCBIN  build\spritecontainer\sprite_004F89F4_004F8A28.bin
        INCBIN  build\spritecontainer\sprite_004F8A28_004F8BA0.bin
        INCBIN  build\spritecontainer\sprite_004F8BA0_004F8BC8.bin
        INCBIN  build\spritecontainer\sprite_004F8BC8_004F8BEC.bin
        INCBIN  build\spritecontainer\sprite_004F8BEC_004F8E00.bin
        INCBIN  build\spritecontainer\sprite_004F8E00_004F8E28.bin
        INCBIN  build\spritecontainer\sprite_004F8E28_004F8E4C.bin
        INCBIN  build\spritecontainer\sprite_004F8E4C_004F9338.bin
        INCBIN  build\spritecontainer\sprite_004F9338_004F93D8.bin
        INCBIN  build\spritecontainer\sprite_004F93D8_004F93FC.bin
        INCBIN  build\spritecontainer\sprite_004F93FC_004F9FC0.bin
        INCBIN  build\spritecontainer\sprite_004F9FC0_004FA100.bin
        INCBIN  build\spritecontainer\sprite_004FA100_004FA144.bin
        INCBIN  build\spritecontainer\sprite_004FA144_004FAD8C.bin
        INCBIN  build\spritecontainer\sprite_004FAD8C_004FAECC.bin
        INCBIN  build\spritecontainer\sprite_004FAECC_004FAF10.bin
        INCBIN  build\spritecontainer\sprite_004FAF10_004FB88C.bin
        INCBIN  build\spritecontainer\sprite_004FB88C_004FB97C.bin
        INCBIN  build\spritecontainer\sprite_004FB97C_004FB9B0.bin
        INCBIN  build\spritecontainer\sprite_004FB9B0_004FC7F8.bin
        INCBIN  build\spritecontainer\sprite_004FC7F8_004FC938.bin
        INCBIN  build\spritecontainer\sprite_004FC938_004FC97C.bin
        INCBIN  build\spritecontainer\sprite_004FC97C_004FD774.bin
        INCBIN  build\spritecontainer\sprite_004FD774_004FD8B4.bin
        INCBIN  build\spritecontainer\sprite_004FD8B4_004FD8F8.bin
        INCBIN  build\spritecontainer\sprite_004FD8F8_004FDBCC.bin
        INCBIN  build\spritecontainer\sprite_004FDBCC_004FDC1C.bin
        INCBIN  build\spritecontainer\sprite_004FDC1C_004FDC30.bin
        INCBIN  build\spritecontainer\sprite_004FDC30_004FE5B8.bin
        INCBIN  build\spritecontainer\sprite_004FE5B8_004FE6A8.bin
        INCBIN  build\spritecontainer\sprite_004FE6A8_004FE6DC.bin
        INCBIN  build\spritecontainer\sprite_004FE6DC_004FEB48.bin
        INCBIN  build\spritecontainer\sprite_004FEB48_004FEB98.bin
        INCBIN  build\spritecontainer\sprite_004FEB98_004FEBDC.bin
        INCBIN  build\spritecontainer\sprite_004FEBDC_004FF0A8.bin
        INCBIN  build\spritecontainer\sprite_004FF0A8_004FF148.bin
        INCBIN  build\spritecontainer\sprite_004FF148_004FF16C.bin
        INCBIN  build\spritecontainer\sprite_004FF16C_004FF37C.bin
        INCBIN  build\spritecontainer\sprite_004FF37C_004FF3A4.bin
        INCBIN  build\spritecontainer\sprite_004FF3A4_004FF3C8.bin
        INCBIN  build\spritecontainer\sprite_004FF3C8_004FFE3C.bin
        INCBIN  build\spritecontainer\sprite_004FFE3C_004FFF7C.bin
        INCBIN  build\spritecontainer\sprite_004FFF7C_004FFFC0.bin
        INCBIN  build\spritecontainer\sprite_004FFFC0_00500290.bin
        INCBIN  build\spritecontainer\sprite_00500290_00500330.bin
        INCBIN  build\spritecontainer\sprite_00500330_00500374.bin
        INCBIN  build\spritecontainer\sprite_00500374_00500C90.bin
        INCBIN  build\spritecontainer\sprite_00500C90_00500D80.bin
        INCBIN  build\spritecontainer\sprite_00500D80_00500DB4.bin
        INCBIN  build\spritecontainer\sprite_00500DB4_0050179C.bin
        INCBIN  build\spritecontainer\sprite_0050179C_0050188C.bin
        INCBIN  build\spritecontainer\sprite_0050188C_005018C0.bin
        INCBIN  build\spritecontainer\sprite_005018C0_00501DC8.bin
        INCBIN  build\spritecontainer\sprite_00501DC8_00501E68.bin
        INCBIN  build\spritecontainer\sprite_00501E68_00501E8C.bin
        INCBIN  build\spritecontainer\sprite_00501E8C_00502AC4.bin
        INCBIN  build\spritecontainer\sprite_00502AC4_00502C04.bin
        INCBIN  build\spritecontainer\sprite_00502C04_00502C48.bin
        INCBIN  build\spritecontainer\sprite_00502C48_005038B4.bin
        INCBIN  build\spritecontainer\sprite_005038B4_005039F4.bin
        INCBIN  build\spritecontainer\sprite_005039F4_00503A38.bin
        INCBIN  build\spritecontainer\sprite_00503A38_005043D0.bin
        INCBIN  build\spritecontainer\sprite_005043D0_005044C0.bin
        INCBIN  build\spritecontainer\sprite_005044C0_005044F4.bin
        INCBIN  build\spritecontainer\sprite_005044F4_00505350.bin
        INCBIN  build\spritecontainer\sprite_00505350_00505490.bin
        INCBIN  build\spritecontainer\sprite_00505490_005054D4.bin
        INCBIN  build\spritecontainer\sprite_005054D4_00506304.bin
        INCBIN  build\spritecontainer\sprite_00506304_00506444.bin
        INCBIN  build\spritecontainer\sprite_00506444_00506488.bin
        INCBIN  build\spritecontainer\sprite_00506488_00506778.bin
        INCBIN  build\spritecontainer\sprite_00506778_005067C8.bin
        INCBIN  build\spritecontainer\sprite_005067C8_005067DC.bin
        INCBIN  build\spritecontainer\sprite_005067DC_0050714C.bin
        INCBIN  build\spritecontainer\sprite_0050714C_0050723C.bin
        INCBIN  build\spritecontainer\sprite_0050723C_00507270.bin
        INCBIN  build\spritecontainer\sprite_00507270_005076BC.bin
        INCBIN  build\spritecontainer\sprite_005076BC_0050770C.bin
        INCBIN  build\spritecontainer\sprite_0050770C_00507750.bin
        INCBIN  build\spritecontainer\sprite_00507750_00507C30.bin
        INCBIN  build\spritecontainer\sprite_00507C30_00507CD0.bin
        INCBIN  build\spritecontainer\sprite_00507CD0_00507CF4.bin
        INCBIN  build\spritecontainer\sprite_00507CF4_00507EF0.bin
        INCBIN  build\spritecontainer\sprite_00507EF0_00507F18.bin
        INCBIN  build\spritecontainer\sprite_00507F18_00507F3C.bin
        INCBIN  build\spritecontainer\sprite_00507F3C_0050884C.bin
        INCBIN  build\spritecontainer\sprite_0050884C_0050893C.bin
        INCBIN  build\spritecontainer\sprite_0050893C_00508970.bin
        INCBIN  build\spritecontainer\sprite_00508970_005093D8.bin
        INCBIN  build\spritecontainer\sprite_005093D8_00509518.bin
        INCBIN  build\spritecontainer\sprite_00509518_0050955C.bin
        INCBIN  build\spritecontainer\sprite_0050955C_00509E2C.bin
        INCBIN  build\spritecontainer\sprite_00509E2C_00509F6C.bin
        INCBIN  build\spritecontainer\sprite_00509F6C_00509FB0.bin
        INCBIN  build\spritecontainer\sprite_00509FB0_0050A2B8.bin
        INCBIN  build\spritecontainer\sprite_0050A2B8_0050A358.bin
        INCBIN  build\spritecontainer\sprite_0050A358_0050A39C.bin
        INCBIN  build\spritecontainer\sprite_0050A39C_0050AD14.bin
        INCBIN  build\spritecontainer\sprite_0050AD14_0050AE04.bin
        INCBIN  build\spritecontainer\sprite_0050AE04_0050AE38.bin
        INCBIN  build\spritecontainer\sprite_0050AE38_0050B858.bin
        INCBIN  build\spritecontainer\sprite_0050B858_0050B948.bin
        INCBIN  build\spritecontainer\sprite_0050B948_0050B97C.bin
        INCBIN  build\spritecontainer\sprite_0050B97C_0050BB20.bin
        INCBIN  build\spritecontainer\sprite_0050BB20_0050BB48.bin
        INCBIN  build\spritecontainer\sprite_0050BB48_0050BB6C.bin
        INCBIN  build\spritecontainer\sprite_0050BB6C_0050BB94.bin
        INCBIN  build\spritecontainer\sprite_0050BB94_0050BBB8.bin
        INCBIN  build\spritecontainer\sprite_0050BBB8_0050C13C.bin
        INCBIN  build\spritecontainer\sprite_0050C13C_0050C1DC.bin
        INCBIN  build\spritecontainer\sprite_0050C1DC_0050C200.bin
        INCBIN  build\spritecontainer\sprite_0050C200_0050CE34.bin
        INCBIN  build\spritecontainer\sprite_0050CE34_0050CF74.bin
        INCBIN  build\spritecontainer\sprite_0050CF74_0050CFB8.bin
        INCBIN  build\spritecontainer\sprite_0050CFB8_0050DBD4.bin
        INCBIN  build\spritecontainer\sprite_0050DBD4_0050DD14.bin
        INCBIN  build\spritecontainer\sprite_0050DD14_0050DD58.bin
        INCBIN  build\spritecontainer\sprite_0050DD58_0050E6EC.bin
        INCBIN  build\spritecontainer\sprite_0050E6EC_0050E7DC.bin
        INCBIN  build\spritecontainer\sprite_0050E7DC_0050E810.bin
        INCBIN  build\spritecontainer\sprite_0050E810_0050F54C.bin
        INCBIN  build\spritecontainer\sprite_0050F54C_0050F68C.bin
        INCBIN  build\spritecontainer\sprite_0050F68C_0050F6D0.bin
        INCBIN  build\spritecontainer\sprite_0050F6D0_005103A8.bin
        INCBIN  build\spritecontainer\sprite_005103A8_005104E8.bin
        INCBIN  build\spritecontainer\sprite_005104E8_0051052C.bin
        INCBIN  build\spritecontainer\sprite_0051052C_005111DC.bin
        INCBIN  build\spritecontainer\sprite_005111DC_0051131C.bin
        INCBIN  build\spritecontainer\sprite_0051131C_00511360.bin
        INCBIN  build\spritecontainer\sprite_00511360_00511650.bin
        INCBIN  build\spritecontainer\sprite_00511650_005116A0.bin
        INCBIN  build\spritecontainer\sprite_005116A0_005116B4.bin
        INCBIN  build\spritecontainer\sprite_005116B4_00511A48.bin
        INCBIN  build\spritecontainer\sprite_00511A48_00511A98.bin
        INCBIN  build\spritecontainer\sprite_00511A98_00511ADC.bin
        INCBIN  build\spritecontainer\sprite_00511ADC_00512474.bin
        INCBIN  build\spritecontainer\sprite_00512474_00512564.bin
        INCBIN  build\spritecontainer\sprite_00512564_00512598.bin
        INCBIN  build\spritecontainer\sprite_00512598_00512BFC.bin
        INCBIN  build\spritecontainer\sprite_00512BFC_00512CD8.bin
        INCBIN  build\spritecontainer\sprite_00512CD8_00512D8C.bin
        INCBIN  build\spritecontainer\sprite_00512D8C_00513314.bin
        INCBIN  build\spritecontainer\sprite_00513314_005133B4.bin
        INCBIN  build\spritecontainer\sprite_005133B4_005133D8.bin
        INCBIN  build\spritecontainer\sprite_005133D8_00513640.bin
        INCBIN  build\spritecontainer\sprite_00513640_00513668.bin
        INCBIN  build\spritecontainer\sprite_00513668_0051368C.bin
        INCBIN  build\spritecontainer\sprite_0051368C_00513FB4.bin
        INCBIN  build\spritecontainer\sprite_00513FB4_005140A4.bin
        INCBIN  build\spritecontainer\sprite_005140A4_005140D8.bin
        INCBIN  build\spritecontainer\sprite_005140D8_00514888.bin
        INCBIN  build\spritecontainer\sprite_00514888_005149C8.bin
        INCBIN  build\spritecontainer\sprite_005149C8_00514A0C.bin
        INCBIN  build\spritecontainer\sprite_00514A0C_00514F2C.bin
        INCBIN  build\spritecontainer\sprite_00514F2C_0051506C.bin
        INCBIN  build\spritecontainer\sprite_0051506C_005150B0.bin
        INCBIN  build\spritecontainer\sprite_005150B0_00515494.bin
        INCBIN  build\spritecontainer\sprite_00515494_00515534.bin
        INCBIN  build\spritecontainer\sprite_00515534_00515578.bin
        INCBIN  build\spritecontainer\sprite_00515578_00515E6C.bin
        INCBIN  build\spritecontainer\sprite_00515E6C_00515F5C.bin
        INCBIN  build\spritecontainer\sprite_00515F5C_00515F90.bin
        INCBIN  build\spritecontainer\sprite_00515F90_005165BC.bin
        INCBIN  build\spritecontainer\sprite_005165BC_005166AC.bin
        INCBIN  build\spritecontainer\sprite_005166AC_005166E0.bin
        INCBIN  build\spritecontainer\sprite_005166E0_00517394.bin
        INCBIN  build\spritecontainer\sprite_00517394_0051754C.bin
        INCBIN  build\spritecontainer\sprite_0051754C_00517600.bin
        INCBIN  build\spritecontainer\sprite_00517600_00517B80.bin
        INCBIN  build\spritecontainer\sprite_00517B80_00517C20.bin
        INCBIN  build\spritecontainer\sprite_00517C20_00517C44.bin
        INCBIN  build\spritecontainer\sprite_00517C44_005188E8.bin
        INCBIN  build\spritecontainer\sprite_005188E8_00518A28.bin
        INCBIN  build\spritecontainer\sprite_00518A28_00518A6C.bin
        INCBIN  build\spritecontainer\sprite_00518A6C_005197BC.bin
        INCBIN  build\spritecontainer\sprite_005197BC_005198FC.bin
        INCBIN  build\spritecontainer\sprite_005198FC_00519940.bin
        INCBIN  build\spritecontainer\sprite_00519940_0051A63C.bin
        INCBIN  build\spritecontainer\sprite_0051A63C_0051A77C.bin
        INCBIN  build\spritecontainer\sprite_0051A77C_0051A7C0.bin
        INCBIN  build\spritecontainer\sprite_0051A7C0_0051AAC0.bin
        INCBIN  build\spritecontainer\sprite_0051AAC0_0051AB10.bin
        INCBIN  build\spritecontainer\sprite_0051AB10_0051AB24.bin
        INCBIN  build\spritecontainer\sprite_0051AB24_0051B4E4.bin
        INCBIN  build\spritecontainer\sprite_0051B4E4_0051B5D4.bin
        INCBIN  build\spritecontainer\sprite_0051B5D4_0051B608.bin
        INCBIN  build\spritecontainer\sprite_0051B608_0051BB9C.bin
        INCBIN  build\spritecontainer\sprite_0051BB9C_0051BC3C.bin
        INCBIN  build\spritecontainer\sprite_0051BC3C_0051BC60.bin
        INCBIN  build\spritecontainer\sprite_0051BC60_0051C494.bin
        INCBIN  build\spritecontainer\sprite_0051C494_0051C5D4.bin
        INCBIN  build\spritecontainer\sprite_0051C5D4_0051C618.bin
|unk_0851C618|
        INCBIN  build\spritecontainer\sprite_0051C618_0051C898.bin
        INCBIN  build\spritecontainer\sprite_0051C898_0051C8F0.bin
        INCBIN  build\spritecontainer\sprite_0051C8F0_0051CE64.bin
        INCBIN  build\spritecontainer\sprite_0051CE64_0051CF04.bin
        INCBIN  build\spritecontainer\sprite_0051CF04_0051CF28.bin
        INCBIN  build\spritecontainer\sprite_0051CF28_0051DBAC.bin
        INCBIN  build\spritecontainer\sprite_0051DBAC_0051DCEC.bin
        INCBIN  build\spritecontainer\sprite_0051DCEC_0051DD30.bin
        INCBIN  build\spritecontainer\sprite_0051DD30_0051EA38.bin
        INCBIN  build\spritecontainer\sprite_0051EA38_0051EB78.bin
        INCBIN  build\spritecontainer\sprite_0051EB78_0051EBBC.bin
        INCBIN  build\spritecontainer\sprite_0051EBBC_0051F5DC.bin
        INCBIN  build\spritecontainer\sprite_0051F5DC_0051F6CC.bin
        INCBIN  build\spritecontainer\sprite_0051F6CC_0051F700.bin
        INCBIN  build\spritecontainer\sprite_0051F700_005205F4.bin
        INCBIN  build\spritecontainer\sprite_005205F4_00520734.bin
        INCBIN  build\spritecontainer\sprite_00520734_00520778.bin
        INCBIN  build\spritecontainer\sprite_00520778_005208B8.bin
        INCBIN  build\spritecontainer\sprite_005208B8_005208FC.bin
        INCBIN  build\spritecontainer\sprite_005208FC_0052174C.bin
        INCBIN  build\spritecontainer\sprite_0052174C_0052188C.bin
        INCBIN  build\spritecontainer\sprite_0052188C_005218D0.bin
        INCBIN  build\spritecontainer\sprite_005218D0_00521BE0.bin
        INCBIN  build\spritecontainer\sprite_00521BE0_00521C30.bin
        INCBIN  build\spritecontainer\sprite_00521C30_00521C44.bin
        INCBIN  build\spritecontainer\sprite_00521C44_00522648.bin
        INCBIN  build\spritecontainer\sprite_00522648_00522738.bin
        INCBIN  build\spritecontainer\sprite_00522738_0052276C.bin
        INCBIN  build\spritecontainer\sprite_0052276C_00522ECC.bin
        INCBIN  build\spritecontainer\sprite_00522ECC_00522FA8.bin
        INCBIN  build\spritecontainer\sprite_00522FA8_0052305C.bin
        INCBIN  build\spritecontainer\sprite_0052305C_00523518.bin
        INCBIN  build\spritecontainer\sprite_00523518_00523568.bin
        INCBIN  build\spritecontainer\sprite_00523568_005235AC.bin
        INCBIN  build\spritecontainer\sprite_005235AC_00523B20.bin
        INCBIN  build\spritecontainer\sprite_00523B20_00523BC0.bin
        INCBIN  build\spritecontainer\sprite_00523BC0_00523BE4.bin
        INCBIN  build\spritecontainer\sprite_00523BE4_00523E24.bin
        INCBIN  build\spritecontainer\sprite_00523E24_00523E4C.bin
        INCBIN  build\spritecontainer\sprite_00523E4C_00523E70.bin
        INCBIN  build\spritecontainer\sprite_00523E70_005247BC.bin
        INCBIN  build\spritecontainer\sprite_005247BC_005248AC.bin
        INCBIN  build\spritecontainer\sprite_005248AC_005248E0.bin
        INCBIN  build\spritecontainer\sprite_005248E0_00525088.bin
        INCBIN  build\spritecontainer\sprite_00525088_005251C8.bin
        INCBIN  build\spritecontainer\sprite_005251C8_0052520C.bin
        INCBIN  build\spritecontainer\sprite_0052520C_00525640.bin
        INCBIN  build\spritecontainer\sprite_00525640_005256E0.bin
        INCBIN  build\spritecontainer\sprite_005256E0_00525724.bin
        INCBIN  build\spritecontainer\sprite_00525724_005260E0.bin
        INCBIN  build\spritecontainer\sprite_005260E0_005261D0.bin
        INCBIN  build\spritecontainer\sprite_005261D0_00526204.bin
        INCBIN  build\spritecontainer\sprite_00526204_005267B8.bin
        INCBIN  build\spritecontainer\sprite_005267B8_005268A8.bin
        INCBIN  build\spritecontainer\sprite_005268A8_005268DC.bin
        INCBIN  build\spritecontainer\sprite_005268DC_005275B0.bin
        INCBIN  build\spritecontainer\sprite_005275B0_00527768.bin
        INCBIN  build\spritecontainer\sprite_00527768_0052781C.bin
|unk_0852781C|
        INCBIN  build\spritecontainer\sprite_0052781C_00527A7C.bin
        INCBIN  build\spritecontainer\sprite_00527A7C_00527AD4.bin
        INCBIN  build\spritecontainer\sprite_00527AD4_005281A8.bin
        INCBIN  build\spritecontainer\sprite_005281A8_00528248.bin
        INCBIN  build\spritecontainer\sprite_00528248_0052826C.bin
        INCBIN  build\spritecontainer\sprite_0052826C_00529208.bin
        INCBIN  build\spritecontainer\sprite_00529208_00529348.bin
        INCBIN  build\spritecontainer\sprite_00529348_0052938C.bin
        INCBIN  build\spritecontainer\sprite_0052938C_0052A334.bin
        INCBIN  build\spritecontainer\sprite_0052A334_0052A474.bin
        INCBIN  build\spritecontainer\sprite_0052A474_0052A4B8.bin
        INCBIN  build\spritecontainer\sprite_0052A4B8_0052B0C4.bin
        INCBIN  build\spritecontainer\sprite_0052B0C4_0052B1B4.bin
        INCBIN  build\spritecontainer\sprite_0052B1B4_0052B1E8.bin
        INCBIN  build\spritecontainer\sprite_0052B1E8_0052C2A4.bin
        INCBIN  build\spritecontainer\sprite_0052C2A4_0052C3E4.bin
        INCBIN  build\spritecontainer\sprite_0052C3E4_0052C428.bin
        INCBIN  build\spritecontainer\sprite_0052C428_0052C568.bin
        INCBIN  build\spritecontainer\sprite_0052C568_0052C5AC.bin
        INCBIN  build\spritecontainer\sprite_0052C5AC_0052D5B8.bin
        INCBIN  build\spritecontainer\sprite_0052D5B8_0052D6F8.bin
        INCBIN  build\spritecontainer\sprite_0052D6F8_0052D73C.bin
        INCBIN  build\spritecontainer\sprite_0052D73C_0052DB20.bin
        INCBIN  build\spritecontainer\sprite_0052DB20_0052DB70.bin
        INCBIN  build\spritecontainer\sprite_0052DB70_0052DB84.bin
        INCBIN  build\spritecontainer\sprite_0052DB84_0052E788.bin
        INCBIN  build\spritecontainer\sprite_0052E788_0052E878.bin
        INCBIN  build\spritecontainer\sprite_0052E878_0052E8AC.bin
        INCBIN  build\spritecontainer\sprite_0052E8AC_0052ED88.bin
        INCBIN  build\spritecontainer\sprite_0052ED88_0052EDD8.bin
        INCBIN  build\spritecontainer\sprite_0052EDD8_0052EE1C.bin
        INCBIN  build\spritecontainer\sprite_0052EE1C_0052F504.bin
        INCBIN  build\spritecontainer\sprite_0052F504_0052F5A4.bin
        INCBIN  build\spritecontainer\sprite_0052F5A4_0052F5C8.bin
        INCBIN  build\spritecontainer\sprite_0052F5C8_0052F8C8.bin
        INCBIN  build\spritecontainer\sprite_0052F8C8_0052F8F0.bin
        INCBIN  build\spritecontainer\sprite_0052F8F0_0052F914.bin
        INCBIN  build\spritecontainer\sprite_0052F914_005304B8.bin
        INCBIN  build\spritecontainer\sprite_005304B8_005305A8.bin
        INCBIN  build\spritecontainer\sprite_005305A8_005305DC.bin
        INCBIN  build\spritecontainer\sprite_005305DC_00531160.bin
        INCBIN  build\spritecontainer\sprite_00531160_005312A0.bin
        INCBIN  build\spritecontainer\sprite_005312A0_005312E4.bin
        INCBIN  build\spritecontainer\sprite_005312E4_005316B0.bin
        INCBIN  build\spritecontainer\sprite_005316B0_00531750.bin
        INCBIN  build\spritecontainer\sprite_00531750_00531794.bin
        INCBIN  build\spritecontainer\sprite_00531794_00532350.bin
        INCBIN  build\spritecontainer\sprite_00532350_00532440.bin
        INCBIN  build\spritecontainer\sprite_00532440_00532474.bin
        INCBIN  build\spritecontainer\sprite_00532474_00532AF8.bin
        INCBIN  build\spritecontainer\sprite_00532AF8_00532BE8.bin
        INCBIN  build\spritecontainer\sprite_00532BE8_00532C1C.bin
|unk_08532C1C|
        INCBIN  build\spritecontainer\sprite_00532C1C_00532DCC.bin
        INCBIN  build\spritecontainer\sprite_00532DCC_00532E1C.bin
        INCBIN  build\spritecontainer\sprite_00532E1C_00533218.bin
        INCBIN  build\spritecontainer\sprite_00533218_005332B8.bin
        INCBIN  build\spritecontainer\sprite_005332B8_005332DC.bin
        INCBIN  build\spritecontainer\sprite_005332DC_00533C28.bin
        INCBIN  build\spritecontainer\sprite_00533C28_00533D68.bin
        INCBIN  build\spritecontainer\sprite_00533D68_00533DAC.bin
        INCBIN  build\spritecontainer\sprite_00533DAC_005347E0.bin
        INCBIN  build\spritecontainer\sprite_005347E0_00534920.bin
        INCBIN  build\spritecontainer\sprite_00534920_00534964.bin
        INCBIN  build\spritecontainer\sprite_00534964_005350E0.bin
        INCBIN  build\spritecontainer\sprite_005350E0_005351D0.bin
        INCBIN  build\spritecontainer\sprite_005351D0_00535204.bin
        INCBIN  build\spritecontainer\sprite_00535204_00535DDC.bin
        INCBIN  build\spritecontainer\sprite_00535DDC_00535F1C.bin
        INCBIN  build\spritecontainer\sprite_00535F1C_00535F60.bin
        INCBIN  build\spritecontainer\sprite_00535F60_00536A30.bin
        INCBIN  build\spritecontainer\sprite_00536A30_00536B70.bin
        INCBIN  build\spritecontainer\sprite_00536B70_00536BB4.bin
        INCBIN  build\spritecontainer\sprite_00536BB4_00536DE8.bin
        INCBIN  build\spritecontainer\sprite_00536DE8_00536E38.bin
        INCBIN  build\spritecontainer\sprite_00536E38_00536E4C.bin
        INCBIN  build\spritecontainer\sprite_00536E4C_0053714C.bin
        INCBIN  build\spritecontainer\sprite_0053714C_0053719C.bin
        INCBIN  build\spritecontainer\sprite_0053719C_005371E0.bin
        INCBIN  build\spritecontainer\sprite_005371E0_00537974.bin
        INCBIN  build\spritecontainer\sprite_00537974_00537A64.bin
        INCBIN  build\spritecontainer\sprite_00537A64_00537A98.bin
        INCBIN  build\spritecontainer\sprite_00537A98_005380A8.bin
        INCBIN  build\spritecontainer\sprite_005380A8_00538184.bin
        INCBIN  build\spritecontainer\sprite_00538184_00538238.bin
        INCBIN  build\spritecontainer\sprite_00538238_00538638.bin
        INCBIN  build\spritecontainer\sprite_00538638_005386D8.bin
        INCBIN  build\spritecontainer\sprite_005386D8_005386FC.bin
        INCBIN  build\spritecontainer\sprite_005386FC_005388E0.bin
        INCBIN  build\spritecontainer\sprite_005388E0_00538908.bin
        INCBIN  build\spritecontainer\sprite_00538908_0053892C.bin
        INCBIN  build\spritecontainer\sprite_0053892C_00538FE0.bin
        INCBIN  build\spritecontainer\sprite_00538FE0_005390D0.bin
        INCBIN  build\spritecontainer\sprite_005390D0_00539104.bin
        INCBIN  build\spritecontainer\sprite_00539104_00539864.bin
        INCBIN  build\spritecontainer\sprite_00539864_005399A4.bin
        INCBIN  build\spritecontainer\sprite_005399A4_005399E8.bin
        INCBIN  build\spritecontainer\sprite_005399E8_0053A08C.bin
        INCBIN  build\spritecontainer\sprite_0053A08C_0053A1CC.bin
        INCBIN  build\spritecontainer\sprite_0053A1CC_0053A210.bin
        INCBIN  build\spritecontainer\sprite_0053A210_0053A540.bin
        INCBIN  build\spritecontainer\sprite_0053A540_0053A5E0.bin
        INCBIN  build\spritecontainer\sprite_0053A5E0_0053A624.bin
        INCBIN  build\spritecontainer\sprite_0053A624_0053AD5C.bin
        INCBIN  build\spritecontainer\sprite_0053AD5C_0053AE4C.bin
        INCBIN  build\spritecontainer\sprite_0053AE4C_0053AE80.bin
        INCBIN  build\spritecontainer\sprite_0053AE80_0053B9D8.bin
        INCBIN  build\spritecontainer\sprite_0053B9D8_0053BB18.bin
        INCBIN  build\spritecontainer\sprite_0053BB18_0053BB5C.bin
        INCBIN  build\spritecontainer\sprite_0053BB5C_0053BF04.bin
        INCBIN  build\spritecontainer\sprite_0053BF04_0053BF40.bin
        INCBIN  build\spritecontainer\sprite_0053BF40_0053BF74.bin
        INCBIN  build\spritecontainer\sprite_0053BF74_0053CA0C.bin
        INCBIN  build\spritecontainer\sprite_0053CA0C_0053CBC4.bin
        INCBIN  build\spritecontainer\sprite_0053CBC4_0053CC78.bin
        INCBIN  build\spritecontainer\sprite_0053CC78_0053D144.bin
        INCBIN  build\spritecontainer\sprite_0053D144_0053D1E4.bin
        INCBIN  build\spritecontainer\sprite_0053D1E4_0053D208.bin
        INCBIN  build\spritecontainer\sprite_0053D208_0053DDA8.bin
        INCBIN  build\spritecontainer\sprite_0053DDA8_0053DEE8.bin
        INCBIN  build\spritecontainer\sprite_0053DEE8_0053DF2C.bin
        INCBIN  build\spritecontainer\sprite_0053DF2C_0053EB60.bin
        INCBIN  build\spritecontainer\sprite_0053EB60_0053ECA0.bin
        INCBIN  build\spritecontainer\sprite_0053ECA0_0053ECE4.bin
        INCBIN  build\spritecontainer\sprite_0053ECE4_0053F5E8.bin
        INCBIN  build\spritecontainer\sprite_0053F5E8_0053F6D8.bin
        INCBIN  build\spritecontainer\sprite_0053F6D8_0053F70C.bin
        INCBIN  build\spritecontainer\sprite_0053F70C_00540524.bin
        INCBIN  build\spritecontainer\sprite_00540524_00540664.bin
        INCBIN  build\spritecontainer\sprite_00540664_005406A8.bin
        INCBIN  build\spritecontainer\sprite_005406A8_005413A4.bin
        INCBIN  build\spritecontainer\sprite_005413A4_005414E4.bin
        INCBIN  build\spritecontainer\sprite_005414E4_00541528.bin
        INCBIN  build\spritecontainer\sprite_00541528_005417F8.bin
        INCBIN  build\spritecontainer\sprite_005417F8_00541848.bin
        INCBIN  build\spritecontainer\sprite_00541848_0054185C.bin
        INCBIN  build\spritecontainer\sprite_0054185C_0054215C.bin
        INCBIN  build\spritecontainer\sprite_0054215C_0054224C.bin
        INCBIN  build\spritecontainer\sprite_0054224C_00542280.bin
        INCBIN  build\spritecontainer\sprite_00542280_005426D4.bin
        INCBIN  build\spritecontainer\sprite_005426D4_00542724.bin
        INCBIN  build\spritecontainer\sprite_00542724_00542768.bin
        INCBIN  build\spritecontainer\sprite_00542768_00542D14.bin
        INCBIN  build\spritecontainer\sprite_00542D14_00542DB4.bin
        INCBIN  build\spritecontainer\sprite_00542DB4_00542DD8.bin
        INCBIN  build\spritecontainer\sprite_00542DD8_00542FF4.bin
        INCBIN  build\spritecontainer\sprite_00542FF4_0054301C.bin
        INCBIN  build\spritecontainer\sprite_0054301C_00543040.bin
        INCBIN  build\spritecontainer\sprite_00543040_005438B8.bin
        INCBIN  build\spritecontainer\sprite_005438B8_005439A8.bin
        INCBIN  build\spritecontainer\sprite_005439A8_005439DC.bin
        INCBIN  build\spritecontainer\sprite_005439DC_005442F8.bin
        INCBIN  build\spritecontainer\sprite_005442F8_00544438.bin
        INCBIN  build\spritecontainer\sprite_00544438_0054447C.bin
        INCBIN  build\spritecontainer\sprite_0054447C_0054476C.bin
        INCBIN  build\spritecontainer\sprite_0054476C_0054480C.bin
        INCBIN  build\spritecontainer\sprite_0054480C_00544850.bin
        INCBIN  build\spritecontainer\sprite_00544850_005450F8.bin
        INCBIN  build\spritecontainer\sprite_005450F8_005451E8.bin
        INCBIN  build\spritecontainer\sprite_005451E8_0054521C.bin
        INCBIN  build\spritecontainer\sprite_0054521C_00545F44.bin
        INCBIN  build\spritecontainer\sprite_00545F44_00546084.bin
        INCBIN  build\spritecontainer\sprite_00546084_005460C8.bin
        INCBIN  build\spritecontainer\sprite_005460C8_00546C9C.bin
        INCBIN  build\spritecontainer\sprite_00546C9C_00546E54.bin
        INCBIN  build\spritecontainer\sprite_00546E54_00546F08.bin
        INCBIN  build\spritecontainer\sprite_00546F08_0054734C.bin
        INCBIN  build\spritecontainer\sprite_0054734C_005473EC.bin
        INCBIN  build\spritecontainer\sprite_005473EC_00547410.bin
        INCBIN  build\spritecontainer\sprite_00547410_00547E24.bin
        INCBIN  build\spritecontainer\sprite_00547E24_00547F64.bin
        INCBIN  build\spritecontainer\sprite_00547F64_00547FA8.bin
        INCBIN  build\spritecontainer\sprite_00547FA8_005484B8.bin
        INCBIN  build\spritecontainer\sprite_005484B8_00548558.bin
        INCBIN  build\spritecontainer\sprite_00548558_0054857C.bin
        INCBIN  build\spritecontainer\sprite_0054857C_0054916C.bin
        INCBIN  build\spritecontainer\sprite_0054916C_005492AC.bin
        INCBIN  build\spritecontainer\sprite_005492AC_005492F0.bin
        INCBIN  build\spritecontainer\sprite_005492F0_00549F08.bin
        INCBIN  build\spritecontainer\sprite_00549F08_0054A048.bin
        INCBIN  build\spritecontainer\sprite_0054A048_0054A08C.bin
        INCBIN  build\spritecontainer\sprite_0054A08C_0054AA28.bin
        INCBIN  build\spritecontainer\sprite_0054AA28_0054AB18.bin
        INCBIN  build\spritecontainer\sprite_0054AB18_0054AB4C.bin
        INCBIN  build\spritecontainer\sprite_0054AB4C_0054B7F4.bin
        INCBIN  build\spritecontainer\sprite_0054B7F4_0054B934.bin
        INCBIN  build\spritecontainer\sprite_0054B934_0054B978.bin
        INCBIN  build\spritecontainer\sprite_0054B978_0054C6FC.bin
        INCBIN  build\spritecontainer\sprite_0054C6FC_0054C83C.bin
        INCBIN  build\spritecontainer\sprite_0054C83C_0054C880.bin
        INCBIN  build\spritecontainer\sprite_0054C880_0054CB74.bin
        INCBIN  build\spritecontainer\sprite_0054CB74_0054CBC4.bin
        INCBIN  build\spritecontainer\sprite_0054CBC4_0054CBD8.bin
        INCBIN  build\spritecontainer\sprite_0054CBD8_0054CF50.bin
        INCBIN  build\spritecontainer\sprite_0054CF50_0054CF8C.bin
        INCBIN  build\spritecontainer\sprite_0054CF8C_0054CFC0.bin
        INCBIN  build\spritecontainer\sprite_0054CFC0_0054D8D8.bin
        INCBIN  build\spritecontainer\sprite_0054D8D8_0054D9C8.bin
        INCBIN  build\spritecontainer\sprite_0054D9C8_0054D9FC.bin
        INCBIN  build\spritecontainer\sprite_0054D9FC_0054DFB0.bin
        INCBIN  build\spritecontainer\sprite_0054DFB0_0054E08C.bin
        INCBIN  build\spritecontainer\sprite_0054E08C_0054E140.bin
        INCBIN  build\spritecontainer\sprite_0054E140_0054E648.bin
        INCBIN  build\spritecontainer\sprite_0054E648_0054E6E8.bin
        INCBIN  build\spritecontainer\sprite_0054E6E8_0054E70C.bin
        INCBIN  build\spritecontainer\sprite_0054E70C_0054E928.bin
        INCBIN  build\spritecontainer\sprite_0054E928_0054E950.bin
        INCBIN  build\spritecontainer\sprite_0054E950_0054E974.bin
        INCBIN  build\spritecontainer\sprite_0054E974_0054F238.bin
        INCBIN  build\spritecontainer\sprite_0054F238_0054F328.bin
        INCBIN  build\spritecontainer\sprite_0054F328_0054F35C.bin
        INCBIN  build\spritecontainer\sprite_0054F35C_0054FCC4.bin
        INCBIN  build\spritecontainer\sprite_0054FCC4_0054FE04.bin
        INCBIN  build\spritecontainer\sprite_0054FE04_0054FE48.bin
        INCBIN  build\spritecontainer\sprite_0054FE48_005506B4.bin
        INCBIN  build\spritecontainer\sprite_005506B4_005507F4.bin
        INCBIN  build\spritecontainer\sprite_005507F4_00550838.bin
        INCBIN  build\spritecontainer\sprite_00550838_00550BD0.bin
        INCBIN  build\spritecontainer\sprite_00550BD0_00550C70.bin
        INCBIN  build\spritecontainer\sprite_00550C70_00550CB4.bin
        INCBIN  build\spritecontainer\sprite_00550CB4_00550DE0.bin
        INCBIN  build\spritecontainer\sprite_00550DE0_00550DF4.bin
        INCBIN  build\spritecontainer\sprite_00550DF4_00550E08.bin
        INCBIN  build\spritecontainer\sprite_00550E08_00551EF0.bin
        INCBIN  build\spritecontainer\sprite_00551EF0_00552080.bin
        INCBIN  build\spritecontainer\sprite_00552080_005520D4.bin
        INCBIN  build\spritecontainer\sprite_005520D4_00552208.bin
        INCBIN  build\spritecontainer\sprite_00552208_0055221C.bin
        INCBIN  build\spritecontainer\sprite_0055221C_00552230.bin
        INCBIN  build\spritecontainer\sprite_00552230_005524AC.bin
        INCBIN  build\spritecontainer\sprite_005524AC_005524D4.bin
        INCBIN  build\spritecontainer\sprite_005524D4_005524F8.bin
        INCBIN  build\spritecontainer\sprite_005524F8_005528F8.bin
        INCBIN  build\spritecontainer\sprite_005528F8_00552934.bin
        INCBIN  build\spritecontainer\sprite_00552934_00552968.bin
        INCBIN  build\spritecontainer\sprite_00552968_00552B9C.bin
        INCBIN  build\spritecontainer\sprite_00552B9C_00552BC4.bin
        INCBIN  build\spritecontainer\sprite_00552BC4_00552BE8.bin
        INCBIN  build\spritecontainer\sprite_00552BE8_00552F38.bin
        INCBIN  build\spritecontainer\sprite_00552F38_00552F74.bin
        INCBIN  build\spritecontainer\sprite_00552F74_00552FA8.bin
        INCBIN  build\spritecontainer\sprite_00552FA8_005534CC.bin
        INCBIN  build\spritecontainer\sprite_005534CC_0055356C.bin
        INCBIN  build\spritecontainer\sprite_0055356C_00553590.bin
        INCBIN  build\spritecontainer\sprite_00553590_005541D4.bin
        INCBIN  build\spritecontainer\sprite_005541D4_00554314.bin
        INCBIN  build\spritecontainer\sprite_00554314_00554358.bin
        INCBIN  build\spritecontainer\sprite_00554358_00555018.bin
        INCBIN  build\spritecontainer\sprite_00555018_00555158.bin
        INCBIN  build\spritecontainer\sprite_00555158_0055519C.bin
        INCBIN  build\spritecontainer\sprite_0055519C_00555B84.bin
        INCBIN  build\spritecontainer\sprite_00555B84_00555C74.bin
        INCBIN  build\spritecontainer\sprite_00555C74_00555CA8.bin
        INCBIN  build\spritecontainer\sprite_00555CA8_00556A00.bin
        INCBIN  build\spritecontainer\sprite_00556A00_00556B40.bin
        INCBIN  build\spritecontainer\sprite_00556B40_00556B84.bin
        INCBIN  build\spritecontainer\sprite_00556B84_0055795C.bin
        INCBIN  build\spritecontainer\sprite_0055795C_00557A9C.bin
        INCBIN  build\spritecontainer\sprite_00557A9C_00557AE0.bin
        INCBIN  build\spritecontainer\sprite_00557AE0_00557DE0.bin
        INCBIN  build\spritecontainer\sprite_00557DE0_00557E30.bin
        INCBIN  build\spritecontainer\sprite_00557E30_00557E44.bin
        INCBIN  build\spritecontainer\sprite_00557E44_00558798.bin
        INCBIN  build\spritecontainer\sprite_00558798_00558888.bin
        INCBIN  build\spritecontainer\sprite_00558888_005588BC.bin
        INCBIN  build\spritecontainer\sprite_005588BC_00558FB0.bin
        INCBIN  build\spritecontainer\sprite_00558FB0_0055908C.bin
        INCBIN  build\spritecontainer\sprite_0055908C_00559140.bin
        INCBIN  build\spritecontainer\sprite_00559140_0055975C.bin
        INCBIN  build\spritecontainer\sprite_0055975C_005597C0.bin
        INCBIN  build\spritecontainer\sprite_005597C0_00559814.bin
        INCBIN  build\spritecontainer\sprite_00559814_00559C34.bin
        INCBIN  build\spritecontainer\sprite_00559C34_00559CD4.bin
        INCBIN  build\spritecontainer\sprite_00559CD4_00559CF8.bin
        INCBIN  build\spritecontainer\sprite_00559CF8_00559F18.bin
        INCBIN  build\spritecontainer\sprite_00559F18_00559F40.bin
        INCBIN  build\spritecontainer\sprite_00559F40_00559F64.bin
        INCBIN  build\spritecontainer\sprite_00559F64_0055A860.bin
        INCBIN  build\spritecontainer\sprite_0055A860_0055A950.bin
        INCBIN  build\spritecontainer\sprite_0055A950_0055A984.bin
        INCBIN  build\spritecontainer\sprite_0055A984_0055B374.bin
        INCBIN  build\spritecontainer\sprite_0055B374_0055B4B4.bin
        INCBIN  build\spritecontainer\sprite_0055B4B4_0055B4F8.bin
        INCBIN  build\spritecontainer\sprite_0055B4F8_0055B8C8.bin
        INCBIN  build\spritecontainer\sprite_0055B8C8_0055B968.bin
        INCBIN  build\spritecontainer\sprite_0055B968_0055B9AC.bin
        INCBIN  build\spritecontainer\sprite_0055B9AC_0055BADC.bin
        INCBIN  build\spritecontainer\sprite_0055BADC_0055BAF0.bin
        INCBIN  build\spritecontainer\sprite_0055BAF0_0055BB04.bin
        INCBIN  build\spritecontainer\sprite_0055BB04_0055CC6C.bin
        INCBIN  build\spritecontainer\sprite_0055CC6C_0055CDFC.bin
        INCBIN  build\spritecontainer\sprite_0055CDFC_0055CE50.bin
        INCBIN  build\spritecontainer\sprite_0055CE50_0055D360.bin
        INCBIN  build\spritecontainer\sprite_0055D360_0055D400.bin
        INCBIN  build\spritecontainer\sprite_0055D400_0055D424.bin
        INCBIN  build\spritecontainer\sprite_0055D424_0055E360.bin
        INCBIN  build\spritecontainer\sprite_0055E360_0055E4A0.bin
        INCBIN  build\spritecontainer\sprite_0055E4A0_0055E4E4.bin
        INCBIN  build\spritecontainer\sprite_0055E4E4_0055F47C.bin
        INCBIN  build\spritecontainer\sprite_0055F47C_0055F5BC.bin
        INCBIN  build\spritecontainer\sprite_0055F5BC_0055F600.bin
        INCBIN  build\spritecontainer\sprite_0055F600_005601C0.bin
        INCBIN  build\spritecontainer\sprite_005601C0_005602B0.bin
        INCBIN  build\spritecontainer\sprite_005602B0_005602E4.bin
        INCBIN  build\spritecontainer\sprite_005602E4_005611E0.bin
        INCBIN  build\spritecontainer\sprite_005611E0_00561320.bin
        INCBIN  build\spritecontainer\sprite_00561320_00561364.bin
        INCBIN  build\spritecontainer\sprite_00561364_00562328.bin
        INCBIN  build\spritecontainer\sprite_00562328_00562468.bin
        INCBIN  build\spritecontainer\sprite_00562468_005624AC.bin
        INCBIN  build\spritecontainer\sprite_005624AC_0056286C.bin
        INCBIN  build\spritecontainer\sprite_0056286C_005628BC.bin
        INCBIN  build\spritecontainer\sprite_005628BC_005628D0.bin
        INCBIN  build\spritecontainer\sprite_005628D0_00563490.bin
        INCBIN  build\spritecontainer\sprite_00563490_00563580.bin
        INCBIN  build\spritecontainer\sprite_00563580_005635B4.bin
        INCBIN  build\spritecontainer\sprite_005635B4_00563C1C.bin
        INCBIN  build\spritecontainer\sprite_00563C1C_00563C80.bin
        INCBIN  build\spritecontainer\sprite_00563C80_00563CD4.bin
        INCBIN  build\spritecontainer\sprite_00563CD4_00564494.bin
        INCBIN  build\spritecontainer\sprite_00564494_00564534.bin
        INCBIN  build\spritecontainer\sprite_00564534_00564558.bin
        INCBIN  build\spritecontainer\sprite_00564558_00564804.bin
        INCBIN  build\spritecontainer\sprite_00564804_0056482C.bin
        INCBIN  build\spritecontainer\sprite_0056482C_00564850.bin
        INCBIN  build\spritecontainer\sprite_00564850_00565368.bin
        INCBIN  build\spritecontainer\sprite_00565368_00565458.bin
        INCBIN  build\spritecontainer\sprite_00565458_0056548C.bin
        INCBIN  build\spritecontainer\sprite_0056548C_00566004.bin
        INCBIN  build\spritecontainer\sprite_00566004_00566144.bin
        INCBIN  build\spritecontainer\sprite_00566144_00566188.bin
        INCBIN  build\spritecontainer\sprite_00566188_005664EC.bin
        INCBIN  build\spritecontainer\sprite_005664EC_0056658C.bin
        INCBIN  build\spritecontainer\sprite_0056658C_005665D0.bin
        INCBIN  build\spritecontainer\sprite_005665D0_00566758.bin
        INCBIN  build\spritecontainer\sprite_00566758_0056676C.bin
        INCBIN  build\spritecontainer\sprite_0056676C_00566780.bin
        INCBIN  build\spritecontainer\sprite_00566780_00567AD4.bin
        INCBIN  build\spritecontainer\sprite_00567AD4_00567C64.bin
        INCBIN  build\spritecontainer\sprite_00567C64_00567CB8.bin
        INCBIN  build\spritecontainer\sprite_00567CB8_005680D8.bin
        INCBIN  build\spritecontainer\sprite_005680D8_00568178.bin
        INCBIN  build\spritecontainer\sprite_00568178_0056819C.bin
        INCBIN  build\spritecontainer\sprite_0056819C_00569204.bin
        INCBIN  build\spritecontainer\sprite_00569204_00569344.bin
        INCBIN  build\spritecontainer\sprite_00569344_00569388.bin
        INCBIN  build\spritecontainer\sprite_00569388_00569510.bin
        INCBIN  build\spritecontainer\sprite_00569510_00569524.bin
        INCBIN  build\spritecontainer\sprite_00569524_00569538.bin
        INCBIN  build\spritecontainer\sprite_00569538_005696DC.bin
        INCBIN  build\spritecontainer\sprite_005696DC_00569704.bin
        INCBIN  build\spritecontainer\sprite_00569704_00569728.bin
        INCBIN  build\spritecontainer\sprite_00569728_005698D8.bin
        INCBIN  build\spritecontainer\sprite_005698D8_00569A18.bin
        INCBIN  build\spritecontainer\sprite_00569A18_00569A5C.bin
        INCBIN  build\spritecontainer\sprite_00569A5C_0056A0D4.bin
        INCBIN  build\spritecontainer\sprite_0056A0D4_0056A174.bin
        INCBIN  build\spritecontainer\sprite_0056A174_0056A198.bin
        INCBIN  build\spritecontainer\sprite_0056A198_0056AEA0.bin
        INCBIN  build\spritecontainer\sprite_0056AEA0_0056AFE0.bin
        INCBIN  build\spritecontainer\sprite_0056AFE0_0056B024.bin
        INCBIN  build\spritecontainer\sprite_0056B024_0056BF0C.bin
        INCBIN  build\spritecontainer\sprite_0056BF0C_0056C04C.bin
        INCBIN  build\spritecontainer\sprite_0056C04C_0056C090.bin
        INCBIN  build\spritecontainer\sprite_0056C090_0056C3B0.bin
        INCBIN  build\spritecontainer\sprite_0056C3B0_0056C400.bin
        INCBIN  build\spritecontainer\sprite_0056C400_0056C414.bin
        INCBIN  build\spritecontainer\sprite_0056C414_0056CFDC.bin
        INCBIN  build\spritecontainer\sprite_0056CFDC_0056D0CC.bin
        INCBIN  build\spritecontainer\sprite_0056D0CC_0056D100.bin
        INCBIN  build\spritecontainer\sprite_0056D100_0056E078.bin
        INCBIN  build\spritecontainer\sprite_0056E078_0056E1B8.bin
        INCBIN  build\spritecontainer\sprite_0056E1B8_0056E1FC.bin
        INCBIN  build\spritecontainer\sprite_0056E1FC_0056E644.bin
        INCBIN  build\spritecontainer\sprite_0056E644_0056E6E4.bin
        INCBIN  build\spritecontainer\sprite_0056E6E4_0056E708.bin
        INCBIN  build\spritecontainer\sprite_0056E708_0056F118.bin
        INCBIN  build\spritecontainer\sprite_0056F118_0056F258.bin
        INCBIN  build\spritecontainer\sprite_0056F258_0056F29C.bin
        INCBIN  build\spritecontainer\sprite_0056F29C_0056FD60.bin
        INCBIN  build\spritecontainer\sprite_0056FD60_0056FEA0.bin
        INCBIN  build\spritecontainer\sprite_0056FEA0_0056FEE4.bin
        INCBIN  build\spritecontainer\sprite_0056FEE4_00570710.bin
        INCBIN  build\spritecontainer\sprite_00570710_00570800.bin
        INCBIN  build\spritecontainer\sprite_00570800_00570834.bin
        INCBIN  build\spritecontainer\sprite_00570834_00571424.bin
        INCBIN  build\spritecontainer\sprite_00571424_00571564.bin
        INCBIN  build\spritecontainer\sprite_00571564_005715A8.bin
        INCBIN  build\spritecontainer\sprite_005715A8_005720EC.bin
        INCBIN  build\spritecontainer\sprite_005720EC_0057222C.bin
        INCBIN  build\spritecontainer\sprite_0057222C_00572270.bin
        INCBIN  build\spritecontainer\sprite_00572270_005724A0.bin
        INCBIN  build\spritecontainer\sprite_005724A0_005724F0.bin
        INCBIN  build\spritecontainer\sprite_005724F0_00572504.bin
        INCBIN  build\spritecontainer\sprite_00572504_00572C74.bin
        INCBIN  build\spritecontainer\sprite_00572C74_00572D64.bin
        INCBIN  build\spritecontainer\sprite_00572D64_00572D98.bin
        INCBIN  build\spritecontainer\sprite_00572D98_00572F94.bin
        INCBIN  build\spritecontainer\sprite_00572F94_00572FBC.bin
        INCBIN  build\spritecontainer\sprite_00572FBC_00572FE0.bin
        INCBIN  build\spritecontainer\sprite_00572FE0_00573358.bin
        INCBIN  build\spritecontainer\sprite_00573358_005733F8.bin
        INCBIN  build\spritecontainer\sprite_005733F8_0057343C.bin
        INCBIN  build\spritecontainer\sprite_0057343C_0057355C.bin
        INCBIN  build\spritecontainer\sprite_0057355C_00573570.bin
        INCBIN  build\spritecontainer\sprite_00573570_00573584.bin
        INCBIN  build\spritecontainer\sprite_00573584_00573A90.bin
        INCBIN  build\spritecontainer\sprite_00573A90_00573B30.bin
        INCBIN  build\spritecontainer\sprite_00573B30_00573B54.bin
        INCBIN  build\spritecontainer\sprite_00573B54_0057472C.bin
        INCBIN  build\spritecontainer\sprite_0057472C_0057486C.bin
        INCBIN  build\spritecontainer\sprite_0057486C_005748B0.bin
        INCBIN  build\spritecontainer\sprite_005748B0_00574EAC.bin
        INCBIN  build\spritecontainer\sprite_00574EAC_00574F4C.bin
        INCBIN  build\spritecontainer\sprite_00574F4C_00574F70.bin
        INCBIN  build\spritecontainer\sprite_00574F70_00575430.bin
        INCBIN  build\spritecontainer\sprite_00575430_005754D0.bin
        INCBIN  build\spritecontainer\sprite_005754D0_005754F4.bin
        INCBIN  build\spritecontainer\sprite_005754F4_0057607C.bin
        INCBIN  build\spritecontainer\sprite_0057607C_005761BC.bin
        INCBIN  build\spritecontainer\sprite_005761BC_00576200.bin
        INCBIN  build\spritecontainer\sprite_00576200_00576FD8.bin
        INCBIN  build\spritecontainer\sprite_00576FD8_00577118.bin
        INCBIN  build\spritecontainer\sprite_00577118_0057715C.bin
        INCBIN  build\spritecontainer\sprite_0057715C_0057741C.bin
        INCBIN  build\spritecontainer\sprite_0057741C_0057746C.bin
        INCBIN  build\spritecontainer\sprite_0057746C_00577480.bin
        INCBIN  build\spritecontainer\sprite_00577480_00577DDC.bin
        INCBIN  build\spritecontainer\sprite_00577DDC_00577ECC.bin
        INCBIN  build\spritecontainer\sprite_00577ECC_00577F00.bin
        INCBIN  build\spritecontainer\sprite_00577F00_005783C0.bin
        INCBIN  build\spritecontainer\sprite_005783C0_00578460.bin
        INCBIN  build\spritecontainer\sprite_00578460_00578484.bin
        INCBIN  build\spritecontainer\sprite_00578484_0057886C.bin
        INCBIN  build\spritecontainer\sprite_0057886C_0057890C.bin
        INCBIN  build\spritecontainer\sprite_0057890C_00578950.bin
        INCBIN  build\spritecontainer\sprite_00578950_00578C54.bin
        INCBIN  build\spritecontainer\sprite_00578C54_00578C7C.bin
        INCBIN  build\spritecontainer\sprite_00578C7C_00578CA0.bin
        INCBIN  build\spritecontainer\sprite_00578CA0_00578F9C.bin
        INCBIN  build\spritecontainer\sprite_00578F9C_00578FC4.bin
        INCBIN  build\spritecontainer\sprite_00578FC4_00578FE8.bin
        INCBIN  build\spritecontainer\sprite_00578FE8_00579890.bin
        INCBIN  build\spritecontainer\sprite_00579890_00579900.bin
        INCBIN  build\spritecontainer\sprite_00579900_00579924.bin
        INCBIN  build\spritecontainer\sprite_00579924_00579A3C.bin
        INCBIN  build\spritecontainer\sprite_00579A3C_00579A64.bin
        INCBIN  build\spritecontainer\sprite_00579A64_00579A88.bin
        INCBIN  build\spritecontainer\sprite_00579A88_00579C9C.bin
        INCBIN  build\spritecontainer\sprite_00579C9C_00579CD8.bin
        INCBIN  build\spritecontainer\sprite_00579CD8_00579D0C.bin
        INCBIN  build\spritecontainer\sprite_00579D0C_0057A1D4.bin
        INCBIN  build\spritecontainer\sprite_0057A1D4_0057A260.bin
        INCBIN  build\spritecontainer\sprite_0057A260_0057A2D4.bin
        INCBIN  build\spritecontainer\sprite_0057A2D4_0057A2FC.bin
        INCBIN  build\spritecontainer\sprite_0057A2FC_0057A320.bin
        INCBIN  build\spritecontainer\sprite_0057A320_0057A35C.bin
        INCBIN  build\spritecontainer\sprite_0057A35C_0057A390.bin
        INCBIN  build\spritecontainer\sprite_0057A390_0057A41C.bin
        INCBIN  build\spritecontainer\sprite_0057A41C_0057A490.bin
        INCBIN  build\spritecontainer\sprite_0057A490_0057AF58.bin
        INCBIN  build\spritecontainer\sprite_0057AF58_0057AFA8.bin
        INCBIN  build\spritecontainer\sprite_0057AFA8_0057AFEC.bin
        INCBIN  build\spritecontainer\sprite_0057AFEC_0057B7C0.bin
        INCBIN  build\spritecontainer\sprite_0057B7C0_0057B7FC.bin
        INCBIN  build\spritecontainer\sprite_0057B7FC_0057B830.bin
        INCBIN  build\spritecontainer\sprite_0057B830_0057B880.bin
        INCBIN  build\spritecontainer\sprite_0057B880_0057B8C4.bin
        INCBIN  build\spritecontainer\sprite_0057B8C4_0057C27C.bin
        INCBIN  build\spritecontainer\sprite_0057C27C_0057C2B8.bin
        INCBIN  build\spritecontainer\sprite_0057C2B8_0057C2EC.bin
        INCBIN  build\spritecontainer\sprite_0057C2EC_0057C2FC.bin
        INCBIN  build\spritecontainer\sprite_0057C2FC_0057C324.bin
        INCBIN  build\spritecontainer\sprite_0057C324_0057C348.bin
        INCBIN  build\spritecontainer\sprite_0057C348_0057C728.bin
        INCBIN  build\spritecontainer\sprite_0057C728_0057C908.bin
        INCBIN  build\spritecontainer\sprite_0057C908_0057C96C.bin
        INCBIN  build\spritecontainer\sprite_0057C96C_0057CB4C.bin
        INCBIN  build\spritecontainer\sprite_0057CB4C_0057CBB0.bin
        INCBIN  build\spritecontainer\sprite_0057CBB0_0057CBD8.bin
        INCBIN  build\spritecontainer\sprite_0057CBD8_0057CBFC.bin
        INCBIN  build\spritecontainer\sprite_0057CBFC_0057CD3C.bin
        INCBIN  build\spritecontainer\sprite_0057CD3C_0057CD80.bin
        INCBIN  build\spritecontainer\sprite_0057CD80_0057CF20.bin
        INCBIN  build\spritecontainer\sprite_0057CF20_0057D420.bin
        INCBIN  build\spritecontainer\sprite_0057D420_0057D524.bin
        INCBIN  build\spritecontainer\sprite_0057D524_0057DA24.bin
        INCBIN  build\spritecontainer\sprite_0057DA24_0057DB28.bin
        INCBIN  build\spritecontainer\sprite_0057DB28_0057DD78.bin
        INCBIN  build\spritecontainer\sprite_0057DD78_0057DDA0.bin
        INCBIN  build\spritecontainer\sprite_0057DDA0_0057DDC4.bin
        INCBIN  build\spritecontainer\sprite_0057DDC4_0057E178.bin
        INCBIN  build\spritecontainer\sprite_0057E178_0057E1B4.bin
        INCBIN  build\spritecontainer\sprite_0057E1B4_0057E1E8.bin
        INCBIN  build\spritecontainer\sprite_0057E1E8_0057E310.bin
        INCBIN  build\spritecontainer\sprite_0057E310_0057E324.bin
        INCBIN  build\spritecontainer\sprite_0057E324_0057E338.bin
        INCBIN  build\spritecontainer\sprite_0057E338_0057E874.bin
        INCBIN  build\spritecontainer\sprite_0057E874_0057E914.bin
        INCBIN  build\spritecontainer\sprite_0057E914_0057E938.bin
        INCBIN  build\spritecontainer\sprite_0057E938_0057F324.bin
        INCBIN  build\spritecontainer\sprite_0057F324_0057F414.bin
        INCBIN  build\spritecontainer\sprite_0057F414_0057F448.bin
        INCBIN  build\spritecontainer\sprite_0057F448_0057FED0.bin
        INCBIN  build\spritecontainer\sprite_0057FED0_0057FFC0.bin
        INCBIN  build\spritecontainer\sprite_0057FFC0_0057FFF4.bin
        INCBIN  build\spritecontainer\sprite_0057FFF4_00580A54.bin
        INCBIN  build\spritecontainer\sprite_00580A54_00580AF4.bin
        INCBIN  build\spritecontainer\sprite_00580AF4_00580B18.bin
        INCBIN  build\spritecontainer\sprite_00580B18_00581928.bin
        INCBIN  build\spritecontainer\sprite_00581928_005819C8.bin
        INCBIN  build\spritecontainer\sprite_005819C8_005819EC.bin
        INCBIN  build\spritecontainer\sprite_005819EC_00583CB0.bin
        INCBIN  build\spritecontainer\sprite_00583CB0_00583DF0.bin
        INCBIN  build\spritecontainer\sprite_00583DF0_00583E34.bin
        INCBIN  build\spritecontainer\sprite_00583E34_00586234.bin
        INCBIN  build\spritecontainer\sprite_00586234_00586374.bin
        INCBIN  build\spritecontainer\sprite_00586374_005863B8.bin
        INCBIN  build\spritecontainer\sprite_005863B8_00586C14.bin
        INCBIN  build\spritecontainer\sprite_00586C14_00586C64.bin
        INCBIN  build\spritecontainer\sprite_00586C64_00586C78.bin
        INCBIN  build\spritecontainer\sprite_00586C78_00588550.bin
        INCBIN  build\spritecontainer\sprite_00588550_00588640.bin
        INCBIN  build\spritecontainer\sprite_00588640_00588674.bin
        INCBIN  build\spritecontainer\sprite_00588674_0058A184.bin
        INCBIN  build\spritecontainer\sprite_0058A184_0058A2C4.bin
        INCBIN  build\spritecontainer\sprite_0058A2C4_0058A348.bin
        INCBIN  build\spritecontainer\sprite_0058A348_0058C3E8.bin
        INCBIN  build\spritecontainer\sprite_0058C3E8_0058C4C4.bin
        INCBIN  build\spritecontainer\sprite_0058C4C4_0058C578.bin
        INCBIN  build\spritecontainer\sprite_0058C578_0058FAE8.bin
        INCBIN  build\spritecontainer\sprite_0058FAE8_0058FC78.bin
        INCBIN  build\spritecontainer\sprite_0058FC78_0058FCCC.bin
        INCBIN  build\spritecontainer\sprite_0058FCCC_0058FDA8.bin
        INCBIN  build\spritecontainer\sprite_0058FDA8_0058FE5C.bin
        INCBIN  build\spritecontainer\sprite_0058FE5C_00590350.bin
        INCBIN  build\spritecontainer\sprite_00590350_005903F0.bin
        INCBIN  build\spritecontainer\sprite_005903F0_00590414.bin
        INCBIN  build\spritecontainer\sprite_00590414_00590FEC.bin
        INCBIN  build\spritecontainer\sprite_00590FEC_0059112C.bin
        INCBIN  build\spritecontainer\sprite_0059112C_00591170.bin
        INCBIN  build\spritecontainer\sprite_00591170_005913E0.bin
        INCBIN  build\spritecontainer\sprite_005913E0_00591520.bin
        INCBIN  build\spritecontainer\sprite_00591520_00591564.bin
        INCBIN  build\spritecontainer\sprite_00591564_00591654.bin
        INCBIN  build\spritecontainer\sprite_00591654_00591688.bin
        INCBIN  build\spritecontainer\sprite_00591688_00591DA4.bin
        INCBIN  build\spritecontainer\sprite_00591DA4_00591E44.bin
        INCBIN  build\spritecontainer\sprite_00591E44_00591E68.bin
        INCBIN  build\spritecontainer\sprite_00591E68_00592FE8.bin
        INCBIN  build\spritecontainer\sprite_00592FE8_00593128.bin
        INCBIN  build\spritecontainer\sprite_00593128_0059316C.bin
        INCBIN  build\spritecontainer\sprite_0059316C_00593A30.bin
        INCBIN  build\spritecontainer\sprite_00593A30_00593AD0.bin
        INCBIN  build\spritecontainer\sprite_00593AD0_00593AF4.bin
        INCBIN  build\spritecontainer\sprite_00593AF4_00594A18.bin
        INCBIN  build\spritecontainer\sprite_00594A18_00594B58.bin
        INCBIN  build\spritecontainer\sprite_00594B58_00594B9C.bin
        INCBIN  build\spritecontainer\sprite_00594B9C_00595260.bin
        INCBIN  build\spritecontainer\sprite_00595260_00595300.bin
        INCBIN  build\spritecontainer\sprite_00595300_00595324.bin
        INCBIN  build\spritecontainer\sprite_00595324_005962E0.bin
        INCBIN  build\spritecontainer\sprite_005962E0_00596420.bin
        INCBIN  build\spritecontainer\sprite_00596420_00596464.bin
        INCBIN  build\spritecontainer\sprite_00596464_00596B1C.bin
        INCBIN  build\spritecontainer\sprite_00596B1C_00596BBC.bin
        INCBIN  build\spritecontainer\sprite_00596BBC_00596BE0.bin
        INCBIN  build\spritecontainer\sprite_00596BE0_0059707C.bin
        INCBIN  build\spritecontainer\sprite_0059707C_0059711C.bin
        INCBIN  build\spritecontainer\sprite_0059711C_00597140.bin
        INCBIN  build\spritecontainer\sprite_00597140_00597C2C.bin
        INCBIN  build\spritecontainer\sprite_00597C2C_00597D6C.bin
        INCBIN  build\spritecontainer\sprite_00597D6C_00597DB0.bin
|unk_08597DB0|
        INCBIN  build\spritecontainer\sprite_00597DB0_00597DF0.bin
        INCBIN  build\spritecontainer\sprite_00597DF0_00597E24.bin
        INCBIN  build\spritecontainer\sprite_00597E24_0059826C.bin
        INCBIN  build\spritecontainer\sprite_0059826C_0059830C.bin
        INCBIN  build\spritecontainer\sprite_0059830C_00598330.bin
        INCBIN  build\spritecontainer\sprite_00598330_00599420.bin
        INCBIN  build\spritecontainer\sprite_00599420_00599560.bin
        INCBIN  build\spritecontainer\sprite_00599560_005995A4.bin
        INCBIN  build\spritecontainer\sprite_005995A4_00599BE0.bin
        INCBIN  build\spritecontainer\sprite_00599BE0_00599C80.bin
        INCBIN  build\spritecontainer\sprite_00599C80_00599CA4.bin
        INCBIN  build\spritecontainer\sprite_00599CA4_0059A820.bin
        INCBIN  build\spritecontainer\sprite_0059A820_0059A860.bin
        INCBIN  build\spritecontainer\sprite_0059A860_0059A884.bin
        INCBIN  build\spritecontainer\sprite_0059A884_0059C8D4.bin
        INCBIN  build\spritecontainer\sprite_0059C8D4_0059C974.bin
        INCBIN  build\spritecontainer\sprite_0059C974_0059C9C8.bin
        INCBIN  build\spritecontainer\sprite_0059C9C8_0059E768.bin
        INCBIN  build\spritecontainer\sprite_0059E768_0059E808.bin
        INCBIN  build\spritecontainer\sprite_0059E808_0059E82C.bin
        INCBIN  build\spritecontainer\sprite_0059E82C_005A2BB8.bin
        INCBIN  build\spritecontainer\sprite_005A2BB8_005A2CF8.bin
        INCBIN  build\spritecontainer\sprite_005A2CF8_005A2D3C.bin
        INCBIN  build\spritecontainer\sprite_005A2D3C_005A6ED0.bin
        INCBIN  build\spritecontainer\sprite_005A6ED0_005A7010.bin
        INCBIN  build\spritecontainer\sprite_005A7010_005A7054.bin
        INCBIN  build\spritecontainer\sprite_005A7054_005A80C0.bin
        INCBIN  build\spritecontainer\sprite_005A80C0_005A8110.bin
        INCBIN  build\spritecontainer\sprite_005A8110_005A8124.bin
        INCBIN  build\spritecontainer\sprite_005A8124_005AC3F0.bin
        INCBIN  build\spritecontainer\sprite_005AC3F0_005AC530.bin
        INCBIN  build\spritecontainer\sprite_005AC530_005AC574.bin
        INCBIN  build\spritecontainer\sprite_005AC574_005AC814.bin
        INCBIN  build\spritecontainer\sprite_005AC814_005AC8B4.bin
        INCBIN  build\spritecontainer\sprite_005AC8B4_005AC8D8.bin
        INCBIN  build\spritecontainer\sprite_005AC8D8_005ACD5C.bin
        INCBIN  build\spritecontainer\sprite_005ACD5C_005ACDFC.bin
        INCBIN  build\spritecontainer\sprite_005ACDFC_005ACE20.bin
        INCBIN  build\spritecontainer\sprite_005ACE20_005AD8E0.bin
        INCBIN  build\spritecontainer\sprite_005AD8E0_005ADA20.bin
        INCBIN  build\spritecontainer\sprite_005ADA20_005ADA64.bin
        INCBIN  build\spritecontainer\sprite_005ADA64_005ADE80.bin
        INCBIN  build\spritecontainer\sprite_005ADE80_005ADF20.bin
        INCBIN  build\spritecontainer\sprite_005ADF20_005ADF64.bin
        INCBIN  build\spritecontainer\sprite_005ADF64_005AE3C0.bin
        INCBIN  build\spritecontainer\sprite_005AE3C0_005AE460.bin
        INCBIN  build\spritecontainer\sprite_005AE460_005AE484.bin
        INCBIN  build\spritecontainer\sprite_005AE484_005AEB8C.bin
        INCBIN  build\spritecontainer\sprite_005AEB8C_005AECCC.bin
        INCBIN  build\spritecontainer\sprite_005AECCC_005AED10.bin
        INCBIN  build\spritecontainer\sprite_005AED10_005AEE20.bin
        INCBIN  build\spritecontainer\sprite_005AEE20_005AEE34.bin
        INCBIN  build\spritecontainer\sprite_005AEE34_005AEE48.bin
        INCBIN  build\spritecontainer\sprite_005AEE48_005AF0D8.bin
        INCBIN  build\spritecontainer\sprite_005AF0D8_005AF178.bin
        INCBIN  build\spritecontainer\sprite_005AF178_005AF19C.bin
        INCBIN  build\spritecontainer\sprite_005AF19C_005AF9DC.bin
        INCBIN  build\spritecontainer\sprite_005AF9DC_005AFACC.bin
        INCBIN  build\spritecontainer\sprite_005AFACC_005AFB00.bin
        INCBIN  build\spritecontainer\sprite_005AFB00_005AFF84.bin
        INCBIN  build\spritecontainer\sprite_005AFF84_005B00C4.bin
        INCBIN  build\spritecontainer\sprite_005B00C4_005B0108.bin
        INCBIN  build\spritecontainer\sprite_005B0108_005B0248.bin
        INCBIN  build\spritecontainer\sprite_005B0248_005B028C.bin
        INCBIN  build\spritecontainer\sprite_005B028C_005B07B4.bin
        INCBIN  build\spritecontainer\sprite_005B07B4_005B08A4.bin
        INCBIN  build\spritecontainer\sprite_005B08A4_005B08D8.bin
        INCBIN  build\spritecontainer\sprite_005B08D8_005B099C.bin
        INCBIN  build\spritecontainer\sprite_005B099C_005B0A3C.bin
        INCBIN  build\spritecontainer\sprite_005B0A3C_005B0A80.bin
        INCBIN  build\spritecontainer\sprite_005B0A80_005B0ED4.bin
        INCBIN  build\spritecontainer\sprite_005B0ED4_005B0F74.bin
        INCBIN  build\spritecontainer\sprite_005B0F74_005B0F98.bin
        INCBIN  build\spritecontainer\sprite_005B0F98_005B1A44.bin
        INCBIN  build\spritecontainer\sprite_005B1A44_005B1B84.bin
        INCBIN  build\spritecontainer\sprite_005B1B84_005B1BC8.bin
        INCBIN  build\spritecontainer\sprite_005B1BC8_005B2814.bin
        INCBIN  build\spritecontainer\sprite_005B2814_005B2954.bin
        INCBIN  build\spritecontainer\sprite_005B2954_005B2998.bin
        INCBIN  build\spritecontainer\sprite_005B2998_005B2C08.bin
        INCBIN  build\spritecontainer\sprite_005B2C08_005B2C58.bin
        INCBIN  build\spritecontainer\sprite_005B2C58_005B2C6C.bin
        INCBIN  build\spritecontainer\sprite_005B2C6C_005B2F04.bin
        INCBIN  build\spritecontainer\sprite_005B2F04_005B2F54.bin
        INCBIN  build\spritecontainer\sprite_005B2F54_005B2F68.bin
        INCBIN  build\spritecontainer\sprite_005B2F68_005B3560.bin
        INCBIN  build\spritecontainer\sprite_005B3560_005B3600.bin
        INCBIN  build\spritecontainer\sprite_005B3600_005B3624.bin
        INCBIN  build\spritecontainer\sprite_005B3624_005B4430.bin
        INCBIN  build\spritecontainer\sprite_005B4430_005B4570.bin
        INCBIN  build\spritecontainer\sprite_005B4570_005B45B4.bin
        INCBIN  build\spritecontainer\sprite_005B45B4_005B5118.bin
        INCBIN  build\spritecontainer\sprite_005B5118_005B5208.bin
        INCBIN  build\spritecontainer\sprite_005B5208_005B523C.bin
        INCBIN  build\spritecontainer\sprite_005B523C_005B5D74.bin
        INCBIN  build\spritecontainer\sprite_005B5D74_005B5E64.bin
        INCBIN  build\spritecontainer\sprite_005B5E64_005B5E98.bin
        INCBIN  build\spritecontainer\sprite_005B5E98_005B6334.bin
        INCBIN  build\spritecontainer\sprite_005B6334_005B63D4.bin
        INCBIN  build\spritecontainer\sprite_005B63D4_005B63F8.bin
        INCBIN  build\spritecontainer\sprite_005B63F8_005B713C.bin
        INCBIN  build\spritecontainer\sprite_005B713C_005B727C.bin
        INCBIN  build\spritecontainer\sprite_005B727C_005B72C0.bin
        INCBIN  build\spritecontainer\sprite_005B72C0_005B7D54.bin
        INCBIN  build\spritecontainer\sprite_005B7D54_005B7E44.bin
        INCBIN  build\spritecontainer\sprite_005B7E44_005B7E78.bin
        INCBIN  build\spritecontainer\sprite_005B7E78_005B8374.bin
        INCBIN  build\spritecontainer\sprite_005B8374_005B8414.bin
        INCBIN  build\spritecontainer\sprite_005B8414_005B8438.bin
        INCBIN  build\spritecontainer\sprite_005B8438_005B8FE4.bin
        INCBIN  build\spritecontainer\sprite_005B8FE4_005B9124.bin
        INCBIN  build\spritecontainer\sprite_005B9124_005B9168.bin
        INCBIN  build\spritecontainer\sprite_005B9168_005B9AE8.bin
        INCBIN  build\spritecontainer\sprite_005B9AE8_005B9BD8.bin
        INCBIN  build\spritecontainer\sprite_005B9BD8_005B9C0C.bin
        INCBIN  build\spritecontainer\sprite_005B9C0C_005BA264.bin
        INCBIN  build\spritecontainer\sprite_005BA264_005BA304.bin
        INCBIN  build\spritecontainer\sprite_005BA304_005BA328.bin
        INCBIN  build\spritecontainer\sprite_005BA328_005BAC8C.bin
        INCBIN  build\spritecontainer\sprite_005BAC8C_005BAD7C.bin
        INCBIN  build\spritecontainer\sprite_005BAD7C_005BADB0.bin
        INCBIN  build\spritecontainer\sprite_005BADB0_005BB2B8.bin
        INCBIN  build\spritecontainer\sprite_005BB2B8_005BB358.bin
        INCBIN  build\spritecontainer\sprite_005BB358_005BB37C.bin
        INCBIN  build\spritecontainer\sprite_005BB37C_005BBFBC.bin
        INCBIN  build\spritecontainer\sprite_005BBFBC_005BC0FC.bin
        INCBIN  build\spritecontainer\sprite_005BC0FC_005BC140.bin
        INCBIN  build\spritecontainer\sprite_005BC140_005BC644.bin
        INCBIN  build\spritecontainer\sprite_005BC644_005BC6E4.bin
        INCBIN  build\spritecontainer\sprite_005BC6E4_005BC708.bin
        INCBIN  build\spritecontainer\sprite_005BC708_005BCBFC.bin
        INCBIN  build\spritecontainer\sprite_005BCBFC_005BCC9C.bin
        INCBIN  build\spritecontainer\sprite_005BCC9C_005BCCC0.bin
        INCBIN  build\spritecontainer\sprite_005BCCC0_005BD910.bin
        INCBIN  build\spritecontainer\sprite_005BD910_005BDA50.bin
        INCBIN  build\spritecontainer\sprite_005BDA50_005BDA94.bin
        INCBIN  build\spritecontainer\sprite_005BDA94_005BE090.bin
        INCBIN  build\spritecontainer\sprite_005BE090_005BE130.bin
        INCBIN  build\spritecontainer\sprite_005BE130_005BE154.bin
        INCBIN  build\spritecontainer\sprite_005BE154_005BE680.bin
        INCBIN  build\spritecontainer\sprite_005BE680_005BE720.bin
        INCBIN  build\spritecontainer\sprite_005BE720_005BE744.bin
        INCBIN  build\spritecontainer\sprite_005BE744_005BF3B0.bin
        INCBIN  build\spritecontainer\sprite_005BF3B0_005BF4F0.bin
        INCBIN  build\spritecontainer\sprite_005BF4F0_005BF534.bin
        INCBIN  build\spritecontainer\sprite_005BF534_005BFB80.bin
        INCBIN  build\spritecontainer\sprite_005BFB80_005BFC20.bin
        INCBIN  build\spritecontainer\sprite_005BFC20_005BFC44.bin
|unk_085BFC44|
        INCBIN  build\spritecontainer\sprite_005BFC44_005BFC84.bin
        INCBIN  build\spritecontainer\sprite_005BFC84_005BFC98.bin
        INCBIN  build\spritecontainer\sprite_005BFC98_005C06E8.bin
        INCBIN  build\spritecontainer\sprite_005C06E8_005C0710.bin
        INCBIN  build\spritecontainer\sprite_005C0710_005C0734.bin
        INCBIN  build\spritecontainer\sprite_005C0734_005C075C.bin
        INCBIN  build\spritecontainer\sprite_005C075C_005C0780.bin
        INCBIN  build\spritecontainer\sprite_005C0780_005C1C78.bin
        INCBIN  build\spritecontainer\sprite_005C1C78_005C1CC8.bin
        INCBIN  build\spritecontainer\sprite_005C1CC8_005C1D0C.bin
        INCBIN  build\spritecontainer\sprite_005C1D0C_005C2138.bin
        INCBIN  build\spritecontainer\sprite_005C2138_005C21D8.bin
        INCBIN  build\spritecontainer\sprite_005C21D8_005C21FC.bin
        INCBIN  build\spritecontainer\sprite_005C21FC_005C2BAC.bin
        INCBIN  build\spritecontainer\sprite_005C2BAC_005C2CEC.bin
        INCBIN  build\spritecontainer\sprite_005C2CEC_005C2D30.bin
        INCBIN  build\spritecontainer\sprite_005C2D30_005C314C.bin
        INCBIN  build\spritecontainer\sprite_005C314C_005C31EC.bin
        INCBIN  build\spritecontainer\sprite_005C31EC_005C3210.bin
        INCBIN  build\spritecontainer\sprite_005C3210_005C34B8.bin
        INCBIN  build\spritecontainer\sprite_005C34B8_005C3558.bin
        INCBIN  build\spritecontainer\sprite_005C3558_005C357C.bin
        INCBIN  build\spritecontainer\sprite_005C357C_005C3FE0.bin
        INCBIN  build\spritecontainer\sprite_005C3FE0_005C4120.bin
        INCBIN  build\spritecontainer\sprite_005C4120_005C4164.bin
        INCBIN  build\spritecontainer\sprite_005C4164_005C44E8.bin
        INCBIN  build\spritecontainer\sprite_005C44E8_005C4588.bin
        INCBIN  build\spritecontainer\sprite_005C4588_005C45AC.bin
        INCBIN  build\spritecontainer\sprite_005C45AC_005C50EC.bin
        INCBIN  build\spritecontainer\sprite_005C50EC_005C518C.bin
        INCBIN  build\spritecontainer\sprite_005C518C_005C51B0.bin
        INCBIN  build\spritecontainer\sprite_005C51B0_005C6714.bin
        INCBIN  build\spritecontainer\sprite_005C6714_005C6854.bin
        INCBIN  build\spritecontainer\sprite_005C6854_005C6898.bin
        INCBIN  build\spritecontainer\sprite_005C6898_005C7E08.bin
        INCBIN  build\spritecontainer\sprite_005C7E08_005C7F48.bin
        INCBIN  build\spritecontainer\sprite_005C7F48_005C7F8C.bin
        INCBIN  build\spritecontainer\sprite_005C7F8C_005C8480.bin
        INCBIN  build\spritecontainer\sprite_005C8480_005C84D0.bin
        INCBIN  build\spritecontainer\sprite_005C84D0_005C84E4.bin
        INCBIN  build\spritecontainer\sprite_005C84E4_005C9524.bin
        INCBIN  build\spritecontainer\sprite_005C9524_005C9614.bin
        INCBIN  build\spritecontainer\sprite_005C9614_005C9648.bin
        INCBIN  build\spritecontainer\sprite_005C9648_005CA5CC.bin
        INCBIN  build\spritecontainer\sprite_005CA5CC_005CA6BC.bin
        INCBIN  build\spritecontainer\sprite_005CA6BC_005CA6F0.bin
        INCBIN  build\spritecontainer\sprite_005CA6F0_005CA980.bin
        INCBIN  build\spritecontainer\sprite_005CA980_005CA9D0.bin
        INCBIN  build\spritecontainer\sprite_005CA9D0_005CA9E4.bin
        INCBIN  build\spritecontainer\sprite_005CA9E4_005CB7CC.bin
        INCBIN  build\spritecontainer\sprite_005CB7CC_005CB9AC.bin
        INCBIN  build\spritecontainer\sprite_005CB9AC_005CBA10.bin
        INCBIN  build\spritecontainer\sprite_005CBA10_005CBB00.bin
        INCBIN  build\spritecontainer\sprite_005CBB00_005CBB34.bin
        INCBIN  build\spritecontainer\sprite_005CBB34_005CBF8C.bin
        INCBIN  build\spritecontainer\sprite_005CBF8C_005CC02C.bin
        INCBIN  build\spritecontainer\sprite_005CC02C_005CC050.bin
        INCBIN  build\spritecontainer\sprite_005CC050_005CD198.bin
        INCBIN  build\spritecontainer\sprite_005CD198_005CD2D8.bin
        INCBIN  build\spritecontainer\sprite_005CD2D8_005CD31C.bin
        INCBIN  build\spritecontainer\sprite_005CD31C_005CE034.bin
        INCBIN  build\spritecontainer\sprite_005CE034_005CE124.bin
        INCBIN  build\spritecontainer\sprite_005CE124_005CE158.bin
        INCBIN  build\spritecontainer\sprite_005CE158_005CF48C.bin
        INCBIN  build\spritecontainer\sprite_005CF48C_005CF5CC.bin
        INCBIN  build\spritecontainer\sprite_005CF5CC_005CF610.bin
        INCBIN  build\spritecontainer\sprite_005CF610_005CF900.bin
        INCBIN  build\spritecontainer\sprite_005CF900_005CF9A0.bin
        INCBIN  build\spritecontainer\sprite_005CF9A0_005CF9C4.bin
        INCBIN  build\spritecontainer\sprite_005CF9C4_005D059C.bin
        INCBIN  build\spritecontainer\sprite_005D059C_005D06DC.bin
        INCBIN  build\spritecontainer\sprite_005D06DC_005D0720.bin
        INCBIN  build\spritecontainer\sprite_005D0720_005D0B14.bin
        INCBIN  build\spritecontainer\sprite_005D0B14_005D0BB4.bin
        INCBIN  build\spritecontainer\sprite_005D0BB4_005D0BD8.bin
        INCBIN  build\spritecontainer\sprite_005D0BD8_005D10FC.bin
        INCBIN  build\spritecontainer\sprite_005D10FC_005D119C.bin
        INCBIN  build\spritecontainer\sprite_005D119C_005D11C0.bin
        INCBIN  build\spritecontainer\sprite_005D11C0_005D1E2C.bin
        INCBIN  build\spritecontainer\sprite_005D1E2C_005D1F6C.bin
        INCBIN  build\spritecontainer\sprite_005D1F6C_005D1FB0.bin
        INCBIN  build\spritecontainer\sprite_005D1FB0_005D2628.bin
        INCBIN  build\spritecontainer\sprite_005D2628_005D26C8.bin
        INCBIN  build\spritecontainer\sprite_005D26C8_005D26EC.bin
        INCBIN  build\spritecontainer\sprite_005D26EC_005D2A38.bin
        INCBIN  build\spritecontainer\sprite_005D2A38_005D2AD8.bin
        INCBIN  build\spritecontainer\sprite_005D2AD8_005D2AFC.bin
        INCBIN  build\spritecontainer\sprite_005D2AFC_005D37E4.bin
        INCBIN  build\spritecontainer\sprite_005D37E4_005D3924.bin
        INCBIN  build\spritecontainer\sprite_005D3924_005D3968.bin
        INCBIN  build\spritecontainer\sprite_005D3968_005D3FBC.bin
        INCBIN  build\spritecontainer\sprite_005D3FBC_005D405C.bin
        INCBIN  build\spritecontainer\sprite_005D405C_005D4080.bin
        INCBIN  build\spritecontainer\sprite_005D4080_005D49B4.bin
        INCBIN  build\spritecontainer\sprite_005D49B4_005D4A54.bin
        INCBIN  build\spritecontainer\sprite_005D4A54_005D4A78.bin
        INCBIN  build\spritecontainer\sprite_005D4A78_005D5C2C.bin
        INCBIN  build\spritecontainer\sprite_005D5C2C_005D5D6C.bin
        INCBIN  build\spritecontainer\sprite_005D5D6C_005D5DB0.bin
        INCBIN  build\spritecontainer\sprite_005D5DB0_005D6A3C.bin
        INCBIN  build\spritecontainer\sprite_005D6A3C_005D6B2C.bin
        INCBIN  build\spritecontainer\sprite_005D6B2C_005D6B60.bin
        INCBIN  build\spritecontainer\sprite_005D6B60_005D7424.bin
        INCBIN  build\spritecontainer\sprite_005D7424_005D7514.bin
        INCBIN  build\spritecontainer\sprite_005D7514_005D7548.bin
        INCBIN  build\spritecontainer\sprite_005D7548_005D7C14.bin
        INCBIN  build\spritecontainer\sprite_005D7C14_005D7CB4.bin
        INCBIN  build\spritecontainer\sprite_005D7CB4_005D7CD8.bin
        INCBIN  build\spritecontainer\sprite_005D7CD8_005D8D08.bin
        INCBIN  build\spritecontainer\sprite_005D8D08_005D8E48.bin
        INCBIN  build\spritecontainer\sprite_005D8E48_005D8E8C.bin
        INCBIN  build\spritecontainer\sprite_005D8E8C_005D933C.bin
        INCBIN  build\spritecontainer\sprite_005D933C_005D93DC.bin
        INCBIN  build\spritecontainer\sprite_005D93DC_005D9400.bin
        INCBIN  build\spritecontainer\sprite_005D9400_005D9890.bin
        INCBIN  build\spritecontainer\sprite_005D9890_005D9930.bin
        INCBIN  build\spritecontainer\sprite_005D9930_005D9954.bin
        INCBIN  build\spritecontainer\sprite_005D9954_005DA390.bin
        INCBIN  build\spritecontainer\sprite_005DA390_005DA4D0.bin
        INCBIN  build\spritecontainer\sprite_005DA4D0_005DA514.bin
        INCBIN  build\spritecontainer\sprite_005DA514_005DB164.bin
        INCBIN  build\spritecontainer\sprite_005DB164_005DB2A4.bin
        INCBIN  build\spritecontainer\sprite_005DB2A4_005DB2E8.bin
        INCBIN  build\spritecontainer\sprite_005DB2E8_005DB578.bin
        INCBIN  build\spritecontainer\sprite_005DB578_005DB5C8.bin
        INCBIN  build\spritecontainer\sprite_005DB5C8_005DB5DC.bin
        INCBIN  build\spritecontainer\sprite_005DB5DC_005DBE2C.bin
        INCBIN  build\spritecontainer\sprite_005DBE2C_005DBF1C.bin
        INCBIN  build\spritecontainer\sprite_005DBF1C_005DBF50.bin
        INCBIN  build\spritecontainer\sprite_005DBF50_005DC068.bin
        INCBIN  build\spritecontainer\sprite_005DC068_005DC090.bin
        INCBIN  build\spritecontainer\sprite_005DC090_005DC0B4.bin
        INCBIN  build\spritecontainer\sprite_005DC0B4_005DCCB4.bin
        INCBIN  build\spritecontainer\sprite_005DCCB4_005DCDF4.bin
        INCBIN  build\spritecontainer\sprite_005DCDF4_005DCE38.bin
        INCBIN  build\spritecontainer\sprite_005DCE38_005DD388.bin
        INCBIN  build\spritecontainer\sprite_005DD388_005DD428.bin
        INCBIN  build\spritecontainer\sprite_005DD428_005DD44C.bin
        INCBIN  build\spritecontainer\sprite_005DD44C_005DE0E8.bin
        INCBIN  build\spritecontainer\sprite_005DE0E8_005DE228.bin
        INCBIN  build\spritecontainer\sprite_005DE228_005DE26C.bin
        INCBIN  build\spritecontainer\sprite_005DE26C_005DE7B0.bin
        INCBIN  build\spritecontainer\sprite_005DE7B0_005DE850.bin
        INCBIN  build\spritecontainer\sprite_005DE850_005DE874.bin
        INCBIN  build\spritecontainer\sprite_005DE874_005DE950.bin
        INCBIN  build\spritecontainer\sprite_005DE950_005DE964.bin
        INCBIN  build\spritecontainer\sprite_005DE964_005DE978.bin
        INCBIN  build\spritecontainer\sprite_005DE978_005DEE8C.bin
        INCBIN  build\spritecontainer\sprite_005DEE8C_005DEF2C.bin
        INCBIN  build\spritecontainer\sprite_005DEF2C_005DEF50.bin
        INCBIN  build\spritecontainer\sprite_005DEF50_005DFB58.bin
        INCBIN  build\spritecontainer\sprite_005DFB58_005DFC98.bin
        INCBIN  build\spritecontainer\sprite_005DFC98_005DFCDC.bin
        INCBIN  build\spritecontainer\sprite_005DFCDC_005E02E0.bin
        INCBIN  build\spritecontainer\sprite_005E02E0_005E0380.bin
        INCBIN  build\spritecontainer\sprite_005E0380_005E03A4.bin
        INCBIN  build\spritecontainer\sprite_005E03A4_005E09C0.bin
        INCBIN  build\spritecontainer\sprite_005E09C0_005E0A60.bin
        INCBIN  build\spritecontainer\sprite_005E0A60_005E0A84.bin
        INCBIN  build\spritecontainer\sprite_005E0A84_005E1878.bin
        INCBIN  build\spritecontainer\sprite_005E1878_005E19B8.bin
        INCBIN  build\spritecontainer\sprite_005E19B8_005E19FC.bin
        INCBIN  build\spritecontainer\sprite_005E19FC_005E29C4.bin
        INCBIN  build\spritecontainer\sprite_005E29C4_005E2B04.bin
        INCBIN  build\spritecontainer\sprite_005E2B04_005E2B48.bin
        INCBIN  build\spritecontainer\sprite_005E2B48_005E2EC0.bin
        INCBIN  build\spritecontainer\sprite_005E2EC0_005E2F10.bin
        INCBIN  build\spritecontainer\sprite_005E2F10_005E2F24.bin
        INCBIN  build\spritecontainer\sprite_005E2F24_005E3A40.bin
        INCBIN  build\spritecontainer\sprite_005E3A40_005E3B30.bin
        INCBIN  build\spritecontainer\sprite_005E3B30_005E3B64.bin
        INCBIN  build\spritecontainer\sprite_005E3B64_005E4180.bin
        INCBIN  build\spritecontainer\sprite_005E4180_005E4220.bin
        INCBIN  build\spritecontainer\sprite_005E4220_005E4244.bin
        INCBIN  build\spritecontainer\sprite_005E4244_005E4690.bin
        INCBIN  build\spritecontainer\sprite_005E4690_005E4730.bin
        INCBIN  build\spritecontainer\sprite_005E4730_005E4754.bin
        INCBIN  build\spritecontainer\sprite_005E4754_005E51A4.bin
        INCBIN  build\spritecontainer\sprite_005E51A4_005E52E4.bin
        INCBIN  build\spritecontainer\sprite_005E52E4_005E5328.bin
        INCBIN  build\spritecontainer\sprite_005E5328_005E5868.bin
        INCBIN  build\spritecontainer\sprite_005E5868_005E5908.bin
        INCBIN  build\spritecontainer\sprite_005E5908_005E592C.bin
        INCBIN  build\spritecontainer\sprite_005E592C_005E5F40.bin
        INCBIN  build\spritecontainer\sprite_005E5F40_005E5FE0.bin
        INCBIN  build\spritecontainer\sprite_005E5FE0_005E6004.bin
        INCBIN  build\spritecontainer\sprite_005E6004_005E6BA4.bin
        INCBIN  build\spritecontainer\sprite_005E6BA4_005E6CE4.bin
        INCBIN  build\spritecontainer\sprite_005E6CE4_005E6D28.bin
        INCBIN  build\spritecontainer\sprite_005E6D28_005E7B64.bin
        INCBIN  build\spritecontainer\sprite_005E7B64_005E7CA4.bin
        INCBIN  build\spritecontainer\sprite_005E7CA4_005E7CE8.bin
        INCBIN  build\spritecontainer\sprite_005E7CE8_005E7FC4.bin
        INCBIN  build\spritecontainer\sprite_005E7FC4_005E8014.bin
        INCBIN  build\spritecontainer\sprite_005E8014_005E8028.bin
        INCBIN  build\spritecontainer\sprite_005E8028_005E89D0.bin
        INCBIN  build\spritecontainer\sprite_005E89D0_005E8AC0.bin
        INCBIN  build\spritecontainer\sprite_005E8AC0_005E8AF4.bin
        INCBIN  build\spritecontainer\sprite_005E8AF4_005E9C48.bin
        INCBIN  build\spritecontainer\sprite_005E9C48_005E9CE8.bin
        INCBIN  build\spritecontainer\sprite_005E9CE8_005E9D0C.bin
        INCBIN  build\spritecontainer\sprite_005E9D0C_005EC744.bin
        INCBIN  build\spritecontainer\sprite_005EC744_005EC884.bin
        INCBIN  build\spritecontainer\sprite_005EC884_005EC8C8.bin
        INCBIN  build\spritecontainer\sprite_005EC8C8_005ECCA8.bin
        INCBIN  build\spritecontainer\sprite_005ECCA8_005ECD48.bin
        INCBIN  build\spritecontainer\sprite_005ECD48_005ECD6C.bin
        INCBIN  build\spritecontainer\sprite_005ECD6C_005ED6A4.bin
        INCBIN  build\spritecontainer\sprite_005ED6A4_005ED7E4.bin
        INCBIN  build\spritecontainer\sprite_005ED7E4_005ED828.bin
        INCBIN  build\spritecontainer\sprite_005ED828_005EDEAC.bin
        INCBIN  build\spritecontainer\sprite_005EDEAC_005EDF4C.bin
        INCBIN  build\spritecontainer\sprite_005EDF4C_005EDF70.bin
        INCBIN  build\spritecontainer\sprite_005EDF70_005EF02C.bin
        INCBIN  build\spritecontainer\sprite_005EF02C_005EF16C.bin
        INCBIN  build\spritecontainer\sprite_005EF16C_005EF1B0.bin
        INCBIN  build\spritecontainer\sprite_005EF1B0_005EFDFC.bin
        INCBIN  build\spritecontainer\sprite_005EFDFC_005EFEEC.bin
        INCBIN  build\spritecontainer\sprite_005EFEEC_005EFF20.bin
        INCBIN  build\spritecontainer\sprite_005EFF20_005F0DF4.bin
        INCBIN  build\spritecontainer\sprite_005F0DF4_005F0F34.bin
        INCBIN  build\spritecontainer\sprite_005F0F34_005F0F78.bin
        INCBIN  build\spritecontainer\sprite_005F0F78_005F1FE8.bin
        INCBIN  build\spritecontainer\sprite_005F1FE8_005F2128.bin
        INCBIN  build\spritecontainer\sprite_005F2128_005F216C.bin
        INCBIN  build\spritecontainer\sprite_005F216C_005F2578.bin
        INCBIN  build\spritecontainer\sprite_005F2578_005F25C8.bin
        INCBIN  build\spritecontainer\sprite_005F25C8_005F25DC.bin
        INCBIN  build\spritecontainer\sprite_005F25DC_005F32E0.bin
        INCBIN  build\spritecontainer\sprite_005F32E0_005F33D0.bin
        INCBIN  build\spritecontainer\sprite_005F33D0_005F3404.bin
        INCBIN  build\spritecontainer\sprite_005F3404_005F3E70.bin
        INCBIN  build\spritecontainer\sprite_005F3E70_005F3FB0.bin
        INCBIN  build\spritecontainer\sprite_005F3FB0_005F3FF4.bin
        INCBIN  build\spritecontainer\sprite_005F3FF4_005F4F18.bin
        INCBIN  build\spritecontainer\sprite_005F4F18_005F5058.bin
        INCBIN  build\spritecontainer\sprite_005F5058_005F509C.bin
        INCBIN  build\spritecontainer\sprite_005F509C_005F556C.bin
        INCBIN  build\spritecontainer\sprite_005F556C_005F560C.bin
        INCBIN  build\spritecontainer\sprite_005F560C_005F5650.bin
        INCBIN  build\spritecontainer\sprite_005F5650_005F57CC.bin
        INCBIN  build\spritecontainer\sprite_005F57CC_005F57E0.bin
        INCBIN  build\spritecontainer\sprite_005F57E0_005F57F4.bin
        INCBIN  build\spritecontainer\sprite_005F57F4_005F5D64.bin
        INCBIN  build\spritecontainer\sprite_005F5D64_005F5E04.bin
        INCBIN  build\spritecontainer\sprite_005F5E04_005F5E28.bin
        INCBIN  build\spritecontainer\sprite_005F5E28_005F69C0.bin
        INCBIN  build\spritecontainer\sprite_005F69C0_005F6B00.bin
        INCBIN  build\spritecontainer\sprite_005F6B00_005F6B44.bin
        INCBIN  build\spritecontainer\sprite_005F6B44_005F6D7C.bin
        INCBIN  build\spritecontainer\sprite_005F6D7C_005F6DA4.bin
        INCBIN  build\spritecontainer\sprite_005F6DA4_005F6DC8.bin
        INCBIN  build\spritecontainer\sprite_005F6DC8_005F735C.bin
        INCBIN  build\spritecontainer\sprite_005F735C_005F73FC.bin
        INCBIN  build\spritecontainer\sprite_005F73FC_005F7420.bin
        INCBIN  build\spritecontainer\sprite_005F7420_005F80E0.bin
        INCBIN  build\spritecontainer\sprite_005F80E0_005F8220.bin
        INCBIN  build\spritecontainer\sprite_005F8220_005F8264.bin
        INCBIN  build\spritecontainer\sprite_005F8264_005F8CC0.bin
        INCBIN  build\spritecontainer\sprite_005F8CC0_005F8DB0.bin
        INCBIN  build\spritecontainer\sprite_005F8DB0_005F8DE4.bin
        INCBIN  build\spritecontainer\sprite_005F8DE4_005F9D0C.bin
        INCBIN  build\spritecontainer\sprite_005F9D0C_005F9E4C.bin
        INCBIN  build\spritecontainer\sprite_005F9E4C_005F9E90.bin
        INCBIN  build\spritecontainer\sprite_005F9E90_005FAC78.bin
        INCBIN  build\spritecontainer\sprite_005FAC78_005FADB8.bin
        INCBIN  build\spritecontainer\sprite_005FADB8_005FADFC.bin
        INCBIN  build\spritecontainer\sprite_005FADFC_005FB130.bin
        INCBIN  build\spritecontainer\sprite_005FB130_005FB180.bin
        INCBIN  build\spritecontainer\sprite_005FB180_005FB194.bin
        INCBIN  build\spritecontainer\sprite_005FB194_005FBBCC.bin
        INCBIN  build\spritecontainer\sprite_005FBBCC_005FBCBC.bin
        INCBIN  build\spritecontainer\sprite_005FBCBC_005FBCF0.bin
        INCBIN  build\spritecontainer\sprite_005FBCF0_005FC26C.bin
        INCBIN  build\spritecontainer\sprite_005FC26C_005FC30C.bin
        INCBIN  build\spritecontainer\sprite_005FC30C_005FC330.bin
        INCBIN  build\spritecontainer\sprite_005FC330_005FCE20.bin
        INCBIN  build\spritecontainer\sprite_005FCE20_005FCF60.bin
        INCBIN  build\spritecontainer\sprite_005FCF60_005FCFA4.bin
        INCBIN  build\spritecontainer\sprite_005FCFA4_005FD45C.bin
        INCBIN  build\spritecontainer\sprite_005FD45C_005FD4FC.bin
        INCBIN  build\spritecontainer\sprite_005FD4FC_005FD540.bin
        INCBIN  build\spritecontainer\sprite_005FD540_005FE6BC.bin
        INCBIN  build\spritecontainer\sprite_005FE6BC_005FE75C.bin
        INCBIN  build\spritecontainer\sprite_005FE75C_005FE780.bin
        INCBIN  build\spritecontainer\sprite_005FE780_00601078.bin
        INCBIN  build\spritecontainer\sprite_00601078_006011B8.bin
        INCBIN  build\spritecontainer\sprite_006011B8_006011FC.bin
        INCBIN  build\spritecontainer\sprite_006011FC_0060163C.bin
        INCBIN  build\spritecontainer\sprite_0060163C_0060168C.bin
        INCBIN  build\spritecontainer\sprite_0060168C_006016A0.bin
        INCBIN  build\spritecontainer\sprite_006016A0_00601C40.bin
        INCBIN  build\spritecontainer\sprite_00601C40_00601CE0.bin
        INCBIN  build\spritecontainer\sprite_00601CE0_00601D04.bin
        INCBIN  build\spritecontainer\sprite_00601D04_00602A04.bin
        INCBIN  build\spritecontainer\sprite_00602A04_00602B44.bin
        INCBIN  build\spritecontainer\sprite_00602B44_00602B88.bin
        INCBIN  build\spritecontainer\sprite_00602B88_00603124.bin
        INCBIN  build\spritecontainer\sprite_00603124_006031C4.bin
        INCBIN  build\spritecontainer\sprite_006031C4_006031E8.bin
        INCBIN  build\spritecontainer\sprite_006031E8_00603408.bin
        INCBIN  build\spritecontainer\sprite_00603408_00603548.bin
        INCBIN  build\spritecontainer\sprite_00603548_0060358C.bin
        INCBIN  build\spritecontainer\sprite_0060358C_006037B0.bin
        INCBIN  build\spritecontainer\sprite_006037B0_00603850.bin
        INCBIN  build\spritecontainer\sprite_00603850_00603874.bin
        INCBIN  build\spritecontainer\sprite_00603874_0060415C.bin
        INCBIN  build\spritecontainer\sprite_0060415C_006041FC.bin
        INCBIN  build\spritecontainer\sprite_006041FC_00604220.bin
        INCBIN  build\spritecontainer\sprite_00604220_0060579C.bin
        INCBIN  build\spritecontainer\sprite_0060579C_006058DC.bin
        INCBIN  build\spritecontainer\sprite_006058DC_00605920.bin
        INCBIN  build\spritecontainer\sprite_00605920_00606EF4.bin
        INCBIN  build\spritecontainer\sprite_00606EF4_00607034.bin
        INCBIN  build\spritecontainer\sprite_00607034_00607078.bin
        INCBIN  build\spritecontainer\sprite_00607078_00607FD0.bin
        INCBIN  build\spritecontainer\sprite_00607FD0_006080C0.bin
        INCBIN  build\spritecontainer\sprite_006080C0_006080F4.bin
        INCBIN  build\spritecontainer\sprite_006080F4_006084A4.bin
        INCBIN  build\spritecontainer\sprite_006084A4_00608544.bin
        INCBIN  build\spritecontainer\sprite_00608544_00608568.bin
        INCBIN  build\spritecontainer\sprite_00608568_006093F0.bin
        INCBIN  build\spritecontainer\sprite_006093F0_00609530.bin
        INCBIN  build\spritecontainer\sprite_00609530_00609574.bin
        INCBIN  build\spritecontainer\sprite_00609574_00609CE4.bin
        INCBIN  build\spritecontainer\sprite_00609CE4_00609D84.bin
        INCBIN  build\spritecontainer\sprite_00609D84_00609DA8.bin
        INCBIN  build\spritecontainer\sprite_00609DA8_0060ADE0.bin
        INCBIN  build\spritecontainer\sprite_0060ADE0_0060AF20.bin
        INCBIN  build\spritecontainer\sprite_0060AF20_0060AF64.bin
        INCBIN  build\spritecontainer\sprite_0060AF64_0060BF5C.bin
        INCBIN  build\spritecontainer\sprite_0060BF5C_0060C09C.bin
        INCBIN  build\spritecontainer\sprite_0060C09C_0060C0E0.bin
        INCBIN  build\spritecontainer\sprite_0060C0E0_0060C4D4.bin
        INCBIN  build\spritecontainer\sprite_0060C4D4_0060C524.bin
        INCBIN  build\spritecontainer\sprite_0060C524_0060C538.bin
        INCBIN  build\spritecontainer\sprite_0060C538_0060D144.bin
        INCBIN  build\spritecontainer\sprite_0060D144_0060D234.bin
        INCBIN  build\spritecontainer\sprite_0060D234_0060D268.bin
        INCBIN  build\spritecontainer\sprite_0060D268_0060D630.bin
        INCBIN  build\spritecontainer\sprite_0060D630_0060D680.bin
        INCBIN  build\spritecontainer\sprite_0060D680_0060D694.bin
        INCBIN  build\spritecontainer\sprite_0060D694_0060DB24.bin
        INCBIN  build\spritecontainer\sprite_0060DB24_0060DBC4.bin
        INCBIN  build\spritecontainer\sprite_0060DBC4_0060DBE8.bin
        INCBIN  build\spritecontainer\sprite_0060DBE8_0060E6DC.bin
        INCBIN  build\spritecontainer\sprite_0060E6DC_0060E81C.bin
        INCBIN  build\spritecontainer\sprite_0060E81C_0060E860.bin
        INCBIN  build\spritecontainer\sprite_0060E860_0060ED2C.bin
        INCBIN  build\spritecontainer\sprite_0060ED2C_0060EDCC.bin
        INCBIN  build\spritecontainer\sprite_0060EDCC_0060EDF0.bin
        INCBIN  build\spritecontainer\sprite_0060EDF0_0060F948.bin
        INCBIN  build\spritecontainer\sprite_0060F948_0060FA88.bin
        INCBIN  build\spritecontainer\sprite_0060FA88_0060FACC.bin
        INCBIN  build\spritecontainer\sprite_0060FACC_0060FF64.bin
        INCBIN  build\spritecontainer\sprite_0060FF64_00610004.bin
        INCBIN  build\spritecontainer\sprite_00610004_00610028.bin
        INCBIN  build\spritecontainer\sprite_00610028_00610734.bin
        INCBIN  build\spritecontainer\sprite_00610734_006107D4.bin
        INCBIN  build\spritecontainer\sprite_006107D4_006107F8.bin
        INCBIN  build\spritecontainer\sprite_006107F8_0061173C.bin
        INCBIN  build\spritecontainer\sprite_0061173C_0061187C.bin
        INCBIN  build\spritecontainer\sprite_0061187C_006118C0.bin
        INCBIN  build\spritecontainer\sprite_006118C0_00612744.bin
        INCBIN  build\spritecontainer\sprite_00612744_00612884.bin
        INCBIN  build\spritecontainer\sprite_00612884_006128C8.bin
        INCBIN  build\spritecontainer\sprite_006128C8_00612C10.bin
        INCBIN  build\spritecontainer\sprite_00612C10_00612C60.bin
        INCBIN  build\spritecontainer\sprite_00612C60_00612C74.bin
        INCBIN  build\spritecontainer\sprite_00612C74_006137B4.bin
        INCBIN  build\spritecontainer\sprite_006137B4_006138A4.bin
        INCBIN  build\spritecontainer\sprite_006138A4_006138D8.bin
        INCBIN  build\spritecontainer\sprite_006138D8_00613E10.bin
        INCBIN  build\spritecontainer\sprite_00613E10_00613E60.bin
        INCBIN  build\spritecontainer\sprite_00613E60_00613EA4.bin
        INCBIN  build\spritecontainer\sprite_00613EA4_00613EF4.bin
        INCBIN  build\spritecontainer\sprite_00613EF4_00613F38.bin
        INCBIN  build\spritecontainer\sprite_00613F38_00614494.bin
        INCBIN  build\spritecontainer\sprite_00614494_00614534.bin
        INCBIN  build\spritecontainer\sprite_00614534_00614558.bin
        INCBIN  build\spritecontainer\sprite_00614558_00615230.bin
        INCBIN  build\spritecontainer\sprite_00615230_00615370.bin
        INCBIN  build\spritecontainer\sprite_00615370_006153B4.bin
        INCBIN  build\spritecontainer\sprite_006153B4_00615800.bin
        INCBIN  build\spritecontainer\sprite_00615800_00615850.bin
        INCBIN  build\spritecontainer\sprite_00615850_00615894.bin
        INCBIN  build\spritecontainer\sprite_00615894_00615D78.bin
        INCBIN  build\spritecontainer\sprite_00615D78_00615E18.bin
        INCBIN  build\spritecontainer\sprite_00615E18_00615E3C.bin
        INCBIN  build\spritecontainer\sprite_00615E3C_006169B8.bin
        INCBIN  build\spritecontainer\sprite_006169B8_00616AF8.bin
        INCBIN  build\spritecontainer\sprite_00616AF8_00616B3C.bin
        INCBIN  build\spritecontainer\sprite_00616B3C_00617158.bin
        INCBIN  build\spritecontainer\sprite_00617158_00617298.bin
        INCBIN  build\spritecontainer\sprite_00617298_006172DC.bin
        INCBIN  build\spritecontainer\sprite_006172DC_0061776C.bin
        INCBIN  build\spritecontainer\sprite_0061776C_0061780C.bin
        INCBIN  build\spritecontainer\sprite_0061780C_00617830.bin
        INCBIN  build\spritecontainer\sprite_00617830_00618B14.bin
        INCBIN  build\spritecontainer\sprite_00618B14_00618C54.bin
        INCBIN  build\spritecontainer\sprite_00618C54_00618C98.bin
        INCBIN  build\spritecontainer\sprite_00618C98_00618EE0.bin
        INCBIN  build\spritecontainer\sprite_00618EE0_00618F30.bin
        INCBIN  build\spritecontainer\sprite_00618F30_00618F74.bin
        INCBIN  build\spritecontainer\sprite_00618F74_0061A2B0.bin
        INCBIN  build\spritecontainer\sprite_0061A2B0_0061A350.bin
        INCBIN  build\spritecontainer\sprite_0061A350_0061A374.bin
        INCBIN  build\spritecontainer\sprite_0061A374_0061CF8C.bin
        INCBIN  build\spritecontainer\sprite_0061CF8C_0061D16C.bin
        INCBIN  build\spritecontainer\sprite_0061D16C_0061D1D0.bin
        INCBIN  build\spritecontainer\sprite_0061D1D0_0061FF68.bin
        INCBIN  build\spritecontainer\sprite_0061FF68_006200A8.bin
        INCBIN  build\spritecontainer\sprite_006200A8_006200EC.bin
        INCBIN  build\spritecontainer\sprite_006200EC_00620ABC.bin
        INCBIN  build\spritecontainer\sprite_00620ABC_00620B0C.bin
        INCBIN  build\spritecontainer\sprite_00620B0C_00620B20.bin
        INCBIN  build\spritecontainer\sprite_00620B20_00622C84.bin
        INCBIN  build\spritecontainer\sprite_00622C84_00622D74.bin
        INCBIN  build\spritecontainer\sprite_00622D74_00622DA8.bin
        INCBIN  build\spritecontainer\sprite_00622DA8_006235D8.bin
        INCBIN  build\spritecontainer\sprite_006235D8_00623628.bin
        INCBIN  build\spritecontainer\sprite_00623628_0062363C.bin
        INCBIN  build\spritecontainer\sprite_0062363C_0062416C.bin
        INCBIN  build\spritecontainer\sprite_0062416C_006241E4.bin
        INCBIN  build\spritecontainer\sprite_006241E4_00624218.bin
        INCBIN  build\spritecontainer\sprite_00624218_00626248.bin
        INCBIN  build\spritecontainer\sprite_00626248_00626338.bin
        INCBIN  build\spritecontainer\sprite_00626338_0062636C.bin
        INCBIN  build\spritecontainer\sprite_0062636C_00626740.bin
        INCBIN  build\spritecontainer\sprite_00626740_00626754.bin
        INCBIN  build\spritecontainer\sprite_00626754_00626768.bin
        INCBIN  build\spritecontainer\sprite_00626768_006269D0.bin
        INCBIN  build\spritecontainer\sprite_006269D0_00626A20.bin
        INCBIN  build\spritecontainer\sprite_00626A20_00626A34.bin
        INCBIN  build\spritecontainer\sprite_00626A34_0062706C.bin
        INCBIN  build\spritecontainer\sprite_0062706C_0062710C.bin
        INCBIN  build\spritecontainer\sprite_0062710C_00627130.bin
        INCBIN  build\spritecontainer\sprite_00627130_00628028.bin
        INCBIN  build\spritecontainer\sprite_00628028_00628168.bin
        INCBIN  build\spritecontainer\sprite_00628168_006281AC.bin
        INCBIN  build\spritecontainer\sprite_006281AC_00628D30.bin
        INCBIN  build\spritecontainer\sprite_00628D30_00628E20.bin
        INCBIN  build\spritecontainer\sprite_00628E20_00628E54.bin
        INCBIN  build\spritecontainer\sprite_00628E54_006295B8.bin
        INCBIN  build\spritecontainer\sprite_006295B8_00629658.bin
        INCBIN  build\spritecontainer\sprite_00629658_0062967C.bin
        INCBIN  build\spritecontainer\sprite_0062967C_0062A358.bin
        INCBIN  build\spritecontainer\sprite_0062A358_0062A498.bin
        INCBIN  build\spritecontainer\sprite_0062A498_0062A4DC.bin
        INCBIN  build\spritecontainer\sprite_0062A4DC_0062A968.bin
        INCBIN  build\spritecontainer\sprite_0062A968_0062AA08.bin
        INCBIN  build\spritecontainer\sprite_0062AA08_0062AA4C.bin
        INCBIN  build\spritecontainer\sprite_0062AA4C_0062B748.bin
        INCBIN  build\spritecontainer\sprite_0062B748_0062B7E8.bin
        INCBIN  build\spritecontainer\sprite_0062B7E8_0062B80C.bin
        INCBIN  build\spritecontainer\sprite_0062B80C_0062D1F4.bin
        INCBIN  build\spritecontainer\sprite_0062D1F4_0062D2E4.bin
        INCBIN  build\spritecontainer\sprite_0062D2E4_0062D318.bin
        INCBIN  build\spritecontainer\sprite_0062D318_0062FD14.bin
        INCBIN  build\spritecontainer\sprite_0062FD14_0062FE54.bin
        INCBIN  build\spritecontainer\sprite_0062FE54_0062FE98.bin
        INCBIN  build\spritecontainer\sprite_0062FE98_006303EC.bin
        INCBIN  build\spritecontainer\sprite_006303EC_0063048C.bin
        INCBIN  build\spritecontainer\sprite_0063048C_006304B0.bin
        INCBIN  build\spritecontainer\sprite_006304B0_006306F4.bin
        INCBIN  build\spritecontainer\sprite_006306F4_0063071C.bin
        INCBIN  build\spritecontainer\sprite_0063071C_00630740.bin
        INCBIN  build\spritecontainer\sprite_00630740_00630E14.bin
        INCBIN  build\spritecontainer\sprite_00630E14_00630F04.bin
        INCBIN  build\spritecontainer\sprite_00630F04_00630FC8.bin
        INCBIN  build\spritecontainer\sprite_00630FC8_006314BC.bin
        INCBIN  build\spritecontainer\sprite_006314BC_0063155C.bin
        INCBIN  build\spritecontainer\sprite_0063155C_00631580.bin
        INCBIN  build\spritecontainer\sprite_00631580_00632160.bin
        INCBIN  build\spritecontainer\sprite_00632160_006322A0.bin
        INCBIN  build\spritecontainer\sprite_006322A0_006322E4.bin
        INCBIN  build\spritecontainer\sprite_006322E4_00633090.bin
        INCBIN  build\spritecontainer\sprite_00633090_006331D0.bin
        INCBIN  build\spritecontainer\sprite_006331D0_00633214.bin
        INCBIN  build\spritecontainer\sprite_00633214_00633BC0.bin
        INCBIN  build\spritecontainer\sprite_00633BC0_00633CB0.bin
        INCBIN  build\spritecontainer\sprite_00633CB0_00633CE4.bin
        INCBIN  build\spritecontainer\sprite_00633CE4_006341C4.bin
        INCBIN  build\spritecontainer\sprite_006341C4_00634264.bin
        INCBIN  build\spritecontainer\sprite_00634264_00634288.bin
        INCBIN  build\spritecontainer\sprite_00634288_006347B4.bin
        INCBIN  build\spritecontainer\sprite_006347B4_00634854.bin
        INCBIN  build\spritecontainer\sprite_00634854_00634878.bin
        INCBIN  build\spritecontainer\sprite_00634878_006354A4.bin
        INCBIN  build\spritecontainer\sprite_006354A4_006355E4.bin
        INCBIN  build\spritecontainer\sprite_006355E4_00635628.bin
        INCBIN  build\spritecontainer\sprite_00635628_00635C3C.bin
        INCBIN  build\spritecontainer\sprite_00635C3C_00635CDC.bin
        INCBIN  build\spritecontainer\sprite_00635CDC_00635D00.bin
        INCBIN  build\spritecontainer\sprite_00635D00_006368C0.bin
        INCBIN  build\spritecontainer\sprite_006368C0_00636960.bin
        INCBIN  build\spritecontainer\sprite_00636960_00636984.bin
        INCBIN  build\spritecontainer\sprite_00636984_0063987C.bin
        INCBIN  build\spritecontainer\sprite_0063987C_006399BC.bin
        INCBIN  build\spritecontainer\sprite_006399BC_00639A00.bin
        INCBIN  build\spritecontainer\sprite_00639A00_0063C8E0.bin
        INCBIN  build\spritecontainer\sprite_0063C8E0_0063CA20.bin
        INCBIN  build\spritecontainer\sprite_0063CA20_0063CA64.bin
        INCBIN  build\spritecontainer\sprite_0063CA64_0063CB54.bin
        INCBIN  build\spritecontainer\sprite_0063CB54_0063CB88.bin
        INCBIN  build\spritecontainer\sprite_0063CB88_0063D0BC.bin
        INCBIN  build\spritecontainer\sprite_0063D0BC_0063D15C.bin
        INCBIN  build\spritecontainer\sprite_0063D15C_0063D180.bin
        INCBIN  build\spritecontainer\sprite_0063D180_0063DDC4.bin
        INCBIN  build\spritecontainer\sprite_0063DDC4_0063DF04.bin
        INCBIN  build\spritecontainer\sprite_0063DF04_0063DF48.bin
        INCBIN  build\spritecontainer\sprite_0063DF48_0063E550.bin
        INCBIN  build\spritecontainer\sprite_0063E550_0063E5F0.bin
        INCBIN  build\spritecontainer\sprite_0063E5F0_0063E614.bin
        INCBIN  build\spritecontainer\sprite_0063E614_0063E668.bin
        INCBIN  build\spritecontainer\sprite_0063E668_0063E690.bin
        INCBIN  build\spritecontainer\sprite_0063E690_0063E6B4.bin
        INCBIN  build\spritecontainer\sprite_0063E6B4_0063EBA8.bin
        INCBIN  build\spritecontainer\sprite_0063EBA8_0063EC48.bin
        INCBIN  build\spritecontainer\sprite_0063EC48_0063EC6C.bin
        INCBIN  build\spritecontainer\sprite_0063EC6C_0063F828.bin
        INCBIN  build\spritecontainer\sprite_0063F828_0063F968.bin
        INCBIN  build\spritecontainer\sprite_0063F968_0063F9AC.bin
        INCBIN  build\spritecontainer\sprite_0063F9AC_00640600.bin
        INCBIN  build\spritecontainer\sprite_00640600_00640740.bin
        INCBIN  build\spritecontainer\sprite_00640740_00640784.bin
        INCBIN  build\spritecontainer\sprite_00640784_00641108.bin
        INCBIN  build\spritecontainer\sprite_00641108_006411F8.bin
        INCBIN  build\spritecontainer\sprite_006411F8_0064122C.bin
        INCBIN  build\spritecontainer\sprite_0064122C_00641F1C.bin
        INCBIN  build\spritecontainer\sprite_00641F1C_0064205C.bin
        INCBIN  build\spritecontainer\sprite_0064205C_006420A0.bin
        INCBIN  build\spritecontainer\sprite_006420A0_00642E1C.bin
        INCBIN  build\spritecontainer\sprite_00642E1C_00642F5C.bin
        INCBIN  build\spritecontainer\sprite_00642F5C_00642FA0.bin
        INCBIN  build\spritecontainer\sprite_00642FA0_0064327C.bin
        INCBIN  build\spritecontainer\sprite_0064327C_006432CC.bin
        INCBIN  build\spritecontainer\sprite_006432CC_006432E0.bin
        INCBIN  build\spritecontainer\sprite_006432E0_00643714.bin
        INCBIN  build\spritecontainer\sprite_00643714_00643764.bin
        INCBIN  build\spritecontainer\sprite_00643764_006437A8.bin
        INCBIN  build\spritecontainer\sprite_006437A8_006440A0.bin
        INCBIN  build\spritecontainer\sprite_006440A0_00644190.bin
        INCBIN  build\spritecontainer\sprite_00644190_006441C4.bin
        INCBIN  build\spritecontainer\sprite_006441C4_006447B8.bin
        INCBIN  build\spritecontainer\sprite_006447B8_00644894.bin
        INCBIN  build\spritecontainer\sprite_00644894_00644948.bin
        INCBIN  build\spritecontainer\sprite_00644948_00644B4C.bin
        INCBIN  build\spritecontainer\sprite_00644B4C_00644B74.bin
        INCBIN  build\spritecontainer\sprite_00644B74_00644B98.bin
        INCBIN  build\spritecontainer\sprite_00644B98_00644DC4.bin
        INCBIN  build\spritecontainer\sprite_00644DC4_00644DEC.bin
        INCBIN  build\spritecontainer\sprite_00644DEC_00644E10.bin
        INCBIN  build\spritecontainer\sprite_00644E10_006456C8.bin
        INCBIN  build\spritecontainer\sprite_006456C8_006457B8.bin
        INCBIN  build\spritecontainer\sprite_006457B8_006457EC.bin
        INCBIN  build\spritecontainer\sprite_006457EC_00646280.bin
        INCBIN  build\spritecontainer\sprite_00646280_006463C0.bin
        INCBIN  build\spritecontainer\sprite_006463C0_00646404.bin
        INCBIN  build\spritecontainer\sprite_00646404_00646CFC.bin
        INCBIN  build\spritecontainer\sprite_00646CFC_00646E3C.bin
        INCBIN  build\spritecontainer\sprite_00646E3C_00646E80.bin
        INCBIN  build\spritecontainer\sprite_00646E80_0064727C.bin
        INCBIN  build\spritecontainer\sprite_0064727C_0064731C.bin
        INCBIN  build\spritecontainer\sprite_0064731C_00647360.bin
        INCBIN  build\spritecontainer\sprite_00647360_00647C5C.bin
        INCBIN  build\spritecontainer\sprite_00647C5C_00647D4C.bin
        INCBIN  build\spritecontainer\sprite_00647D4C_00647D80.bin
        INCBIN  build\spritecontainer\sprite_00647D80_00647E70.bin
        INCBIN  build\spritecontainer\sprite_00647E70_00647EA4.bin
        INCBIN  build\spritecontainer\sprite_00647EA4_00648B04.bin
        INCBIN  build\spritecontainer\sprite_00648B04_00648CBC.bin
        INCBIN  build\spritecontainer\sprite_00648CBC_00648D70.bin
        INCBIN  build\spritecontainer\sprite_00648D70_0064937C.bin
        INCBIN  build\spritecontainer\sprite_0064937C_0064941C.bin
        INCBIN  build\spritecontainer\sprite_0064941C_00649440.bin
        INCBIN  build\spritecontainer\sprite_00649440_0064A018.bin
        INCBIN  build\spritecontainer\sprite_0064A018_0064A158.bin
        INCBIN  build\spritecontainer\sprite_0064A158_0064A19C.bin
        INCBIN  build\spritecontainer\sprite_0064A19C_0064AE8C.bin
        INCBIN  build\spritecontainer\sprite_0064AE8C_0064AFCC.bin
        INCBIN  build\spritecontainer\sprite_0064AFCC_0064B010.bin
        INCBIN  build\spritecontainer\sprite_0064B010_0064B9EC.bin
        INCBIN  build\spritecontainer\sprite_0064B9EC_0064BADC.bin
        INCBIN  build\spritecontainer\sprite_0064BADC_0064BB10.bin
        INCBIN  build\spritecontainer\sprite_0064BB10_0064C824.bin
        INCBIN  build\spritecontainer\sprite_0064C824_0064C964.bin
        INCBIN  build\spritecontainer\sprite_0064C964_0064C9A8.bin
        INCBIN  build\spritecontainer\sprite_0064C9A8_0064D7F0.bin
        INCBIN  build\spritecontainer\sprite_0064D7F0_0064D930.bin
        INCBIN  build\spritecontainer\sprite_0064D930_0064D974.bin
        INCBIN  build\spritecontainer\sprite_0064D974_0064DC58.bin
        INCBIN  build\spritecontainer\sprite_0064DC58_0064DCA8.bin
        INCBIN  build\spritecontainer\sprite_0064DCA8_0064DCBC.bin
        INCBIN  build\spritecontainer\sprite_0064DCBC_0064E624.bin
        INCBIN  build\spritecontainer\sprite_0064E624_0064E714.bin
        INCBIN  build\spritecontainer\sprite_0064E714_0064E748.bin
        INCBIN  build\spritecontainer\sprite_0064E748_0064EBA0.bin
        INCBIN  build\spritecontainer\sprite_0064EBA0_0064EBF0.bin
        INCBIN  build\spritecontainer\sprite_0064EBF0_0064EC34.bin
        INCBIN  build\spritecontainer\sprite_0064EC34_0064EE48.bin
        INCBIN  build\spritecontainer\sprite_0064EE48_0064EE70.bin
        INCBIN  build\spritecontainer\sprite_0064EE70_0064EE94.bin
        INCBIN  build\spritecontainer\sprite_0064EE94_0064F0BC.bin
        INCBIN  build\spritecontainer\sprite_0064F0BC_0064F0E4.bin
        INCBIN  build\spritecontainer\sprite_0064F0E4_0064F108.bin
        INCBIN  build\spritecontainer\sprite_0064F108_0064F9CC.bin
        INCBIN  build\spritecontainer\sprite_0064F9CC_0064FABC.bin
        INCBIN  build\spritecontainer\sprite_0064FABC_0064FAF0.bin
        INCBIN  build\spritecontainer\sprite_0064FAF0_00650604.bin
        INCBIN  build\spritecontainer\sprite_00650604_00650744.bin
        INCBIN  build\spritecontainer\sprite_00650744_00650788.bin
        INCBIN  build\spritecontainer\sprite_00650788_00650AA4.bin
        INCBIN  build\spritecontainer\sprite_00650AA4_00650B44.bin
        INCBIN  build\spritecontainer\sprite_00650B44_00650B88.bin
        INCBIN  build\spritecontainer\sprite_00650B88_00651514.bin
        INCBIN  build\spritecontainer\sprite_00651514_00651604.bin
        INCBIN  build\spritecontainer\sprite_00651604_00651638.bin
        INCBIN  build\spritecontainer\sprite_00651638_00651728.bin
        INCBIN  build\spritecontainer\sprite_00651728_0065175C.bin
        INCBIN  build\spritecontainer\sprite_0065175C_006523CC.bin
        INCBIN  build\spritecontainer\sprite_006523CC_00652584.bin
        INCBIN  build\spritecontainer\sprite_00652584_00652638.bin
        INCBIN  build\spritecontainer\sprite_00652638_00652B5C.bin
        INCBIN  build\spritecontainer\sprite_00652B5C_00652BFC.bin
        INCBIN  build\spritecontainer\sprite_00652BFC_00652C20.bin
        INCBIN  build\spritecontainer\sprite_00652C20_0065382C.bin
        INCBIN  build\spritecontainer\sprite_0065382C_0065396C.bin
        INCBIN  build\spritecontainer\sprite_0065396C_006539B0.bin
        INCBIN  build\spritecontainer\sprite_006539B0_00653E00.bin
        INCBIN  build\spritecontainer\sprite_00653E00_00653EA0.bin
        INCBIN  build\spritecontainer\sprite_00653EA0_00653EC4.bin
        INCBIN  build\spritecontainer\sprite_00653EC4_00654908.bin
        INCBIN  build\spritecontainer\sprite_00654908_00654A48.bin
        INCBIN  build\spritecontainer\sprite_00654A48_00654A8C.bin
        INCBIN  build\spritecontainer\sprite_00654A8C_006556BC.bin
        INCBIN  build\spritecontainer\sprite_006556BC_006557FC.bin
        INCBIN  build\spritecontainer\sprite_006557FC_00655840.bin
        INCBIN  build\spritecontainer\sprite_00655840_0065645C.bin
        INCBIN  build\spritecontainer\sprite_0065645C_0065659C.bin
        INCBIN  build\spritecontainer\sprite_0065659C_006565E0.bin
        INCBIN  build\spritecontainer\sprite_006565E0_00656854.bin
        INCBIN  build\spritecontainer\sprite_00656854_006568A4.bin
        INCBIN  build\spritecontainer\sprite_006568A4_006568B8.bin
        INCBIN  build\spritecontainer\sprite_006568B8_006570E4.bin
        INCBIN  build\spritecontainer\sprite_006570E4_006571D4.bin
        INCBIN  build\spritecontainer\sprite_006571D4_00657208.bin
        INCBIN  build\spritecontainer\sprite_00657208_00657728.bin
        INCBIN  build\spritecontainer\sprite_00657728_006577C8.bin
        INCBIN  build\spritecontainer\sprite_006577C8_006577EC.bin
        INCBIN  build\spritecontainer\sprite_006577EC_00657B38.bin
        INCBIN  build\spritecontainer\sprite_00657B38_00657BD8.bin
        INCBIN  build\spritecontainer\sprite_00657BD8_00657C1C.bin
        INCBIN  build\spritecontainer\sprite_00657C1C_00658160.bin
        INCBIN  build\spritecontainer\sprite_00658160_00658200.bin
        INCBIN  build\spritecontainer\sprite_00658200_00658224.bin
        INCBIN  build\spritecontainer\sprite_00658224_00659140.bin
        INCBIN  build\spritecontainer\sprite_00659140_00659280.bin
        INCBIN  build\spritecontainer\sprite_00659280_006592C4.bin
        INCBIN  build\spritecontainer\sprite_006592C4_00659D64.bin
        INCBIN  build\spritecontainer\sprite_00659D64_00659E54.bin
        INCBIN  build\spritecontainer\sprite_00659E54_00659E88.bin
        INCBIN  build\spritecontainer\sprite_00659E88_0065ADC4.bin
        INCBIN  build\spritecontainer\sprite_0065ADC4_0065AF04.bin
        INCBIN  build\spritecontainer\sprite_0065AF04_0065AF48.bin
        INCBIN  build\spritecontainer\sprite_0065AF48_0065BA88.bin
        INCBIN  build\spritecontainer\sprite_0065BA88_0065BBC8.bin
        INCBIN  build\spritecontainer\sprite_0065BBC8_0065BC0C.bin
        INCBIN  build\spritecontainer\sprite_0065BC0C_0065BCFC.bin
        INCBIN  build\spritecontainer\sprite_0065BCFC_0065BD30.bin
        INCBIN  build\spritecontainer\sprite_0065BD30_0065C214.bin
        INCBIN  build\spritecontainer\sprite_0065C214_0065C2B4.bin
        INCBIN  build\spritecontainer\sprite_0065C2B4_0065C2D8.bin
        INCBIN  build\spritecontainer\sprite_0065C2D8_0065CE64.bin
        INCBIN  build\spritecontainer\sprite_0065CE64_0065CFA4.bin
        INCBIN  build\spritecontainer\sprite_0065CFA4_0065CFE8.bin
        INCBIN  build\spritecontainer\sprite_0065CFE8_0065D4AC.bin
        INCBIN  build\spritecontainer\sprite_0065D4AC_0065D54C.bin
        INCBIN  build\spritecontainer\sprite_0065D54C_0065D590.bin
        INCBIN  build\spritecontainer\sprite_0065D590_0065DA00.bin
        INCBIN  build\spritecontainer\sprite_0065DA00_0065DAA0.bin
        INCBIN  build\spritecontainer\sprite_0065DAA0_0065DAC4.bin
        INCBIN  build\spritecontainer\sprite_0065DAC4_0065E520.bin
        INCBIN  build\spritecontainer\sprite_0065E520_0065E660.bin
        INCBIN  build\spritecontainer\sprite_0065E660_0065E6A4.bin
        INCBIN  build\spritecontainer\sprite_0065E6A4_0065F120.bin
        INCBIN  build\spritecontainer\sprite_0065F120_0065F260.bin
        INCBIN  build\spritecontainer\sprite_0065F260_0065F2A4.bin
        INCBIN  build\spritecontainer\sprite_0065F2A4_0065FA7C.bin
        INCBIN  build\spritecontainer\sprite_0065FA7C_0065FB6C.bin
        INCBIN  build\spritecontainer\sprite_0065FB6C_0065FBA0.bin
        INCBIN  build\spritecontainer\sprite_0065FBA0_0066075C.bin
        INCBIN  build\spritecontainer\sprite_0066075C_0066089C.bin
        INCBIN  build\spritecontainer\sprite_0066089C_006608E0.bin
        INCBIN  build\spritecontainer\sprite_006608E0_00660A20.bin
        INCBIN  build\spritecontainer\sprite_00660A20_00660A64.bin
        INCBIN  build\spritecontainer\sprite_00660A64_00661644.bin
        INCBIN  build\spritecontainer\sprite_00661644_00661784.bin
        INCBIN  build\spritecontainer\sprite_00661784_006617C8.bin
        INCBIN  build\spritecontainer\sprite_006617C8_00661A4C.bin
        INCBIN  build\spritecontainer\sprite_00661A4C_00661A9C.bin
        INCBIN  build\spritecontainer\sprite_00661A9C_00661AB0.bin
        INCBIN  build\spritecontainer\sprite_00661AB0_00661EB0.bin
        INCBIN  build\spritecontainer\sprite_00661EB0_00661F00.bin
        INCBIN  build\spritecontainer\sprite_00661F00_00661F44.bin
        INCBIN  build\spritecontainer\sprite_00661F44_00662788.bin
        INCBIN  build\spritecontainer\sprite_00662788_00662878.bin
        INCBIN  build\spritecontainer\sprite_00662878_006628AC.bin
        INCBIN  build\spritecontainer\sprite_006628AC_00662E9C.bin
        INCBIN  build\spritecontainer\sprite_00662E9C_00662F78.bin
        INCBIN  build\spritecontainer\sprite_00662F78_0066302C.bin
        INCBIN  build\spritecontainer\sprite_0066302C_00663500.bin
        INCBIN  build\spritecontainer\sprite_00663500_006635A0.bin
        INCBIN  build\spritecontainer\sprite_006635A0_006635C4.bin
        INCBIN  build\spritecontainer\sprite_006635C4_006637A0.bin
        INCBIN  build\spritecontainer\sprite_006637A0_006637C8.bin
        INCBIN  build\spritecontainer\sprite_006637C8_006637EC.bin
        INCBIN  build\spritecontainer\sprite_006637EC_00663F64.bin
        INCBIN  build\spritecontainer\sprite_00663F64_00664054.bin
        INCBIN  build\spritecontainer\sprite_00664054_00664088.bin
        INCBIN  build\spritecontainer\sprite_00664088_006647FC.bin
        INCBIN  build\spritecontainer\sprite_006647FC_0066493C.bin
        INCBIN  build\spritecontainer\sprite_0066493C_00664980.bin
        INCBIN  build\spritecontainer\sprite_00664980_00664FB4.bin
        INCBIN  build\spritecontainer\sprite_00664FB4_006650F4.bin
        INCBIN  build\spritecontainer\sprite_006650F4_00665138.bin
        INCBIN  build\spritecontainer\sprite_00665138_00665544.bin
        INCBIN  build\spritecontainer\sprite_00665544_006655E4.bin
        INCBIN  build\spritecontainer\sprite_006655E4_00665628.bin
        INCBIN  build\spritecontainer\sprite_00665628_00665C9C.bin
        INCBIN  build\spritecontainer\sprite_00665C9C_00665D3C.bin
        INCBIN  build\spritecontainer\sprite_00665D3C_00665D60.bin
        INCBIN  build\spritecontainer\sprite_00665D60_00666FB8.bin
        INCBIN  build\spritecontainer\sprite_00666FB8_00667148.bin
        INCBIN  build\spritecontainer\sprite_00667148_0066719C.bin
        INCBIN  build\spritecontainer\sprite_0066719C_00667CF8.bin
        INCBIN  build\spritecontainer\sprite_00667CF8_00667EB0.bin
        INCBIN  build\spritecontainer\sprite_00667EB0_00667F64.bin
|unk_08667F64|
        INCBIN  build\spritecontainer\sprite_00667F64_006681EC.bin
        INCBIN  build\spritecontainer\sprite_006681EC_00668244.bin
        INCBIN  build\spritecontainer\sprite_00668244_006686E0.bin
        INCBIN  build\spritecontainer\sprite_006686E0_00668780.bin
        INCBIN  build\spritecontainer\sprite_00668780_006687A4.bin
        INCBIN  build\spritecontainer\sprite_006687A4_00668CF8.bin
        INCBIN  build\spritecontainer\sprite_00668CF8_00668D98.bin
        INCBIN  build\spritecontainer\sprite_00668D98_00668DBC.bin
        INCBIN  build\spritecontainer\sprite_00668DBC_006692DC.bin
        INCBIN  build\spritecontainer\sprite_006692DC_0066937C.bin
        INCBIN  build\spritecontainer\sprite_0066937C_006693A0.bin
        INCBIN  build\spritecontainer\sprite_006693A0_00669FE8.bin
        INCBIN  build\spritecontainer\sprite_00669FE8_0066A128.bin
        INCBIN  build\spritecontainer\sprite_0066A128_0066A16C.bin
        INCBIN  build\spritecontainer\sprite_0066A16C_0066ADB8.bin
        INCBIN  build\spritecontainer\sprite_0066ADB8_0066AEF8.bin
        INCBIN  build\spritecontainer\sprite_0066AEF8_0066AF3C.bin
        INCBIN  build\spritecontainer\sprite_0066AF3C_0066B8AC.bin
        INCBIN  build\spritecontainer\sprite_0066B8AC_0066B99C.bin
        INCBIN  build\spritecontainer\sprite_0066B99C_0066B9D0.bin
        INCBIN  build\spritecontainer\sprite_0066B9D0_0066C7A0.bin
        INCBIN  build\spritecontainer\sprite_0066C7A0_0066C8E0.bin
        INCBIN  build\spritecontainer\sprite_0066C8E0_0066C924.bin
        INCBIN  build\spritecontainer\sprite_0066C924_0066CA64.bin
        INCBIN  build\spritecontainer\sprite_0066CA64_0066CAA8.bin
        INCBIN  build\spritecontainer\sprite_0066CAA8_0066D884.bin
        INCBIN  build\spritecontainer\sprite_0066D884_0066D9C4.bin
        INCBIN  build\spritecontainer\sprite_0066D9C4_0066DA08.bin
        INCBIN  build\spritecontainer\sprite_0066DA08_0066DCFC.bin
        INCBIN  build\spritecontainer\sprite_0066DCFC_0066DD4C.bin
        INCBIN  build\spritecontainer\sprite_0066DD4C_0066DD60.bin
        INCBIN  build\spritecontainer\sprite_0066DD60_0066E708.bin
        INCBIN  build\spritecontainer\sprite_0066E708_0066E7F8.bin
        INCBIN  build\spritecontainer\sprite_0066E7F8_0066E82C.bin
        INCBIN  build\spritecontainer\sprite_0066E82C_0066EC7C.bin
        INCBIN  build\spritecontainer\sprite_0066EC7C_0066ECCC.bin
        INCBIN  build\spritecontainer\sprite_0066ECCC_0066ED10.bin
        INCBIN  build\spritecontainer\sprite_0066ED10_0066F2C4.bin
        INCBIN  build\spritecontainer\sprite_0066F2C4_0066F364.bin
        INCBIN  build\spritecontainer\sprite_0066F364_0066F388.bin
        INCBIN  build\spritecontainer\sprite_0066F388_0066F590.bin
        INCBIN  build\spritecontainer\sprite_0066F590_0066F5B8.bin
        INCBIN  build\spritecontainer\sprite_0066F5B8_0066F5DC.bin
        INCBIN  build\spritecontainer\sprite_0066F5DC_0066FEC4.bin
        INCBIN  build\spritecontainer\sprite_0066FEC4_0066FFB4.bin
        INCBIN  build\spritecontainer\sprite_0066FFB4_0066FFE8.bin
        INCBIN  build\spritecontainer\sprite_0066FFE8_00670890.bin
        INCBIN  build\spritecontainer\sprite_00670890_006709D0.bin
        INCBIN  build\spritecontainer\sprite_006709D0_00670A14.bin
        INCBIN  build\spritecontainer\sprite_00670A14_006710B8.bin
        INCBIN  build\spritecontainer\sprite_006710B8_006711F8.bin
        INCBIN  build\spritecontainer\sprite_006711F8_0067123C.bin
        INCBIN  build\spritecontainer\sprite_0067123C_0067158C.bin
        INCBIN  build\spritecontainer\sprite_0067158C_0067162C.bin
        INCBIN  build\spritecontainer\sprite_0067162C_00671670.bin
        INCBIN  build\spritecontainer\sprite_00671670_00671DD0.bin
        INCBIN  build\spritecontainer\sprite_00671DD0_00671E70.bin
        INCBIN  build\spritecontainer\sprite_00671E70_00671E94.bin
        INCBIN  build\spritecontainer\sprite_00671E94_006730B4.bin
        INCBIN  build\spritecontainer\sprite_006730B4_00673244.bin
        INCBIN  build\spritecontainer\sprite_00673244_00673298.bin
        INCBIN  build\spritecontainer\sprite_00673298_00673EE8.bin
        INCBIN  build\spritecontainer\sprite_00673EE8_006740A0.bin
        INCBIN  build\spritecontainer\sprite_006740A0_00674154.bin
|unk_08674154|
        INCBIN  build\spritecontainer\sprite_00674154_00674384.bin
        INCBIN  build\spritecontainer\sprite_00674384_006743DC.bin
        INCBIN  build\spritecontainer\sprite_006743DC_0067498C.bin
        INCBIN  build\spritecontainer\sprite_0067498C_00674A2C.bin
        INCBIN  build\spritecontainer\sprite_00674A2C_00674A50.bin
        INCBIN  build\spritecontainer\sprite_00674A50_006757A8.bin
        INCBIN  build\spritecontainer\sprite_006757A8_006758E8.bin
        INCBIN  build\spritecontainer\sprite_006758E8_0067592C.bin
        INCBIN  build\spritecontainer\sprite_0067592C_006766C0.bin
        INCBIN  build\spritecontainer\sprite_006766C0_00676800.bin
        INCBIN  build\spritecontainer\sprite_00676800_00676844.bin
        INCBIN  build\spritecontainer\sprite_00676844_00677258.bin
        INCBIN  build\spritecontainer\sprite_00677258_00677348.bin
        INCBIN  build\spritecontainer\sprite_00677348_0067737C.bin
        INCBIN  build\spritecontainer\sprite_0067737C_0067824C.bin
        INCBIN  build\spritecontainer\sprite_0067824C_0067838C.bin
        INCBIN  build\spritecontainer\sprite_0067838C_006783D0.bin
        INCBIN  build\spritecontainer\sprite_006783D0_00679294.bin
        INCBIN  build\spritecontainer\sprite_00679294_006793D4.bin
        INCBIN  build\spritecontainer\sprite_006793D4_00679418.bin
        INCBIN  build\spritecontainer\sprite_00679418_00679748.bin
        INCBIN  build\spritecontainer\sprite_00679748_00679798.bin
        INCBIN  build\spritecontainer\sprite_00679798_006797AC.bin
        INCBIN  build\spritecontainer\sprite_006797AC_0067A1E4.bin
        INCBIN  build\spritecontainer\sprite_0067A1E4_0067A2D4.bin
        INCBIN  build\spritecontainer\sprite_0067A2D4_0067A308.bin
        INCBIN  build\spritecontainer\sprite_0067A308_0067A8D8.bin
        INCBIN  build\spritecontainer\sprite_0067A8D8_0067A9B4.bin
        INCBIN  build\spritecontainer\sprite_0067A9B4_0067AA68.bin
        INCBIN  build\spritecontainer\sprite_0067AA68_0067AECC.bin
        INCBIN  build\spritecontainer\sprite_0067AECC_0067AF1C.bin
        INCBIN  build\spritecontainer\sprite_0067AF1C_0067AF60.bin
        INCBIN  build\spritecontainer\sprite_0067AF60_0067B190.bin
        INCBIN  build\spritecontainer\sprite_0067B190_0067B1B8.bin
        INCBIN  build\spritecontainer\sprite_0067B1B8_0067B1DC.bin
        INCBIN  build\spritecontainer\sprite_0067B1DC_0067BB70.bin
        INCBIN  build\spritecontainer\sprite_0067BB70_0067BC60.bin
        INCBIN  build\spritecontainer\sprite_0067BC60_0067BC94.bin
        INCBIN  build\spritecontainer\sprite_0067BC94_0067C0EC.bin
        INCBIN  build\spritecontainer\sprite_0067C0EC_0067C18C.bin
        INCBIN  build\spritecontainer\sprite_0067C18C_0067C1D0.bin
        INCBIN  build\spritecontainer\sprite_0067C1D0_0067C9B0.bin
        INCBIN  build\spritecontainer\sprite_0067C9B0_0067CA50.bin
        INCBIN  build\spritecontainer\sprite_0067CA50_0067CA74.bin
        INCBIN  build\spritecontainer\sprite_0067CA74_0067D2F0.bin
        INCBIN  build\spritecontainer\sprite_0067D2F0_0067D610.bin
        INCBIN  build\spritecontainer\sprite_0067D610_0067D6B4.bin
        INCBIN  build\spritecontainer\sprite_0067D6B4_0067DB28.bin
        INCBIN  build\spritecontainer\sprite_0067DB28_0067DBC8.bin
        INCBIN  build\spritecontainer\sprite_0067DBC8_0067DBEC.bin
        INCBIN  build\spritecontainer\sprite_0067DBEC_0067E68C.bin
        INCBIN  build\spritecontainer\sprite_0067E68C_0067E7CC.bin
        INCBIN  build\spritecontainer\sprite_0067E7CC_0067E810.bin
        INCBIN  build\spritecontainer\sprite_0067E810_0067ECA0.bin
        INCBIN  build\spritecontainer\sprite_0067ECA0_0067ED40.bin
        INCBIN  build\spritecontainer\sprite_0067ED40_0067ED64.bin
        INCBIN  build\spritecontainer\sprite_0067ED64_0067F1D4.bin
        INCBIN  build\spritecontainer\sprite_0067F1D4_0067F274.bin
        INCBIN  build\spritecontainer\sprite_0067F274_0067F298.bin
        INCBIN  build\spritecontainer\sprite_0067F298_0067FD0C.bin
        INCBIN  build\spritecontainer\sprite_0067FD0C_0067FE4C.bin
        INCBIN  build\spritecontainer\sprite_0067FE4C_0067FE90.bin
        INCBIN  build\spritecontainer\sprite_0067FE90_006806AC.bin
        INCBIN  build\spritecontainer\sprite_006806AC_0068079C.bin
        INCBIN  build\spritecontainer\sprite_0068079C_006807D0.bin
        INCBIN  build\spritecontainer\sprite_006807D0_006813D8.bin
        INCBIN  build\spritecontainer\sprite_006813D8_00681518.bin
        INCBIN  build\spritecontainer\sprite_00681518_0068155C.bin
        INCBIN  build\spritecontainer\sprite_0068155C_00682174.bin
        INCBIN  build\spritecontainer\sprite_00682174_006822B4.bin
        INCBIN  build\spritecontainer\sprite_006822B4_006822F8.bin
        INCBIN  build\spritecontainer\sprite_006822F8_00682578.bin
        INCBIN  build\spritecontainer\sprite_00682578_006825C8.bin
        INCBIN  build\spritecontainer\sprite_006825C8_006825DC.bin
        INCBIN  build\spritecontainer\sprite_006825DC_00682E18.bin
        INCBIN  build\spritecontainer\sprite_00682E18_00682F08.bin
        INCBIN  build\spritecontainer\sprite_00682F08_00682F3C.bin
        INCBIN  build\spritecontainer\sprite_00682F3C_006833AC.bin
        INCBIN  build\spritecontainer\sprite_006833AC_0068344C.bin
        INCBIN  build\spritecontainer\sprite_0068344C_00683470.bin
        INCBIN  build\spritecontainer\sprite_00683470_00683CDC.bin
        INCBIN  build\spritecontainer\sprite_00683CDC_00683E1C.bin
        INCBIN  build\spritecontainer\sprite_00683E1C_00683E60.bin
        INCBIN  build\spritecontainer\sprite_00683E60_006841A4.bin
        INCBIN  build\spritecontainer\sprite_006841A4_00684244.bin
        INCBIN  build\spritecontainer\sprite_00684244_00684288.bin
        INCBIN  build\spritecontainer\sprite_00684288_00684434.bin
        INCBIN  build\spritecontainer\sprite_00684434_00684448.bin
        INCBIN  build\spritecontainer\sprite_00684448_0068445C.bin
        INCBIN  build\spritecontainer\sprite_0068445C_00684E78.bin
        INCBIN  build\spritecontainer\sprite_00684E78_00684FB8.bin
        INCBIN  build\spritecontainer\sprite_00684FB8_00684FFC.bin
        INCBIN  build\spritecontainer\sprite_00684FFC_006855B4.bin
        INCBIN  build\spritecontainer\sprite_006855B4_00685654.bin
        INCBIN  build\spritecontainer\sprite_00685654_00685678.bin
        INCBIN  build\spritecontainer\sprite_00685678_00686728.bin
        INCBIN  build\spritecontainer\sprite_00686728_00686868.bin
        INCBIN  build\spritecontainer\sprite_00686868_006868AC.bin
        INCBIN  build\spritecontainer\sprite_006868AC_00686D3C.bin
        INCBIN  build\spritecontainer\sprite_00686D3C_00686E2C.bin
        INCBIN  build\spritecontainer\sprite_00686E2C_00686E60.bin
        INCBIN  build\spritecontainer\sprite_00686E60_006873EC.bin
        INCBIN  build\spritecontainer\sprite_006873EC_0068748C.bin
        INCBIN  build\spritecontainer\sprite_0068748C_006874B0.bin
        INCBIN  build\spritecontainer\sprite_006874B0_00688234.bin
        INCBIN  build\spritecontainer\sprite_00688234_00688374.bin
        INCBIN  build\spritecontainer\sprite_00688374_006883B8.bin
        INCBIN  build\spritecontainer\sprite_006883B8_0068885C.bin
        INCBIN  build\spritecontainer\sprite_0068885C_006888FC.bin
        INCBIN  build\spritecontainer\sprite_006888FC_00688920.bin
        INCBIN  build\spritecontainer\sprite_00688920_00688E20.bin
        INCBIN  build\spritecontainer\sprite_00688E20_00688EC0.bin
        INCBIN  build\spritecontainer\sprite_00688EC0_00688EE4.bin
        INCBIN  build\spritecontainer\sprite_00688EE4_00689AD0.bin
        INCBIN  build\spritecontainer\sprite_00689AD0_00689C10.bin
        INCBIN  build\spritecontainer\sprite_00689C10_00689C54.bin
        INCBIN  build\spritecontainer\sprite_00689C54_0068A170.bin
        INCBIN  build\spritecontainer\sprite_0068A170_0068A210.bin
        INCBIN  build\spritecontainer\sprite_0068A210_0068A234.bin
        INCBIN  build\spritecontainer\sprite_0068A234_0068A724.bin
        INCBIN  build\spritecontainer\sprite_0068A724_0068A7C4.bin
        INCBIN  build\spritecontainer\sprite_0068A7C4_0068A7E8.bin
        INCBIN  build\spritecontainer\sprite_0068A7E8_0068B330.bin
        INCBIN  build\spritecontainer\sprite_0068B330_0068B470.bin
        INCBIN  build\spritecontainer\sprite_0068B470_0068B4B4.bin
        INCBIN  build\spritecontainer\sprite_0068B4B4_0068B984.bin
        INCBIN  build\spritecontainer\sprite_0068B984_0068BA24.bin
        INCBIN  build\spritecontainer\sprite_0068BA24_0068BA48.bin
        INCBIN  build\spritecontainer\sprite_0068BA48_0068BBAC.bin
        INCBIN  build\spritecontainer\sprite_0068BBAC_0068BBFC.bin
        INCBIN  build\spritecontainer\sprite_0068BBFC_0068BC10.bin
        INCBIN  build\spritecontainer\sprite_0068BC10_0068BCFC.bin
        INCBIN  build\spritecontainer\sprite_0068BCFC_0068BD4C.bin
        INCBIN  build\spritecontainer\sprite_0068BD4C_0068BD60.bin
        INCBIN  build\spritecontainer\sprite_0068BD60_0068BE10.bin
        INCBIN  build\spritecontainer\sprite_0068BE10_0068BE60.bin
        INCBIN  build\spritecontainer\sprite_0068BE60_0068BE74.bin
        INCBIN  build\spritecontainer\sprite_0068BE74_0068C38C.bin
        INCBIN  build\spritecontainer\sprite_0068C38C_0068C42C.bin
        INCBIN  build\spritecontainer\sprite_0068C42C_0068C450.bin
        INCBIN  build\spritecontainer\sprite_0068C450_0068CE34.bin
        INCBIN  build\spritecontainer\sprite_0068CE34_0068CE5C.bin
        INCBIN  build\spritecontainer\sprite_0068CE5C_0068CE80.bin
        INCBIN  build\spritecontainer\sprite_0068CE80_0068F4F0.bin
        INCBIN  build\spritecontainer\sprite_0068F4F0_0068F630.bin
        INCBIN  build\spritecontainer\sprite_0068F630_0068F674.bin
        INCBIN  build\spritecontainer\sprite_0068F674_0069094C.bin
        INCBIN  build\spritecontainer\sprite_0069094C_0069099C.bin
        INCBIN  build\spritecontainer\sprite_0069099C_006909E0.bin
        INCBIN  build\spritecontainer\sprite_006909E0_00690A30.bin
        INCBIN  build\spritecontainer\sprite_00690A30_00690A74.bin
        INCBIN  build\spritecontainer\sprite_00690A74_00690E50.bin
        INCBIN  build\spritecontainer\sprite_00690E50_00690E64.bin
        INCBIN  build\spritecontainer\sprite_00690E64_00690E78.bin
        INCBIN  build\spritecontainer\sprite_00690E78_006920F8.bin
        INCBIN  build\spritecontainer\sprite_006920F8_00692148.bin
        INCBIN  build\spritecontainer\sprite_00692148_0069218C.bin
        INCBIN  build\spritecontainer\sprite_0069218C_00693474.bin
        INCBIN  build\spritecontainer\sprite_00693474_006934EC.bin
        INCBIN  build\spritecontainer\sprite_006934EC_00693550.bin
        INCBIN  build\spritecontainer\sprite_00693550_0069517C.bin
        INCBIN  build\spritecontainer\sprite_0069517C_006951F4.bin
        INCBIN  build\spritecontainer\sprite_006951F4_00695258.bin
        INCBIN  build\spritecontainer\sprite_00695258_00695280.bin
        INCBIN  build\spritecontainer\sprite_00695280_006952A4.bin
        INCBIN  build\spritecontainer\sprite_006952A4_00695B6C.bin
        INCBIN  build\spritecontainer\sprite_00695B6C_00695C0C.bin
        INCBIN  build\spritecontainer\sprite_00695C0C_00695C30.bin
        INCBIN  build\spritecontainer\sprite_00695C30_00696B90.bin
        INCBIN  build\spritecontainer\sprite_00696B90_00696C80.bin
        INCBIN  build\spritecontainer\sprite_00696C80_00696CB4.bin
        INCBIN  build\spritecontainer\sprite_00696CB4_00697C04.bin
        INCBIN  build\spritecontainer\sprite_00697C04_00697CF4.bin
        INCBIN  build\spritecontainer\sprite_00697CF4_00697D28.bin
        INCBIN  build\spritecontainer\sprite_00697D28_00698AEC.bin
        INCBIN  build\spritecontainer\sprite_00698AEC_00698BDC.bin
        INCBIN  build\spritecontainer\sprite_00698BDC_00698C10.bin
        INCBIN  build\spritecontainer\sprite_00698C10_0069909C.bin
        INCBIN  build\spritecontainer\sprite_0069909C_0069913C.bin
        INCBIN  build\spritecontainer\sprite_0069913C_00699160.bin
        INCBIN  build\spritecontainer\sprite_00699160_00699C04.bin
        INCBIN  build\spritecontainer\sprite_00699C04_00699D44.bin
        INCBIN  build\spritecontainer\sprite_00699D44_00699D88.bin
        INCBIN  build\spritecontainer\sprite_00699D88_0069A214.bin
        INCBIN  build\spritecontainer\sprite_0069A214_0069A2B4.bin
        INCBIN  build\spritecontainer\sprite_0069A2B4_0069A2D8.bin
        INCBIN  build\spritecontainer\sprite_0069A2D8_0069AEEC.bin
        INCBIN  build\spritecontainer\sprite_0069AEEC_0069AFBC.bin
        INCBIN  build\spritecontainer\sprite_0069AFBC_0069AFE0.bin
        INCBIN  build\spritecontainer\sprite_0069AFE0_0069CFDC.bin
        INCBIN  build\spritecontainer\sprite_0069CFDC_0069D11C.bin
        INCBIN  build\spritecontainer\sprite_0069D11C_0069D160.bin
        INCBIN  build\spritecontainer\sprite_0069D160_0069F55C.bin
        INCBIN  build\spritecontainer\sprite_0069F55C_0069F69C.bin
        INCBIN  build\spritecontainer\sprite_0069F69C_0069F6E0.bin
        INCBIN  build\spritecontainer\sprite_0069F6E0_0069FDF8.bin
        INCBIN  build\spritecontainer\sprite_0069FDF8_0069FE48.bin
        INCBIN  build\spritecontainer\sprite_0069FE48_0069FE5C.bin
        INCBIN  build\spritecontainer\sprite_0069FE5C_006A15E4.bin
        INCBIN  build\spritecontainer\sprite_006A15E4_006A16D4.bin
        INCBIN  build\spritecontainer\sprite_006A16D4_006A1708.bin
        INCBIN  build\spritecontainer\sprite_006A1708_006A1D44.bin
        INCBIN  build\spritecontainer\sprite_006A1D44_006A1D94.bin
        INCBIN  build\spritecontainer\sprite_006A1D94_006A1DA8.bin
        INCBIN  build\spritecontainer\sprite_006A1DA8_006A25EC.bin
        INCBIN  build\spritecontainer\sprite_006A25EC_006A2664.bin
        INCBIN  build\spritecontainer\sprite_006A2664_006A2698.bin
        INCBIN  build\spritecontainer\sprite_006A2698_006A333C.bin
        INCBIN  build\spritecontainer\sprite_006A333C_006A33DC.bin
        INCBIN  build\spritecontainer\sprite_006A33DC_006A3420.bin
        INCBIN  build\spritecontainer\sprite_006A3420_006A3820.bin
        INCBIN  build\spritecontainer\sprite_006A3820_006A38C0.bin
        INCBIN  build\spritecontainer\sprite_006A38C0_006A38E4.bin
        INCBIN  build\spritecontainer\sprite_006A38E4_006A42F4.bin
        INCBIN  build\spritecontainer\sprite_006A42F4_006A4434.bin
        INCBIN  build\spritecontainer\sprite_006A4434_006A4478.bin
        INCBIN  build\spritecontainer\sprite_006A4478_006A4874.bin
        INCBIN  build\spritecontainer\sprite_006A4874_006A4914.bin
        INCBIN  build\spritecontainer\sprite_006A4914_006A4938.bin
        INCBIN  build\spritecontainer\sprite_006A4938_006A4D7C.bin
        INCBIN  build\spritecontainer\sprite_006A4D7C_006A4E1C.bin
        INCBIN  build\spritecontainer\sprite_006A4E1C_006A4E40.bin
        INCBIN  build\spritecontainer\sprite_006A4E40_006A58AC.bin
        INCBIN  build\spritecontainer\sprite_006A58AC_006A59EC.bin
        INCBIN  build\spritecontainer\sprite_006A59EC_006A5A30.bin
        INCBIN  build\spritecontainer\sprite_006A5A30_006A5E6C.bin
        INCBIN  build\spritecontainer\sprite_006A5E6C_006A5F0C.bin
        INCBIN  build\spritecontainer\sprite_006A5F0C_006A5F30.bin
        INCBIN  build\spritecontainer\sprite_006A5F30_006A6384.bin
        INCBIN  build\spritecontainer\sprite_006A6384_006A6424.bin
        INCBIN  build\spritecontainer\sprite_006A6424_006A6448.bin
        INCBIN  build\spritecontainer\sprite_006A6448_006A70F8.bin
        INCBIN  build\spritecontainer\sprite_006A70F8_006A7238.bin
        INCBIN  build\spritecontainer\sprite_006A7238_006A727C.bin
        INCBIN  build\spritecontainer\sprite_006A727C_006A7D8C.bin
        INCBIN  build\spritecontainer\sprite_006A7D8C_006A7E7C.bin
        INCBIN  build\spritecontainer\sprite_006A7E7C_006A7EB0.bin
        INCBIN  build\spritecontainer\sprite_006A7EB0_006A88AC.bin
|inc_0x6a88ac_0x7b79a4|
        INCBIN  build\spritedefs\spritedefs_006A88AC_006A899C.bin
        INCBIN  build\spritedefs\spritedefs_006A899C_006A89D0.bin
        INCBIN  build\spritedefs\spritedefs_006A89D0_006B6BDC.bin
        INCBIN  build\spritedefs\spritedefs_006B6BDC_006B7080.bin
        INCLUDE rawlabeled_6b7080.s
        INCBIN  build\endrom\endrom_006B7E8C_006B801C.bin
        INCLUDE rawlabeled_6b801c.s
        INCBIN  build\endrom\endrom_006B814C_006B8284.bin
        INCLUDE rawlabeled_6b8284.s
        INCBIN  build\endrom\endrom_006B8294_006B82DC.bin
        INCLUDE rawlabeled_6b82dc.s
        INCBIN  build\endrom\endrom_006B880C_006F393C.bin
        INCBIN  build\endrom\endrom_006F393C_006F3BC8.bin
|unk_086F3BC8|
        INCBIN  baserom.gba_0x6f3bc8_0x6f3c30.extracted
        INCBIN  build\endrom\endrom_006F3C30_006F82EC.bin
        INCBIN  build\endrom\endrom_006F82EC_006F9EC4.bin
        INCLUDE rawlabeled_6f9ec4.s
        INCBIN  build\endrom\endrom_006F9EC8_006FC238.bin
        INCBIN  build\endrom\endrom_006FC238_006FC260.bin
        INCLUDE rawlabeled_6fc260.s
        INCBIN  build\endrom\endrom_006FDA00_006FDA1C.bin
        INCLUDE rawlabeled_6fda1c.s
        INCBIN  build\endrom\endrom_006FDA30_006FDA4C.bin
        INCLUDE rawlabeled_6fda4c.s
        INCBIN  build\endrom\endrom_006FDB18_006FDB28.bin
|unk_086FDB28|
        INCBIN  baserom.gba_0x6fdb28_0x6fdb68.extracted
        INCBIN  build\endrom\endrom_006FDB68_006FDB78.bin
|unk_086FDB78|
        INCBIN  baserom.gba_0x6fdb78_0x6fdba4.extracted
        INCBIN  build\endrom\endrom_006FDBA4_006FDBB4.bin
|unk_086FDBB4|
        INCBIN  baserom.gba_0x6fdbb4_0x6fdbb8.extracted
        INCBIN  build\endrom\endrom_006FDBB8_006FDC18.bin
|unk_086FDC18|
        INCBIN  baserom.gba_0x6fdc18_0x6fdc44.extracted
        INCBIN  build\endrom\endrom_006FDC44_006FDC54.bin
|unk_086FDC54|
        INCBIN  baserom.gba_0x6fdc54_0x6fdc58.extracted
        INCBIN  build\endrom\endrom_006FDC58_006FDD3C.bin
|unk_086FDD3C|
        INCBIN  baserom.gba_0x6fdd3c_0x6fdd64.extracted
        INCBIN  build\endrom\endrom_006FDD64_006FDD74.bin
|unk_086FDD74|
        INCBIN  baserom.gba_0x6fdd74_0x6fdd78.extracted
        INCBIN  build\endrom\endrom_006FDD78_006FDD94.bin
|unk_086FDD94|
        INCBIN  baserom.gba_0x6fdd94_0x6fdda4.extracted
        INCBIN  build\endrom\endrom_006FDDA4_006FDDB4.bin
|unk_086FDDB4|
        INCBIN  baserom.gba_0x6fddb4_0x6fddb8.extracted
        INCBIN  build\endrom\endrom_006FDDB8_006FDE08.bin
|unk_086FDE08|
        INCBIN  baserom.gba_0x6fde08_0x6fde44.extracted
        INCBIN  build\endrom\endrom_006FDE44_006FDE54.bin
|unk_086FDE54|
        INCBIN  baserom.gba_0x6fde54_0x6fde58.extracted
        INCBIN  build\endrom\endrom_006FDE58_006FDEA0.bin
|unk_086FDEA0|
        INCBIN  baserom.gba_0x6fdea0_0x6fdedc.extracted
        INCBIN  build\endrom\endrom_006FDEDC_006FDEEC.bin
|unk_086FDEEC|
        INCBIN  baserom.gba_0x6fdeec_0x6fdef0.extracted
        INCBIN  build\endrom\endrom_006FDEF0_006FDF20.bin
|unk_086FDF20|
        INCBIN  baserom.gba_0x6fdf20_0x6fdf4c.extracted
        INCBIN  build\endrom\endrom_006FDF4C_006FDF5C.bin
|unk_086FDF5C|
        INCBIN  baserom.gba_0x6fdf5c_0x6fdf60.extracted
        INCBIN  build\endrom\endrom_006FDF60_006FE034.bin
|unk_086FE034|
        INCBIN  baserom.gba_0x6fe034_0x6fe044.extracted
        INCBIN  build\endrom\endrom_006FE044_006FE054.bin
|unk_086FE054|
        INCBIN  baserom.gba_0x6fe054_0x6fe058.extracted
        INCBIN  build\endrom\endrom_006FE058_006FE0A4.bin
|unk_086FE0A4|
        INCBIN  baserom.gba_0x6fe0a4_0x6fe0a8.extracted
        INCBIN  build\endrom\endrom_006FE0A8_006FE0F8.bin
|unk_086FE0F8|
        INCBIN  baserom.gba_0x6fe0f8_0x6fe11c.extracted
        INCBIN  build\endrom\endrom_006FE11C_006FE258.bin
|unk_086FE258|
        INCBIN  baserom.gba_0x6fe258_0x6fe25c.extracted
        INCBIN  build\endrom\endrom_006FE25C_006FE2BC.bin
|unk_086FE2BC|
        INCBIN  baserom.gba_0x6fe2bc_0x6fe2c0.extracted
        INCBIN  build\endrom\endrom_006FE2C0_006FE2E0.bin
|unk_086FE2E0|
        INCBIN  baserom.gba_0x6fe2e0_0x6fe2e4.extracted
        INCBIN  build\endrom\endrom_006FE2E4_006FE310.bin
|unk_086FE310|
        INCBIN  baserom.gba_0x6fe310_0x6fe344.extracted
        INCBIN  build\endrom\endrom_006FE344_006FE354.bin
|unk_086FE354|
        INCBIN  baserom.gba_0x6fe354_0x6fe358.extracted
        INCBIN  build\endrom\endrom_006FE358_006FE368.bin
|unk_086FE368|
        INCBIN  baserom.gba_0x6fe368_0x6fe36c.extracted
        INCBIN  build\endrom\endrom_006FE36C_006FE3E4.bin
|unk_086FE3E4|
        INCBIN  baserom.gba_0x6fe3e4_0x6fe3f8.extracted
        INCBIN  build\endrom\endrom_006FE3F8_006FE408.bin
|unk_086FE408|
        INCBIN  baserom.gba_0x6fe408_0x6fe40c.extracted
        INCBIN  build\endrom\endrom_006FE40C_006FE41C.bin
|unk_086FE41C|
        INCBIN  baserom.gba_0x6fe41c_0x6fe420.extracted
        INCBIN  build\endrom\endrom_006FE420_006FE46C.bin
|unk_086FE46C|
        INCBIN  baserom.gba_0x6fe46c_0x6fe470.extracted
        INCBIN  build\endrom\endrom_006FE470_006FE4B0.bin
|unk_086FE4B0|
        INCBIN  baserom.gba_0x6fe4b0_0x6fe4b4.extracted
        INCBIN  build\endrom\endrom_006FE4B4_006FE51C.bin
|unk_086FE51C|
        INCBIN  baserom.gba_0x6fe51c_0x6fe520.extracted
        INCBIN  build\endrom\endrom_006FE520_006FE578.bin
|unk_086FE578|
        INCBIN  baserom.gba_0x6fe578_0x6fe57c.extracted
        INCBIN  build\endrom\endrom_006FE57C_006FE5BC.bin
|unk_086FE5BC|
        INCBIN  baserom.gba_0x6fe5bc_0x6fe5cc.extracted
        INCBIN  build\endrom\endrom_006FE5CC_006FE5DC.bin
|unk_086FE5DC|
        INCBIN  baserom.gba_0x6fe5dc_0x6fe5e0.extracted
        INCBIN  build\endrom\endrom_006FE5E0_006FE638.bin
|unk_086FE638|
        INCBIN  baserom.gba_0x6fe638_0x6fe63c.extracted
        INCBIN  build\endrom\endrom_006FE63C_006FE67C.bin
|unk_086FE67C|
        INCBIN  baserom.gba_0x6fe67c_0x6fe68c.extracted
        INCBIN  build\endrom\endrom_006FE68C_006FE69C.bin
|unk_086FE69C|
        INCBIN  baserom.gba_0x6fe69c_0x6fe6b0.extracted
        INCBIN  build\endrom\endrom_006FE6B0_006FE6C0.bin
|unk_086FE6C0|
        INCBIN  baserom.gba_0x6fe6c0_0x6fe6c4.extracted
        INCBIN  build\endrom\endrom_006FE6C4_006FE6D4.bin
|unk_086FE6D4|
        INCBIN  baserom.gba_0x6fe6d4_0x6fe6e8.extracted
        INCBIN  build\endrom\endrom_006FE6E8_006FE6F8.bin
|unk_086FE6F8|
        INCBIN  baserom.gba_0x6fe6f8_0x6fe6fc.extracted
        INCBIN  build\endrom\endrom_006FE6FC_006FE70C.bin
|unk_086FE70C|
        INCBIN  baserom.gba_0x6fe70c_0x6fe734.extracted
        INCBIN  build\endrom\endrom_006FE734_006FE744.bin
|unk_086FE744|
        INCBIN  baserom.gba_0x6fe744_0x6fe76c.extracted
        INCBIN  build\endrom\endrom_006FE76C_006FE77C.bin
|unk_086FE77C|
        INCBIN  baserom.gba_0x6fe77c_0x6fe790.extracted
        INCBIN  build\endrom\endrom_006FE790_006FE7A0.bin
|unk_086FE7A0|
        INCBIN  baserom.gba_0x6fe7a0_0x6fe7b4.extracted
        INCBIN  build\endrom\endrom_006FE7B4_006FE7C4.bin
|unk_086FE7C4|
        INCBIN  baserom.gba_0x6fe7c4_0x6fe7c8.extracted
        INCBIN  build\endrom\endrom_006FE7C8_006FE820.bin
        INCLUDE rawlabeled_6fe820.s
        INCBIN  build\endrom\endrom_006FE824_006FE900.bin
        INCLUDE rawlabeled_6fe900.s
        INCBIN  build\endrom\endrom_006FE904_006FE9C0.bin
        INCLUDE rawlabeled_6fe9c0.s
        INCBIN  build\endrom\endrom_006FE9C4_006FE9D4.bin
        INCLUDE rawlabeled_6fe9d4.s
        INCBIN  build\endrom\endrom_006FE9E8_006FE9F8.bin
        INCLUDE rawlabeled_6fe9f8.s
        INCBIN  build\endrom\endrom_006FE9FC_006FEA30.bin
|unk_086FEA30|
        INCBIN  baserom.gba_0x6fea30_0x6fea44.extracted
        INCBIN  build\endrom\endrom_006FEA44_006FEA64.bin
|unk_086FEA64|
        INCBIN  baserom.gba_0x6fea64_0x6fea68.extracted
        INCBIN  build\endrom\endrom_006FEA68_006FEAC8.bin
|unk_086FEAC8|
        INCBIN  baserom.gba_0x6feac8_0x6fead8.extracted
        INCBIN  build\endrom\endrom_006FEAD8_006FEAE8.bin
|unk_086FEAE8|
        INCBIN  baserom.gba_0x6feae8_0x6feb10.extracted
        INCBIN  build\endrom\endrom_006FEB10_006FEB20.bin
|unk_086FEB20|
        INCBIN  baserom.gba_0x6feb20_0x6feb98.extracted
        INCBIN  build\endrom\endrom_006FEB98_006FEBA8.bin
|unk_086FEBA8|
        INCBIN  baserom.gba_0x6feba8_0x6febac.extracted
        INCBIN  build\endrom\endrom_006FEBAC_006FEBDC.bin
|unk_086FEBDC|
        INCBIN  baserom.gba_0x6febdc_0x6febe0.extracted
        INCBIN  build\endrom\endrom_006FEBE0_006FEBF0.bin
|unk_086FEBF0|
        INCBIN  baserom.gba_0x6febf0_0x6febf4.extracted
        INCBIN  build\endrom\endrom_006FEBF4_006FEC3C.bin
|unk_086FEC3C|
        INCBIN  baserom.gba_0x6fec3c_0x6fecb8.extracted
        INCBIN  build\endrom\endrom_006FECB8_006FECD8.bin
|unk_086FECD8|
        INCBIN  baserom.gba_0x6fecd8_0x6fecdc.extracted
        INCBIN  build\endrom\endrom_006FECDC_006FED14.bin
|unk_086FED14|
        INCBIN  baserom.gba_0x6fed14_0x6fed24.extracted
        INCBIN  build\endrom\endrom_006FED24_006FED34.bin
|unk_086FED34|
        INCBIN  baserom.gba_0x6fed34_0x6fed38.extracted
        INCBIN  build\endrom\endrom_006FED38_006FEDCC.bin
|unk_086FEDCC|
        INCBIN  baserom.gba_0x6fedcc_0x6fede0.extracted
        INCBIN  build\endrom\endrom_006FEDE0_006FEDF0.bin
|unk_086FEDF0|
        INCBIN  baserom.gba_0x6fedf0_0x6fedf4.extracted
        INCBIN  build\endrom\endrom_006FEDF4_006FEEA8.bin
|unk_086FEEA8|
        INCBIN  baserom.gba_0x6feea8_0x6feeac.extracted
        INCBIN  build\endrom\endrom_006FEEAC_006FEF04.bin
|unk_086FEF04|
        INCBIN  baserom.gba_0x6fef04_0x6fef14.extracted
        INCBIN  build\endrom\endrom_006FEF14_006FEF8C.bin
|unk_086FEF8C|
        INCBIN  baserom.gba_0x6fef8c_0x6fef9c.extracted
        INCBIN  build\endrom\endrom_006FEF9C_006FEFAC.bin
|unk_086FEFAC|
        INCBIN  baserom.gba_0x6fefac_0x6fefb0.extracted
        INCBIN  build\endrom\endrom_006FEFB0_006FF02C.bin
|unk_086FF02C|
        INCBIN  baserom.gba_0x6ff02c_0x6ff08c.extracted
        INCBIN  build\endrom\endrom_006FF08C_006FF09C.bin
|unk_086FF09C|
        INCBIN  baserom.gba_0x6ff09c_0x6ff0a0.extracted
        INCBIN  build\endrom\endrom_006FF0A0_006FF0C8.bin
|unk_086FF0C8|
        INCBIN  baserom.gba_0x6ff0c8_0x6ff0e0.extracted
        INCBIN  build\endrom\endrom_006FF0E0_006FF0F0.bin
|unk_086FF0F0|
        INCBIN  baserom.gba_0x6ff0f0_0x6ff0f4.extracted
        INCBIN  build\endrom\endrom_006FF0F4_006FF120.bin
|unk_086FF120|
        INCBIN  baserom.gba_0x6ff120_0x6ff130.extracted
        INCBIN  build\endrom\endrom_006FF130_006FF140.bin
|unk_086FF140|
        INCBIN  baserom.gba_0x6ff140_0x6ff168.extracted
        INCBIN  build\endrom\endrom_006FF168_006FF178.bin
|unk_086FF178|
        INCBIN  baserom.gba_0x6ff178_0x6ff1a4.extracted
        INCBIN  build\endrom\endrom_006FF1A4_006FF1B4.bin
|unk_086FF1B4|
        INCBIN  baserom.gba_0x6ff1b4_0x6ff22c.extracted
        INCBIN  build\endrom\endrom_006FF22C_006FF23C.bin
|unk_086FF23C|
        INCBIN  baserom.gba_0x6ff23c_0x6ff240.extracted
        INCBIN  build\endrom\endrom_006FF240_006FF2A8.bin
|unk_086FF2A8|
        INCBIN  baserom.gba_0x6ff2a8_0x6ff324.extracted
        INCBIN  build\endrom\endrom_006FF324_006FF344.bin
|unk_086FF344|
        INCBIN  baserom.gba_0x6ff344_0x6ff348.extracted
        INCBIN  build\endrom\endrom_006FF348_006FF380.bin
|unk_086FF380|
        INCBIN  baserom.gba_0x6ff380_0x6ff390.extracted
        INCBIN  build\endrom\endrom_006FF390_006FF3A0.bin
|unk_086FF3A0|
        INCBIN  baserom.gba_0x6ff3a0_0x6ff3a4.extracted
        INCBIN  build\endrom\endrom_006FF3A4_006FF420.bin
|unk_086FF420|
        INCBIN  baserom.gba_0x6ff420_0x6ff434.extracted
        INCBIN  build\endrom\endrom_006FF434_006FF444.bin
|unk_086FF444|
        INCBIN  baserom.gba_0x6ff444_0x6ff448.extracted
        INCBIN  build\endrom\endrom_006FF448_006FF4EC.bin
|unk_086FF4EC|
        INCBIN  baserom.gba_0x6ff4ec_0x6ff4f0.extracted
        INCBIN  build\endrom\endrom_006FF4F0_006FF538.bin
|unk_086FF538|
        INCBIN  baserom.gba_0x6ff538_0x6ff548.extracted
        INCBIN  build\endrom\endrom_006FF548_006FF5C0.bin
|unk_086FF5C0|
        INCBIN  baserom.gba_0x6ff5c0_0x6ff5d0.extracted
        INCBIN  build\endrom\endrom_006FF5D0_006FF5E0.bin
|unk_086FF5E0|
        INCBIN  baserom.gba_0x6ff5e0_0x6ff5e4.extracted
        INCBIN  build\endrom\endrom_006FF5E4_006FF640.bin
|unk_086FF640|
        INCBIN  baserom.gba_0x6ff640_0x6ff69c.extracted
        INCBIN  build\endrom\endrom_006FF69C_006FF6AC.bin
|unk_086FF6AC|
        INCBIN  baserom.gba_0x6ff6ac_0x6ff6b0.extracted
        INCBIN  build\endrom\endrom_006FF6B0_006FF6C0.bin
|unk_086FF6C0|
        INCBIN  baserom.gba_0x6ff6c0_0x6ff6d8.extracted
        INCBIN  build\endrom\endrom_006FF6D8_006FF6E8.bin
|unk_086FF6E8|
        INCBIN  baserom.gba_0x6ff6e8_0x6ff6ec.extracted
        INCBIN  build\endrom\endrom_006FF6EC_006FF78C.bin
|unk_086FF78C|
        INCBIN  baserom.gba_0x6ff78c_0x6ff790.extracted
        INCBIN  build\endrom\endrom_006FF790_006FF8FC.bin
        INCLUDE rawlabeled_6ff8fc.s
        INCBIN  build\endrom\endrom_006FF900_006FF940.bin
        INCLUDE rawlabeled_6ff940.s
        INCBIN  build\endrom\endrom_006FF974_006FF984.bin
        INCLUDE rawlabeled_6ff984.s
        INCBIN  build\endrom\endrom_006FF9AC_006FFA24.bin
        INCLUDE rawlabeled_6ffa24.s
        INCBIN  build\endrom\endrom_006FFA28_006FFA68.bin
        INCLUDE rawlabeled_6ffa68.s
        INCBIN  build\endrom\endrom_006FFA8C_006FFA9C.bin
        INCLUDE rawlabeled_6ffa9c.s
        INCBIN  build\endrom\endrom_006FFAA0_006FFAD8.bin
|unk_086FFAD8|
        INCBIN  baserom.gba_0x6ffad8_0x6ffaf0.extracted
        INCBIN  build\endrom\endrom_006FFAF0_006FFB00.bin
|unk_086FFB00|
        INCBIN  baserom.gba_0x6ffb00_0x6ffb04.extracted
        INCBIN  build\endrom\endrom_006FFB04_006FFB70.bin
|unk_086FFB70|
        INCBIN  baserom.gba_0x6ffb70_0x6ffb74.extracted
        INCBIN  build\endrom\endrom_006FFB74_006FFBD4.bin
|unk_086FFBD4|
        INCBIN  baserom.gba_0x6ffbd4_0x6ffbd8.extracted
        INCBIN  build\endrom\endrom_006FFBD8_006FFC18.bin
|unk_086FFC18|
        INCBIN  baserom.gba_0x6ffc18_0x6ffc28.extracted
        INCBIN  build\endrom\endrom_006FFC28_006FFCC4.bin
|unk_086FFCC4|
        INCBIN  baserom.gba_0x6ffcc4_0x6ffcd4.extracted
        INCBIN  build\endrom\endrom_006FFCD4_006FFCE4.bin
|unk_086FFCE4|
        INCBIN  baserom.gba_0x6ffce4_0x6ffd04.extracted
        INCBIN  build\endrom\endrom_006FFD04_006FFD14.bin
|unk_086FFD14|
        INCBIN  baserom.gba_0x6ffd14_0x6ffd28.extracted
        INCBIN  build\endrom\endrom_006FFD28_006FFD38.bin
|unk_086FFD38|
        INCBIN  baserom.gba_0x6ffd38_0x6ffd3c.extracted
        INCBIN  build\endrom\endrom_006FFD3C_006FFD80.bin
|unk_086FFD80|
        INCBIN  baserom.gba_0x6ffd80_0x6ffd90.extracted
        INCBIN  build\endrom\endrom_006FFD90_006FFE28.bin
|unk_086FFE28|
        INCBIN  baserom.gba_0x6ffe28_0x6ffe38.extracted
        INCBIN  build\endrom\endrom_006FFE38_006FFE48.bin
|unk_086FFE48|
        INCBIN  baserom.gba_0x6ffe48_0x6ffe5c.extracted
        INCBIN  build\endrom\endrom_006FFE5C_006FFE6C.bin
|unk_086FFE6C|
        INCBIN  baserom.gba_0x6ffe6c_0x6ffe70.extracted
        INCBIN  build\endrom\endrom_006FFE70_006FFE80.bin
|unk_086FFE80|
        INCBIN  baserom.gba_0x6ffe80_0x6ffe84.extracted
        INCBIN  build\endrom\endrom_006FFE84_006FFEE4.bin
|unk_086FFEE4|
        INCBIN  baserom.gba_0x6ffee4_0x6ffee8.extracted
        INCBIN  build\endrom\endrom_006FFEE8_006FFEF8.bin
|unk_086FFEF8|
        INCBIN  baserom.gba_0x6ffef8_0x6ffefc.extracted
        INCBIN  build\endrom\endrom_006FFEFC_006FFF0C.bin
|unk_086FFF0C|
        INCBIN  baserom.gba_0x6fff0c_0x6fff10.extracted
        INCBIN  build\endrom\endrom_006FFF10_006FFF20.bin
|unk_086FFF20|
        INCBIN  baserom.gba_0x6fff20_0x6fff24.extracted
        INCBIN  build\endrom\endrom_006FFF24_006FFF34.bin
|unk_086FFF34|
        INCBIN  baserom.gba_0x6fff34_0x6fff38.extracted
        INCBIN  build\endrom\endrom_006FFF38_006FFF70.bin
|unk_086FFF70|
        INCBIN  baserom.gba_0x6fff70_0x6fff80.extracted
        INCBIN  build\endrom\endrom_006FFF80_006FFF90.bin
|unk_086FFF90|
        INCBIN  baserom.gba_0x6fff90_0x6fff94.extracted
        INCBIN  build\endrom\endrom_006FFF94_006FFFC8.bin
|unk_086FFFC8|
        INCBIN  baserom.gba_0x6fffc8_0x700000.extracted
        INCBIN  build\endrom\endrom_00700000_00700010.bin
|unk_08700010|
        INCBIN  baserom.gba_0x700010_0x700014.extracted
        INCBIN  build\endrom\endrom_00700014_00700090.bin
|unk_08700090|
        INCBIN  baserom.gba_0x700090_0x7000b4.extracted
        INCBIN  build\endrom\endrom_007000B4_007000D4.bin
|unk_087000D4|
        INCBIN  baserom.gba_0x7000d4_0x7000e8.extracted
        INCBIN  build\endrom\endrom_007000E8_007000F8.bin
|unk_087000F8|
        INCBIN  baserom.gba_0x7000f8_0x700120.extracted
        INCBIN  build\endrom\endrom_00700120_00700130.bin
|unk_08700130|
        INCBIN  baserom.gba_0x700130_0x700144.extracted
        INCBIN  build\endrom\endrom_00700144_00700154.bin
|unk_08700154|
        INCBIN  baserom.gba_0x700154_0x700168.extracted
        INCBIN  build\endrom\endrom_00700168_00700178.bin
|unk_08700178|
        INCBIN  baserom.gba_0x700178_0x70017c.extracted
        INCBIN  build\endrom\endrom_0070017C_0070018C.bin
|unk_0870018C|
        INCBIN  baserom.gba_0x70018c_0x700190.extracted
        INCBIN  build\endrom\endrom_00700190_00700210.bin
|unk_08700210|
        INCBIN  baserom.gba_0x700210_0x700220.extracted
        INCBIN  build\endrom\endrom_00700220_00700230.bin
|unk_08700230|
        INCBIN  baserom.gba_0x700230_0x700234.extracted
        INCBIN  build\endrom\endrom_00700234_007002CC.bin
|unk_087002CC|
        INCBIN  baserom.gba_0x7002cc_0x7002d0.extracted
        INCBIN  build\endrom\endrom_007002D0_00700300.bin
|unk_08700300|
        INCBIN  baserom.gba_0x700300_0x700310.extracted
        INCBIN  build\endrom\endrom_00700310_00700320.bin
|unk_08700320|
        INCBIN  baserom.gba_0x700320_0x700324.extracted
        INCBIN  build\endrom\endrom_00700324_00700380.bin
|unk_08700380|
        INCBIN  baserom.gba_0x700380_0x700390.extracted
        INCBIN  build\endrom\endrom_00700390_007003A0.bin
|unk_087003A0|
        INCBIN  baserom.gba_0x7003a0_0x7003e8.extracted
        INCBIN  build\endrom\endrom_007003E8_007003F8.bin
|unk_087003F8|
        INCBIN  baserom.gba_0x7003f8_0x70040c.extracted
        INCBIN  build\endrom\endrom_0070040C_0070041C.bin
|unk_0870041C|
        INCBIN  baserom.gba_0x70041c_0x700420.extracted
        INCBIN  build\endrom\endrom_00700420_0070043C.bin
|unk_0870043C|
        INCBIN  baserom.gba_0x70043c_0x700450.extracted
        INCBIN  build\endrom\endrom_00700450_00700460.bin
|unk_08700460|
        INCBIN  baserom.gba_0x700460_0x700478.extracted
        INCBIN  build\endrom\endrom_00700478_00700488.bin
|unk_08700488|
        INCBIN  baserom.gba_0x700488_0x7004a0.extracted
        INCBIN  build\endrom\endrom_007004A0_007004B0.bin
|unk_087004B0|
        INCBIN  baserom.gba_0x7004b0_0x7004b4.extracted
        INCBIN  build\endrom\endrom_007004B4_007004C4.bin
|unk_087004C4|
        INCBIN  baserom.gba_0x7004c4_0x7004f0.extracted
        INCBIN  build\endrom\endrom_007004F0_00700500.bin
|unk_08700500|
        INCBIN  baserom.gba_0x700500_0x700504.extracted
        INCBIN  build\endrom\endrom_00700504_00700558.bin
|unk_08700558|
        INCBIN  baserom.gba_0x700558_0x700568.extracted
        INCBIN  build\endrom\endrom_00700568_007005F4.bin
|unk_087005F4|
        INCBIN  baserom.gba_0x7005f4_0x7005fc.extracted
        INCBIN  build\endrom\endrom_007005FC_00700650.bin
|unk_08700650|
        INCBIN  baserom.gba_0x700650_0x700658.extracted
        INCBIN  build\endrom\endrom_00700658_00700678.bin
|unk_08700678|
        INCBIN  baserom.gba_0x700678_0x70067c.extracted
        INCBIN  build\endrom\endrom_0070067C_00700700.bin
|unk_08700700|
        INCBIN  baserom.gba_0x700700_0x700710.extracted
        INCBIN  build\endrom\endrom_00700710_007007A4.bin
|unk_087007A4|
        INCBIN  baserom.gba_0x7007a4_0x7007a8.extracted
        INCBIN  build\endrom\endrom_007007A8_007007E8.bin
|unk_087007E8|
        INCBIN  baserom.gba_0x7007e8_0x7007f8.extracted
        INCBIN  build\endrom\endrom_007007F8_00700808.bin
|unk_08700808|
        INCBIN  baserom.gba_0x700808_0x700820.extracted
        INCBIN  build\endrom\endrom_00700820_00700830.bin
|unk_08700830|
        INCBIN  baserom.gba_0x700830_0x700848.extracted
        INCBIN  build\endrom\endrom_00700848_00700858.bin
|unk_08700858|
        INCBIN  baserom.gba_0x700858_0x70085c.extracted
        INCBIN  build\endrom\endrom_0070085C_00700888.bin
|unk_08700888|
        INCBIN  baserom.gba_0x700888_0x700898.extracted
        INCBIN  build\endrom\endrom_00700898_007008A8.bin
|unk_087008A8|
        INCBIN  baserom.gba_0x7008a8_0x7008ac.extracted
        INCBIN  build\endrom\endrom_007008AC_00700930.bin
|unk_08700930|
        INCBIN  baserom.gba_0x700930_0x700940.extracted
        INCBIN  build\endrom\endrom_00700940_00700950.bin
|unk_08700950|
        INCBIN  baserom.gba_0x700950_0x700954.extracted
        INCBIN  build\endrom\endrom_00700954_00700974.bin
|unk_08700974|
        INCBIN  baserom.gba_0x700974_0x700978.extracted
        INCBIN  build\endrom\endrom_00700978_00700988.bin
|unk_08700988|
        INCBIN  baserom.gba_0x700988_0x70098c.extracted
        INCBIN  build\endrom\endrom_0070098C_007009B8.bin
|unk_087009B8|
        INCBIN  baserom.gba_0x7009b8_0x7009e0.extracted
        INCBIN  build\endrom\endrom_007009E0_00700AE8.bin
|unk_08700AE8|
        INCBIN  baserom.gba_0x700ae8_0x700b10.extracted
        INCBIN  build\endrom\endrom_00700B10_00700B20.bin
|unk_08700B20|
        INCBIN  baserom.gba_0x700b20_0x700b28.extracted
        INCBIN  build\endrom\endrom_00700B28_00700B50.bin
|unk_08700B50|
        INCBIN  baserom.gba_0x700b50_0x700b54.extracted
        INCBIN  build\endrom\endrom_00700B54_00700B64.bin
|unk_08700B64|
        INCBIN  baserom.gba_0x700b64_0x700b68.extracted
        INCBIN  build\endrom\endrom_00700B68_00700C08.bin
|unk_08700C08|
        INCBIN  baserom.gba_0x700c08_0x700c0c.extracted
        INCBIN  build\endrom\endrom_00700C0C_00700C4C.bin
|unk_08700C4C|
        INCBIN  baserom.gba_0x700c4c_0x700c5c.extracted
        INCBIN  build\endrom\endrom_00700C5C_00700C6C.bin
|unk_08700C6C|
        INCBIN  baserom.gba_0x700c6c_0x700c7c.extracted
        INCBIN  build\endrom\endrom_00700C7C_00700C8C.bin
|unk_08700C8C|
        INCBIN  baserom.gba_0x700c8c_0x700d18.extracted
        INCBIN  build\endrom\endrom_00700D18_00700D28.bin
|unk_08700D28|
        INCBIN  baserom.gba_0x700d28_0x700da0.extracted
        INCBIN  build\endrom\endrom_00700DA0_00700DB0.bin
|unk_08700DB0|
        INCBIN  baserom.gba_0x700db0_0x700db4.extracted
        INCBIN  build\endrom\endrom_00700DB4_00700E20.bin
|unk_08700E20|
        INCBIN  baserom.gba_0x700e20_0x700e74.extracted
        INCBIN  build\endrom\endrom_00700E74_00700E94.bin
|unk_08700E94|
        INCBIN  baserom.gba_0x700e94_0x700e98.extracted
        INCBIN  build\endrom\endrom_00700E98_00700EB8.bin
|unk_08700EB8|
        INCBIN  baserom.gba_0x700eb8_0x700ec8.extracted
        INCBIN  build\endrom\endrom_00700EC8_00700ED8.bin
|unk_08700ED8|
        INCBIN  baserom.gba_0x700ed8_0x700edc.extracted
        INCBIN  build\endrom\endrom_00700EDC_00700F68.bin
|unk_08700F68|
        INCBIN  baserom.gba_0x700f68_0x700f80.extracted
        INCBIN  build\endrom\endrom_00700F80_00700F90.bin
|unk_08700F90|
        INCBIN  baserom.gba_0x700f90_0x700f94.extracted
        INCBIN  build\endrom\endrom_00700F94_00701060.bin
|unk_08701060|
        INCBIN  baserom.gba_0x701060_0x7010a0.extracted
        INCBIN  build\endrom\endrom_007010A0_007010F4.bin
|unk_087010F4|
        INCBIN  baserom.gba_0x7010f4_0x7010f8.extracted
        INCBIN  build\endrom\endrom_007010F8_00701128.bin
|unk_08701128|
        INCBIN  baserom.gba_0x701128_0x701138.extracted
        INCBIN  build\endrom\endrom_00701138_00701148.bin
|unk_08701148|
        INCBIN  baserom.gba_0x701148_0x7011b8.extracted
        INCBIN  build\endrom\endrom_007011B8_007011C8.bin
|unk_087011C8|
        INCBIN  baserom.gba_0x7011c8_0x7011cc.extracted
        INCBIN  build\endrom\endrom_007011CC_007011F4.bin
|unk_087011F4|
        INCBIN  baserom.gba_0x7011f4_0x7011f8.extracted
        INCBIN  build\endrom\endrom_007011F8_00701208.bin
|unk_08701208|
        INCBIN  baserom.gba_0x701208_0x70120c.extracted
        INCBIN  build\endrom\endrom_0070120C_00701244.bin
|unk_08701244|
        INCBIN  baserom.gba_0x701244_0x701248.extracted
        INCBIN  build\endrom\endrom_00701248_00701298.bin
|unk_08701298|
        INCBIN  baserom.gba_0x701298_0x7012d4.extracted
        INCBIN  build\endrom\endrom_007012D4_007012E4.bin
|unk_087012E4|
        INCBIN  baserom.gba_0x7012e4_0x701310.extracted
        INCBIN  build\endrom\endrom_00701310_00701320.bin
|unk_08701320|
        INCBIN  baserom.gba_0x701320_0x701324.extracted
        INCBIN  build\endrom\endrom_00701324_0070137C.bin
|unk_0870137C|
        INCBIN  baserom.gba_0x70137c_0x7013a8.extracted
        INCBIN  build\endrom\endrom_007013A8_007013B8.bin
|unk_087013B8|
        INCBIN  baserom.gba_0x7013b8_0x7013bc.extracted
        INCBIN  build\endrom\endrom_007013BC_007014A0.bin
|unk_087014A0|
        INCBIN  baserom.gba_0x7014a0_0x7014a4.extracted
        INCBIN  build\endrom\endrom_007014A4_007014E4.bin
|unk_087014E4|
        INCBIN  baserom.gba_0x7014e4_0x7014f4.extracted
        INCBIN  build\endrom\endrom_007014F4_00701504.bin
|unk_08701504|
        INCBIN  baserom.gba_0x701504_0x701568.extracted
        INCBIN  build\endrom\endrom_00701568_00701578.bin
|unk_08701578|
        INCBIN  baserom.gba_0x701578_0x7015f0.extracted
        INCBIN  build\endrom\endrom_007015F0_00701600.bin
|unk_08701600|
        INCBIN  baserom.gba_0x701600_0x701604.extracted
        INCBIN  build\endrom\endrom_00701604_0070165C.bin
|unk_0870165C|
        INCBIN  baserom.gba_0x70165c_0x7016b0.extracted
        INCBIN  build\endrom\endrom_007016B0_007016D0.bin
|unk_087016D0|
        INCBIN  baserom.gba_0x7016d0_0x7016d4.extracted
        INCBIN  build\endrom\endrom_007016D4_007016F4.bin
|unk_087016F4|
        INCBIN  baserom.gba_0x7016f4_0x701704.extracted
        INCBIN  build\endrom\endrom_00701704_00701714.bin
|unk_08701714|
        INCBIN  baserom.gba_0x701714_0x701718.extracted
        INCBIN  build\endrom\endrom_00701718_00701794.bin
|unk_08701794|
        INCBIN  baserom.gba_0x701794_0x7017ac.extracted
        INCBIN  build\endrom\endrom_007017AC_007017BC.bin
|unk_087017BC|
        INCBIN  baserom.gba_0x7017bc_0x7017c0.extracted
        INCBIN  build\endrom\endrom_007017C0_00701868.bin
|unk_08701868|
        INCBIN  baserom.gba_0x701868_0x70186c.extracted
        INCBIN  build\endrom\endrom_0070186C_0070189C.bin
|unk_0870189C|
        INCBIN  baserom.gba_0x70189c_0x70190c.extracted
        INCBIN  build\endrom\endrom_0070190C_0070191C.bin
|unk_0870191C|
        INCBIN  baserom.gba_0x70191c_0x701920.extracted
        INCBIN  build\endrom\endrom_00701920_00701930.bin
|unk_08701930|
        INCBIN  baserom.gba_0x701930_0x701948.extracted
        INCBIN  build\endrom\endrom_00701948_00701958.bin
|unk_08701958|
        INCBIN  baserom.gba_0x701958_0x70195c.extracted
        INCBIN  build\endrom\endrom_0070195C_00701998.bin
|unk_08701998|
        INCBIN  baserom.gba_0x701998_0x70199c.extracted
        INCBIN  build\endrom\endrom_0070199C_007019DC.bin
|unk_087019DC|
        INCBIN  baserom.gba_0x7019dc_0x7019ec.extracted
        INCBIN  build\endrom\endrom_007019EC_007019FC.bin
|unk_087019FC|
        INCBIN  baserom.gba_0x7019fc_0x701a0c.extracted
        INCBIN  build\endrom\endrom_00701A0C_00701A1C.bin
|unk_08701A1C|
        INCBIN  baserom.gba_0x701a1c_0x701aa8.extracted
        INCBIN  build\endrom\endrom_00701AA8_00701AB8.bin
|unk_08701AB8|
        INCBIN  baserom.gba_0x701ab8_0x701b30.extracted
        INCBIN  build\endrom\endrom_00701B30_00701B40.bin
|unk_08701B40|
        INCBIN  baserom.gba_0x701b40_0x701b44.extracted
        INCBIN  build\endrom\endrom_00701B44_00701BB0.bin
|unk_08701BB0|
        INCBIN  baserom.gba_0x701bb0_0x701c04.extracted
        INCBIN  build\endrom\endrom_00701C04_00701C24.bin
|unk_08701C24|
        INCBIN  baserom.gba_0x701c24_0x701c28.extracted
        INCBIN  build\endrom\endrom_00701C28_00701C58.bin
|unk_08701C58|
        INCBIN  baserom.gba_0x701c58_0x701c68.extracted
        INCBIN  build\endrom\endrom_00701C68_00701C78.bin
|unk_08701C78|
        INCBIN  baserom.gba_0x701c78_0x701c7c.extracted
        INCBIN  build\endrom\endrom_00701C7C_00701CF8.bin
|unk_08701CF8|
        INCBIN  baserom.gba_0x701cf8_0x701d10.extracted
        INCBIN  build\endrom\endrom_00701D10_00701D20.bin
|unk_08701D20|
        INCBIN  baserom.gba_0x701d20_0x701d24.extracted
        INCBIN  build\endrom\endrom_00701D24_00701E00.bin
|unk_08701E00|
        INCBIN  baserom.gba_0x701e00_0x701e24.extracted
        INCBIN  build\endrom\endrom_00701E24_00701E34.bin
|unk_08701E34|
        INCBIN  baserom.gba_0x701e34_0x701e50.extracted
        INCBIN  build\endrom\endrom_00701E50_00701EA4.bin
|unk_08701EA4|
        INCBIN  baserom.gba_0x701ea4_0x701ea8.extracted
        INCBIN  build\endrom\endrom_00701EA8_00701ED8.bin
|unk_08701ED8|
        INCBIN  baserom.gba_0x701ed8_0x701ee8.extracted
        INCBIN  build\endrom\endrom_00701EE8_00701EF8.bin
|unk_08701EF8|
        INCBIN  baserom.gba_0x701ef8_0x701f68.extracted
        INCBIN  build\endrom\endrom_00701F68_00701F78.bin
|unk_08701F78|
        INCBIN  baserom.gba_0x701f78_0x701f7c.extracted
        INCBIN  build\endrom\endrom_00701F7C_00701FA4.bin
|unk_08701FA4|
        INCBIN  baserom.gba_0x701fa4_0x701fd4.extracted
        INCBIN  build\endrom\endrom_00701FD4_00701FE4.bin
|unk_08701FE4|
        INCBIN  baserom.gba_0x701fe4_0x701fe8.extracted
        INCBIN  build\endrom\endrom_00701FE8_00702050.bin
|unk_08702050|
        INCBIN  baserom.gba_0x702050_0x702054.extracted
        INCBIN  build\endrom\endrom_00702054_0070207C.bin
|unk_0870207C|
        INCBIN  baserom.gba_0x70207c_0x7020a0.extracted
        INCBIN  build\endrom\endrom_007020A0_007020B0.bin
|unk_087020B0|
        INCBIN  baserom.gba_0x7020b0_0x7020b4.extracted
        INCBIN  build\endrom\endrom_007020B4_0070210C.bin
|unk_0870210C|
        INCBIN  baserom.gba_0x70210c_0x702120.extracted
        INCBIN  build\endrom\endrom_00702120_00702130.bin
|unk_08702130|
        INCBIN  baserom.gba_0x702130_0x702134.extracted
        INCBIN  build\endrom\endrom_00702134_00702144.bin
|unk_08702144|
        INCBIN  baserom.gba_0x702144_0x702148.extracted
        INCBIN  build\endrom\endrom_00702148_00702188.bin
|unk_08702188|
        INCBIN  baserom.gba_0x702188_0x7021ac.extracted
        INCBIN  build\endrom\endrom_007021AC_007021BC.bin
|unk_087021BC|
        INCBIN  baserom.gba_0x7021bc_0x7021c0.extracted
        INCBIN  build\endrom\endrom_007021C0_00702228.bin
        INCLUDE rawlabeled_702228.s
        INCBIN  build\endrom\endrom_0070222C_0070226C.bin
        INCLUDE rawlabeled_70226c.s
        INCBIN  build\endrom\endrom_0070228C_0070229C.bin
        INCLUDE rawlabeled_70229c.s
        INCBIN  build\endrom\endrom_007022A0_007022B0.bin
        INCLUDE rawlabeled_7022b0.s
        INCBIN  build\endrom\endrom_007022B4_007022C4.bin
        INCLUDE rawlabeled_7022c4.s
        INCBIN  build\endrom\endrom_007022D8_007022E8.bin
        INCLUDE rawlabeled_7022e8.s
        INCBIN  build\endrom\endrom_00702310_00702320.bin
        INCLUDE rawlabeled_702320.s
        INCBIN  build\endrom\endrom_00702334_00702344.bin
        INCLUDE rawlabeled_702344.s
        INCBIN  build\endrom\endrom_00702348_00702358.bin
        INCLUDE rawlabeled_702358.s
        INCBIN  build\endrom\endrom_0070235C_00702470.bin
        INCLUDE rawlabeled_702470.s
        INCBIN  build\endrom\endrom_00702474_007024A4.bin
        INCLUDE rawlabeled_7024a4.s
        INCBIN  build\endrom\endrom_007024D8_007024E8.bin
        INCLUDE rawlabeled_7024e8.s
        INCBIN  build\endrom\endrom_007024EC_007024FC.bin
        INCLUDE rawlabeled_7024fc.s
        INCBIN  build\endrom\endrom_00702528_00702538.bin
        INCLUDE rawlabeled_702538.s
        INCBIN  build\endrom\endrom_0070253C_00702584.bin
|unk_08702584|
        INCBIN  baserom.gba_0x702584_0x702594.extracted
        INCBIN  build\endrom\endrom_00702594_007025A4.bin
|unk_087025A4|
        INCBIN  baserom.gba_0x7025a4_0x7025b8.extracted
        INCBIN  build\endrom\endrom_007025B8_007025C8.bin
|unk_087025C8|
        INCBIN  baserom.gba_0x7025c8_0x7025cc.extracted
        INCBIN  build\endrom\endrom_007025CC_007025DC.bin
|unk_087025DC|
        INCBIN  baserom.gba_0x7025dc_0x7025e0.extracted
        INCBIN  build\endrom\endrom_007025E0_00702624.bin
|unk_08702624|
        INCBIN  baserom.gba_0x702624_0x702628.extracted
        INCBIN  build\endrom\endrom_00702628_00702638.bin
|unk_08702638|
        INCBIN  baserom.gba_0x702638_0x70263c.extracted
        INCBIN  build\endrom\endrom_0070263C_007026C8.bin
|unk_087026C8|
        INCBIN  baserom.gba_0x7026c8_0x7026dc.extracted
        INCBIN  build\endrom\endrom_007026DC_007026EC.bin
|unk_087026EC|
        INCBIN  baserom.gba_0x7026ec_0x7026f0.extracted
        INCBIN  build\endrom\endrom_007026F0_0070271C.bin
|unk_0870271C|
        INCBIN  baserom.gba_0x70271c_0x70272c.extracted
        INCBIN  build\endrom\endrom_0070272C_007027B4.bin
|unk_087027B4|
        INCBIN  baserom.gba_0x7027b4_0x702804.extracted
        INCBIN  build\endrom\endrom_00702804_00702814.bin
|unk_08702814|
        INCBIN  baserom.gba_0x702814_0x702818.extracted
        INCBIN  build\endrom\endrom_00702818_0070289C.bin
|unk_0870289C|
        INCBIN  baserom.gba_0x70289c_0x7028b0.extracted
        INCBIN  build\endrom\endrom_007028B0_007028C0.bin
|unk_087028C0|
        INCBIN  baserom.gba_0x7028c0_0x7028c4.extracted
        INCBIN  build\endrom\endrom_007028C4_0070297C.bin
|unk_0870297C|
        INCBIN  baserom.gba_0x70297c_0x702980.extracted
        INCBIN  build\endrom\endrom_00702980_007029D0.bin
|unk_087029D0|
        INCBIN  baserom.gba_0x7029d0_0x7029e4.extracted
        INCBIN  build\endrom\endrom_007029E4_007029F4.bin
|unk_087029F4|
        INCBIN  baserom.gba_0x7029f4_0x702a30.extracted
        INCBIN  build\endrom\endrom_00702A30_00702A40.bin
|unk_08702A40|
        INCBIN  baserom.gba_0x702a40_0x702a80.extracted
        INCBIN  build\endrom\endrom_00702A80_00702A90.bin
|unk_08702A90|
        INCBIN  baserom.gba_0x702a90_0x702ac8.extracted
        INCBIN  build\endrom\endrom_00702AC8_00702AD8.bin
|unk_08702AD8|
        INCBIN  baserom.gba_0x702ad8_0x702aec.extracted
        INCBIN  build\endrom\endrom_00702AEC_00702AFC.bin
|unk_08702AFC|
        INCBIN  baserom.gba_0x702afc_0x702b00.extracted
        INCBIN  build\endrom\endrom_00702B00_00702B4C.bin
|unk_08702B4C|
        INCBIN  baserom.gba_0x702b4c_0x702b50.extracted
        INCBIN  build\endrom\endrom_00702B50_00702B94.bin
|unk_08702B94|
        INCBIN  baserom.gba_0x702b94_0x702b98.extracted
        INCBIN  build\endrom\endrom_00702B98_00702BC8.bin
|unk_08702BC8|
        INCBIN  baserom.gba_0x702bc8_0x702bdc.extracted
        INCBIN  build\endrom\endrom_00702BDC_00702BEC.bin
|unk_08702BEC|
        INCBIN  baserom.gba_0x702bec_0x702bf0.extracted
        INCBIN  build\endrom\endrom_00702BF0_00702C70.bin
|unk_08702C70|
        INCBIN  baserom.gba_0x702c70_0x702c74.extracted
        INCBIN  build\endrom\endrom_00702C74_00702CA0.bin
|unk_08702CA0|
        INCBIN  baserom.gba_0x702ca0_0x702ca4.extracted
        INCBIN  build\endrom\endrom_00702CA4_00702CB4.bin
|unk_08702CB4|
        INCBIN  baserom.gba_0x702cb4_0x702cb8.extracted
        INCBIN  build\endrom\endrom_00702CB8_00702D38.bin
|unk_08702D38|
        INCBIN  baserom.gba_0x702d38_0x702d3c.extracted
        INCBIN  build\endrom\endrom_00702D3C_00702D7C.bin
|unk_08702D7C|
        INCBIN  baserom.gba_0x702d7c_0x702db0.extracted
        INCBIN  build\endrom\endrom_00702DB0_00702DC0.bin
|unk_08702DC0|
        INCBIN  baserom.gba_0x702dc0_0x702dd8.extracted
        INCBIN  build\endrom\endrom_00702DD8_00702DE8.bin
|unk_08702DE8|
        INCBIN  baserom.gba_0x702de8_0x702dec.extracted
        INCBIN  build\endrom\endrom_00702DEC_00702E6C.bin
|unk_08702E6C|
        INCBIN  baserom.gba_0x702e6c_0x702e70.extracted
        INCBIN  build\endrom\endrom_00702E70_00702FA0.bin
|unk_08702FA0|
        INCBIN  baserom.gba_0x702fa0_0x702fb0.extracted
        INCBIN  build\endrom\endrom_00702FB0_00702FC0.bin
|unk_08702FC0|
        INCBIN  baserom.gba_0x702fc0_0x702fc4.extracted
        INCBIN  build\endrom\endrom_00702FC4_00703008.bin
|unk_08703008|
        INCBIN  baserom.gba_0x703008_0x703018.extracted
        INCBIN  build\endrom\endrom_00703018_00703028.bin
|unk_08703028|
        INCBIN  baserom.gba_0x703028_0x70302c.extracted
        INCBIN  build\endrom\endrom_0070302C_00703070.bin
|unk_08703070|
        INCBIN  baserom.gba_0x703070_0x703080.extracted
        INCBIN  build\endrom\endrom_00703080_00703090.bin
|unk_08703090|
        INCBIN  baserom.gba_0x703090_0x703094.extracted
        INCBIN  build\endrom\endrom_00703094_0070327C.bin
|unk_0870327C|
        INCBIN  baserom.gba_0x70327c_0x70328c.extracted
        INCBIN  build\endrom\endrom_0070328C_0070329C.bin
|unk_0870329C|
        INCBIN  baserom.gba_0x70329c_0x7032a0.extracted
        INCBIN  build\endrom\endrom_007032A0_007032D8.bin
|unk_087032D8|
        INCBIN  baserom.gba_0x7032d8_0x703310.extracted
        INCBIN  build\endrom\endrom_00703310_00703320.bin
|unk_08703320|
        INCBIN  baserom.gba_0x703320_0x703324.extracted
        INCBIN  build\endrom\endrom_00703324_00703474.bin
|unk_08703474|
        INCBIN  baserom.gba_0x703474_0x703484.extracted
        INCBIN  build\endrom\endrom_00703484_00703494.bin
|unk_08703494|
        INCBIN  baserom.gba_0x703494_0x703498.extracted
        INCBIN  build\endrom\endrom_00703498_00703524.bin
|unk_08703524|
        INCBIN  baserom.gba_0x703524_0x703528.extracted
        INCBIN  build\endrom\endrom_00703528_00703568.bin
|unk_08703568|
        INCBIN  baserom.gba_0x703568_0x70358c.extracted
        INCBIN  build\endrom\endrom_0070358C_0070359C.bin
|unk_0870359C|
        INCBIN  baserom.gba_0x70359c_0x7035d4.extracted
        INCBIN  build\endrom\endrom_007035D4_007035E4.bin
|unk_087035E4|
        INCBIN  baserom.gba_0x7035e4_0x7035e8.extracted
        INCBIN  build\endrom\endrom_007035E8_007035F8.bin
|unk_087035F8|
        INCBIN  baserom.gba_0x7035f8_0x70360c.extracted
        INCBIN  build\endrom\endrom_0070360C_0070361C.bin
|unk_0870361C|
        INCBIN  baserom.gba_0x70361c_0x703620.extracted
        INCBIN  build\endrom\endrom_00703620_00703630.bin
|unk_08703630|
        INCBIN  baserom.gba_0x703630_0x703644.extracted
        INCBIN  build\endrom\endrom_00703644_00703654.bin
|unk_08703654|
        INCBIN  baserom.gba_0x703654_0x703668.extracted
        INCBIN  build\endrom\endrom_00703668_00703678.bin
|unk_08703678|
        INCBIN  baserom.gba_0x703678_0x7036a0.extracted
        INCBIN  build\endrom\endrom_007036A0_007036B0.bin
|unk_087036B0|
        INCBIN  baserom.gba_0x7036b0_0x7036c4.extracted
        INCBIN  build\endrom\endrom_007036C4_007036D4.bin
|unk_087036D4|
        INCBIN  baserom.gba_0x7036d4_0x7036d8.extracted
        INCBIN  build\endrom\endrom_007036D8_007036E8.bin
|unk_087036E8|
        INCBIN  baserom.gba_0x7036e8_0x7036ec.extracted
        INCBIN  build\endrom\endrom_007036EC_00703784.bin
|unk_08703784|
        INCBIN  baserom.gba_0x703784_0x703788.extracted
        INCBIN  build\endrom\endrom_00703788_00703820.bin
|unk_08703820|
        INCBIN  baserom.gba_0x703820_0x703824.extracted
        INCBIN  build\endrom\endrom_00703824_00703904.bin
|unk_08703904|
        INCBIN  baserom.gba_0x703904_0x703938.extracted
        INCBIN  build\endrom\endrom_00703938_00703948.bin
|unk_08703948|
        INCBIN  baserom.gba_0x703948_0x703974.extracted
        INCBIN  build\endrom\endrom_00703974_00703984.bin
|unk_08703984|
        INCBIN  baserom.gba_0x703984_0x703988.extracted
        INCBIN  build\endrom\endrom_00703988_00703998.bin
|unk_08703998|
        INCBIN  baserom.gba_0x703998_0x7039c4.extracted
        INCBIN  build\endrom\endrom_007039C4_007039D4.bin
|unk_087039D4|
        INCBIN  baserom.gba_0x7039d4_0x7039d8.extracted
        INCBIN  build\endrom\endrom_007039D8_00703A98.bin
|unk_08703A98|
        INCBIN  baserom.gba_0x703a98_0x703acc.extracted
        INCBIN  build\endrom\endrom_00703ACC_00703ADC.bin
|unk_08703ADC|
        INCBIN  baserom.gba_0x703adc_0x703ae0.extracted
        INCBIN  build\endrom\endrom_00703AE0_00703AF0.bin
|unk_08703AF0|
        INCBIN  baserom.gba_0x703af0_0x703b04.extracted
        INCBIN  build\endrom\endrom_00703B04_00703B14.bin
|unk_08703B14|
        INCBIN  baserom.gba_0x703b14_0x703b18.extracted
        INCBIN  build\endrom\endrom_00703B18_00703B28.bin
|unk_08703B28|
        INCBIN  baserom.gba_0x703b28_0x703b3c.extracted
        INCBIN  build\endrom\endrom_00703B3C_00703B4C.bin
|unk_08703B4C|
        INCBIN  baserom.gba_0x703b4c_0x703b60.extracted
        INCBIN  build\endrom\endrom_00703B60_00703B70.bin
|unk_08703B70|
        INCBIN  baserom.gba_0x703b70_0x703b98.extracted
        INCBIN  build\endrom\endrom_00703B98_00703BA8.bin
|unk_08703BA8|
        INCBIN  baserom.gba_0x703ba8_0x703bbc.extracted
        INCBIN  build\endrom\endrom_00703BBC_00703BCC.bin
|unk_08703BCC|
        INCBIN  baserom.gba_0x703bcc_0x703bd0.extracted
        INCBIN  build\endrom\endrom_00703BD0_00703BE0.bin
|unk_08703BE0|
        INCBIN  baserom.gba_0x703be0_0x703be4.extracted
        INCBIN  build\endrom\endrom_00703BE4_00703C78.bin
|unk_08703C78|
        INCBIN  baserom.gba_0x703c78_0x703c7c.extracted
        INCBIN  build\endrom\endrom_00703C7C_00703D14.bin
|unk_08703D14|
        INCBIN  baserom.gba_0x703d14_0x703d18.extracted
        INCBIN  build\endrom\endrom_00703D18_00703E10.bin
|unk_08703E10|
        INCBIN  baserom.gba_0x703e10_0x703e20.extracted
        INCBIN  build\endrom\endrom_00703E20_00703E30.bin
|unk_08703E30|
        INCBIN  baserom.gba_0x703e30_0x703e68.extracted
        INCBIN  build\endrom\endrom_00703E68_00703E78.bin
|unk_08703E78|
        INCBIN  baserom.gba_0x703e78_0x703e7c.extracted
        INCBIN  build\endrom\endrom_00703E7C_00703E98.bin
|unk_08703E98|
        INCBIN  baserom.gba_0x703e98_0x703ec0.extracted
        INCBIN  build\endrom\endrom_00703EC0_00703ED0.bin
|unk_08703ED0|
        INCBIN  baserom.gba_0x703ed0_0x703ed4.extracted
        INCBIN  build\endrom\endrom_00703ED4_00703EE4.bin
|unk_08703EE4|
        INCBIN  baserom.gba_0x703ee4_0x703f10.extracted
        INCBIN  build\endrom\endrom_00703F10_00703F20.bin
|unk_08703F20|
        INCBIN  baserom.gba_0x703f20_0x703f24.extracted
        INCBIN  build\endrom\endrom_00703F24_00703F74.bin
|unk_08703F74|
        INCBIN  baserom.gba_0x703f74_0x703f78.extracted
        INCBIN  build\endrom\endrom_00703F78_00703FAC.bin
|unk_08703FAC|
        INCBIN  baserom.gba_0x703fac_0x703fe4.extracted
        INCBIN  build\endrom\endrom_00703FE4_00704004.bin
|unk_08704004|
        INCBIN  baserom.gba_0x704004_0x704014.extracted
        INCBIN  build\endrom\endrom_00704014_00704024.bin
|unk_08704024|
        INCBIN  baserom.gba_0x704024_0x704028.extracted
        INCBIN  build\endrom\endrom_00704028_007040BC.bin
|unk_087040BC|
        INCBIN  baserom.gba_0x7040bc_0x7040cc.extracted
        INCBIN  build\endrom\endrom_007040CC_007040EC.bin
|unk_087040EC|
        INCBIN  baserom.gba_0x7040ec_0x7040f0.extracted
        INCBIN  build\endrom\endrom_007040F0_00704148.bin
|unk_08704148|
        INCBIN  baserom.gba_0x704148_0x704164.extracted
        INCBIN  build\endrom\endrom_00704164_00704174.bin
|unk_08704174|
        INCBIN  baserom.gba_0x704174_0x704178.extracted
        INCBIN  build\endrom\endrom_00704178_007041A4.bin
|unk_087041A4|
        INCBIN  baserom.gba_0x7041a4_0x7041a8.extracted
        INCBIN  build\endrom\endrom_007041A8_007041E0.bin
|unk_087041E0|
        INCBIN  baserom.gba_0x7041e0_0x704200.extracted
        INCBIN  build\endrom\endrom_00704200_00704210.bin
|unk_08704210|
        INCBIN  baserom.gba_0x704210_0x704214.extracted
        INCBIN  build\endrom\endrom_00704214_007042C8.bin
|unk_087042C8|
        INCBIN  baserom.gba_0x7042c8_0x7042d8.extracted
        INCBIN  build\endrom\endrom_007042D8_007042E8.bin
|unk_087042E8|
        INCBIN  baserom.gba_0x7042e8_0x704304.extracted
        INCBIN  build\endrom\endrom_00704304_00704314.bin
|unk_08704314|
        INCBIN  baserom.gba_0x704314_0x704318.extracted
        INCBIN  build\endrom\endrom_00704318_00704408.bin
|unk_08704408|
        INCBIN  baserom.gba_0x704408_0x70440c.extracted
        INCBIN  build\endrom\endrom_0070440C_0070444C.bin
|unk_0870444C|
        INCBIN  baserom.gba_0x70444c_0x70446c.extracted
        INCBIN  build\endrom\endrom_0070446C_0070447C.bin
|unk_0870447C|
        INCBIN  baserom.gba_0x70447c_0x704480.extracted
        INCBIN  build\endrom\endrom_00704480_00704490.bin
|unk_08704490|
        INCBIN  baserom.gba_0x704490_0x704494.extracted
        INCBIN  build\endrom\endrom_00704494_007044A4.bin
|unk_087044A4|
        INCBIN  baserom.gba_0x7044a4_0x7044b8.extracted
        INCBIN  build\endrom\endrom_007044B8_007044C8.bin
|unk_087044C8|
        INCBIN  baserom.gba_0x7044c8_0x7044f0.extracted
        INCBIN  build\endrom\endrom_007044F0_00704500.bin
|unk_08704500|
        INCBIN  baserom.gba_0x704500_0x704514.extracted
        INCBIN  build\endrom\endrom_00704514_00704524.bin
|unk_08704524|
        INCBIN  baserom.gba_0x704524_0x704528.extracted
        INCBIN  build\endrom\endrom_00704528_00704538.bin
|unk_08704538|
        INCBIN  baserom.gba_0x704538_0x70453c.extracted
        INCBIN  build\endrom\endrom_0070453C_00704650.bin
|unk_08704650|
        INCBIN  baserom.gba_0x704650_0x704654.extracted
        INCBIN  build\endrom\endrom_00704654_00704684.bin
|unk_08704684|
        INCBIN  baserom.gba_0x704684_0x7046b8.extracted
        INCBIN  build\endrom\endrom_007046B8_007046C8.bin
|unk_087046C8|
        INCBIN  baserom.gba_0x7046c8_0x7046cc.extracted
        INCBIN  build\endrom\endrom_007046CC_007046DC.bin
|unk_087046DC|
        INCBIN  baserom.gba_0x7046dc_0x704708.extracted
        INCBIN  build\endrom\endrom_00704708_00704718.bin
|unk_08704718|
        INCBIN  baserom.gba_0x704718_0x70471c.extracted
        INCBIN  build\endrom\endrom_0070471C_00704758.bin
|unk_08704758|
        INCBIN  baserom.gba_0x704758_0x70475c.extracted
        INCBIN  build\endrom\endrom_0070475C_007047AC.bin
|unk_087047AC|
        INCBIN  baserom.gba_0x7047ac_0x7047c0.extracted
        INCBIN  build\endrom\endrom_007047C0_007047D0.bin
|unk_087047D0|
        INCBIN  baserom.gba_0x7047d0_0x7047d4.extracted
        INCBIN  build\endrom\endrom_007047D4_007047E4.bin
|unk_087047E4|
        INCBIN  baserom.gba_0x7047e4_0x7047f8.extracted
        INCBIN  build\endrom\endrom_007047F8_00704808.bin
|unk_08704808|
        INCBIN  baserom.gba_0x704808_0x704830.extracted
        INCBIN  build\endrom\endrom_00704830_00704840.bin
|unk_08704840|
        INCBIN  baserom.gba_0x704840_0x704854.extracted
        INCBIN  build\endrom\endrom_00704854_00704864.bin
|unk_08704864|
        INCBIN  baserom.gba_0x704864_0x704878.extracted
        INCBIN  build\endrom\endrom_00704878_00704888.bin
|unk_08704888|
        INCBIN  baserom.gba_0x704888_0x70488c.extracted
        INCBIN  build\endrom\endrom_0070488C_007048C8.bin
        INCLUDE rawlabeled_7048c8.s
        INCBIN  build\endrom\endrom_007048CC_0070494C.bin
|unk_0870494C|
        INCBIN  baserom.gba_0x70494c_0x704950.extracted
        INCBIN  build\endrom\endrom_00704950_00704A34.bin
|unk_08704A34|
        INCBIN  baserom.gba_0x704a34_0x704a44.extracted
        INCBIN  build\endrom\endrom_00704A44_00704A64.bin
|unk_08704A64|
        INCBIN  baserom.gba_0x704a64_0x704a68.extracted
        INCBIN  build\endrom\endrom_00704A68_00704AA4.bin
|unk_08704AA4|
        INCBIN  baserom.gba_0x704aa4_0x704aa8.extracted
        INCBIN  build\endrom\endrom_00704AA8_00704AE8.bin
|unk_08704AE8|
        INCBIN  baserom.gba_0x704ae8_0x704b08.extracted
        INCBIN  build\endrom\endrom_00704B08_00704B18.bin
|unk_08704B18|
        INCBIN  baserom.gba_0x704b18_0x704b1c.extracted
        INCBIN  build\endrom\endrom_00704B1C_00704B2C.bin
|unk_08704B2C|
        INCBIN  baserom.gba_0x704b2c_0x704b30.extracted
        INCBIN  build\endrom\endrom_00704B30_00704B40.bin
|unk_08704B40|
        INCBIN  baserom.gba_0x704b40_0x704b54.extracted
        INCBIN  build\endrom\endrom_00704B54_00704B64.bin
|unk_08704B64|
        INCBIN  baserom.gba_0x704b64_0x704b8c.extracted
        INCBIN  build\endrom\endrom_00704B8C_00704B9C.bin
|unk_08704B9C|
        INCBIN  baserom.gba_0x704b9c_0x704bc4.extracted
        INCBIN  build\endrom\endrom_00704BC4_00704BD4.bin
|unk_08704BD4|
        INCBIN  baserom.gba_0x704bd4_0x704bfc.extracted
        INCBIN  build\endrom\endrom_00704BFC_00704C0C.bin
|unk_08704C0C|
        INCBIN  baserom.gba_0x704c0c_0x704c20.extracted
        INCBIN  build\endrom\endrom_00704C20_00704C30.bin
|unk_08704C30|
        INCBIN  baserom.gba_0x704c30_0x704c34.extracted
        INCBIN  build\endrom\endrom_00704C34_00704C44.bin
|unk_08704C44|
        INCBIN  baserom.gba_0x704c44_0x704c48.extracted
        INCBIN  build\endrom\endrom_00704C48_00704CDC.bin
|unk_08704CDC|
        INCBIN  baserom.gba_0x704cdc_0x704ce0.extracted
        INCBIN  build\endrom\endrom_00704CE0_00704DC8.bin
|unk_08704DC8|
        INCBIN  baserom.gba_0x704dc8_0x704dcc.extracted
        INCBIN  build\endrom\endrom_00704DCC_00704DFC.bin
|unk_08704DFC|
        INCBIN  baserom.gba_0x704dfc_0x704e30.extracted
        INCBIN  build\endrom\endrom_00704E30_00704E40.bin
|unk_08704E40|
        INCBIN  baserom.gba_0x704e40_0x704e44.extracted
        INCBIN  build\endrom\endrom_00704E44_00704E54.bin
|unk_08704E54|
        INCBIN  baserom.gba_0x704e54_0x704e80.extracted
        INCBIN  build\endrom\endrom_00704E80_00704E90.bin
|unk_08704E90|
        INCBIN  baserom.gba_0x704e90_0x704e94.extracted
        INCBIN  build\endrom\endrom_00704E94_00704ED0.bin
|unk_08704ED0|
        INCBIN  baserom.gba_0x704ed0_0x704ed4.extracted
        INCBIN  build\endrom\endrom_00704ED4_00704F14.bin
|unk_08704F14|
        INCBIN  baserom.gba_0x704f14_0x704f34.extracted
        INCBIN  build\endrom\endrom_00704F34_00704F44.bin
|unk_08704F44|
        INCBIN  baserom.gba_0x704f44_0x704f48.extracted
        INCBIN  build\endrom\endrom_00704F48_00704F58.bin
|unk_08704F58|
        INCBIN  baserom.gba_0x704f58_0x704f5c.extracted
        INCBIN  build\endrom\endrom_00704F5C_00704F6C.bin
        INCLUDE rawlabeled_704f6c.s
        INCBIN  build\endrom\endrom_00704F80_00704F90.bin
        INCLUDE rawlabeled_704f90.s
        INCBIN  build\endrom\endrom_00704FB8_00704FC8.bin
|unk_08704FC8|
        INCBIN  baserom.gba_0x704fc8_0x704fdc.extracted
        INCBIN  build\endrom\endrom_00704FDC_00704FEC.bin
|unk_08704FEC|
        INCBIN  baserom.gba_0x704fec_0x704ff0.extracted
        INCBIN  build\endrom\endrom_00704FF0_00705000.bin
|unk_08705000|
        INCBIN  baserom.gba_0x705000_0x705004.extracted
        INCBIN  build\endrom\endrom_00705004_007050E4.bin
|unk_087050E4|
        INCBIN  baserom.gba_0x7050e4_0x7050e8.extracted
        INCBIN  build\endrom\endrom_007050E8_00705130.bin
|unk_08705130|
        INCBIN  baserom.gba_0x705130_0x705134.extracted
        INCBIN  build\endrom\endrom_00705134_00705168.bin
|unk_08705168|
        INCBIN  baserom.gba_0x705168_0x705178.extracted
        INCBIN  build\endrom\endrom_00705178_00705188.bin
|unk_08705188|
        INCBIN  baserom.gba_0x705188_0x7051e8.extracted
        INCBIN  build\endrom\endrom_007051E8_007051F8.bin
|unk_087051F8|
        INCBIN  baserom.gba_0x7051f8_0x7051fc.extracted
        INCBIN  build\endrom\endrom_007051FC_00705224.bin
        INCLUDE rawlabeled_705224.s
        INCBIN  build\endrom\endrom_0070527C_0070528C.bin
|unk_0870528C|
        INCBIN  baserom.gba_0x70528c_0x705290.extracted
        INCBIN  build\endrom\endrom_00705290_007052F0.bin
|unk_087052F0|
        INCBIN  baserom.gba_0x7052f0_0x705300.extracted
        INCBIN  build\endrom\endrom_00705300_00705310.bin
|unk_08705310|
        INCBIN  baserom.gba_0x705310_0x705320.extracted
        INCBIN  build\endrom\endrom_00705320_00705330.bin
|unk_08705330|
        INCBIN  baserom.gba_0x705330_0x705334.extracted
        INCBIN  build\endrom\endrom_00705334_00705360.bin
|unk_08705360|
        INCBIN  baserom.gba_0x705360_0x705364.extracted
        INCBIN  build\endrom\endrom_00705364_007053C4.bin
|unk_087053C4|
        INCBIN  baserom.gba_0x7053c4_0x7053c8.extracted
        INCBIN  build\endrom\endrom_007053C8_007053F8.bin
|unk_087053F8|
        INCBIN  baserom.gba_0x7053f8_0x705408.extracted
        INCBIN  build\endrom\endrom_00705408_00705418.bin
|unk_08705418|
        INCBIN  baserom.gba_0x705418_0x70542c.extracted
        INCBIN  build\endrom\endrom_0070542C_0070543C.bin
|unk_0870543C|
        INCBIN  baserom.gba_0x70543c_0x705440.extracted
        INCBIN  build\endrom\endrom_00705440_00705484.bin
|unk_08705484|
        INCBIN  baserom.gba_0x705484_0x7054ac.extracted
        INCBIN  build\endrom\endrom_007054AC_007054BC.bin
|unk_087054BC|
        INCBIN  baserom.gba_0x7054bc_0x7054c0.extracted
        INCBIN  build\endrom\endrom_007054C0_00705514.bin
|unk_08705514|
        INCBIN  baserom.gba_0x705514_0x705518.extracted
        INCBIN  build\endrom\endrom_00705518_00705568.bin
|unk_08705568|
        INCBIN  baserom.gba_0x705568_0x70557c.extracted
        INCBIN  build\endrom\endrom_0070557C_0070558C.bin
|unk_0870558C|
        INCBIN  baserom.gba_0x70558c_0x7055b4.extracted
        INCBIN  build\endrom\endrom_007055B4_007055C4.bin
|unk_087055C4|
        INCBIN  baserom.gba_0x7055c4_0x7055c8.extracted
        INCBIN  build\endrom\endrom_007055C8_007055D8.bin
|unk_087055D8|
        INCBIN  baserom.gba_0x7055d8_0x705614.extracted
        INCBIN  build\endrom\endrom_00705614_00705624.bin
|unk_08705624|
        INCBIN  baserom.gba_0x705624_0x70564c.extracted
        INCBIN  build\endrom\endrom_0070564C_0070565C.bin
|unk_0870565C|
        INCBIN  baserom.gba_0x70565c_0x705670.extracted
        INCBIN  build\endrom\endrom_00705670_00705680.bin
|unk_08705680|
        INCBIN  baserom.gba_0x705680_0x705684.extracted
        INCBIN  build\endrom\endrom_00705684_007057EC.bin
|unk_087057EC|
        INCBIN  baserom.gba_0x7057ec_0x7057f0.extracted
        INCBIN  build\endrom\endrom_007057F0_00705800.bin
|unk_08705800|
        INCBIN  baserom.gba_0x705800_0x705804.extracted
        INCBIN  build\endrom\endrom_00705804_00705838.bin
|unk_08705838|
        INCBIN  baserom.gba_0x705838_0x70584c.extracted
        INCBIN  build\endrom\endrom_0070584C_0070586C.bin
|unk_0870586C|
        INCBIN  baserom.gba_0x70586c_0x705870.extracted
        INCBIN  build\endrom\endrom_00705870_007058A8.bin
|unk_087058A8|
        INCBIN  baserom.gba_0x7058a8_0x7058ac.extracted
        INCBIN  build\endrom\endrom_007058AC_007058EC.bin
|unk_087058EC|
        INCBIN  baserom.gba_0x7058ec_0x7058fc.extracted
        INCBIN  build\endrom\endrom_007058FC_0070590C.bin
|unk_0870590C|
        INCBIN  baserom.gba_0x70590c_0x705920.extracted
        INCBIN  build\endrom\endrom_00705920_00705930.bin
|unk_08705930|
        INCBIN  baserom.gba_0x705930_0x705934.extracted
        INCBIN  build\endrom\endrom_00705934_00705944.bin
|unk_08705944|
        INCBIN  baserom.gba_0x705944_0x705958.extracted
        INCBIN  build\endrom\endrom_00705958_00705968.bin
|unk_08705968|
        INCBIN  baserom.gba_0x705968_0x70596c.extracted
        INCBIN  build\endrom\endrom_0070596C_0070597C.bin
|unk_0870597C|
        INCBIN  baserom.gba_0x70597c_0x7059a4.extracted
        INCBIN  build\endrom\endrom_007059A4_007059B4.bin
|unk_087059B4|
        INCBIN  baserom.gba_0x7059b4_0x7059dc.extracted
        INCBIN  build\endrom\endrom_007059DC_007059EC.bin
|unk_087059EC|
        INCBIN  baserom.gba_0x7059ec_0x705a00.extracted
        INCBIN  build\endrom\endrom_00705A00_00705A10.bin
|unk_08705A10|
        INCBIN  baserom.gba_0x705a10_0x705a24.extracted
        INCBIN  build\endrom\endrom_00705A24_00705A34.bin
|unk_08705A34|
        INCBIN  baserom.gba_0x705a34_0x705a38.extracted
        INCBIN  build\endrom\endrom_00705A38_00705BD8.bin
|unk_08705BD8|
        INCBIN  baserom.gba_0x705bd8_0x705bdc.extracted
        INCBIN  build\endrom\endrom_00705BDC_00705C0C.bin
|unk_08705C0C|
        INCBIN  baserom.gba_0x705c0c_0x705c40.extracted
        INCBIN  build\endrom\endrom_00705C40_00705C50.bin
|unk_08705C50|
        INCBIN  baserom.gba_0x705c50_0x705c54.extracted
        INCBIN  build\endrom\endrom_00705C54_00705C64.bin
|unk_08705C64|
        INCBIN  baserom.gba_0x705c64_0x705c90.extracted
        INCBIN  build\endrom\endrom_00705C90_00705CA0.bin
|unk_08705CA0|
        INCBIN  baserom.gba_0x705ca0_0x705ca4.extracted
        INCBIN  build\endrom\endrom_00705CA4_00705CE8.bin
|unk_08705CE8|
        INCBIN  baserom.gba_0x705ce8_0x705cf8.extracted
        INCBIN  build\endrom\endrom_00705CF8_00705D08.bin
|unk_08705D08|
        INCBIN  baserom.gba_0x705d08_0x705d0c.extracted
        INCBIN  build\endrom\endrom_00705D0C_00705D5C.bin
|unk_08705D5C|
        INCBIN  baserom.gba_0x705d5c_0x705d6c.extracted
        INCBIN  build\endrom\endrom_00705D6C_00705D7C.bin
|unk_08705D7C|
        INCBIN  baserom.gba_0x705d7c_0x705d90.extracted
        INCBIN  build\endrom\endrom_00705D90_00705DA0.bin
|unk_08705DA0|
        INCBIN  baserom.gba_0x705da0_0x705da4.extracted
        INCBIN  build\endrom\endrom_00705DA4_00705DB4.bin
|unk_08705DB4|
        INCBIN  baserom.gba_0x705db4_0x705dc8.extracted
        INCBIN  build\endrom\endrom_00705DC8_00705DD8.bin
|unk_08705DD8|
        INCBIN  baserom.gba_0x705dd8_0x705ddc.extracted
        INCBIN  build\endrom\endrom_00705DDC_00705DEC.bin
|unk_08705DEC|
        INCBIN  baserom.gba_0x705dec_0x705e14.extracted
        INCBIN  build\endrom\endrom_00705E14_00705E24.bin
|unk_08705E24|
        INCBIN  baserom.gba_0x705e24_0x705e4c.extracted
        INCBIN  build\endrom\endrom_00705E4C_00705E5C.bin
|unk_08705E5C|
        INCBIN  baserom.gba_0x705e5c_0x705e70.extracted
        INCBIN  build\endrom\endrom_00705E70_00705E80.bin
|unk_08705E80|
        INCBIN  baserom.gba_0x705e80_0x705e94.extracted
        INCBIN  build\endrom\endrom_00705E94_00705EA4.bin
|unk_08705EA4|
        INCBIN  baserom.gba_0x705ea4_0x705ea8.extracted
        INCBIN  build\endrom\endrom_00705EA8_00706048.bin
|unk_08706048|
        INCBIN  baserom.gba_0x706048_0x70604c.extracted
        INCBIN  build\endrom\endrom_0070604C_0070607C.bin
|unk_0870607C|
        INCBIN  baserom.gba_0x70607c_0x7060b0.extracted
        INCBIN  build\endrom\endrom_007060B0_007060C0.bin
|unk_087060C0|
        INCBIN  baserom.gba_0x7060c0_0x7060c4.extracted
        INCBIN  build\endrom\endrom_007060C4_007060D4.bin
|unk_087060D4|
        INCBIN  baserom.gba_0x7060d4_0x706100.extracted
        INCBIN  build\endrom\endrom_00706100_00706110.bin
|unk_08706110|
        INCBIN  baserom.gba_0x706110_0x706114.extracted
        INCBIN  build\endrom\endrom_00706114_00706150.bin
|unk_08706150|
        INCBIN  baserom.gba_0x706150_0x706154.extracted
        INCBIN  build\endrom\endrom_00706154_00706194.bin
|unk_08706194|
        INCBIN  baserom.gba_0x706194_0x7061a8.extracted
        INCBIN  build\endrom\endrom_007061A8_007061B8.bin
|unk_087061B8|
        INCBIN  baserom.gba_0x7061b8_0x7061cc.extracted
        INCBIN  build\endrom\endrom_007061CC_007061DC.bin
|unk_087061DC|
        INCBIN  baserom.gba_0x7061dc_0x7061f0.extracted
        INCBIN  build\endrom\endrom_007061F0_00706200.bin
|unk_08706200|
        INCBIN  baserom.gba_0x706200_0x706204.extracted
        INCBIN  build\endrom\endrom_00706204_00706214.bin
|unk_08706214|
        INCBIN  baserom.gba_0x706214_0x706228.extracted
        INCBIN  build\endrom\endrom_00706228_00706238.bin
|unk_08706238|
        INCBIN  baserom.gba_0x706238_0x70623c.extracted
        INCBIN  build\endrom\endrom_0070623C_0070624C.bin
|unk_0870624C|
        INCBIN  baserom.gba_0x70624c_0x706274.extracted
        INCBIN  build\endrom\endrom_00706274_00706284.bin
|unk_08706284|
        INCBIN  baserom.gba_0x706284_0x7062ac.extracted
        INCBIN  build\endrom\endrom_007062AC_007062BC.bin
|unk_087062BC|
        INCBIN  baserom.gba_0x7062bc_0x7062d0.extracted
        INCBIN  build\endrom\endrom_007062D0_007062E0.bin
|unk_087062E0|
        INCBIN  baserom.gba_0x7062e0_0x7062f4.extracted
        INCBIN  build\endrom\endrom_007062F4_00706304.bin
|unk_08706304|
        INCBIN  baserom.gba_0x706304_0x706308.extracted
        INCBIN  build\endrom\endrom_00706308_007064AC.bin
|unk_087064AC|
        INCBIN  baserom.gba_0x7064ac_0x7064b0.extracted
        INCBIN  build\endrom\endrom_007064B0_007064E0.bin
|unk_087064E0|
        INCBIN  baserom.gba_0x7064e0_0x706514.extracted
        INCBIN  build\endrom\endrom_00706514_00706524.bin
|unk_08706524|
        INCBIN  baserom.gba_0x706524_0x706528.extracted
        INCBIN  build\endrom\endrom_00706528_00706538.bin
|unk_08706538|
        INCBIN  baserom.gba_0x706538_0x706564.extracted
        INCBIN  build\endrom\endrom_00706564_00706574.bin
|unk_08706574|
        INCBIN  baserom.gba_0x706574_0x706578.extracted
        INCBIN  build\endrom\endrom_00706578_007065BC.bin
|unk_087065BC|
        INCBIN  baserom.gba_0x7065bc_0x7065cc.extracted
        INCBIN  build\endrom\endrom_007065CC_007065DC.bin
|unk_087065DC|
        INCBIN  baserom.gba_0x7065dc_0x7065e0.extracted
        INCBIN  build\endrom\endrom_007065E0_00706630.bin
|unk_08706630|
        INCBIN  baserom.gba_0x706630_0x706640.extracted
        INCBIN  build\endrom\endrom_00706640_00706650.bin
|unk_08706650|
        INCBIN  baserom.gba_0x706650_0x706664.extracted
        INCBIN  build\endrom\endrom_00706664_00706674.bin
|unk_08706674|
        INCBIN  baserom.gba_0x706674_0x706678.extracted
        INCBIN  build\endrom\endrom_00706678_00706688.bin
|unk_08706688|
        INCBIN  baserom.gba_0x706688_0x70669c.extracted
        INCBIN  build\endrom\endrom_0070669C_007066AC.bin
|unk_087066AC|
        INCBIN  baserom.gba_0x7066ac_0x7066b0.extracted
        INCBIN  build\endrom\endrom_007066B0_007066C0.bin
|unk_087066C0|
        INCBIN  baserom.gba_0x7066c0_0x7066e8.extracted
        INCBIN  build\endrom\endrom_007066E8_007066F8.bin
|unk_087066F8|
        INCBIN  baserom.gba_0x7066f8_0x706720.extracted
        INCBIN  build\endrom\endrom_00706720_00706730.bin
|unk_08706730|
        INCBIN  baserom.gba_0x706730_0x706744.extracted
        INCBIN  build\endrom\endrom_00706744_00706754.bin
|unk_08706754|
        INCBIN  baserom.gba_0x706754_0x706768.extracted
        INCBIN  build\endrom\endrom_00706768_00706778.bin
|unk_08706778|
        INCBIN  baserom.gba_0x706778_0x70677c.extracted
        INCBIN  build\endrom\endrom_0070677C_00706920.bin
|unk_08706920|
        INCBIN  baserom.gba_0x706920_0x706924.extracted
        INCBIN  build\endrom\endrom_00706924_00706954.bin
|unk_08706954|
        INCBIN  baserom.gba_0x706954_0x706988.extracted
        INCBIN  build\endrom\endrom_00706988_00706998.bin
|unk_08706998|
        INCBIN  baserom.gba_0x706998_0x70699c.extracted
        INCBIN  build\endrom\endrom_0070699C_007069AC.bin
|unk_087069AC|
        INCBIN  baserom.gba_0x7069ac_0x7069d8.extracted
        INCBIN  build\endrom\endrom_007069D8_007069E8.bin
|unk_087069E8|
        INCBIN  baserom.gba_0x7069e8_0x7069ec.extracted
        INCBIN  build\endrom\endrom_007069EC_00706A48.bin
        INCLUDE rawlabeled_706a48.s
        INCBIN  build\endrom\endrom_00706A4C_00706A8C.bin
        INCLUDE rawlabeled_706a8c.s
        INCBIN  build\endrom\endrom_00706AAC_00706ABC.bin
        INCLUDE rawlabeled_706abc.s
        INCBIN  build\endrom\endrom_00706AC0_00706AD0.bin
        INCLUDE rawlabeled_706ad0.s
        INCBIN  build\endrom\endrom_00706AD4_00706AE4.bin
        INCLUDE rawlabeled_706ae4.s
        INCBIN  build\endrom\endrom_00706AF8_00706B08.bin
        INCLUDE rawlabeled_706b08.s
        INCBIN  build\endrom\endrom_00706B30_00706B40.bin
        INCLUDE rawlabeled_706b40.s
        INCBIN  build\endrom\endrom_00706B54_00706B64.bin
        INCLUDE rawlabeled_706b64.s
        INCBIN  build\endrom\endrom_00706B68_00706B78.bin
        INCLUDE rawlabeled_706b78.s
        INCBIN  build\endrom\endrom_00706B7C_00706C90.bin
        INCLUDE rawlabeled_706c90.s
        INCBIN  build\endrom\endrom_00706C94_00706CEC.bin
        INCLUDE rawlabeled_706cec.s
        INCBIN  build\endrom\endrom_00706CF0_00706D30.bin
        INCLUDE rawlabeled_706d30.s
        INCBIN  build\endrom\endrom_00706D40_00706D50.bin
        INCLUDE rawlabeled_706d50.s
        INCBIN  build\endrom\endrom_00706DB4_00706DC4.bin
        INCLUDE rawlabeled_706dc4.s
        INCBIN  build\endrom\endrom_00706DD8_00706DE8.bin
        INCLUDE rawlabeled_706de8.s
        INCBIN  build\endrom\endrom_00706DFC_00706E0C.bin
        INCLUDE rawlabeled_706e0c.s
        INCBIN  build\endrom\endrom_00706E10_00706E94.bin
        INCLUDE rawlabeled_706e94.s
        INCBIN  build\endrom\endrom_00706EE8_00706F08.bin
        INCLUDE rawlabeled_706f08.s
        INCBIN  build\endrom\endrom_00706F0C_00706F2C.bin
|unk_08706F2C|
        INCBIN  baserom.gba_0x706f2c_0x706f3c.extracted
        INCBIN  build\endrom\endrom_00706F3C_00706F4C.bin
|unk_08706F4C|
        INCBIN  baserom.gba_0x706f4c_0x706f50.extracted
        INCBIN  build\endrom\endrom_00706F50_00706FCC.bin
        INCLUDE rawlabeled_706fcc.s
        INCBIN  build\endrom\endrom_00706FE0_00706FF0.bin
        INCLUDE rawlabeled_706ff0.s
        INCBIN  build\endrom\endrom_00706FF4_0070709C.bin
        INCLUDE rawlabeled_70709c.s
        INCBIN  build\endrom\endrom_007070A0_007070D0.bin
        INCLUDE rawlabeled_7070d0.s
        INCBIN  build\endrom\endrom_00707140_00707150.bin
        INCLUDE rawlabeled_707150.s
        INCBIN  build\endrom\endrom_00707154_00707164.bin
        INCLUDE rawlabeled_707164.s
        INCBIN  build\endrom\endrom_0070717C_0070718C.bin
        INCLUDE rawlabeled_70718c.s
        INCBIN  build\endrom\endrom_00707190_007071CC.bin
|unk_087071CC|
        INCBIN  baserom.gba_0x7071cc_0x7071d0.extracted
        INCBIN  build\endrom\endrom_007071D0_00707210.bin
|unk_08707210|
        INCBIN  baserom.gba_0x707210_0x707230.extracted
        INCBIN  build\endrom\endrom_00707230_00707240.bin
|unk_08707240|
        INCBIN  baserom.gba_0x707240_0x707244.extracted
        INCBIN  build\endrom\endrom_00707244_00707254.bin
|unk_08707254|
        INCBIN  baserom.gba_0x707254_0x707258.extracted
        INCBIN  build\endrom\endrom_00707258_00707268.bin
|unk_08707268|
        INCBIN  baserom.gba_0x707268_0x70727c.extracted
        INCBIN  build\endrom\endrom_0070727C_0070728C.bin
|unk_0870728C|
        INCBIN  baserom.gba_0x70728c_0x7072b4.extracted
        INCBIN  build\endrom\endrom_007072B4_007072C4.bin
|unk_087072C4|
        INCBIN  baserom.gba_0x7072c4_0x7072d8.extracted
        INCBIN  build\endrom\endrom_007072D8_007072E8.bin
|unk_087072E8|
        INCBIN  baserom.gba_0x7072e8_0x7072ec.extracted
        INCBIN  build\endrom\endrom_007072EC_007072FC.bin
|unk_087072FC|
        INCBIN  baserom.gba_0x7072fc_0x707300.extracted
        INCBIN  build\endrom\endrom_00707300_00707414.bin
|unk_08707414|
        INCBIN  baserom.gba_0x707414_0x707418.extracted
        INCBIN  build\endrom\endrom_00707418_00707460.bin
|unk_08707460|
        INCBIN  baserom.gba_0x707460_0x707464.extracted
        INCBIN  build\endrom\endrom_00707464_007074D4.bin
|unk_087074D4|
        INCBIN  baserom.gba_0x7074d4_0x7074d8.extracted
        INCBIN  build\endrom\endrom_007074D8_00707570.bin
|unk_08707570|
        INCBIN  baserom.gba_0x707570_0x707590.extracted
        INCBIN  build\endrom\endrom_00707590_007075A0.bin
|unk_087075A0|
        INCBIN  baserom.gba_0x7075a0_0x7075d0.extracted
        INCBIN  build\endrom\endrom_007075D0_007075F0.bin
|unk_087075F0|
        INCBIN  baserom.gba_0x7075f0_0x7075f4.extracted
        INCBIN  build\endrom\endrom_007075F4_00707628.bin
|unk_08707628|
        INCBIN  baserom.gba_0x707628_0x707644.extracted
        INCBIN  build\endrom\endrom_00707644_007076E0.bin
|unk_087076E0|
        INCBIN  baserom.gba_0x7076e0_0x7076e4.extracted
        INCBIN  build\endrom\endrom_007076E4_00707754.bin
|unk_08707754|
        INCBIN  baserom.gba_0x707754_0x707768.extracted
        INCBIN  build\endrom\endrom_00707768_00707778.bin
|unk_08707778|
        INCBIN  baserom.gba_0x707778_0x70777c.extracted
        INCBIN  build\endrom\endrom_0070777C_0070778C.bin
|unk_0870778C|
        INCBIN  baserom.gba_0x70778c_0x7077a0.extracted
        INCBIN  build\endrom\endrom_007077A0_007077B0.bin
|unk_087077B0|
        INCBIN  baserom.gba_0x7077b0_0x7077d8.extracted
        INCBIN  build\endrom\endrom_007077D8_007077E8.bin
|unk_087077E8|
        INCBIN  baserom.gba_0x7077e8_0x7077fc.extracted
        INCBIN  build\endrom\endrom_007077FC_0070780C.bin
|unk_0870780C|
        INCBIN  baserom.gba_0x70780c_0x707820.extracted
        INCBIN  build\endrom\endrom_00707820_00707830.bin
|unk_08707830|
        INCBIN  baserom.gba_0x707830_0x707834.extracted
        INCBIN  build\endrom\endrom_00707834_00707980.bin
|unk_08707980|
        INCBIN  baserom.gba_0x707980_0x707994.extracted
        INCBIN  build\endrom\endrom_00707994_007079A4.bin
|unk_087079A4|
        INCBIN  baserom.gba_0x7079a4_0x7079a8.extracted
        INCBIN  build\endrom\endrom_007079A8_007079B8.bin
|unk_087079B8|
        INCBIN  baserom.gba_0x7079b8_0x7079cc.extracted
        INCBIN  build\endrom\endrom_007079CC_007079DC.bin
|unk_087079DC|
        INCBIN  baserom.gba_0x7079dc_0x707a04.extracted
        INCBIN  build\endrom\endrom_00707A04_00707A14.bin
|unk_08707A14|
        INCBIN  baserom.gba_0x707a14_0x707a28.extracted
        INCBIN  build\endrom\endrom_00707A28_00707A38.bin
|unk_08707A38|
        INCBIN  baserom.gba_0x707a38_0x707a4c.extracted
        INCBIN  build\endrom\endrom_00707A4C_00707A5C.bin
|unk_08707A5C|
        INCBIN  baserom.gba_0x707a5c_0x707a60.extracted
        INCBIN  build\endrom\endrom_00707A60_00707B38.bin
|unk_08707B38|
        INCBIN  baserom.gba_0x707b38_0x707b48.extracted
        INCBIN  build\endrom\endrom_00707B48_00707B58.bin
|unk_08707B58|
        INCBIN  baserom.gba_0x707b58_0x707b6c.extracted
        INCBIN  build\endrom\endrom_00707B6C_00707B7C.bin
|unk_08707B7C|
        INCBIN  baserom.gba_0x707b7c_0x707b80.extracted
        INCBIN  build\endrom\endrom_00707B80_00707B98.bin
|unk_08707B98|
        INCBIN  baserom.gba_0x707b98_0x707ba8.extracted
        INCBIN  build\endrom\endrom_00707BA8_00707BB8.bin
|unk_08707BB8|
        INCBIN  baserom.gba_0x707bb8_0x707bbc.extracted
        INCBIN  build\endrom\endrom_00707BBC_00707BE4.bin
|unk_08707BE4|
        INCBIN  baserom.gba_0x707be4_0x707be8.extracted
        INCBIN  build\endrom\endrom_00707BE8_00707C68.bin
|unk_08707C68|
        INCBIN  baserom.gba_0x707c68_0x707c6c.extracted
        INCBIN  build\endrom\endrom_00707C6C_00707CAC.bin
|unk_08707CAC|
        INCBIN  baserom.gba_0x707cac_0x707cc0.extracted
        INCBIN  build\endrom\endrom_00707CC0_00707CD0.bin
|unk_08707CD0|
        INCBIN  baserom.gba_0x707cd0_0x707ce4.extracted
        INCBIN  build\endrom\endrom_00707CE4_00707CF4.bin
|unk_08707CF4|
        INCBIN  baserom.gba_0x707cf4_0x707d08.extracted
        INCBIN  build\endrom\endrom_00707D08_00707D18.bin
|unk_08707D18|
        INCBIN  baserom.gba_0x707d18_0x707d1c.extracted
        INCBIN  build\endrom\endrom_00707D1C_00707D2C.bin
|unk_08707D2C|
        INCBIN  baserom.gba_0x707d2c_0x707d40.extracted
        INCBIN  build\endrom\endrom_00707D40_00707D50.bin
|unk_08707D50|
        INCBIN  baserom.gba_0x707d50_0x707d54.extracted
        INCBIN  build\endrom\endrom_00707D54_00707D64.bin
|unk_08707D64|
        INCBIN  baserom.gba_0x707d64_0x707d8c.extracted
        INCBIN  build\endrom\endrom_00707D8C_00707D9C.bin
|unk_08707D9C|
        INCBIN  baserom.gba_0x707d9c_0x707dc4.extracted
        INCBIN  build\endrom\endrom_00707DC4_00707DD4.bin
|unk_08707DD4|
        INCBIN  baserom.gba_0x707dd4_0x707de8.extracted
        INCBIN  build\endrom\endrom_00707DE8_00707DF8.bin
|unk_08707DF8|
        INCBIN  baserom.gba_0x707df8_0x707e0c.extracted
        INCBIN  build\endrom\endrom_00707E0C_00707E1C.bin
|unk_08707E1C|
        INCBIN  baserom.gba_0x707e1c_0x707e20.extracted
        INCBIN  build\endrom\endrom_00707E20_00707FC4.bin
|unk_08707FC4|
        INCBIN  baserom.gba_0x707fc4_0x707fc8.extracted
        INCBIN  build\endrom\endrom_00707FC8_00707FF8.bin
|unk_08707FF8|
        INCBIN  baserom.gba_0x707ff8_0x70802c.extracted
        INCBIN  build\endrom\endrom_0070802C_0070803C.bin
|unk_0870803C|
        INCBIN  baserom.gba_0x70803c_0x708040.extracted
        INCBIN  build\endrom\endrom_00708040_00708050.bin
|unk_08708050|
        INCBIN  baserom.gba_0x708050_0x70807c.extracted
        INCBIN  build\endrom\endrom_0070807C_0070808C.bin
|unk_0870808C|
        INCBIN  baserom.gba_0x70808c_0x708090.extracted
        INCBIN  build\endrom\endrom_00708090_007080AC.bin
|unk_087080AC|
        INCBIN  baserom.gba_0x7080ac_0x7080bc.extracted
        INCBIN  build\endrom\endrom_007080BC_007080CC.bin
|unk_087080CC|
        INCBIN  baserom.gba_0x7080cc_0x7080d0.extracted
        INCBIN  build\endrom\endrom_007080D0_00708120.bin
|unk_08708120|
        INCBIN  baserom.gba_0x708120_0x708130.extracted
        INCBIN  build\endrom\endrom_00708130_00708140.bin
|unk_08708140|
        INCBIN  baserom.gba_0x708140_0x708144.extracted
        INCBIN  build\endrom\endrom_00708144_00708184.bin
|unk_08708184|
        INCBIN  baserom.gba_0x708184_0x708194.extracted
        INCBIN  build\endrom\endrom_00708194_007081A4.bin
|unk_087081A4|
        INCBIN  baserom.gba_0x7081a4_0x7081b8.extracted
        INCBIN  build\endrom\endrom_007081B8_007081C8.bin
|unk_087081C8|
        INCBIN  baserom.gba_0x7081c8_0x7081cc.extracted
        INCBIN  build\endrom\endrom_007081CC_007081DC.bin
|unk_087081DC|
        INCBIN  baserom.gba_0x7081dc_0x7081f0.extracted
        INCBIN  build\endrom\endrom_007081F0_00708200.bin
|unk_08708200|
        INCBIN  baserom.gba_0x708200_0x708204.extracted
        INCBIN  build\endrom\endrom_00708204_00708214.bin
|unk_08708214|
        INCBIN  baserom.gba_0x708214_0x70823c.extracted
        INCBIN  build\endrom\endrom_0070823C_0070824C.bin
|unk_0870824C|
        INCBIN  baserom.gba_0x70824c_0x708274.extracted
        INCBIN  build\endrom\endrom_00708274_00708284.bin
|unk_08708284|
        INCBIN  baserom.gba_0x708284_0x708298.extracted
        INCBIN  build\endrom\endrom_00708298_007082A8.bin
|unk_087082A8|
        INCBIN  baserom.gba_0x7082a8_0x7082bc.extracted
        INCBIN  build\endrom\endrom_007082BC_007082CC.bin
|unk_087082CC|
        INCBIN  baserom.gba_0x7082cc_0x7082d0.extracted
        INCBIN  build\endrom\endrom_007082D0_00708474.bin
|unk_08708474|
        INCBIN  baserom.gba_0x708474_0x708478.extracted
        INCBIN  build\endrom\endrom_00708478_007084A8.bin
|unk_087084A8|
        INCBIN  baserom.gba_0x7084a8_0x7084dc.extracted
        INCBIN  build\endrom\endrom_007084DC_007084EC.bin
|unk_087084EC|
        INCBIN  baserom.gba_0x7084ec_0x7084f0.extracted
        INCBIN  build\endrom\endrom_007084F0_00708500.bin
|unk_08708500|
        INCBIN  baserom.gba_0x708500_0x70852c.extracted
        INCBIN  build\endrom\endrom_0070852C_0070853C.bin
|unk_0870853C|
        INCBIN  baserom.gba_0x70853c_0x708540.extracted
        INCBIN  build\endrom\endrom_00708540_0070857C.bin
|unk_0870857C|
        INCBIN  baserom.gba_0x70857c_0x708580.extracted
        INCBIN  build\endrom\endrom_00708580_007085D0.bin
|unk_087085D0|
        INCBIN  baserom.gba_0x7085d0_0x7085e4.extracted
        INCBIN  build\endrom\endrom_007085E4_007085F4.bin
|unk_087085F4|
        INCBIN  baserom.gba_0x7085f4_0x70861c.extracted
        INCBIN  build\endrom\endrom_0070861C_0070862C.bin
|unk_0870862C|
        INCBIN  baserom.gba_0x70862c_0x708650.extracted
        INCBIN  build\endrom\endrom_00708650_00708660.bin
|unk_08708660|
        INCBIN  baserom.gba_0x708660_0x708674.extracted
        INCBIN  build\endrom\endrom_00708674_00708684.bin
|unk_08708684|
        INCBIN  baserom.gba_0x708684_0x708688.extracted
        INCBIN  build\endrom\endrom_00708688_00708698.bin
|unk_08708698|
        INCBIN  baserom.gba_0x708698_0x70869c.extracted
        INCBIN  build\endrom\endrom_0070869C_007086F8.bin
|unk_087086F8|
        INCBIN  baserom.gba_0x7086f8_0x708710.extracted
        INCBIN  build\endrom\endrom_00708710_0070877C.bin
|unk_0870877C|
        INCBIN  baserom.gba_0x70877c_0x708780.extracted
        INCBIN  build\endrom\endrom_00708780_007087CC.bin
|unk_087087CC|
        INCBIN  baserom.gba_0x7087cc_0x7087f8.extracted
        INCBIN  build\endrom\endrom_007087F8_00708808.bin
|unk_08708808|
        INCBIN  baserom.gba_0x708808_0x708834.extracted
        INCBIN  build\endrom\endrom_00708834_00708844.bin
|unk_08708844|
        INCBIN  baserom.gba_0x708844_0x708848.extracted
        INCBIN  build\endrom\endrom_00708848_00708858.bin
|unk_08708858|
        INCBIN  baserom.gba_0x708858_0x70885c.extracted
        INCBIN  build\endrom\endrom_0070885C_00708894.bin
|unk_08708894|
        INCBIN  baserom.gba_0x708894_0x7088ac.extracted
        INCBIN  build\endrom\endrom_007088AC_007088BC.bin
|unk_087088BC|
        INCBIN  baserom.gba_0x7088bc_0x7088e8.extracted
        INCBIN  build\endrom\endrom_007088E8_00708968.bin
|unk_08708968|
        INCBIN  baserom.gba_0x708968_0x70896c.extracted
        INCBIN  build\endrom\endrom_0070896C_0070897C.bin
|unk_0870897C|
        INCBIN  baserom.gba_0x70897c_0x708980.extracted
        INCBIN  build\endrom\endrom_00708980_007089D8.bin
|unk_087089D8|
        INCBIN  baserom.gba_0x7089d8_0x7089e0.extracted
        INCBIN  build\endrom\endrom_007089E0_00708A4C.bin
|unk_08708A4C|
        INCBIN  baserom.gba_0x708a4c_0x708a50.extracted
        INCBIN  build\endrom\endrom_00708A50_00708A90.bin
|unk_08708A90|
        INCBIN  baserom.gba_0x708a90_0x708ab0.extracted
        INCBIN  build\endrom\endrom_00708AB0_00708AC0.bin
|unk_08708AC0|
        INCBIN  baserom.gba_0x708ac0_0x708ac4.extracted
        INCBIN  build\endrom\endrom_00708AC4_00708AD4.bin
|unk_08708AD4|
        INCBIN  baserom.gba_0x708ad4_0x708ad8.extracted
        INCBIN  build\endrom\endrom_00708AD8_00708AE8.bin
|unk_08708AE8|
        INCBIN  baserom.gba_0x708ae8_0x708afc.extracted
        INCBIN  build\endrom\endrom_00708AFC_00708B0C.bin
|unk_08708B0C|
        INCBIN  baserom.gba_0x708b0c_0x708b34.extracted
        INCBIN  build\endrom\endrom_00708B34_00708B44.bin
|unk_08708B44|
        INCBIN  baserom.gba_0x708b44_0x708b58.extracted
        INCBIN  build\endrom\endrom_00708B58_00708B68.bin
|unk_08708B68|
        INCBIN  baserom.gba_0x708b68_0x708b6c.extracted
        INCBIN  build\endrom\endrom_00708B6C_00708B7C.bin
|unk_08708B7C|
        INCBIN  baserom.gba_0x708b7c_0x708b80.extracted
        INCBIN  build\endrom\endrom_00708B80_00708CA4.bin
|unk_08708CA4|
        INCBIN  baserom.gba_0x708ca4_0x708ca8.extracted
        INCBIN  build\endrom\endrom_00708CA8_00708CD8.bin
|unk_08708CD8|
        INCBIN  baserom.gba_0x708cd8_0x708d0c.extracted
        INCBIN  build\endrom\endrom_00708D0C_00708D1C.bin
|unk_08708D1C|
        INCBIN  baserom.gba_0x708d1c_0x708d20.extracted
        INCBIN  build\endrom\endrom_00708D20_00708D30.bin
|unk_08708D30|
        INCBIN  baserom.gba_0x708d30_0x708d5c.extracted
        INCBIN  build\endrom\endrom_00708D5C_00708D6C.bin
|unk_08708D6C|
        INCBIN  baserom.gba_0x708d6c_0x708d70.extracted
        INCBIN  build\endrom\endrom_00708D70_00708DAC.bin
|unk_08708DAC|
        INCBIN  baserom.gba_0x708dac_0x708db0.extracted
        INCBIN  build\endrom\endrom_00708DB0_00708DF0.bin
|unk_08708DF0|
        INCBIN  baserom.gba_0x708df0_0x708e10.extracted
        INCBIN  build\endrom\endrom_00708E10_00708E20.bin
|unk_08708E20|
        INCBIN  baserom.gba_0x708e20_0x708e24.extracted
        INCBIN  build\endrom\endrom_00708E24_00708E34.bin
|unk_08708E34|
        INCBIN  baserom.gba_0x708e34_0x708e38.extracted
        INCBIN  build\endrom\endrom_00708E38_00708E48.bin
|unk_08708E48|
        INCBIN  baserom.gba_0x708e48_0x708e5c.extracted
        INCBIN  build\endrom\endrom_00708E5C_00708E6C.bin
|unk_08708E6C|
        INCBIN  baserom.gba_0x708e6c_0x708e94.extracted
        INCBIN  build\endrom\endrom_00708E94_00708EA4.bin
|unk_08708EA4|
        INCBIN  baserom.gba_0x708ea4_0x708eb8.extracted
        INCBIN  build\endrom\endrom_00708EB8_00708EC8.bin
|unk_08708EC8|
        INCBIN  baserom.gba_0x708ec8_0x708ecc.extracted
        INCBIN  build\endrom\endrom_00708ECC_00708EDC.bin
|unk_08708EDC|
        INCBIN  baserom.gba_0x708edc_0x708ee0.extracted
        INCBIN  build\endrom\endrom_00708EE0_00708FF4.bin
|unk_08708FF4|
        INCBIN  baserom.gba_0x708ff4_0x708ff8.extracted
        INCBIN  build\endrom\endrom_00708FF8_00709028.bin
|unk_08709028|
        INCBIN  baserom.gba_0x709028_0x70905c.extracted
        INCBIN  build\endrom\endrom_0070905C_0070906C.bin
|unk_0870906C|
        INCBIN  baserom.gba_0x70906c_0x709070.extracted
        INCBIN  build\endrom\endrom_00709070_00709080.bin
|unk_08709080|
        INCBIN  baserom.gba_0x709080_0x7090ac.extracted
        INCBIN  build\endrom\endrom_007090AC_007090BC.bin
|unk_087090BC|
        INCBIN  baserom.gba_0x7090bc_0x7090c0.extracted
        INCBIN  build\endrom\endrom_007090C0_007090FC.bin
|unk_087090FC|
        INCBIN  baserom.gba_0x7090fc_0x709120.extracted
        INCBIN  build\endrom\endrom_00709120_00709130.bin
|unk_08709130|
        INCBIN  baserom.gba_0x709130_0x709154.extracted
        INCBIN  build\endrom\endrom_00709154_00709164.bin
|unk_08709164|
        INCBIN  baserom.gba_0x709164_0x709168.extracted
        INCBIN  build\endrom\endrom_00709168_00709178.bin
|unk_08709178|
        INCBIN  baserom.gba_0x709178_0x70917c.extracted
        INCBIN  build\endrom\endrom_0070917C_0070918C.bin
|unk_0870918C|
        INCBIN  baserom.gba_0x70918c_0x7091a0.extracted
        INCBIN  build\endrom\endrom_007091A0_007091B0.bin
|unk_087091B0|
        INCBIN  baserom.gba_0x7091b0_0x7091d8.extracted
        INCBIN  build\endrom\endrom_007091D8_007091E8.bin
|unk_087091E8|
        INCBIN  baserom.gba_0x7091e8_0x7091fc.extracted
        INCBIN  build\endrom\endrom_007091FC_0070920C.bin
|unk_0870920C|
        INCBIN  baserom.gba_0x70920c_0x709210.extracted
        INCBIN  build\endrom\endrom_00709210_00709220.bin
|unk_08709220|
        INCBIN  baserom.gba_0x709220_0x709224.extracted
        INCBIN  build\endrom\endrom_00709224_0070933C.bin
|unk_0870933C|
        INCBIN  baserom.gba_0x70933c_0x709340.extracted
        INCBIN  build\endrom\endrom_00709340_00709370.bin
|unk_08709370|
        INCBIN  baserom.gba_0x709370_0x7093a4.extracted
        INCBIN  build\endrom\endrom_007093A4_007093B4.bin
|unk_087093B4|
        INCBIN  baserom.gba_0x7093b4_0x7093b8.extracted
        INCBIN  build\endrom\endrom_007093B8_007093C8.bin
|unk_087093C8|
        INCBIN  baserom.gba_0x7093c8_0x7093f4.extracted
        INCBIN  build\endrom\endrom_007093F4_00709404.bin
|unk_08709404|
        INCBIN  baserom.gba_0x709404_0x709408.extracted
        INCBIN  build\endrom\endrom_00709408_00709484.bin
|unk_08709484|
        INCBIN  baserom.gba_0x709484_0x709488.extracted
        INCBIN  build\endrom\endrom_00709488_007094C8.bin
|unk_087094C8|
        INCBIN  baserom.gba_0x7094c8_0x7094e8.extracted
        INCBIN  build\endrom\endrom_007094E8_007094F8.bin
|unk_087094F8|
        INCBIN  baserom.gba_0x7094f8_0x7094fc.extracted
        INCBIN  build\endrom\endrom_007094FC_0070950C.bin
|unk_0870950C|
        INCBIN  baserom.gba_0x70950c_0x709510.extracted
        INCBIN  build\endrom\endrom_00709510_00709520.bin
|unk_08709520|
        INCBIN  baserom.gba_0x709520_0x709534.extracted
        INCBIN  build\endrom\endrom_00709534_00709544.bin
|unk_08709544|
        INCBIN  baserom.gba_0x709544_0x70956c.extracted
        INCBIN  build\endrom\endrom_0070956C_0070957C.bin
|unk_0870957C|
        INCBIN  baserom.gba_0x70957c_0x709590.extracted
        INCBIN  build\endrom\endrom_00709590_007095A0.bin
|unk_087095A0|
        INCBIN  baserom.gba_0x7095a0_0x7095a4.extracted
        INCBIN  build\endrom\endrom_007095A4_007095B4.bin
|unk_087095B4|
        INCBIN  baserom.gba_0x7095b4_0x7095b8.extracted
        INCBIN  build\endrom\endrom_007095B8_007096CC.bin
|unk_087096CC|
        INCBIN  baserom.gba_0x7096cc_0x7096d0.extracted
        INCBIN  build\endrom\endrom_007096D0_00709700.bin
|unk_08709700|
        INCBIN  baserom.gba_0x709700_0x709734.extracted
        INCBIN  build\endrom\endrom_00709734_00709744.bin
|unk_08709744|
        INCBIN  baserom.gba_0x709744_0x709748.extracted
        INCBIN  build\endrom\endrom_00709748_00709758.bin
|unk_08709758|
        INCBIN  baserom.gba_0x709758_0x709784.extracted
        INCBIN  build\endrom\endrom_00709784_00709794.bin
|unk_08709794|
        INCBIN  baserom.gba_0x709794_0x709798.extracted
        INCBIN  build\endrom\endrom_00709798_007097E4.bin
|unk_087097E4|
        INCBIN  baserom.gba_0x7097e4_0x7097e8.extracted
        INCBIN  build\endrom\endrom_007097E8_00709828.bin
|unk_08709828|
        INCBIN  baserom.gba_0x709828_0x709838.extracted
        INCBIN  build\endrom\endrom_00709838_00709848.bin
|unk_08709848|
        INCBIN  baserom.gba_0x709848_0x709858.extracted
        INCBIN  build\endrom\endrom_00709858_00709868.bin
|unk_08709868|
        INCBIN  baserom.gba_0x709868_0x7098f4.extracted
        INCBIN  build\endrom\endrom_007098F4_00709904.bin
|unk_08709904|
        INCBIN  baserom.gba_0x709904_0x70997c.extracted
        INCBIN  build\endrom\endrom_0070997C_0070998C.bin
|unk_0870998C|
        INCBIN  baserom.gba_0x70998c_0x709990.extracted
        INCBIN  build\endrom\endrom_00709990_007099EC.bin
|unk_087099EC|
        INCBIN  baserom.gba_0x7099ec_0x709a40.extracted
        INCBIN  build\endrom\endrom_00709A40_00709A70.bin
|unk_08709A70|
        INCBIN  baserom.gba_0x709a70_0x709a74.extracted
        INCBIN  build\endrom\endrom_00709A74_00709A98.bin
|unk_08709A98|
        INCBIN  baserom.gba_0x709a98_0x709aa8.extracted
        INCBIN  build\endrom\endrom_00709AA8_00709AB8.bin
|unk_08709AB8|
        INCBIN  baserom.gba_0x709ab8_0x709abc.extracted
        INCBIN  build\endrom\endrom_00709ABC_00709B38.bin
|unk_08709B38|
        INCBIN  baserom.gba_0x709b38_0x709b50.extracted
        INCBIN  build\endrom\endrom_00709B50_00709B60.bin
|unk_08709B60|
        INCBIN  baserom.gba_0x709b60_0x709b64.extracted
        INCBIN  build\endrom\endrom_00709B64_00709C40.bin
|unk_08709C40|
        INCBIN  baserom.gba_0x709c40_0x709c90.extracted
        INCBIN  build\endrom\endrom_00709C90_00709CE4.bin
|unk_08709CE4|
        INCBIN  baserom.gba_0x709ce4_0x709ce8.extracted
        INCBIN  build\endrom\endrom_00709CE8_00709D18.bin
|unk_08709D18|
        INCBIN  baserom.gba_0x709d18_0x709d88.extracted
        INCBIN  build\endrom\endrom_00709D88_00709D98.bin
|unk_08709D98|
        INCBIN  baserom.gba_0x709d98_0x709d9c.extracted
        INCBIN  build\endrom\endrom_00709D9C_00709DAC.bin
|unk_08709DAC|
        INCBIN  baserom.gba_0x709dac_0x709db0.extracted
        INCBIN  build\endrom\endrom_00709DB0_00709DC0.bin
|unk_08709DC0|
        INCBIN  baserom.gba_0x709dc0_0x709dc4.extracted
        INCBIN  build\endrom\endrom_00709DC4_00709E00.bin
|unk_08709E00|
        INCBIN  baserom.gba_0x709e00_0x709e04.extracted
        INCBIN  build\endrom\endrom_00709E04_00709E44.bin
|unk_08709E44|
        INCBIN  baserom.gba_0x709e44_0x709e54.extracted
        INCBIN  build\endrom\endrom_00709E54_00709E64.bin
|unk_08709E64|
        INCBIN  baserom.gba_0x709e64_0x709e74.extracted
        INCBIN  build\endrom\endrom_00709E74_00709E84.bin
|unk_08709E84|
        INCBIN  baserom.gba_0x709e84_0x709f10.extracted
        INCBIN  build\endrom\endrom_00709F10_00709F20.bin
|unk_08709F20|
        INCBIN  baserom.gba_0x709f20_0x709f98.extracted
        INCBIN  build\endrom\endrom_00709F98_00709FA8.bin
|unk_08709FA8|
        INCBIN  baserom.gba_0x709fa8_0x709fac.extracted
        INCBIN  build\endrom\endrom_00709FAC_0070A008.bin
|unk_0870A008|
        INCBIN  baserom.gba_0x70a008_0x70a05c.extracted
        INCBIN  build\endrom\endrom_0070A05C_0070A08C.bin
|unk_0870A08C|
        INCBIN  baserom.gba_0x70a08c_0x70a090.extracted
        INCBIN  build\endrom\endrom_0070A090_0070A0B4.bin
|unk_0870A0B4|
        INCBIN  baserom.gba_0x70a0b4_0x70a0c4.extracted
        INCBIN  build\endrom\endrom_0070A0C4_0070A0D4.bin
|unk_0870A0D4|
        INCBIN  baserom.gba_0x70a0d4_0x70a0d8.extracted
        INCBIN  build\endrom\endrom_0070A0D8_0070A154.bin
|unk_0870A154|
        INCBIN  baserom.gba_0x70a154_0x70a16c.extracted
        INCBIN  build\endrom\endrom_0070A16C_0070A17C.bin
|unk_0870A17C|
        INCBIN  baserom.gba_0x70a17c_0x70a180.extracted
        INCBIN  build\endrom\endrom_0070A180_0070A250.bin
|unk_0870A250|
        INCBIN  baserom.gba_0x70a250_0x70a290.extracted
        INCBIN  build\endrom\endrom_0070A290_0070A2E4.bin
|unk_0870A2E4|
        INCBIN  baserom.gba_0x70a2e4_0x70a2e8.extracted
        INCBIN  build\endrom\endrom_0070A2E8_0070A338.bin
|unk_0870A338|
        INCBIN  baserom.gba_0x70a338_0x70a364.extracted
        INCBIN  build\endrom\endrom_0070A364_0070A374.bin
|unk_0870A374|
        INCBIN  baserom.gba_0x70a374_0x70a378.extracted
        INCBIN  build\endrom\endrom_0070A378_0070A3B0.bin
|unk_0870A3B0|
        INCBIN  baserom.gba_0x70a3b0_0x70a3dc.extracted
        INCBIN  build\endrom\endrom_0070A3DC_0070A3EC.bin
|unk_0870A3EC|
        INCBIN  baserom.gba_0x70a3ec_0x70a3f0.extracted
        INCBIN  build\endrom\endrom_0070A3F0_0070A448.bin
|unk_0870A448|
        INCBIN  baserom.gba_0x70a448_0x70a44c.extracted
        INCBIN  build\endrom\endrom_0070A44C_0070A4A8.bin
|unk_0870A4A8|
        INCBIN  baserom.gba_0x70a4a8_0x70a4cc.extracted
        INCBIN  build\endrom\endrom_0070A4CC_0070A4DC.bin
|unk_0870A4DC|
        INCBIN  baserom.gba_0x70a4dc_0x70a54c.extracted
        INCBIN  build\endrom\endrom_0070A54C_0070A55C.bin
|unk_0870A55C|
        INCBIN  baserom.gba_0x70a55c_0x70a570.extracted
        INCBIN  build\endrom\endrom_0070A570_0070A580.bin
|unk_0870A580|
        INCBIN  baserom.gba_0x70a580_0x70a584.extracted
        INCBIN  build\endrom\endrom_0070A584_0070A5B0.bin
|unk_0870A5B0|
        INCBIN  baserom.gba_0x70a5b0_0x70a5b4.extracted
        INCBIN  build\endrom\endrom_0070A5B4_0070A5C4.bin
|unk_0870A5C4|
        INCBIN  baserom.gba_0x70a5c4_0x70a5c8.extracted
        INCBIN  build\endrom\endrom_0070A5C8_0070A5F4.bin
|unk_0870A5F4|
        INCBIN  baserom.gba_0x70a5f4_0x70a604.extracted
        INCBIN  build\endrom\endrom_0070A604_0070A614.bin
|unk_0870A614|
        INCBIN  baserom.gba_0x70a614_0x70a624.extracted
        INCBIN  build\endrom\endrom_0070A624_0070A634.bin
|unk_0870A634|
        INCBIN  baserom.gba_0x70a634_0x70a6c0.extracted
        INCBIN  build\endrom\endrom_0070A6C0_0070A6D0.bin
|unk_0870A6D0|
        INCBIN  baserom.gba_0x70a6d0_0x70a748.extracted
        INCBIN  build\endrom\endrom_0070A748_0070A758.bin
|unk_0870A758|
        INCBIN  baserom.gba_0x70a758_0x70a75c.extracted
        INCBIN  build\endrom\endrom_0070A75C_0070A7B8.bin
|unk_0870A7B8|
        INCBIN  baserom.gba_0x70a7b8_0x70a80c.extracted
        INCBIN  build\endrom\endrom_0070A80C_0070A83C.bin
|unk_0870A83C|
        INCBIN  baserom.gba_0x70a83c_0x70a840.extracted
        INCBIN  build\endrom\endrom_0070A840_0070A884.bin
|unk_0870A884|
        INCBIN  baserom.gba_0x70a884_0x70a894.extracted
        INCBIN  build\endrom\endrom_0070A894_0070A8A4.bin
|unk_0870A8A4|
        INCBIN  baserom.gba_0x70a8a4_0x70a8a8.extracted
        INCBIN  build\endrom\endrom_0070A8A8_0070A924.bin
|unk_0870A924|
        INCBIN  baserom.gba_0x70a924_0x70a93c.extracted
        INCBIN  build\endrom\endrom_0070A93C_0070A94C.bin
|unk_0870A94C|
        INCBIN  baserom.gba_0x70a94c_0x70a950.extracted
        INCBIN  build\endrom\endrom_0070A950_0070AA30.bin
|unk_0870AA30|
        INCBIN  baserom.gba_0x70aa30_0x70aa80.extracted
        INCBIN  build\endrom\endrom_0070AA80_0070AAD4.bin
|unk_0870AAD4|
        INCBIN  baserom.gba_0x70aad4_0x70aad8.extracted
        INCBIN  build\endrom\endrom_0070AAD8_0070AB28.bin
|unk_0870AB28|
        INCBIN  baserom.gba_0x70ab28_0x70ab54.extracted
        INCBIN  build\endrom\endrom_0070AB54_0070AB64.bin
|unk_0870AB64|
        INCBIN  baserom.gba_0x70ab64_0x70ab68.extracted
        INCBIN  build\endrom\endrom_0070AB68_0070ABA0.bin
|unk_0870ABA0|
        INCBIN  baserom.gba_0x70aba0_0x70abcc.extracted
        INCBIN  build\endrom\endrom_0070ABCC_0070ABDC.bin
|unk_0870ABDC|
        INCBIN  baserom.gba_0x70abdc_0x70abe0.extracted
        INCBIN  build\endrom\endrom_0070ABE0_0070AC1C.bin
|unk_0870AC1C|
        INCBIN  baserom.gba_0x70ac1c_0x70ac40.extracted
        INCBIN  build\endrom\endrom_0070AC40_0070AC50.bin
|unk_0870AC50|
        INCBIN  baserom.gba_0x70ac50_0x70acc0.extracted
        INCBIN  build\endrom\endrom_0070ACC0_0070ACD0.bin
|unk_0870ACD0|
        INCBIN  baserom.gba_0x70acd0_0x70acd4.extracted
        INCBIN  build\endrom\endrom_0070ACD4_0070ACFC.bin
|unk_0870ACFC|
        INCBIN  baserom.gba_0x70acfc_0x70ad00.extracted
        INCBIN  build\endrom\endrom_0070AD00_0070AD10.bin
|unk_0870AD10|
        INCBIN  baserom.gba_0x70ad10_0x70ad14.extracted
        INCBIN  build\endrom\endrom_0070AD14_0070AD50.bin
|unk_0870AD50|
        INCBIN  baserom.gba_0x70ad50_0x70ad54.extracted
        INCBIN  build\endrom\endrom_0070AD54_0070AD94.bin
|unk_0870AD94|
        INCBIN  baserom.gba_0x70ad94_0x70ada4.extracted
        INCBIN  build\endrom\endrom_0070ADA4_0070ADB4.bin
|unk_0870ADB4|
        INCBIN  baserom.gba_0x70adb4_0x70adc4.extracted
        INCBIN  build\endrom\endrom_0070ADC4_0070ADD4.bin
|unk_0870ADD4|
        INCBIN  baserom.gba_0x70add4_0x70ae60.extracted
        INCBIN  build\endrom\endrom_0070AE60_0070AE70.bin
|unk_0870AE70|
        INCBIN  baserom.gba_0x70ae70_0x70aee8.extracted
        INCBIN  build\endrom\endrom_0070AEE8_0070AEF8.bin
|unk_0870AEF8|
        INCBIN  baserom.gba_0x70aef8_0x70aefc.extracted
        INCBIN  build\endrom\endrom_0070AEFC_0070AF58.bin
|unk_0870AF58|
        INCBIN  baserom.gba_0x70af58_0x70afac.extracted
        INCBIN  build\endrom\endrom_0070AFAC_0070AFDC.bin
|unk_0870AFDC|
        INCBIN  baserom.gba_0x70afdc_0x70afe0.extracted
        INCBIN  build\endrom\endrom_0070AFE0_0070B004.bin
|unk_0870B004|
        INCBIN  baserom.gba_0x70b004_0x70b014.extracted
        INCBIN  build\endrom\endrom_0070B014_0070B024.bin
|unk_0870B024|
        INCBIN  baserom.gba_0x70b024_0x70b028.extracted
        INCBIN  build\endrom\endrom_0070B028_0070B0A4.bin
|unk_0870B0A4|
        INCBIN  baserom.gba_0x70b0a4_0x70b0bc.extracted
        INCBIN  build\endrom\endrom_0070B0BC_0070B0CC.bin
|unk_0870B0CC|
        INCBIN  baserom.gba_0x70b0cc_0x70b0d0.extracted
        INCBIN  build\endrom\endrom_0070B0D0_0070B1A0.bin
|unk_0870B1A0|
        INCBIN  baserom.gba_0x70b1a0_0x70b1e0.extracted
        INCBIN  build\endrom\endrom_0070B1E0_0070B234.bin
|unk_0870B234|
        INCBIN  baserom.gba_0x70b234_0x70b238.extracted
        INCBIN  build\endrom\endrom_0070B238_0070B288.bin
|unk_0870B288|
        INCBIN  baserom.gba_0x70b288_0x70b2b4.extracted
        INCBIN  build\endrom\endrom_0070B2B4_0070B2C4.bin
|unk_0870B2C4|
        INCBIN  baserom.gba_0x70b2c4_0x70b2c8.extracted
        INCBIN  build\endrom\endrom_0070B2C8_0070B300.bin
|unk_0870B300|
        INCBIN  baserom.gba_0x70b300_0x70b32c.extracted
        INCBIN  build\endrom\endrom_0070B32C_0070B33C.bin
|unk_0870B33C|
        INCBIN  baserom.gba_0x70b33c_0x70b340.extracted
        INCBIN  build\endrom\endrom_0070B340_0070B3B4.bin
|unk_0870B3B4|
        INCBIN  baserom.gba_0x70b3b4_0x70b3b8.extracted
        INCBIN  build\endrom\endrom_0070B3B8_0070B3F8.bin
|unk_0870B3F8|
        INCBIN  baserom.gba_0x70b3f8_0x70b41c.extracted
        INCBIN  build\endrom\endrom_0070B41C_0070B42C.bin
|unk_0870B42C|
        INCBIN  baserom.gba_0x70b42c_0x70b49c.extracted
        INCBIN  build\endrom\endrom_0070B49C_0070B4AC.bin
|unk_0870B4AC|
        INCBIN  baserom.gba_0x70b4ac_0x70b4c0.extracted
        INCBIN  build\endrom\endrom_0070B4C0_0070B4D0.bin
|unk_0870B4D0|
        INCBIN  baserom.gba_0x70b4d0_0x70b4d4.extracted
        INCBIN  build\endrom\endrom_0070B4D4_0070B500.bin
|unk_0870B500|
        INCBIN  baserom.gba_0x70b500_0x70b504.extracted
        INCBIN  build\endrom\endrom_0070B504_0070B514.bin
|unk_0870B514|
        INCBIN  baserom.gba_0x70b514_0x70b518.extracted
        INCBIN  build\endrom\endrom_0070B518_0070B548.bin
|unk_0870B548|
        INCBIN  baserom.gba_0x70b548_0x70b558.extracted
        INCBIN  build\endrom\endrom_0070B558_0070B568.bin
|unk_0870B568|
        INCBIN  baserom.gba_0x70b568_0x70b578.extracted
        INCBIN  build\endrom\endrom_0070B578_0070B588.bin
|unk_0870B588|
        INCBIN  baserom.gba_0x70b588_0x70b614.extracted
        INCBIN  build\endrom\endrom_0070B614_0070B624.bin
|unk_0870B624|
        INCBIN  baserom.gba_0x70b624_0x70b69c.extracted
        INCBIN  build\endrom\endrom_0070B69C_0070B6AC.bin
|unk_0870B6AC|
        INCBIN  baserom.gba_0x70b6ac_0x70b6b0.extracted
        INCBIN  build\endrom\endrom_0070B6B0_0070B70C.bin
|unk_0870B70C|
        INCBIN  baserom.gba_0x70b70c_0x70b760.extracted
        INCBIN  build\endrom\endrom_0070B760_0070B790.bin
|unk_0870B790|
        INCBIN  baserom.gba_0x70b790_0x70b794.extracted
        INCBIN  build\endrom\endrom_0070B794_0070B7B8.bin
|unk_0870B7B8|
        INCBIN  baserom.gba_0x70b7b8_0x70b7c8.extracted
        INCBIN  build\endrom\endrom_0070B7C8_0070B7D8.bin
|unk_0870B7D8|
        INCBIN  baserom.gba_0x70b7d8_0x70b7dc.extracted
        INCBIN  build\endrom\endrom_0070B7DC_0070B858.bin
|unk_0870B858|
        INCBIN  baserom.gba_0x70b858_0x70b870.extracted
        INCBIN  build\endrom\endrom_0070B870_0070B880.bin
|unk_0870B880|
        INCBIN  baserom.gba_0x70b880_0x70b884.extracted
        INCBIN  build\endrom\endrom_0070B884_0070B954.bin
|unk_0870B954|
        INCBIN  baserom.gba_0x70b954_0x70b994.extracted
        INCBIN  build\endrom\endrom_0070B994_0070B9E8.bin
|unk_0870B9E8|
        INCBIN  baserom.gba_0x70b9e8_0x70b9ec.extracted
        INCBIN  build\endrom\endrom_0070B9EC_0070BA3C.bin
|unk_0870BA3C|
        INCBIN  baserom.gba_0x70ba3c_0x70ba68.extracted
        INCBIN  build\endrom\endrom_0070BA68_0070BA78.bin
|unk_0870BA78|
        INCBIN  baserom.gba_0x70ba78_0x70ba7c.extracted
        INCBIN  build\endrom\endrom_0070BA7C_0070BAB4.bin
|unk_0870BAB4|
        INCBIN  baserom.gba_0x70bab4_0x70bae0.extracted
        INCBIN  build\endrom\endrom_0070BAE0_0070BAF0.bin
|unk_0870BAF0|
        INCBIN  baserom.gba_0x70baf0_0x70baf4.extracted
        INCBIN  build\endrom\endrom_0070BAF4_0070BB30.bin
|unk_0870BB30|
        INCBIN  baserom.gba_0x70bb30_0x70bb54.extracted
        INCBIN  build\endrom\endrom_0070BB54_0070BB64.bin
|unk_0870BB64|
        INCBIN  baserom.gba_0x70bb64_0x70bbd4.extracted
        INCBIN  build\endrom\endrom_0070BBD4_0070BBE4.bin
|unk_0870BBE4|
        INCBIN  baserom.gba_0x70bbe4_0x70bbe8.extracted
        INCBIN  build\endrom\endrom_0070BBE8_0070BC10.bin
|unk_0870BC10|
        INCBIN  baserom.gba_0x70bc10_0x70bc14.extracted
        INCBIN  build\endrom\endrom_0070BC14_0070BC24.bin
|unk_0870BC24|
        INCBIN  baserom.gba_0x70bc24_0x70bc28.extracted
        INCBIN  build\endrom\endrom_0070BC28_0070BC68.bin
|unk_0870BC68|
        INCBIN  baserom.gba_0x70bc68_0x70bc6c.extracted
        INCBIN  build\endrom\endrom_0070BC6C_0070BCAC.bin
|unk_0870BCAC|
        INCBIN  baserom.gba_0x70bcac_0x70bcbc.extracted
        INCBIN  build\endrom\endrom_0070BCBC_0070BCCC.bin
|unk_0870BCCC|
        INCBIN  baserom.gba_0x70bccc_0x70bd6c.extracted
        INCBIN  build\endrom\endrom_0070BD6C_0070BD7C.bin
|unk_0870BD7C|
        INCBIN  baserom.gba_0x70bd7c_0x70bdf4.extracted
        INCBIN  build\endrom\endrom_0070BDF4_0070BE04.bin
|unk_0870BE04|
        INCBIN  baserom.gba_0x70be04_0x70be08.extracted
        INCBIN  build\endrom\endrom_0070BE08_0070BE60.bin
|unk_0870BE60|
        INCBIN  baserom.gba_0x70be60_0x70beb4.extracted
        INCBIN  build\endrom\endrom_0070BEB4_0070BEE4.bin
|unk_0870BEE4|
        INCBIN  baserom.gba_0x70bee4_0x70bee8.extracted
        INCBIN  build\endrom\endrom_0070BEE8_0070BF0C.bin
|unk_0870BF0C|
        INCBIN  baserom.gba_0x70bf0c_0x70bf1c.extracted
        INCBIN  build\endrom\endrom_0070BF1C_0070BF2C.bin
|unk_0870BF2C|
        INCBIN  baserom.gba_0x70bf2c_0x70bf30.extracted
        INCBIN  build\endrom\endrom_0070BF30_0070BFAC.bin
|unk_0870BFAC|
        INCBIN  baserom.gba_0x70bfac_0x70bfc4.extracted
        INCBIN  build\endrom\endrom_0070BFC4_0070BFD4.bin
|unk_0870BFD4|
        INCBIN  baserom.gba_0x70bfd4_0x70bfd8.extracted
        INCBIN  build\endrom\endrom_0070BFD8_0070C12C.bin
|unk_0870C12C|
        INCBIN  baserom.gba_0x70c12c_0x70c130.extracted
        INCBIN  build\endrom\endrom_0070C130_0070C160.bin
|unk_0870C160|
        INCBIN  baserom.gba_0x70c160_0x70c1d0.extracted
        INCBIN  build\endrom\endrom_0070C1D0_0070C1E0.bin
|unk_0870C1E0|
        INCBIN  baserom.gba_0x70c1e0_0x70c1e4.extracted
        INCBIN  build\endrom\endrom_0070C1E4_0070C1F4.bin
|unk_0870C1F4|
        INCBIN  baserom.gba_0x70c1f4_0x70c1f8.extracted
        INCBIN  build\endrom\endrom_0070C1F8_0070C208.bin
|unk_0870C208|
        INCBIN  baserom.gba_0x70c208_0x70c20c.extracted
        INCBIN  build\endrom\endrom_0070C20C_0070C24C.bin
|unk_0870C24C|
        INCBIN  baserom.gba_0x70c24c_0x70c250.extracted
        INCBIN  build\endrom\endrom_0070C250_0070C338.bin
|unk_0870C338|
        INCBIN  baserom.gba_0x70c338_0x70c348.extracted
        INCBIN  build\endrom\endrom_0070C348_0070C358.bin
|unk_0870C358|
        INCBIN  baserom.gba_0x70c358_0x70c35c.extracted
        INCBIN  build\endrom\endrom_0070C35C_0070C460.bin
|unk_0870C460|
        INCBIN  baserom.gba_0x70c460_0x70c470.extracted
        INCBIN  build\endrom\endrom_0070C470_0070C480.bin
|unk_0870C480|
        INCBIN  baserom.gba_0x70c480_0x70c484.extracted
        INCBIN  build\endrom\endrom_0070C484_0070C580.bin
|unk_0870C580|
        INCBIN  baserom.gba_0x70c580_0x70c584.extracted
        INCBIN  build\endrom\endrom_0070C584_0070C5C4.bin
|unk_0870C5C4|
        INCBIN  baserom.gba_0x70c5c4_0x70c5d4.extracted
        INCBIN  build\endrom\endrom_0070C5D4_0070C5E4.bin
|unk_0870C5E4|
        INCBIN  baserom.gba_0x70c5e4_0x70c684.extracted
        INCBIN  build\endrom\endrom_0070C684_0070C694.bin
|unk_0870C694|
        INCBIN  baserom.gba_0x70c694_0x70c70c.extracted
        INCBIN  build\endrom\endrom_0070C70C_0070C71C.bin
|unk_0870C71C|
        INCBIN  baserom.gba_0x70c71c_0x70c720.extracted
        INCBIN  build\endrom\endrom_0070C720_0070C778.bin
|unk_0870C778|
        INCBIN  baserom.gba_0x70c778_0x70c7cc.extracted
        INCBIN  build\endrom\endrom_0070C7CC_0070C7FC.bin
|unk_0870C7FC|
        INCBIN  baserom.gba_0x70c7fc_0x70c800.extracted
        INCBIN  build\endrom\endrom_0070C800_0070C824.bin
|unk_0870C824|
        INCBIN  baserom.gba_0x70c824_0x70c834.extracted
        INCBIN  build\endrom\endrom_0070C834_0070C844.bin
|unk_0870C844|
        INCBIN  baserom.gba_0x70c844_0x70c848.extracted
        INCBIN  build\endrom\endrom_0070C848_0070C8C4.bin
|unk_0870C8C4|
        INCBIN  baserom.gba_0x70c8c4_0x70c8dc.extracted
        INCBIN  build\endrom\endrom_0070C8DC_0070C8EC.bin
|unk_0870C8EC|
        INCBIN  baserom.gba_0x70c8ec_0x70c8f0.extracted
        INCBIN  build\endrom\endrom_0070C8F0_0070CA74.bin
|unk_0870CA74|
        INCBIN  baserom.gba_0x70ca74_0x70ca78.extracted
        INCBIN  build\endrom\endrom_0070CA78_0070CAC8.bin
|unk_0870CAC8|
        INCBIN  baserom.gba_0x70cac8_0x70caf4.extracted
        INCBIN  build\endrom\endrom_0070CAF4_0070CB04.bin
|unk_0870CB04|
        INCBIN  baserom.gba_0x70cb04_0x70cb08.extracted
        INCBIN  build\endrom\endrom_0070CB08_0070CB40.bin
|unk_0870CB40|
        INCBIN  baserom.gba_0x70cb40_0x70cb6c.extracted
        INCBIN  build\endrom\endrom_0070CB6C_0070CB7C.bin
|unk_0870CB7C|
        INCBIN  baserom.gba_0x70cb7c_0x70cb80.extracted
        INCBIN  build\endrom\endrom_0070CB80_0070CBE4.bin
|unk_0870CBE4|
        INCBIN  baserom.gba_0x70cbe4_0x70cc08.extracted
        INCBIN  build\endrom\endrom_0070CC08_0070CC18.bin
|unk_0870CC18|
        INCBIN  baserom.gba_0x70cc18_0x70cc88.extracted
        INCBIN  build\endrom\endrom_0070CC88_0070CC98.bin
|unk_0870CC98|
        INCBIN  baserom.gba_0x70cc98_0x70cc9c.extracted
        INCBIN  build\endrom\endrom_0070CC9C_0070CCC4.bin
|unk_0870CCC4|
        INCBIN  baserom.gba_0x70ccc4_0x70ccc8.extracted
        INCBIN  build\endrom\endrom_0070CCC8_0070CCD8.bin
|unk_0870CCD8|
        INCBIN  baserom.gba_0x70ccd8_0x70ccdc.extracted
        INCBIN  build\endrom\endrom_0070CCDC_0070CD1C.bin
|unk_0870CD1C|
        INCBIN  baserom.gba_0x70cd1c_0x70cd20.extracted
        INCBIN  build\endrom\endrom_0070CD20_0070CD60.bin
|unk_0870CD60|
        INCBIN  baserom.gba_0x70cd60_0x70cd70.extracted
        INCBIN  build\endrom\endrom_0070CD70_0070CD80.bin
|unk_0870CD80|
        INCBIN  baserom.gba_0x70cd80_0x70cd90.extracted
        INCBIN  build\endrom\endrom_0070CD90_0070CDA0.bin
|unk_0870CDA0|
        INCBIN  baserom.gba_0x70cda0_0x70ce2c.extracted
        INCBIN  build\endrom\endrom_0070CE2C_0070CE3C.bin
|unk_0870CE3C|
        INCBIN  baserom.gba_0x70ce3c_0x70ceb4.extracted
        INCBIN  build\endrom\endrom_0070CEB4_0070CEC4.bin
|unk_0870CEC4|
        INCBIN  baserom.gba_0x70cec4_0x70cec8.extracted
        INCBIN  build\endrom\endrom_0070CEC8_0070CF24.bin
|unk_0870CF24|
        INCBIN  baserom.gba_0x70cf24_0x70cf78.extracted
        INCBIN  build\endrom\endrom_0070CF78_0070CF98.bin
|unk_0870CF98|
        INCBIN  baserom.gba_0x70cf98_0x70cf9c.extracted
        INCBIN  build\endrom\endrom_0070CF9C_0070CFAC.bin
|unk_0870CFAC|
        INCBIN  baserom.gba_0x70cfac_0x70cfb0.extracted
        INCBIN  build\endrom\endrom_0070CFB0_0070CFD4.bin
|unk_0870CFD4|
        INCBIN  baserom.gba_0x70cfd4_0x70cfe4.extracted
        INCBIN  build\endrom\endrom_0070CFE4_0070CFF4.bin
|unk_0870CFF4|
        INCBIN  baserom.gba_0x70cff4_0x70cff8.extracted
        INCBIN  build\endrom\endrom_0070CFF8_0070D074.bin
|unk_0870D074|
        INCBIN  baserom.gba_0x70d074_0x70d08c.extracted
        INCBIN  build\endrom\endrom_0070D08C_0070D09C.bin
|unk_0870D09C|
        INCBIN  baserom.gba_0x70d09c_0x70d0a0.extracted
        INCBIN  build\endrom\endrom_0070D0A0_0070D170.bin
|unk_0870D170|
        INCBIN  baserom.gba_0x70d170_0x70d1b0.extracted
        INCBIN  build\endrom\endrom_0070D1B0_0070D204.bin
|unk_0870D204|
        INCBIN  baserom.gba_0x70d204_0x70d208.extracted
        INCBIN  build\endrom\endrom_0070D208_0070D258.bin
|unk_0870D258|
        INCBIN  baserom.gba_0x70d258_0x70d284.extracted
        INCBIN  build\endrom\endrom_0070D284_0070D294.bin
|unk_0870D294|
        INCBIN  baserom.gba_0x70d294_0x70d298.extracted
        INCBIN  build\endrom\endrom_0070D298_0070D2D0.bin
|unk_0870D2D0|
        INCBIN  baserom.gba_0x70d2d0_0x70d2fc.extracted
        INCBIN  build\endrom\endrom_0070D2FC_0070D30C.bin
|unk_0870D30C|
        INCBIN  baserom.gba_0x70d30c_0x70d310.extracted
        INCBIN  build\endrom\endrom_0070D310_0070D384.bin
|unk_0870D384|
        INCBIN  baserom.gba_0x70d384_0x70d3a8.extracted
        INCBIN  build\endrom\endrom_0070D3A8_0070D3B8.bin
|unk_0870D3B8|
        INCBIN  baserom.gba_0x70d3b8_0x70d428.extracted
        INCBIN  build\endrom\endrom_0070D428_0070D438.bin
|unk_0870D438|
        INCBIN  baserom.gba_0x70d438_0x70d43c.extracted
        INCBIN  build\endrom\endrom_0070D43C_0070D464.bin
|unk_0870D464|
        INCBIN  baserom.gba_0x70d464_0x70d468.extracted
        INCBIN  build\endrom\endrom_0070D468_0070D478.bin
|unk_0870D478|
        INCBIN  baserom.gba_0x70d478_0x70d47c.extracted
        INCBIN  build\endrom\endrom_0070D47C_0070D498.bin
|unk_0870D498|
        INCBIN  baserom.gba_0x70d498_0x70d4a8.extracted
        INCBIN  build\endrom\endrom_0070D4A8_0070D4B8.bin
|unk_0870D4B8|
        INCBIN  baserom.gba_0x70d4b8_0x70d4d4.extracted
        INCBIN  build\endrom\endrom_0070D4D4_0070D4E4.bin
|unk_0870D4E4|
        INCBIN  baserom.gba_0x70d4e4_0x70d4e8.extracted
        INCBIN  build\endrom\endrom_0070D4E8_0070D5D8.bin
|unk_0870D5D8|
        INCBIN  baserom.gba_0x70d5d8_0x70d5dc.extracted
        INCBIN  build\endrom\endrom_0070D5DC_0070D61C.bin
|unk_0870D61C|
        INCBIN  baserom.gba_0x70d61c_0x70d62c.extracted
        INCBIN  build\endrom\endrom_0070D62C_0070D63C.bin
|unk_0870D63C|
        INCBIN  baserom.gba_0x70d63c_0x70d6b4.extracted
        INCBIN  build\endrom\endrom_0070D6B4_0070D6C4.bin
|unk_0870D6C4|
        INCBIN  baserom.gba_0x70d6c4_0x70d73c.extracted
        INCBIN  build\endrom\endrom_0070D73C_0070D74C.bin
|unk_0870D74C|
        INCBIN  baserom.gba_0x70d74c_0x70d750.extracted
        INCBIN  build\endrom\endrom_0070D750_0070D7A8.bin
|unk_0870D7A8|
        INCBIN  baserom.gba_0x70d7a8_0x70d7fc.extracted
        INCBIN  build\endrom\endrom_0070D7FC_0070D81C.bin
|unk_0870D81C|
        INCBIN  baserom.gba_0x70d81c_0x70d820.extracted
        INCBIN  build\endrom\endrom_0070D820_0070D840.bin
|unk_0870D840|
        INCBIN  baserom.gba_0x70d840_0x70d850.extracted
        INCBIN  build\endrom\endrom_0070D850_0070D860.bin
|unk_0870D860|
        INCBIN  baserom.gba_0x70d860_0x70d864.extracted
        INCBIN  build\endrom\endrom_0070D864_0070D8E0.bin
|unk_0870D8E0|
        INCBIN  baserom.gba_0x70d8e0_0x70d8f8.extracted
        INCBIN  build\endrom\endrom_0070D8F8_0070D908.bin
|unk_0870D908|
        INCBIN  baserom.gba_0x70d908_0x70d90c.extracted
        INCBIN  build\endrom\endrom_0070D90C_0070D964.bin
|unk_0870D964|
        INCBIN  baserom.gba_0x70d964_0x70d968.extracted
        INCBIN  build\endrom\endrom_0070D968_0070D9EC.bin
|unk_0870D9EC|
        INCBIN  baserom.gba_0x70d9ec_0x70da18.extracted
        INCBIN  build\endrom\endrom_0070DA18_0070DA28.bin
|unk_0870DA28|
        INCBIN  baserom.gba_0x70da28_0x70da2c.extracted
        INCBIN  build\endrom\endrom_0070DA2C_0070DA5C.bin
|unk_0870DA5C|
        INCBIN  baserom.gba_0x70da5c_0x70da78.extracted
        INCBIN  build\endrom\endrom_0070DA78_0070DA88.bin
|unk_0870DA88|
        INCBIN  baserom.gba_0x70da88_0x70da8c.extracted
        INCBIN  build\endrom\endrom_0070DA8C_0070DAA4.bin
|unk_0870DAA4|
        INCBIN  baserom.gba_0x70daa4_0x70dabc.extracted
        INCBIN  build\endrom\endrom_0070DABC_0070DACC.bin
|unk_0870DACC|
        INCBIN  baserom.gba_0x70dacc_0x70db40.extracted
        INCBIN  build\endrom\endrom_0070DB40_0070DB50.bin
|unk_0870DB50|
        INCBIN  baserom.gba_0x70db50_0x70db54.extracted
        INCBIN  build\endrom\endrom_0070DB54_0070DB7C.bin
|unk_0870DB7C|
        INCBIN  baserom.gba_0x70db7c_0x70db80.extracted
        INCBIN  build\endrom\endrom_0070DB80_0070DB90.bin
|unk_0870DB90|
        INCBIN  baserom.gba_0x70db90_0x70db94.extracted
        INCBIN  build\endrom\endrom_0070DB94_0070DBD0.bin
|unk_0870DBD0|
        INCBIN  baserom.gba_0x70dbd0_0x70dbd4.extracted
        INCBIN  build\endrom\endrom_0070DBD4_0070DC14.bin
|unk_0870DC14|
        INCBIN  baserom.gba_0x70dc14_0x70dc38.extracted
        INCBIN  build\endrom\endrom_0070DC38_0070DCCC.bin
|unk_0870DCCC|
        INCBIN  baserom.gba_0x70dccc_0x70dcf4.extracted
        INCBIN  build\endrom\endrom_0070DCF4_0070DD04.bin
|unk_0870DD04|
        INCBIN  baserom.gba_0x70dd04_0x70dd08.extracted
        INCBIN  build\endrom\endrom_0070DD08_0070DD68.bin
|unk_0870DD68|
        INCBIN  baserom.gba_0x70dd68_0x70dd6c.extracted
        INCBIN  build\endrom\endrom_0070DD6C_0070DDAC.bin
|unk_0870DDAC|
        INCBIN  baserom.gba_0x70ddac_0x70ddd0.extracted
        INCBIN  build\endrom\endrom_0070DDD0_0070DE34.bin
|unk_0870DE34|
        INCBIN  baserom.gba_0x70de34_0x70de38.extracted
        INCBIN  build\endrom\endrom_0070DE38_0070DEB0.bin
|unk_0870DEB0|
        INCBIN  baserom.gba_0x70deb0_0x70dec4.extracted
        INCBIN  build\endrom\endrom_0070DEC4_0070DED4.bin
|unk_0870DED4|
        INCBIN  baserom.gba_0x70ded4_0x70defc.extracted
        INCBIN  build\endrom\endrom_0070DEFC_0070DF0C.bin
|unk_0870DF0C|
        INCBIN  baserom.gba_0x70df0c_0x70df10.extracted
        INCBIN  build\endrom\endrom_0070DF10_0070DF20.bin
|unk_0870DF20|
        INCBIN  baserom.gba_0x70df20_0x70df5c.extracted
        INCBIN  build\endrom\endrom_0070DF5C_0070DF6C.bin
|unk_0870DF6C|
        INCBIN  baserom.gba_0x70df6c_0x70df94.extracted
        INCBIN  build\endrom\endrom_0070DF94_0070DFA4.bin
|unk_0870DFA4|
        INCBIN  baserom.gba_0x70dfa4_0x70dfb8.extracted
        INCBIN  build\endrom\endrom_0070DFB8_0070DFC8.bin
|unk_0870DFC8|
        INCBIN  baserom.gba_0x70dfc8_0x70dfcc.extracted
        INCBIN  build\endrom\endrom_0070DFCC_0070E114.bin
|unk_0870E114|
        INCBIN  baserom.gba_0x70e114_0x70e118.extracted
        INCBIN  build\endrom\endrom_0070E118_0070E128.bin
|unk_0870E128|
        INCBIN  baserom.gba_0x70e128_0x70e12c.extracted
        INCBIN  build\endrom\endrom_0070E12C_0070E160.bin
|unk_0870E160|
        INCBIN  baserom.gba_0x70e160_0x70e170.extracted
        INCBIN  build\endrom\endrom_0070E170_0070E180.bin
|unk_0870E180|
        INCBIN  baserom.gba_0x70e180_0x70e184.extracted
        INCBIN  build\endrom\endrom_0070E184_0070E1D4.bin
|unk_0870E1D4|
        INCBIN  baserom.gba_0x70e1d4_0x70e1ec.extracted
        INCBIN  build\endrom\endrom_0070E1EC_0070E224.bin
|unk_0870E224|
        INCBIN  baserom.gba_0x70e224_0x70e228.extracted
        INCBIN  build\endrom\endrom_0070E228_0070E260.bin
|unk_0870E260|
        INCBIN  baserom.gba_0x70e260_0x70e264.extracted
        INCBIN  build\endrom\endrom_0070E264_0070E2A4.bin
|unk_0870E2A4|
        INCBIN  baserom.gba_0x70e2a4_0x70e2c8.extracted
        INCBIN  build\endrom\endrom_0070E2C8_0070E2E8.bin
|unk_0870E2E8|
        INCBIN  baserom.gba_0x70e2e8_0x70e2fc.extracted
        INCBIN  build\endrom\endrom_0070E2FC_0070E30C.bin
|unk_0870E30C|
        INCBIN  baserom.gba_0x70e30c_0x70e310.extracted
        INCBIN  build\endrom\endrom_0070E310_0070E320.bin
|unk_0870E320|
        INCBIN  baserom.gba_0x70e320_0x70e334.extracted
        INCBIN  build\endrom\endrom_0070E334_0070E344.bin
|unk_0870E344|
        INCBIN  baserom.gba_0x70e344_0x70e348.extracted
        INCBIN  build\endrom\endrom_0070E348_0070E368.bin
|unk_0870E368|
        INCBIN  baserom.gba_0x70e368_0x70e36c.extracted
        INCBIN  build\endrom\endrom_0070E36C_0070E394.bin
|unk_0870E394|
        INCBIN  baserom.gba_0x70e394_0x70e3ac.extracted
        INCBIN  build\endrom\endrom_0070E3AC_0070E3BC.bin
|unk_0870E3BC|
        INCBIN  baserom.gba_0x70e3bc_0x70e3c0.extracted
        INCBIN  build\endrom\endrom_0070E3C0_0070E404.bin
|unk_0870E404|
        INCBIN  baserom.gba_0x70e404_0x70e41c.extracted
        INCBIN  build\endrom\endrom_0070E41C_0070E42C.bin
|unk_0870E42C|
        INCBIN  baserom.gba_0x70e42c_0x70e430.extracted
        INCBIN  build\endrom\endrom_0070E430_0070E448.bin
|unk_0870E448|
        INCBIN  baserom.gba_0x70e448_0x70e458.extracted
        INCBIN  build\endrom\endrom_0070E458_0070E4D4.bin
|unk_0870E4D4|
        INCBIN  baserom.gba_0x70e4d4_0x70e4e8.extracted
        INCBIN  build\endrom\endrom_0070E4E8_0070E4F8.bin
|unk_0870E4F8|
        INCBIN  baserom.gba_0x70e4f8_0x70e4fc.extracted
        INCBIN  build\endrom\endrom_0070E4FC_0070E57C.bin
|unk_0870E57C|
        INCBIN  baserom.gba_0x70e57c_0x70e580.extracted
        INCBIN  build\endrom\endrom_0070E580_0070E590.bin
|unk_0870E590|
        INCBIN  baserom.gba_0x70e590_0x70e594.extracted
        INCBIN  build\endrom\endrom_0070E594_0070E5DC.bin
|unk_0870E5DC|
        INCBIN  baserom.gba_0x70e5dc_0x70e5e0.extracted
        INCBIN  build\endrom\endrom_0070E5E0_0070E664.bin
|unk_0870E664|
        INCBIN  baserom.gba_0x70e664_0x70e678.extracted
        INCBIN  build\endrom\endrom_0070E678_0070E688.bin
|unk_0870E688|
        INCBIN  baserom.gba_0x70e688_0x70e6a0.extracted
        INCBIN  build\endrom\endrom_0070E6A0_0070E6B0.bin
|unk_0870E6B0|
        INCBIN  baserom.gba_0x70e6b0_0x70e6b4.extracted
        INCBIN  build\endrom\endrom_0070E6B4_0070E6C4.bin
|unk_0870E6C4|
        INCBIN  baserom.gba_0x70e6c4_0x70e6c8.extracted
        INCBIN  build\endrom\endrom_0070E6C8_0070E6D8.bin
|unk_0870E6D8|
        INCBIN  baserom.gba_0x70e6d8_0x70e6dc.extracted
        INCBIN  build\endrom\endrom_0070E6DC_0070E71C.bin
|unk_0870E71C|
        INCBIN  baserom.gba_0x70e71c_0x70e734.extracted
        INCBIN  build\endrom\endrom_0070E734_0070E744.bin
|unk_0870E744|
        INCBIN  baserom.gba_0x70e744_0x70e748.extracted
        INCBIN  build\endrom\endrom_0070E748_0070E758.bin
|unk_0870E758|
        INCBIN  baserom.gba_0x70e758_0x70e78c.extracted
        INCBIN  build\endrom\endrom_0070E78C_0070E79C.bin
|unk_0870E79C|
        INCBIN  baserom.gba_0x70e79c_0x70e7a0.extracted
        INCBIN  build\endrom\endrom_0070E7A0_0070E7CC.bin
|unk_0870E7CC|
        INCBIN  baserom.gba_0x70e7cc_0x70e7d0.extracted
        INCBIN  build\endrom\endrom_0070E7D0_0070E7E0.bin
|unk_0870E7E0|
        INCBIN  baserom.gba_0x70e7e0_0x70e814.extracted
        INCBIN  build\endrom\endrom_0070E814_0070E824.bin
|unk_0870E824|
        INCBIN  baserom.gba_0x70e824_0x70e828.extracted
        INCBIN  build\endrom\endrom_0070E828_0070E854.bin
|unk_0870E854|
        INCBIN  baserom.gba_0x70e854_0x70e858.extracted
        INCBIN  build\endrom\endrom_0070E858_0070E868.bin
|unk_0870E868|
        INCBIN  baserom.gba_0x70e868_0x70e87c.extracted
        INCBIN  build\endrom\endrom_0070E87C_0070E88C.bin
|unk_0870E88C|
        INCBIN  baserom.gba_0x70e88c_0x70e8dc.extracted
        INCBIN  build\endrom\endrom_0070E8DC_0070E8EC.bin
|unk_0870E8EC|
        INCBIN  baserom.gba_0x70e8ec_0x70e8f0.extracted
        INCBIN  build\endrom\endrom_0070E8F0_0070E978.bin
|unk_0870E978|
        INCBIN  baserom.gba_0x70e978_0x70e97c.extracted
        INCBIN  build\endrom\endrom_0070E97C_0070E994.bin
|unk_0870E994|
        INCBIN  baserom.gba_0x70e994_0x70e9ac.extracted
        INCBIN  build\endrom\endrom_0070E9AC_0070E9BC.bin
|unk_0870E9BC|
        INCBIN  baserom.gba_0x70e9bc_0x70e9d0.extracted
        INCBIN  build\endrom\endrom_0070E9D0_0070E9E0.bin
|unk_0870E9E0|
        INCBIN  baserom.gba_0x70e9e0_0x70e9e4.extracted
        INCBIN  build\endrom\endrom_0070E9E4_0070EA2C.bin
|unk_0870EA2C|
        INCBIN  baserom.gba_0x70ea2c_0x70ea4c.extracted
        INCBIN  build\endrom\endrom_0070EA4C_0070EA78.bin
|unk_0870EA78|
        INCBIN  baserom.gba_0x70ea78_0x70ea7c.extracted
        INCBIN  build\endrom\endrom_0070EA7C_0070EAA4.bin
|unk_0870EAA4|
        INCBIN  baserom.gba_0x70eaa4_0x70eaa8.extracted
        INCBIN  build\endrom\endrom_0070EAA8_0070EB9C.bin
|unk_0870EB9C|
        INCBIN  baserom.gba_0x70eb9c_0x70eba0.extracted
        INCBIN  build\endrom\endrom_0070EBA0_0070EBF4.bin
|unk_0870EBF4|
        INCBIN  baserom.gba_0x70ebf4_0x70ebfc.extracted
        INCBIN  build\endrom\endrom_0070EBFC_0070EC40.bin
|unk_0870EC40|
        INCBIN  baserom.gba_0x70ec40_0x70ec44.extracted
        INCBIN  build\endrom\endrom_0070EC44_0070EC74.bin
|unk_0870EC74|
        INCBIN  baserom.gba_0x70ec74_0x70ec9c.extracted
        INCBIN  build\endrom\endrom_0070EC9C_0070ECAC.bin
|unk_0870ECAC|
        INCBIN  baserom.gba_0x70ecac_0x70ecb0.extracted
        INCBIN  build\endrom\endrom_0070ECB0_0070ECC8.bin
|unk_0870ECC8|
        INCBIN  baserom.gba_0x70ecc8_0x70ecec.extracted
        INCBIN  build\endrom\endrom_0070ECEC_0070ECFC.bin
|unk_0870ECFC|
        INCBIN  baserom.gba_0x70ecfc_0x70ed50.extracted
        INCBIN  build\endrom\endrom_0070ED50_0070ED60.bin
|unk_0870ED60|
        INCBIN  baserom.gba_0x70ed60_0x70ed64.extracted
        INCBIN  build\endrom\endrom_0070ED64_0070ED90.bin
|unk_0870ED90|
        INCBIN  baserom.gba_0x70ed90_0x70edb0.extracted
        INCBIN  build\endrom\endrom_0070EDB0_0070EDC0.bin
|unk_0870EDC0|
        INCBIN  baserom.gba_0x70edc0_0x70edc8.extracted
        INCBIN  build\endrom\endrom_0070EDC8_0070EE58.bin
|unk_0870EE58|
        INCBIN  baserom.gba_0x70ee58_0x70ee68.extracted
        INCBIN  build\endrom\endrom_0070EE68_0070EE78.bin
|unk_0870EE78|
        INCBIN  baserom.gba_0x70ee78_0x70ee7c.extracted
        INCBIN  build\endrom\endrom_0070EE7C_0070EECC.bin
|unk_0870EECC|
        INCBIN  baserom.gba_0x70eecc_0x70eed0.extracted
        INCBIN  build\endrom\endrom_0070EED0_0070EF8C.bin
|unk_0870EF8C|
        INCBIN  baserom.gba_0x70ef8c_0x70ef9c.extracted
        INCBIN  build\endrom\endrom_0070EF9C_0070EFAC.bin
|unk_0870EFAC|
        INCBIN  baserom.gba_0x70efac_0x70efb0.extracted
        INCBIN  build\endrom\endrom_0070EFB0_0070F020.bin
|unk_0870F020|
        INCBIN  baserom.gba_0x70f020_0x70f054.extracted
        INCBIN  build\endrom\endrom_0070F054_0070F064.bin
|unk_0870F064|
        INCBIN  baserom.gba_0x70f064_0x70f068.extracted
        INCBIN  build\endrom\endrom_0070F068_0070F078.bin
|unk_0870F078|
        INCBIN  baserom.gba_0x70f078_0x70f08c.extracted
        INCBIN  build\endrom\endrom_0070F08C_0070F09C.bin
|unk_0870F09C|
        INCBIN  baserom.gba_0x70f09c_0x70f0c4.extracted
        INCBIN  build\endrom\endrom_0070F0C4_0070F0D4.bin
|unk_0870F0D4|
        INCBIN  baserom.gba_0x70f0d4_0x70f0e8.extracted
        INCBIN  build\endrom\endrom_0070F0E8_0070F0F8.bin
|unk_0870F0F8|
        INCBIN  baserom.gba_0x70f0f8_0x70f0fc.extracted
        INCBIN  build\endrom\endrom_0070F0FC_0070F10C.bin
|unk_0870F10C|
        INCBIN  baserom.gba_0x70f10c_0x70f110.extracted
        INCBIN  build\endrom\endrom_0070F110_0070F19C.bin
|unk_0870F19C|
        INCBIN  baserom.gba_0x70f19c_0x70f1a0.extracted
        INCBIN  build\endrom\endrom_0070F1A0_0070F238.bin
|unk_0870F238|
        INCBIN  baserom.gba_0x70f238_0x70f23c.extracted
        INCBIN  build\endrom\endrom_0070F23C_0070F26C.bin
|unk_0870F26C|
        INCBIN  baserom.gba_0x70f26c_0x70f27c.extracted
        INCBIN  build\endrom\endrom_0070F27C_0070F28C.bin
|unk_0870F28C|
        INCBIN  baserom.gba_0x70f28c_0x70f2c0.extracted
        INCBIN  build\endrom\endrom_0070F2C0_0070F2D0.bin
|unk_0870F2D0|
        INCBIN  baserom.gba_0x70f2d0_0x70f2d4.extracted
        INCBIN  build\endrom\endrom_0070F2D4_0070F2FC.bin
|unk_0870F2FC|
        INCBIN  baserom.gba_0x70f2fc_0x70f328.extracted
        INCBIN  build\endrom\endrom_0070F328_0070F338.bin
|unk_0870F338|
        INCBIN  baserom.gba_0x70f338_0x70f33c.extracted
        INCBIN  build\endrom\endrom_0070F33C_0070F394.bin
|unk_0870F394|
        INCBIN  baserom.gba_0x70f394_0x70f398.extracted
        INCBIN  build\endrom\endrom_0070F398_0070F3F8.bin
|unk_0870F3F8|
        INCBIN  baserom.gba_0x70f3f8_0x70f3fc.extracted
        INCBIN  build\endrom\endrom_0070F3FC_0070F434.bin
|unk_0870F434|
        INCBIN  baserom.gba_0x70f434_0x70f444.extracted
        INCBIN  build\endrom\endrom_0070F444_0070F464.bin
|unk_0870F464|
        INCBIN  baserom.gba_0x70f464_0x70f468.extracted
        INCBIN  build\endrom\endrom_0070F468_0070F4AC.bin
|unk_0870F4AC|
        INCBIN  baserom.gba_0x70f4ac_0x70f4b0.extracted
        INCBIN  build\endrom\endrom_0070F4B0_0070F4C0.bin
|unk_0870F4C0|
        INCBIN  baserom.gba_0x70f4c0_0x70f4c4.extracted
        INCBIN  build\endrom\endrom_0070F4C4_0070F514.bin
        INCBIN  build\endrom\endrom_0070F514_00710EF4.bin
        INCLUDE rawlabeled_710ef4.s
        INCBIN  build\endrom\endrom_00711274_007122DC.bin
        INCLUDE rawlabeled_7122dc.s
        INCLUDE rawlabeled_7122f8.s
        INCBIN  build\endrom\endrom_0071E258_0071E274.bin
        INCLUDE rawlabeled_71e274.s
        INCBIN  build\endrom\endrom_0072C378_0072C388.bin
        INCLUDE rawlabeled_72c388.s
        INCBIN  build\endrom\endrom_007315E8_0073198C.bin
        INCLUDE rawlabeled_73198c.s
        INCBIN  build\endrom\endrom_007319E0_00732350.bin
        INCLUDE rawlabeled_732350.s
        INCBIN  build\endrom\endrom_00732384_007325E8.bin
        INCLUDE rawlabeled_7325e8.s
        INCBIN  build\endrom\endrom_00732604_00732B20.bin
        INCLUDE rawlabeled_732b20.s
        INCBIN  build\endrom\endrom_00733040_00733AE8.bin
        INCLUDE rawlabeled_733ae8.s
        INCBIN  build\endrom\endrom_00733B8C_00733C9C.bin
        INCLUDE rawlabeled_733c9c.s
        INCBIN  build\endrom\endrom_00734084_007347BC.bin
        INCLUDE rawlabeled_7347bc.s
        INCBIN  build\endrom\endrom_007348B0_00734A5C.bin
        INCLUDE rawlabeled_734a5c.s
        INCBIN  build\endrom\endrom_00734AF4_00734C9C.bin
        INCLUDE rawlabeled_734c9c.s
        INCBIN  build\endrom\endrom_00734D74_00734FD4.bin
        INCLUDE rawlabeled_734fd4.s
        INCBIN  build\endrom\endrom_00735210_007357F0.bin
        INCLUDE rawlabeled_7357f0.s
        INCBIN  build\endrom\endrom_00735944_00735C74.bin
        INCLUDE rawlabeled_735c74.s
        INCBIN  build\endrom\endrom_00735D1C_00735E34.bin
        INCLUDE rawlabeled_735e34.s
        INCBIN  build\endrom\endrom_007366A8_007372E8.bin
        INCLUDE rawlabeled_7372e8.s
        INCBIN  build\endrom\endrom_00737D58_0073917C.bin
        INCLUDE rawlabeled_73917c.s
        INCBIN  build\endrom\endrom_00739BB8_0073A134.bin
        INCLUDE rawlabeled_73a134.s
        INCBIN  build\endrom\endrom_0073A9B4_0073AF04.bin
        INCLUDE rawlabeled_73af04.s
        INCBIN  build\endrom\endrom_0073B050_0073B1D8.bin
        INCLUDE rawlabeled_73b1d8.s
        INCBIN  build\endrom\endrom_0073B2AC_0073B4C4.bin
        INCLUDE rawlabeled_73b4c4.s
        INCBIN  build\endrom\endrom_0073B800_0073BE30.bin
        INCLUDE rawlabeled_73be30.s
        INCBIN  build\endrom\endrom_0073BEF4_0073C04C.bin
        INCLUDE rawlabeled_73c04c.s
        INCBIN  build\endrom\endrom_0073C4B4_0073C998.bin
        INCLUDE rawlabeled_73c998.s
        INCBIN  build\endrom\endrom_0073CAD8_0073CBB4.bin
        INCLUDE rawlabeled_73cbb4.s
        INCBIN  build\endrom\endrom_0073CC84_0073CE0C.bin
        INCLUDE rawlabeled_73ce0c.s
        INCBIN  build\endrom\endrom_0073D490_0073DDD4.bin
        INCLUDE rawlabeled_73ddd4.s
        INCBIN  build\endrom\endrom_0073DF88_0073E120.bin
        INCLUDE rawlabeled_73e120.s
        INCBIN  build\endrom\endrom_0073E31C_0073E540.bin
        INCLUDE rawlabeled_73e540.s
        INCBIN  build\endrom\endrom_0073F0CC_0073FE00.bin
        INCLUDE rawlabeled_73fe00.s
        INCBIN  build\endrom\endrom_007400E0_00740440.bin
        INCLUDE rawlabeled_740440.s
        INCBIN  build\endrom\endrom_00740654_007408D8.bin
        INCLUDE rawlabeled_7408d8.s
        INCBIN  build\endrom\endrom_00740938_0074098C.bin
        INCLUDE rawlabeled_74098c.s
        INCBIN  build\endrom\endrom_00740A5C_00740B98.bin
        INCLUDE rawlabeled_740b98.s
        INCBIN  build\endrom\endrom_00740CA8_00740E1C.bin
        INCLUDE rawlabeled_740e1c.s
        INCBIN  build\endrom\endrom_0074188C_00742B20.bin
        INCLUDE rawlabeled_742b20.s
        INCBIN  build\endrom\endrom_00742BEC_00742C48.bin
        INCLUDE rawlabeled_742c48.s
        INCBIN  build\endrom\endrom_00742E18_0074312C.bin
|unk_0874312C|
        INCBIN  baserom.gba_0x74312c_0x743264.extracted
        INCBIN  build\endrom\endrom_00743264_007434B0.bin
|unk_087434B0|
        INCBIN  baserom.gba_0x7434b0_0x743e68.extracted
        INCBIN  build\endrom\endrom_00743E68_00744EF0.bin
|unk_08744EF0|
        INCBIN  baserom.gba_0x744ef0_0x74535c.extracted
        INCBIN  build\endrom\endrom_0074535C_00745798.bin
|unk_08745798|
        INCBIN  baserom.gba_0x745798_0x74606c.extracted
        INCBIN  build\endrom\endrom_0074606C_00746844.bin
|unk_08746844|
        INCBIN  baserom.gba_0x746844_0x746c74.extracted
        INCBIN  build\endrom\endrom_00746C74_007473E4.bin
|unk_087473E4|
        INCBIN  baserom.gba_0x7473e4_0x74798c.extracted
        INCBIN  build\endrom\endrom_0074798C_00747E64.bin
|unk_08747E64|
        INCBIN  baserom.gba_0x747e64_0x74829c.extracted
        INCBIN  build\endrom\endrom_0074829C_00748668.bin
|unk_08748668|
        INCBIN  baserom.gba_0x748668_0x748788.extracted
        INCBIN  build\endrom\endrom_00748788_00748860.bin
|unk_08748860|
        INCBIN  baserom.gba_0x748860_0x7488e4.extracted
        INCBIN  build\endrom\endrom_007488E4_007489D4.bin
|unk_087489D4|
        INCBIN  baserom.gba_0x7489d4_0x748a38.extracted
        INCBIN  build\endrom\endrom_00748A38_00748AC8.bin
|unk_08748AC8|
        INCBIN  baserom.gba_0x748ac8_0x748c58.extracted
        INCBIN  build\endrom\endrom_00748C58_00748F34.bin
|unk_08748F34|
        INCBIN  baserom.gba_0x748f34_0x74901c.extracted
        INCBIN  build\endrom\endrom_0074901C_00749118.bin
|unk_08749118|
        INCBIN  baserom.gba_0x749118_0x749178.extracted
        INCBIN  build\endrom\endrom_00749178_007491D0.bin
|unk_087491D0|
        INCBIN  baserom.gba_0x7491d0_0x7495c8.extracted
        INCBIN  build\endrom\endrom_007495C8_0074980C.bin
|unk_0874980C|
        INCBIN  baserom.gba_0x74980c_0x749cbc.extracted
        INCBIN  build\endrom\endrom_00749CBC_00749F1C.bin
|unk_08749F1C|
        INCBIN  baserom.gba_0x749f1c_0x74a820.extracted
        INCBIN  build\endrom\endrom_0074A820_0074AA98.bin
|unk_0874AA98|
        INCBIN  baserom.gba_0x74aa98_0x74ac18.extracted
        INCBIN  build\endrom\endrom_0074AC18_0074ACB4.bin
|unk_0874ACB4|
        INCBIN  baserom.gba_0x74acb4_0x74b0f8.extracted
        INCBIN  build\endrom\endrom_0074B0F8_0074B8B4.bin
|unk_0874B8B4|
        INCBIN  baserom.gba_0x74b8b4_0x74ba44.extracted
        INCBIN  build\endrom\endrom_0074BA44_0074BB40.bin
|unk_0874BB40|
        INCBIN  baserom.gba_0x74bb40_0x74bc88.extracted
        INCBIN  build\endrom\endrom_0074BC88_0074BCF8.bin
|unk_0874BCF8|
        INCBIN  baserom.gba_0x74bcf8_0x74bfb4.extracted
        INCBIN  build\endrom\endrom_0074BFB4_0074C58C.bin
|unk_0874C58C|
        INCBIN  baserom.gba_0x74c58c_0x74c660.extracted
        INCBIN  build\endrom\endrom_0074C660_0074C804.bin
|unk_0874C804|
        INCBIN  baserom.gba_0x74c804_0x74c884.extracted
        INCBIN  build\endrom\endrom_0074C884_0074C92C.bin
        INCLUDE rawlabeled_74c92c.s
        INCBIN  build\endrom\endrom_0074CA2C_0074CA3C.bin
|unk_0874CA3C|
        INCBIN  baserom.gba_0x74ca3c_0x74ca60.extracted
        INCBIN  build\endrom\endrom_0074CA60_0074CA70.bin
|unk_0874CA70|
        INCBIN  baserom.gba_0x74ca70_0x74ca90.extracted
        INCBIN  build\endrom\endrom_0074CA90_0074CAA0.bin
|unk_0874CAA0|
        INCBIN  baserom.gba_0x74caa0_0x74cac4.extracted
        INCBIN  build\endrom\endrom_0074CAC4_0074CAD4.bin
|unk_0874CAD4|
        INCBIN  baserom.gba_0x74cad4_0x74caf4.extracted
        INCBIN  build\endrom\endrom_0074CAF4_0074CB04.bin
        INCLUDE rawlabeled_74cb04.s
        INCBIN  build\endrom\endrom_0074D044_0074D248.bin
        INCLUDE  raw_labeled_74d248.s
        INCBIN  build\endrom\endrom_0074F058_0074F080.bin
        INCLUDE rawlabeled_74f080.s
        INCBIN  build\endrom\endrom_0075023C_0075024C.bin
|unk_0875024C|
        INCLUDE fill_75024c.s
        INCBIN  build\endrom\endrom_00750254_00750270.bin
|unk_08750270|
        INCBIN  baserom.gba_0x750270_0x75027c.extracted
        INCBIN  build\endrom\endrom_0075027C_0075029C.bin
        INCLUDE rawlabeled_75029c.s
        INCBIN  build\endrom\endrom_00752D4C_00752D68.bin
|unk_08752D68|
        INCBIN  baserom.gba_0x752d68_0x752dac.extracted
        INCBIN  build\endrom\endrom_00752DAC_00752DEC.bin
        INCLUDE rawlabeled_752dec.s
        INCBIN  build\endrom\endrom_00752E18_00752E28.bin
|unk_08752E28|
        INCBIN  baserom.gba_0x752e28_0x752e68.extracted
        INCBIN  build\endrom\endrom_00752E68_00752E78.bin
|unk_08752E78|
        INCBIN  baserom.gba_0x752e78_0x752e9c.extracted
        INCBIN  build\endrom\endrom_00752E9C_00752EB8.bin
|unk_08752EB8|
        INCBIN  baserom.gba_0x752eb8_0x752ed4.extracted
        INCBIN  build\endrom\endrom_00752ED4_00752EF0.bin
        INCLUDE rawlabeled_752ef0.s
        INCBIN  build\endrom\endrom_00754910_00754958.bin
|unk_08754958|
        INCBIN  baserom.gba_0x754958_0x75495c.extracted
        INCBIN  build\endrom\endrom_0075495C_00754978.bin
        INCLUDE rawlabeled_754978.s
        INCBIN  build\endrom\endrom_00756A4C_00756A74.bin
|unk_08756A74|
        INCBIN  baserom.gba_0x756a74_0x756a94.extracted
        INCBIN  build\endrom\endrom_00756A94_00756AA4.bin
|unk_08756AA4|
        INCBIN  baserom.gba_0x756aa4_0x756ae4.extracted
        INCBIN  build\endrom\endrom_00756AE4_00756B10.bin
|unk_08756B10|
        INCBIN  baserom.gba_0x756b10_0x756b2c.extracted
        INCBIN  build\endrom\endrom_00756B2C_00756B3C.bin
|unk_08756B3C|
        INCBIN  baserom.gba_0x756b3c_0x756b58.extracted
        INCBIN  build\endrom\endrom_00756B58_00756B68.bin
        INCLUDE rawlabeled_756b68.s
        INCBIN  build\endrom\endrom_007572AC_007572C8.bin
|unk_087572C8|
        INCBIN  baserom.gba_0x7572c8_0x7572f0.extracted
        INCBIN  build\endrom\endrom_007572F0_00757324.bin
        INCLUDE rawlabeled_757324.s
        INCBIN  build\endrom\endrom_00757344_00757354.bin
|unk_08757354|
        INCBIN  baserom.gba_0x757354_0x757374.extracted
        INCBIN  build\endrom\endrom_00757374_00757390.bin
        INCLUDE rawlabeled_757390.s
        INCBIN  build\endrom\endrom_00757A40_00757A50.bin
|unk_08757A50|
        INCBIN  baserom.gba_0x757a50_0x757a74.extracted
        INCBIN  build\endrom\endrom_00757A74_00757A84.bin
|unk_08757A84|
        INCBIN  baserom.gba_0x757a84_0x757aa4.extracted
        INCBIN  build\endrom\endrom_00757AA4_00757AD0.bin
        INCLUDE rawlabeled_757ad0.s
        INCBIN  build\endrom\endrom_00757AD8_00757AE8.bin
|unk_08757AE8|
        INCBIN  baserom.gba_0x757ae8_0x757b04.extracted
        INCBIN  build\endrom\endrom_00757B04_00757B58.bin
        INCLUDE rawlabeled_757b58.s
        INCBIN  build\endrom\endrom_007581CC_007581E8.bin
        INCLUDE rawlabeled_7581e8.s
        INCBIN  build\endrom\endrom_0075916C_0075917C.bin
|unk_0875917C|
        INCBIN  baserom.gba_0x75917c_0x75918c.extracted
        INCBIN  build\endrom\endrom_0075918C_0075919C.bin
        INCLUDE rawlabeled_75919c.s
        INCBIN  build\endrom\endrom_007591DC_007591EC.bin
|unk_087591EC|
        INCBIN  baserom.gba_0x7591ec_0x759210.extracted
        INCBIN  build\endrom\endrom_00759210_00759220.bin
        INCLUDE rawlabeled_759220.s
        INCBIN  build\endrom\endrom_00759234_0075925C.bin
        INCLUDE rawlabeled_75925c.s
        INCBIN  build\endrom\endrom_007592AC_007592BC.bin
        INCLUDE rawlabeled_7592bc.s
        INCBIN  build\endrom\endrom_00759324_00759334.bin
        INCLUDE rawlabeled_759334.s
        INCBIN  build\endrom\endrom_00759354_0075939C.bin
|unk_0875939C|
        INCBIN  baserom.gba_0x75939c_0x7593bc.extracted
        INCBIN  build\endrom\endrom_007593BC_007593CC.bin
        INCLUDE rawlabeled_7593cc.s
        INCBIN  build\endrom\endrom_007593EC_007593FC.bin
|unk_087593FC|
        INCBIN  baserom.gba_0x7593fc_0x759418.extracted
        INCBIN  build\endrom\endrom_00759418_00759440.bin
|unk_08759440|
        INCBIN  baserom.gba_0x759440_0x759460.extracted
        INCBIN  build\endrom\endrom_00759460_00759480.bin
|unk_08759480|
        INCBIN  baserom.gba_0x759480_0x7594a0.extracted
        INCBIN  build\endrom\endrom_007594A0_007594B0.bin
|unk_087594B0|
        INCBIN  baserom.gba_0x7594b0_0x7594d0.extracted
        INCBIN  build\endrom\endrom_007594D0_007594EC.bin
|unk_087594EC|
        INCBIN  baserom.gba_0x7594ec_0x7594f0.extracted
        INCBIN  build\endrom\endrom_007594F0_00759510.bin
|unk_08759510|
        INCBIN  baserom.gba_0x759510_0x759620.extracted
|unk_08759620|
        INCBIN  build\endrom\endrom_00759620_00759680.bin
|unk_08759680|
        INCBIN  baserom.gba_0x759680_0x75a0e9.extracted
        INCLUDE fill_75a0e9.s
|unk_0875A22F|
        INCBIN  baserom.gba_0x75a22f_0x75a2a0.extracted
        INCLUDE fill_75a2a0.s
|unk_0875A6A8|
        INCBIN  baserom.gba_0x75a6a8_0x75a6dc.extracted
        INCBIN  build\endrom\endrom_0075A6DC_0075A714.bin
        INCLUDE rawlabeled_75a714.s
        INCBIN  build\endrom\endrom_0075A718_0075A738.bin
        INCLUDE rawlabeled_75a738.s
        INCBIN  build\endrom\endrom_0076CCD4_0076CCE4.bin
        INCLUDE rawlabeled_76cce4.s
        INCBIN  build\endrom\endrom_0077AE68_0077AE84.bin
|unk_0877AE84|
        INCBIN  baserom.gba_0x77ae84_0x77aec0.extracted
        INCBIN  build\endrom\endrom_0077AEC0_0077AED0.bin
|unk_0877AED0|
        INCBIN  baserom.gba_0x77aed0_0x77af0c.extracted
        INCBIN  build\endrom\endrom_0077AF0C_0077AF34.bin
        INCLUDE rawlabeled_77af34.s
        INCBIN  build\endrom\endrom_0077AF50_0077AF78.bin
        INCLUDE rawlabeled_77af78.s
        INCBIN  build\endrom\endrom_0077AFC0_0077AFDC.bin
        INCLUDE rawlabeled_77afdc.s
        INCBIN  build\endrom\endrom_0077B03C_0077B04C.bin
|unk_0877B04C|
        INCBIN  baserom.gba_0x77b04c_0x77b070.extracted
        INCBIN  build\endrom\endrom_0077B070_0077B0B0.bin
        INCLUDE rawlabeled_77b0b0.s
        INCBIN  build\endrom\endrom_0077B0F8_0077B138.bin
|unk_0877B138|
        DCD	|unk_030019A4|
        DCD	|unk_03001990|
        INCBIN  build\endrom\endrom_0077B140_0077B16C.bin
        INCLUDE rawlabeled_77b16c.s
        INCBIN  build\endrom\endrom_0077B170_0077B180.bin
        INCLUDE rawlabeled_77b180.s
        INCBIN  build\endrom\endrom_0077B1B0_0077B1C0.bin
|unk_0877B1C0|
        INCBIN  baserom.gba_0x77b1c0_0x77b1e4.extracted
        INCBIN  build\endrom\endrom_0077B1E4_0077B200.bin
        INCLUDE rawlabeled_77b200.s
        INCBIN  build\endrom\endrom_0077C47C_0077C48C.bin
        INCLUDE rawlabeled_77c48c.s
        INCBIN  build\endrom\endrom_0077C498_0077C4D4.bin
|unk_0877C4D4|
        INCBIN  baserom.gba_0x77c4d4_0x77c4f4.extracted
        INCBIN  build\endrom\endrom_0077C4F4_0077C510.bin
|unk_0877C510|
        INCBIN  baserom.gba_0x77c510_0x77c5a4.extracted
        INCBIN  build\endrom\endrom_0077C5A4_0079B704.bin
        INCBIN  build\endrom\endrom_0079B704_0079BF2C.bin
        INCBIN  build\endrom\endrom_0079BF2C_007B5B64.bin
        INCLUDE  raw_labeled_7b5b64.s
|sub_087b79a4|
        STMFD    sp!,{r8,sb,sl,fp}
        MOV      ip,#REG_DISPCNT
        LDR      fp,[pc,#0x2c]
        ADD      sl,fp,#0x28
        MOV      sb,#1
        MOV      r8,#0
        STRB     r8,[ip,#0x208]
        LDMIA    sl,{r0,r1}
        STMIA    sl!,{r1}
        STMIA    sl!,{r0}
        LDRB     r0,[fp,#5]
        STRB     r8,[fp,#5]
        STRB     sb,[ip,#0x208]
        LDMFD    sp!,{r8,sb,sl,fp}
        BX       lr
|dat_087b79e0|
        DCD      0x03004a9c
|sub_087b79e4|
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp,lr}
        MOV      r5,#8
        MOV      sl,#0
        MOV      ip,#1
        B        |loc_087b7a08|
|loc_087b79f8|
        MOV      r8,r3
        BL       |loc_087b7c30|
        ADD      r7,r7,r4
|loc_087b7a04|
        STRB     r7,[r0],#1
|loc_087b7a08|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b79f8|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b7b20|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BLO      |loc_087b7ad4|
        MOV      r8,#4
        BL       |loc_087b7c30|
        SUBS     r7,r7,#1
        BEQ      |loc_087b7a04|
        BPL      |loc_087b7acc|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BLO      |loc_087b7a9c|
|loc_087b7a6c|
        MOV      sb,#0x100
|loc_087b7a70|
        MOV      r8,#8
        BL       |loc_087b7c30|
        STRB     r7,[r0],#1
        SUBS     sb,sb,#1
        BNE      |loc_087b7a70|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b7a6c|
        B        |loc_087b7a08|
|loc_087b7a9c|
        MOV      r4,#0
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      r3,r4,#7
        CMP      r3,#8
        BEQ      |loc_087b7a08|
        MOV      r8,#8
        BL       |loc_087b7c30|
        MOV      r4,r7
        B        |loc_087b7a08|
|loc_087b7acc|
        LDRB     r7,[r0,-r7]
        B        |loc_087b7a04|
|loc_087b7ad4|
        MOV      r8,#7
        BL       |loc_087b7c30|
        CMP      r7,#0
        BEQ      |loc_087b7b00|
        MOV      ip,r7
        MOV      r8,#2
        BL       |loc_087b7c30|
        ADD      sb,r7,#2
        CMP      ip,#1
        BNE      |loc_087b7c08|
        B        |loc_087b7c1c|
|loc_087b7b00|
        MOV      r8,#2
        BL       |loc_087b7c30|
        CMP      r7,#0
        BEQ      |loc_087b7c78|
        ADD      r8,r7,#3
        BL       |loc_087b7c30|
        MOV      r5,r7
        B        |loc_087b7a08|
|loc_087b7b20|
        MOV      sb,#1
|loc_087b7b24|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      sb,sb,sb
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b7b24|
        CMP      sb,#2
        BNE      |loc_087b7b8c|
        MOV      sb,#1
|loc_087b7b58|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      sb,sb,sb
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b7b58|
        CMP      ip,#1
        BNE      |loc_087b7c08|
        B        |loc_087b7c1c|
|loc_087b7b8c|
        SUB      sb,sb,#3
        MOV      r8,r5
        BL       |loc_087b7c30|
        ADD      ip,r7,sb,lsl r5
        MOV      sb,#1
|loc_087b7ba0|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      sb,sb,sb
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b7ba0|
        CMP      ip,#0x10000
        ADDHS    sb,sb,#3
        BHS      |loc_087b7c08|
        LDR      r8,[pc,#0xf0]
        CMP      ip,r8
        ADDHS    sb,sb,#2
        BHS      |loc_087b7c08|
        LDR      r8,[pc,#0xe4]
        CMP      ip,r8
        ADDHS    sb,sb,#1
        BHS      |loc_087b7c08|
        CMP      ip,#0x7f
        BHI      |loc_087b7c08|
        ADD      sb,sb,#4
        CMP      ip,#1
        BEQ      |loc_087b7c1c|
|loc_087b7c08|
        LDRB     r8,[r0,-ip]
        STRB     r8,[r0],#1
        SUBS     sb,sb,#1
        BNE      |loc_087b7c08|
        B        |loc_087b7a08|
|loc_087b7c1c|
        LDRB     r8,[r0,-ip]
|loc_087b7c20|
        STRB     r8,[r0],#1
        SUBS     sb,sb,#1
        BNE      |loc_087b7c20|
        B        |loc_087b7a08|
|loc_087b7c30|
        CMP      sl,#0
        LDREQ    r6,[r1],#4
        MOVEQ    sl,#0x20
        MOV      fp,r8
        CMP      fp,sl
        MOVHI    fp,sl
        RSB      r7,fp,#0x20
        MOV      r7,r6,LSR r7
        MOV      r6,r6,LSL fp
        SUB      sl,sl,fp
        SUBS     r8,r8,fp
        BXEQ     lr
        LDR      r6,[r1],#4
        RSB      sl,r8,#0x20
        MOV      fp,r6,LSR sl
        ADD      r7,fp,r7,lsl r8
        MOV      r6,r6,LSL r8
        BX       lr
|loc_087b7c78|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp,lr}
        BX       lr
        STMFD    sp!,{r4,r5,r6}
        MOV      ip,#0xff
|loc_087b7c88|
        LDR      r4,[r1],#4
        ANDS     r5,ip,r4,lsr #24
        LDRNEB   r5,[r2,r5]
        ANDS     r6,ip,r4,lsr #16
        LDRNEB   r6,[r2,r6]
        ORR      r5,r6,r5,lsl #8
        ANDS     r6,ip,r4,lsr #8
        LDRNEB   r6,[r2,r6]
        ORR      r5,r6,r5,lsl #8
        ANDS     r6,ip,r4
        LDRNEB   r6,[r2,r6]
        ORR      r5,r6,r5,lsl #8
        STR      r5,[r0],#4
        SUBS     r3,r3,#4
        BNE      |loc_087b7c88|
        LDMFD    sp!,{r4,r5,r6}
        BX       lr
|dat_087b7ccc|
        DCD      0x000037ff
        DCD      0x0000027f
|sub_087b7cd4|
        STMFD    sp!,{r4,r5}
        LDR      r2,[r0,#0x30]
        LDR      r0,[r0,#0x24]
        SUB      r0,r0,#4
        MOV      r4,#0xff
|loc_087b7ce8|
        SUBS     r2,r2,#4
        BMI      |loc_087b7d24|
        ADD      r0,r0,#4
        LDR      r3,[r1],#4
        CMP      r3,#0
        BEQ      |loc_087b7ce8|
        ANDS     r5,r4,r3
        STRNEB   r5,[r0]
        ANDS     r5,r4,r3,lsr #8
        STRNEB   r5,[r0,#1]
        ANDS     r5,r4,r3,lsr #16
        STRNEB   r5,[r0,#2]
        ANDS     r5,r4,r3,lsr #24
        STRNEB   r5,[r0,#3]
        B        |loc_087b7ce8|
|loc_087b7d24|
        LDMFD    sp!,{r4,r5}
        BX       lr
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        LDR      r2,[r0,#0x24]
        LDR      r3,[r0,#0x28]
        LDR      r4,[r0,#0x2c]
|loc_087b7d3c|
        MOV      r5,r3
        MOV      r6,r2
|loc_087b7d44|
        MOV      r7,r6
        LDMIA    r7,{r8,sb}
        ADD      r7,r7,r3
        LDMIA    r7,{sl,fp}
        ADD      r7,r7,r3
        STMIA    r1!,{r8,sb,sl,fp}
        LDMIA    r7,{r8,sb}
        ADD      r7,r7,r3
        LDMIA    r7,{sl,fp}
        ADD      r7,r7,r3
        STMIA    r1!,{r8,sb,sl,fp}
        LDMIA    r7,{r8,sb}
        ADD      r7,r7,r3
        LDMIA    r7,{sl,fp}
        ADD      r7,r7,r3
        STMIA    r1!,{r8,sb,sl,fp}
        LDMIA    r7,{r8,sb}
        ADD      r7,r7,r3
        LDMIA    r7,{sl,fp}
        ADD      r7,r7,r3
        STMIA    r1!,{r8,sb,sl,fp}
        ADD      r6,r6,#8
        SUBS     r5,r5,#8
        BNE      |loc_087b7d44|
        ADD      r2,r2,r3,lsl #3
        SUBS     r4,r4,#8
        BNE      |loc_087b7d3c|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        BX       lr
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        LDMIA    r2,{r3,r4,r5,r6}
        LDR      r7,[r0,#0x24]
        LDR      r8,[r0,#0x28]
        MLA      r1,r8,r4,r1
        ADD      r1,r1,r3,lsl #3
        MLA      r7,r8,r4,r7
        ADD      r7,r7,r3
        SUB      sb,r6,r4
        SUB      sl,r5,r3
        SUB      fp,r8,sl
|loc_087b7de4|
        MOV      r2,r7
        MOV      r3,sl
|loc_087b7dec|
        MOV      r0,r2
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        ADD      r2,r2,#8
        SUBS     r3,r3,#8
        BNE      |loc_087b7dec|
        ADD      r7,r7,r8,lsl #3
        ADD      r1,r1,fp,lsl #3
        SUBS     sb,sb,#8
        BNE      |loc_087b7de4|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        BX       lr
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        LDMIA    r2,{r3,r4,r5,r6}
        LDR      r7,[r0,#0x24]
        LDR      r8,[r0,#0x28]
        MLA      r7,r8,r4,r7
        ADD      r7,r7,r3
        SUB      sb,r6,r4
        SUB      sl,r5,r3
        SUB      fp,r8,sl
|loc_087b7e88|
        MOV      r2,r7
        MOV      r3,sl
|loc_087b7e90|
        MOV      r0,r2
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        LDMIA    r0,{r4,r5}
        ADD      r0,r0,r8
        LDMIA    r0,{r6,ip}
        ADD      r0,r0,r8
        STMIA    r1!,{r4,r5,r6,ip}
        ADD      r2,r2,#8
        SUBS     r3,r3,#8
        BNE      |loc_087b7e90|
        ADD      r7,r7,r8,lsl #3
        SUBS     sb,sb,#8
        BNE      |loc_087b7e88|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        BX       lr
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp,lr}
        SUB      sp,sp,#0x30
        MOV      lr,r2
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMULL    r7,r8,r4,r3
        SMULL    sb,sl,r5,r3
        SMULL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        MOV      r4,r7,LSR #0xa
        MOV      r5,sb,LSR #0xa
        MOV      r6,fp,LSR #0xa
        ADD      r4,r4,r8,lsl #22
        ADD      r5,r5,sl,lsl #22
        ADD      r6,r6,ip,lsl #22
        STMIA    sp,{r4,r5,r6}
        MOV      lr,r2
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMULL    r7,r8,r4,r3
        SMULL    sb,sl,r5,r3
        SMULL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        MOV      r4,r7,LSR #0xa
        MOV      r5,sb,LSR #0xa
        MOV      r6,fp,LSR #0xa
        ADD      r4,r4,r8,lsl #22
        ADD      r5,r5,sl,lsl #22
        ADD      r6,r6,ip,lsl #22
        ADD      lr,sp,#0xc
        STMIA    lr,{r4,r5,r6}
        MOV      lr,r2
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMULL    r7,r8,r4,r3
        SMULL    sb,sl,r5,r3
        SMULL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        MOV      r4,r7,LSR #0xa
        MOV      r5,sb,LSR #0xa
        MOV      r6,fp,LSR #0xa
        ADD      r4,r4,r8,lsl #22
        ADD      r5,r5,sl,lsl #22
        ADD      r6,r6,ip,lsl #22
        ADD      lr,sp,#0x18
        STMIA    lr,{r4,r5,r6}
        MOV      lr,r2
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMULL    r7,r8,r4,r3
        SMULL    sb,sl,r5,r3
        SMULL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        LDR      r3,[r1],#4
        LDMIA    lr!,{r4,r5,r6}
        SMLAL    r7,r8,r4,r3
        SMLAL    sb,sl,r5,r3
        SMLAL    fp,ip,r6,r3
        LDMIA    lr!,{r4,r5,r6}
        ADD      r4,r4,r7,lsr #10
        ADD      r5,r5,sb,lsr #10
        ADD      r6,r6,fp,lsr #10
        ADD      r4,r4,r8,lsl #22
        ADD      r5,r5,sl,lsl #22
        ADD      r6,r6,ip,lsl #22
        ADD      lr,sp,#0x24
        STMIA    lr,{r4,r5,r6}
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb}
        STMIA    r0!,{r4,r5,r6,r7,r8,sb}
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb}
        STMIA    r0!,{r4,r5,r6,r7,r8,sb}
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp,lr}
        BX       lr
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        LDR      r3,[r1]
        LDMIA    r2!,{r4,r5,r6}
        SMULL    r7,r8,r3,r4
        SMULL    sb,sl,r3,r5
        SMULL    fp,ip,r3,r6
        LDR      r3,[r1,#4]
        LDMIA    r2!,{r4,r5,r6}
        SMLAL    r7,r8,r3,r4
        SMLAL    sb,sl,r3,r5
        SMLAL    fp,ip,r3,r6
        LDR      r3,[r1,#8]
        LDMIA    r2!,{r4,r5,r6}
        SMLAL    r7,r8,r3,r4
        SMLAL    sb,sl,r3,r5
        SMLAL    fp,ip,r3,r6
        LDMIA    r2!,{r4,r5,r6}
        ADD      r4,r4,r7,lsr #10
        ADD      r4,r4,r8,lsl #22
        ADD      r5,r5,sb,lsr #10
        ADD      r5,r5,sl,lsl #22
        ADD      r6,r6,fp,lsr #10
        ADD      r6,r6,ip,lsl #22
        STMIA    r0,{r4,r5,r6}
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp}
        BX       lr
        CMP      r2,#0x20
        BLT      |loc_087b8138|
        STMFD    sp!,{r4,r5,r6,r7,r8,sb}
        SUB      r2,r2,#0x20
|loc_087b811c|
        LDMIA    r1!,{r3,r4,r5,r6,r7,r8,sb,ip}
        STMIA    r0!,{r3,r4,r5,r6,r7,r8,sb,ip}
        SUBS     r2,r2,#0x20
        BGT      |loc_087b811c|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb}
        ADDS     r2,r2,#0x20
        BXEQ     lr
|loc_087b8138|
        LDR      r3,[r1],#4
        STR      r3,[r0],#4
        SUBS     r2,r2,#4
        BGT      |loc_087b8138|
        BX       lr
        CMP      r2,#0x20
        BLT      |loc_087b8190|
        STMFD    sp!,{r4,r5,r6,r7,r8}
        MOV      r3,r1
        MOV      r4,r1
        MOV      r5,r1
        MOV      r6,r1
        MOV      r7,r1
        MOV      r8,r1
        MOV      ip,r1
        SUB      r2,r2,#0x20
|loc_087b8178|
        STMIA    r0!,{r1,r3,r4,r5,r6,r7,r8,ip}
        SUBS     r2,r2,#0x20
        BGT      |loc_087b8178|
        LDMFD    sp!,{r4,r5,r6,r7,r8}
        ADDS     r2,r2,#0x20
        BXEQ     lr
|loc_087b8190|
        STR      r1,[r0],#4
        SUBS     r2,r2,#4
        BGT      |loc_087b8190|
        BX       lr
        RSB      r3,r2,#0x10
        AND      r3,r3,#0xe
        ADD      pc,pc,r3,lsl #2
        MOV      r0,r0
|loc_087b81b0|
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        LDRH     r3,[r1],#2
        STRH     r3,[r0],#2
        SUBS     r2,r2,#0x10
        BGT      |loc_087b81b0|
        BX       lr
|loc_087b81fc|
        STRH     r1,[r0],#2
        SUBS     r2,r2,#2
        BGT      |loc_087b81fc|
        BX       lr
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl}
        LDMIA    r0,{r3,r4,r5,r6}
        MOV      r7,r3,LSL #0x12
        MOV      r8,r4,LSL #0x12
        ADD      r3,r5,r3,asr #14
        MOV      r4,r4,ASR #0xe
        TST      r2,#1
        BEQ      |loc_087b824c|
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        LDR      r5,[r1]
        MLA      r5,r6,r0,r5
        STR      r5,[r1],#4
        SUBS     r2,r2,#1
        BEQ      |loc_087b832c|
|loc_087b824c|
        CMP      r4,#0
        BEQ      |loc_087b8334|
        TST      r2,#2
        BEQ      |loc_087b828c|
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        LDRSB    r5,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        LDMIA    r1,{sb,ip}
        MLA      sb,r6,r0,sb
        MLA      ip,r6,r5,ip
        STMIA    r1!,{sb,ip}
        SUBS     r2,r2,#2
        BEQ      |loc_087b832c|
|loc_087b828c|
        TST      r2,#4
        BNE      |loc_087b82dc|
|loc_087b8294|
        LDMIA    r1,{r5,sb,sl,ip}
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      r5,r6,r0,r5
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      sb,r6,r0,sb
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      sl,r6,r0,sl
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      ip,r6,r0,ip
        STMIA    r1!,{r5,sb,sl,ip}
|loc_087b82dc|
        LDMIA    r1,{r5,sb,sl,ip}
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      r5,r6,r0,r5
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      sb,r6,r0,sb
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      sl,r6,r0,sl
        LDRSB    r0,[r3]
        ADDS     r7,r7,r8
        ADC      r3,r3,r4
        MLA      ip,r6,r0,ip
        STMIA    r1!,{r5,sb,sl,ip}
        SUBS     r2,r2,#8
        BHI      |loc_087b8294|
|loc_087b832c|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl}
        BX       lr
|loc_087b8334|
        LDRSB    r0,[r3]
        TST      r2,#2
        BEQ      |loc_087b8368|
        LDMIA    r1,{sb,ip}
        MLA      sb,r6,r0,sb
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        MLA      ip,r6,r0,ip
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        STMIA    r1!,{sb,ip}
        SUBS     r2,r2,#2
        BEQ      |loc_087b832c|
|loc_087b8368|
        TST      r2,#4
        BNE      |loc_087b83a8|
|loc_087b8370|
        LDMIA    r1,{r4,r5,sb,ip}
        MLA      r4,r6,r0,r4
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        MLA      r5,r6,r0,r5
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        MLA      sb,r6,r0,sb
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        MLA      ip,r6,r0,ip
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        STMIA    r1!,{r4,r5,sb,ip}
|loc_087b83a8|
        LDMIA    r1,{r4,r5,sb,ip}
        MLA      r4,r6,r0,r4
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        MLA      r5,r6,r0,r5
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        MLA      sb,r6,r0,sb
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        MLA      ip,r6,r0,ip
        ADDS     r7,r7,r8
        LDRHSSB  r0,[r3,#1]!
        STMIA    r1!,{r4,r5,sb,ip}
        SUBS     r2,r2,#8
        BHI      |loc_087b8370|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl}
        BX       lr
        STMFD    sp!,{r4,r5,r6,r7,r8}
        MOV      r8,#0
        MOV      ip,#0
|loc_087b83fc|
        LDMIA    r2,{r4,r6}
        STMIA    r2!,{r8,ip}
        MOV      r5,r4,ASR #0x16
        MOV      r7,r6,ASR #0x16
        MOV      r4,r4,LSL #0x10
        MOV      r6,r6,LSL #0x10
        MOV      r4,r4,ASR #0x16
        MOV      r6,r6,ASR #0x16
        CMP      r4,#0x7f
        MOVGT    r4,#0x7f
        CMN      r4,#0x80
        MVNLT    r4,#0x7f
        CMP      r5,#0x7f
        MOVGT    r5,#0x7f
        CMN      r5,#0x80
        MVNLT    r5,#0x7f
        CMP      r6,#0x7f
        MOVGT    r6,#0x7f
        CMN      r6,#0x80
        MVNLT    r6,#0x7f
        CMP      r7,#0x7f
        MOVGT    r7,#0x7f
        CMN      r7,#0x80
        MVNLT    r7,#0x7f
        AND      r4,r4,#0xff
        ORR      r4,r4,r6,lsl #8
        AND      r5,r5,#0xff
        ORR      r5,r5,r7,lsl #8
        STRH     r4,[r0],#2
        STRH     r5,[r1],#2
        SUBS     r3,r3,#2
        BGT      |loc_087b83fc|
        LDMFD    sp!,{r4,r5,r6,r7,r8}
        BX       lr
        LDR      r0,[pc,#0x78]
        LDR      r1,[r0,#4]
        ADD      r1,r1,#0x10
        STR      r1,[r0,#4]
        MOVS     ip,r1,LSL #0x17
        BNE      |loc_087b84d0|
        MOVS     r2,r1,LSL #0x16
        MOV      r2,#EWRAM_BASE
        BPL      |loc_087b84b8|
        STR      ip,[r3,#-0x130]!
        ADD      r2,r2,#0x400
        SUB      ip,r3,#0x2c
        B        |loc_087b84c4|
|loc_087b84b8|
        STR      ip,[r0,#4]
        STR      ip,[r3,#-0x13c]!
        SUB      ip,r3,#0x24
|loc_087b84c4|
        STMDB    r3,{r2,ip}
        LDR      ip,[pc,#0x38]
        STR      ip,[r3]
|loc_087b84d0|
        LDR      ip,[r0,#8]
        SUB      ip,ip,r1
        MOV      ip,ip,LSL #0x16
        CMP      ip,#0x18000000
        BXNE     r4
        LDRB     ip,[r0]
        CMP      ip,#0
        BXNE     r4
        MRS      r2,CPSR
        BIC      r2,r2,#0x80
        MSR      CPSR_c,r2
        LDR      r1,[pc,#8]
        BX       r1
|dat_087b8504|
        DCD      0x03003898
        DCD      0xf6400004
        DCD      0x0803f297
|sub_087b8510|
        MOV      r3,#REG_DISPCNT
        LDR      r2,[r3,#0x200]!
        LDRH     r1,[r3,#8]
        MRS      r0,SPSR
        STMFD    sp!,{r0,r1,r2,r3,r4,r5,lr}
        MOV      r0,#1
        STRH     r0,[r3,#8]
        AND      r1,r2,r2,lsr #16
        MOV      ip,#0x9f
        MOV      r4,#0x28
        ANDS     r0,r1,#0x400
        BNE      |loc_087b85e4|
        MOV      ip,#0x1f
        MOV      r4,#0x1c
        ANDS     r0,r1,#0x80
        BNE      |loc_087b85e0|
        MOV      r4,#0x18
        ANDS     r0,r1,#0x40
        BNE      |loc_087b85e0|
        MOV      r4,#0
        ANDS     r0,r1,#1
        BNE      |loc_087b85e0|
        MOV      r4,#4
        ANDS     r0,r1,#2
        BNE      |loc_087b85e0|
        MOV      r4,#8
        ANDS     r0,r1,#4
        BNE      |loc_087b85e0|
        MOV      r4,#0xc
        ANDS     r0,r1,#8
        BNE      |loc_087b85e0|
        MOV      r4,#0x10
        ANDS     r0,r1,#0x10
        BNE      |loc_087b85e0|
        MOV      r4,#0x14
        ANDS     r0,r1,#0x20
        BNE      |loc_087b85e0|
        MOV      r4,#0x20
        ANDS     r0,r1,#0x100
        BNE      |loc_087b85e0|
        MOV      r4,#0x24
        ANDS     r0,r1,#0x200
        BNE      |loc_087b85e0|
        MOV      r4,#0x2c
        ANDS     r0,r1,#0x800
        BNE      |loc_087b85e0|
        MOV      r4,#0x30
        ANDS     r0,r1,#0x1000
        BNE      |loc_087b85e0|
        ANDS     r0,r1,#0x2000
        BEQ      |loc_087b8628|
|loc_087b85dc|
        B        |loc_087b85dc|
|loc_087b85e0|
        BIC      r2,r2,r0
|loc_087b85e4|
        ORR      r2,r2,r0,lsl #16
        STR      r2,[r3]
        LDR      r1,[pc,#0x4c]
        LDRH     r5,[r1,#0x38]
        ORR      r5,r5,r0
        STRH     r5,[r1,#0x38]
        MRS      r5,CPSR
        BIC      r0,r5,#0x80
        ORR      r0,r0,ip
        MSR      CPSR_c,r0
        STR      lr,[sp,#-4]!
        ADD      lr,pc,#0x25
        LDR      r0,[r1,r4]
        ADD      r4,pc,#0
        BX       r0
        DCB      0x04,0xe0,0x9d,0xe4
        MSR      CPSR_fsxc,r5
|loc_087b8628|
        LDMFD    sp!,{r0,r1,r2,r3,r4,r5,lr}
        STRH     r2,[r3]
        STRH     r1,[r3,#8]
        MSR      SPSR_fsxc,r0
        BX       lr
        ANDEQ    r4,r0,r0,lsr #14
|dat_087b8640|
        DCD      0x03000fb0
|sub_087b8644|
        STMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp,lr}
        MOV      r5,#8
        MOV      sl,#0
        MOV      ip,#1
        B        |loc_087b866c|
|loc_087b8658|
        MOV      r8,r3
        BL       |loc_087b8898|
        ADD      r7,r7,r4
        LDRB     r7,[r2,r7]
|loc_087b8668|
        STRB     r7,[r0],#1
|loc_087b866c|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b8658|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b8788|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BLO      |loc_087b873c|
        MOV      r8,#4
        BL       |loc_087b8898|
        SUBS     r7,r7,#1
        BEQ      |loc_087b8668|
        BPL      |loc_087b8734|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BLO      |loc_087b8704|
|loc_087b86d0|
        MOV      sb,#0x100
|loc_087b86d4|
        MOV      r8,#8
        BL       |loc_087b8898|
        LDRB     r7,[r2,r7]
        STRB     r7,[r0],#1
        SUBS     sb,sb,#1
        BNE      |loc_087b86d4|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b86d0|
        B        |loc_087b866c|
|loc_087b8704|
        MOV      r4,#0
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      r3,r4,#7
        CMP      r3,#8
        BEQ      |loc_087b866c|
        MOV      r8,#8
        BL       |loc_087b8898|
        MOV      r4,r7
        B        |loc_087b866c|
|loc_087b8734|
        LDRB     r7,[r0,-r7]
        B        |loc_087b8668|
|loc_087b873c|
        MOV      r8,#7
        BL       |loc_087b8898|
        CMP      r7,#0
        BEQ      |loc_087b8768|
        MOV      ip,r7
        MOV      r8,#2
        BL       |loc_087b8898|
        ADD      sb,r7,#2
        CMP      ip,#1
        BNE      |loc_087b8870|
        B        |loc_087b8884|
|loc_087b8768|
        MOV      r8,#2
        BL       |loc_087b8898|
        CMP      r7,#0
        BEQ      |loc_087b88e0|
        ADD      r8,r7,#3
        BL       |loc_087b8898|
        MOV      r5,r7
        B        |loc_087b866c|
|loc_087b8788|
        MOV      sb,#1
|loc_087b878c|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      sb,sb,sb
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b878c|
        CMP      sb,#2
        BNE      |loc_087b87f4|
        MOV      sb,#1
|loc_087b87c0|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      sb,sb,sb
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b87c0|
        CMP      ip,#1
        BNE      |loc_087b8870|
        B        |loc_087b8884|
|loc_087b87f4|
        SUB      sb,sb,#3
        MOV      r8,r5
        BL       |loc_087b8898|
        ADD      ip,r7,sb,lsl r5
        MOV      sb,#1
|loc_087b8808|
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        ADC      sb,sb,sb
        SUBS     sl,sl,#1
        LDRMI    r6,[r1],#4
        MOVMI    sl,#0x1f
        ADDS     r6,r6,r6
        BHS      |loc_087b8808|
        CMP      ip,#0x10000
        ADDHS    sb,sb,#3
        BHS      |loc_087b8870|
        LDR      r8,[pc,#0xa4]
        CMP      ip,r8
        ADDHS    sb,sb,#2
        BHS      |loc_087b8870|
        LDR      r8,[pc,#0x98]
        CMP      ip,r8
        ADDHS    sb,sb,#1
        BHS      |loc_087b8870|
        CMP      ip,#0x7f
        BHI      |loc_087b8870|
        ADD      sb,sb,#4
        CMP      ip,#1
        BEQ      |loc_087b8884|
|loc_087b8870|
        LDRB     r8,[r0,-ip]
        STRB     r8,[r0],#1
        SUBS     sb,sb,#1
        BNE      |loc_087b8870|
        B        |loc_087b866c|
|loc_087b8884|
        LDRB     r8,[r0,-ip]
|loc_087b8888|
        STRB     r8,[r0],#1
        SUBS     sb,sb,#1
        BNE      |loc_087b8888|
        B        |loc_087b866c|
|loc_087b8898|
        CMP      sl,#0
        LDREQ    r6,[r1],#4
        MOVEQ    sl,#0x20
        MOV      fp,r8
        CMP      fp,sl
        MOVHI    fp,sl
        RSB      r7,fp,#0x20
        MOV      r7,r6,LSR r7
        MOV      r6,r6,LSL fp
        SUB      sl,sl,fp
        SUBS     r8,r8,fp
        BXEQ     lr
        LDR      r6,[r1],#4
        RSB      sl,r8,#0x20
        MOV      fp,r6,LSR sl
        ADD      r7,fp,r7,lsl r8
        MOV      r6,r6,LSL r8
        BX       lr
|loc_087b88e0|
        LDMFD    sp!,{r4,r5,r6,r7,r8,sb,sl,fp,lr}
        BX       lr
|dat_087b88e8|
|unk_087B88E8|
; cited by 0x087B883C (a pc-relative load targets 0x087B88E8)
        INCBIN	baserom.gba_0x7b88e8_0x7b89a8.extracted
		GBLA	fill_0x7b89a8
fill_0x7b89a8	SETA	292440
		WHILE	fill_0x7b89a8 > 0
		DCB		0xFF
fill_0x7b89a8	SETA	fill_0x7b89a8 - 1
		WEND
	END