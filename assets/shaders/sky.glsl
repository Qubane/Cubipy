#version 430
#define GRAD_LEN 5


// shader output
out vec4 fragColor;

// uniforms
uniform vec3 u_resolution;

// player uniforms
uniform vec2 u_playerDirection;

// sky uniforms
uniform int u_skyGradient[GRAD_LEN];

// world uniforms
uniform vec3 u_worldSun;


vec3 getColor(int index) {
    return vec3(
        float(u_skyGradient[index] >> 16) / 255.f,
        float((u_skyGradient[index] >> 8) & 0xff) / 255.f,
        float(u_skyGradient[index] & 0xff) / 255.f);
}


void main() {
    vec2 uv = (gl_FragCoord.xy - u_resolution.xy * 0.5f) / u_resolution.y;
    float t = (sin(u_playerDirection.x + (gl_FragCoord.y * 3.14159265f / u_resolution.y)) + 1.f) / 2.f;

    int skySliceIndex = int(t * (GRAD_LEN - 1));

    vec3 startColor = getColor(skySliceIndex);
    vec3 endColor = getColor(skySliceIndex + 1);

    float color_t = mod(t, 1.f / (GRAD_LEN - 1)) * (GRAD_LEN - 1);

    fragColor = vec4(vec3(startColor * (1.f - color_t) + endColor * color_t), 1.f);
}