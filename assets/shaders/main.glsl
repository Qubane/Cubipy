#define CHUNK_SIZE 16
#define STEP_SIZE 0.01f


uniform int CHUNK_DATA[CHUNK_SIZE * CHUNK_SIZE * CHUNK_SIZE];


int get_voxel(ivec3 pos) {
    if (pos.x > -1 && pos.x < CHUNK_SIZE &&
        pos.y > -1 && pos.y < CHUNK_SIZE &&
        pos.z > -1 && pos.z < CHUNK_SIZE) {
        return CHUNK_DATA[pos.z * CHUNK_SIZE * CHUNK_SIZE + pos.y * CHUNK_SIZE + pos.x];
    }
    return -1;
}


vec3 cast_ray(vec3 origin, vec3 direction) {
    float d;
    while (true) {
        if (get_voxel(ivec3(origin)) > 0)
            return origin;

        origin += direction * STEP_SIZE;
        d += STEP_SIZE;

        if (d > 32.f)
            return origin;
    }
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - iResolution.xy * 0.5f) / iResolution.y;

    vec3 origin = vec3(8);
    vec3 direction = normalize(vec3(uv.x, 0.5f, uv.y));
    vec3 block_pos = cast_ray(origin, direction);

    fragColor = vec4(length(block_pos) / 48);
}
