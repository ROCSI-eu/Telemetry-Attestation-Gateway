// EXPERIMENTAL
// SYNTHETIC_ONLY
// A0_SYNTHETIC
// NOT VALIDATION OR PRODUCTION AUTHORIZATION

fn main(
    speed_cm_s: u32,
    version: pub u32,
    maximum_speed_cm_s: pub u32,
    context_hi: pub u128,
    context_lo: pub u128,
) {
    assert(version == 0, "unsupported experimental version");
    assert(
        context_hi == 0xe835225e3470b8ecae7748209d432ac2,
        "unexpected experimental context high limb",
    );
    assert(
        context_lo == 0x6df591a1febb1176f0a96a0d439c94b5,
        "unexpected experimental context low limb",
    );
    assert(speed_cm_s <= maximum_speed_cm_s, "synthetic speed exceeds maximum");
}
