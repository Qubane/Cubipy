uniform uint CHUNK_SIZE;
uniform uint CHUNK_DATA[16*16*16];


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - iResolution.xy * 0.5f) / iResolution.y;

    CHUNK_SIZE;  // keep uniforms active
    CHUNK_DATA[0];  // keep uniforms active

    fragColor = vec4(uv, 0, 0);
}
