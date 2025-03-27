#version 430


// shader output
out vec4 fragColor;

// uniforms
uniform vec3 u_resolution;

// player uniforms
uniform vec2 u_playerDirection;

// sky uniforms
uniform int u_skyGradient[5];

// world uniforms
uniform vec3 u_worldSun;


void main() {
    vec2 uv = (gl_FragCoord.xy - u_resolution.xy * 0.5f) / u_resolution.y;

    fragColor = vec4(uv, 0, 1);
}