void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 normalizedFragCoord = fragCoord / iResolution.xy;
    fragColor = vec4(fragCoord, 0, 0);
}
