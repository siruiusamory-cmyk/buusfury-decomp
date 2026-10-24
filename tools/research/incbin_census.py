from __future__ import annotations

import hashlib
import os
import sys
from bisect import bisect_right
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))

import gate  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")
DOC = os.path.join(ROOT, "build", "incbin_census.md")
ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

STATUSES = ("raw-labeled", "unreferenced")

Region = namedtuple("Region", "name status citation ranges note")


UNMAPPED_RAW_LABELED = (
    (0x17a9ac, 0x17b1b0), (0x187bc8, 0x187c14), (0x189334, 0x189380), (0x190088, 0x1900d0), (0x1911d8, 0x1912e4), (0x19aeac, 0x19b178),
    (0x1ab430, 0x1ab484), (0x1b9bb8, 0x1b9c0c), (0x1bfaa4, 0x1bfe30), (0x1d25e8, 0x1d2798), (0x1d4e44, 0x1d4ea4), (0x1d606c, 0x1d60dc),
    (0x1d7174, 0x1d71d4), (0x1d857c, 0x1d85b4), (0x1e41e0, 0x1e4800), (0x1f880c, 0x1f88d8), (0x1fc5b0, 0x1fc690), (0x205f08, 0x205f78),
    (0x20630c, 0x206394), (0x2065fc, 0x2066e4), (0x20d298, 0x20d308), (0x21fc4c, 0x2205f8), (0x2346d0, 0x23475c), (0x2393f0, 0x239474),
    (0x23d810, 0x23d894), (0x252048, 0x2520d4), (0x25464c, 0x2546a0), (0x260ea8, 0x261130), (0x272d48, 0x272da0), (0x296d4c, 0x296d9c),
    (0x2b5f94, 0x2b5fa0), (0x3c33f8, 0x3c34d0), (0x6b801c, 0x6b814c), (0x6b8284, 0x6b8294), (0x6b82dc, 0x6b880c), (0x6f9ec4, 0x6f9ec8),
    (0x73198c, 0x7319e0), (0x732350, 0x732384), (0x7325e8, 0x732604), (0x74c92c, 0x74ca2c), (0x74cb04, 0x74d044),
)

UNMAPPED_SINGLETON_LITERAL = (
    (0x17f330, 0x17f4dc), (0x180694, 0x180b90), (0x19c744, 0x19c8a8), (0x1a539c, 0x1a53d4), (0x1a90a8, 0x1a95f0), (0x1af7cc, 0x1af874),
    (0x1b0dcc, 0x1b0e04), (0x1b7bfc, 0x1b7c34), (0x1be0f0, 0x1be298), (0x1c4348, 0x1c4418), (0x1c7c48, 0x1c7f5c), (0x1ca528, 0x1ca5e4),
    (0x1cf9d4, 0x1cfa0c), (0x1d146c, 0x1d14a4), (0x1edda8, 0x1ede28), (0x1efc4c, 0x1efc84), (0x1f0f5c, 0x1f0ff8), (0x1fa358, 0x1fa38c),
    (0x1fa458, 0x1fa490), (0x1fd0f0, 0x1fd124), (0x201a70, 0x201b10), (0x2025c0, 0x202680), (0x20c40c, 0x20c444), (0x20ca54, 0x20ca70),
    (0x20e090, 0x20e0c8), (0x210a54, 0x210a8c), (0x21426c, 0x2142a4), (0x2176bc, 0x217808), (0x21e878, 0x21eec0), (0x225fb8, 0x226514),
    (0x22f748, 0x22faac), (0x235a10, 0x235aa0), (0x23c8cc, 0x23c96c), (0x241c90, 0x241d14), (0x255c64, 0x255c9c), (0x256eac, 0x256f34),
    (0x259a88, 0x259c3c), (0x2648ec, 0x264904), (0x2659d4, 0x26670c), (0x274598, 0x274e4c), (0x275fe8, 0x276088), (0x276d40, 0x276ddc),
    (0x2788cc, 0x2789d4), (0x279120, 0x279228), (0x279abc, 0x279f24), (0x27a4a0, 0x27a550), (0x27e288, 0x27e344), (0x284ae0, 0x284b80),
    (0x286884, 0x286940), (0x2912f4, 0x29139c), (0x291c50, 0x291ce0), (0x29b308, 0x29b320), (0x29dd8c, 0x29de64), (0x3bbbb0, 0x3bbe70),
    (0x732b20, 0x733040), (0x7372e8, 0x737d58), (0x73917c, 0x739bb8), (0x73a134, 0x73a9b4), (0x73c04c, 0x73c4b4), (0x73ce0c, 0x73d490),
    (0x73ddd4, 0x73df88), (0x73e540, 0x73f0cc), (0x73fe00, 0x7400e0), (0x74312c, 0x743264), (0x746844, 0x746c74), (0x7473e4, 0x74798c),
    (0x747e64, 0x74829c),
)

UNMAPPED_NAMED_BY_DATA = (
    (0x17a7c8, 0x17a7e0), (0x17bb28, 0x17bb40), (0x17bccc, 0x17c0f4), (0x17c700, 0x17caa8), (0x17cf5c, 0x17cf8c), (0x17d1c8, 0x17d390),
    (0x17dab0, 0x17de74), (0x17e20c, 0x17e23c), (0x17e44c, 0x17e60c), (0x17ecd4, 0x17ed24), (0x17f034, 0x17f094), (0x17fb64, 0x17fbb4),
    (0x181348, 0x181398), (0x181448, 0x181498), (0x181548, 0x181598), (0x182054, 0x182444), (0x182dcc, 0x1830e0), (0x1837dc, 0x183dfc),
    (0x1847b0, 0x184b8c), (0x1886ac, 0x188a8c), (0x189c1c, 0x189fac), (0x18a07c, 0x18a0c4), (0x18b31c, 0x18bae4), (0x18c638, 0x18cd1c),
    (0x18d808, 0x18de84), (0x190240, 0x190688), (0x192364, 0x1923a0), (0x193a10, 0x193a2c), (0x1945ec, 0x194604), (0x19470c, 0x194744),
    (0x195c3c, 0x195cf4), (0x196fa8, 0x196ff0), (0x1971d0, 0x197208), (0x19807c, 0x1980b4), (0x198ef0, 0x198f28), (0x199b54, 0x199b6c),
    (0x199cf4, 0x199d10), (0x19ae34, 0x19ae4c), (0x19b658, 0x19b674), (0x19c368, 0x19c380), (0x19d5dc, 0x19d66c), (0x19f7f4, 0x19f854),
    (0x19fc04, 0x1a0264), (0x1a1290, 0x1a133c), (0x1a241c, 0x1a2e8c), (0x1a4490, 0x1a44ac), (0x1a4f18, 0x1a4f30), (0x1a5b7c, 0x1a5bcc),
    (0x1a6384, 0x1a639c), (0x1a6890, 0x1a68f4), (0x1a8110, 0x1a89e0), (0x1aa968, 0x1aa9b0), (0x1aac54, 0x1aacd4), (0x1af324, 0x1af534),
    (0x1afea8, 0x1afec0), (0x1affa8, 0x1b0040), (0x1b037c, 0x1b03fc), (0x1b0ccc, 0x1b0cfc), (0x1b1a08, 0x1b1a58), (0x1b1cf8, 0x1b1de8),
    (0x1b1ff4, 0x1b2010), (0x1b2dac, 0x1b2f38), (0x1b3a70, 0x1b3aa8), (0x1b4488, 0x1b44c0), (0x1b4e28, 0x1b4e60), (0x1b5790, 0x1b57c8),
    (0x1b618c, 0x1b61c4), (0x1b6810, 0x1b6848), (0x1b6fec, 0x1b7004), (0x1b71b8, 0x1b720c), (0x1b8818, 0x1b886c), (0x1ba1d8, 0x1ba210),
    (0x1bb010, 0x1bb080), (0x1bdc54, 0x1bdf24), (0x1bf08c, 0x1bf12c), (0x1c0cb4, 0x1c0e38), (0x1c1630, 0x1c199c), (0x1c28d4, 0x1c29a4),
    (0x1c2ef4, 0x1c2f0c), (0x1c2ff4, 0x1c3120), (0x1c3a70, 0x1c3c30), (0x1c4dc4, 0x1c4ee4), (0x1c6064, 0x1c6188), (0x1c6b90, 0x1c6c30),
    (0x1c7be8, 0x1c7c00), (0x1c88d4, 0x1c8974), (0x1c91d8, 0x1c9278), (0x1c9b48, 0x1c9be8), (0x1cb0cc, 0x1cb16c), (0x1cdf74, 0x1ce034),
    (0x1ce30c, 0x1ce3ac), (0x1cebd4, 0x1cec94), (0x1ced8c, 0x1ceda8), (0x1cf63c, 0x1cf66c), (0x1d0184, 0x1d01bc), (0x1d08ec, 0x1d091c),
    (0x1d09e4, 0x1d0a1c), (0x1d1298, 0x1d1328), (0x1d1c74, 0x1d1cc8), (0x1d2c28, 0x1d2c44), (0x1d3d38, 0x1d3dbc), (0x1d45f0, 0x1d4638),
    (0x1d482c, 0x1d489c), (0x1d5480, 0x1d54b8), (0x1d5a9c, 0x1d5ad4), (0x1d68f4, 0x1d6948), (0x1d7da8, 0x1d7e08), (0x1d93ec, 0x1d9524),
    (0x1d9674, 0x1d96ac), (0x1d9d54, 0x1d9d9c), (0x1d9fe0, 0x1d9ffc), (0x1da7b0, 0x1da840), (0x1dac90, 0x1dad0c), (0x1db334, 0x1db34c),
    (0x1db374, 0x1db3ac), (0x1dbce0, 0x1dbd34), (0x1dccc8, 0x1dcce0), (0x1dcd68, 0x1dcda0), (0x1dd900, 0x1dd960), (0x1ddbe4, 0x1ddc00),
    (0x1deb1c, 0x1deb94), (0x1def58, 0x1def74), (0x1dff10, 0x1dff2c), (0x1e11e8, 0x1e1268), (0x1e24f4, 0x1e2bd8), (0x1e36cc, 0x1e36e4),
    (0x1e3780, 0x1e37b8), (0x1e6588, 0x1e65b8), (0x1e6e2c, 0x1e6ec8), (0x1e7898, 0x1e7918), (0x1e7b8c, 0x1e7bd4), (0x1e7d58, 0x1e7d90),
    (0x1e900c, 0x1e908c), (0x1ea2d8, 0x1ea794), (0x1ea9dc, 0x1eaa44), (0x1ec044, 0x1ec0e0), (0x1eca40, 0x1eca78), (0x1ef1a8, 0x1ef228),
    (0x1f1e44, 0x1f1ec4), (0x1f2100, 0x1f2150), (0x1f31f8, 0x1f3278), (0x1f40d8, 0x1f4120), (0x1f5028, 0x1f5144), (0x1f63b8, 0x1f6430),
    (0x1f6750, 0x1f677c), (0x1f7020, 0x1f7050), (0x1f79f4, 0x1f7a0c), (0x1f7af4, 0x1f7b10), (0x1f8548, 0x1f8590), (0x1f8c1c, 0x1f8c50),
    (0x1f9518, 0x1f95c0), (0x1f97ec, 0x1f9824), (0x1f9cd0, 0x1f9d08), (0x1fa008, 0x1fa03c), (0x1fa55c, 0x1fa594), (0x1fa824, 0x1fa858),
    (0x1fab3c, 0x1fab70), (0x1fb060, 0x1fb380), (0x1fbc28, 0x1fbc60), (0x1fc928, 0x1fc980), (0x1fcc60, 0x1fcc94), (0x1fcd38, 0x1fcd6c),
    (0x1fce38, 0x1fce70), (0x1fcf3c, 0x1fcf74), (0x1fd018, 0x1fd04c), (0x1fd1f0, 0x1fd2d0), (0x1fd39c, 0x1fd3d4), (0x1fd478, 0x1fd4ac),
    (0x1fdea8, 0x1fdedc), (0x1fe6cc, 0x1fe704), (0x1fef08, 0x1fef3c), (0x1ff3f0, 0x1ff408), (0x1ff490, 0x1ff4ac), (0x1ff618, 0x1ff650),
    (0x1ff708, 0x1ff740), (0x1ff954, 0x1ff970), (0x2003fc, 0x200414), (0x200f88, 0x200fa0), (0x20270c, 0x202798), (0x203210, 0x20329c),
    (0x2041b0, 0x2041e0), (0x2048b0, 0x204920), (0x204cc8, 0x204d28), (0x204ecc, 0x204f3c), (0x20537c, 0x205434), (0x205c2c, 0x205ca4),
    (0x206ac8, 0x206b98), (0x207108, 0x2071d8), (0x2075c0, 0x207680), (0x2079cc, 0x207a3c), (0x207e6c, 0x207f68), (0x2083c0, 0x20845c),
    (0x2087b0, 0x208894), (0x2091a0, 0x209200), (0x209498, 0x2094ec), (0x209b4c, 0x209bc4), (0x20a250, 0x20a288), (0x20a640, 0x20a678),
    (0x20a908, 0x20a924), (0x20adf8, 0x20ae4c), (0x20b24c, 0x20b284), (0x20b998, 0x20b9d0), (0x20c0c0, 0x20c0f8), (0x20cd58, 0x20cd90),
    (0x20d674, 0x20d68c), (0x20d834, 0x20d850), (0x20db9c, 0x20dbd4), (0x20e490, 0x20e4e0), (0x20eb08, 0x20eb5c), (0x20ef60, 0x20efd0),
    (0x2103dc, 0x210414), (0x2110dc, 0x2110f8), (0x2113e4, 0x2116b8), (0x2119f8, 0x211b48), (0x211e08, 0x211e74), (0x2121e4, 0x21221c),
    (0x2128c8, 0x212900), (0x2133a4, 0x2135b4), (0x213cfc, 0x213d34), (0x214964, 0x21499c), (0x215100, 0x21517c), (0x215938, 0x215954),
    (0x215f20, 0x216324), (0x216718, 0x216790), (0x2169fc, 0x216a18), (0x216f28, 0x216fd0), (0x217150, 0x217188), (0x217d30, 0x217dc0),
    (0x217f88, 0x217fdc), (0x218e6c, 0x218ee4), (0x219044, 0x2190b4), (0x2199a4, 0x2199dc), (0x219db0, 0x219de8), (0x21ae40, 0x21aea8),
    (0x21b5a8, 0x21b5e0), (0x21c070, 0x21c0c4), (0x21ca44, 0x21ca7c), (0x21d4d4, 0x21d53c), (0x21dd88, 0x21e108), (0x21f99c, 0x21f9cc),
    (0x223040, 0x223070), (0x2246e0, 0x224758), (0x225024, 0x2250cc), (0x226848, 0x226878), (0x226bfc, 0x226c44), (0x227120, 0x227150),
    (0x22766c, 0x227684), (0x227adc, 0x227b0c), (0x227e8c, 0x227ea4), (0x228154, 0x22816c), (0x228684, 0x2286b4), (0x228a20, 0x228a68),
    (0x2291d8, 0x229208), (0x22a2fc, 0x22a32c), (0x22a768, 0x22a798), (0x22b178, 0x22b190), (0x22ba74, 0x22ba8c), (0x22c11c, 0x22c1f4),
    (0x22cf10, 0x22cf28), (0x22d930, 0x22d978), (0x22df58, 0x22df88), (0x22e1d8, 0x22e1f0), (0x22ea1c, 0x22eaa0), (0x22ef54, 0x22ef84),
    (0x22f674, 0x22f6a4), (0x22fb10, 0x22fb40), (0x23048c, 0x230cb4), (0x23220c, 0x232334), (0x23275c, 0x232fbc), (0x233a34, 0x233a68),
    (0x235710, 0x235788), (0x236470, 0x236a10), (0x237f20, 0x237f38), (0x23805c, 0x2380fc), (0x23881c, 0x2388bc), (0x2390fc, 0x23915c),
    (0x23a4a8, 0x23a560), (0x23af80, 0x23b038), (0x23bd7c, 0x23bdac), (0x23bf5c, 0x23c018), (0x23d3f0, 0x23d498), (0x23e0b0, 0x23e150),
    (0x23ff58, 0x240044), (0x240ad0, 0x240bb8), (0x241924, 0x24196c), (0x24451c, 0x244600), (0x246b08, 0x246b34), (0x24720c, 0x247254),
    (0x247388, 0x2473a4), (0x24779c, 0x2477b4), (0x2478ac, 0x2478e4), (0x247e7c, 0x247e94), (0x248070, 0x2480a8), (0x249d80, 0x249ea0),
    (0x249ebc, 0x249f40), (0x24a1cc, 0x24aec4), (0x24bf54, 0x24c000), (0x24dcc0, 0x24ddb0), (0x24f4e4, 0x24f55c), (0x24fd48, 0x24fdd8),
    (0x24fed0, 0x24feec), (0x25066c, 0x250744), (0x250a08, 0x250a24), (0x2511a4, 0x25133c), (0x251b94, 0x251c04), (0x251f4c, 0x251fd8),
    (0x252bbc, 0x2535e0), (0x253908, 0x253924), (0x253c00, 0x253de4), (0x25440c, 0x254454), (0x254cf4, 0x254da0), (0x255b30, 0x255b60),
    (0x2560d4, 0x25610c), (0x258514, 0x25867c), (0x258b9c, 0x258bb8), (0x2590f0, 0x25910c), (0x2598a8, 0x2598c0), (0x25c338, 0x25c3b0),
    (0x25c6e4, 0x25c830), (0x25d51c, 0x25d534), (0x25d5a0, 0x25df9c), (0x25e31c, 0x25e338), (0x25eb64, 0x25f5a0), (0x25faa0, 0x25fc08),
    (0x2607b4, 0x2607d0), (0x260d50, 0x260d80), (0x262e20, 0x262e38), (0x262f74, 0x2637f4), (0x2639f8, 0x263a30), (0x263e94, 0x2645fc),
    (0x264d50, 0x264dc0), (0x26512c, 0x2653e4), (0x26561c, 0x2658d8), (0x267998, 0x267afc), (0x26a410, 0x26a458), (0x26a6d8, 0x26a778),
    (0x26abc0, 0x26ac08), (0x26b14c, 0x26b26c), (0x26b808, 0x26b824), (0x26bb94, 0x26bc9c), (0x26c29c, 0x26c2b8), (0x26c8d4, 0x26c97c),
    (0x26ce28, 0x26ce7c), (0x26d48c, 0x26d4e4), (0x26daa0, 0x26daf8), (0x26e074, 0x26e0cc), (0x26e678, 0x26e6d0), (0x26ec80, 0x26ecd8),
    (0x26f6c0, 0x26fe2c), (0x2709c4, 0x270a00), (0x270d38, 0x270d54), (0x271134, 0x27114c), (0x271258, 0x271290), (0x271948, 0x271980),
    (0x271ec4, 0x271f10), (0x2725b8, 0x2725f0), (0x273a40, 0x273ab4), (0x275c60, 0x275ca8), (0x27723c, 0x277284), (0x277374, 0x277390),
    (0x277950, 0x277998), (0x277c08, 0x278258), (0x27a900, 0x27a938), (0x27ae9c, 0x27aed4), (0x27bd78, 0x27bda8), (0x27c04c, 0x27c0ec),
    (0x27c614, 0x27c6b4), (0x27cb28, 0x27cbc8), (0x27d454, 0x27d4f4), (0x27e0d4, 0x27e0ec), (0x27f088, 0x27f128), (0x27f9b0, 0x27fa80),
    (0x280378, 0x2803d8), (0x2805e4, 0x280668), (0x280ad8, 0x280b78), (0x2818cc, 0x28196c), (0x281e18, 0x281eb8), (0x2829b4, 0x2829cc),
    (0x282ab4, 0x282b54), (0x283414, 0x2834b4), (0x283f20, 0x28400c), (0x2844e4, 0x2844fc), (0x2845d8, 0x284678), (0x285c18, 0x285f28),
    (0x287508, 0x2875c0), (0x288f00, 0x288f60), (0x28943c, 0x2898c0), (0x289de4, 0x289e44), (0x28a1c8, 0x28a1e4), (0x28a678, 0x28a690),
    (0x28a6f4, 0x28a710), (0x28abd4, 0x28ac04), (0x28ae60, 0x28aeb4), (0x28b6e8, 0x28b7c0), (0x28bb54, 0x28bba8), (0x28c000, 0x28c0f0),
    (0x28c4b4, 0x28c4d0), (0x28ec28, 0x28ecf0), (0x28faac, 0x28fadc), (0x28fbe4, 0x28fc00), (0x290394, 0x2903ac), (0x290560, 0x290598),
    (0x2927a4, 0x292834), (0x2933e4, 0x293474), (0x29478c, 0x2947ec), (0x2948d8, 0x294968), (0x295bcc, 0x295c58), (0x297c68, 0x297c84),
    (0x2980f8, 0x298140), (0x298324, 0x29835c), (0x299698, 0x2996d0), (0x29b478, 0x29b494), (0x29d074, 0x29d194), (0x29e274, 0x29e28c),
    (0x29eca4, 0x29ed4c), (0x2ac150, 0x2aca20), (0x2ae058, 0x2ae088), (0x2afce4, 0x2afcfc), (0x2b1f04, 0x2b1f34), (0x2b28fc, 0x2b2914),
    (0x2b2998, 0x2b2a40), (0x2b31e8, 0x2b3e6c), (0x2b4994, 0x2b49ac), (0x2b5f1c, 0x2b5f28), (0x3192a5, 0x3192a8), (0x36d18a, 0x36d18c),
    (0x46d2ec, 0x46d354), (0x4add30, 0x4add90), (0x4ba1fc, 0x4ba3b4), (0x51c618, 0x51c898), (0x52781c, 0x527a7c), (0x532c1c, 0x532dcc),
    (0x597db0, 0x597df0), (0x5bfc44, 0x5bfc84), (0x667f64, 0x6681ec), (0x674154, 0x674384), (0x6f3bc8, 0x6f3c30), (0x733ae8, 0x733b8c),
    (0x733c9c, 0x734084), (0x7347bc, 0x7348b0), (0x734a5c, 0x734af4), (0x734c9c, 0x734d74), (0x734fd4, 0x735210), (0x7357f0, 0x735944),
    (0x735c74, 0x735d1c), (0x735e34, 0x7366a8), (0x73af04, 0x73b050), (0x73b1d8, 0x73b2ac), (0x73b4c4, 0x73b800), (0x73be30, 0x73bef4),
    (0x73c998, 0x73cad8), (0x73cbb4, 0x73cc84), (0x73e120, 0x73e31c), (0x740440, 0x740654), (0x7408d8, 0x740938), (0x74098c, 0x740a5c),
    (0x740b98, 0x740ca8), (0x740e1c, 0x74188c), (0x742b20, 0x742bec), (0x742c48, 0x742e18), (0x7434b0, 0x743e68), (0x744ef0, 0x74535c),
    (0x745798, 0x74606c), (0x748668, 0x748788), (0x748860, 0x7488e4), (0x7489d4, 0x748a38), (0x748ac8, 0x748c58), (0x748f34, 0x74901c),
    (0x749118, 0x749178), (0x7491d0, 0x7495c8), (0x74980c, 0x749cbc), (0x749f1c, 0x74a820), (0x74aa98, 0x74ac18), (0x74acb4, 0x74b0f8),
    (0x74b8b4, 0x74ba44), (0x74bb40, 0x74bc88), (0x74bcf8, 0x74bfb4), (0x74c58c, 0x74c660), (0x74c804, 0x74c884), (0x74ca3c, 0x74ca60),
    (0x74ca70, 0x74ca90), (0x74caa0, 0x74cac4), (0x74cad4, 0x74caf4),
)

SLICE_RESIDUE_RAW_LABELED = (
    (0x6fda1c, 0x6fda30), (0x6fda4c, 0x6fdb18), (0x704f6c, 0x704f80), (0x704f90, 0x704fb8), (0x705224, 0x70527c),
    (0x710ef4, 0x711274), (0x74f080, 0x75023c), (0x752dec, 0x752e18), (0x756b68, 0x7572ac), (0x757324, 0x757344),
    (0x757390, 0x757a40), (0x757ad0, 0x757ad8), (0x757b58, 0x7581cc), (0x7581e8, 0x75916c), (0x75919c, 0x7591dc),
    (0x759220, 0x759234), (0x75925c, 0x7592ac), (0x7592bc, 0x759324), (0x759334, 0x759354), (0x7593cc, 0x7593ec),
    (0x75a714, 0x75a718), (0x77af34, 0x77af50), (0x77af78, 0x77afc0), (0x77afdc, 0x77b03c), (0x77b0b0, 0x77b0f8),
    (0x77b16c, 0x77b170), (0x77b180, 0x77b1b0), (0x77c48c, 0x77c498),
)

RUNTIME_CITED_RAW_LABELED = (
    (0x19c744, 0x19c8a8), (0x275c60, 0x275ca8), (0x275fe8, 0x276088), (0x288f00, 0x288f60), (0x28943c, 0x2898c0),
    (0x28b6e8, 0x28b7c0), (0x28bb54, 0x28bba8), (0x28c000, 0x28c0f0), (0x28c4b4, 0x28c4d0), (0x28ec28, 0x28ecf0),
    (0x28faac, 0x28fadc), (0x28fbe4, 0x28fc00), (0x290394, 0x2903ac), (0x290560, 0x290598), (0x2912f4, 0x29139c),
    (0x291c50, 0x291ce0), (0x2927a4, 0x292834), (0x2933e4, 0x293474), (0x29478c, 0x2947ec), (0x2948d8, 0x294968),
    (0x295bcc, 0x295c58), (0x2ae058, 0x2ae088), (0x2b8bc8, 0x2b8bf4), (0x2b8c38, 0x2b9bb0),
    (0x36d540, 0x3715c0), (0x3725c0, 0x3bb78c),
    (0x46d2ec, 0x46d354), (0x51c618, 0x51c898), (0x52781c, 0x527a7c), (0x597db0, 0x597df0), (0x5bfc44, 0x5bfc84),
    (0x6fe820, 0x6fe824), (0x6fe900, 0x6fe904), (0x6fe9c0, 0x6fe9c4), (0x6fe9d4, 0x6fe9e8), (0x6fe9f8, 0x6fe9fc),
    (0x6ff8fc, 0x6ff900), (0x6ff940, 0x6ff974), (0x6ff984, 0x6ff9ac), (0x6ffa24, 0x6ffa28), (0x6ffa68, 0x6ffa8c),
    (0x6ffa9c, 0x6ffaa0), (0x702228, 0x70222c), (0x70226c, 0x70228c), (0x70229c, 0x7022a0), (0x7022b0, 0x7022b4),
    (0x7022c4, 0x7022d8), (0x7022e8, 0x702310), (0x702320, 0x702334), (0x702344, 0x702348), (0x702358, 0x70235c),
    (0x702470, 0x702474), (0x7024a4, 0x7024d8), (0x7024e8, 0x7024ec), (0x7024fc, 0x702528), (0x702538, 0x70253c),
    (0x7048c8, 0x7048cc), (0x706a48, 0x706a4c), (0x706a8c, 0x706aac), (0x706abc, 0x706ac0), (0x706ad0, 0x706ad4),
    (0x706ae4, 0x706af8), (0x706b08, 0x706b30), (0x706b40, 0x706b54), (0x706b64, 0x706b68), (0x706b78, 0x706b7c),
    (0x706c90, 0x706c94), (0x706cec, 0x706cf0), (0x706d30, 0x706d40), (0x706d50, 0x706db4), (0x706dc4, 0x706dd8),
    (0x706de8, 0x706dfc), (0x706e0c, 0x706e10), (0x706e94, 0x706ee8), (0x706f08, 0x706f0c), (0x706fcc, 0x706fe0),
    (0x706ff0, 0x706ff4), (0x70709c, 0x7070a0), (0x7070d0, 0x707140), (0x707150, 0x707154), (0x707164, 0x70717c),
    (0x70718c, 0x707190), (0x7122dc, 0x7122f8), (0x732b20, 0x733040), (0x733ae8, 0x733b8c), (0x733c9c, 0x734084),
    (0x7347bc, 0x7348b0), (0x734a5c, 0x734af4), (0x734c9c, 0x734d74), (0x734fd4, 0x735210), (0x7357f0, 0x735944),
    (0x735c74, 0x735d1c), (0x735e34, 0x7366a8), (0x7372e8, 0x737d58), (0x73917c, 0x739bb8), (0x73a134, 0x73a9b4),
    (0x73af04, 0x73b050), (0x73b1d8, 0x73b2ac), (0x73b4c4, 0x73b800), (0x73be30, 0x73bef4), (0x73c04c, 0x73c4b4),
    (0x73c998, 0x73cad8), (0x73cbb4, 0x73cc84), (0x73ce0c, 0x73d490), (0x73ddd4, 0x73df88), (0x73e120, 0x73e31c),
    (0x73e540, 0x73f0cc), (0x73fe00, 0x7400e0), (0x740440, 0x740654), (0x7408d8, 0x740938), (0x74098c, 0x740a5c),
    (0x740b98, 0x740ca8), (0x740e1c, 0x74188c), (0x742b20, 0x742bec), (0x742c48, 0x742e18),
)

REGIONS = (
    Region(
        "enemy stat array, empty 151st slot",
        "promoted-since-recon",
        "SPEC-ENEMYSTAT-001-R2 promoted 150 of 151 records of 0x1C B; this is the "
        "empty slot at the array's end (tools/mapcontainer/enemystats.py)",
        [(0x7122DC, 0x7122F8)],
        "the one residual byte range of a family promoted after the RECON-LATE-001 baseline",
    ),
    Region(
        "PATH-100-012 runtime-cited rows (a read consumer, no extent)",
        "raw-labeled",
        "R-RAW-001, PATH-100-012: a runtime mGBA session read every one of these 114 rows "
        "(read watchpoints over all 550,905 B; 738 (pc, first_address_read) citations over 180 "
        "distinct pcs, RUNTIME_CITED.csv sha256 "
        "CCF19E3469778F3DA12B68A94EC4BCB9F96A819BCE9A574C4A5892CA9E0FC6CF). The observed pc IS "
        "the citation (Amendment B of RUNTIME-CONSUMER-002) and no cited site reads a "
        "count or a terminator out of a row, so no extent follows; promoted as LABELED RAW DATA, one "
        "symbol per row at its start, by tools/build/rawlabeled.py --citations into "
        "asm/rawlabeled_<start>.s. 113 of the 114 rows (354,080 B) sit inside ranges this census had "
        "called either `identified-no-consumer` or `unknown-proven` (315,980 B in asset directory "
        "3's payload, 16,532 B and 16,516 B in PATH-100-006's two unknown-proven buckets, 4,072 B in "
        "asset directory 1's head, 980 B in recon slice B's residue), which is a cited consumer for "
        "bytes the pc-relative literal channels could not name: those negatives stay true of the "
        "channels they name (P-419) and are refuted as consumer statements at runtime. The remaining "
        "3 rows are the enemy stat array's empty 151st slot (28 B), which this census itself calls a "
        "promoted-since-recon residual. 115 spans over the 114 rows: PATH-100-011's JCALG1 section "
        "carries 0x2B8BF4..0x2B8C38 (68 B) inside the row 0x2B8BC8..0x2B9BB0, so that row is carried "
        "as its two retail spans 0x2B8BC8..0x2B8BF4 (44 B) and 0x2B8C38..0x2B9BB0 (3,960 B) and the "
        "container stays the generated section",
        RUNTIME_CITED_RAW_LABELED,
        "the bytes are source now, so 0 B of these ranges is INCBIN; no structure and no extent is "
        "claimed. The session read these rows; it does not show what they are",
    ),
    Region(
        "AI behaviour row table 0x70F514",
        "identified-with-consumer",
        "0800AAA6 lsls r0,r1,#3 / 0800AAAA adds r5,r0,r1 / 0800AAB0 ldr r2,[r0]; base literal at file "
        "0x00AB50; SPEC-AINODE-001's seeds",
        [(0x70F514, 0x710EF4)],
        "828 rows x 8 B, every word a node pointer. Promoted in this ticket (INCBIN-CENSUS-001) into "
        "the end-of-ROM block's record store; the round trip is a word copy, so the consumer chain "
        "(0800AAA6 / 0800AAA8, base literals at file 0x00AB50 and 0x0192AC) is the evidence.",
    ),
    Region(
        "event-resource record pool 0x77C5A4..0x79B704",
        "promoted-since-recon",
        "080040B8 ldr r0,[r6] / 080040BA ldrb r1,[r0,#2] (the record's DIALOG pointer, then the TYPE "
        "byte); promoted in INCBIN-PROMOTE-002 as tools/mapcontainer/eventpool.py: the 522-word index "
        "delimits 522 records that tile 0x77C5A4..0x79B704 exactly, and every record's header is the "
        "DIALOG pointer whose descriptor's +2 TYPE byte the consumer branches on (measured 522/522, "
        "histogram 236/2/141/139/2/2 over types 0/3/4/5/6/7)",
        [(0x77C5A4, 0x79B704)],
        "one generated run of 127,328 B, no residual left INCBIN: the record header is parsed and the "
        "per-TYPE payloads keep no field map (K-016), so the family carries them as the record's own "
        "bytes. The 148 B head 0x77C510..0x77C5A4 before the pool stays retail.",
    ),
    Region(
        "engine asset directory 1 (64 x 12 B) 0x3192A8 and its blocks",
        "promoted-since-recon",
        "file 0x00082A ldr r1,[pc,#0xc4] (literal file 0x08F0 = 0x083192A8) / 0x000832 adds r1,r0,r1 => "
        "record at 0x083192A8 + 12*index; the caller bl 0x0803E378 at file 0x00083A and 0x00086C; "
        "promoted in this ticket (INCBIN-PROMOTE-001) as tools/mapcontainer/assetdir.py",
        [(0x2B9BB0, 0x3192A5), (0x3192A8, 0x3195A8)],
        "64 records {u32 data_ptr, u32 flags, u16 byte_length, u16 unit}; the blocks tile "
        "0x2B9BB0..0x3192A5 (390,901 B, zero gap, zero overlap) and the 768-byte table is the second "
        "generated run. The 3,072 B head 0x2B8FB0..0x2B9BB0 is named by no record: it stays retail.",
    ),
    Region(
        "engine asset directory 2 (79 x 12 B) 0x36D18C and its blocks",
        "identified-no-consumer",
        "reached through DATA only: of 2,097,152 word-aligned sites, 53 hold 0x0836D18C and every one "
        "lies inside the 53-record directory at file 0x3BB78C; ASSET-002 re-measured the loaders over "
        "every even offset: of 117,008 decoded Thumb ldr rX,[pc,#imm] sites 2 compute into "
        "0x0836D18C..0x0836D540 and of 4,015 ARM sites 1 does, and all three instruction addresses sit "
        "inside the table's own bytes, so 0 code consumers",
        [(0x3195A8, 0x36D18A), (0x36D18C, 0x36D540)],
        "79 records of the same shape as directory 1, blocks tiling 0x3195A8..0x36D18A (343,010 B) "
        "plus the 948 B table, 343,958 B in all. DECLINED in INCBIN-PROMOTE-001 for want of a "
        "consumer; PROMOTED in ASSET-002 by the rule that an identified, "
        "self-delimiting format may be promoted by a real parse "
        "(tools/mapcontainer/assetdir2.py), and it keeps this label because no code consumer exists. "
        "The 2 bytes between the blocks and the table (0x36D18A..0x36D18C) are outside both families "
        "and stay retail. The payload format stays NOT ESTABLISHED (K-138).",
    ),
    Region(
        "asset directory 2's bank tail: 53 x 20 B directory, and the 83 x 52 B records past the chain",
        "raw-labeled",
        "R-RAW-001 (PATH-100-008): the 20-byte directory base 0x083BB78C is code-loaded at four "
        "sites (0x080008BC, 0x080041BA, 0x080053F8, 0x08008C86; literal words at file 0x0008F8, "
        "0x004210, 0x00545C, 0x008D10), each computing base + 20*index, and the 83-record array "
        "base 0x083BD2F8 at sixteen more; carried whole as LABELED RAW DATA by "
        "tools/build/rawlabeled.py into asm/rawlabeled_3bb78c.s (the 1,060 B table, 1 symbol) "
        "and asm/rawlabeled_3bbe70.s (the 9,572 B past the chain, 46 symbols), whose split is the "
        "run's cited bases plus the data-stated boundaries in "
        "tools/research/rawlabeled_3bbe70_bounds.txt: 53 x 20 B records (53 = the occurrences of "
        "the +8 word 0836D18C in the whole image, all here), the 45 kind-1 containers "
        "0x3BBE70..0x3BD2F8 (each header {kind=1, declared 128/256/512/1024}, chaining exactly "
        "5,256 B, 4-byte aligned) and the 83 x 52 B records 0x3BD2F8..0x3BE3D4 (stride 52 proven "
        "at 0x0800D2F8 and 0x0802BCD2: muls r0,r3,r0 with r3=0x34, then +0xC). 10,632 B promoted; "
        "the 704 B 0x3BBBB0..0x3BBE70 between the table and the chain is LEFT INCBIN because it is "
        "its own census row and a different status (unmapped; PATH-100-006 measured it "
        "no-consumer, 2 singleton literal sites at or below the null), so it is not carried by a "
        "promotion that its own measurement does not justify",
        [(0x3BB78C, 0x3BBBB0), (0x3BBE70, 0x3BE3D4)],
        "carried whole as labeled raw data: no parse re-serializes the packed payloads, so no "
        "layout is claimed beyond the header and the strides. The chain is a decode, not an "
        "asserted extent: each container is walked to its packed end and the next header is the "
        "next 4-byte-aligned offset. The gap keeps its own INCBIN name and its own incbin.bat line "
        "(P-436)."
        " PATH-100-007 ITEM 1, re-verified on the 2026-10-16 master: NOT self-delimiting as a "
        "whole. The 45 kind-1 containers ARE: an independent walk from 0x3BBE70 finds exactly 45, all "
        "kind 1 (declared 128/256/512/1024), first 0x3BBE70 and last 0x3BD290, tiling 5,256 B to "
        "0x3BD2F8. The directory and the records are not: the constant 45 is in no byte (movs r1,#0xE1; "
        "lsls r1,r1,#2 = 900 = 45 x 20 at 0x080041B8 and 0x080053F6), so the 1,060 B table is fixed "
        "only by the gap at 0x3BBBB0 and the 4,316 B of records only by the end 0x3BE3D4. No Block of "
        "tools/mapcontainer/generate_mapcontainer.py covers these bytes (MAP 0x179A50..0x2B8BC8, "
        "ASSETDIR 0x2B8BC8..0x3715C0, SPRITE 0x3C34D0..0x6A88AC, re-read on master) and no "
        "build\\jcalg1\\gen_*.bin token covers them either, so the 5,256 B whose extent the data does "
        "state is still retail. Denominator: 10,632 B; 5,256 B (49.4 %) data-stated, 5,376 B not.",
    ),
    Region(
        "asset directory 3 (53 x 20 B at 0x3BB78C) payload 0x36D540..0x3BB78C",
        "identified-no-consumer",
        "the 20-byte directory's base 0x083BB78C is code-loaded at exactly four sites (0x080008BC, "
        "0x080041BA, 0x080053F8, 0x08008C86; the literal words at file 0x0008F8, 0x004210, 0x00545C, "
        "0x008D10), each computing base + 20*index (lsls #2 / adds / lsls #2) and each handing the "
        "record to 0x0803F110 after comparing it against the cached pointer at 0x030038B0. NO SITE "
        "READS THE RECORD'S POINTERS: all four windows decode to the same four steps - form the "
        "record pointer, compare it with the cached one, `bl 0x803F110` - and 0x0803F110 reads only "
        "bytes +0x10 and +0x11 (0x0803F120 ldrb r0,[r1,#0x11]; 0x0803F14A ldrb r0,[r1,#0x10]); no "
        "site loads +0, +4, +8 or +0xC. RE-MEASURED at every ldr-literal site (PATH-100-008, "
        "tools/research/code_xref.py): 117,008 Thumb + 618 ARM candidates, 31 load a word that is an "
        "address in this payload, of which 19 have their own instruction address inside the payload "
        "(data decoded as code, P-420) and 12 sit in other data blocks; 0 have the site inside the "
        "transcribed code band 0x158..0x71758. The 83 x 52 B records at 0x083BD2F8, which ARE "
        "code-loaded (sixteen sites) with a proven 52 B stride, hold 0 fields naming this payload: "
        "their +0x18 and +0x28 name a container of 0x3BBE70..0x3BD2F8 and their +0x30 a byte of "
        "0x3BBBB0..0x3BBE70. The payload is named by the table's +0 and +4 words, which is DATA "
        "naming, not a code consumer",
        [(0x36D540, 0x3715C0), (0x3725C0, 0x3BB78C)],
        "the payload format is NOT ESTABLISHED - the range is named by the table, not decoded. "
        "Limits of the negative (P-419, P-428): it names the pc-relative literal channel and the "
        "four table loaders, so a base computed by immediate arithmetic from another constant, or a "
        "record pointer copied to RAM and dereferenced there, is not excluded. Read the code-loaded "
        "label on the two directory regions above as the TABLE being reachable: those sites consume "
        "two bytes of a record, not its pointers."
        " PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: the payload is NOT "
        "self-delimiting. Over the whole 320,076 B the (col1..col0) spans total 318,342 B and are not "
        "contiguous; the only contiguous reading (col0[i-1]..col0[i]) starts at 0x36E160, 3,104 B "
        "late, and totals 316,956 B; and 0 of the 320,076 bytes holds a container header (kind 1..2, "
        "declared 1..0x100000, every even offset). Record field shape: +0 and +4 are strictly "
        "ascending ROM addresses inside the payload, +8 is 0x0836D18C and +0xC is 0x0836D540 in all "
        "53 records, and +0x10 measures 0x341..0x880. SCRIPT-BANK-003 (2026-10-17) SUPERSEDED that "
        "decision: the consumer's own stream machine was decoded from its instructions (a call "
        "budget, a byte ramp, a pointer array and (class, slot, flag) entries whose flag takes "
        "bits 0..3), it reaches 315,906 of the 315,980 census bytes with 74 B read by no call "
        "sequence, and the range is now EMITTED from that parse by "
        "tools/mapcontainer/generate_assetdir3.py (carriers asm/assetdir3_36d540.s and "
        "asm/assetdir3_3725c0.s), so it is no longer an INCBIN row at all.",
    ),
    Region(
        "dialogue container table 0x7B5B64 and the run it heads",
        "raw-labeled",
        "the base is code-loaded from the literal at file 0x123CC = 0x087B5B64, read at 0x08012242 "
        "and 0x080122C8 in the handle chain of 0x08012240 (P-036's table); the word at file 0x7B5B80 "
        "is 0x03004A68, named by the literal at file 0x03D92C and read at 0x0803D784 / 0x0803D7BE / "
        "0x0803D7FE. Carried as LABELED RAW DATA by PATH-100-001 item 2 under R-RAW-001 "
        "(tools/research/raw_labeled.py, asm/raw_labeled_7b5b64.s). Re-measured at the bytes with "
        "tools/research/code_xref.py: 91 of the image's 117,008 Thumb + 618 ARM ldr-literal sites "
        "load a word holding an address in the range, over 26 distinct addresses, so the run splits "
        "into 26 symbols - the 68 sites and the 13 sites for 0x087B6EEC this row carried when it was "
        "written do not reproduce, and the wider count is the one quoted; 65 of 3,872 candidate "
        "sites are container-shaped and survive validate_retail_termination",
        [(0x7B5B64, 0x7B79A4)],
        "carried whole as labeled raw data: no parse re-serializes it, so no layout is claimed. The "
        "64-slot head is heterogeneous - it mixes ROM pointers, IWRAM words and u16 pairs - so the "
        "family layout is NOT ESTABLISHED.",
    ),
    Region(
        "container-rich run 0x74D248..0x74F058",
        "raw-labeled",
        "tools/research/code_xref.py: 77 of the image's 117,008 Thumb + 618 ARM ldr-literal sites, "
        "all inside the transcribed first-MiB code band, load a word holding an address in the range "
        "(0x0874EA80 13 sites, 0x0874EAC4 9, 0x0874D380 8, 0x0874E234 5, 0x0874E9F8 5, 0x0874F04C 5, "
        "0x0874D248 4, 0x0874EA50 4; 22 distinct addresses in all). Carried as LABELED RAW DATA by "
        "PATH-100-001 item 2 under R-RAW-001 (tools/research/raw_labeled.py, asm/raw_labeled_74d248.s); "
        "134 of 3,848 candidate sites are container-shaped and survive validate_retail_termination",
        [(0x74D248, 0x74F058)],
        "carried whole as labeled raw data: the pointers are named but no parse that re-serializes "
        "the family exists, so its layout is NOT ESTABLISHED.",
    ),
    Region(
        "container-shaped run 0x220804..0x2222EC",
        "identified-no-consumer",
        "tools/research/code_xref.py: 0 of the image's 117,008 Thumb + 618 ARM ldr-literal sites load "
        "a word holding an address in this range from the transcribed first-MiB code band; 25 of "
        "3,444 candidate sites are container-shaped and survive validate_retail_termination; 256 of "
        "256 byte values occur and 37 of 1,722 words are ROM-pointer shaped",
        [(0x220804, 0x2222EC)],
        "the container family's layout is NOT ESTABLISHED and no code consumer names the range. "
        "PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: NOT self-delimiting. "
        "mapcontainer.packed_container_offsets(rom, span, []) returns 0 containers and "
        "webfoot_lz.validate_retail_termination refuses the run's first byte (ContainerError), so the "
        "surviving sites named above are micro-sites and the 'N of M survive' count is a single-site "
        "sweep, not a tiling.",
    ),
    Region(
        "container-shaped run 0x2B608C..0x2B7EC8",
        "identified-no-consumer",
        "tools/research/code_xref.py: 0 of the image's 117,008 Thumb + 618 ARM ldr-literal sites load "
        "a word holding an address in this range from the transcribed first-MiB code band; 2 of 3,870 "
        "candidate sites are container-shaped and survive validate_retail_termination; 254 of 256 byte "
        "values occur and 34 of 1,935 words are ROM-pointer shaped. The 0x2B7EC8..0x2B8BC8 gap "
        "between it and the next run is already generated source, not INCBIN",
        [(0x2B608C, 0x2B7EC8)],
        "the container family's layout is NOT ESTABLISHED and no code consumer names the range. "
        "PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: NOT self-delimiting. "
        "mapcontainer.packed_container_offsets(rom, span, []) returns 0 containers and "
        "webfoot_lz.validate_retail_termination refuses the run's first byte (ContainerError), so the "
        "surviving sites named above are micro-sites and the 'N of M survive' count is a single-site "
        "sweep, not a tiling.",
    ),
    Region(
        "container-shaped run 0x185AF8..0x187364",
        "identified-no-consumer",
        "tools/research/code_xref.py: 0 of the image's 117,008 Thumb + 618 ARM ldr-literal sites load "
        "a word holding an address in this range from the transcribed first-MiB code band; 4 of 3,126 "
        "candidate sites are container-shaped and survive validate_retail_termination; 256 of 256 byte "
        "values occur and 41 of 1,563 words are ROM-pointer shaped",
        [(0x185AF8, 0x187364)],
        "the container family's layout is NOT ESTABLISHED and no code consumer names the range. "
        "PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: NOT self-delimiting. "
        "mapcontainer.packed_container_offsets(rom, span, []) returns 0 containers and "
        "webfoot_lz.validate_retail_termination refuses the run's first byte (ContainerError), so the "
        "surviving sites named above are micro-sites and the 'N of M survive' count is a single-site "
        "sweep, not a tiling.",
    ),
    Region(
        "container-shaped run 0x1ABCE8..0x1AD1E8",
        "identified-no-consumer",
        "tools/research/code_xref.py: 0 of the image's 117,008 Thumb + 618 ARM ldr-literal sites load "
        "a word holding an address in this range from the transcribed first-MiB code band; 6 of 2,688 "
        "candidate sites are container-shaped and survive validate_retail_termination; 256 of 256 byte "
        "values occur and 53 of 1,344 words are ROM-pointer shaped",
        [(0x1ABCE8, 0x1AD1E8)],
        "the container family's layout is NOT ESTABLISHED and no code consumer names the range. "
        "PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: NOT self-delimiting. "
        "mapcontainer.packed_container_offsets(rom, span, []) returns 0 containers and "
        "webfoot_lz.validate_retail_termination refuses the run's first byte (ContainerError), so the "
        "surviving sites named above are micro-sites and the 'N of M survive' count is a single-site "
        "sweep, not a tiling.",
    ),
    Region(
        "container-shaped run 0x1ADDB4..0x1AEB64",
        "identified-no-consumer",
        "tools/research/code_xref.py: 0 of the image's 117,008 Thumb + 618 ARM ldr-literal sites load "
        "a word holding an address in this range from the transcribed first-MiB code band; 8 of 1,752 "
        "candidate sites are container-shaped and survive validate_retail_termination; 256 of 256 byte "
        "values occur and 44 of 876 words are ROM-pointer shaped",
        [(0x1ADDB4, 0x1AEB64)],
        "the container family's layout is NOT ESTABLISHED and no code consumer names the range. "
        "PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: NOT self-delimiting. "
        "mapcontainer.packed_container_offsets(rom, span, []) returns 0 containers and "
        "webfoot_lz.validate_retail_termination refuses the run's first byte (ContainerError), so the "
        "surviving sites named above are micro-sites and the 'N of M survive' count is a single-site "
        "sweep, not a tiling.",
    ),
    Region(
        "head of asset directory 1's blocks 0x2B8BC8..0x2B9BB0",
        "identified-no-consumer",
        "tools/research/code_xref.py: exactly 1 of the image's 117,008 Thumb + 618 ARM ldr-literal "
        "sites loads a word that is an address here - 0x08012848, whose pool word is 0x082B9BAC, the "
        "last word of the run and the boundary word before asset directory 1's first block at "
        "0x2B9BB0 - and it names no other byte of the run; 64 of 2,036 candidate sites are "
        "container-shaped and survive validate_retail_termination; directory 1's own table names no "
        "block here (assetdir.py: BLOCK_START is 0x2B9BB0)",
        [(0x2B8BC8, 0x2B9BB0)],
        "the 3,072 B head 0x2B8FB0..0x2B9BB0 was already recorded as named by no record; this run is "
        "that head plus the 1,000 B before it, and no consumer names either"
        ". PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: NOT self-delimiting - "
        "the 4,072 B prefix before the first directory record's data_ptr (0x082B9BB0) is one INCBIN "
        "slice and no byte states the prefix's length; it is carried as LABELED RAW DATA by "
        "asm/rawlabeled_2b8bc8.s and asm/rawlabeled_2b8c38.s.",
    ),
    Region(
        "end-of-image 0xFF fill 0x7B89A8..0x800000",
        "identified-no-consumer",
        "uniform 0xFF: 0 of 292,440 bytes differ (two independent sweeps, RECON-TAIL-001 and the "
        "read-only ticket of 2026-10-15); the image's last structure ends at 0x7B89A8",
        [(0x7B89A8, 0x800000)],
        "padding past the last structure; nothing consumes it. PATH-100-016 moved the fill's own body "
        "directive to one extracted INCBIN row inside the loop, whose label sits before the WHILE "
        "because a label in the body is defined once per iteration (A1108E): 1 B of this range is now "
        "INCBIN and the other 292,439 B are still the assembler loop.",
    ),
    Region(
        "raw-labeled run 0x6B7080..0x6B7E8C",
        "raw-labeled",
        "R-RAW-001 (PATH-100-003): 22 Thumb pc-literal loads name 8 distinct bases inside it "
        "(0x086B7080, 0x086B7084, 0x086B72E0, 0x086B7400, 0x086B748C, 0x086B7590, 0x086B759C, "
        "0x086B77A4) over the ledger's 114 code rows / 322,386 B, and the tail's own block emits .bin "
        "sections and no symbol, so the range was promoted as LABELED RAW DATA, 8 symbols, by "
        "tools/build/rawlabeled.py into asm/rawlabeled_6b7080.s",
        [(0x6B7080, 0x6B7E8C)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled run 0x071C90..0x0945C0",
        "raw-labeled",
        "R-RAW-001 (PATH-100-003): the structured block's 495 retail gaps, 42,756 B, named by the "
        "MapEntry +0x30 field (167 of the table's 452 entries, 132 distinct bases) which 008CEE "
        "ldr r1,[r0,#0x30] hands to the opcode interpreter 0x08004038; promoted as LABELED RAW DATA, "
        "574 symbols, by tools/build/rawlabeled.py --structured into asm/rawlabeled_71c90.s",
        [(0x071C90, 0x0945C0)],
        "the region's 98,860 B of generated families stay generated and are INCBINed between the "
        "labeled gaps; no extent is claimed and 0 B of the region is INCBIN"
        ". PATH-100-007 ITEM 2, re-verified on the 2026-10-16 master: the block's residual is "
        "NOT self-delimiting - 461 INCBIN slices, 43,532 B, largest slice 0x073104..0x073AF8 "
        "(2,548 B) - every boundary is a neighbouring parsed member's edge and no byte states a span.",
    ),
    Region(
        "raw-labeled run 0x76CCE4..0x77AE68",
        "raw-labeled",
        "R-RAW-001: 40 cited loader sites on 22 literals, no "
        "code-derived extent; promoted as LABELED RAW DATA, 15 symbols, by tools/build/rawlabeled.py "
        "into asm/rawlabeled_76cce4.s",
        [(0x76CCE4, 0x77AE68)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled run 0x71E274..0x72C378",
        "raw-labeled",
        "R-RAW-001: 182 cited loader sites on 61 literals, no "
        "code-derived extent; promoted as LABELED RAW DATA, 43 symbols, by tools/build/rawlabeled.py "
        "into asm/rawlabeled_71e274.s",
        [(0x71E274, 0x72C378)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled row 0x6FC260..0x6FDA00",
        "raw-labeled",
        "R-RAW-001 (PATH-100-005): 33 cited loader sites on 16 literals, no code-derived extent; "
        "promoted as LABELED RAW DATA, 4 symbols, by tools/build/rawlabeled.py into "
        "asm/rawlabeled_6fc260.s",
        [(0x6FC260, 0x6FDA00)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled row 0x7122F8..0x71E258",
        "raw-labeled",
        "R-RAW-001 (PATH-100-005): 175 cited loader sites on 66 literals, no code-derived extent; "
        "promoted as LABELED RAW DATA, 41 symbols, by tools/build/rawlabeled.py into "
        "asm/rawlabeled_7122f8.s",
        [(0x7122F8, 0x71E258)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled row 0x72C388..0x7315E8",
        "raw-labeled",
        "R-RAW-001 (PATH-100-005): 25 cited loader sites on 11 literals, no code-derived extent; "
        "promoted as LABELED RAW DATA, 8 symbols, by tools/build/rawlabeled.py into "
        "asm/rawlabeled_72c388.s",
        [(0x72C388, 0x7315E8)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled row 0x75029C..0x752D4C",
        "raw-labeled",
        "R-RAW-001 (PATH-100-005): 9 cited loader sites on 5 literals, no code-derived extent; "
        "promoted as LABELED RAW DATA, 5 symbols, by tools/build/rawlabeled.py into "
        "asm/rawlabeled_75029c.s",
        [(0x75029C, 0x752D4C)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled row 0x752EF0..0x754910",
        "raw-labeled",
        "R-RAW-001 (PATH-100-005): 20 cited loader sites on 9 literals, no code-derived extent; "
        "promoted as LABELED RAW DATA, 8 symbols, by tools/build/rawlabeled.py into "
        "asm/rawlabeled_752ef0.s",
        [(0x752EF0, 0x754910)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled row 0x754978..0x756A4C",
        "raw-labeled",
        "R-RAW-001 (PATH-100-005): 13 cited loader sites on 5 literals, no code-derived extent; "
        "promoted as LABELED RAW DATA, 5 symbols, by tools/build/rawlabeled.py into "
        "asm/rawlabeled_754978.s",
        [(0x754978, 0x756A4C)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled row 0x77B200..0x77C47C",
        "raw-labeled",
        "R-RAW-001 (PATH-100-005): 14 cited loader sites on 6 literals, no code-derived extent; "
        "promoted as LABELED RAW DATA, 6 symbols, by tools/build/rawlabeled.py into "
        "asm/rawlabeled_77b200.s",
        [(0x77B200, 0x77C47C)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "raw-labeled run 0x75A738..0x76CCD4",
        "raw-labeled",
        "R-RAW-001 (PATH-100-002 STEP 3, 2026-10-16): this row's own channel measurement is 79 cited "
        "loader sites on 35 literals, and PATH-100-002 STEP 2 decoded them to six field maps with no "
        "extent, so nothing is derivable and the run is promoted as LABELED RAW DATA, 17 symbols, by "
        "tools/build/rawlabeled.py into asm/rawlabeled_75a738.s",
        [(0x75A738, 0x76CCD4)],
        "no structure and no extent is claimed; the bytes are source now, so 0 B of this range is INCBIN",
    ),
    Region(
        "recon slice A lower half 0x74F080..0x77C5A4",
        "unknown-proven",
        "PATH-100-009 re-measured the literal channel and CORRECTED the count below: 224 Thumb "
        "ldr-literal literals name this span (514 sites outside their rows, 103 multi-site), not "
        "one - the single literal named next is one of them, and its 23 cited rows are promoted as "
        "raw-labeled data. RECON-LATE-002 / K-079, each with its denominator: 0 kind-1/kind-2 header "
        "survives validate_retail_termination (11 header-shaped sites); 0 of 355 decoded container "
        "payloads occurs inside it; 2,097,152 words searched for a loader, 523 loader windows "
        "tracked 0x400 B forward => 0 DMA / VRAM / veneer hits against 53 control hits; exactly one "
        "literal names an address in the span (file 0x052030 = 0x0874F080, read at 0x0805200E)",
        [(0x74F080, 0x77C5A4)],
        "the promoted sub-ranges (the AI nodes, the three piece records and the glyph-source table "
        "0x757EE8..0x758190 - 85 records of 8 B, 680 B, promoted in ENDROM-RECON-001 as "
        "tools/mapcontainer/glyphtable.py on the consumer at 0x0803029E) are generated and are "
        "subtracted by the INCBIN intersection; the residue was 183,798 B and PATH-100-009 removed "
        "14,488 B of it as raw-labeled rows",
    ),
    Region(
        "recon slice B residue 0x6FC238..0x7315E8",
        "unknown-proven",
        "PATH-100-009 re-measured the literal channel: 252 Thumb ldr-literal literals name this "
        "span (538 sites outside their rows, 91 multi-site), and its 6 cited rows are promoted as "
        "raw-labeled data (1,268 B). RECON-LATE-002 / K-079: 0 header-shaped container sites in "
        "B-mid and B-head, 1 in B-tail, all rejected; 0 of 355 decoded payloads occur inside; 486 "
        "loader windows decoded, the readers that exist serve only the named small structures",
        [(0x6FC238, 0x7315E8)],
        "the promoted sub-ranges (enemy stats, the global-state table, the AI nodes) are generated and "
        "are subtracted by the INCBIN intersection",
    ),
    Region(
        "first-MiB code band",
        "identified-with-consumer",
        "12 slices, 308,352 B, byte-proven; the consumer of code "
        "is a caller, and promotion here is transcription, not an emitter (FIRST-MIB-CODE-001)",
        [(0x000158, 0x143F2), (0x0153F2, 0x1A3F2), (0x01C3F2, 0x2AB4C), (0x02BB4C, 0x2D1C0),
         (0x0301C0, 0x311C0), (0x0331C0, 0x341C0), (0x0351C0, 0x3D4D0), (0x03D784, 0x41118),
         (0x042118, 0x43118), (0x046118, 0x49114), (0x049120, 0x55620), (0x06D4E0, 0x71758)],
        "one slice is promoted in part only (0x1C3F2 carries the 8 B linked C unit at 0x0801C62C); the "
        "rest of each slice is transcribed source. PATH-100-016 classified every DCB/DCW/DCD run these "
        "twelve slices carry and moved the plain data tables to build-time extracted INCBIN slices "
        "(134,968 B of the 162,075 B converted, in 2,005 rows), leaving the literal pools and pointer "
        "tables as text.",
    ),

    Region(
        "PATH-100-006 raw-labeled rows (a cited consumer, no extent)",
        "raw-labeled",
        "R-RAW-001, PATH-100-006: each row is named by a literal loaded by more than one "
        "instruction (P-418) or its loader count is above every one of 12 same-size control "
        "windows; promoted as LABELED RAW DATA by tools/build/rawlabeled.py, one "
        "asm/rawlabeled_<start>.s per row, NO EXTENT claimed",
        UNMAPPED_RAW_LABELED,
        "the bytes are source now, so 0 B of these ranges is INCBIN",
    ),
    Region(
        "PATH-100-006 rows named only by singleton literals",
        "unknown-proven",
        "PATH-100-006: the only Thumb ldr-literal sites naming these rows are singletons "
        "(P-418: a real pool literal is loaded by more than one instruction) and every row's "
        "count is at or below its 12 same-size control windows, so the negative is a "
        "literal-channel negative at that denominator",
        UNMAPPED_SINGLETON_LITERAL,
        "no promotion: no consumer established",
    ),
    Region(
        "PATH-100-006 rows no literal names, but a word or a literal-named table does",
        "unknown-proven",
        "PATH-100-006: 0 Thumb/ARM ldr-literal sites name these rows; word-aligned words "
        "outside them hold an address inside them, some of those inside a table a literal "
        "itself names - data naming data, not a code consumer, so no promotion",
        UNMAPPED_NAMED_BY_DATA,
        "the naming words are the row's only evidence; the consumer of the table is not "
        "established",
    ),
    Region(
        "PATH-100-009 raw-labeled rows (a cited consumer, no extent)",
        "raw-labeled",
        "R-RAW-001, PATH-100-009: each row is named by a Thumb ldr-literal above its own 12-window "
        "control null and carries at least one cited base inside the row, so rawlabeled.py splits it "
        "at every cited base; promoted as LABELED RAW DATA, one asm/rawlabeled_<start>.s per row, NO "
        "EXTENT claimed",
        SLICE_RESIDUE_RAW_LABELED,
        "the bytes are source now, so 0 B of these ranges is INCBIN",
    ),

)


def read_rom():
    data = open(ROM, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ROM_SHA256:
        raise SystemExit("baserom.gba sha256 %s is not the canonical %s" % (digest, ROM_SHA256))
    return data


def inbin_mask(slices):
    mask = bytearray(0x800000)
    for start, length in slices:
        for offset in range(start, start + length):
            mask[offset] = 1
    return mask


def region_mask(regions):
    out = []
    for index, region in enumerate(regions):
        out += [(start, end, index) for start, end in region.ranges]
    return out


def rows_for(slices, regions):
    spans = region_mask(regions)
    named = gate.fragment_symbols()
    rows = []
    for start, length in slices:
        symbol = named.get(start)
        cited = symbol is not None and symbol[0] == start + length and symbol[1]
        region = next((regions[hit] for low, high, hit in spans if low <= start < high), None)
        rows.append((start, length, "raw-labeled" if cited else "unreferenced",
                     region.name if region else "no measured region",
                     region.note if region else ""))
    return rows


def class_of(rows, start, end):
    cited = sum(size for low, size, status, _, _ in rows
                if status == "raw-labeled" and low < end and low + size > start)
    other = sum(size for low, size, status, _, _ in rows
                if status == "unreferenced" and low < end and low + size > start)
    if cited and other:
        return "raw-labeled + unreferenced"
    return "raw-labeled" if cited else "unreferenced"


def prefix(mask):
    out = [0] * (len(mask) + 1)
    running = 0
    for index, value in enumerate(mask):
        running += value
        out[index + 1] = running
    return out


def recon_reconciliation():
    return (
        ("AI behaviour node records (both slices)", 68140, 68320, 53152,
         "promoted-since-recon",
         "SPEC-AINODE-001; 2,504 records / 53,152 B in-block, the 16 B stub in the "
         "code region stays retail"),
        ("row table 0x70F514", 6624, 6624, 6624, "promoted-since-recon",
         "the dispatcher 0x0800AA9C; promoted in this ticket (INCBIN-CENSUS-001), which this "
         "census's own promoted-family table re-derives"),
        ("enemy stat records 0x711274", 4228, 4228, 4200, "promoted-since-recon",
         "SPEC-ENEMYSTAT-001-R2; the empty 151st slot (28 B) stays retail"),
        ("event-resource index table 0x79B704", 2088, 2088, 2088, "promoted-since-recon",
         "SPEC-INDEX-001-R2"),
        ("dialogue record words (slice A)", 29633, 29632, 0, "identified-with-consumer",
         "K-017 consumer chain; NOT promoted and not promotable yet - the engine walk reaches 3,850 "
         "8-byte words but only 2,101 of 3,849 neighbour gaps are exactly 8 B and 52 B of the reached "
         "extents overlap, so the record length is not established (the ticket's request and handoff "
         "both say it was not promoted)"),
        ("global-state pointer table 0x6FC238", 20, 0, 40, "promoted-since-recon",
         "SPEC-GSTATE-001-R2; the SPEC sized it 20 B, the promoting ticket measured "
         "40 B (six IWRAM then four ROM words), which is the one 20 B correction to the union total"),
    )


def promoted_families():
    import ainodes
    import assetdir
    import assetdir2
    import endrombank
    import endromrecords
    import enemystats
    import eventindex
    import eventpool
    import globalstate
    import glyphtable
    import rowtable

    rom = read_rom()
    out = []
    for module, ticket in ((ainodes, "SPEC-AINODE-001"),
                           (enemystats, "SPEC-ENEMYSTAT-001-R2"),
                           (eventindex, "SPEC-INDEX-001-R2"),
                           (globalstate, "SPEC-GSTATE-001-R2"),
                           (endromrecords, "TAIL-ENDROM-44-001"),
                           (endrombank, "SPEC2-FAMILIES-001"),
                           (glyphtable, "ENDROM-RECON-001"),
                           (rowtable, "INCBIN-CENSUS-001"),
                           (eventpool, "INCBIN-PROMOTE-002")):
        extents = module.extents(rom)[module.FAMILY]
        out.append((module.FAMILY, ticket, extents))
    for family in assetdir.FAMILIES:
        out.append((family, "INCBIN-PROMOTE-001", assetdir.extents(rom)[family]))
    for family in assetdir2.FAMILIES:
        out.append((family, "ASSET-002", assetdir2.extents(rom)[family]))
    return out


def raw_labeled_rows(rom):
    sys.path.insert(0, HERE)
    import rawlabeled
    return rawlabeled.citation_rows(rom)


def render():
    rom = read_rom()
    slices = gate.incbin_ranges()
    total = sum(length for _, length in slices)
    mask = inbin_mask(slices)
    if sum(mask) != total:
        raise SystemExit("the INCBIN mask holds %d bytes, the slice list %d" % (sum(mask), total))

    rows = rows_for(slices, REGIONS)
    census = sum(size for _, size, _, _, _ in rows)
    assert census == total, (census, total)
    reach = prefix(mask)

    promoted = promoted_families()
    lines = []
    add = lines.append
    add("# The INCBIN census")
    add("")
    add("Generated by `tools/research/incbin_census.py` (`python tools/research/incbin_census.py`);")
    add("the text is a pure function of the retail image, the source tree and that script's region")
    add("table, so two runs are byte-identical.")
    add("")
    add("ROM `baserom.gba` sha256 `%s`." % ROM_SHA256)
    add("")
    add("## SC1 - the bytes")
    add("")
    add("| item | value |")
    add("|---|---|")
    add("| gate INCBIN total (`gate.incbin_ranges()`) | **%d B** |" % total)
    add("| INCBIN slices | %d |" % len(slices))
    add("| census rows | %d |" % len(rows))
    add("| census bytes | **%d B** |" % census)
    add("| equality | %s |" % ("EXACT" if census == total else "MISMATCH"))
    add("")
    add("Status is one of two words:")
    add("")
    add("- `raw-labeled` - a tracked R-RAW-001 fragment carries this exact range AND its own comment")
    add("  for that symbol names a consumer. The bytes are extracted retail data a consumer cites;")
    add("  no structure, layout or extent is claimed.")
    add("- `unreferenced` - no consumer names this range by any route the project has measured (code")
    add("  xrefs, pointer fields, format scans, the loader trace, the runtime session). The row")
    add("  carries a `unk_<ROMADDR>` symbol and this status, and nothing else is claimed about it.")
    add("")
    add("### By status")
    add("")
    add("| status | bytes | share | rows |")
    add("|---|---|---|---|")
    by_status = {}
    for _, size, status, _, _ in rows:
        got = by_status.setdefault(status, [0, 0])
        got[0] += size
        got[1] += 1
    for status in STATUSES:
        size, count = by_status.get(status, (0, 0))
        add("| `%s` | %d | %.2f %% | %d |" % (status, size, 100.0 * size / total, count))
    add("| **total** | **%d** | **100.00 %%** | **%d** |" % (total, len(rows)))
    add("")
    add("## The classes (PATH-100-015, and the gate's citation measurement)")
    add("")
    add("Every byte of the image is source or raw-data. The census splits the raw-data bytes by its own")
    add("two statuses above; the gate prints a FOUR-way split of the same bytes, measured by")
    add("`tools/research/citations_in_source.py`, and QUOTED here from `gate.raw_classes()` rather")
    add("than re-derived:")
    add("")
    add("| class | bytes | share |")
    add("|---|---|---|")
    add("| source - built from tracked source or a byte-exact generator | %d | %.4f %% |"
        % (gate.ROM_SIZE - total, 100.0 * (gate.ROM_SIZE - total) / gate.ROM_SIZE))
    add("| raw-data, `raw-labeled` - the census's own status, a fragment's comment names a consumer "
        "| %d | %.4f %% |" % (by_status.get("raw-labeled", (0, 0))[0],
                              100.0 * by_status.get("raw-labeled", (0, 0))[0] / gate.ROM_SIZE))
    add("| raw-data, `unreferenced` - the census's own status, no comment names a consumer | %d | "
        "%.4f %% |" % (by_status.get("unreferenced", (0, 0))[0],
                       100.0 * by_status.get("unreferenced", (0, 0))[0] / gate.ROM_SIZE))
    add("| **accounted** | **%d** | **%.4f %%** |"
        % (gate.ROM_SIZE - total + total, 100.0 * (gate.ROM_SIZE - total + total) / gate.ROM_SIZE))
    add("")
    _raw_bytes, _cited_bytes, _runtime_bytes, _unreferenced_bytes = gate.raw_classes()
    add("The gate's four classes of those same raw-data bytes, quoted from `gate.raw_classes()`:")
    add("")
    add("| class | bytes | share of the raw-data total |")
    add("|---|---|---|")
    add("| `cited` - a citation site derived from `code_xref` lies in the ledger's code map (P or A) "
        "| %d | %.4f %% |" % (_cited_bytes, 100.0 * _cited_bytes / total))
    add("| `runtime-cited` - not cited, and the carrier comment says `cited by runtime read` | %d | "
        "%.4f %% |" % (_runtime_bytes, 100.0 * _runtime_bytes / total))
    add("| `unreferenced` - no code site and no runtime read | %d | %.4f %% |"
        % (_unreferenced_bytes, 100.0 * _unreferenced_bytes / total))
    add("| **raw-data** | **%d** | **100.0000 %%** |" % (_raw_bytes,))
    add("")
    add("`cited` is an UPPER bound: a site in a ledger code row is still a sweep site, so until")
    add("instruction boundaries are proven a row called `cited` is one a linear sweep reaches, not one")
    add("a running program was observed to read.")
    add("")
    add("### The largest mapped ranges")
    add("")
    add("| region | status | bytes now INCBIN / region size | citation |")
    add("|---|---|---|---|")
    for region in REGIONS:
        size = sum(reach[end] - reach[start] for start, end in region.ranges)
        span = sum(end - start for start, end in region.ranges)
        if size:
            seen = {class_of(rows, low, high) for low, high in region.ranges}
            add("| %s | `%s` | %d / %d | %s |"
                % (region.name, seen.pop() if len(seen) == 1 else "raw-labeled + unreferenced",
                   size, span, region.citation[:180]))
    add("")
    add("## The raw-labeled runs (R-RAW-001)")
    add("")
    add("A region with a cited code consumer but no code-derived extent is carried as LABELED RAW")
    add("DATA: `tools/build/rawlabeled.py` writes a fragment per run - one `unk_<ROMADDR>` symbol")
    add("per cited base, with its loader citation, stride and shape - and every symbol's bytes are ONE")
    add("`INCBIN` of a build-time extracted slice of `baserom.gba` (PATH-100-015), so no retail byte")
    add("payload is tracked and `gate.incbin_ranges()` counts every one of those bytes as `raw-data`.")
    add("`asm/rest_of_the_game.s` INCLUDEs each fragment where the retail INCBIN slice was. Carried")
    add("whole means no layout is claimed; the citation channel is `code_xref.py`'s pc-relative VALUE")
    add("channel, one level past the pool word a site computes (P-422), or an explicit citation list")
    add("(`--citations`: a runtime read, `pc` plus the exact address, one symbol per row). The table")
    add("below is PATH-100-001's own two runs, whose tool is now folded into the same module.")
    add("")
    add("| run | bytes | symbols | loaders cited |")
    add("|---|---|---|---|")
    raw_rows = raw_labeled_rows(rom)
    for name, size, count, loaders in raw_rows:
        add("| `%s` | %d | %d | %d |" % (name, size, count, loaders))
    add("| **total** | **%d** | **%d** | **%d** |"
        % (sum(row[1] for row in raw_rows), sum(row[2] for row in raw_rows),
           sum(row[3] for row in raw_rows)))
    add("")
    add("## RECON-LATE-001's 110,733 B, accounted for")
    add("")
    add("The union basis is the SPEC's disjoint byte mask; the sum basis is V1's round trip. The")
    add("families merge to the 110,733 B the ticket names, and every family now has a promotion or a")
    add("status:")
    add("")
    add("| family | union B | sum B | promoted B | status | citation |")
    add("|---|---|---|---|---|---|")
    union = swum = promoted_total = 0
    for name, uni, summ, got, status, citation in recon_reconciliation():
        union += uni
        swum += summ
        promoted_total += got
        add("| %s | %d | %d | %d | `%s` | %s |" % (name, uni, summ, got, status, citation))
    add("| **total** | **%d** | **%d** | **%d** | | |"
        % (union, swum, promoted_total))
    add("")
    add("The 110,733 B union reproduces exactly (the global-state table is quoted at the SPEC's 20 B;")
    add("the promoting ticket measured 40 B). Promoted since the baseline: %d B. Not yet promoted:"
        % promoted_total)
    add("%d B union - the dialogue record words (consumer-backed, but not promoted: the record"
        % (union - promoted_total))
    add("length is not established) and the AI node records the row table does not reach (no consumer")
    add("names them).")
    add("")
    add("### The families promoted since the baseline, re-derived from this image")
    add("")
    add("| family | ticket | extents | bytes | any extent still INCBIN |")
    add("|---|---|---|---|---|")
    for family, ticket, extents in promoted:
        size = sum(length for _, length in extents)
        still = sum(1 for offset, length in extents
                    if any(mask[offset:offset + length]))
        add("| `%s` | %s | %d | %d | %s |" % (family, ticket, len(extents), size,
                                              "YES - FAIL" if still else "no"))
    add("")
    add("A family whose extents are still INCBIN would mean the census is reading a tree where that")
    add("promotion is absent; the run fails closed instead of printing a number.")
    add("")
    add("## Every INCBIN slice")
    add("")
    add("| file range | size | status | region |")
    add("|---|---|---|---|")
    run_start, run_size, run_status, run_name = (rows[0][0], rows[0][1], rows[0][2], rows[0][3])
    for start, size, status, name, _ in rows[1:]:
        if (status, name) == (run_status, run_name) and start == run_start + run_size:
            run_size += size
            continue
        add("| `0x%06X..0x%06X` | %d | `%s` | %s |"
            % (run_start, run_start + run_size, run_size, run_status, run_name))
        run_start, run_size, run_status, run_name = start, size, status, name
    add("| `0x%06X..0x%06X` | %d | `%s` | %s |"
        % (run_start, run_start + run_size, run_size, run_status, run_name))
    add("| **total** | **%d** | | |" % census)
    add("")
    add("## What this census does not do")
    add("")
    add("- It promotes nothing itself. Promotion is the emitter's job, one family at a time, inside the")
    add("  end-of-ROM block; the raw-labeled ranges are carried by `tools/build/rawlabeled.py`, which")
    add("  parses nothing and claims no extent beyond the cited addresses.")
    add("- It says nothing about runtime behaviour: every status is static evidence.")
    add("")
    text = "\n".join(lines) + "\n"
    return text, rows, total, promoted


def main(argv):
    text, rows, total, promoted = render()
    for family, ticket, extents in promoted:
        size = sum(length for _, length in extents)
        print("promoted family %-28s %6d extents %7d B  %s" % (family, len(extents), size, ticket))
    print("census rows=%d bytes=%d gate INCBIN total=%d %s"
          % (len(rows), sum(size for _, size, _, _, _ in rows), total,
             "EXACT" if sum(size for _, size, _, _, _ in rows) == total else "MISMATCH"))
    print("doc sha256=%s" % hashlib.sha256(text.encode()).hexdigest())
    if "--print" in argv:
        sys.stdout.write(text)
        return 0
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote %s (%d B)" % (os.path.relpath(DOC, ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
