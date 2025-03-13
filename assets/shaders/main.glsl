#define CHUNK_SIZE 16


struct CollisionInfo {
    vec3 position;
    float dist;
    int voxel_id;
};


uniform int CHUNK_DATA[CHUNK_SIZE * CHUNK_SIZE * CHUNK_SIZE];


int get_voxel(ivec3 pos) {
    if (pos.x > -1 && pos.x < CHUNK_SIZE &&
        pos.y > -1 && pos.y < CHUNK_SIZE &&
        pos.z > -1 && pos.z < CHUNK_SIZE) {
        return CHUNK_DATA[pos.z * CHUNK_SIZE * CHUNK_SIZE + pos.y * CHUNK_SIZE + pos.x];
    }
    return -1;
}


CollisionInfo cast_ray(vec3 origin, vec3 direction) {
    ivec3 ray_pos, ray_step;
    vec3 ray_unit_step, ray_length;
    float dist;

    // calculate integer ray positon and unit step
    ray_pos = ivec3(origin);
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
                direction * dist,
                dist,
                voxel_id);

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
                direction * dist,
                dist,
                voxel_id);
    }
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - iResolution.xy * 0.5f) / iResolution.y;

    vec3 origin = vec3(8);
    vec3 direction = normalize(vec3(uv.x, 0.5f, uv.y));
    CollisionInfo casted_ray = cast_ray(origin, direction);

    fragColor = vec4(casted_ray.dist / 48);
}
