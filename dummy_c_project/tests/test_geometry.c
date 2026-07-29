#include <assert.h>

#include "geometry.h"

int main(void) {
    struct Point p1 = {1, 2};
    struct Point p2 = {3, 4};
    struct Point sum = add_points(p1, p2);

    assert(sum.x == 4);
    assert(sum.y == 6);
    return 0;
}
