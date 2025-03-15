#define CHUNK_SIZE 16
#define INDEX_MASK 255


struct CollisionInfo {
    int voxel_id;
    vec3 position;
    float dist;
};


uniform int CHUNK_DATA[CHUNK_SIZE * CHUNK_SIZE * CHUNK_SIZE / 4];
uniform float PLR_FOV;
uniform vec3 PLR_POS;
uniform vec2 PLR_DIR;


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


int get_voxel(ivec3 pos) {
    if (pos.x > -1 && pos.x < CHUNK_SIZE &&
        pos.y > -1 && pos.y < CHUNK_SIZE &&
        pos.z > -1 && pos.z < CHUNK_SIZE) {
        int index = pos.z * CHUNK_SIZE * CHUNK_SIZE + pos.y * CHUNK_SIZE + pos.x;
        int mask_offset = (index & 3) << 3;
        return (CHUNK_DATA[index >> 2] & (INDEX_MASK << mask_offset)) >> mask_offset;
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
        if (dist > 64.f)
            return CollisionInfo(
                voxel_id,
                origin + direction * dist,
                dist);
    }
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - iResolution.xy * 0.5f) / iResolution.y;

    vec3 direction = normalize(vec3(uv.x, PLR_FOV, uv.y));
    direction = rotate_around_z(rotate_around_x(direction, PLR_DIR.x), PLR_DIR.y);

    CollisionInfo collision = cast_ray(PLR_POS, direction);

    if (collision.voxel_id > 0)
        fragColor = vec4(floor(collision.position), 0);
    else
        fragColor = vec4(0, 0, 0, 0);
}
