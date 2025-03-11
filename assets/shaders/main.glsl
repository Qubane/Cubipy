#define MAX_ITERATIONS 128


int iterate_pos(vec2 coord) {
    vec2 z = coord;
    float zmagx, zmagy;
    for (int i = 0; i < MAX_ITERATIONS; i++) {
        zmagx = z.x * z.x;
        zmagy = z.y * z.y;
        if (zmagx + zmagy > 4) {
            return i;
        }
        z = vec2(zmagx - zmagy + z.x, 2 * z.x * z.y + z.y);
    }
    return MAX_ITERATIONS;
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 normalizedFragCoord = fragCoord / iResolution.xy;
    fragColor = vec4(fragCoord, 0, 0);
}
