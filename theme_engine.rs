// PLASMA FORGE — Theme engine
// Génère une palette unique + params à chaque invocation
// Args: [seed]  -> JSON sur stdout

use std::env;
use std::time::{SystemTime, UNIX_EPOCH};

fn xorshift(state: &mut u64) -> u64 {
    let mut x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    x
}

fn main() {
    let seed_arg = env::args().nth(1).unwrap_or_default();
    let mut state = if !seed_arg.is_empty() {
        let parsed = seed_arg.parse::<u64>();
        match parsed {
            Ok(n) => n.wrapping_add(0x9E3779B97F4A7C15),
            Err(_) => {
                let mut h: u64 = 0x517cc1b727220a95;
                for b in seed_arg.bytes() {
                    h = h.wrapping_mul(0x100000001b3).wrapping_add(b as u64);
                }
                h
            }
        }
    } else {
        SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64
    };
    if state == 0 { state = 1; }

    let rng = &mut state;

    // Type de schéma
    let scheme_type = (xorshift(rng) % 4) as u8;
    let scheme_name = match scheme_type {
        0 => "monochromatic",
        1 => "complementary",
        2 => "triadic",
        _ => "tetradic",
    };

    // Hue de base
    let base_hue = (xorshift(rng) % 360) as f64;
    let base_sat = 60.0 + (xorshift(rng) % 30) as f64;
    let base_light = 45.0 + (xorshift(rng) % 20) as f64;

    // BG très sombre
    let bg_h = base_hue;
    let bg_s = base_sat * 0.5;
    let bg_l = 6.0 + (xorshift(rng) % 6) as f64;
    let surface_l = bg_l + 8.0;

    // Accent selon scheme
    let (accent_h, accent2_h) = match scheme_type {
        0 => (base_hue, base_hue),
        1 => ((base_hue + 180.0) % 360.0, base_hue),
        2 => ((base_hue + 120.0) % 360.0, (base_hue + 240.0) % 360.0),
        _ => ((base_hue + 90.0) % 360.0, (base_hue + 270.0) % 360.0),
    };

    // Animations + layout
    let anim_duration = 6.0 + (xorshift(rng) % 12) as f64;
    let blob_count = 3 + (xorshift(rng) % 4) as u8;
    let grid_cols = 4 + (xorshift(rng) % 4) as u8;
    let border_radius = 4.0 + (xorshift(rng) % 20) as f64;
    let font_scale = 0.95 + (xorshift(rng) % 10) as f64 / 100.0;
    let letter_spacing = -0.04 + (xorshift(rng) % 8) as f64 / 100.0;

    // SVG pattern
    let voronoi_points = 8 + (xorshift(rng) % 8) as u8;
    let noise_scale = 0.5 + (xorshift(rng) % 50) as f64 / 25.0;
    let pattern_rotation = (xorshift(rng) % 360) as f64;

    // Palette 5 couleurs
    let palette = vec![
        format!("hsl({:.0}, {:.0}%, {:.0}%)", base_hue, base_sat, base_light),
        format!("hsl({:.0}, {:.0}%, {:.0}%)", accent_h, base_sat, base_light + 5.0),
        format!("hsl({:.0}, {:.0}%, {:.0}%)", accent2_h, base_sat, base_light + 5.0),
        format!("hsl({:.0}, {:.0}%, {:.0}%)", base_hue, base_sat * 0.7, base_light + 25.0),
        format!("hsl({:.0}, {:.0}%, {:.0}%)", (base_hue + 60.0) % 360.0, base_sat, base_light),
    ];

    println!("{{");
    println!("  \"seed\": \"{}\",", state);
    println!("  \"scheme\": \"{}\",", scheme_name);
    println!("  \"colors\": {{");
    println!("    \"bg\": \"hsl({:.0}, {:.0}%, {:.0}%)\",", bg_h, bg_s, bg_l);
    println!("    \"surface\": \"hsl({:.0}, {:.0}%, {:.0}%)\",", bg_h, bg_s, surface_l);
    println!("    \"primary\": \"hsl({:.0}, {:.0}%, {:.0}%)\",", base_hue, base_sat, base_light);
    println!("    \"accent\": \"hsl({:.0}, {:.0}%, {:.0}%)\",", accent_h, base_sat, base_light + 10.0);
    println!("    \"accent2\": \"hsl({:.0}, {:.0}%, {:.0}%)\",", accent2_h, base_sat, base_light + 10.0);
    println!("    \"text\": \"hsl({:.0}, {:.0}%, 92.0%)\",", base_hue, 15.0);
    println!("    \"muted\": \"hsl({:.0}, {:.0}%, 65.0%)\",", base_hue, 15.0);
    print!("    \"palette\": [");
    for (i, c) in palette.iter().enumerate() {
        if i > 0 { print!(", "); }
        print!("\"{}\"", c);
    }
    println!("]");
    println!("  }},");
    println!("  \"params\": {{");
    println!("    \"anim_duration\": {:.1},", anim_duration);
    println!("    \"blob_count\": {},", blob_count);
    println!("    \"grid_cols\": {},", grid_cols);
    println!("    \"border_radius\": {:.1},", border_radius);
    println!("    \"font_scale\": {:.2},", font_scale);
    println!("    \"letter_spacing\": {:.3}", letter_spacing);
    println!("  }},");
    println!("  \"svg\": {{");
    println!("    \"voronoi_points\": {},", voronoi_points);
    println!("    \"noise_scale\": {:.2},", noise_scale);
    println!("    \"rotation\": {:.0}", pattern_rotation);
    println!("  }},");
    println!("  \"timestamp\": {}", SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs());
    println!("}}");
}
