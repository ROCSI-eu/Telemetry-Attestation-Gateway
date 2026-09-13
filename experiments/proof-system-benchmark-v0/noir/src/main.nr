// EXPERIMENTAL
// SYNTHETIC_ONLY
// A0_SYNTHETIC
// NOT VALIDATION OR PRODUCTION AUTHORIZATION

fn main(speed_cm_s: u32, maximum_speed_cm_s: pub u32) {
    assert(speed_cm_s <= maximum_speed_cm_s, "synthetic speed exceeds maximum");
}
