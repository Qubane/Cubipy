#version 430
#define CHUNK_SIZE 256
#define INDEX_MASK 255


// chunk cube diagonal
const float CUBE_DIAG = pow(CHUNK_SIZE * CHUNK_SIZE * 3, 0.5f);


// information about the point of ray collision
struct CollisionInfo {
    int voxelId;        // collided voxel id
    vec3 position;      // collision position
    float distance;     // distance from ray origin to collision position
};


// shader output
out vec4 fragColor;

// uniforms
uniform vec3 u_resolution;

// textures
uniform int u_textureMapping[256 * 6];  // 256 blocks with 6 sides per block
uniform sampler2DArray u_textureArray;

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


// simple vector math. Rotations around different axises
// Uses `point` as a point to rotate
// Uses `angle` to rotate the point
// Returns the rotated point
vec3 rotateX(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x;
    temp.y = point.y * cos(angle) - point.z * sin(angle);
    temp.z = point.z * cos(angle) + point.y * sin(angle);

    return temp;
}


// Uses `point` as a point to rotate
// Uses `angle` to rotate the point
// Returns the rotated point
vec3 rotateY(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x * cos(angle) - point.z * sin(angle);
    temp.y = point.y;
    temp.z = point.z * cos(angle) + point.x * sin(angle);

    return temp;
}


// Uses `point` as a point to rotate
// Uses `angle` to rotate the point
// Returns the rotated point
vec3 rotateZ(vec3 point, float angle) {
    vec3 temp = vec3(0);

    temp.x = point.x * cos(angle) - point.y * sin(angle);
    temp.y = point.y * cos(angle) + point.x * sin(angle);
    temp.z = point.z;

    return temp;
}


// get block / voxel
// Uses `pos` to define integer block position
// Returns int that defines the block. Returns -1 when block is out of bounds
int getBlock(ivec3 pos) {
    if (pos.x > -1 && pos.x < CHUNK_SIZE &&
        pos.y > -1 && pos.y < CHUNK_SIZE &&
        pos.z > -1 && pos.z < CHUNK_SIZE) {

        // calculate generic index
        int index = pos.z * CHUNK_SIZE * CHUNK_SIZE + pos.y * CHUNK_SIZE + pos.x;

        // calculate the bitwise mask offset
        int mask_offset = (index & 3) << 3;

        // return the block / voxel
        return (ssbo_voxelData[index >> 2] & (INDEX_MASK << mask_offset)) >> mask_offset;
    }

    // return -1 (void / sky)
    return -1;
}


// voxel normal vector
// Uses `pos` as a position to check
// Uses `offset` to define the accuracy of the check
// Returns normal vector
ivec3 getNormal(vec3 pos, float offset) {
    return ivec3(
        int(getBlock(ivec3(pos.x - offset, pos.y, pos.z)) > 0) - int(getBlock(ivec3(pos.x + offset, pos.y, pos.z)) > 0),
        int(getBlock(ivec3(pos.x, pos.y - offset, pos.z)) > 0) - int(getBlock(ivec3(pos.x, pos.y + offset, pos.z)) > 0),
        int(getBlock(ivec3(pos.x, pos.y, pos.z - offset)) > 0) - int(getBlock(ivec3(pos.x, pos.y, pos.z + offset)) > 0));
}


// voxel UV coord
// Uses `pos` as a position to be converted
// Uses `norm` as a normal, used to fetch coordinates from `pos` argument
// Returns UV coord
vec2 getUvCoord(vec3 pos, ivec3 norm) {
    // wrap the position to be in 0.0 - 1.0 range
    pos = mod(pos, 1.f);

    // fetch the coordinates in the correct order according to the normal vector
    if (norm.x != 0) {
        if (norm.x > 0) {
            return vec2(1.f - pos.y, pos.z);
        } else {
            return vec2(pos.y, pos.z);
        }
    }
    if (norm.y != 0) {
        if (norm.y > 0) {
            return vec2(pos.x, pos.z);
        } else {
            return vec2(1.f - pos.x, pos.z);
        }
    }
    if (norm.z != 0) {
        if (norm.z > 0) {
            return vec2(pos.x, pos.y);
        } else {
            return vec2(1.f - pos.x, 1.f - pos.y);
        }
    }
    return vec2(-1.f, -1.f);
}


int getLayerByVoxel(int voxelId, ivec3 norm) {
    if (norm.x != 0) {
        if (norm.x > 0) {
            return u_textureMapping[voxelId * 6];
        } else {
            return u_textureMapping[voxelId * 6 + 1];
        }
    }
    if (norm.y != 0) {
        if (norm.y > 0) {
            return u_textureMapping[voxelId * 6 + 2];
        } else {
            return u_textureMapping[voxelId * 6 + 3];
        }
    }
    if (norm.z != 0) {
        if (norm.z > 0) {
            return u_textureMapping[voxelId * 6 + 4];
        } else {
            return u_textureMapping[voxelId * 6 + 5];
        }
    }
    return 0;
}


// ray caster
// Uses `origin` as a starting position for the ray
// Uses `direction` as a direction in which to cast ray
// Returns `CollisionInfo`
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
    int voxelId;
    while (true) {
        // check for block collision
        voxelId = getBlock(rayPostion);
        if (voxelId > 0)
            break;

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
            break;
    }
    return CollisionInfo(
        voxelId,
        origin + direction * dist,
        dist);
}


void main() {
    vec2 uv = (gl_FragCoord.xy - u_resolution.xy * 0.5f) / u_resolution.y;

    // calculate distance to chunk border surface
    float chunkDistance = max(distance(u_playerPosition, vec3(CHUNK_SIZE / 2)) - CUBE_DIAG / 2, 0.f);

    // calculate ray direction
    vec3 direction = normalize(vec3(uv.x, u_playerFov, uv.y));
    direction = rotateZ(rotateX(direction, u_playerDirection.x), u_playerDirection.y);

    // calculate ray origin
    vec3 origin = u_playerPosition + direction * chunkDistance;

    // cast ray
    CollisionInfo initial = castRay(origin, direction);

    // calculate distance dependant offsets
    float distancePrecision = max(initial.distance * initial.distance * 1e-6, 5e-5);

    // calculate normal and uv texture coordinate for block
    ivec3 voxelNormal = getNormal(initial.position, distancePrecision);
    vec2 textureUv = getUvCoord(initial.position, voxelNormal);

    // calculate base color
    vec3 baseColor = texture(u_textureArray, vec3(textureUv, getLayerByVoxel(initial.voxelId, voxelNormal))).rgb;

    // cast shadow ray
    CollisionInfo shadow = castRay(initial.position - u_worldSun * distancePrecision * 2.f, -u_worldSun);

    // calculate pixel color
    if (initial.voxelId > 0) {
        // normal shading
        // clamp values between 0.5 and 1.0
        baseColor *= max(0.5f, dot(voxelNormal, -u_worldSun));

        // block is in shadow
        if (shadow.voxelId > 0) {
            baseColor *= 0.3f;
        }

        // write color
        fragColor = vec4(baseColor, 1.f);

//        fragColor = vec4(floor(collision.position) / CHUNK_SIZE, 1.f);
//        fragColor = vec4((getNormal(collision.position) + vec3(1)) / 2, 1.f);
        gl_FragDepth = (initial.distance + chunkDistance) * -1e6f;
    } else {
        fragColor = vec4(0.f);
        gl_FragDepth = 1.f;
    }
}
