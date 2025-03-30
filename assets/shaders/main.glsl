#version 430
#define CHUNK_SIZE 256
#define INDEX_MASK 255


// chunk cube diagonal
const float CUBE_DIAG = pow(CHUNK_SIZE * CHUNK_SIZE * 3, 0.5f);


// DDA struct
struct DDAData {
    ivec3 ipos;     // integer position
    ivec3 istep;    // integer step
    vec3 ustep;     // unit step size
    vec3 alen;      // length for each axis
};

// information about the point of ray collision
struct RayCast {
    int voxelId;    // collided voxel id
    vec3 pos;       // collision position
    float len;      // distance from ray origin to collision position
    DDAData dda;    // dda data
};

// calculated information about the pixel
struct CollisionData {
    RayCast ray;    // ray data

    vec4 color;     // pixel color
    vec2 uv;        // pixel uv coordinate

    ivec3 normal;   // voxel normal data
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
// Uses `ipos` as a position for the voxel that will be checked
// Returns normal vector
ivec3 getNormal(vec3 pos, ivec3 ipos) {
    // compute delta for collision position and block center
    vec3 delta = pos - ipos - vec3(0.5f);
    vec3 absDelta = abs(delta);

    // find biggest axial length
    if (absDelta.x > absDelta.y && absDelta.x > absDelta.z) {
        if (delta.x > 0.f)
            return ivec3(1, 0, 0);
        else
            return ivec3(-1, 0, 0);
    } else if (absDelta.y > absDelta.z) {
        if (delta.y > 0.f)
            return ivec3(0, 1, 0);
        else
            return ivec3(0, -1, 0);
    } else {
        if (delta.z > 0.f)
            return ivec3(0, 0, 1);
        else
            return ivec3(0, 0, -1);
    }
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


// computes DDA
DDAData computeDDA(vec3 origin, vec3 direction) {
    DDAData dda;

    // compute integer position and unit step
    dda.ipos = ivec3(floor(origin));
    dda.ustep = abs(1.f / direction);

    // compute integer step and axial lengths
    if (direction.x > 0) {
        dda.istep.x = 1;
        dda.alen.x = (float(dda.ipos.x) - origin.x + 1) * dda.ustep.x;
    } else {
        dda.istep.x = -1;
        dda.alen.x = (origin.x - float(dda.ipos.x)) * dda.ustep.x;
    }
    if (direction.y > 0) {
        dda.istep.y = 1;
        dda.alen.y = (float(dda.ipos.y) - origin.y + 1) * dda.ustep.y;
    } else {
        dda.istep.y = -1;
        dda.alen.y = (origin.y - float(dda.ipos.y)) * dda.ustep.y;
    }
    if (direction.z > 0) {
        dda.istep.z = 1;
        dda.alen.z = (float(dda.ipos.z) - origin.z + 1) * dda.ustep.z;
    } else {
        dda.istep.z = -1;
        dda.alen.z = (origin.z - float(dda.ipos.z)) * dda.ustep.z;
    }

    // return
    return dda;
}


// ray caster
// Uses `origin` as a starting position for the ray
// Uses `direction` as a direction in which to cast ray
// Returns `RayData`
RayCast castRay(vec3 origin, vec3 direction) {
    // compute DDA variables
    DDAData dda = computeDDA(origin, direction);

    // distance
    float dist;

    // cast ray
    int voxelId;
    while (true) {
        // check for block collision
        voxelId = getBlock(dda.ipos);
        if (voxelId > 0)
            break;

        // make a step
        if (dda.alen.x < dda.alen.y && dda.alen.x < dda.alen.z) {
            dda.ipos.x += dda.istep.x;
            dist = dda.alen.x;
            dda.alen.x += dda.ustep.x;
        } else if (dda.alen.y < dda.alen.z) {
            dda.ipos.y += dda.istep.y;
            dist = dda.alen.y;
            dda.alen.y += dda.ustep.y;
        } else {
            dda.ipos.z += dda.istep.z;
            dist = dda.alen.z;
            dda.alen.z += dda.ustep.z;
        }

        // check for length; if too far then return
        if (dist > CUBE_DIAG)
            break;
    }
    return RayCast(
        voxelId,
        origin + direction * dist,
        dist,
        dda);
}


// calculates pixel from casting a ray
// Uses `origin` as a starting position for the ray
// Uses `direction` as a direction in which to cast ray
// Returns `CollisionData`
CollisionData castColorRay(vec3 origin, vec3 direction) {
    // cast ray
    RayCast ray = castRay(origin, direction);

    // if collision with block
    if (ray.voxelId > 0) {
        // calculate normal and uv texture coordinate for block
        ivec3 voxelNormal = getNormal(ray.pos, ray.dda.ipos);
        vec2 textureUv = getUvCoord(ray.pos, voxelNormal);

        // calculate base color
        vec4 baseColor = texture(u_textureArray, vec3(textureUv, getLayerByVoxel(ray.voxelId, voxelNormal)));

        // return data
        return CollisionData(
            ray,            // ray data
            baseColor,      // pixel color
            textureUv,      // uv coordinate
            voxelNormal);   // voxel normal data
    }
    // if collision with sky
    // return data
    return CollisionData(
        ray,        // ray data
        vec4(0),    // pixel color
        vec2(0),    // uv coordinate
        ivec3(0));  // voxel normal data
}


vec4 calculatePixel(vec3 origin, vec3 direction) {
    vec3 curPosition = origin;
    vec3 curDirection = direction;

    vec4 cumColor;

    CollisionData rayHit = castColorRay(curPosition, curDirection);
    cumColor += rayHit.color;

    return cumColor;
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

    // calculate pixel data
    fragColor = calculatePixel(origin, direction);
}
