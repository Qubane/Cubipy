#define MAX_ITERATIONS 128


int iterate_pos(vec2 coord) {
    vec2 z = coord;
    vec2 sq;
    for (int i = 0; i < MAX_ITERATIONS; i++) {
        sq = z * z;
        if (sq.x + sq.y > 4)
            return i;
        z = vec2(sq.x - sq.y + coord.x, 2.f * z.x * z.y + coord.y);
    }
    return 0;
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - iResolution.xy * 0.5f) / iResolution.y;
    uv *= 2;

    float value = float(iterate_pos(uv - vec2(0.5f, 0.f))) / MAX_ITERATIONS;

    fragColor = vec4(value);
}
