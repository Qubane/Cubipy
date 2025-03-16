#version 430
#define CHUNK_SIZE 128
#define INDEX_MASK 255


const float CUBE_DIAG = pow(CHUNK_SIZE * CHUNK_SIZE * 3, 0.5f);


// information about the point of ray collision
struct CollisionInfo {
    int voxel_id;
    vec3 position;
    float dist;
};


// shader output
out vec4 fragColor;

// uniforms
uniform vec3 iResolution;

// player uniforms
uniform float PLR_FOV;
uniform vec3 PLR_POS;
uniform vec2 PLR_DIR;


// chunk data
layout (std430, binding = 0) buffer CHUNK_DATA_BLOCK {
    int CHUNK[CHUNK_SIZE * CHUNK_SIZE * CHUNK_SIZE / 4];
};


// rotations
vec3 rotate_around_x(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x;
    temp.y = point.y * cos(angle) - point.z * sin(angle);
    temp.z = point.z * cos(angle) + point.y * sin(angle);

    return temp;
}


vec3 rotate_around_y(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x * cos(angle) - point.z * sin(angle);
    temp.y = point.y;
    temp.z = point.z * cos(angle) + point.x * sin(angle);

    return temp;
}


vec3 rotate_around_z(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x * cos(angle) - point.y * sin(angle);
    temp.y = point.y * cos(angle) + point.x * sin(angle);
    temp.z = point.z;

    return temp;
}


// world related
int get_voxel(ivec3 pos) {
    if (pos.x > -1 && pos.x < CHUNK_SIZE &&
        pos.y > -1 && pos.y < CHUNK_SIZE &&
        pos.z > -1 && pos.z < CHUNK_SIZE) {
        int index = pos.z * CHUNK_SIZE * CHUNK_SIZE + pos.y * CHUNK_SIZE + pos.x;
        int mask_offset = (index & 3) << 3;
        return (CHUNK[index >> 2] & (INDEX_MASK << mask_offset)) >> mask_offset;
    }
    return -1;
}


CollisionInfo cast_ray(vec3 origin, vec3 direction) {
    ivec3 ray_pos, ray_step;
    vec3 ray_unit_step, ray_length;
    float dist;

    // calculate integer ray positon and unit step
    ray_pos = ivec3(floor(origin));
    ray_unit_step = abs(1.f / direction);

    // calculate steps and starting lengths
    if (direction.x > 0) {
        ray_step.x = 1;
        ray_length.x = (float(ray_pos.x) - origin.x + 1) * ray_unit_step.x;
    } else {
        ray_step.x = -1;
        ray_length.x = (origin.x - float(ray_pos.x)) * ray_unit_step.x;
    }
    if (direction.y > 0) {
        ray_step.y = 1;
        ray_length.y = (float(ray_pos.y) - origin.y + 1) * ray_unit_step.y;
    } else {
        ray_step.y = -1;
        ray_length.y = (origin.y - float(ray_pos.y)) * ray_unit_step.y;
    }
    if (direction.z > 0) {
        ray_step.z = 1;
        ray_length.z = (float(ray_pos.z) - origin.z + 1) * ray_unit_step.z;
    } else {
        ray_step.z = -1;
        ray_length.z = (origin.z - float(ray_pos.z)) * ray_unit_step.z;
    }

    // cast ray
    int voxel_id;
    while (true) {
        // check for block collision
        voxel_id = get_voxel(ray_pos);
        if (voxel_id > 0)
            return CollisionInfo(
                voxel_id,
                origin + direction * dist,
                dist);

        // make a step
        if (ray_length.x < ray_length.y && ray_length.x < ray_length.z) {
            ray_pos.x += ray_step.x;
            dist = ray_length.x;
            ray_length.x += ray_unit_step.x;
        } else if (ray_length.y < ray_length.z) {
            ray_pos.y += ray_step.y;
            dist = ray_length.y;
            ray_length.y += ray_unit_step.y;
        } else {
            ray_pos.z += ray_step.z;
            dist = ray_length.z;
            ray_length.z += ray_unit_step.z;
        }

        // check for length; if too far then return
        if (dist > CUBE_DIAG)
            return CollisionInfo(
                voxel_id,
                origin + direction * dist,
                dist);
    }
}


void main() {
    vec2 uv = (gl_FragCoord.xy - iResolution.xy * 0.5f) / iResolution.y;

    // calculate distance to chunk border surface
    float distance_to_chunk = max(distance(PLR_POS, vec3(CHUNK_SIZE / 2)) - CUBE_DIAG / 2, 0.f);

    // calculate ray direction
    vec3 direction = normalize(vec3(uv.x, PLR_FOV, uv.y));
    direction = rotate_around_z(rotate_around_x(direction, PLR_DIR.x), PLR_DIR.y);

    // calculate ray origin
    vec3 origin = PLR_POS + direction * distance_to_chunk;

    // cast ray
    CollisionInfo collision = cast_ray(origin, direction);

    // calculate pixel color
    if (collision.voxel_id > 0) {
        fragColor = vec4(floor(collision.position - direction * 0.01f) / CHUNK_SIZE, 1);
//        fragColor = vec4(vec3((collision.dist + distance_to_chunk) / 128.f), 1.f);
        gl_FragDepth = (collision.dist + distance_to_chunk) * -1e6f;
    } else {
        fragColor = vec4(0.f);
        gl_FragDepth = 1.f;
    }
}
