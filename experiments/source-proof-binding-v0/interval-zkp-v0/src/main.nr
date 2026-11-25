// EXPERIMENTAL | SYNTHETIC_ONLY | A0_SYNTHETIC | NOT VALIDATION OR PRODUCTION AUTHORIZATION
fn main(frames: [[u8; 53]; 3], digests: pub [[u8; 32]; 3], maximum_speed_cm_s: pub u32, version: pub u32) {
    assert(version == 2, "unsupported interval version");
    assert(maximum_speed_cm_s == 500, "unsupported limit");
    for i in 0..3 {
        check_frame(frames[i], digests[i], maximum_speed_cm_s);
    }
}
fn check_frame(frame: [u8; 53], signed_frame_digest: [u8; 32], maximum_speed_cm_s: u32) {
    // Fixed-length signed MAVLink2 GLOBAL_POSITION_INT observation.
    assert(frame[0] == 0xfd, "not MAVLink2");
    assert(frame[1] == 28, "unexpected payload length");
    assert(frame[2] == 1, "not signed MAVLink2");
    assert(frame[7] == 33, "not GLOBAL_POSITION_INT");
    assert((frame[8] == 0) & (frame[9] == 0), "unexpected message id");
    assert((frame[5] != 0) & (frame[6] != 0), "invalid source identifier");

    // Bind the *private frame bytes* to the digest of the independently
    // authenticated signed frame. This is stronger than passing source_trust
    // alongside an unrelated private speed witness.
    assert(std::hash::blake2s(frame) == signed_frame_digest, "source digest mismatch");

    // Pinned GPI payload: vx and vy are signed 16-bit little-endian cm/s,
    // at offsets 20/22 from the start of the payload (10-byte header).
    let raw_vx: u32 = (frame[30] as u32) + (frame[31] as u32) * 256;
    let raw_vy: u32 = (frame[32] as u32) + (frame[33] as u32) * 256;
    let vx: u32 = if raw_vx >= 32768 { 65536 - raw_vx } else { raw_vx };
    let vy: u32 = if raw_vy >= 32768 { 65536 - raw_vy } else { raw_vy };
    let vx64: u64 = vx as u64;
    let vy64: u64 = vy as u64;
    let limit: u64 = maximum_speed_cm_s as u64;
    assert(vx64 * vx64 + vy64 * vy64 <= limit * limit, "speed exceeds limit");
}
