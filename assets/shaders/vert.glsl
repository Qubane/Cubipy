#version 430


in vec2 in_vert;


void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}