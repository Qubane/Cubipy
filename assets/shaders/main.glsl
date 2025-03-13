#define CHUNK_SIZE 16
#define CHUNK_LAYER CHUNK_SIZE * CHUNK_SIZE
#define CHUNK_ROW CHUNK_SIZE
#define STEP_SIZE 0.05f


uniform uint CHUNK_DATA[CHUNK_SIZE * CHUNK_SIZE * CHUNK_SIZE];


vec3 cast_ray(vec3 origin, vec3 direction) {
    ivec3 position;
    float d;
    while (true) {
        position = ivec3(origin);
        if (position.x > -1 && position.x < CHUNK_SIZE &&
            position.y > -1 && position.y < CHUNK_SIZE &&
            position.z > -1 && position.z < CHUNK_SIZE) {
            if (CHUNK_DATA[int(position.z * CHUNK_LAYER + position.y * CHUNK_ROW + position.x)] > 0.f) {
                return origin;
            }
        }

        origin += direction * STEP_SIZE;
        d += STEP_SIZE;

        if (d > 32.f) {
            return origin;
        }
    }
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - iResolution.xy * 0.5f) / iResolution.y;

    vec3 origin = vec3(8);
    vec3 direction = normalize(vec3(uv.x, 0.5f, uv.y));
    vec3 block_pos = cast_ray(origin, direction);

    fragColor = vec4(length(block_pos) / 48);
}
