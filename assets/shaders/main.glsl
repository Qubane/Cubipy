struct Voxel {
    uint id;
};


uniform Voxel CHUNK_DATA[];
uniform uint CHUNK_SIZE;


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - iResolution.xy * 0.5f) / iResolution.y;

    fragColor = vec4(uv, 0, 0);
}
