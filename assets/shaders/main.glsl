#version 430
#define CHUNK_SIZE 256
#define INDEX_MASK 255


const float CUBE_DIAG = pow(CHUNK_SIZE * CHUNK_SIZE * 3, 0.5f);


// information about the point of ray collision
struct CollisionInfo {
    int voxelId;
    vec3 position;
    float distance;
};


// shader output
out vec4 fragColor;

// uniforms
uniform vec3 u_Resolution;

// player uniforms
uniform float u_playerFov;
uniform vec3 u_playerPosition;
uniform vec2 u_playerDirection;

// world uniforms
uniform vec3 u_worldSun;


// chunk data
layout (std430, binding = 0) buffer voxelData {
    int ssbo_voxelData[CHUNK_SIZE * CHUNK_SIZE * CHUNK_SIZE / 4];
};


// rotations
vec3 rotateX(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x;
    temp.y = point.y * cos(angle) - point.z * sin(angle);
    temp.z = point.z * cos(angle) + point.y * sin(angle);

    return temp;
}


vec3 rotateY(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x * cos(angle) - point.z * sin(angle);
    temp.y = point.y;
    temp.z = point.z * cos(angle) + point.x * sin(angle);

    return temp;
}


vec3 rotateZ(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x * cos(angle) - point.y * sin(angle);
    temp.y = point.y * cos(angle) + point.x * sin(angle);
    temp.z = point.z;

    return temp;
}


// world related
int getBlock(ivec3 pos) {
    if (pos.x > -1 && pos.x < CHUNK_SIZE &&
        pos.y > -1 && pos.y < CHUNK_SIZE &&
        pos.z > -1 && pos.z < CHUNK_SIZE) {
        int index = pos.z * CHUNK_SIZE * CHUNK_SIZE + pos.y * CHUNK_SIZE + pos.x;
        int mask_offset = (index & 3) << 3;
        return (ssbo_voxelData[index >> 2] & (INDEX_MASK << mask_offset)) >> mask_offset;
    }
    return -1;
}


vec3 getNormal(vec3 pos) {
    return vec3(
        int(getBlock(ivec3(pos.x - 2e-4, pos.y, pos.z)) == 0) - int(getBlock(ivec3(pos.x + 2e-4, pos.y, pos.z)) == 0),
        int(getBlock(ivec3(pos.x, pos.y - 2e-4, pos.z)) == 0) - int(getBlock(ivec3(pos.x, pos.y + 2e-4, pos.z)) == 0),
        int(getBlock(ivec3(pos.x, pos.y, pos.z - 2e-4)) == 0) - int(getBlock(ivec3(pos.x, pos.y, pos.z + 2e-4)) == 0));
}


// ray caster
CollisionInfo castRay(vec3 origin, vec3 direction) {
    ivec3 rayPostion, rayStep;
    vec3 rayUnit, rayLength;
    float dist;

    // calculate integer ray positon and unit step
    rayPostion = ivec3(floor(origin));
    rayUnit = abs(1.f / direction);

    // calculate steps and starting lengths
    if (direction.x > 0) {
        rayStep.x = 1;
        rayLength.x = (float(rayPostion.x) - origin.x + 1) * rayUnit.x;
    } else {
        rayStep.x = -1;
        rayLength.x = (origin.x - float(rayPostion.x)) * rayUnit.x;
    }
    if (direction.y > 0) {
        rayStep.y = 1;
        rayLength.y = (float(rayPostion.y) - origin.y + 1) * rayUnit.y;
    } else {
        rayStep.y = -1;
        rayLength.y = (origin.y - float(rayPostion.y)) * rayUnit.y;
    }
    if (direction.z > 0) {
        rayStep.z = 1;
        rayLength.z = (float(rayPostion.z) - origin.z + 1) * rayUnit.z;
    } else {
        rayStep.z = -1;
        rayLength.z = (origin.z - float(rayPostion.z)) * rayUnit.z;
    }

    // cast ray
    int voxel_id;
    while (true) {
        // check for block collision
        voxel_id = getBlock(rayPostion);
        if (voxel_id > 0)
            return CollisionInfo(
                voxel_id,
                origin + direction * (dist - 1e-4),
                dist);

        // make a step
        if (rayLength.x < rayLength.y && rayLength.x < rayLength.z) {
            rayPostion.x += rayStep.x;
            dist = rayLength.x;
            rayLength.x += rayUnit.x;
        } else if (rayLength.y < rayLength.z) {
            rayPostion.y += rayStep.y;
            dist = rayLength.y;
            rayLength.y += rayUnit.y;
        } else {
            rayPostion.z += rayStep.z;
            dist = rayLength.z;
            rayLength.z += rayUnit.z;
        }

        // check for length; if too far then return
        if (dist > CUBE_DIAG)
            return CollisionInfo(
                voxel_id,
                origin + direction * (dist - 1e-4),
                dist);
    }
}


void main() {
    vec2 uv = (gl_FragCoord.xy - u_Resolution.xy * 0.5f) / u_Resolution.y;

    // calculate distance to chunk border surface
    float chunkDistance = max(distance(u_playerPosition, vec3(CHUNK_SIZE / 2)) - CUBE_DIAG / 2, 0.f);

    // calculate ray direction
    vec3 direction = normalize(vec3(uv.x, u_playerFov, uv.y));
    direction = rotateZ(rotateX(direction, u_playerDirection.x), u_playerDirection.y);

    // calculate ray origin
    vec3 origin = u_playerPosition + direction * chunkDistance;

    // cast ray
    CollisionInfo initial = castRay(origin, direction);

    // cast shadow ray
    CollisionInfo shadow = castRay(initial.position, -u_worldSun);

    // calculate pixel color
    if (initial.voxelId > 0) {
        vec3 initialColor = (getNormal(initial.position) + vec3(1)) / 2;

        // block is not in shadow
        if (shadow.voxelId == -1) {
            fragColor = vec4(initialColor, 1.f);
        } else {
            fragColor = vec4(initialColor * 0.1f, 1.f);
        }

//        fragColor = vec4(floor(collision.position) / CHUNK_SIZE, 1.f);
//        fragColor = vec4((getNormal(collision.position) + vec3(1)) / 2, 1.f);
        gl_FragDepth = (initial.distance + chunkDistance) * -1e6f;
    } else {
        fragColor = vec4(0.f);
        gl_FragDepth = 1.f;
    }
}
